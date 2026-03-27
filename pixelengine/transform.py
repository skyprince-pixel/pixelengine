"""PixelEngine transform animations — shape morphing and interpolation.

Inspired by Manim's Transform/ReplacementTransform. Smoothly morph one shape
into another by interpolating vertices, positions, colors, and dimensions.
"""
import math
from pixelengine.animation import Animation, linear
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


class MorphTo(Animation):
    """Morph one shape into another by interpolating properties.

    For polygon-like shapes: interpolates vertex positions.
    For rect/circle: interpolates position, size, and color.

    The source object transforms into the target shape's appearance.
    After completion, the source has the target's properties.

    Usage::

        square = Rect(30, 30, x=50, y=50, color="#FF004D")
        scene.add(square)
        scene.play(MorphTo(square, target_shape=Circle(15, x=150, y=50, color="#29ADFF")),
                   duration=1.5)
    """

    def __init__(self, source: PObject, target_shape: PObject, easing=None):
        from pixelengine.animation import ease_in_out
        super().__init__(source, easing or ease_in_out)
        self.target_shape = target_shape
        # Source properties (captured on start)
        self.src_x = None
        self.src_y = None
        self.src_color = None
        self.src_opacity = None
        # Target properties
        self.dst_x = None
        self.dst_y = None
        self.dst_color = None
        self.dst_opacity = None
        # Dimension morphing
        self.src_width = None
        self.src_height = None
        self.dst_width = None
        self.dst_height = None
        self.src_radius = None
        self.dst_radius = None
        # Point morphing (for polygons/triangles)
        self.src_points = None
        self.dst_points = None

    def on_start(self):
        # Position
        self.src_x = self.target.x
        self.src_y = self.target.y
        self.dst_x = self.target_shape.x
        self.dst_y = self.target_shape.y
        # Color
        self.src_color = self.target.color
        self.dst_color = self.target_shape.color
        # Opacity
        self.src_opacity = self.target.opacity
        self.dst_opacity = self.target_shape.opacity
        # Dimensions (Rect-like)
        self.src_width = getattr(self.target, 'width', None)
        self.src_height = getattr(self.target, 'height', None)
        self.dst_width = getattr(self.target_shape, 'width', None)
        self.dst_height = getattr(self.target_shape, 'height', None)
        # Radius (Circle-like)
        self.src_radius = getattr(self.target, 'radius', None)
        self.dst_radius = getattr(self.target_shape, 'radius', None)
        # Points (Triangle/Polygon)
        self.src_points = getattr(self.target, 'points', None)
        self.dst_points = getattr(self.target_shape, 'points', None)
        if self.src_points and self.dst_points:
            self._match_point_counts()

    def _match_point_counts(self):
        """Ensure both point lists have the same length by interpolating."""
        src = list(self.src_points)
        dst = list(self.dst_points)
        # Pad shorter list by repeating last point
        while len(src) < len(dst):
            src.append(src[-1])
        while len(dst) < len(src):
            dst.append(dst[-1])
        self.src_points = src
        self.dst_points = dst

    def update(self, alpha: float):
        # Interpolate position
        self.target.x = self.src_x + (self.dst_x - self.src_x) * alpha
        self.target.y = self.src_y + (self.dst_y - self.src_y) * alpha
        # Interpolate color
        r = int(self.src_color[0] + (self.dst_color[0] - self.src_color[0]) * alpha)
        g = int(self.src_color[1] + (self.dst_color[1] - self.src_color[1]) * alpha)
        b = int(self.src_color[2] + (self.dst_color[2] - self.src_color[2]) * alpha)
        a = int(self.src_color[3] + (self.dst_color[3] - self.src_color[3]) * alpha)
        self.target.color = (r, g, b, a)
        # Interpolate opacity
        self.target.opacity = self.src_opacity + (self.dst_opacity - self.src_opacity) * alpha
        # Interpolate dimensions
        if self.src_width is not None and self.dst_width is not None:
            self.target.width = max(1, int(self.src_width + (self.dst_width - self.src_width) * alpha))
        if self.src_height is not None and self.dst_height is not None:
            self.target.height = max(1, int(self.src_height + (self.dst_height - self.src_height) * alpha))
        # Interpolate radius
        if self.src_radius is not None and self.dst_radius is not None:
            self.target.radius = max(1, int(self.src_radius + (self.dst_radius - self.src_radius) * alpha))
        # Interpolate points
        if self.src_points and self.dst_points:
            new_points = []
            for (sx, sy), (dx, dy) in zip(self.src_points, self.dst_points):
                nx = int(sx + (dx - sx) * alpha)
                ny = int(sy + (dy - sy) * alpha)
                new_points.append((nx, ny))
            self.target.points = new_points


