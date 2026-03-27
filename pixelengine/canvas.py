"""PixelEngine canvas — the low-res pixel art rendering surface.

Uses a numpy array internally for fast pixel operations, with Pillow
for final image output and upscaling.
"""
import numpy as np
from PIL import Image
from pixelengine.color import parse_color


class Canvas:
    """Low-resolution RGBA rendering surface.

    All drawing happens at the pixel art resolution (e.g. 480×270).
    The canvas is then upscaled with nearest-neighbor for final output.

    Internally uses a numpy (H, W, 4) uint8 array for fast pixel operations.
    """

    def __init__(self, width: int, height: int, background: str = "#000000"):
        self.width = width
        self.height = height
        self.background = parse_color(background)
        # Primary buffer: numpy (H, W, 4) uint8 array
        self._pixels = np.zeros((height, width, 4), dtype=np.uint8)
        self._bg_array = np.zeros((height, width, 4), dtype=np.uint8)
        self._bg_array[:, :] = self.background
        self._pixels[:] = self._bg_array
        # Pillow image (lazy-created for compatibility)
        self._image = None
        self._image_dirty = True

    def clear(self):
        """Clear the canvas to the background color."""
        self._pixels[:] = self._bg_array
        self._image_dirty = True

    def set_pixel(self, x: int, y: int, color: tuple):
        """Set a single pixel. Silently ignores out-of-bounds coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if len(color) >= 4 and color[3] < 255:
                # Alpha compositing
                fg = np.array(color[:4], dtype=np.float32)
                bg = self._pixels[y, x].astype(np.float32)
                fa = fg[3] / 255.0
                ba = bg[3] / 255.0
                out_a = fa + ba * (1.0 - fa)
                if out_a > 0:
                    out_rgb = (fg[:3] * fa + bg[:3] * ba * (1.0 - fa)) / out_a
                    self._pixels[y, x, :3] = out_rgb.astype(np.uint8)
                    self._pixels[y, x, 3] = int(out_a * 255)
                else:
                    self._pixels[y, x] = 0
            else:
                self._pixels[y, x] = color[:4]
            self._image_dirty = True

    def _sync_image(self):
        """Sync the Pillow image from the numpy array."""
        if self._image_dirty or self._image is None:
            self._image = Image.fromarray(self._pixels, mode="RGBA")
            self._image_dirty = False

    @property
    def _pil_image(self) -> Image.Image:
        """Get the current Pillow image (syncs from numpy if needed)."""
        self._sync_image()
        return self._image

    def blit(self, image: Image.Image, x: int, y: int):
        """Paste an RGBA image onto the canvas with alpha compositing.

        Handles images that extend beyond canvas bounds by cropping.
        """
        x, y = int(x), int(y)

        # Calculate the visible region
        src_x = max(0, -x)
        src_y = max(0, -y)
        dst_x = max(0, x)
        dst_y = max(0, y)

        # Crop the source image to fit within canvas bounds
        crop_w = min(image.width - src_x, self.width - dst_x)
        crop_h = min(image.height - src_y, self.height - dst_y)

        if crop_w <= 0 or crop_h <= 0:
            return  # Entirely off-screen

        # Convert source to numpy and composite
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        src_array = np.array(image)
        src_region = src_array[src_y:src_y + crop_h, src_x:src_x + crop_w]

        # Vectorized alpha compositing
        fg = src_region.astype(np.float32)
        bg = self._pixels[dst_y:dst_y + crop_h, dst_x:dst_x + crop_w].astype(np.float32)

        fa = fg[:, :, 3:4] / 255.0
        ba = bg[:, :, 3:4] / 255.0
        out_a = fa + ba * (1.0 - fa)

        # Avoid division by zero
        safe_a = np.where(out_a > 0, out_a, 1.0)
        out_rgb = (fg[:, :, :3] * fa + bg[:, :, :3] * ba * (1.0 - fa)) / safe_a

        result = np.zeros_like(fg)
        result[:, :, :3] = out_rgb
        result[:, :, 3:4] = out_a * 255.0

        self._pixels[dst_y:dst_y + crop_h, dst_x:dst_x + crop_w] = result.astype(np.uint8)
        self._image_dirty = True

    def get_frame(self, upscale: int = 1) -> Image.Image:
        """Return the canvas as a PIL Image, optionally upscaled.

        Always uses NEAREST resampling to preserve pixel crispness.
        """
        self._sync_image()
        if upscale <= 1:
            return self._image.copy()

        new_size = (self.width * upscale, self.height * upscale)
        return self._image.resize(new_size, Image.Resampling.NEAREST)

    def get_raw_bytes(self, upscale: int = 1) -> bytes:
        """Return raw RGB bytes suitable for ffmpeg pipe input."""
        frame = self.get_frame(upscale)
        # Convert RGBA → RGB (flatten alpha onto black background)
        if frame.mode == "RGBA":
            rgb = Image.new("RGB", frame.size, (0, 0, 0))
            rgb.paste(frame, mask=frame.split()[3])
            return rgb.tobytes()
        return frame.convert("RGB").tobytes()

    def blit_quality(self, image: Image.Image, x: int, y: int, quality: float):
        """Paste an image with quality scaling for multi-resolution rendering.

        Args:
            image: Source RGBA image to blit.
            x, y: Destination position on the canvas.
            quality: Resolution multiplier.
                - quality > 1.0: Render larger, then downscale with bilinear
                  filtering for a smoother, anti-aliased look.
                - quality < 1.0: Render smaller, then upscale with nearest-
                  neighbor for a chunkier, extra-pixelated look.
                - quality == 1.0: Normal pass-through.
        """
        if abs(quality - 1.0) < 0.01:
            self.blit(image, x, y)
            return

        w, h = image.size
        if quality > 1.0:
            # Upscale then downscale with bilinear to smooth
            up_w = max(1, int(w * quality))
            up_h = max(1, int(h * quality))
            upscaled = image.resize((up_w, up_h), Image.Resampling.BILINEAR)
            smoothed = upscaled.resize((w, h), Image.Resampling.BILINEAR)
            self.blit(smoothed, x, y)
        else:
            # Downscale then upscale with nearest-neighbor for chunkier look
            down_w = max(1, int(w * quality))
            down_h = max(1, int(h * quality))
            downscaled = image.resize((down_w, down_h), Image.Resampling.NEAREST)
            chunky = downscaled.resize((w, h), Image.Resampling.NEAREST)
            self.blit(chunky, x, y)

    @staticmethod
    def _alpha_blend(fg: tuple, bg: tuple) -> tuple:
        """Alpha-composite foreground over background."""
        fa = fg[3] / 255.0
        ba = bg[3] / 255.0 if len(bg) >= 4 else 1.0
        out_a = fa + ba * (1 - fa)
        if out_a == 0:
            return (0, 0, 0, 0)
        r = int((fg[0] * fa + bg[0] * ba * (1 - fa)) / out_a)
        g = int((fg[1] * fa + bg[1] * ba * (1 - fa)) / out_a)
        b = int((fg[2] * fa + bg[2] * ba * (1 - fa)) / out_a)
        a = int(out_a * 255)
        return (r, g, b, a)
