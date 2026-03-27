"""PixelEngine simulations — pre-built physics simulations.

Ready-to-use Pendulum, Spring, Orbital, Rope, and Fluid simulations.
Each is a PObject that renders itself and advances its own physics.
"""
import math
import random
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


class Pendulum(PObject):
    """Simple pendulum simulation.

    Renders a swinging pendulum with bob and string.

    Usage::

        pend = Pendulum(pivot_x=128, pivot_y=30, length=60,
                        angle=45, color="#FF004D")
        scene.add(pend)
        scene.wait(5)  # Simulate for 5 seconds
    """

    def __init__(self, pivot_x: int = 128, pivot_y: int = 30,
                 length: int = 60, angle: float = 45,
                 damping: float = 0.995, gravity: float = 200,
                 bob_radius: int = 4, color: str = "#FF004D",
                 string_color: str = "#C2C3C7", mass: float = 1.0):
        super().__init__(x=pivot_x, y=pivot_y, color=color)
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.length = length
        self.theta = math.radians(angle)  # Current angle
        self.omega = 0.0                  # Angular velocity
        self.damping = damping
        self.gravity = gravity
        self.bob_radius = bob_radius
        self.mass = mass
        self.string_color = parse_color(string_color)
        self.z_index = 50
        self._fps: int = 24  # Set by Scene to actual FPS

    @property
    def bob_x(self) -> int:
        return int(self.pivot_x + self.length * math.sin(self.theta))

    @property
    def bob_y(self) -> int:
        return int(self.pivot_y + self.length * math.cos(self.theta))

    def render(self, canvas):
        if not self.visible:
            return

        # Step physics
        dt = 1.0 / self._fps
        alpha = -self.gravity / self.length * math.sin(self.theta)
        self.omega += alpha * dt
        self.omega *= self.damping
        self.theta += self.omega * dt

        bx, by = self.bob_x, self.bob_y
        string_color = (*self.string_color[:3], int(self.string_color[3] * self.opacity))
        bob_color = self.get_render_color()

        # Draw string (line from pivot to bob)
        self._draw_line(canvas, self.pivot_x, self.pivot_y, bx, by, string_color)

        # Draw pivot point
        canvas.set_pixel(self.pivot_x, self.pivot_y, string_color)
        canvas.set_pixel(self.pivot_x - 1, self.pivot_y, string_color)
        canvas.set_pixel(self.pivot_x + 1, self.pivot_y, string_color)

        # Draw bob
        r = self.bob_radius
        r_sq = r * r
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r_sq:
                    canvas.set_pixel(bx + dx, by + dy, bob_color)

    @staticmethod
    def _draw_line(canvas, x1, y1, x2, y2, color):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            canvas.set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy


