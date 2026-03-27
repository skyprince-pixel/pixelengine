"""PixelEngine backgrounds — solid, gradient, starfield, and parallax layers."""
import math
import random
from PIL import Image, ImageDraw
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


class Background(PObject):
    """Solid color background that fills the entire canvas.

    Usage::

        bg = Background(color="#1D2B53")
        bg.z_index = -100
        scene.add(bg)
    """

    def __init__(self, color: str = "#000000"):
        super().__init__(x=0, y=0, color=color)
        self.z_index = -100  # Always behind everything

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        img = Image.new("RGBA", (canvas.width, canvas.height), color)
        canvas.blit(img, 0, 0)


class GradientBackground(PObject):
    """Vertical or horizontal gradient background.

    Usage::

        sky = GradientBackground(
            color_top="#0B0E2A",
            color_bottom="#1D2B53",
            direction="vertical",
        )
        scene.add(sky)
    """

    def __init__(
        self,
        color_top: str = "#000033",
        color_bottom: str = "#000000",
        direction: str = "vertical",
    ):
        super().__init__(x=0, y=0)
        self.color_top = parse_color(color_top)
        self.color_bottom = parse_color(color_bottom)
        self.direction = direction  # "vertical" or "horizontal"
        self.z_index = -100

    def render(self, canvas):
        if not self.visible:
            return

        # Cache the gradient image — it never changes
        cache_key = (canvas.width, canvas.height, self.direction,
                     self.color_top, self.color_bottom)
        if getattr(self, '_cache_key', None) == cache_key and self._cached_img is not None:
            canvas.blit(self._cached_img, 0, 0)
            return

        img = Image.new("RGBA", (canvas.width, canvas.height))

        if self.direction == "vertical":
            for y in range(canvas.height):
                t = y / max(1, canvas.height - 1)
                color = self._lerp_color(self.color_top, self.color_bottom, t)
                for x in range(canvas.width):
                    img.putpixel((x, y), color)
        else:
            for x in range(canvas.width):
                t = x / max(1, canvas.width - 1)
                color = self._lerp_color(self.color_top, self.color_bottom, t)
                for y in range(canvas.height):
                    img.putpixel((x, y), color)

        self._cached_img = img
        self._cache_key = cache_key
        canvas.blit(img, 0, 0)

    @staticmethod
    def _lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
        """Linear interpolation between two RGBA colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )


class Starfield(PObject):
    """Procedural starfield background with twinkling.

    Usage::

        stars = Starfield(star_count=80, seed=42)
        scene.add(stars)
    """

    def __init__(
        self,
        star_count: int = 50,
        color: str = "#FFF1E8",
        dim_color: str = "#83769C",
        seed: int = None,
        twinkle: bool = True,
    ):
        super().__init__(x=0, y=0, color=color)
        self.star_count = star_count
        self.dim_color = parse_color(dim_color)
        self.twinkle = twinkle
        self.z_index = -90
        self._stars: list = []
        self._seed = seed
        self._frame_counter = 0
        self._generated = False

    def _generate_stars(self, width: int, height: int):
        """Generate star positions (deferred until first render)."""
        rng = random.Random(self._seed)
        self._stars = []
        for _ in range(self.star_count):
            sx = rng.randint(0, width - 1)
            sy = rng.randint(0, height - 1)
            brightness = rng.choice([1, 1, 1, 2])  # Most stars dim
            twinkle_phase = rng.random()
            self._stars.append((sx, sy, brightness, twinkle_phase))
        self._generated = True

    def render(self, canvas):
        if not self.visible:
            return

        if not self._generated:
            self._generate_stars(canvas.width, canvas.height)

        self._frame_counter += 1
        bright_color = self.get_render_color()

        for sx, sy, brightness, phase in self._stars:
            # Twinkle: some stars periodically dim
            if self.twinkle:
                cycle = (self._frame_counter * 0.05 + phase * 6.28) % 6.28
                is_bright = math.sin(cycle) > 0.3
            else:
                is_bright = True

            if brightness == 2 and is_bright:
                canvas.set_pixel(sx, sy, bright_color)
            elif brightness == 2:
                canvas.set_pixel(sx, sy, self.dim_color)
            elif is_bright:
                canvas.set_pixel(sx, sy, self.dim_color)
            # brightness 1 and not bright = invisible (twinkling off)


class ParallaxLayer(PObject):
    """A scrolling background layer for parallax depth effect.

    Layers with smaller scroll_speed appear further away.

    Usage::

        far_mountains = ParallaxLayer.from_art([
            "....TTTT........TTTTT....",
            "...TTTTTT......TTTTTTT...",
            "..TTTTTTTT....TTTTTTTTT..",
            "TTTTTTTTTTTTTTTTTTTTTTTTTT",
        ], scroll_speed=0.3, color="#1D2B53", y_offset=100)
        scene.add(far_mountains)
    """

    def __init__(
        self,
        image: Image.Image,
        scroll_speed: float = 0.5,
        y_offset: int = 0,
        tile: bool = True,
    ):
        super().__init__(x=0, y=y_offset)
        self._image = image.convert("RGBA")
        self.scroll_speed = scroll_speed
        self.tile = tile
        self.z_index = -50
        self._scroll_x: float = 0

    @classmethod
    def from_art(
        cls,
        art: list,
        scroll_speed: float = 0.5,
        y_offset: int = 0,
        color_map: dict = None,
        tile: bool = True,
    ) -> "ParallaxLayer":
        """Create a parallax layer from ASCII art."""
        from pixelengine.sprite import Sprite
        img = Sprite._art_to_image(art, color_map)
        return cls(img, scroll_speed=scroll_speed, y_offset=y_offset, tile=tile)

    @classmethod
    def from_color_rows(
        cls,
        width: int,
        heights: list,
        colors: list,
        scroll_speed: float = 0.5,
        y_offset: int = 0,
    ) -> "ParallaxLayer":
        """Create a layered terrain from color strips.

        Args:
            width: Layer width in pixels.
            heights: List of row heights (top to bottom).
            colors: List of color strings (one per height band).
        """
        total_h = sum(heights)
        img = Image.new("RGBA", (width, total_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        y = 0
        for h, c in zip(heights, colors):
            color = parse_color(c)
            draw.rectangle([0, y, width - 1, y + h - 1], fill=color)
            y += h
        return cls(img, scroll_speed=scroll_speed, y_offset=y_offset, tile=True)

    def scroll(self, dx: float):
        """Manually scroll the layer by dx pixels (scaled by scroll_speed)."""
        self._scroll_x += dx * self.scroll_speed

    def render(self, canvas):
        if not self.visible:
            return

        img = self._image
        w, h = img.width, img.height
        scroll_px = int(self._scroll_x) % w if w > 0 else 0
        ry = int(self.y)

        if self.tile:
            # Tile the image across the canvas width
            start_x = -scroll_px
            while start_x < canvas.width:
                canvas.blit(img, start_x, ry)
                start_x += w
        else:
            canvas.blit(img, -scroll_px, ry)
