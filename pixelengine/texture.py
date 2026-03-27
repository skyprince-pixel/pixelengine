"""PixelEngine texture system — procedural patterns and fill textures.

Pixel-art-friendly textures: checkerboard, stripes, dithering, noise,
gradients, animated and scrolling textures. Applied as fill patterns
to shapes instead of flat colors.
"""
import math
import random
from pixelengine.color import parse_color


class Texture:
    """Base class for all textures.

    A texture provides a color for any (x, y) coordinate.
    Subclasses override ``get_pixel(x, y)`` to define the pattern.

    Usage::

        tex = PatternTexture("checkerboard", color1="#FF004D", color2="#1D2B53")
        rect = Rect(60, 40, x=50, y=30, color="#FFFFFF")
        rect.fill_texture = tex
        scene.add(rect)
    """

    def __init__(self):
        self._frame = 0  # For animated textures

    def get_pixel(self, x: int, y: int) -> tuple:
        """Return RGBA color for position (x, y). Override in subclasses."""
        return (255, 255, 255, 255)

    def advance_frame(self):
        """Advance one animation frame. Called by Scene each frame."""
        self._frame += 1


class PatternTexture(Texture):
    """Built-in procedural patterns for pixel art fills.

    Available patterns:
    - ``checkerboard`` — alternating squares
    - ``stripes_h`` — horizontal stripes
    - ``stripes_v`` — vertical stripes
    - ``diagonal`` — diagonal stripes (45°)
    - ``dots`` — dot grid
    - ``crosshatch`` — cross-hatching
    - ``brick`` — brick wall pattern
    - ``herringbone`` — zig-zag herringbone

    Usage::

        tex = PatternTexture("checkerboard", cell_size=4,
                             color1="#FF004D", color2="#1D2B53")
    """

    PATTERNS = (
        "checkerboard", "stripes_h", "stripes_v", "diagonal",
        "dots", "crosshatch", "brick", "herringbone",
    )

    def __init__(self, pattern: str = "checkerboard",
                 color1: str = "#FFFFFF", color2: str = "#000000",
                 cell_size: int = 4):
        super().__init__()
        if pattern not in self.PATTERNS:
            raise ValueError(f"Unknown pattern {pattern!r}. Available: {self.PATTERNS}")
        self.pattern = pattern
        self.color1 = parse_color(color1)
        self.color2 = parse_color(color2)
        self.cell_size = max(1, cell_size)

    def get_pixel(self, x: int, y: int) -> tuple:
        cs = self.cell_size

        if self.pattern == "checkerboard":
            return self.color1 if ((x // cs) + (y // cs)) % 2 == 0 else self.color2

        elif self.pattern == "stripes_h":
            return self.color1 if (y // cs) % 2 == 0 else self.color2

        elif self.pattern == "stripes_v":
            return self.color1 if (x // cs) % 2 == 0 else self.color2

        elif self.pattern == "diagonal":
            return self.color1 if ((x + y) // cs) % 2 == 0 else self.color2

        elif self.pattern == "dots":
            cx = x % (cs * 2)
            cy = y % (cs * 2)
            if cx < cs and cy < cs:
                # Center dot
                mid = cs // 2
                if abs(cx - mid) + abs(cy - mid) <= cs // 3:
                    return self.color1
            return self.color2

        elif self.pattern == "crosshatch":
            if x % cs == 0 or y % cs == 0:
                return self.color1
            return self.color2

        elif self.pattern == "brick":
            row = y // cs
            offset = (cs // 2) * (row % 2)
            if y % cs == 0:
                return self.color1
            if (x + offset) % (cs * 2) == 0:
                return self.color1
            return self.color2

        elif self.pattern == "herringbone":
            row = y // cs
            if row % 2 == 0:
                return self.color1 if ((x + y) // cs) % 2 == 0 else self.color2
            else:
                return self.color1 if ((x - y) // cs) % 2 == 0 else self.color2

        return self.color1


class DitherTexture(Texture):
    """Ordered dithering between two colors.

    Creates retro-friendly color blending using Bayer matrix patterns.

    Usage::

        tex = DitherTexture(color1="#FF004D", color2="#29ADFF", density=0.5)
    """

    # 4x4 Bayer matrix for ordered dithering
    BAYER_4X4 = [
        [0,  8,  2, 10],
        [12, 4, 14,  6],
        [3, 11,  1,  9],
        [15, 7, 13,  5],
    ]

    def __init__(self, color1: str = "#FFFFFF", color2: str = "#000000",
                 density: float = 0.5):
        super().__init__()
        self.color1 = parse_color(color1)
        self.color2 = parse_color(color2)
        self.density = max(0.0, min(1.0, density))

    def get_pixel(self, x: int, y: int) -> tuple:
        threshold = self.BAYER_4X4[y % 4][x % 4] / 16.0
        return self.color1 if self.density > threshold else self.color2


class NoiseTexture(Texture):
    """Noise-based texture mapped to color palette.

    Uses a simple hash-based noise for deterministic pixel patterns.

    Usage::

        tex = NoiseTexture(
            colors=["#FF004D", "#FFA300", "#FFEC27", "#00E436"],
            scale=4
        )
    """

    def __init__(self, colors: list = None, scale: int = 4, seed: int = 42):
        super().__init__()
        self.colors = [parse_color(c) for c in (colors or ["#FFFFFF", "#C2C3C7"])]
        self.scale = max(1, scale)
        self.seed = seed

    def get_pixel(self, x: int, y: int) -> tuple:
        # Simple hash-based noise
        sx = x // self.scale
        sy = y // self.scale
        h = ((sx * 374761393 + sy * 668265263 + self.seed) ^ 0x5DEECE66D) & 0xFFFFFFFF
        h = ((h >> 16) ^ h) * 2654435769
        h = ((h >> 16) ^ h) & 0xFFFFFFFF
        idx = h % len(self.colors)
        return self.colors[idx]


class GradientTexture(Texture):
    """Linear gradient fill between two colors.

    Usage::

        tex = GradientTexture(color1="#FF004D", color2="#29ADFF",
                              direction="horizontal", width=60)
    """

    def __init__(self, color1: str = "#FFFFFF", color2: str = "#000000",
                 direction: str = "horizontal", width: int = 64,
                 height: int = 64):
        super().__init__()
        self.color1 = parse_color(color1)
        self.color2 = parse_color(color2)
        self.direction = direction  # horizontal, vertical, diagonal
        self.grad_width = max(1, width)
        self.grad_height = max(1, height)

    def get_pixel(self, x: int, y: int) -> tuple:
        if self.direction == "horizontal":
            t = min(1.0, x / self.grad_width)
        elif self.direction == "vertical":
            t = min(1.0, y / self.grad_height)
        elif self.direction == "diagonal":
            t = min(1.0, (x + y) / (self.grad_width + self.grad_height))
        else:
            t = 0.5

        r = int(self.color1[0] + (self.color2[0] - self.color1[0]) * t)
        g = int(self.color1[1] + (self.color2[1] - self.color1[1]) * t)
        b = int(self.color1[2] + (self.color2[2] - self.color1[2]) * t)
        a = int(self.color1[3] + (self.color2[3] - self.color1[3]) * t)
        return (r, g, b, a)


class AnimatedTexture(Texture):
    """Cycles between multiple textures at a given FPS.

    Usage::

        tex1 = PatternTexture("stripes_h", color1="#FF004D", color2="#000000")
        tex2 = PatternTexture("stripes_v", color1="#FF004D", color2="#000000")
        animated = AnimatedTexture([tex1, tex2], fps=4)
    """

    def __init__(self, textures: list, fps: int = 4):
        super().__init__()
        self.textures = textures
        self.tex_fps = max(1, fps)

    def get_pixel(self, x: int, y: int) -> tuple:
        n = len(self.textures)
        if n == 0:
            return (255, 255, 255, 255)
        # 12 FPS render / tex_fps = frames per texture cycle
        frame_per_tex = max(1, 12 // self.tex_fps)
        idx = (self._frame // frame_per_tex) % n
        return self.textures[idx].get_pixel(x, y)


class ScrollingTexture(Texture):
    """Texture that scrolls over time.

    Usage::

        base = PatternTexture("diagonal", color1="#29ADFF", color2="#1D2B53")
        scroll = ScrollingTexture(base, dx=1, dy=0)
    """

    def __init__(self, texture: Texture, dx: int = 1, dy: int = 0):
        super().__init__()
        self.texture = texture
        self.dx = dx
        self.dy = dy

    def get_pixel(self, x: int, y: int) -> tuple:
        offset_x = x - self._frame * self.dx
        offset_y = y - self._frame * self.dy
        return self.texture.get_pixel(offset_x, offset_y)
