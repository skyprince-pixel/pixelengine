"""PixelEngine shapes — pixel-perfect geometric primitives."""
from PIL import Image, ImageDraw
from pixelengine.pobject import PObject


class Rect(PObject):
    """Pixel-perfect filled or outlined rectangle."""

    def __init__(
        self,
        width: int,
        height: int,
        x: int = 0,
        y: int = 0,
        color: str = "#FFFFFF",
        filled: bool = True,
        border_width: int = 1,
    ):
        super().__init__(x=x, y=y, color=color)
        self.width = width
        self.height = height
        self.filled = filled
        self.border_width = border_width

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if self.filled:
            draw.rectangle(
                [0, 0, self.width - 1, self.height - 1], fill=color
            )
        else:
            for i in range(self.border_width):
                draw.rectangle(
                    [i, i, self.width - 1 - i, self.height - 1 - i],
                    outline=color,
                )
        canvas.blit(img, int(self.x), int(self.y))

    @property
    def center_x(self) -> int:
        return int(self.x + self.width // 2)

    @property
    def center_y(self) -> int:
        return int(self.y + self.height // 2)

    def __repr__(self) -> str:
        return (
            f"Rect({self.width}×{self.height} at ({self.x},{self.y}), "
            f"color={self.color})"
        )


class Circle(PObject):
    """Pixel-perfect circle using midpoint/Bresenham algorithm."""

    def __init__(
        self,
        radius: int,
        x: int = 0,
        y: int = 0,
        color: str = "#FFFFFF",
        filled: bool = True,
    ):
        super().__init__(x=x, y=y, color=color)
        self.radius = radius
        self.filled = filled

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        size = self.radius * 2 + 1
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cx, cy = self.radius, self.radius

        if self.filled:
            # Filled circle: test each pixel against radius²
            r_sq = self.radius * self.radius
            for dy in range(-self.radius, self.radius + 1):
                for dx in range(-self.radius, self.radius + 1):
                    if dx * dx + dy * dy <= r_sq:
                        px, py = cx + dx, cy + dy
                        if 0 <= px < size and 0 <= py < size:
                            img.putpixel((px, py), color)
        else:
            # Bresenham circle outline
            self._bresenham_circle(img, cx, cy, self.radius, color)

        canvas.blit(img, int(self.x), int(self.y))

    @staticmethod
    def _bresenham_circle(img, cx, cy, r, color):
        """Draw circle outline using Bresenham's midpoint algorithm."""
        x, y = 0, r
        d = 3 - 2 * r
        while x <= y:
            for px, py in [
                (cx + x, cy + y), (cx - x, cy + y),
                (cx + x, cy - y), (cx - x, cy - y),
                (cx + y, cy + x), (cx - y, cy + x),
                (cx + y, cy - x), (cx - y, cy - x),
            ]:
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    @property
    def center_x(self) -> int:
        return int(self.x + self.radius)

    @property
    def center_y(self) -> int:
        return int(self.y + self.radius)

    def __repr__(self) -> str:
        return (
            f"Circle(r={self.radius} at ({self.x},{self.y}), "
            f"color={self.color})"
        )


class Line(PObject):
    """Pixel-perfect line using Bresenham's algorithm."""

    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str = "#FFFFFF",
        thickness: int = 1,
    ):
        super().__init__(x=min(x1, x2), y=min(y1, y2), color=color)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        # Bresenham line algorithm
        dx = abs(self.x2 - self.x1)
        dy = abs(self.y2 - self.y1)
        sx = 1 if self.x1 < self.x2 else -1
        sy = 1 if self.y1 < self.y2 else -1
        err = dx - dy
        x, y = self.x1, self.y1

        half_t = self.thickness // 2
        while True:
            # Draw pixel with thickness
            for tx in range(-half_t, half_t + 1):
                for ty in range(-half_t, half_t + 1):
                    canvas.set_pixel(x + tx, y + ty, color)
            if x == self.x2 and y == self.y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    @property
    def center_x(self) -> int:
        return (self.x1 + self.x2) // 2

    @property
    def center_y(self) -> int:
        return (self.y1 + self.y2) // 2


class Triangle(PObject):
    """Filled or outlined triangle from 3 vertices."""

    def __init__(
        self,
        points: list,
        color: str = "#FFFFFF",
        filled: bool = True,
    ):
        """Create a triangle.

        Args:
            points: List of 3 (x, y) tuples — the triangle vertices.
        """
        if len(points) != 3:
            raise ValueError(f"Triangle needs 3 points, got {len(points)}")
        super().__init__(x=0, y=0, color=color)
        self.points = [(int(p[0]), int(p[1])) for p in points]
        self.filled = filled

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        if self.filled:
            self._fill_triangle(canvas, color)
        else:
            pts = self.points
            for i in range(3):
                p1, p2 = pts[i], pts[(i + 1) % 3]
                line = Line(p1[0], p1[1], p2[0], p2[1])
                line.color = self.color
                line.opacity = self.opacity
                line.render(canvas)

    def _fill_triangle(self, canvas, color):
        """Scanline fill algorithm for triangle."""
        pts = sorted(self.points, key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts

        def _interp_x(ya, xa, yb, xb, y):
            """Interpolate X for a given Y along an edge."""
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)

        for y in range(y0, y2 + 1):
            if y < y1:
                # Upper half
                xa = _interp_x(y0, x0, y2, x2, y)
                xb = _interp_x(y0, x0, y1, x1, y)
            else:
                # Lower half
                xa = _interp_x(y0, x0, y2, x2, y)
                xb = _interp_x(y1, x1, y2, x2, y)
            if xa > xb:
                xa, xb = xb, xa
            for x in range(xa, xb + 1):
                canvas.set_pixel(x, y, color)

    @property
    def center_x(self) -> int:
        return sum(p[0] for p in self.points) // 3

    @property
    def center_y(self) -> int:
        return sum(p[1] for p in self.points) // 3


class Polygon(PObject):
    """Filled or outlined polygon from N vertices."""

    def __init__(
        self,
        points: list,
        color: str = "#FFFFFF",
        filled: bool = True,
    ):
        """Create a polygon.

        Args:
            points: List of (x, y) tuples — polygon vertices.
        """
        if len(points) < 3:
            raise ValueError(f"Polygon needs ≥3 points, got {len(points)}")
        super().__init__(x=0, y=0, color=color)
        self.points = [(int(p[0]), int(p[1])) for p in points]
        self.filled = filled

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        if self.filled:
            # Use PIL ImageDraw for filled polygon rendering
            min_x = min(p[0] for p in self.points)
            min_y = min(p[1] for p in self.points)
            max_x = max(p[0] for p in self.points)
            max_y = max(p[1] for p in self.points)
            w = max_x - min_x + 1
            h = max_y - min_y + 1
            if w <= 0 or h <= 0:
                return
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            local_pts = [(p[0] - min_x, p[1] - min_y) for p in self.points]
            draw.polygon(local_pts, fill=color)
            canvas.blit(img, min_x, min_y)
        else:
            for i in range(len(self.points)):
                p1 = self.points[i]
                p2 = self.points[(i + 1) % len(self.points)]
                line = Line(p1[0], p1[1], p2[0], p2[1])
                line.color = self.color
                line.opacity = self.opacity
                line.render(canvas)

    @property
    def center_x(self) -> int:
        return sum(p[0] for p in self.points) // len(self.points)

    @property
    def center_y(self) -> int:
        return sum(p[1] for p in self.points) // len(self.points)
