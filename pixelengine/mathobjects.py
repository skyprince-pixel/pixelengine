"""PixelEngine math objects — educational primitives that self-animate.

Inspired by Manim's mobjects. NumberLine, BarChart, Graph, Axes, and
ValueTracker for reactive educational animations.
"""
import math
from pixelengine.pobject import PObject
from pixelengine.shapes import Rect, Line, Circle
from pixelengine.text import PixelText
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  ValueTracker & Updater System
# ═══════════════════════════════════════════════════════════

class ValueTracker:
    """Track an animatable numeric value.

    Used with updaters to create reactive animations where objects
    respond to changing values.

    Usage::

        tracker = ValueTracker(0)
        bar = Rect(10, 50, x=100, y=60, color="#FF004D")
        bar.add_updater(lambda obj, dt: setattr(obj, 'height',
            max(1, int(50 * tracker.value / 100))))
        scene.add(bar)
        scene.play(tracker.animate_to(100), duration=2.0)
    """

    def __init__(self, value: float = 0):
        self._value = value
        self._updaters = []

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float):
        self._value = v

    def set_value(self, v: float):
        self._value = v
        return self

    def get_value(self) -> float:
        return self._value

    def animate_to(self, target_value: float, easing=None):
        """Return an animation that smoothly changes the value."""
        return _ValueAnimation(self, target_value, easing)

    def increment(self, delta: float):
        self._value += delta
        return self


class _ValueAnimation:
    """Internal: animates a ValueTracker from current to target value."""

    def __init__(self, tracker: ValueTracker, target: float, easing=None):
        from pixelengine.animation import ease_in_out, get_easing
        self.tracker = tracker
        self.target_val = target
        self.start_val = None
        self.easing = get_easing(easing or ease_in_out)
        self._started = False

    def interpolate(self, raw_alpha: float):
        alpha = max(0.0, min(1.0, raw_alpha))
        eased = self.easing(alpha)
        if not self._started:
            self.start_val = self.tracker.value
            self._started = True
        self.tracker.value = self.start_val + (self.target_val - self.start_val) * eased


# ═══════════════════════════════════════════════════════════
#  Updater Mixin
# ═══════════════════════════════════════════════════════════

def _add_updater(self, func):
    """Add an updater function called every frame.

    Args:
        func: callback(obj, dt) — called each frame with the object and dt.
    """
    if not hasattr(self, '_updaters'):
        self._updaters = []
    self._updaters.append(func)
    return self


def _remove_updater(self, func):
    """Remove a previously added updater."""
    if hasattr(self, '_updaters'):
        self._updaters = [u for u in self._updaters if u is not func]
    return self


def _clear_updaters(self):
    """Remove all updaters."""
    self._updaters = []
    return self


# Monkey-patch PObject to support updaters
PObject.add_updater = _add_updater
PObject.remove_updater = _remove_updater
PObject.clear_updaters = _clear_updaters


# ═══════════════════════════════════════════════════════════
#  NumberLine
# ═══════════════════════════════════════════════════════════

