"""PixelEngine configuration — resolution, FPS, aspect ratio presets."""
from dataclasses import dataclass


@dataclass
class PixelConfig:
    """Configuration for a PixelEngine scene.

    The pixel art canvas is rendered at low resolution (e.g. 256×144)
    and upscaled with nearest-neighbor to the output resolution,
    preserving crisp pixel edges.
    """

    # Canvas dimensions (the low-res pixel art surface)
    canvas_width: int = 256
    canvas_height: int = 144

    # Upscale factor for output (nearest-neighbor)
    upscale: int = 4

    # Frames per second
    fps: int = 12

    # Output format
    output_format: str = "mp4"

    # Background color (hex string)
    background_color: str = "#000000"

    # ── Computed properties ──────────────────────────────────

    @property
    def output_width(self) -> int:
        """Final video width after upscaling."""
        return self.canvas_width * self.upscale

    @property
    def output_height(self) -> int:
        """Final video height after upscaling."""
        return self.canvas_height * self.upscale

    # ── Presets ──────────────────────────────────────────────

    @classmethod
    def landscape(cls) -> "PixelConfig":
        """16:9 for YouTube standard (256×144 → 1024×576)."""
        return cls(canvas_width=256, canvas_height=144, upscale=4)

    @classmethod
    def portrait(cls) -> "PixelConfig":
        """9:16 for YouTube Shorts (144×256 → 576×1024)."""
        return cls(canvas_width=144, canvas_height=256, upscale=4)

    @classmethod
    def square(cls) -> "PixelConfig":
        """1:1 square format (192×192 → 768×768)."""
        return cls(canvas_width=192, canvas_height=192, upscale=4)

    @classmethod
    def hd(cls) -> "PixelConfig":
        """HD 16:9 (320×180 → 1280×720)."""
        return cls(canvas_width=320, canvas_height=180, upscale=4)

    @classmethod
    def full_hd(cls) -> "PixelConfig":
        """Full HD 16:9 (480×270 → 1920×1080)."""
        return cls(canvas_width=480, canvas_height=270, upscale=4)


# Global default config instance
DEFAULT_CONFIG = PixelConfig()
