"""PixelEngine physics — gravity, forces, and body simulation.

Uses Pymunk (Chipmunk2D) when available for robust rigid-body physics.
Falls back to a simple Euler-integration system otherwise.
"""
from pixelengine.pobject import PObject

# Try importing Pymunk
try:
    import pymunk
    HAS_PYMUNK = True
except ImportError:
    HAS_PYMUNK = False


class PhysicsBody:
    """Wraps a PObject with physics properties.

    When Pymunk is available, creates native Pymunk Body + Shape objects
    for accurate rigid-body physics. Otherwise uses simple Euler integration.

    Usage::

        ball = Circle(5, x=128, y=20, color="#FF004D")
        body = PhysicsBody(ball, mass=1.0, vx=2, vy=0)
        physics.add_body(body)
    """

    def __init__(self, pobject: PObject, mass: float = 1.0,
                 vx: float = 0, vy: float = 0,
                 restitution: float = 0.8, friction: float = 0.99,
                 is_static: bool = False):
        self.pobject = pobject
        self.mass = max(0.001, mass)
        self.vx = vx
        self.vy = vy
        self.ax = 0.0
        self.ay = 0.0
        self.restitution = restitution
        self.friction = friction
        self.is_static = is_static
        self.active = True

        # Pymunk objects (created when added to a PymunkWorld)
        self._pm_body = None
        self._pm_shape = None

    def _create_pymunk(self):
        """Create Pymunk body and shape from PObject geometry."""
        if not HAS_PYMUNK:
            return

        if self.is_static:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            moment = pymunk.moment_for_circle(self.mass, 0,
                                               self._radius or 5)
            body = pymunk.Body(self.mass, moment)

        body.position = (self.pobject.x + (self._radius or 0),
                        self.pobject.y + (self._radius or 0))
        body.velocity = (self.vx, self.vy)

        # Create shape based on geometry
        if self._radius is not None:
            shape = pymunk.Circle(body, self._radius)
        elif self._width is not None and self._height is not None:
            hw, hh = self._width / 2, self._height / 2
            verts = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
            shape = pymunk.Poly(body, verts)
            body.position = (self.pobject.x + hw,
                           self.pobject.y + hh)
        else:
            shape = pymunk.Circle(body, 2)

        shape.elasticity = self.restitution
        shape.friction = max(0, 1.0 - self.friction)
        shape.collision_type = id(self) % (2**31)  # Unique collision type

        self._pm_body = body
        self._pm_shape = shape

    def _sync_from_pymunk(self):
        """Update PObject position from Pymunk body."""
        if self._pm_body is None:
            return
        px, py = self._pm_body.position
        if self._radius is not None:
            self.pobject.x = px - self._radius
            self.pobject.y = py - self._radius
        elif self._width is not None and self._height is not None:
            self.pobject.x = px - self._width / 2
            self.pobject.y = py - self._height / 2
        else:
            self.pobject.x = px
            self.pobject.y = py
        self.vx, self.vy = self._pm_body.velocity

    @property
    def _radius(self):
        """Live geometry from underlying PObject (not cached)."""
        return getattr(self.pobject, 'radius', None)

    @property
    def _width(self):
        """Live geometry from underlying PObject (not cached)."""
        return getattr(self.pobject, 'width', None)

    @property
    def _height(self):
        """Live geometry from underlying PObject (not cached)."""
        return getattr(self.pobject, 'height', None)

    @property
    def x(self) -> float:
        return self.pobject.x

    @x.setter
    def x(self, v):
        self.pobject.x = v

    @property
    def y(self) -> float:
        return self.pobject.y

    @y.setter
    def y(self, v):
        self.pobject.y = v

    def apply_force(self, fx: float, fy: float):
        """Apply a force this frame (accumulated into acceleration)."""
        if self._pm_body and HAS_PYMUNK:
            self._pm_body.apply_force_at_local_point((fx, fy))
        else:
            self.ax += fx / self.mass
            self.ay += fy / self.mass

    def apply_impulse(self, ix: float, iy: float):
        """Apply an instant velocity change."""
        if self._pm_body and HAS_PYMUNK:
            self._pm_body.apply_impulse_at_local_point((ix, iy))
        else:
            self.vx += ix / self.mass
            self.vy += iy / self.mass

    @property
    def center_x(self) -> float:
        if self._width:
            return self.x + self._width / 2
        if self._radius:
            return self.x + self._radius
        return self.x

    @property
    def center_y(self) -> float:
        if self._height:
            return self.y + self._height / 2
        if self._radius:
            return self.y + self._radius
        return self.y

    @property
    def shape_type(self) -> str:
        if self._radius is not None:
            return "circle"
        if self._width is not None and self._height is not None:
            return "rect"
        return "point"


