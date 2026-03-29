"""PixelEngine 3D math — vectors, matrices, and projection.

Lightweight 3D math for wireframe projection onto the 2D pixel canvas.
Uses pure Python + math module — no numpy dependency for 3D.
"""
import math


class Vec3:
    """3D vector with standard operations.

    Usage::

        v = Vec3(1, 2, 3)
        w = Vec3(4, 5, 6)
        cross = v.cross(w)
        length = v.length()
    """

    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __repr__(self):
        return f"Vec3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        vec_len = self.length()
        if vec_len < 1e-10:
            return Vec3(0, 0, 0)
        return Vec3(self.x / vec_len, self.y / vec_len, self.z / vec_len)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def copy(self):
        return Vec3(self.x, self.y, self.z)


class Mat4:
    """4x4 transformation matrix for 3D operations.

    Stored as a flat list of 16 floats in row-major order.
    """

    def __init__(self, data=None):
        if data is not None:
            self.m = list(data)
        else:
            # Identity matrix
            self.m = [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1,
            ]

    @staticmethod
    def identity():
        return Mat4()

    @staticmethod
    def translate(x: float, y: float, z: float):
        m = Mat4()
        m.m[3] = x
        m.m[7] = y
        m.m[11] = z
        return m

    @staticmethod
    def scale(sx: float, sy: float, sz: float):
        m = Mat4()
        m.m[0] = sx
        m.m[5] = sy
        m.m[10] = sz
        return m

    @staticmethod
    def rotate_x(angle_deg: float):
        """Rotation around X axis."""
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        m = Mat4()
        m.m[5] = c
        m.m[6] = -s
        m.m[9] = s
        m.m[10] = c
        return m

    @staticmethod
    def rotate_y(angle_deg: float):
        """Rotation around Y axis."""
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        m = Mat4()
        m.m[0] = c
        m.m[2] = s
        m.m[8] = -s
        m.m[10] = c
        return m

    @staticmethod
    def rotate_z(angle_deg: float):
        """Rotation around Z axis."""
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        m = Mat4()
        m.m[0] = c
        m.m[1] = -s
        m.m[4] = s
        m.m[5] = c
        return m

    def __mul__(self, other):
        """Matrix multiplication.

        If other is Mat4: matrix × matrix.
        If other is Vec3: matrix × vector (treats as column vector with w=1).
        """
        if isinstance(other, Mat4):
            result = Mat4([0] * 16)
            for row in range(4):
                for col in range(4):
                    s = 0
                    for k in range(4):
                        s += self.m[row * 4 + k] * other.m[k * 4 + col]
                    result.m[row * 4 + col] = s
            return result
        elif isinstance(other, Vec3):
            return self.transform_vec3(other)
        else:
            raise TypeError(f"Cannot multiply Mat4 by {type(other)}")

    def transform_vec3(self, v: Vec3) -> Vec3:
        """Transform a Vec3 by this matrix (w=1, perspective divide)."""
        x = self.m[0] * v.x + self.m[1] * v.y + self.m[2] * v.z + self.m[3]
        y = self.m[4] * v.x + self.m[5] * v.y + self.m[6] * v.z + self.m[7]
        z = self.m[8] * v.x + self.m[9] * v.y + self.m[10] * v.z + self.m[11]
        w = self.m[12] * v.x + self.m[13] * v.y + self.m[14] * v.z + self.m[15]
        if abs(w) > 1e-10:
            return Vec3(x / w, y / w, z / w)
        return Vec3(x, y, z)


def project_perspective(v: Vec3, fov: float = 60, aspect: float = 16/9,
                        near: float = 0.1, far: float = 100,
                        screen_w: int = 256, screen_h: int = 144) -> tuple:
    """Project a 3D point to 2D screen coordinates using perspective.

    Returns (screen_x, screen_y, depth) or None if behind camera.
    """
    if v.z <= near:
        return None  # Behind camera

    fov_rad = math.radians(fov)
    f = 1.0 / math.tan(fov_rad / 2)

    # Project
    px = f * v.x / v.z
    py = f * v.y / v.z

    # Map to screen coordinates
    screen_x = int(screen_w / 2 + px * screen_w / 2)
    screen_y = int(screen_h / 2 - py * screen_h / 2)

    return (screen_x, screen_y, v.z)


def project_isometric(v: Vec3, scale: float = 8,
                      screen_w: int = 256, screen_h: int = 144) -> tuple:
    """Project a 3D point to 2D using isometric projection.

    Returns (screen_x, screen_y, depth).
    """
    # Standard isometric angles
    iso_x = (v.x - v.z) * math.cos(math.radians(30)) * scale
    iso_y = (v.x + v.z) * math.sin(math.radians(30)) * scale - v.y * scale

    screen_x = int(screen_w / 2 + iso_x)
    screen_y = int(screen_h / 2 + iso_y)

    # Depth for sorting (approximate)
    depth = v.x + v.y + v.z

    return (screen_x, screen_y, depth)