class Spring(PObject):
    """Spring simulation with Hooke's law.

    Renders an anchor, spring coils, and attached mass.

    Usage::

        spring = Spring(anchor_x=128, anchor_y=20, rest_length=50,
                        k=100, mass_val=2.0, color="#00E436")
        scene.add(spring)
    """

    def __init__(self, anchor_x: int = 128, anchor_y: int = 20,
                 rest_length: int = 50, k: float = 100,
                 mass_val: float = 2.0, displacement: float = 30,
                 damping: float = 0.98, coils: int = 8,
                 color: str = "#00E436", spring_color: str = "#C2C3C7"):
        super().__init__(x=anchor_x, y=anchor_y, color=color)
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.rest_length = rest_length
        self.k = k
        self.mass_val = mass_val
        self.position = float(rest_length + displacement)  # Current extension
        self.velocity = 0.0
        self.damping = damping
        self.coils = coils
        self.spring_color = parse_color(spring_color)
        self.mass_size = 8
        self.z_index = 50
        self._fps: int = 24  # Set by Scene to actual FPS

    def render(self, canvas):
        if not self.visible:
            return

        # Step physics (Hooke's law: F = -kx)
        dt = 1.0 / self._fps
        extension = self.position - self.rest_length
        force = -self.k * extension
        accel = force / self.mass_val
        self.velocity += accel * dt
        self.velocity *= self.damping
        self.position += self.velocity * dt
        self.position = max(10, self.position)

        color = self.get_render_color()
        sc = (*self.spring_color[:3], int(self.spring_color[3] * self.opacity))

        mass_y = int(self.anchor_y + self.position)

        # Draw spring coils (zig-zag)
        coil_segment = self.position / (self.coils * 2)
        coil_width = 6
        for i in range(self.coils * 2):
            y1 = int(self.anchor_y + i * coil_segment)
            y2 = int(self.anchor_y + (i + 1) * coil_segment)
            if i % 2 == 0:
                x1, x2 = self.anchor_x - coil_width, self.anchor_x + coil_width
            else:
                x1, x2 = self.anchor_x + coil_width, self.anchor_x - coil_width
            Pendulum._draw_line(canvas, x1, y1, x2, y2, sc)

        # Draw anchor
        for dx in range(-3, 4):
            canvas.set_pixel(self.anchor_x + dx, self.anchor_y, sc)

        # Draw mass block
        hs = self.mass_size // 2
        for dy in range(-hs, hs + 1):
            for dx in range(-hs, hs + 1):
                canvas.set_pixel(self.anchor_x + dx, mass_y + dy, color)


class OrbitalSystem(PObject):
    """N-body gravitational orbit simulation.

    Simulates planets orbiting around each other using Newton's law.

    Usage::

        system = OrbitalSystem(G=5000)
        system.add_body(128, 72, mass=100, vx=0, vy=0, radius=5,
                        color="#FFEC27")  # Sun
        system.add_body(180, 72, mass=1, vx=0, vy=-50, radius=2,
                        color="#29ADFF")  # Planet
        scene.add(system)
    """

    def __init__(self, G: float = 5000, color: str = "#FFFFFF"):
        super().__init__(x=0, y=0, color=color)
        self.G = G
        self._bodies: list = []
        self.z_index = 50
        self.show_trails: bool = True
        self.trail_length: int = 30
        self._trails: dict = {}
        self._fps: int = 24  # Set by Scene to actual FPS

    def add_body(self, x: float, y: float, mass: float = 1,
                 vx: float = 0, vy: float = 0, radius: int = 3,
                 color: str = "#FFFFFF"):
        body = {
            'x': float(x), 'y': float(y),
            'vx': vx, 'vy': vy,
            'mass': mass, 'radius': radius,
            'color': parse_color(color),
        }
        idx = len(self._bodies)
        self._bodies.append(body)
        self._trails[idx] = []
        return self

    def render(self, canvas):
        if not self.visible:
            return

        # Step physics
        dt = 1.0 / self._fps
        n = len(self._bodies)

        # Calculate forces
        for i in range(n):
            ax, ay = 0, 0
            bi = self._bodies[i]
            for j in range(n):
                if i == j:
                    continue
                bj = self._bodies[j]
                dx = bj['x'] - bi['x']
                dy = bj['y'] - bi['y']
                dist_sq = dx * dx + dy * dy
                dist = max(1.0, dist_sq ** 0.5)
                force = self.G * bj['mass'] / dist_sq
                ax += force * dx / dist
                ay += force * dy / dist
            bi['vx'] += ax * dt
            bi['vy'] += ay * dt

        # Update positions
        for i, b in enumerate(self._bodies):
            b['x'] += b['vx'] * dt
            b['y'] += b['vy'] * dt
            # Record trail
            if self.show_trails:
                self._trails[i].append((int(b['x']), int(b['y'])))
                if len(self._trails[i]) > self.trail_length:
                    self._trails[i] = self._trails[i][-self.trail_length:]

        # Draw trails
        if self.show_trails:
            for i, trail in self._trails.items():
                bc = self._bodies[i]['color']
                tn = len(trail)
                for ti, (tx, ty) in enumerate(trail):
                    alpha = int(100 * (ti + 1) / tn)
                    tc = (*bc[:3], alpha)
                    canvas.set_pixel(tx, ty, tc)

        # Draw bodies
        for b in self._bodies:
            r = b['radius']
            cx, cy = int(b['x']), int(b['y'])
            color = (*b['color'][:3], int(b['color'][3] * self.opacity))
            r_sq = r * r
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r_sq:
                        canvas.set_pixel(cx + dx, cy + dy, color)


