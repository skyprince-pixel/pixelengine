"""PixelEngine backgrounds — solid, gradient, starfield, parallax, noise, and weather."""
import math
import random
import numpy as np
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
        self._cached_img = None
        self._cache_key = None

    def render(self, canvas):
        if not self.visible:
            return

        # Cache the gradient image — it never changes
        cache_key = (canvas.width, canvas.height, self.direction,
                     self.color_top, self.color_bottom, self.opacity)
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
        w = img.width
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


class MultiGradientBackground(PObject):
    """Multi-stop gradient background with linear or radial direction.

    Usage::

        sunset = MultiGradientBackground(
            stops=[(0.0, "#0B0E2A"), (0.4, "#FF6B35"), (0.7, "#F7931E"), (1.0, "#FFD700")],
            direction="vertical",
        )
        scene.add(sunset)

        spotlight = MultiGradientBackground(
            stops=[(0.0, "#FFFFFF"), (0.3, "#29ADFF"), (1.0, "#000000")],
            direction="radial",
        )
    """

    def __init__(
        self,
        stops: list = None,
        direction: str = "vertical",
    ):
        super().__init__(x=0, y=0)
        if stops is None:
            stops = [(0.0, "#000033"), (1.0, "#000000")]
        self._stops = [(pos, parse_color(c)) for pos, c in stops]
        self._stops.sort(key=lambda s: s[0])
        self.direction = direction  # "vertical", "horizontal", or "radial"
        self.z_index = -100
        self._cached_img = None
        self._cache_key = None

    def _sample_gradient(self, t: float) -> tuple:
        """Sample the multi-stop gradient at position t (0-1)."""
        t = max(0.0, min(1.0, t))
        if len(self._stops) == 0:
            return (0, 0, 0, 255)
        if t <= self._stops[0][0]:
            return self._stops[0][1]
        if t >= self._stops[-1][0]:
            return self._stops[-1][1]
        for i in range(len(self._stops) - 1):
            p0, c0 = self._stops[i]
            p1, c1 = self._stops[i + 1]
            if p0 <= t <= p1:
                local_t = (t - p0) / (p1 - p0) if p1 != p0 else 0.0
                return (
                    int(c0[0] + (c1[0] - c0[0]) * local_t),
                    int(c0[1] + (c1[1] - c0[1]) * local_t),
                    int(c0[2] + (c1[2] - c0[2]) * local_t),
                    int(c0[3] + (c1[3] - c0[3]) * local_t),
                )
        return self._stops[-1][1]

    def render(self, canvas):
        if not self.visible:
            return
        cache_key = (canvas.width, canvas.height, self.direction,
                     tuple(self._stops), self.opacity)
        if self._cache_key == cache_key and self._cached_img is not None:
            canvas.blit(self._cached_img, 0, 0)
            return

        w, h = canvas.width, canvas.height
        pixels = np.zeros((h, w, 4), dtype=np.uint8)

        if self.direction == "radial":
            cx, cy = w / 2, h / 2
            max_r = math.sqrt(cx * cx + cy * cy)
            ys = np.arange(h).reshape(-1, 1)
            xs = np.arange(w).reshape(1, -1)
            dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
            t_map = dist / max_r
            for y in range(h):
                for x in range(w):
                    pixels[y, x] = self._sample_gradient(t_map[y, x])
        else:
            if self.direction == "vertical":
                for y in range(h):
                    t = y / max(1, h - 1)
                    color = self._sample_gradient(t)
                    pixels[y, :] = color
            else:
                for x in range(w):
                    t = x / max(1, w - 1)
                    color = self._sample_gradient(t)
                    pixels[:, x] = color

        img = Image.fromarray(pixels, "RGBA")
        self._cached_img = img
        self._cache_key = cache_key
        canvas.blit(img, 0, 0)


