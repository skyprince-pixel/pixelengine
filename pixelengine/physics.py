"""PixelEngine physics — gravity, forces, and body simulation.

Simple Euler-integration physics system for educational simulations.
PhysicsWorld manages bodies and steps the simulation each frame.
"""
from pixelengine.pobject import PObject


class PhysicsBody:
    """Wraps a PObject with physics properties.

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
        self.ax = 0.0  # Accumulated acceleration
        self.ay = 0.0
        self.restitution = restitution  # Bounciness (0=none, 1=perfect)
        self.friction = friction         # Velocity damping
        self.is_static = is_static       # Static bodies don't move
        self.active = True
        # Shape info for collision
        self._radius = getattr(pobject, 'radius', None)
        self._width = getattr(pobject, 'width', None)
        self._height = getattr(pobject, 'height', None)

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
        self.ax += fx / self.mass
        self.ay += fy / self.mass

    def apply_impulse(self, ix: float, iy: float):
        """Apply an instant velocity change."""
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
        self.bounds = bounds  # (x_min, y_min, x_max, y_max) or None
        self._callbacks: list = []

    def add_body(self, body: PhysicsBody):
        if body not in self.bodies:
            self.bodies.append(body)
        return self

    def remove_body(self, body: PhysicsBody):
        if body in self.bodies:
            self.bodies.remove(body)
        return self

    def add_collision_callback(self, callback):
        """Add a collision callback: fn(body_a, body_b)."""
        self._callbacks.append(callback)

    def step(self, dt: float):
        """Advance simulation by dt seconds."""
        for body in self.bodies:
            if body.is_static or not body.active:
                continue

            # Apply gravity
            body.ax += self.gravity_x
            body.ay += self.gravity_y

            # Euler integration
            body.vx += body.ax * dt
            body.vy += body.ay * dt
            body.vx *= body.friction
            body.vy *= body.friction
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
            # Circle-circle
            dx = a.center_x - b.center_x
            dy = a.center_y - b.center_y
            dist_sq = dx * dx + dy * dy
            r_sum = (a._radius or 0) + (b._radius or 0)
            return dist_sq < r_sum * r_sum
        elif a.shape_type == "rect" and b.shape_type == "rect":
            # AABB
            return (a.x < b.x + (b._width or 0) and
                    a.x + (a._width or 0) > b.x and
                    a.y < b.y + (b._height or 0) and
                    a.y + (a._height or 0) > b.y)
        else:
            # Mixed or point — use AABB approximation
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
            # Circle-circle: swap velocities along collision normal
            dx = b.center_x - a.center_x
            dy = b.center_y - a.center_y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 0.001:
                dist = 0.001
            nx, ny = dx / dist, dy / dist

            # Separation
            overlap = (a._radius or 0) + (b._radius or 0) - dist
            if overlap > 0:
                if not a.is_static:
                    a.x -= nx * overlap / 2
                    a.y -= ny * overlap / 2
                if not b.is_static:
                    b.x += nx * overlap / 2
                    b.y += ny * overlap / 2

            # Velocity reflection
            rel_vx = a.vx - b.vx
            rel_vy = a.vy - b.vy
            vel_along = rel_vx * nx + rel_vy * ny
            if vel_along > 0:
                return  # Moving apart

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
            # AABB collision: simple velocity reversal
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
