"""PixelEngine shaders — per-pixel post-processing effects.

NumPy-vectorized shader effects that plug into the existing
``CameraFXPipeline``.  Each shader implements the same ``.apply()``
interface used by ``Vignette``, ``FilmGrain``, etc.

Classes:
    PixelShader      — User-defined custom shader via a callable.
    CRTScanlines     — Horizontal dark lines simulating a CRT monitor.
    Ripple           — Radial ripple/wave distortion.
    HeatShimmer      — Vertical wavy distortion that animates over time.
    Pixelate         — Mosaic / downscale effect with configurable block size.
    ColorGrade       — Apply tint/sepia/cool/warm colour grading.

Usage::

    from pixelengine import CRTScanlines, Ripple, PixelShader

    scene.add_camera_fx(CRTScanlines(line_spacing=4, darkness=0.3))
    scene.add_camera_fx(Ripple(wavelength=20, amplitude=3))

    # Custom shader
    def invert(arr, t):
        arr[:, :, :3] = 255 - arr[:, :, :3]
        return arr
    scene.add_camera_fx(PixelShader(invert))
"""
import numpy as np
from PIL import Image


class PixelShader:
    """User-defined per-pixel shader effect.

    The callable receives a NumPy ``(H, W, 4)`` uint8 array and a float
    ``time`` (seconds since scene start), and must return the modified array.

    Args:
        fn: Callable ``(np_array, time) -> np_array``.
        enabled: Whether the effect is active.

    Usage::

        def sepia(arr, t):
            r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
            gray = (0.299*r + 0.587*g + 0.114*b).astype(np.uint8)
            arr[:,:,0] = np.clip(gray + 40, 0, 255)
            arr[:,:,1] = np.clip(gray + 20, 0, 255)
            arr[:,:,2] = gray
            return arr

        scene.add_camera_fx(PixelShader(sepia))
    """

    def __init__(self, fn, enabled: bool = True):
        self.fn = fn
        self.enabled = enabled
        self._time = 0.0

    def apply(self, frame: Image.Image) -> Image.Image:
        if not self.enabled:
            return frame
        arr = np.array(frame)
        arr = self.fn(arr, self._time)
        return Image.fromarray(arr, mode=frame.mode)


class CRTScanlines:
    """Horizontal dark lines simulating a CRT monitor.

    Every Nth row is darkened to create that classic retro TV look.

    Args:
        line_spacing: Gap between dark lines (pixels).
        darkness: How much to darken the line (0.0–1.0).
        enabled: Whether the effect is active.
    """

    def __init__(self, line_spacing: int = 3, darkness: float = 0.3,
                 enabled: bool = True):
        self.line_spacing = max(2, line_spacing)
        self.darkness = max(0.0, min(1.0, darkness))
        self.enabled = enabled
        self._mask = None
        self._mask_size = None

    def apply(self, frame: Image.Image) -> Image.Image:
        if not self.enabled:
            return frame

        w, h = frame.size

        # Cache the scanline mask
        if self._mask is None or self._mask_size != (w, h):
            mask = np.ones((h, w), dtype=np.float32)
            mask[::self.line_spacing, :] = 1.0 - self.darkness
            self._mask = mask
            self._mask_size = (w, h)

        arr = np.array(frame, dtype=np.float32)
        arr[:, :, 0] *= self._mask
        arr[:, :, 1] *= self._mask
        arr[:, :, 2] *= self._mask
        np.clip(arr, 0, 255, out=arr)
        return Image.fromarray(arr.astype(np.uint8), mode=frame.mode)


class Ripple:
    """Radial ripple/wave distortion from a center point.

    Displaces pixels based on their distance from the center,
    creating a water-ripple effect.

    Args:
        center_x, center_y: Ripple origin (pixels).
        wavelength: Distance between wave peaks (pixels).
        amplitude: Maximum pixel displacement.
        speed: Animation speed multiplier.
        enabled: Whether the effect is active.
    """

    def __init__(self, center_x: int = None, center_y: int = None,
                 wavelength: float = 20.0, amplitude: float = 3.0,
                 speed: float = 2.0, enabled: bool = True):
        self.center_x = center_x
        self.center_y = center_y
        self.wavelength = max(1.0, wavelength)
        self.amplitude = amplitude
        self.speed = speed
        self.enabled = enabled
        self._time = 0.0

    def apply(self, frame: Image.Image) -> Image.Image:
        if not self.enabled or self.amplitude <= 0:
            return frame

        w, h = frame.size
        cx = self.center_x if self.center_x is not None else w // 2
        cy = self.center_y if self.center_y is not None else h // 2

        arr = np.array(frame)

        # Coordinate grids
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)

        # Wave displacement (radial outward from center)
        phase = dist / self.wavelength * 2 * np.pi - self._time * self.speed
        
        # Avoid division by zero at the exact center point
        safe_dist = np.maximum(dist, 1e-4)
        
        # Calculate displacement amount based on sine wave
        disp = self.amplitude * np.sin(phase)
        
        # Apply displacement directionally outward
        dx = (disp * (xs - cx) / safe_dist).astype(np.int32)
        dy = (disp * (ys - cy) / safe_dist).astype(np.int32)

        # Displaced source coordinates
        src_x = np.clip((xs + dx).astype(np.int32), 0, w - 1)
        src_y = np.clip((ys + dy).astype(np.int32), 0, h - 1)

        result = arr[src_y, src_x]
        return Image.fromarray(result, mode=frame.mode)


