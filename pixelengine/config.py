"""PixelEngine configuration — resolution, FPS, aspect ratio presets."""
from dataclasses import dataclass


@dataclass
class PixelConfig:
    """Configuration for a PixelEngine scene.

    The canvas is rendered at a configurable resolution and upscaled
    with nearest-neighbor to the output resolution, preserving crisp
    pixel edges. Default is 480×270 → 1920×1080 (Full HD).
    """

    # Canvas dimensions (the rendering surface)
    canvas_width: int = 480
    canvas_height: int = 270

    # Upscale factor for output (nearest-neighbor)
    upscale: int = 4

    # Frames per second
    fps: int = 24

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
    def retro(cls) -> "PixelConfig":
        """Classic 8-bit retro (256×144 → 1024×576)."""
        return cls(canvas_width=256, canvas_height=144, upscale=4)

    @classmethod
    def landscape(cls) -> "PixelConfig":
        """16:9 standard (480×270 → 1920×1080 Full HD)."""
        return cls(canvas_width=480, canvas_height=270, upscale=4)

    @classmethod
    def portrait(cls) -> "PixelConfig":
        """9:16 for YouTube Shorts (270×480 → 1080×1920 Full HD)."""
        return cls(canvas_width=270, canvas_height=480, upscale=4)
        
    @classmethod
    def high_res_portrait(cls) -> "PixelConfig":
        """High-detail 9:16 for smooth pixel art (540×960 → 1080×1920)."""
        return cls(canvas_width=540, canvas_height=960, upscale=2)
        
    @classmethod
    def high_res_landscape(cls) -> "PixelConfig":
        """High-detail 16:9 for smooth pixel art (960×540 → 1920×1080)."""
        return cls(canvas_width=960, canvas_height=540, upscale=2)

    @classmethod
    def square(cls) -> "PixelConfig":
        """1:1 square format (384×384 → 1536×1536)."""
        return cls(canvas_width=384, canvas_height=384, upscale=4)

    @classmethod
    def hd(cls) -> "PixelConfig":
        """HD 16:9 (320×180 → 1280×720)."""
        return cls(canvas_width=320, canvas_height=180, upscale=4)

    @classmethod
    def full_hd(cls) -> "PixelConfig":
        """Full HD 16:9 (480×270 → 1920×1080)."""
        return cls(canvas_width=480, canvas_height=270, upscale=4)

    @classmethod
    def qhd(cls) -> "PixelConfig":
        """QHD 16:9 (640×360 → 2560×1440)."""
        return cls(canvas_width=640, canvas_height=360, upscale=4)


# Global default config instance
DEFAULT_CONFIG = PixelConfig()
