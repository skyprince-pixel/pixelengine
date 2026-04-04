"""PixelEngine vector graphics — parametric shapes, SVG paths, and bezier curves.

Provides smooth, resolution-independent vector primitives that integrate
with PixelEngine's animation system (Create, Uncreate, DrawBorderThenFill).
All shapes build ``svgelements.Path`` objects internally and render via PIL.

Classes:
    VectorObject — Base class for all vector graphics.
    VPath        — Arbitrary SVG path string or svgelements.Path.
    VLine        — Parametric line segment between two points.
    VCircle      — Parametric circle / arc.
    VRect        — Parametric rectangle with optional rounded corners.
    VPolygon     — Closed polygon from N vertices.
    VArrow       — Line segment with a triangular arrowhead.
    Vector       — Mathematical arrow originating from a custom or default origin.
    SVGMobject   — Load and render external SVG files.
"""
import os
import math
from PIL import Image, ImageDraw
try:
    import svgelements as se
except ImportError:
    se = None  # Vector graphics unavailable without svgelements

def _require_svgelements():
    if se is None:
        raise ImportError(
            "Vector graphics require the 'svgelements' package. "
            "Install it with:  pip install svgelements"
        )

from pixelengine.pobject import PObject
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  VectorObject — base class
# ═══════════════════════════════════════════════════════════

class VectorObject(PObject):
    """Base class for parametric path-based vector graphics.

    Subclasses populate ``self.paths`` with dicts containing an
    ``svgelements.Path`` and optional stroke/fill/stroke_width overrides.
    The base ``render()`` walks every path, samples points along it
    (clipped by ``_create_progress`` for animation), and draws with PIL.

    Attributes:
        stroke_width (float): Default stroke thickness in pixels.
        fill_color: Default fill color (None = no fill).
    """

    def __init__(self, x: int = 0, y: int = 0, color: str = "#FFFFFF",
                 stroke_width: float = 1.0, fill_color=None):
        _require_svgelements()
        super().__init__(x=x, y=y, color=color)
        self.paths: list[dict] = []
        self.stroke_width = stroke_width
        self.fill_color = parse_color(fill_color) if fill_color else None

    # ── Path management ────────────────────────────────────

    def add_path(self, path: "se.Path", stroke=None, fill=None, stroke_width=None):
        """Append a path with optional per-path overrides."""
        self.paths.append({
            "path": path,
            "stroke": stroke,
            "fill": fill,
            "stroke_width": stroke_width,
        })
        return self

    def clear_paths(self):
        """Remove all stored paths."""
        self.paths.clear()
        return self

    # ── Rendering ──────────────────────────────────────────

    def render(self, canvas):
        draw_alpha = getattr(self, '_create_progress', 1.0)
        if not self.visible or draw_alpha <= 0:
            return

        main_color = self.get_render_color()
        default_fill = self.fill_color

        # Full-canvas image for global positioning
        img = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        sx, sy = self.scale_x, self.scale_y

        for pdata in self.paths:
            path = pdata["path"]
            stroke = pdata["stroke"] if pdata["stroke"] is not None else main_color
            fill = pdata["fill"] if pdata["fill"] is not None else default_fill
            thickness = pdata["stroke_width"] if pdata["stroke_width"] is not None else self.stroke_width

            # Resolve colour strings
            if stroke:
                if isinstance(stroke, str):
                    stroke = parse_color(stroke)
                stroke = (*stroke[:3], int(stroke[3] * self.opacity))
            if fill:
                if isinstance(fill, str):
                    fill = parse_color(fill)
                fill = (*fill[:3], int(fill[3] * self.opacity))

            length = path.length()
            if length == 0:
                continue

            # Sample density scales with visual size
            visual_length = length * max(abs(sx), abs(sy))
            samples = max(4, int(visual_length * 2))

            # Clip path by create progress
            limit = int(samples * draw_alpha)
            if limit < 1:
                continue

            pts = []
            for i in range(limit + 1):
                t = i / samples
                try:
                    pt = path.point(t)
                    px = self.x + pt.x * sx
                    py = self.y + pt.y * sy
                    pts.append((px, py))
                except Exception:
                    pass

            if not pts:
                continue

            # Filled polygon when the path is complete
            if len(pts) > 2 and fill and draw_alpha >= 0.99:
                draw.polygon(pts, fill=fill)

            # Stroke
            if len(pts) > 1 and stroke and thickness > 0:
                thk = max(1, int(thickness * max(abs(sx), abs(sy))))
                draw.line(pts, fill=stroke, width=thk, joint="curve")

        canvas.blit(img, 0, 0)

    # ── Geometry helpers ───────────────────────────────────

    def get_bounding_box(self):
        """Return (min_x, min_y, max_x, max_y) of all path points."""
        all_x, all_y = [], []
        for pdata in self.paths:
            path = pdata["path"]
            length = path.length()
            if length == 0:
                continue
            samples = max(4, int(length * 2))
            for i in range(samples + 1):
                t = i / samples
                try:
                    pt = path.point(t)
                    all_x.append(self.x + pt.x * self.scale_x)
                    all_y.append(self.y + pt.y * self.scale_y)
                except Exception:
                    pass
        if not all_x:
            return (self.x, self.y, self.x, self.y)
        return (min(all_x), min(all_y), max(all_x), max(all_y))

    @property
    def center_x(self) -> int:
        bb = self.get_bounding_box()
        return int((bb[0] + bb[2]) / 2)

    @property
    def center_y(self) -> int:
        bb = self.get_bounding_box()
        return int((bb[1] + bb[3]) / 2)