class Rope(PObject):
    """Verlet-integrated rope/chain simulation.

    Uses position-based dynamics for realistic rope physics.

    Usage::

        rope = Rope(start_x=64, start_y=20, end_x=192, end_y=20,
                    segments=15, color="#FFA300")
        scene.add(rope)
    """

    def __init__(self, start_x: int = 64, start_y: int = 20,
                 end_x: int = 192, end_y: int = 20,
                 segments: int = 15, gravity: float = 200,
                 pin_start: bool = True, pin_end: bool = True,
                 color: str = "#FFA300", iterations: int = 5):
        super().__init__(x=start_x, y=start_y, color=color)
        self.gravity = gravity
        self.pin_start = pin_start
        self.pin_end = pin_end
        self.iterations = iterations
        self.z_index = 50
        self._fps: int = 24  # Set by Scene to actual FPS

        # Create points along a straight line
        self._points = []
        seg_len = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5 / segments
        self.seg_length = seg_len

        for i in range(segments + 1):
            t = i / segments
            px = start_x + (end_x - start_x) * t
            py = start_y + (end_y - start_y) * t
            self._points.append({
                'x': float(px), 'y': float(py),
                'ox': float(px), 'oy': float(py),  # Old position
                'pinned': (i == 0 and pin_start) or (i == segments and pin_end),
            })

    def render(self, canvas):
        if not self.visible:
            return

        dt = 1.0 / self._fps
        color = self.get_render_color()

        # Verlet integration
        for p in self._points:
            if p['pinned']:
                continue
            vx = p['x'] - p['ox']
            vy = p['y'] - p['oy']
            p['ox'] = p['x']
            p['oy'] = p['y']
            p['x'] += vx * 0.99  # Damping
            p['y'] += vy * 0.99
            p['y'] += self.gravity * dt * dt

        # Constraint satisfaction
        for _ in range(self.iterations):
            for i in range(len(self._points) - 1):
                a = self._points[i]
                b = self._points[i + 1]
                dx = b['x'] - a['x']
                dy = b['y'] - a['y']
                dist = max(0.001, (dx*dx + dy*dy)**0.5)
                diff = (dist - self.seg_length) / dist
                if not a['pinned']:
                    a['x'] += dx * 0.5 * diff
                    a['y'] += dy * 0.5 * diff
                if not b['pinned']:
                    b['x'] -= dx * 0.5 * diff
                    b['y'] -= dy * 0.5 * diff

        # Draw segments
        for i in range(len(self._points) - 1):
            a = self._points[i]
            b = self._points[i + 1]
            Pendulum._draw_line(canvas, int(a['x']), int(a['y']),
                                int(b['x']), int(b['y']), color)

        # Draw joints
        for p in self._points:
            if p['pinned']:
                canvas.set_pixel(int(p['x']), int(p['y']), color)
                canvas.set_pixel(int(p['x']) - 1, int(p['y']), color)
                canvas.set_pixel(int(p['x']) + 1, int(p['y']), color)


