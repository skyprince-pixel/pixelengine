"""PixelEngine terrain — procedural pixel art landscape generator.

Generates 2D terrains using layered value noise rendered as coloured
horizontal slices.  No external dependencies — noise is implemented
in pure NumPy.

Classes:
    Terrain — A PObject that renders a procedural landscape.

Usage::

    from pixelengine import Terrain

    mountains = Terrain(width=480, height=270, style="mountains", seed=42)
    scene.add(mountains)
"""
import math
import numpy as np
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  Value Noise (pure NumPy, no external deps)
# ═══════════════════════════════════════════════════════════

def _value_noise_1d(width: int, octaves: int = 4, seed: int = 0) -> np.ndarray:
    """Generate a 1D value noise heightmap in [0, 1]."""
    rng = np.random.RandomState(seed)
    result = np.zeros(width, dtype=np.float64)
    amplitude = 1.0
    total_amp = 0.0

    for octave in range(octaves):
        freq = 2 ** octave
        n_points = max(2, freq + 1)
        # Random control points
        control = rng.random(n_points)
        # Interpolate to full width
        x_ctrl = np.linspace(0, width - 1, n_points)
        x_full = np.arange(width)
        interp = np.interp(x_full, x_ctrl, control)
        result += interp * amplitude
        total_amp += amplitude
        amplitude *= 0.5

    # Normalize to [0, 1]
    result /= total_amp
    return result


def _value_noise_2d(width: int, height: int, octaves: int = 4,
                    seed: int = 0) -> np.ndarray:
    """Generate a 2D value noise map in [0, 1]."""
    rng = np.random.RandomState(seed)
    result = np.zeros((height, width), dtype=np.float64)
    amplitude = 1.0
    total_amp = 0.0

    for octave in range(octaves):
        freq = 2 ** octave
        n_x = max(2, freq + 1)
        n_y = max(2, freq + 1)
        control = rng.random((n_y, n_x))

        # Bilinear interpolation to full size
        from PIL import Image as PILImage
        ctrl_img = PILImage.fromarray((control * 255).astype(np.uint8), mode="L")
        interp_img = ctrl_img.resize((width, height), PILImage.Resampling.BILINEAR)
        interp = np.array(interp_img).astype(np.float64) / 255.0

        result += interp * amplitude
        total_amp += amplitude
        amplitude *= 0.5

    result /= total_amp
    return result


# ═══════════════════════════════════════════════════════════
#  Terrain Styles (colour palettes + generation rules)
# ═══════════════════════════════════════════════════════════

TERRAIN_STYLES = {
    "mountains": {
        "sky_top": "#0B0C10",
        "sky_bottom": "#1F4068",
        "layers": [
            (0.20, "#FFFFFF"),   # Snow peaks
            (0.35, "#8B95A2"),   # Rock
            (0.55, "#4A6741"),   # Forest
            (0.75, "#2D5A27"),   # Dark forest
            (0.90, "#5B4A3F"),   # Earth
            (1.00, "#3A2F27"),   # Deep earth
        ],
        "base_height": 0.35,
        "amplitude": 0.45,
        "octaves": 5,
    },
    "desert": {
        "sky_top": "#FF6B35",
        "sky_bottom": "#FFD166",
        "layers": [
            (0.30, "#F4D35E"),   # Light sand
            (0.55, "#E8C547"),   # Sand
            (0.75, "#D4A843"),   # Dark sand
            (0.90, "#B8860B"),   # Deep sand
            (1.00, "#8B6914"),   # Bedrock
        ],
        "base_height": 0.55,
        "amplitude": 0.25,
        "octaves": 3,
    },
    "ocean": {
        "sky_top": "#87CEEB",
        "sky_bottom": "#E0F0FF",
        "layers": [
            (0.15, "#4ECDC4"),   # Shallow water
            (0.35, "#2E86AB"),   # Mid water
            (0.55, "#1B4965"),   # Deep water
            (0.75, "#0D1B2A"),   # Abyss
            (0.90, "#3A506B"),   # Seafloor
            (1.00, "#2D3A4A"),   # Deep seabed
        ],
        "base_height": 0.25,
        "amplitude": 0.15,
        "octaves": 4,
    },
    "forest": {
        "sky_top": "#2C3E50",
        "sky_bottom": "#85C1E9",
        "layers": [
            (0.25, "#1B5E20"),   # Canopy tops
            (0.45, "#2E7D32"),   # Mid canopy
            (0.60, "#388E3C"),   # Lower canopy
            (0.75, "#4E342E"),   # Trunks
            (0.90, "#3E2723"),   # Ground
            (1.00, "#2C1B18"),   # Roots
        ],
        "base_height": 0.30,
        "amplitude": 0.40,
        "octaves": 6,
    },
    "caves": {
        "sky_top": "#1A1A2E",
        "sky_bottom": "#16213E",
        "layers": [
            (0.20, "#4A4A6A"),   # Stalactites
            (0.40, "#2D2D44"),   # Cave wall
            (0.60, "#1A1A2E"),   # Deep cave
            (0.75, "#3D3D5C"),   # Floor rock
            (0.90, "#5A5A7A"),   # Stalagmites
            (1.00, "#4A4A6A"),   # Base
        ],
        "base_height": 0.45,
        "amplitude": 0.35,
        "octaves": 5,
    },
}


