"""PixelEngine 3D objects — wireframe shapes projected onto 2D canvas.

3D primitives that render as wireframes on the pixel canvas.
Perfect for educational geometry videos.
"""
import math
from pixelengine.pobject import PObject
from pixelengine.math3d import Vec3, Mat4, project_perspective, project_isometric
from pixelengine.color import parse_color


class Object3D(PObject):
    """Base class for 3D wireframe objects.

    Stores vertices and edges in 3D space, projects them onto
    the 2D canvas for rendering.

    Attributes:
        vertices: List of Vec3 points.
        edges: List of (i, j) index pairs connecting vertices.
        rotation_x/y/z: Euler rotation angles in degrees.
        position: Vec3 world position.
        projection: "perspective" or "isometric".
    """

    def __init__(self, x: int = 128, y: int = 72, color: str = "#FFFFFF",
                 projection: str = "perspective"):
        super().__init__(x=x, y=y, color=color)
        self.vertices: list = []  # List of Vec3
        self.edges: list = []     # List of (int, int) vertex index pairs
        self.faces: list = []     # List of [i, j, k, ...] vertex index lists
        self.rotation_x: float = 0
        self.rotation_y: float = 0
        self.rotation_z: float = 0
        self.position: Vec3 = Vec3(0, 0, 5)  # Default: in front of camera
        self.obj_scale: float = 1.0
        self.projection = projection
        self.render_faces: bool = False  # Fill faces with flat color
        self.face_color = None  # Optional separate face color

    def get_transform(self) -> Mat4:
        """Build the full model transformation matrix."""
        t = Mat4.translate(self.position.x, self.position.y, self.position.z)
        rx = Mat4.rotate_x(self.rotation_x)
        ry = Mat4.rotate_y(self.rotation_y)
        rz = Mat4.rotate_z(self.rotation_z)
        s = Mat4.scale(self.obj_scale, self.obj_scale, self.obj_scale)
        return t * ry * rx * rz * s

    def project_vertices(self, screen_w: int = 256, screen_h: int = 144) -> list:
        """Project all vertices to screen coordinates.

        Returns list of (screen_x, screen_y, depth) or None for each vertex.
        """
        transform = self.get_transform()
        projected = []
        for v in self.vertices:
            world_v = transform.transform_vec3(v)
            if self.projection == "isometric":
                p = project_isometric(world_v, scale=self.obj_scale * 8,
                                      screen_w=screen_w, screen_h=screen_h)
            else:
                p = project_perspective(world_v, screen_w=screen_w,
                                        screen_h=screen_h)
            projected.append(p)
        return projected

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        projected = self.project_vertices(canvas.width, canvas.height)

        # Draw filled faces if enabled
        if self.render_faces and self.faces:
            self._render_filled_faces(canvas, projected, color)

        # Draw edges
        for i, j in self.edges:
            p1 = projected[i]
            p2 = projected[j]
            if p1 is None or p2 is None:
                continue
            self._draw_line(canvas, p1[0], p1[1], p2[0], p2[1], color)

    def _render_filled_faces(self, canvas, projected, edge_color):
        """Render filled faces with painter's algorithm and flat shading."""
        transform = self.get_transform()
        face_data = []

        for face_indices in self.faces:
            # Check all vertices are valid
            pts = [projected[i] for i in face_indices]
            if any(p is None for p in pts):
                continue

            # Calculate face center depth for painter's algorithm
            avg_depth = sum(p[2] for p in pts) / len(pts)

            # Calculate face normal for flat shading
            if len(face_indices) >= 3:
                world_verts = [transform.transform_vec3(self.vertices[i]) for i in face_indices]
                v0 = world_verts[0]
                v1 = world_verts[1]
                v2 = world_verts[2]
                # Cross product of two edges
                e1 = Vec3(v1.x - v0.x, v1.y - v0.y, v1.z - v0.z)
                e2 = Vec3(v2.x - v0.x, v2.y - v0.y, v2.z - v0.z)
                nx = e1.y * e2.z - e1.z * e2.y
                ny = e1.z * e2.x - e1.x * e2.z
                nz = e1.x * e2.y - e1.y * e2.x
                n_len = math.sqrt(nx * nx + ny * ny + nz * nz)
                if n_len > 0:
                    nx, ny, nz = nx / n_len, ny / n_len, nz / n_len
                else:
                    nx, ny, nz = 0, 0, 1

                # Simple directional light from upper-left-front
                light_dir = (0.3, -0.5, -0.8)
                l_len = math.sqrt(sum(d * d for d in light_dir))
                if l_len > 0:
                    lx, ly, lz = light_dir[0] / l_len, light_dir[1] / l_len, light_dir[2] / l_len
                else:
                    lx, ly, lz = 0.0, 0.0, -1.0

                # Lambert diffuse
                dot = max(0.0, -(nx * lx + ny * ly + nz * lz))
                shade = 0.3 + 0.7 * dot  # ambient + diffuse

                # Back-face culling
                if nz > 0:
                    continue
            else:
                shade = 0.5

            screen_pts = [(p[0], p[1]) for p in pts]
            face_data.append((avg_depth, screen_pts, shade))

        # Painter's algorithm: sort by depth (far to near)
        face_data.sort(key=lambda f: f[0], reverse=True)

        for _, screen_pts, shade in face_data:
            fc = self.face_color or self.color
            if isinstance(fc, str):
                fc = parse_color(fc)
            shaded = (
                int(fc[0] * shade),
                int(fc[1] * shade),
                int(fc[2] * shade),
                int(fc[3] * self.opacity),
            )
            self._fill_polygon(canvas, screen_pts, shaded)

    @staticmethod
    def _fill_polygon(canvas, points, color):
        """Scanline fill a convex polygon on the canvas."""
        if len(points) < 3:
            return
        min_y = max(0, min(p[1] for p in points))
        max_y = min(canvas.height - 1, max(p[1] for p in points))

        for y in range(min_y, max_y + 1):
            intersections = []
            n = len(points)
            for i in range(n):
                p1 = points[i]
                p2 = points[(i + 1) % n]
                y1, y2 = p1[1], p2[1]
                if y1 == y2:
                    continue
                if min(y1, y2) <= y < max(y1, y2):
                    x = p1[0] + (y - y1) * (p2[0] - p1[0]) / (y2 - y1)
                    intersections.append(int(x))
            intersections.sort()
            for i in range(0, len(intersections) - 1, 2):
                x_start = max(0, intersections[i])
                x_end = min(canvas.width - 1, intersections[i + 1])
                for x in range(x_start, x_end + 1):
                    canvas.set_pixel(x, y, color)

    @staticmethod
    def _draw_line(canvas, x1, y1, x2, y2, color):
        """Bresenham line drawing directly on canvas."""
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


