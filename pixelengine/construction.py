"""PixelEngine construction animations — Manim-like gradual build effects.

Inspired by Manim's Create/GrowFromPoint/DrawBorderThenFill pattern.
Objects gradually appear by growing, tracing borders, or sweeping into view.
"""
from pixelengine.animation import Animation, linear
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


class GrowFromPoint(Animation):
    """Grow a shape from a single point to its full size.

    The object scales from 0 at (point_x, point_y) to full size at its
    original position. Creates a "pop in from point" effect.

    Usage::

        rect = Rect(40, 20, x=100, y=60, color="#FF004D")
        scene.add(rect)
        scene.play(GrowFromPoint(rect, point_x=128, point_y=72), duration=1.0)
    """

    def __init__(self, target: PObject, point_x: int = None, point_y: int = None,
                 easing=None):
        from pixelengine.animation import ease_out
        super().__init__(target, easing or ease_out)
        self.point_x = point_x
        self.point_y = point_y
        self.orig_x = None
        self.orig_y = None
        self.orig_scale_x = None
        self.orig_scale_y = None

    def on_start(self):
        self.orig_x = self.target.x
        self.orig_y = self.target.y
        self.orig_scale_x = self.target.scale_x
        self.orig_scale_y = self.target.scale_y
        # Set _base_width/_base_height so update() can scale dimensions
        if hasattr(self.target, 'width') and not hasattr(self.target, '_base_width'):
            self.target._base_width = self.target.width
            self.target._base_height = getattr(self.target, 'height', self.target.width)
        if self.point_x is None:
            cx = getattr(self.target, 'center_x', self.target.x)
            self.point_x = cx
        if self.point_y is None:
            cy = getattr(self.target, 'center_y', self.target.y)
            self.point_y = cy

    def update(self, alpha: float):
        # Scale from 0 to original
        self.target.scale_x = self.orig_scale_x * alpha
        self.target.scale_y = self.orig_scale_y * alpha
        # Position interpolates from point to original
        self.target.x = self.point_x + (self.orig_x - self.point_x) * alpha
        self.target.y = self.point_y + (self.orig_y - self.point_y) * alpha
        # Update width/height for shapes that have them
        if hasattr(self.target, '_base_width'):
            self.target.width = max(1, int(self.target._base_width * alpha))
            self.target.height = max(1, int(self.target._base_height * alpha))

    def on_complete(self):
        self.target.x = self.orig_x
        self.target.y = self.orig_y
        self.target.scale_x = self.orig_scale_x
        self.target.scale_y = self.orig_scale_y
        if hasattr(self.target, '_base_width'):
            self.target.width = self.target._base_width
            self.target.height = self.target._base_height


class GrowFromEdge(Animation):
    """Grow a rect/bar from one edge to full size.

    Perfect for bar chart animations! The bar extends from the specified
    edge (bottom, top, left, right) to its full dimensions.

    Usage::

        bar = Rect(20, 60, x=50, y=40, color="#00E436")
        scene.add(bar)
        scene.play(GrowFromEdge(bar, edge="bottom"), duration=1.0)
    """

    EDGES = ("bottom", "top", "left", "right")

    def __init__(self, target: PObject, edge: str = "bottom", easing=None):
        from pixelengine.animation import ease_out
        super().__init__(target, easing or ease_out)
        if edge not in self.EDGES:
            raise ValueError(f"edge must be one of {self.EDGES}, got {edge!r}")
        self.edge = edge
        self.orig_width = None
        self.orig_height = None
        self.orig_x = None
        self.orig_y = None

    def on_start(self):
        self.orig_width = getattr(self.target, 'width', 0)
        self.orig_height = getattr(self.target, 'height', 0)
        self.orig_x = self.target.x
        self.orig_y = self.target.y

    def update(self, alpha: float):
        if self.edge == "bottom":
            # Grow upward from bottom edge
            new_h = max(1, int(self.orig_height * alpha))
            self.target.height = new_h
            self.target.y = self.orig_y + (self.orig_height - new_h)
            self.target.width = self.orig_width
            self.target.x = self.orig_x
        elif self.edge == "top":
            # Grow downward from top edge
            new_h = max(1, int(self.orig_height * alpha))
            self.target.height = new_h
            self.target.y = self.orig_y
            self.target.width = self.orig_width
            self.target.x = self.orig_x
        elif self.edge == "left":
            # Grow rightward from left edge
            new_w = max(1, int(self.orig_width * alpha))
            self.target.width = new_w
            self.target.x = self.orig_x
            self.target.height = self.orig_height
            self.target.y = self.orig_y
        elif self.edge == "right":
            # Grow leftward from right edge
            new_w = max(1, int(self.orig_width * alpha))
            self.target.width = new_w
            self.target.x = self.orig_x + (self.orig_width - new_w)
            self.target.height = self.orig_height
            self.target.y = self.orig_y

    def on_complete(self):
        self.target.width = self.orig_width
        self.target.height = self.orig_height
        self.target.x = self.orig_x
        self.target.y = self.orig_y