# ═══════════════════════════════════════════════════════════
#  VPath — arbitrary SVG path
# ═══════════════════════════════════════════════════════════

class VPath(VectorObject):
    """Render an arbitrary SVG path string or ``svgelements.Path``.

    Usage::

        heart = VPath("M 10 80 C 40 10, 65 10, 95 80 S 150 150, 10 80",
                       x=60, y=30, color="#FF004D", stroke_width=2)
        scene.add(heart)
        scene.play(Create(heart), duration=2.0)

    Args:
        path_data: An SVG path ``d`` attribute string **or** a
            pre-built ``svgelements.Path`` object.
        x, y: Render origin on canvas.
        color: Stroke colour (hex string).
        stroke_width: Stroke thickness in pixels.
        fill_color: Optional fill colour (hex string or None).
    """

    def __init__(self, path_data, x: int = 0, y: int = 0,
                 color: str = "#FFFFFF", stroke_width: float = 1.0,
                 fill_color=None):
        super().__init__(x=x, y=y, color=color, stroke_width=stroke_width,
                         fill_color=fill_color)
        if isinstance(path_data, se.Path):
            self.add_path(path_data)
        elif isinstance(path_data, str):
            self.add_path(se.Path(path_data))
        else:
            raise TypeError("path_data must be an SVG path string or svgelements.Path")


# ═══════════════════════════════════════════════════════════
#  VLine — line segment
# ═══════════════════════════════════════════════════════════