class Cube3D(Object3D):
    """Wireframe cube.

    Usage::

        cube = Cube3D(size=1.5, color="#29ADFF")
        cube.position = Vec3(0, 0, 5)
        scene.add(cube)
        scene.play(Rotate3D(cube, axis="y", degrees=360), duration=3.0)
    """

    def __init__(self, size: float = 1.0, color: str = "#FFFFFF",
                 projection: str = "perspective", **kwargs):
        super().__init__(color=color, projection=projection, **kwargs)
        self.obj_scale = size
        s = 0.5
        # 8 vertices of a unit cube centered at origin
        self.vertices = [
            Vec3(-s, -s, -s), Vec3(s, -s, -s),
            Vec3(s, s, -s),   Vec3(-s, s, -s),
            Vec3(-s, -s, s),  Vec3(s, -s, s),
            Vec3(s, s, s),    Vec3(-s, s, s),
        ]
        # 12 edges
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
            (0, 4), (1, 5), (2, 6), (3, 7),  # Connecting edges
        ]
        # 6 faces (vertex indices, counter-clockwise from outside)
        self.faces = [
            [0, 1, 2, 3],  # Back
            [5, 4, 7, 6],  # Front
            [4, 0, 3, 7],  # Left
            [1, 5, 6, 2],  # Right
            [4, 5, 1, 0],  # Top
            [3, 2, 6, 7],  # Bottom
        ]


class Sphere3D(Object3D):
    """Wireframe sphere using latitude/longitude lines.

    Usage::

        sphere = Sphere3D(radius=1.5, segments=12, color="#FF77A8")
        scene.add(sphere)
    """

    def __init__(self, radius: float = 1.0, segments: int = 12,
                 rings: int = 8, color: str = "#FFFFFF",
                 projection: str = "perspective", **kwargs):
        super().__init__(color=color, projection=projection, **kwargs)
        self.obj_scale = radius
        self._build_sphere(segments, rings)

    def _build_sphere(self, segments, rings):
        self.vertices = []
        self.edges = []

        # Generate vertices
        for i in range(rings + 1):
            phi = math.pi * i / rings  # 0 to π
            for j in range(segments):
                theta = 2 * math.pi * j / segments  # 0 to 2π
                x = math.sin(phi) * math.cos(theta)
                y = math.cos(phi)
                z = math.sin(phi) * math.sin(theta)
                self.vertices.append(Vec3(x, y, z))

        # Generate edges — latitude lines
        for i in range(rings + 1):
            for j in range(segments):
                curr = i * segments + j
                next_j = i * segments + (j + 1) % segments
                self.edges.append((curr, next_j))

        # Generate edges — longitude lines
        for i in range(rings):
            for j in range(segments):
                curr = i * segments + j
                below = (i + 1) * segments + j
                self.edges.append((curr, below))


class Pyramid3D(Object3D):
    """Wireframe pyramid with square base.

    Usage::

        pyramid = Pyramid3D(base=1.5, height=2.0, color="#FFEC27")
        scene.add(pyramid)
    """

    def __init__(self, base: float = 1.0, height: float = 1.5,
                 color: str = "#FFFFFF",
                 projection: str = "perspective", **kwargs):
        super().__init__(color=color, projection=projection, **kwargs)
        self.obj_scale = base
        h = height / base
        s = 0.5
        self.vertices = [
            Vec3(-s, 0, -s),   # Base corners
            Vec3(s, 0, -s),
            Vec3(s, 0, s),
            Vec3(-s, 0, s),
            Vec3(0, -h, 0),    # Apex (up is -Y)
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Base
            (0, 4), (1, 4), (2, 4), (3, 4),  # Sides to apex
        ]
        # 5 faces: 1 base + 4 triangular sides
        self.faces = [
            [3, 2, 1, 0],  # Base (bottom, facing down)
            [0, 1, 4],     # Side 1
            [1, 2, 4],     # Side 2
            [2, 3, 4],     # Side 3
            [3, 0, 4],     # Side 4
        ]


