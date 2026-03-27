"""PixelEngine path animation — move objects along curves and paths.

Provides BezierPath, CircularPath, LinearPath for defining motion curves,
and FollowPath animation to move objects along them.
"""
import math
from pixelengine.animation import Animation, linear
from pixelengine.pobject import PObject


# ═══════════════════════════════════════════════════════════
#  Path Definitions
# ═══════════════════════════════════════════════════════════

class BezierPath:
    """Cubic Bézier curve defined by start, two control points, and end.

    Usage::

        path = BezierPath(
            start=(50, 200), control1=(150, 20),
            control2=(300, 20), end=(400, 200)
        )
        scene.play(FollowPath(ball, path), duration=2.0)
    """

    def __init__(self, start, control1, control2, end):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end

    def evaluate(self, t: float) -> tuple:
        """Evaluate the Bézier curve at parameter t (0→1)."""
        t = max(0.0, min(1.0, t))
        u = 1.0 - t
        x = (u ** 3 * self.start[0] +
             3 * u ** 2 * t * self.control1[0] +
             3 * u * t ** 2 * self.control2[0] +
             t ** 3 * self.end[0])
        y = (u ** 3 * self.start[1] +
             3 * u ** 2 * t * self.control1[1] +
             3 * u * t ** 2 * self.control2[1] +
             t ** 3 * self.end[1])
        return (x, y)

    def tangent(self, t: float) -> tuple:
        """Compute tangent direction at parameter t (for rotation)."""
        t = max(0.001, min(0.999, t))
        u = 1.0 - t
        # First derivative of cubic Bézier
        dx = (3 * u ** 2 * (self.control1[0] - self.start[0]) +
              6 * u * t * (self.control2[0] - self.control1[0]) +
              3 * t ** 2 * (self.end[0] - self.control2[0]))
        dy = (3 * u ** 2 * (self.control1[1] - self.start[1]) +
              6 * u * t * (self.control2[1] - self.control1[1]) +
              3 * t ** 2 * (self.end[1] - self.control2[1]))
        return (dx, dy)


class QuadraticBezierPath:
    """Quadratic Bézier curve — simpler, one control point.

    Usage::

        path = QuadraticBezierPath(start=(50, 200), control=(200, 20), end=(350, 200))
        scene.play(FollowPath(ball, path), duration=1.5)
    """

    def __init__(self, start, control, end):
        self.start = start
        self.control = control
        self.end = end

    def evaluate(self, t: float) -> tuple:
        t = max(0.0, min(1.0, t))
        u = 1.0 - t
        x = u ** 2 * self.start[0] + 2 * u * t * self.control[0] + t ** 2 * self.end[0]
        y = u ** 2 * self.start[1] + 2 * u * t * self.control[1] + t ** 2 * self.end[1]
        return (x, y)

    def tangent(self, t: float) -> tuple:
        t = max(0.001, min(0.999, t))
        u = 1.0 - t
        dx = 2 * u * (self.control[0] - self.start[0]) + 2 * t * (self.end[0] - self.control[0])
        dy = 2 * u * (self.control[1] - self.start[1]) + 2 * t * (self.end[1] - self.control[1])
        return (dx, dy)


class CircularPath:
    """Circular orbit path around a center point.

    Usage::

        orbit = CircularPath(center_x=240, center_y=135, radius=80)
        scene.play(FollowPath(dot, orbit, loops=2), duration=4.0)

    Args:
        start_angle: Starting angle in degrees (0 = right, 90 = down).
        clockwise: Direction of orbit (default True).
    """

    def __init__(self, center_x: int = 0, center_y: int = 0, radius: float = 50,
                 start_angle: float = 0, clockwise: bool = True):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.start_angle = math.radians(start_angle)
        self.clockwise = clockwise

    def evaluate(self, t: float) -> tuple:
        t = max(0.0, min(1.0, t))
        angle = self.start_angle + (1 if self.clockwise else -1) * 2 * math.pi * t
        x = self.center_x + self.radius * math.cos(angle)
        y = self.center_y + self.radius * math.sin(angle)
        return (x, y)

    def tangent(self, t: float) -> tuple:
        angle = self.start_angle + (1 if self.clockwise else -1) * 2 * math.pi * t
        dx = -math.sin(angle) * (1 if self.clockwise else -1)
        dy = math.cos(angle) * (1 if self.clockwise else -1)
        return (dx, dy)


class LinearPath:
    """Polyline path through a list of points.

    The object moves through each point in sequence, spending equal time
    on each segment.

    Usage::

        path = LinearPath([(50, 200), (150, 50), (250, 200), (350, 50)])
        scene.play(FollowPath(obj, path), duration=3.0)
    """

    def __init__(self, points):
        if len(points) < 2:
            raise ValueError("LinearPath requires at least 2 points")
        self.points = list(points)

    def evaluate(self, t: float) -> tuple:
        t = max(0.0, min(1.0, t))
        n = len(self.points) - 1  # number of segments
        segment_t = t * n
        idx = min(int(segment_t), n - 1)
        local_t = segment_t - idx
        p0 = self.points[idx]
        p1 = self.points[idx + 1]
        x = p0[0] + (p1[0] - p0[0]) * local_t
        y = p0[1] + (p1[1] - p0[1]) * local_t
        return (x, y)

    def tangent(self, t: float) -> tuple:
        t = max(0.0, min(1.0, t))
        n = len(self.points) - 1
        idx = min(int(t * n), n - 1)
        p0 = self.points[idx]
        p1 = self.points[idx + 1]
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        return (dx, dy)


# ═══════════════════════════════════════════════════════════
#  FollowPath Animation
# ═══════════════════════════════════════════════════════════

class FollowPath(Animation):
    """Move an object along a path curve.

    Usage::

        path = BezierPath(start=(50, 200), control1=(150, 20),
                          control2=(300, 20), end=(400, 200))
        scene.play(FollowPath(ball, path, rotate_along=True), duration=2.0)

    Args:
        target: The PObject to move.
        path: A path object (BezierPath, CircularPath, LinearPath).
        rotate_along: If True, rotate the object to face the direction of travel.
        loops: Number of times to traverse the path.
    """

    def __init__(self, target: PObject, path, rotate_along: bool = False,
                 loops: int = 1, easing=linear):
        super().__init__(target, easing)
        self.path = path
        self.rotate_along = rotate_along
        self.loops = max(1, loops)

    def update(self, alpha: float):
        # Handle looping
        path_alpha = (alpha * self.loops) % 1.0
        if alpha >= 1.0:
            path_alpha = 1.0

        pos = self.path.evaluate(path_alpha)
        self.target.x = pos[0]
        self.target.y = pos[1]

        if self.rotate_along and hasattr(self.path, 'tangent'):
            tx, ty = self.path.tangent(path_alpha)
            angle = math.degrees(math.atan2(ty, tx))
            self.target.angle = angle