class VLine(VectorObject):
    """Smooth vector line between two points.

    Unlike the raster ``Line`` shape, ``VLine`` is resolution-independent
    and integrates with the ``Create()`` animation for progressive drawing.

    Usage::

        line = VLine(20, 80, 200, 80, color="#29ADFF", stroke_width=2)
        scene.add(line)
        scene.play(Create(line), duration=1.0)

    Args:
        x1, y1: Start point (absolute canvas coords).
        x2, y2: End point (absolute canvas coords).
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int,
                 color: str = "#FFFFFF", stroke_width: float = 1.0):
        # Origin at (0, 0); path coords are absolute
        super().__init__(x=0, y=0, color=color, stroke_width=stroke_width)
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self._build_path()

    def _build_path(self):
        self.clear_paths()
        p = se.Path()
        p.move((self.x1, self.y1))
        p.line((self.x2, self.y2))
        self.add_path(p)

    def set_points(self, x1, y1, x2, y2):
        """Update endpoints and rebuild the path."""
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self._build_path()
        return self

    @property
    def center_x(self) -> int:
        return (self.x1 + self.x2) // 2

    @property
    def center_y(self) -> int:
        return (self.y1 + self.y2) // 2


# ═══════════════════════════════════════════════════════════
#  VCircle — parametric circle
# ═══════════════════════════════════════════════════════════

class VCircle(VectorObject):
    """Smooth vector circle (or arc).

    Builds a circular SVG path using four cubic-bezier arcs (the standard
    Bézier approximation of a circle).

    Usage::

        circ = VCircle(radius=30, cx=128, cy=72,
                        color="#00E436", stroke_width=2)
        scene.add(circ)
        scene.play(Create(circ), duration=1.5)

    Args:
        radius: Circle radius in pixels.
        cx, cy: Centre of the circle (absolute canvas coords).
        fill_color: Optional fill (hex string or None).
    """

    def __init__(self, radius: int = 20, cx: int = 128, cy: int = 72,
                 color: str = "#FFFFFF", stroke_width: float = 1.0,
                 fill_color=None):
        # Origin stores the top-left of the bounding box
        super().__init__(x=0, y=0, color=color, stroke_width=stroke_width,
                         fill_color=fill_color)
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self._build_path()

    def _build_path(self):
        self.clear_paths()
        # Build a circle as a Path using svgelements' Circle -> Path
        circle = se.Circle(cx=self.cx, cy=self.cy, r=self.radius)
        self.add_path(se.Path(circle))

    @property
    def center_x(self) -> int:
        return int(self.cx)

    @property
    def center_y(self) -> int:
        return int(self.cy)


# ═══════════════════════════════════════════════════════════
#  VRect — parametric rectangle
# ═══════════════════════════════════════════════════════════

class VRect(VectorObject):
    """Smooth vector rectangle with optional rounded corners.

    Usage::

        box = VRect(width=60, height=30, rx=4, x=50, y=40,
                     color="#FFEC27", fill_color="#FF004D", stroke_width=2)
        scene.add(box)
        scene.play(Create(box), duration=1.0)

    Args:
        width, height: Rectangle dimensions in pixels.
        rx: Corner radius for rounded corners (0 = sharp).
        x, y: Top-left corner position.
        fill_color: Optional fill colour.
    """

    def __init__(self, width: int = 40, height: int = 20, rx: int = 0,
                 x: int = 0, y: int = 0, color: str = "#FFFFFF",
                 stroke_width: float = 1.0, fill_color=None):
        super().__init__(x=0, y=0, color=color, stroke_width=stroke_width,
                         fill_color=fill_color)
        self.rect_x = x
        self.rect_y = y
        self.rect_width = width
        self.rect_height = height
        self.rx = rx
        self._build_path()

    def _build_path(self):
        self.clear_paths()
        rect = se.Rect(x=self.rect_x, y=self.rect_y,
                        width=self.rect_width, height=self.rect_height,
                        rx=self.rx, ry=self.rx)
        self.add_path(se.Path(rect))

    @property
    def center_x(self) -> int:
        return int(self.rect_x + self.rect_width / 2)

    @property
    def center_y(self) -> int:
        return int(self.rect_y + self.rect_height / 2)


# ═══════════════════════════════════════════════════════════
#  VPolygon — arbitrary closed polygon
# ═══════════════════════════════════════════════════════════

class VPolygon(VectorObject):
    """Closed polygon from a list of vertex coordinates.

    Usage::

        tri = VPolygon([(64, 100), (128, 30), (192, 100)],
                        color="#FF77A8", fill_color="#AB5236",
                        stroke_width=2)
        scene.add(tri)
        scene.play(Create(tri), duration=1.5)

    Args:
        points: Iterable of ``(x, y)`` tuples (≥ 3 vertices).
        color:  Stroke colour.
        fill_color: Optional fill.
    """

    def __init__(self, points, color: str = "#FFFFFF",
                 stroke_width: float = 1.0, fill_color=None):
        super().__init__(x=0, y=0, color=color, stroke_width=stroke_width,
                         fill_color=fill_color)
        self.points = [(float(p[0]), float(p[1])) for p in points]
        if len(self.points) < 3:
            raise ValueError(f"VPolygon needs ≥ 3 points, got {len(self.points)}")
        self._build_path()

    def _build_path(self):
        self.clear_paths()
        p = se.Path()
        p.move(self.points[0])
        for pt in self.points[1:]:
            p.line(pt)
        p.closed()
        self.add_path(p)

    @property
    def center_x(self) -> int:
        return int(sum(p[0] for p in self.points) / len(self.points))

    @property
    def center_y(self) -> int:
        return int(sum(p[1] for p in self.points) / len(self.points))


# ═══════════════════════════════════════════════════════════
#  VArrow — line with arrowhead
# ═══════════════════════════════════════════════════════════

class VArrow(VectorObject):
    """Line segment with a triangular arrowhead at the tip.

    The arrowhead is a small filled triangle oriented along the line direction.

    Usage::

        arrow = VArrow(30, 100, 200, 50, color="#FFEC27",
                        stroke_width=2, head_length=8, head_width=6)
        scene.add(arrow)
        scene.play(Create(arrow), duration=1.0)

    Args:
        x1, y1: Tail (start) point.
        x2, y2: Head (end) point.
        head_length: Length of the arrowhead triangle along the shaft.
        head_width: Width of the arrowhead triangle perpendicular to the shaft.
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: int,
                 color: str = "#FFFFFF", stroke_width: float = 1.0,
                 head_length: int = 8, head_width: int = 6):
        super().__init__(x=0, y=0, color=color, stroke_width=stroke_width)
        self.x1, self.y1 = float(x1), float(y1)
        self.x2, self.y2 = float(x2), float(y2)
        self.head_length = head_length
        self.head_width = head_width
        self._build_path()

    def _build_path(self):
        self.clear_paths()

        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # Unit direction along the shaft
        ux, uy = dx / length, dy / length
        # Perpendicular
        px, py = -uy, ux

        # Where the shaft ends (a little before the tip to avoid overlap)
        shaft_end_x = self.x2 - ux * self.head_length
        shaft_end_y = self.y2 - uy * self.head_length

        # Shaft path
        shaft = se.Path()
        shaft.move((self.x1, self.y1))
        shaft.line((shaft_end_x, shaft_end_y))
        self.add_path(shaft)

        # Arrowhead triangle path (filled)
        hw = self.head_width / 2
        h_base_left = (shaft_end_x + px * hw, shaft_end_y + py * hw)
        h_base_right = (shaft_end_x - px * hw, shaft_end_y - py * hw)
        h_tip = (self.x2, self.y2)

        head = se.Path()
        head.move(h_base_left)
        head.line(h_tip)
        head.line(h_base_right)
        head.closed()
        self.add_path(head, fill=self.color, stroke=self.color)

    def set_points(self, x1, y1, x2, y2):
        """Update endpoints and rebuild."""
        self.x1, self.y1 = float(x1), float(y1)
        self.x2, self.y2 = float(x2), float(y2)
        self._build_path()
        return self

    @property
    def center_x(self) -> int:
        return int((self.x1 + self.x2) / 2)

    @property
    def center_y(self) -> int:
        return int((self.y1 + self.y2) / 2)


