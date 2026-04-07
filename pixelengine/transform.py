"""PixelEngine transform animations — shape morphing and interpolation.

Inspired by Manim's Transform/ReplacementTransform. Smoothly morph one shape
into another by interpolating vertices, positions, colors, and dimensions.
"""
from pixelengine.animation import Animation
from pixelengine.pobject import PObject


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
        if self.src_points and self.dst_points:
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


class VMorph(Animation):
    """Morph one VectorObject into another by interpolating sampled path points.

    Samples N points along both source and target SVG paths, then
    interpolates between corresponding points each frame.  Also blends
    stroke colour, fill colour, width, and opacity.

    Both source and target must be ``VectorObject`` subclasses.

    Usage::

        from pixelengine import VMorph, VCircle, VRect

        circle = VCircle(radius=30, cx=240, cy=135, color="#00E436")
        rect = VRect(width=60, height=60, x=210, y=105, color="#FF004D")
        scene.add(circle)
        scene.play(VMorph(circle, rect), duration=2.0)
    """

    def __init__(self, source, target_shape, n_samples: int = 100, easing=None):
        from pixelengine.animation import ease_in_out
        super().__init__(source, easing or ease_in_out)
        self.target_shape = target_shape
        self.n_samples = n_samples
        # Captured on start
        self.src_points = None
        self.dst_points = None
        self.src_color = None
        self.dst_color = None
        self.src_fill = None
        self.dst_fill = None
        self.src_stroke_width = None
        self.dst_stroke_width = None
        self.src_opacity = None
        self.dst_opacity = None

    def _sample_paths(self, vobj, n):
        """Sample n points from all paths of a VectorObject."""
        from pixelengine.vector import VectorObject
        points = []
        if not isinstance(vobj, VectorObject) or not vobj.paths:
            # Fallback: bounding box corners
            bb = getattr(vobj, 'get_bounding_box', None)
            if bb:
                b = bb()
                cx, cy = (b[0]+b[2])/2, (b[1]+b[3])/2
                return [(cx, cy)] * n
            return [(vobj.x, vobj.y)] * n

        # Collect all points across all paths
        for pdata in vobj.paths:
            path = pdata["path"]
            length = path.length()
            if length == 0:
                continue
            path_samples = max(2, int(n * length /
                                       max(1, sum(p["path"].length()
                                                  for p in vobj.paths
                                                  if p["path"].length() > 0))))
            sx, sy = vobj.scale_x, vobj.scale_y
            for i in range(path_samples):
                t = i / max(1, path_samples - 1)
                try:
                    pt = path.point(t)
                    px = vobj.x + pt.x * sx
                    py = vobj.y + pt.y * sy
                    points.append((px, py))
                except Exception:
                    pass

        if not points:
            return [(vobj.x, vobj.y)] * n

        # Resample to exactly n points
        if len(points) < n:
            # Interpolate linearly
            import numpy as _np
            xs = _np.array([p[0] for p in points])
            ys = _np.array([p[1] for p in points])
            t_old = _np.linspace(0, 1, len(points))
            t_new = _np.linspace(0, 1, n)
            new_xs = _np.interp(t_new, t_old, xs)
            new_ys = _np.interp(t_new, t_old, ys)
            return list(zip(new_xs.tolist(), new_ys.tolist()))
        elif len(points) > n:
            # Subsample uniformly
            indices = [int(i * (len(points) - 1) / max(1, n - 1)) for i in range(n)]
            return [points[i] for i in indices]
        return points

    def on_start(self):
        self.src_points = self._sample_paths(self.target, self.n_samples)
        self.dst_points = self._sample_paths(self.target_shape, self.n_samples)
        self.src_color = self.target.color
        self.dst_color = self.target_shape.color
        self.src_fill = getattr(self.target, 'fill_color', None)
        self.dst_fill = getattr(self.target_shape, 'fill_color', None)
        self.src_stroke_width = getattr(self.target, 'stroke_width', 1.0)
        self.dst_stroke_width = getattr(self.target_shape, 'stroke_width', 1.0)
        self.src_opacity = self.target.opacity
        self.dst_opacity = self.target_shape.opacity
        # Store original render method
        self.target._vmorph_src = self.src_points
        self.target._vmorph_dst = self.dst_points
        self.target._vmorph_alpha = 0.0
        self.target._original_render = self.target.render
        self.target.render = self._morph_render

    def update(self, alpha: float):
        self.target._vmorph_alpha = alpha
        # Interpolate color
        r = int(self.src_color[0] + (self.dst_color[0] - self.src_color[0]) * alpha)
        g = int(self.src_color[1] + (self.dst_color[1] - self.src_color[1]) * alpha)
        b = int(self.src_color[2] + (self.dst_color[2] - self.src_color[2]) * alpha)
        a = int(self.src_color[3] + (self.dst_color[3] - self.src_color[3]) * alpha)
        self.target.color = (r, g, b, a)
        # Interpolate opacity
        self.target.opacity = self.src_opacity + (self.dst_opacity - self.src_opacity) * alpha
        # Interpolate stroke width
        if hasattr(self.target, 'stroke_width'):
            self.target.stroke_width = (self.src_stroke_width +
                                        (self.dst_stroke_width - self.src_stroke_width) * alpha)

    def _morph_render(self, canvas):
        """Custom render that draws interpolated points."""
        from PIL import Image, ImageDraw
        if not self.target.visible:
            return

        alpha = self.target._vmorph_alpha
        src = self.target._vmorph_src
        dst = self.target._vmorph_dst

        # Interpolate all points
        pts = []
        for (sx, sy), (dx, dy) in zip(src, dst):
            px = sx + (dx - sx) * alpha
            py = sy + (dy - sy) * alpha
            pts.append((px, py))

        if len(pts) < 2:
            return

        img = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        color = self.target.get_render_color()
        stroke = (*color[:3], int(color[3] * self.target.opacity))
        thickness = max(1, int(getattr(self.target, 'stroke_width', 1.0)))

        # Draw fill if available
        fill_color = None
        if self.src_fill and self.dst_fill:
            sf, df = self.src_fill, self.dst_fill
            fr = int(sf[0] + (df[0] - sf[0]) * alpha)
            fg = int(sf[1] + (df[1] - sf[1]) * alpha)
            fb = int(sf[2] + (df[2] - sf[2]) * alpha)
            fa = int(sf[3] + (df[3] - sf[3]) * alpha)
            fill_color = (fr, fg, fb, int(fa * self.target.opacity))

        if fill_color and len(pts) > 2:
            draw.polygon(pts, fill=fill_color)

        # Draw stroke
        draw.line(pts, fill=stroke, width=thickness, joint="curve")

        canvas.blit(img, 0, 0)

    def on_complete(self):
        # Restore original render and copy target's paths
        self._cleanup_render()
        # Copy target shape's paths if both are VectorObjects
        from pixelengine.vector import VectorObject
        if isinstance(self.target, VectorObject) and isinstance(self.target_shape, VectorObject):
            self.target.clear_paths()
            for pdata in self.target_shape.paths:
                self.target.add_path(pdata["path"], stroke=pdata["stroke"],
                                     fill=pdata["fill"], stroke_width=pdata["stroke_width"])
            self.target.x = self.target_shape.x
            self.target.y = self.target_shape.y
            self.target.scale_x = self.target_shape.scale_x
            self.target.scale_y = self.target_shape.scale_y
        if hasattr(self.target, 'fill_color'):
            self.target.fill_color = self.dst_fill
        # Cleanup
        for attr in ('_vmorph_src', '_vmorph_dst', '_vmorph_alpha'):
            if hasattr(self.target, attr):
                delattr(self.target, attr)

    def _cleanup_render(self):
        """Restore the original render method if it was replaced."""
        if hasattr(self.target, '_original_render'):
            self.target.render = self.target._original_render
            del self.target._original_render

    def __del__(self):
        """Safety net: restore render method if animation was interrupted."""
        try:
            if hasattr(self, 'target') and hasattr(self.target, '_original_render'):
                self._cleanup_render()
        except Exception:
            pass  # Best-effort cleanup during garbage collection