class NoiseBackground(PObject):
    """Procedural noise background using value noise.

    Usage::

        clouds = NoiseBackground(
            palette=["#1A1A2E", "#16213E", "#0F3460", "#E94560"],
            octaves=4, seed=42,
        )
        scene.add(clouds)

        nebula = NoiseBackground(
            palette=["#0B0E2A", "#3B1F8E", "#7B2FF7", "#FF2079"],
            style="nebula",
        )
    """

    def __init__(
        self,
        palette: list = None,
        octaves: int = 4,
        seed: int = 0,
        style: str = "clouds",
    ):
        super().__init__(x=0, y=0)
        if palette is None:
            palette = ["#1A1A2E", "#16213E", "#0F3460"]
        self._palette = [parse_color(c) for c in palette]
        self.octaves = octaves
        self.seed = seed
        self.style = style  # "clouds", "nebula", "organic"
        self.z_index = -100
        self._cached_img = None
        self._cache_key = None

    def _sample_palette(self, t: float) -> tuple:
        """Map a 0-1 noise value to a color in the palette."""
        t = max(0.0, min(1.0, t))
        n = len(self._palette)
        if n == 1:
            return self._palette[0]
        idx_f = t * (n - 1)
        idx = int(idx_f)
        frac = idx_f - idx
        if idx >= n - 1:
            return self._palette[-1]
        c0, c1 = self._palette[idx], self._palette[idx + 1]
        return (
            int(c0[0] + (c1[0] - c0[0]) * frac),
            int(c0[1] + (c1[1] - c0[1]) * frac),
            int(c0[2] + (c1[2] - c0[2]) * frac),
            int(c0[3] + (c1[3] - c0[3]) * frac),
        )

    def render(self, canvas):
        if not self.visible:
            return
        cache_key = (canvas.width, canvas.height, self.octaves,
                     self.seed, self.style, tuple(self._palette))
        if self._cache_key == cache_key and self._cached_img is not None:
            canvas.blit(self._cached_img, 0, 0)
            return

        w, h = canvas.width, canvas.height

        # Generate noise using simple value noise (avoids importing terrain)
        rng = np.random.RandomState(self.seed)
        result = np.zeros((h, w), dtype=np.float64)
        amplitude = 1.0
        total_amp = 0.0
        for octave in range(self.octaves):
            freq = 2 ** octave
            n_x = max(2, freq + 1)
            n_y = max(2, freq + 1)
            control = rng.random((n_y, n_x))
            ctrl_img = Image.fromarray((control * 255).astype(np.uint8), mode="L")
            interp_img = ctrl_img.resize((w, h), Image.Resampling.BILINEAR)
            interp = np.array(interp_img).astype(np.float64) / 255.0
            result += interp * amplitude
            total_amp += amplitude
            amplitude *= 0.5
        result /= total_amp

        if self.style == "nebula":
            # Apply contrast curve for dramatic nebula look
            result = np.power(result, 1.8)
        elif self.style == "organic":
            # Softer, more uniform distribution
            result = np.sqrt(result)

        # Map noise to palette colors
        pixels = np.zeros((h, w, 4), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                pixels[y, x] = self._sample_palette(result[y, x])

        img = Image.fromarray(pixels, "RGBA")
        self._cached_img = img
        self._cache_key = cache_key
        canvas.blit(img, 0, 0)


class WeatherBackground(PObject):
    """Background-layer weather effects rendered behind scene objects.

    Usage::

        rain = WeatherBackground(style="rain", canvas_width=480, canvas_height=270)
        scene.add(rain)

        snow = WeatherBackground(style="snow", intensity=0.5)
    """

    def __init__(
        self,
        style: str = "rain",
        canvas_width: int = 480,
        canvas_height: int = 270,
        intensity: float = 1.0,
        seed: int = None,
    ):
        super().__init__(x=0, y=0)
        self.style = style
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self.intensity = intensity
        self.z_index = -80  # Behind scene objects, above backgrounds
        self._particles = []
        self._rng = random.Random(seed)
        self._initialized = False

    def _init_particles(self):
        """Generate initial weather particles."""
        count = int({
            "rain": 80,
            "snow": 40,
            "fog": 20,
        }.get(self.style, 40) * self.intensity)

        for _ in range(count):
            self._particles.append(self._new_particle(initial=True))
        self._initialized = True

    def _new_particle(self, initial=False):
        rng = self._rng
        w, h = self._canvas_width, self._canvas_height
        if self.style == "rain":
            return {
                'x': rng.randint(0, w),
                'y': rng.randint(0, h) if initial else rng.randint(-10, 0),
                'vx': rng.uniform(-0.3, 0.3),
                'vy': rng.uniform(4, 7),
                'length': rng.randint(2, 5),
                'color': parse_color(rng.choice(["#5F8FBF", "#7FAFD7", "#9FBFE7"])),
            }
        elif self.style == "snow":
            return {
                'x': rng.randint(0, w),
                'y': rng.randint(0, h) if initial else rng.randint(-10, 0),
                'vx': rng.uniform(-0.5, 0.5),
                'vy': rng.uniform(0.3, 1.0),
                'size': rng.choice([1, 1, 1, 2]),
                'color': parse_color(rng.choice(["#FFF1E8", "#C2C3C7", "#FFFFFF"])),
                'phase': rng.random() * 6.28,
            }
        else:  # fog
            return {
                'x': rng.randint(0, w),
                'y': rng.randint(0, h),
                'vx': rng.uniform(0.1, 0.4),
                'vy': rng.uniform(-0.05, 0.05),
                'size': rng.randint(8, 20),
                'alpha': rng.uniform(0.05, 0.15),
                'color': parse_color("#C2C3C7"),
            }

    def render(self, canvas):
        if not self.visible:
            return
        if not self._initialized:
            self._init_particles()

        w, h = self._canvas_width, self._canvas_height

        for p in self._particles:
            if self.style == "rain":
                # Draw rain streak
                for i in range(p['length']):
                    px = int(p['x'] + p['vx'] * i)
                    py = int(p['y'] + i)
                    alpha = int(200 * (1 - i / p['length']) * self.opacity)
                    c = p['color']
                    canvas.set_pixel(px, py, (c[0], c[1], c[2], alpha))
                p['x'] += p['vx']
                p['y'] += p['vy']

            elif self.style == "snow":
                # Draw snowflake with wobble
                p['phase'] += 0.05
                wobble_x = math.sin(p['phase']) * 0.5
                px, py = int(p['x']), int(p['y'])
                s = p.get('size', 1)
                c = p['color']
                alpha = int(c[3] * self.opacity)
                for dx in range(s):
                    for dy in range(s):
                        canvas.set_pixel(px + dx, py + dy, (c[0], c[1], c[2], alpha))
                p['x'] += p['vx'] + wobble_x
                p['y'] += p['vy']

            elif self.style == "fog":
                # Draw soft fog blob
                px, py = int(p['x']), int(p['y'])
                size = p['size']
                alpha_base = int(p['alpha'] * 255 * self.opacity)
                c = p['color']
                for dy in range(-size // 2, size // 2 + 1):
                    for dx in range(-size // 2, size // 2 + 1):
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < size / 2:
                            a = int(alpha_base * (1 - dist / (size / 2)))
                            canvas.set_pixel(px + dx, py + dy, (c[0], c[1], c[2], a))
                p['x'] += p['vx']
                p['y'] += p['vy']

        # Recycle particles that go off-screen
        for i, p in enumerate(self._particles):
            if p['y'] > h + 10 or p['y'] < -20 or p['x'] > w + 20 or p['x'] < -20:
                self._particles[i] = self._new_particle(initial=False)


class AnimatedGradientBackground(PObject):
    """Gradient background that shifts colors over time.

    Usage::

        bg = AnimatedGradientBackground(
            color_top_start="#0B0E2A", color_top_end="#FF6B35",
            color_bottom_start="#1D2B53", color_bottom_end="#0B0E2A",
        )
        scene.add(bg)
    """

    def __init__(
        self,
        color_top_start: str = "#0B0E2A",
        color_top_end: str = "#FF6B35",
        color_bottom_start: str = "#1D2B53",
        color_bottom_end: str = "#0B0E2A",
        cycle_seconds: float = 5.0,
        direction: str = "vertical",
    ):
        super().__init__(x=0, y=0)
        self._top_start = parse_color(color_top_start)
        self._top_end = parse_color(color_top_end)
        self._bottom_start = parse_color(color_bottom_start)
        self._bottom_end = parse_color(color_bottom_end)
        self.cycle_seconds = cycle_seconds
        self.direction = direction
        self.z_index = -100
        self._frame_counter = 0

    @staticmethod
    def _lerp(c1, c2, t):
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )

    def render(self, canvas):
        if not self.visible:
            return
        self._frame_counter += 1
        # Use a smooth sine wave for cycling
        t = (math.sin(self._frame_counter * 0.02 / max(0.1, self.cycle_seconds)) + 1) / 2

        color_top = self._lerp(self._top_start, self._top_end, t)
        color_bottom = self._lerp(self._bottom_start, self._bottom_end, t)

        w, h = canvas.width, canvas.height
        pixels = np.zeros((h, w, 4), dtype=np.uint8)

        if self.direction == "vertical":
            for y in range(h):
                yt = y / max(1, h - 1)
                c = self._lerp(color_top, color_bottom, yt)
                pixels[y, :] = c
        else:
            for x in range(w):
                xt = x / max(1, w - 1)
                c = self._lerp(color_top, color_bottom, xt)
                pixels[:, x] = c

        img = Image.fromarray(pixels, "RGBA")
        canvas.blit(img, 0, 0)


class SceneBackground:
    """Factory for production-ready background presets.

    Usage::

        objects = SceneBackground.preset("night_sky", width=480, height=270)
        for obj in objects:
            scene.add(obj)
    """

    @staticmethod
    def preset(name: str, width: int = 480, height: int = 270) -> list:
        """Create a complete themed background from a preset name.

        Available presets: "night_sky", "classroom_board", "code_editor",
        "paper", "ocean_floor", "sunset", "forest".
        """
        presets = {
            "night_sky": lambda: [
                MultiGradientBackground(
                    stops=[(0.0, "#0B0E2A"), (0.6, "#16213E"), (1.0, "#1A1A2E")],
                    direction="vertical",
                ),
                Starfield(star_count=80, seed=42),
            ],
            "classroom_board": lambda: [
                Background(color="#1B4332"),
                _GridOverlay(width, height, color="#2D6A4F"),
            ],
            "code_editor": lambda: [
                Background(color="#1E1E2E"),
                _LineNumbers(width, height),
            ],
            "paper": lambda: [
                Background(color="#FAF0E6"),
                _GridOverlay(width, height, color="#E8D8C8"),
            ],
            "ocean_floor": lambda: [
                MultiGradientBackground(
                    stops=[(0.0, "#006994"), (0.5, "#004466"), (1.0, "#002233")],
                    direction="vertical",
                ),
            ],
            "sunset": lambda: [
                MultiGradientBackground(
                    stops=[
                        (0.0, "#0B0E2A"), (0.3, "#3B1F8E"),
                        (0.5, "#FF6B35"), (0.7, "#F7931E"),
                        (1.0, "#FFD700"),
                    ],
                    direction="vertical",
                ),
            ],
            "forest": lambda: [
                MultiGradientBackground(
                    stops=[(0.0, "#87CEEB"), (0.5, "#4A8C5C"), (1.0, "#2D4A22")],
                    direction="vertical",
                ),
            ],
        }
        factory = presets.get(name)
        if factory is None:
            available = ", ".join(presets.keys())
            raise ValueError(f"Unknown preset: {name!r}. Available: {available}")
        return factory()


class _GridOverlay(PObject):
    """Internal grid overlay for SceneBackground presets."""

    def __init__(self, width, height, color="#1D2B53"):
        super().__init__(x=0, y=0, color=color)
        self._gw = width
        self._gh = height
        self.z_index = -90

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        for gx in range(0, self._gw, 16):
            for gy in range(self._gh):
                canvas.set_pixel(gx, gy, color)
        for gy in range(0, self._gh, 16):
            for gx in range(self._gw):
                canvas.set_pixel(gx, gy, color)


class _LineNumbers(PObject):
    """Internal line number gutter for code_editor preset."""

    def __init__(self, width, height):
        super().__init__(x=0, y=0, color="#313244")
        self._gw = width
        self._gh = height
        self.z_index = -90

    def render(self, canvas):
        if not self.visible:
            return
        gutter_color = parse_color("#313244")
        line_color = parse_color("#45475A")
        # Draw gutter background
        for y in range(self._gh):
            for x in range(12):
                canvas.set_pixel(x, y, gutter_color)
            # Draw separator line
            canvas.set_pixel(12, y, line_color)