# ═══════════════════════════════════════════════════════════
#  Vector — mathematical vector arrow
# ═══════════════════════════════════════════════════════════

class Vector(VArrow):
    """Mathematical vector rendered as an arrow from ``origin`` to ``end``.

    Useful for physics / linear-algebra visualizations.  By default the
    origin is at the canvas centre, but you can override it.

    Usage::

        v = Vector(dx=40, dy=-30, origin_x=128, origin_y=72,
                   color="#FF004D", stroke_width=2, label="F")
        scene.add(v)
        scene.play(Create(v), duration=1.0)

    Args:
        dx, dy: Components of the vector.
        origin_x, origin_y: Tail position (defaults to 128, 72).
        label: Optional text label rendered near the midpoint.
        label_color: Colour for the label text.
    """

    def __init__(self, dx: float = 40, dy: float = 0,
                 origin_x: int = 128, origin_y: int = 72,
                 color: str = "#FFFFFF", stroke_width: float = 1.5,
                 head_length: int = 7, head_width: int = 5,
                 label: str = None, label_color: str = None):
        end_x = origin_x + dx
        end_y = origin_y + dy
        super().__init__(origin_x, origin_y, end_x, end_y,
                         color=color, stroke_width=stroke_width,
                         head_length=head_length, head_width=head_width)
        self.dx = dx
        self.dy = dy
        self.label_text = label
        self.label_color = parse_color(label_color) if label_color else None
        self._label_obj = None

    # ── Render override to add label ───────────────────────

    def render(self, canvas):
        super().render(canvas)

        if self.label_text and self.visible:
            draw_alpha = getattr(self, '_create_progress', 1.0)
            if draw_alpha < 0.5:
                return
            from pixelengine.text import PixelText
            if self._label_obj is None:
                lc = self.label_color or self.get_render_color()
                self._label_obj = PixelText(
                    self.label_text,
                    x=self.center_x, y=self.center_y - 8,
                    color=f"#{lc[0]:02X}{lc[1]:02X}{lc[2]:02X}",
                    align="center",
                )
            else:
                self._label_obj.x = self.center_x
                self._label_obj.y = self.center_y - 8
            self._label_obj.opacity = self.opacity
            self._label_obj.render(canvas)

    # ── Convenience ────────────────────────────────────────

    @property
    def magnitude(self) -> float:
        return math.hypot(self.dx, self.dy)

    @property
    def angle_degrees(self) -> float:
        return math.degrees(math.atan2(-self.dy, self.dx))  # screen-y is inverted

    def set_components(self, dx: float, dy: float):
        """Update vector components and rebuild."""
        self.dx, self.dy = dx, dy
        end_x = self.x1 + dx
        end_y = self.y1 + dy
        self.set_points(self.x1, self.y1, end_x, end_y)
        return self