class ReplacementTransform(Animation):
    """Fade-morph source into target — source fades out while target fades in.

    Both objects must be in the scene. Source fades out and target fades in,
    while positions interpolate toward the target.

    Usage::

        square = Rect(30, 30, x=50, y=50, color="#FF004D")
        circle = Circle(15, x=150, y=50, color="#29ADFF")
        scene.add(square, circle)
        circle.opacity = 0.0
        scene.play(ReplacementTransform(square, circle), duration=1.0)
    """

    def __init__(self, source: PObject, target_obj: PObject, easing=None):
        from pixelengine.animation import ease_in_out
        super().__init__(source, easing or ease_in_out)
        self.target_obj = target_obj
        self.src_x = None
        self.src_y = None

    def on_start(self):
        self.src_x = self.target.x
        self.src_y = self.target.y
        self.target_obj.opacity = 0.0

    def update(self, alpha: float):
        # Source fades out
        self.target.opacity = 1.0 - alpha
        # Target fades in
        self.target_obj.opacity = alpha
        # Both move toward target position
        mid_x = self.src_x + (self.target_obj.x - self.src_x) * alpha
        mid_y = self.src_y + (self.target_obj.y - self.src_y) * alpha
        if alpha < 0.5:
            self.target.x = mid_x
            self.target.y = mid_y

    def on_complete(self):
        self.target.opacity = 0.0
        self.target.visible = False
        self.target_obj.opacity = 1.0


class TransformMatchingPoints(Animation):
    """Morph shapes by matching corresponding vertex points.

    Works best with Triangle and Polygon objects that have explicit
    vertex lists. Vertices are matched by index.

    Usage::

        tri1 = Triangle([(30, 100), (80, 30), (130, 100)], color="#FF004D")
        tri2 = Triangle([(100, 100), (160, 20), (220, 100)], color="#29ADFF")
        scene.add(tri1)
        scene.play(TransformMatchingPoints(tri1, tri2), duration=1.5)
    """

    def __init__(self, source: PObject, target_shape: PObject, easing=None):
        from pixelengine.animation import ease_in_out
        super().__init__(source, easing or ease_in_out)
        self.target_shape = target_shape
        self.src_points = None
        self.dst_points = None
        self.src_color = None
        self.dst_color = None

    def on_start(self):
        self.src_points = list(getattr(self.target, 'points', []))
        self.dst_points = list(getattr(self.target_shape, 'points', []))
        self.src_color = self.target.color
        self.dst_color = self.target_shape.color
        # Match counts
        while len(self.src_points) < len(self.dst_points):
            self.src_points.append(self.src_points[-1])
        while len(self.dst_points) < len(self.src_points):
            self.dst_points.append(self.dst_points[-1])

    def update(self, alpha: float):
        new_points = []
        for (sx, sy), (dx, dy) in zip(self.src_points, self.dst_points):
            nx = int(sx + (dx - sx) * alpha)
            ny = int(sy + (dy - sy) * alpha)
            new_points.append((nx, ny))
        self.target.points = new_points
        # Color interpolation
        r = int(self.src_color[0] + (self.dst_color[0] - self.src_color[0]) * alpha)
        g = int(self.src_color[1] + (self.dst_color[1] - self.src_color[1]) * alpha)
        b = int(self.src_color[2] + (self.dst_color[2] - self.src_color[2]) * alpha)
        a = int(self.src_color[3] + (self.dst_color[3] - self.src_color[3]) * alpha)
        self.target.color = (r, g, b, a)