class HeatShimmer:
    """Vertical wavy distortion simulating heat rising.

    Shifts columns horizontally by a sine wave that animates over time.

    Args:
        amplitude: Maximum horizontal pixel displacement.
        frequency: Vertical wave frequency (lower = wider waves).
        speed: Animation speed multiplier.
        enabled: Whether the effect is active.
    """

    def __init__(self, amplitude: float = 2.0, frequency: float = 0.05,
                 speed: float = 3.0, enabled: bool = True):
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.enabled = enabled
        self._time = 0.0

    def apply(self, frame: Image.Image) -> Image.Image:
        if not self.enabled or self.amplitude <= 0:
            return frame

        w, h = frame.size
        arr = np.array(frame)

        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        # Horizontal displacement based on y-position and time
        shift = self.amplitude * np.sin(
            ys * self.frequency * 2 * np.pi + self._time * self.speed
        )
        src_x = np.clip((xs + shift).astype(np.int32), 0, w - 1)
        src_y = ys.astype(np.int32)

        result = arr[src_y, src_x]
        return Image.fromarray(result, mode=frame.mode)


class Pixelate:
    """Mosaic / pixelation effect with configurable block size.

    Downscales then upscales the image with nearest-neighbor to create
    a chunky pixel mosaic.

    Args:
        block_size: Size of each mosaic block (pixels).
        enabled: Whether the effect is active.
    """

    def __init__(self, block_size: int = 8, enabled: bool = True):
        self.block_size = max(2, block_size)
        self.enabled = enabled

    def apply(self, frame: Image.Image) -> Image.Image:
        if not self.enabled:
            return frame

        w, h = frame.size
        small_w = max(1, w // self.block_size)
        small_h = max(1, h // self.block_size)

        small = frame.resize((small_w, small_h), Image.Resampling.NEAREST)
        return small.resize((w, h), Image.Resampling.NEAREST)


class ColorGrade:
    """Apply colour grading / tinting to the frame.

    Provides preset grades and custom tint control.

    Args:
        preset: One of ``"sepia"``, ``"cool"``, ``"warm"``,
            ``"noir"``, ``"cyberpunk"``, or ``None`` for custom.
        tint: Custom RGBA tint colour as ``(r, g, b)`` tuple (0–255).
        strength: Blend strength of the grade (0.0–1.0).
        enabled: Whether the effect is active.
    """

    PRESETS = {
        "sepia":     (112, 66, 20),
        "cool":      (50, 100, 180),
        "warm":      (200, 120, 50),
        "noir":      (0, 0, 0),       # Desaturate only
        "cyberpunk": (180, 0, 255),
    }

    def __init__(self, preset: str = "sepia", tint: tuple = None,
                 strength: float = 0.3, enabled: bool = True):
        self.preset = preset
        self.tint = tint or self.PRESETS.get(preset, (112, 66, 20))
        self.strength = max(0.0, min(1.0, strength))
        self.enabled = enabled

    def apply(self, frame: Image.Image) -> Image.Image:
        if not self.enabled or self.strength <= 0:
            return frame

        arr = np.array(frame, dtype=np.float32)

        if self.preset == "noir":
            # Desaturate
            gray = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] +
                    0.114 * arr[:, :, 2])
            arr[:, :, 0] = arr[:, :, 0] * (1 - self.strength) + gray * self.strength
            arr[:, :, 1] = arr[:, :, 1] * (1 - self.strength) + gray * self.strength
            arr[:, :, 2] = arr[:, :, 2] * (1 - self.strength) + gray * self.strength
        else:
            # Tint blend
            tint_r, tint_g, tint_b = self.tint[:3]
            arr[:, :, 0] = arr[:, :, 0] * (1 - self.strength) + tint_r * self.strength
            arr[:, :, 1] = arr[:, :, 1] * (1 - self.strength) + tint_g * self.strength
            arr[:, :, 2] = arr[:, :, 2] * (1 - self.strength) + tint_b * self.strength

        np.clip(arr, 0, 255, out=arr)
        return Image.fromarray(arr.astype(np.uint8), mode=frame.mode)