class Terrain(PObject):
    """Procedural pixel art terrain generator.

    Generates a landscape using layered value noise and renders it as
    a coloured 2D heightmap.

    Args:
        width, height: Terrain dimensions in canvas pixels.
        x, y: Top-left position on the canvas.
        style: Terrain style preset.  One of:
            ``"mountains"``, ``"desert"``, ``"ocean"``,
            ``"forest"``, ``"caves"``.
        seed: Random seed for reproducible terrain.
        animate: If True, supports Create() animation (left-to-right reveal).

    Usage::

        bg = Terrain(width=480, height=270, style="mountains", seed=42)
        scene.add(bg)
        scene.play(Create(bg), duration=2.0)
    """

    STYLES = list(TERRAIN_STYLES.keys())

    def __init__(self, width: int = 480, height: int = 270,
                 x: int = 0, y: int = 0,
                 style: str = "mountains", seed: int = 0):
        super().__init__(x=x, y=y)
        self.terrain_width = width
        self.terrain_height = height
        self.style = style if style in TERRAIN_STYLES else "mountains"
        self.seed = seed
        self._rendered: Image.Image | None = None
        self._generate()

    def _generate(self):
        """Generate the terrain image."""
        w, h = self.terrain_width, self.terrain_height
        cfg = TERRAIN_STYLES[self.style]

        # Generate heightmap
        heightmap = _value_noise_1d(w, octaves=cfg["octaves"], seed=self.seed)
        # Scale to pixel heights
        base_h = int(h * cfg["base_height"])
        amp = int(h * cfg["amplitude"])
        terrain_heights = base_h + (heightmap * amp).astype(int)

        # Create image with sky gradient
        img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        pixels = np.array(img)

        sky_top = np.array(parse_color(cfg["sky_top"])[:3], dtype=np.float32)
        sky_bot = np.array(parse_color(cfg["sky_bottom"])[:3], dtype=np.float32)

        # Draw sky gradient
        for y_pos in range(h):
            t = y_pos / max(1, h - 1)
            sky_col = (sky_top * (1 - t) + sky_bot * t).astype(np.uint8)
            pixels[y_pos, :, :3] = sky_col
            pixels[y_pos, :, 3] = 255

        # Draw terrain columns
        layers = cfg["layers"]
        for x_pos in range(w):
            ground_start = h - terrain_heights[x_pos]
            ground_depth = terrain_heights[x_pos]

            if ground_depth <= 0:
                continue

            for y_pos in range(ground_start, h):
                # How deep into the ground are we? (0 = surface, 1 = bottom)
                depth_frac = (y_pos - ground_start) / max(1, ground_depth)

                # Find the correct layer
                layer_color = parse_color(layers[-1][1])[:3]
                for threshold, color_hex in layers:
                    if depth_frac <= threshold:
                        layer_color = parse_color(color_hex)[:3]
                        break

                pixels[y_pos, x_pos, :3] = layer_color

        # Add subtle surface detail variation
        rng = np.random.RandomState(self.seed + 100)
        noise = rng.randint(-8, 9, size=(h, w, 3)).astype(np.int16)
        result = pixels[:, :, :3].astype(np.int16) + noise
        np.clip(result, 0, 255, out=result)
        pixels[:, :, :3] = result.astype(np.uint8)

        self._rendered = Image.fromarray(pixels, mode="RGBA")
        self.width = w
        self.height = h

    def render(self, canvas):
        if not self.visible or self._rendered is None:
            return

        draw_alpha = getattr(self, '_create_progress', 1.0)
        if draw_alpha <= 0:
            return

        img = self._rendered

        # Apply opacity
        if self.opacity < 1.0:
            arr = np.array(img)
            arr[:, :, 3] = (arr[:, :, 3].astype(np.float32) * self.opacity).astype(np.uint8)
            img = Image.fromarray(arr, "RGBA")

        # Create progress: reveal left-to-right
        if draw_alpha < 0.99:
            crop_w = max(1, int(img.width * draw_alpha))
            cropped = img.crop((0, 0, crop_w, img.height))
            full = Image.new("RGBA", img.size, (0, 0, 0, 0))
            full.paste(cropped, (0, 0))
            img = full

        canvas.blit(img, int(self.x), int(self.y))

    def regenerate(self, seed: int = None, style: str = None):
        """Regenerate terrain with a new seed or style."""
        if seed is not None:
            self.seed = seed
        if style is not None and style in TERRAIN_STYLES:
            self.style = style
        self._generate()
        return self

    @property
    def center_x(self) -> int:
        return int(self.x + self.terrain_width / 2)

    @property
    def center_y(self) -> int:
        return int(self.y + self.terrain_height / 2)
