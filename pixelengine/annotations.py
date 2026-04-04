"""PixelEngine annotations — callouts, labels, and markers for educational videos."""
import math
from PIL import Image, ImageDraw
from pixelengine.pobject import PObject
from pixelengine.color import parse_color
from pixelengine.text import PixelText


class Callout(PObject):
    """Speech bubble / callout annotation pointing at a target.

    Usage::

        callout = Callout(
            text="Important!",
            target_x=100, target_y=80,
            x=140, y=40,
            style="bubble",
        )
        scene.add(callout)
    """

    def __init__(
        self,
        text: str,
        target_x: int = 0,
        target_y: int = 0,
        x: int = 0,
        y: int = 0,
        style: str = "bubble",
        bg_color: str = "#FFF1E8",
        text_color: str = "#1D2B53",
        border_color: str = "#29ADFF",
        padding: int = 4,
        scale: int = 1,
    ):
        super().__init__(x=x, y=y)
        self.text = text
        self.target_x = target_x
        self.target_y = target_y
        self.style = style  # "bubble", "arrow", "box"
        self.bg_color = parse_color(bg_color)
        self.text_color = parse_color(text_color)
        self.border_color = parse_color(border_color)
        self.padding = padding
        self.scale = scale
        self.z_index = 50

        # Calculate dimensions from text
        self._label = PixelText(text, x=0, y=0, color=text_color, scale=scale)
        self.width = self._label.width + padding * 2
        self.height = self._label.height + padding * 2

    def render(self, canvas):
        if not self.visible:
            return
        ox, oy = int(self.x), int(self.y)
        bg = (*self.bg_color[:3], int(self.bg_color[3] * self.opacity))
        border = (*self.border_color[:3], int(self.border_color[3] * self.opacity))

        img = Image.new("RGBA", (self.width + 2, self.height + 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if self.style == "bubble":
            # Rounded rectangle body
            draw.rounded_rectangle(
                [1, 1, self.width, self.height],
                radius=3, fill=bg, outline=border,
            )
        else:
            # Simple box
            draw.rectangle(
                [1, 1, self.width, self.height],
                fill=bg, outline=border,
            )

        canvas.blit(img, ox, oy)

        # Draw text inside
        self._label.x = ox + self.padding + 1
        self._label.y = oy + self.padding + 1
        self._label.opacity = self.opacity
        self._label.render(canvas)

        # Draw pointer line to target
        if self.style in ("bubble", "arrow"):
            tx, ty = int(self.target_x), int(self.target_y)
            # Connect from bottom-center of callout to target
            cx = ox + self.width // 2
            cy = oy + self.height + 2
            # Simple line using set_pixel
            self._draw_line(canvas, cx, cy, tx, ty, border)

    def _draw_line(self, canvas, x1, y1, x2, y2, color):
        """Bresenham line for the pointer."""
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


class Label(PObject):
    """Simple text label with background for annotations.

    Usage::

        label = Label("x = 42", x=100, y=50, bg_color="#1D2B53")
        scene.add(label)
    """

    def __init__(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        color: str = "#FFF1E8",
        bg_color: str = None,
        scale: int = 1,
        padding: int = 2,
    ):
        super().__init__(x=x, y=y, color=color)
        self.text = text
        self.bg_color = parse_color(bg_color) if bg_color else None
        self.scale = scale
        self.padding = padding
        self.z_index = 50

        self._label = PixelText(text, x=0, y=0, color=color, scale=scale)
        self.width = self._label.width + padding * 2
        self.height = self._label.height + padding * 2

    def render(self, canvas):
        if not self.visible:
            return
        ox, oy = int(self.x), int(self.y)

        if self.bg_color:
            bg = (*self.bg_color[:3], int(self.bg_color[3] * self.opacity))
            img = Image.new("RGBA", (self.width, self.height), bg)
            canvas.blit(img, ox, oy)

        self._label.x = ox + self.padding
        self._label.y = oy + self.padding
        self._label.opacity = self.opacity
        self._label.color = self.color
        self._label.render(canvas)


class Marker(PObject):
    """Numbered circle marker for highlighting steps or points.

    Usage::

        m1 = Marker(1, x=100, y=50)
        m2 = Marker(2, x=200, y=80)
        scene.add(m1, m2)
    """

    def __init__(
        self,
        number: int = 1,
        x: int = 0,
        y: int = 0,
        color: str = "#FF004D",
        text_color: str = "#FFF1E8",
        radius: int = 6,
    ):
        super().__init__(x=x, y=y, color=color)
        self.number = number
        self.text_color = parse_color(text_color)
        self.radius = radius
        self.z_index = 55
        self.width = radius * 2 + 1
        self.height = radius * 2 + 1

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        r = self.radius
        ox, oy = int(self.x), int(self.y)

        # Draw filled circle
        r_sq = r * r
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r_sq:
                    canvas.set_pixel(ox + r + dx, oy + r + dy, color)

        # Draw number text centered
        text = str(self.number)
        text_obj = PixelText(text, x=0, y=0, color=self.text_color, scale=1)
        text_obj.x = ox + r - text_obj.width // 2
        text_obj.y = oy + r - text_obj.height // 2
        text_obj.opacity = self.opacity
        text_obj.render(canvas)


class HighlightBox(PObject):
    """Glowing border rectangle around a target PObject.

    Usage::

        box = HighlightBox(target=my_rect, color="#FFEC27", padding=3)
        scene.add(box)
    """

    def __init__(self, target=None, x: int = 0, y: int = 0,
                 width: int = 40, height: int = 20,
                 color: str = "#FFEC27", padding: int = 3,
                 thickness: int = 1):
        super().__init__(x=x, y=y, color=color)
        self.target = target
        self.padding = padding
        self.thickness = thickness
        self.width = width
        self.height = height
        self.z_index = 45

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        p = self.padding
        t = self.thickness

        if self.target:
            ox = int(getattr(self.target, 'x', self.x)) - p
            oy = int(getattr(self.target, 'y', self.y)) - p
            w = int(getattr(self.target, 'width', self.width)) + p * 2
            h = int(getattr(self.target, 'height', self.height)) + p * 2
        else:
            ox, oy = int(self.x) - p, int(self.y) - p
            w, h = self.width + p * 2, self.height + p * 2

        for ti in range(t):
            # Top and bottom edges
            for px in range(w):
                canvas.set_pixel(ox + px, oy + ti, color)
                canvas.set_pixel(ox + px, oy + h - 1 - ti, color)
            # Left and right edges
            for py in range(h):
                canvas.set_pixel(ox + ti, oy + py, color)
                canvas.set_pixel(ox + w - 1 - ti, oy + py, color)


class PointerArrow(PObject):
    """Arrow pointing from one position to a target with optional label.

    Usage::

        arrow = PointerArrow(from_x=50, from_y=20, to_x=100, to_y=60,
                             label="important", color="#FF004D")
        scene.add(arrow)
    """

    def __init__(self, from_x: int = 0, from_y: int = 0,
                 to_x: int = 50, to_y: int = 50,
                 label: str = "", color: str = "#FF004D",
                 label_color: str = "#FFF1E8", head_size: int = 4):
        super().__init__(x=from_x, y=from_y, color=color)
        self.from_x = from_x
        self.from_y = from_y
        self.to_x = to_x
        self.to_y = to_y
        self.label = label
        self.label_color = parse_color(label_color)
        self.head_size = head_size
        self.z_index = 48

    def render(self, canvas):
        if not self.visible:
            return
        import math
        color = self.get_render_color()
        x1, y1 = int(self.from_x), int(self.from_y)
        x2, y2 = int(self.to_x), int(self.to_y)

        # Draw shaft
        Callout._draw_line(self, canvas, x1, y1, x2, y2, color)

        # Draw arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        for i in range(1, self.head_size + 1):
            for s in [-1, 1]:
                ax = int(x2 - i * math.cos(angle) + s * i * 0.5 * math.sin(angle))
                ay = int(y2 - i * math.sin(angle) - s * i * 0.5 * math.cos(angle))
                canvas.set_pixel(ax, ay, color)

        # Draw label at midpoint
        if self.label:
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2 - 6
            lbl_color = (*self.label_color[:3], int(self.label_color[3] * self.opacity))
            lbl = PixelText(self.label, x=mx, y=my, color=lbl_color, scale=1)
            lbl.render(canvas)


class AnnotationLayer(PObject):
    """Manages sequenced annotations for step-by-step educational reveals.

    Usage::

        layer = AnnotationLayer(x=0, y=0)
        layer.add_step(
            marker=Marker(1, x=50, y=30),
            highlight=HighlightBox(target=my_obj),
            arrow=PointerArrow(from_x=50, from_y=45, to_x=80, to_y=70, label="Step 1"),
        )
        layer.add_step(
            marker=Marker(2, x=120, y=30),
            highlight=HighlightBox(target=other_obj),
        )
        scene.add(layer)
        scene.play(layer.animate_to_step(1), duration=0.5)
        scene.wait(1.0)
        scene.play(layer.animate_to_step(2), duration=0.5)
    """

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x=x, y=y)
        self._steps = []  # list of {"marker", "highlight", "arrow"} dicts
        self._current_step = 0  # 0 = nothing shown
        self.z_index = 60

    def add_step(self, marker=None, highlight=None, arrow=None):
        """Add an annotation step group."""
        step = {"marker": marker, "highlight": highlight, "arrow": arrow}
        self._steps.append(step)
        return self

    def animate_to_step(self, step_num):
        """Return an animation that transitions to the given step number (1-indexed)."""
        return _AnnotationStepAnim(self, step_num)

    def render(self, canvas):
        if not self.visible:
            return
        for i, step in enumerate(self._steps):
            if i >= self._current_step:
                break
            for key in ("highlight", "arrow", "marker"):
                obj = step.get(key)
                if obj:
                    obj.opacity = self.opacity
                    obj.render(canvas)


class _AnnotationStepAnim:
    """Internal: animate AnnotationLayer to a specific step."""

    def __init__(self, layer, target_step):
        self.layer = layer
        self.target_step = target_step
        self._started = False

    def interpolate(self, raw_alpha):
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self._started = True
        # Snap to target step when animation completes
        if alpha >= 1.0:
            self.layer._current_step = self.target_step
        else:
            # Progressively reveal steps
            steps_to_show = math.ceil(self.target_step * alpha)
            self.layer._current_step = max(self.layer._current_step, steps_to_show)