class Cylinder3D(Object3D):
    """Wireframe cylinder.

    Usage::

        cyl = Cylinder3D(radius=1.0, height=2.0, segments=12, color="#00E436")
        scene.add(cyl)
    """

    def __init__(self, radius: float = 1.0, height: float = 2.0,
                 segments: int = 12, color: str = "#FFFFFF",
                 projection: str = "perspective", **kwargs):
        super().__init__(color=color, projection=projection, **kwargs)
        self.obj_scale = radius
        h = height / radius / 2
        self.vertices = []
        self.edges = []

        # Top and bottom circles
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = math.cos(angle) * 0.5
            z = math.sin(angle) * 0.5
            self.vertices.append(Vec3(x, -h, z))  # Top circle
            self.vertices.append(Vec3(x, h, z))    # Bottom circle

        # Edges
        for i in range(segments):
            top_curr = i * 2
            bot_curr = i * 2 + 1
            top_next = ((i + 1) % segments) * 2
            bot_next = ((i + 1) % segments) * 2 + 1
            self.edges.append((top_curr, top_next))  # Top circle
            self.edges.append((bot_curr, bot_next))  # Bottom circle
            self.edges.append((top_curr, bot_curr))  # Vertical


class Mesh3D(Object3D):
    """Custom wireframe mesh from vertex/edge data.

    Usage::

        mesh = Mesh3D(
            vertices=[Vec3(0,0,0), Vec3(1,0,0), Vec3(0,1,0)],
            edges=[(0,1), (1,2), (2,0)],
            color="#FF004D",
        )
        scene.add(mesh)
    """

    def __init__(self, vertices: list = None, edges: list = None,
                 color: str = "#FFFFFF",
                 projection: str = "perspective", **kwargs):
        super().__init__(color=color, projection=projection, **kwargs)
        self.vertices = vertices or []
        self.edges = edges or []


class Axes3D(Object3D):
    """3D coordinate axes with colored X, Y, Z lines.

    X = Red, Y = Green, Z = Blue (standard RGB convention).

    Usage::

        axes = Axes3D(size=2.0)
        scene.add(axes)
    """

    def __init__(self, size: float = 2.0, color: str = "#FFFFFF",
                 projection: str = "perspective", **kwargs):
        super().__init__(color=color, projection=projection, **kwargs)
        self.obj_scale = size
        self.vertices = [
            Vec3(0, 0, 0),  # Origin
            Vec3(1, 0, 0),  # X+
            Vec3(0, -1, 0), # Y+ (up)
            Vec3(0, 0, 1),  # Z+
        ]
        self.edges = [(0, 1), (0, 2), (0, 3)]
        # Colors: X=Red, Y=Green, Z=Blue
        self._axis_colors = [
            parse_color("#FF004D"),  # X
            parse_color("#00E436"),  # Y
            parse_color("#29ADFF"),  # Z
        ]

    def render(self, canvas):
        if not self.visible:
            return
        projected = self.project_vertices(canvas.width, canvas.height)
        origin = projected[0]
        if origin is None:
            return

        for idx, (i, j) in enumerate(self.edges):
            p1 = projected[i]
            p2 = projected[j]
            if p1 is None or p2 is None:
                continue
            color = self._axis_colors[idx]
            color = (*color[:3], int(color[3] * self.opacity))
            self._draw_line(canvas, p1[0], p1[1], p2[0], p2[1], color)


# ═══════════════════════════════════════════════════════════
#  3D Animations
# ═══════════════════════════════════════════════════════════

class Rotate3D:
    """Animate rotation of a 3D object around an axis.

    Usage::

        scene.play(Rotate3D(cube, axis="y", degrees=360), duration=3.0)
    """

    def __init__(self, target: Object3D, axis: str = "y",
                 degrees: float = 360, easing=None):
        from pixelengine.animation import linear
        self.target = target
        self.axis = axis
        self.degrees = degrees
        self.easing = easing or linear
        self._started = False
        self.start_angle = 0

    def interpolate(self, raw_alpha: float):
        from pixelengine.animation import get_easing
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self._started = True
            self.easing_fn = get_easing(self.easing)
            if self.axis == "x":
                self.start_angle = self.target.rotation_x
            elif self.axis == "y":
                self.start_angle = self.target.rotation_y
            elif self.axis == "z":
                self.start_angle = self.target.rotation_z

        eased = self.easing_fn(alpha)
        angle = self.start_angle + self.degrees * eased

        if self.axis == "x":
            self.target.rotation_x = angle
        elif self.axis == "y":
            self.target.rotation_y = angle
        elif self.axis == "z":
            self.target.rotation_z = angle
