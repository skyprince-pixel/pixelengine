"""PixelEngine annotations — callouts, labels, and markers for educational videos."""
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
