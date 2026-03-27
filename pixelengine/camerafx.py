"""PixelEngine camera effects — post-processing FX pipeline for the camera."""
import math
from PIL import Image, ImageFilter, ImageDraw


# ═══════════════════════════════════════════════════════════
#  Individual Effects
# ═══════════════════════════════════════════════════════════

class DepthOfField:
    """Gaussian blur based on distance from a focus point.

    Objects at the focus point stay sharp; objects farther away get blurred.
    Works on the final frame as a post-processing pass.

    Usage::

        dof = DepthOfField(focus_x=128, focus_y=72, focus_radius=30, blur_strength=2)
        scene.add_camera_fx(dof)

    Args:
        focus_x, focus_y: World coordinates of the focus center.
        focus_radius: Radius (in pixels) that remains perfectly sharp.
        blur_strength: Maximum blur radius for out-of-focus areas (1–5).
        enabled: Whether the effect is active.
    """

    def __init__(self, focus_x: int = 128, focus_y: int = 72,
                 focus_radius: int = 30, blur_strength: int = 2,
                 enabled: bool = True):
        self.focus_x = focus_x
        self.focus_y = focus_y
        self.focus_radius = max(1, focus_radius)
        self.blur_strength = max(1, min(5, blur_strength))
        self.enabled = enabled

    def set_focus(self, x: int, y: int, radius: int = None):
        """Update the focus point and optionally the radius."""
        self.focus_x = x
        self.focus_y = y
        if radius is not None:
            self.focus_radius = max(1, radius)

    def apply(self, frame: Image.Image) -> Image.Image:
        """Apply depth-of-field blur to the frame."""
        if not self.enabled:
            return frame

        w, h = frame.size

        # Create a fully blurred version
        blurred = frame.filter(ImageFilter.GaussianBlur(radius=self.blur_strength))

        # Create a radial mask: white = sharp (original), black = blurred
        mask = Image.new("L", (w, h), 0)
        mask_draw = ImageDraw.Draw(mask)

        # Draw the sharp focus area as a soft gradient circle
        # Inner circle: fully sharp (white)
        # Outer ring: gradient to fully blurred (black)
        max_dist = math.sqrt(w * w + h * h)
        outer_radius = self.focus_radius * 2.5

        # Use concentric circles for gradient
        steps = max(10, int(outer_radius))
        for i in range(steps, -1, -1):
            t = i / steps
            r = int(self.focus_radius + (outer_radius - self.focus_radius) * t)
            brightness = int(255 * (1.0 - t))
            mask_draw.ellipse(
                [self.focus_x - r, self.focus_y - r,
                 self.focus_x + r, self.focus_y + r],
                fill=brightness,
            )

        # Inner focus area: fully sharp
        mask_draw.ellipse(
            [self.focus_x - self.focus_radius,
             self.focus_y - self.focus_radius,
             self.focus_x + self.focus_radius,
             self.focus_y + self.focus_radius],
            fill=255,
        )

        # Composite: mask white = original, mask black = blurred
        result = Image.composite(frame, blurred, mask)
        return result


class Vignette:
    """Darkens the edges of the frame in a radial gradient.

    Usage::

        vig = Vignette(intensity=0.6, radius=0.8)
        scene.add_camera_fx(vig)

    Args:
        intensity: How dark the edges get (0.0–1.0, where 1.0 = fully black).
        radius: Fraction of frame diagonal where darkening begins (0.0–1.0).
        enabled: Whether the effect is active.
    """

    def __init__(self, intensity: float = 0.5, radius: float = 0.7,
                 enabled: bool = True):
        self.intensity = max(0.0, min(1.0, intensity))
        self.radius = max(0.1, min(1.0, radius))
        self.enabled = enabled
        self._cache = None
        self._cache_size = None

    def apply(self, frame: Image.Image) -> Image.Image:
        """Apply vignette darkening to frame edges."""
        if not self.enabled:
            return frame

        w, h = frame.size

        # Cache the vignette mask (it doesn't change between frames)
        if self._cache is None or self._cache_size != (w, h):
            self._cache = self._build_mask(w, h)
            self._cache_size = (w, h)

        # Multiply frame by vignette mask
        result = frame.copy()
        result_pixels = result.load()
        mask_pixels = self._cache.load()

        for py in range(h):
            for px in range(w):
                fp = result_pixels[px, py]
                mp = mask_pixels[px, py]
                brightness = mp[0] / 255.0
                r = int(fp[0] * brightness)
                g = int(fp[1] * brightness)
                b = int(fp[2] * brightness)
                a = fp[3] if len(fp) >= 4 else 255
                result_pixels[px, py] = (r, g, b, a)

        return result

    def _build_mask(self, w: int, h: int) -> Image.Image:
        """Build the vignette brightness mask."""
        mask = Image.new("RGB", (w, h), (255, 255, 255))
        cx, cy = w / 2, h / 2
        max_dist = math.sqrt(cx * cx + cy * cy)
        threshold = max_dist * self.radius

        pixels = mask.load()
        for py in range(h):
            for px in range(w):
                dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                if dist <= threshold:
                    continue  # No darkening inside radius
                # Darken proportionally beyond threshold
                t = min(1.0, (dist - threshold) / (max_dist - threshold))
                brightness = int(255 * (1.0 - t * self.intensity))
                pixels[px, py] = (brightness, brightness, brightness)

        return mask