class DrawBorderThenFill(Animation):
    """Trace a shape's border, then fill the interior.

    First half of the animation draws the outline progressively,
    second half fills the shape.

    Usage::

        tri = Triangle([(64, 100), (128, 30), (192, 100)], color="#FF004D")
        scene.add(tri)
        scene.play(DrawBorderThenFill(tri), duration=2.0)
    """

    def __init__(self, target: PObject, border_ratio: float = 0.6, easing=linear):
        super().__init__(target, easing)
        self.border_ratio = border_ratio
        self.orig_filled = None
        self.orig_opacity = None

    def on_start(self):
        self.orig_filled = getattr(self.target, 'filled', True)
        self.orig_opacity = self.target.opacity
        # Start unfilled and invisible
        if hasattr(self.target, 'filled'):
            self.target.filled = False
        self.target.opacity = 0.0
        # Store draw progress
        self.target._draw_progress = 0.0

    def update(self, alpha: float):
        if alpha <= self.border_ratio:
            # Phase 1: Draw border progressively
            border_alpha = alpha / self.border_ratio
            self.target.opacity = border_alpha
            self.target._draw_progress = border_alpha
            if hasattr(self.target, 'filled'):
                self.target.filled = False
        else:
            # Phase 2: Fill the shape
            fill_alpha = (alpha - self.border_ratio) / (1.0 - self.border_ratio)
            self.target.opacity = 1.0
            self.target._draw_progress = 1.0
            if hasattr(self.target, 'filled'):
                self.target.filled = True
            # Fade in the fill
            self.target.opacity = 0.5 + 0.5 * fill_alpha

    def on_complete(self):
        if hasattr(self.target, 'filled'):
            self.target.filled = self.orig_filled
        self.target.opacity = self.orig_opacity
        if hasattr(self.target, '_draw_progress'):
            del self.target._draw_progress


class Create(Animation):
    """Progressively construct an object — it appears piece by piece.

    For shapes: reveals via a sweep from left to right.
    Objects start invisible and gradually become fully visible.

    Usage::

        circle = Circle(radius=20, x=100, y=60, color="#29ADFF")
        scene.add(circle)
        scene.play(Create(circle), duration=1.0)
    """

    def __init__(self, target: PObject, direction: str = "right", easing=linear):
        super().__init__(target, easing)
        self.direction = direction  # right, left, up, down

    def on_start(self):
        self.target.opacity = 0.0
        self.target._create_progress = 0.0

    def update(self, alpha: float):
        self.target._create_progress = alpha
        self.target.opacity = min(1.0, alpha * 1.5)

    def on_complete(self):
        self.target.opacity = 1.0
        if hasattr(self.target, '_create_progress'):
            del self.target._create_progress


class Uncreate(Animation):
    """Reverse of Create — progressively deconstruct an object.

    Usage::

        scene.play(Uncreate(circle), duration=1.0)
    """

    def __init__(self, target: PObject, easing=linear):
        super().__init__(target, easing)

    def on_start(self):
        self.target._create_progress = 1.0

    def update(self, alpha: float):
        self.target._create_progress = 1.0 - alpha
        self.target.opacity = max(0.0, 1.0 - alpha * 1.5)

    def on_complete(self):
        self.target.opacity = 0.0
        self.target.visible = False
        if hasattr(self.target, '_create_progress'):
            del self.target._create_progress


class ShowPassingFlash(Animation):
    """Highlight an object with a sweeping flash effect.

    A bright flash sweeps across the object, drawing attention to it.

    Usage::

        scene.play(ShowPassingFlash(my_text, flash_color="#FFEC27"), duration=0.5)
    """

    def __init__(self, target: PObject, flash_color: str = "#FFFFFF",
                 flash_width: float = 0.3, easing=linear):
        super().__init__(target, easing)
        self.flash_color = parse_color(flash_color)
        self.flash_width = flash_width
        self.orig_color = None

    def on_start(self):
        self.orig_color = self.target.color

    def update(self, alpha: float):
        # Flash sweeps across: create a bright zone that moves
        flash_center = alpha
        dist = abs(0.5 - flash_center)
        intensity = max(0.0, 1.0 - dist / self.flash_width)

        if intensity > 0:
            r = int(self.orig_color[0] + (self.flash_color[0] - self.orig_color[0]) * intensity)
            g = int(self.orig_color[1] + (self.flash_color[1] - self.orig_color[1]) * intensity)
            b = int(self.orig_color[2] + (self.flash_color[2] - self.orig_color[2]) * intensity)
            self.target.color = (r, g, b, self.orig_color[3])
        else:
            self.target.color = self.orig_color

    def on_complete(self):
        self.target.color = self.orig_color