# ═══════════════════════════════════════════════════════════
#  SVGMobject — load external SVG files
# ═══════════════════════════════════════════════════════════

class SVGMobject(VectorObject):
    """Load and render an external SVG file.

    Usage::

        svg = SVGMobject("logo.svg", x=100, y=100, scale=1.0)
        scene.add(svg)
        scene.play(Create(svg), duration=2.0)
    """

    def __init__(self, file_path: str, x: int = 0, y: int = 0, scale: float = 1.0):
        super().__init__(x=x, y=y)
        self.file_path = file_path
        self.scale_x = scale
        self.scale_y = scale
        self._load_svg()

    def _load_svg(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"SVG file not found: {self.file_path}")

        svg = se.SVG.parse(self.file_path)

        for element in svg.elements():
            if isinstance(element, se.Shape):
                path = se.Path(element)
                if hasattr(element, "transform"):
                    path *= element.transform

                stroke = None
                fill = None

                if getattr(element, 'stroke', None) is not None and element.stroke.value is not None:
                    c = element.stroke
                    stroke = (c.red, c.green, c.blue, int(c.alpha * 255))

                if getattr(element, 'fill', None) is not None and element.fill.value is not None:
                    c = element.fill
                    fill = (c.red, c.green, c.blue, int(c.alpha * 255))

                try:
                    sw = float(getattr(element, 'stroke_width', 1.0) or 1.0)
                except (ValueError, TypeError):
                    sw = 1.0

                if stroke is None and fill is None:
                    stroke = (255, 255, 255, 255)

                self.add_path(path, stroke=stroke, fill=fill, stroke_width=sw)