class NumberLine(PObject):
    """Horizontal number line with tick marks and labels.

    Usage::

        nline = NumberLine(min_val=0, max_val=10, step=1,
                           x=20, y=80, width=200, color="#29ADFF")
        scene.add(nline)
    """

    def __init__(self, min_val: float = 0, max_val: float = 10,
                 step: float = 1, x: int = 20, y: int = 80,
                 width: int = 200, color: str = "#FFFFFF",
                 tick_height: int = 5, show_labels: bool = True,
                 label_color: str = None):
        super().__init__(x=x, y=y, color=color)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.width = width
        self.tick_height = tick_height
        self.show_labels = show_labels
        self.label_color = parse_color(label_color or color)
        self._build_progress = 1.0  # For animation

    def val_to_x(self, val: float) -> int:
        """Convert a numeric value to screen x-coordinate."""
        t = (val - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + t * self.width)

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        progress = getattr(self, '_build_progress', 1.0)
        draw_width = max(1, int(self.width * progress))

        # Main axis line
        for px in range(draw_width):
            canvas.set_pixel(int(self.x) + px, int(self.y), color)

        # Tick marks and labels
        val = self.min_val
        while val <= self.max_val:
            tick_x = self.val_to_x(val)
            if tick_x <= self.x + draw_width:
                # Tick mark
                for dy in range(-self.tick_height // 2, self.tick_height // 2 + 1):
                    canvas.set_pixel(tick_x, int(self.y) + dy, color)
                # Label
                if self.show_labels:
                    label = str(int(val)) if val == int(val) else f"{val:.1f}"
                    lbl_x = tick_x - len(label) * 3
                    lbl_y = int(self.y) + self.tick_height // 2 + 3
                    for i, ch in enumerate(label):
                        if ch in _MINI_DIGITS:
                            self._draw_mini_char(canvas, ch, lbl_x + i * 4, lbl_y,
                                                 self.label_color)
            val += self.step

    @staticmethod
    def _draw_mini_char(canvas, ch, x, y, color):
        """Draw a tiny 3x5 digit character."""
        if ch not in _MINI_DIGITS:
            return
        pattern = _MINI_DIGITS[ch]
        for row_idx, row in enumerate(pattern):
            for col_idx, px in enumerate(row):
                if px:
                    canvas.set_pixel(x + col_idx, y + row_idx, color)


# Mini 3x5 font for number labels
_MINI_DIGITS = {
    '0': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
    '1': [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[1,1,1]],
    '2': [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
    '3': [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
    '4': [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
    '5': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
    '6': [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
    '7': [[1,1,1],[0,0,1],[0,0,1],[0,1,0],[0,1,0]],
    '8': [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
    '9': [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]],
    '-': [[0,0,0],[0,0,0],[1,1,1],[0,0,0],[0,0,0]],
    '.': [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,1,0]],
}


# ═══════════════════════════════════════════════════════════
#  BarChart
# ═══════════════════════════════════════════════════════════

class BarChart(PObject):
    """Animated bar chart with labeled bars.

    Bars grow from bottom using GrowFromEdge-style animation.

    Usage::

        chart = BarChart(
            data=[30, 70, 50, 90, 40],
            labels=["A", "B", "C", "D", "E"],
            colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27", "#FF77A8"],
            x=30, y=20, width=200, height=100,
        )
        scene.add(chart)
        scene.play(chart.animate_build(), duration=2.0)
    """

    def __init__(self, data: list, labels: list = None,
                 colors: list = None, x: int = 30, y: int = 20,
                 width: int = 200, height: int = 100,
                 bar_spacing: int = 2, color: str = "#FFFFFF",
                 show_labels: bool = True):
        super().__init__(x=x, y=y, color=color)
        self.data = list(data)
        self.labels = labels or [str(i) for i in range(len(data))]
        self.width = width
        self.height = height
        self.bar_spacing = bar_spacing
        self.show_labels = show_labels
        self._build_progress = 1.0

        # Parse colors
        default_colors = ["#FF004D", "#00E436", "#29ADFF", "#FFEC27",
                          "#FF77A8", "#FFA300", "#AB5236", "#C2C3C7"]
        if colors:
            self.colors = [parse_color(c) for c in colors]
        else:
            self.colors = [parse_color(default_colors[i % len(default_colors)])
                           for i in range(len(data))]

    def animate_build(self):
        """Return an animation that builds the chart from bottom."""
        return _BarChartBuild(self)

    def render(self, canvas):
        if not self.visible:
            return
        n = len(self.data)
        if n == 0:
            return

        max_val = max(self.data) if max(self.data) > 0 else 1
        bar_w = max(1, (self.width - (n - 1) * self.bar_spacing) // n)
        base_y = int(self.y) + self.height
        progress = getattr(self, '_build_progress', 1.0)

        for i, val in enumerate(self.data):
            bar_h = max(1, int((val / max_val) * self.height * progress))
            bx = int(self.x) + i * (bar_w + self.bar_spacing)
            by = base_y - bar_h
            color = self.colors[i % len(self.colors)]
            # Apply opacity
            color = (*color[:3], int(color[3] * self.opacity))

            # Draw bar
            for px in range(bar_w):
                for py in range(bar_h):
                    canvas.set_pixel(bx + px, by + py, color)

            # Draw label below bar
            if self.show_labels and i < len(self.labels):
                label = self.labels[i][:3].upper()  # Max 3 chars
                lbl_x = bx + bar_w // 2 - len(label) * 3
                lbl_y = base_y + 3
                label_color = (*self.color[:3], int(self.color[3] * self.opacity))
                for ci, ch in enumerate(label):
                    if ch in _MINI_DIGITS:
                        NumberLine._draw_mini_char(canvas, ch, lbl_x + ci * 4,
                                                   lbl_y, label_color)
                    else:
                        # Fall back to main 5x7 font for letters
                        from pixelengine.text import _render_glyph, GLYPH_WIDTH, GLYPH_SPACING
                        glyph = _render_glyph(ch)
                        for row_idx, row in enumerate(glyph):
                            for col_idx, pixel in enumerate(row):
                                if pixel == '#':
                                    canvas.set_pixel(
                                        lbl_x + ci * 4 + col_idx,
                                        lbl_y + row_idx,
                                        label_color,
                                    )


class _BarChartBuild:
    """Internal: animate BarChart bars growing from zero."""

    def __init__(self, chart: BarChart, easing=None):
        from pixelengine.animation import ease_out
        self.chart = chart
        self.easing = easing or ease_out
        self._started = False

    def interpolate(self, raw_alpha: float):
        from pixelengine.animation import get_easing
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self.chart._build_progress = 0.0
            self._started = True
            self.easing_fn = get_easing(self.easing)
        eased = self.easing_fn(alpha)
        self.chart._build_progress = eased


# ═══════════════════════════════════════════════════════════
#  Axes
# ═══════════════════════════════════════════════════════════

class Axes(PObject):
    """2D coordinate axes for plotting.

    Usage::

        axes = Axes(x_range=(-5, 5, 1), y_range=(-3, 3, 1),
                    x=30, y=20, width=200, height=100,
                    color="#5F574F")
        scene.add(axes)
    """

    def __init__(self, x_range: tuple = (-5, 5, 1),
                 y_range: tuple = (-3, 3, 1),
                 x: int = 30, y: int = 20,
                 width: int = 200, height: int = 100,
                 color: str = "#5F574F",
                 show_ticks: bool = True,
                 tick_size: int = 2):
        super().__init__(x=x, y=y, color=color)
        self.x_min, self.x_max, self.x_step = x_range
        self.y_min, self.y_max, self.y_step = y_range
        self.width = width
        self.height = height
        self.show_ticks = show_ticks
        self.tick_size = tick_size

    def val_to_screen(self, vx: float, vy: float) -> tuple:
        """Convert data coordinates to screen pixel coordinates."""
        sx = self.x + (vx - self.x_min) / (self.x_max - self.x_min) * self.width
        sy = self.y + self.height - (vy - self.y_min) / (self.y_max - self.y_min) * self.height
        return int(sx), int(sy)

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()

        # Find origin on screen
        origin_sx, origin_sy = self.val_to_screen(0, 0)
        # Clamp origin to axes bounds
        origin_sx = max(int(self.x), min(int(self.x) + self.width, origin_sx))
        origin_sy = max(int(self.y), min(int(self.y) + self.height, origin_sy))

        # X axis (horizontal line through y=0)
        for px in range(self.width + 1):
            canvas.set_pixel(int(self.x) + px, origin_sy, color)

        # Y axis (vertical line through x=0)
        for py in range(self.height + 1):
            canvas.set_pixel(origin_sx, int(self.y) + py, color)

        # Tick marks
        if self.show_ticks:
            # X ticks
            vx = self.x_min
            while vx <= self.x_max:
                sx, _ = self.val_to_screen(vx, 0)
                for dy in range(-self.tick_size, self.tick_size + 1):
                    canvas.set_pixel(sx, origin_sy + dy, color)
                vx += self.x_step
            # Y ticks
            vy = self.y_min
            while vy <= self.y_max:
                _, sy = self.val_to_screen(0, vy)
                for dx in range(-self.tick_size, self.tick_size + 1):
                    canvas.set_pixel(origin_sx + dx, sy, color)
                vy += self.y_step


# ═══════════════════════════════════════════════════════════
#  Graph (Function Plotter)
# ═══════════════════════════════════════════════════════════

class Graph(PObject):
    """Plot a mathematical function on an Axes.

    The graph draws itself progressively when animated.

    Usage::

        axes = Axes(x_range=(-5, 5, 1), y_range=(-2, 2, 1),
                    x=30, y=20, width=200, height=100)
        graph = Graph(func=math.sin, axes=axes, color="#FF004D")
        scene.add(axes, graph)
        scene.play(graph.animate_draw(), duration=2.0)
    """

    def __init__(self, func, axes: Axes, color: str = "#FF004D",
                 thickness: int = 1, samples: int = 0):
        super().__init__(x=axes.x, y=axes.y, color=color)
        self.func = func
        self.axes = axes
        self.thickness = thickness
        self.samples = samples or axes.width
        self._draw_progress = 1.0

    def animate_draw(self):
        """Return an animation that draws the graph progressively."""
        return _GraphDraw(self)

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        progress = getattr(self, '_draw_progress', 1.0)
        num_samples = max(1, int(self.samples * progress))

        prev_sx, prev_sy = None, None
        for i in range(num_samples):
            t = i / max(1, self.samples - 1)
            vx = self.axes.x_min + t * (self.axes.x_max - self.axes.x_min)
            try:
                vy = self.func(vx)
            except (ValueError, ZeroDivisionError, OverflowError):
                prev_sx, prev_sy = None, None
                continue

            sx, sy = self.axes.val_to_screen(vx, vy)

            # Only render if within axes bounds
            if (int(self.axes.x) <= sx <= int(self.axes.x) + self.axes.width and
                int(self.axes.y) <= sy <= int(self.axes.y) + self.axes.height):

                # Draw connected line segments for thickness
                if prev_sx is not None:
                    steps = max(abs(sx - prev_sx), abs(sy - prev_sy), 1)
                    for s in range(steps + 1):
                        st = s / steps
                        px = int(prev_sx + (sx - prev_sx) * st)
                        py = int(prev_sy + (sy - prev_sy) * st)
                        half_t = self.thickness // 2
                        for dx in range(-half_t, half_t + 1):
                            for dy in range(-half_t, half_t + 1):
                                canvas.set_pixel(px + dx, py + dy, color)
                else:
                    half_t = self.thickness // 2
                    for dx in range(-half_t, half_t + 1):
                        for dy in range(-half_t, half_t + 1):
                            canvas.set_pixel(sx + dx, sy + dy, color)

                prev_sx, prev_sy = sx, sy
            else:
                prev_sx, prev_sy = None, None


class _GraphDraw:
    """Internal: animate Graph drawing progressively."""

    def __init__(self, graph: Graph, easing=None):
        from pixelengine.animation import ease_in_out
        self.graph = graph
        self.easing = easing or ease_in_out
        self._started = False

    def interpolate(self, raw_alpha: float):
        from pixelengine.animation import get_easing
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self.graph._draw_progress = 0.0
            self._started = True
            self.easing_fn = get_easing(self.easing)
        eased = self.easing_fn(alpha)
        self.graph._draw_progress = eased


# ═══════════════════════════════════════════════════════════
#  Dot (point marker)
# ═══════════════════════════════════════════════════════════

class Dot(PObject):
    """Small dot marker for highlighting points on graphs.

    Usage::

        dot = Dot(x=100, y=50, radius=2, color="#FFEC27")
        scene.add(dot)
    """

    def __init__(self, x: int = 0, y: int = 0, radius: int = 2,
                 color: str = "#FFFFFF"):
        super().__init__(x=x, y=y, color=color)
        self.radius = radius

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        r = self.radius
        cx, cy = int(self.x), int(self.y)
        r_sq = r * r
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r_sq:
                    canvas.set_pixel(cx + dx, cy + dy, color)