class ChromaticAberration:
    """Shifts R, G, B channels by small pixel offsets for a lens/glitch effect.

    Usage::

        chroma = ChromaticAberration(offset=2)
        scene.add_camera_fx(chroma)

    Args:
        offset: Pixel shift per channel (1–5). R shifts left, B shifts right.
        enabled: Whether the effect is active.
    """

    def __init__(self, offset: int = 2, enabled: bool = True):
        self.offset = max(1, min(5, offset))
        self.enabled = enabled

    def apply(self, frame: Image.Image) -> Image.Image:
        """Apply chromatic aberration to the frame."""
        if not self.enabled:
            return frame

        w, h = frame.size

        # Split into channels
        if frame.mode == "RGBA":
            r, g, b, a = frame.split()
        else:
            r, g, b = frame.split()
            a = None

        # Shift R channel left, B channel right
        from PIL import ImageChops
        r_shifted = ImageChops.offset(r, -self.offset, 0)
        b_shifted = ImageChops.offset(b, self.offset, 0)

        # Recombine
        if a is not None:
            result = Image.merge("RGBA", (r_shifted, g, b_shifted, a))
        else:
            result = Image.merge("RGB", (r_shifted, g, b_shifted))

        return result


class Letterbox:
    """Adds cinematic black bars to the frame.

    Usage::

        bars = Letterbox(bar_height=12)  # 12 pixels top + 12 pixels bottom
        scene.add_camera_fx(bars)

    Args:
        bar_height: Height of each bar in pixels (canvas-resolution).
            If 0, auto-calculates for 2.35:1 cinema ratio.
        color: Bar color (default black).
        enabled: Whether the effect is active.
    """

    def __init__(self, bar_height: int = 0, color: str = "#000000",
                 enabled: bool = True):
        self.bar_height = bar_height
        from pixelengine.color import parse_color
        self.bar_color = parse_color(color)
        self.enabled = enabled

    def apply(self, frame: Image.Image) -> Image.Image:
        """Apply letterbox bars to the frame."""
        if not self.enabled:
            return frame

        w, h = frame.size
        bar_h = self.bar_height

        # Auto-calculate for 2.35:1 cinematic ratio if not specified
        if bar_h <= 0:
            target_h = int(w / 2.35)
            bar_h = max(1, (h - target_h) // 2)

        result = frame.copy()
        draw = ImageDraw.Draw(result)
        bar_color = self.bar_color[:4]

        # Top bar
        draw.rectangle([0, 0, w - 1, bar_h - 1], fill=bar_color)
        # Bottom bar
        draw.rectangle([0, h - bar_h, w - 1, h - 1], fill=bar_color)

        return result


class FilmGrain:
    """Adds subtle noise grain over the frame for a film look.

    Usage::

        grain = FilmGrain(intensity=0.1)
        scene.add_camera_fx(grain)

    Args:
        intensity: Noise strength (0.0–0.5). Higher = more visible grain.
        enabled: Whether the effect is active.
    """

    def __init__(self, intensity: float = 0.1, enabled: bool = True):
        self.intensity = max(0.0, min(0.5, intensity))
        self.enabled = enabled

    def apply(self, frame: Image.Image) -> Image.Image:
        """Apply film grain noise to the frame."""
        if not self.enabled:
            return frame

        import random
        w, h = frame.size
        result = frame.copy()
        pixels = result.load()

        noise_range = int(255 * self.intensity)
        if noise_range <= 0:
            return frame

        for py in range(h):
            for px in range(w):
                noise = random.randint(-noise_range, noise_range)
                p = pixels[px, py]
                r = max(0, min(255, p[0] + noise))
                g = max(0, min(255, p[1] + noise))
                b = max(0, min(255, p[2] + noise))
                a = p[3] if len(p) >= 4 else 255
                pixels[px, py] = (r, g, b, a)

        return result


# ═══════════════════════════════════════════════════════════
#  FX Pipeline
# ═══════════════════════════════════════════════════════════

class CameraFXPipeline:
    """Ordered chain of post-processing effects applied to each frame.

    Usage::

        pipeline = CameraFXPipeline()
        pipeline.add(Vignette(intensity=0.5))
        pipeline.add(ChromaticAberration(offset=1))
        frame = pipeline.apply(frame)

    Effects are applied in the order they were added.
    """

    def __init__(self):
        self._effects: list = []

    def add(self, effect) -> "CameraFXPipeline":
        """Add an effect to the pipeline."""
        self._effects.append(effect)
        return self

    def remove(self, effect) -> "CameraFXPipeline":
        """Remove an effect from the pipeline."""
        if effect in self._effects:
            self._effects.remove(effect)
        return self

    def clear(self) -> "CameraFXPipeline":
        """Remove all effects."""
        self._effects.clear()
        return self

    @property
    def count(self) -> int:
        """Number of effects in the pipeline."""
        return len(self._effects)

    def apply(self, frame: Image.Image) -> Image.Image:
        """Apply all effects in order to the frame."""
        for effect in self._effects:
            if hasattr(effect, 'enabled') and not effect.enabled:
                continue
            frame = effect.apply(frame)
        return frame