class FluidParticles(PObject):
    """Simple SPH-like fluid particle simulation.

    Particles attract/repel each other to create fluid-like behavior.

    Usage::

        fluid = FluidParticles(count=50, x=100, y=30,
                               width=56, height=40, color="#29ADFF")
        scene.add(fluid)
    """

    def __init__(self, count: int = 50, x: int = 100, y: int = 30,
                 width: int = 56, height: int = 40,
                 gravity: float = 150, viscosity: float = 0.95,
                 interaction_radius: float = 8,
                 color: str = "#29ADFF", color2: str = "#1D2B53"):
        super().__init__(x=x, y=y, color=color)
        self.width_area = width
        self.height_area = height
        self.gravity = gravity
        self.viscosity = viscosity
        self.interaction_radius = interaction_radius
        self.color2 = parse_color(color2)
        self.z_index = 50
        self._fps: int = 24  # Set by Scene to actual FPS

        # Initialize particles randomly
        self._particles = []
        rng = random.Random(42)
        for _ in range(count):
            self._particles.append({
                'x': x + rng.uniform(0, width),
                'y': y + rng.uniform(0, height // 2),
                'vx': rng.uniform(-5, 5),
                'vy': rng.uniform(-2, 2),
            })

    def render(self, canvas):
        if not self.visible:
            return

        dt = 1.0 / self._fps
        color = self.get_render_color()
        ir = self.interaction_radius
        ir_sq = ir * ir

        # Simple particle interaction
        for i, p in enumerate(self._particles):
            # Gravity
            p['vy'] += self.gravity * dt

            # Particle-particle repulsion
            for j in range(i + 1, len(self._particles)):
                q = self._particles[j]
                dx = q['x'] - p['x']
                dy = q['y'] - p['y']
                dist_sq = dx * dx + dy * dy
                if dist_sq < ir_sq and dist_sq > 0.01:
                    dist = dist_sq ** 0.5
                    force = (ir - dist) / ir * 50
                    nx, ny = dx / dist, dy / dist
                    p['vx'] -= nx * force * dt
                    p['vy'] -= ny * force * dt
                    q['vx'] += nx * force * dt
                    q['vy'] += ny * force * dt

            # Damping
            p['vx'] *= self.viscosity
            p['vy'] *= self.viscosity

            # Integration
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt

            # Bounds
            bx_min = self.x
            by_min = self.y
            bx_max = self.x + self.width_area
            by_max = self.y + self.height_area

            if p['x'] < bx_min:
                p['x'] = bx_min
                p['vx'] = abs(p['vx']) * 0.5
            if p['x'] > bx_max:
                p['x'] = bx_max
                p['vx'] = -abs(p['vx']) * 0.5
            if p['y'] < by_min:
                p['y'] = by_min
                p['vy'] = abs(p['vy']) * 0.5
            if p['y'] > by_max:
                p['y'] = by_max
                p['vy'] = -abs(p['vy']) * 0.5

        # Draw particles
        for p in self._particles:
            px, py = int(p['x']), int(p['y'])
            canvas.set_pixel(px, py, color)
            canvas.set_pixel(px + 1, py, color)
            canvas.set_pixel(px, py + 1, color)
            canvas.set_pixel(px + 1, py + 1, color)

        # Draw container outline
        oc = (*self.color2[:3], int(self.color2[3] * self.opacity * 0.5))
        bx, by = int(self.x), int(self.y)
        for dx in range(self.width_area + 1):
            canvas.set_pixel(bx + dx, by + self.height_area, oc)
        for dy in range(self.height_area + 1):
            canvas.set_pixel(bx, by + dy, oc)
            canvas.set_pixel(bx + self.width_area, by + dy, oc)


class NetworkGraph(PObject):
    """Force-directed network graph simulation.

    Nodes repel each other while connecting edges pull them together like springs,
    automatically arranging the graph into an aesthetically pleasing layout.

    Usage::

        graph = NetworkGraph(x=135, y=240)
        graph.add_node("A", label="AI", color="#FF004D")
        graph.add_node("B", label="ML", color="#29ADFF")
        graph.add_edge("A", "B")
        scene.add(graph)
    """

    def __init__(self, x: int = 135, y: int = 240, node_radius: int = 6,
                 repulsion: float = 2000.0, spring_k: float = 3.0, 
                 spring_length: float = 50.0, damping: float = 0.85):
        super().__init__(x=x, y=y)
        self.node_radius = node_radius
        self.repulsion = repulsion
        self.spring_k = spring_k
        self.spring_length = spring_length
        self.damping = damping
        self.z_index = 50
        
        self.nodes = {}  # dict of node_id -> dict
        self.edges = []  # list of (node_id1, node_id2)
        self._fps: int = 24  # Set by Scene

    def add_node(self, node_id: str, label: str = "", color: str = "#29ADFF", radius: int = None):
        """Add a node to the graph."""
        self.nodes[node_id] = {
            'x': self.x + random.uniform(-20, 20),
            'y': self.y + random.uniform(-20, 20),
            'vx': 0.0, 'vy': 0.0,
            'label': label,
            'color': parse_color(color),
            'radius': radius if radius is not None else self.node_radius
        }

    def add_edge(self, id1: str, id2: str):
        """Connect two nodes with a spring."""
        if id1 in self.nodes and id2 in self.nodes:
            self.edges.append((id1, id2))

    def render(self, canvas):
        if not self.visible:
            return
            
        dt = 1.0 / self._fps
        
        # 1. Repulsion between all nodes
        node_ids = list(self.nodes.keys())
        for i in range(len(node_ids)):
            ni = self.nodes[node_ids[i]]
            for j in range(i + 1, len(node_ids)):
                nj = self.nodes[node_ids[j]]
                dx = nj['x'] - ni['x']
                dy = nj['y'] - ni['y']
                dist_sq = dx * dx + dy * dy
                if dist_sq < 0.1:
                    dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
                    dist_sq = dx * dx + dy * dy
                
                # Inverse square repulsion
                force = self.repulsion / dist_sq
                dist = dist_sq ** 0.5
                fx, fy = (dx / dist) * force, (dy / dist) * force
                
                ni['vx'] -= fx * dt
                ni['vy'] -= fy * dt
                nj['vx'] += fx * dt
                nj['vy'] += fy * dt

        # 2. Spring attraction for edges
        for id1, id2 in self.edges:
            n1 = self.nodes[id1]
            n2 = self.nodes[id2]
            dx = n2['x'] - n1['x']
            dy = n2['y'] - n1['y']
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 0.1:
                diff = dist - self.spring_length
                force = self.spring_k * diff
                fx, fy = (dx / dist) * force, (dy / dist) * force
                n1['vx'] += fx * dt
                n1['vy'] += fy * dt
                n2['vx'] -= fx * dt
                n2['vy'] -= fy * dt
                
        # 3. Center gravity (pull everything to center) & Integration
        for n in self.nodes.values():
            # Pull to center anchor to keep graph on screen
            cx_pull = self.x - n['x']
            cy_pull = self.y - n['y']
            n['vx'] += cx_pull * 0.5 * dt
            n['vy'] += cy_pull * 0.5 * dt
            
            n['vx'] *= self.damping
            n['vy'] *= self.damping
            
            n['x'] += n['vx'] * dt
            n['y'] += n['vy'] * dt

        edge_color = (130, 130, 130, int(255 * self.opacity))

        # Draw edges
        for id1, id2 in self.edges:
            n1 = self.nodes[id1]
            n2 = self.nodes[id2]
            Pendulum._draw_line(canvas, int(n1['x']), int(n1['y']), int(n2['x']), int(n2['y']), edge_color)

        # Draw nodes & labels
        from pixelengine.text import PixelText
        for n in self.nodes.values():
            r = n['radius']
            px, py = int(n['x']), int(n['y'])
            r_sq = r * r
            color = (*n['color'][:3], int(n['color'][3] * self.opacity))
            
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r_sq:
                        canvas.set_pixel(px + dx, py + dy, color)
                        
            if n['label']:
                pt = PixelText(n['label'], x=px, y=py - r - 8, align="center")
                pt.opacity = self.opacity
                pt.render(canvas)