class PhysicsWorld:
    """Manages physics bodies and steps the simulation.

    Uses Pymunk when available for accurate rigid-body physics with
    proper collision detection and response. Falls back to simple
    Euler integration otherwise.

    Usage::

        physics = PhysicsWorld(gravity_y=100)  # pixels/s²
        physics.add_body(ball_body)
        # In scene, physics.step(dt) is called automatically each frame

    Objects fall due to gravity, collide with bounds, and interact.
    """

    def __init__(self, gravity_x: float = 0, gravity_y: float = 100,
                 bounds: tuple = None):
        self.gravity_x = gravity_x
        self.gravity_y = gravity_y
        self.bodies: list = []
        self.bounds = bounds
        self._callbacks: list = []
        self._use_pymunk = HAS_PYMUNK

        # Pymunk space
        if self._use_pymunk:
            self._space = pymunk.Space()
            self._space.gravity = (gravity_x, gravity_y)
            self._body_map = {}  # collision_type -> PhysicsBody
        else:
            self._space = None

    def _pymunk_post_step_collisions(self):
        """Check for collisions after step and fire callbacks."""
        if not self._callbacks:
            return
        for arb in self._space._get_arbiters():
            shapes = arb.shapes
            if len(shapes) >= 2:
                body_a = self._body_map.get(shapes[0].collision_type)
                body_b = self._body_map.get(shapes[1].collision_type)
                if body_a and body_b:
                    for cb in self._callbacks:
                        cb(body_a, body_b)

    def add_body(self, body: PhysicsBody):
        if body not in self.bodies:
            self.bodies.append(body)
            if self._use_pymunk:
                body._create_pymunk()
                if body._pm_body and body._pm_shape:
                    self._space.add(body._pm_body, body._pm_shape)
                    self._body_map[body._pm_shape.collision_type] = body
        return self

    def remove_body(self, body: PhysicsBody):
        if body in self.bodies:
            self.bodies.remove(body)
            if self._use_pymunk and body._pm_body and body._pm_shape:
                self._space.remove(body._pm_shape, body._pm_body)
                self._body_map.pop(body._pm_shape.collision_type, None)
        return self

    def add_collision_callback(self, callback):
        """Add a collision callback: fn(body_a, body_b)."""
        self._callbacks.append(callback)

    def step(self, dt: float):
        """Advance simulation by dt seconds."""
        if self._use_pymunk:
            self._step_pymunk(dt)
        else:
            self._step_euler(dt)

    def _step_pymunk(self, dt: float):
        """Step using Pymunk's built-in physics."""
        # Enforce bounds using segment shapes (lazy init)
        if self.bounds and not hasattr(self, '_bounds_added'):
            bx_min, by_min, bx_max, by_max = self.bounds
            walls = [
                pymunk.Segment(self._space.static_body, (bx_min, by_min), (bx_max, by_min), 5),
                pymunk.Segment(self._space.static_body, (bx_max, by_min), (bx_max, by_max), 5),
                pymunk.Segment(self._space.static_body, (bx_max, by_max), (bx_min, by_max), 5),
                pymunk.Segment(self._space.static_body, (bx_min, by_max), (bx_min, by_min), 5),
            ]
            for w in walls:
                w.elasticity = 0.8
                w.friction = 0.3
            self._space.add(*walls)
            self._bounds_added = True

        self._space.step(dt)

        # Fire collision callbacks
        self._pymunk_post_step_collisions()

        # Sync positions back to PObjects
        for body in self.bodies:
            if not body.is_static and body.active:
                body._sync_from_pymunk()

    def _step_euler(self, dt: float):
        """Fallback: simple Euler integration (original behavior)."""
        for body in self.bodies:
            if body.is_static or not body.active:
                continue

            # Apply gravity
            body.ax += self.gravity_x
            body.ay += self.gravity_y

            # Euler integration
            body.vx += body.ax * dt
            body.vy += body.ay * dt
            # Frame-rate independent friction: friction**dt
            # ensures consistent damping regardless of FPS
            friction_dt = body.friction ** dt
            body.vx *= friction_dt
            body.vy *= friction_dt
            body.x += body.vx * dt
            body.y += body.vy * dt

            # Reset acceleration for next frame
            body.ax = 0
            body.ay = 0

        # Collision detection between all body pairs
        n = len(self.bodies)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self.bodies[i], self.bodies[j]
                if not a.active or not b.active:
                    continue
                if self._check_collision(a, b):
                    self._resolve_collision(a, b)
                    for cb in self._callbacks:
                        cb(a, b)

        # Bounds enforcement
        if self.bounds:
            bx_min, by_min, bx_max, by_max = self.bounds
            for body in self.bodies:
                if body.is_static or not body.active:
                    continue
                self._enforce_bounds(body, bx_min, by_min, bx_max, by_max)

    def _check_collision(self, a: PhysicsBody, b: PhysicsBody) -> bool:
        """Check if two bodies are colliding."""
        if a.shape_type == "circle" and b.shape_type == "circle":
            dx = a.center_x - b.center_x
            dy = a.center_y - b.center_y
            dist_sq = dx * dx + dy * dy
            r_sum = (a._radius or 0) + (b._radius or 0)
            return dist_sq < r_sum * r_sum
        elif a.shape_type == "rect" and b.shape_type == "rect":
            return (a.x < b.x + (b._width or 0) and
                    a.x + (a._width or 0) > b.x and
                    a.y < b.y + (b._height or 0) and
                    a.y + (a._height or 0) > b.y)
        else:
            ax1 = a.x
            ay1 = a.y
            aw = a._width or (a._radius or 0) * 2
            ah = a._height or (a._radius or 0) * 2
            bx1 = b.x
            by1 = b.y
            bw = b._width or (b._radius or 0) * 2
            bh = b._height or (b._radius or 0) * 2
            return (ax1 < bx1 + bw and ax1 + aw > bx1 and
                    ay1 < by1 + bh and ay1 + ah > by1)

    def _resolve_collision(self, a: PhysicsBody, b: PhysicsBody):
        """Simple elastic collision response."""
        if a.is_static and b.is_static:
            return

        if a.shape_type == "circle" and b.shape_type == "circle":
            dx = b.center_x - a.center_x
            dy = b.center_y - a.center_y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 0.001:
                dist = 0.001
            nx, ny = dx / dist, dy / dist

            overlap = (a._radius or 0) + (b._radius or 0) - dist
            if overlap > 0:
                if not a.is_static:
                    a.x -= nx * overlap / 2
                    a.y -= ny * overlap / 2
                if not b.is_static:
                    b.x += nx * overlap / 2
                    b.y += ny * overlap / 2

            rel_vx = a.vx - b.vx
            rel_vy = a.vy - b.vy
            vel_along = rel_vx * nx + rel_vy * ny
            if vel_along > 0:
                return

            restitution = min(a.restitution, b.restitution)
            j = -(1 + restitution) * vel_along
            if not a.is_static and not b.is_static:
                j /= (1 / a.mass + 1 / b.mass)
            else:
                j /= (1 / a.mass) if not a.is_static else (1 / b.mass)

            if not a.is_static:
                a.vx += j * nx / a.mass
                a.vy += j * ny / a.mass
            if not b.is_static:
                b.vx -= j * nx / b.mass
                b.vy -= j * ny / b.mass
        else:
            restitution = min(a.restitution, b.restitution)
            if not a.is_static:
                a.vx *= -restitution
                a.vy *= -restitution
            if not b.is_static:
                b.vx *= -restitution
                b.vy *= -restitution

    def _enforce_bounds(self, body: PhysicsBody,
                        bx_min, by_min, bx_max, by_max):
        """Keep body within screen bounds with bounce."""
        r = body._radius or 0
        w = body._width or r * 2
        h = body._height or r * 2

        if body.x < bx_min:
            body.x = bx_min
            body.vx = abs(body.vx) * body.restitution
        if body.x + w > bx_max:
            body.x = bx_max - w
            body.vx = -abs(body.vx) * body.restitution
        if body.y < by_min:
            body.y = by_min
            body.vy = abs(body.vy) * body.restitution
        if body.y + h > by_max:
            body.y = by_max - h
            body.vy = -abs(body.vy) * body.restitution