class GrowArrow(Animation):
    """Grow a line/arrow from start point to end point progressively.

    Usage::

        arrow = Line(20, 70, 200, 70, color="#FFEC27", thickness=2)
        scene.add(arrow)
        scene.play(GrowArrow(arrow), duration=1.0)
    """

    def __init__(self, target, easing=None):
        from pixelengine.animation import ease_out
        super().__init__(target, easing or ease_out)
        self.start_x2 = None
        self.start_y2 = None
        self.end_x2 = None
        self.end_y2 = None

    def on_start(self):
        # For Line objects
        self.start_x2 = self.target.x1
        self.start_y2 = self.target.y1
        self.end_x2 = self.target.x2
        self.end_y2 = self.target.y2

    def update(self, alpha: float):
        self.target.x2 = int(self.start_x2 + (self.end_x2 - self.start_x2) * alpha)
        self.target.y2 = int(self.start_y2 + (self.end_y2 - self.start_y2) * alpha)

    def on_complete(self):
        self.target.x2 = self.end_x2
        self.target.y2 = self.end_y2


class RevealCircular(Animation):
    """Reveal an object through an expanding circular mask.

    Creates a spotlight/iris-in effect centered on the object.

    Usage::

        scene.play(RevealCircular(obj, cx=240, cy=135), duration=1.0)
    """

    def __init__(self, target: PObject, cx: int = None, cy: int = None,
                 max_radius: int = None, easing=None):
        from pixelengine.animation import ease_out
        super().__init__(target, easing or ease_out)
        self.cx = cx
        self.cy = cy
        self.max_radius = max_radius
        self._orig_render = None

    def on_start(self):
        if self.cx is None:
            self.cx = self.target.center_x
        if self.cy is None:
            self.cy = self.target.center_y
        if self.max_radius is None:
            w = getattr(self.target, 'width', 100) or 100
            h = getattr(self.target, 'height', 100) or 100
            import math
            self.max_radius = int(math.sqrt(w * w + h * h))
        self.target.opacity = 1.0
        self._orig_render = self.target.render

        cx, cy, max_radius = self.cx, self.cy, self.max_radius

        def masked_render(canvas, _alpha=[0.0]):
            r = int(max_radius * _alpha[0])
            if r <= 0:
                return
            canvas.set_clip_circle(cx, cy, r)
            self._orig_render(canvas)
            canvas.clear_clip_mask()

        self.target.render = masked_render
        self._masked_render = masked_render

    def update(self, alpha: float):
        self._masked_render.__defaults__ = ([alpha],)

    def on_complete(self):
        self.target.render = self._orig_render


class RevealRect(Animation):
    """Reveal an object through an expanding rectangular mask.

    Creates a wipe/reveal effect from center or edge.

    Usage::

        scene.play(RevealRect(obj, direction="center"), duration=1.0)
    """

    def __init__(self, target: PObject, direction: str = "center", easing=None):
        from pixelengine.animation import ease_out
        super().__init__(target, easing or ease_out)
        self.direction = direction  # "center", "left", "right", "top", "bottom"
        self._orig_render = None

    def on_start(self):
        self.target.opacity = 1.0
        self._orig_render = self.target.render
        self._obj_x = int(self.target.x)
        self._obj_y = int(self.target.y)
        self._obj_w = getattr(self.target, 'width', 50) or 50
        self._obj_h = getattr(self.target, 'height', 50) or 50

        direction = self.direction
        ox, oy, ow, oh = self._obj_x, self._obj_y, self._obj_w, self._obj_h
        orig_render = self._orig_render

        def masked_render(canvas, _alpha=[0.0]):
            a = _alpha[0]
            if a <= 0:
                return
            if direction == "center":
                hw = int(ow * a / 2)
                hh = int(oh * a / 2)
                cx, cy = ox + ow // 2, oy + oh // 2
                canvas.set_clip_rect(cx - hw, cy - hh, hw * 2, hh * 2)
            elif direction == "left":
                canvas.set_clip_rect(ox, oy, int(ow * a), oh)
            elif direction == "right":
                w = int(ow * a)
                canvas.set_clip_rect(ox + ow - w, oy, w, oh)
            elif direction == "top":
                canvas.set_clip_rect(ox, oy, ow, int(oh * a))
            elif direction == "bottom":
                h = int(oh * a)
                canvas.set_clip_rect(ox, oy + oh - h, ow, h)
            orig_render(canvas)
            canvas.clear_clip_mask()

        self.target.render = masked_render
        self._masked_render = masked_render

    def update(self, alpha: float):
        self._masked_render.__defaults__ = ([alpha],)

    def on_complete(self):
        self.target.render = self._orig_render
