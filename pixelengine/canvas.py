"""PixelEngine canvas — the low-res pixel art rendering surface."""
from PIL import Image
from pixelengine.color import parse_color


class Canvas:
    """Low-resolution RGBA rendering surface.

    All drawing happens at the pixel art resolution (e.g. 256×144).
    The canvas is then upscaled with nearest-neighbor for final output.
    """

    def __init__(self, width: int, height: int, background: str = "#000000"):
        self.width = width
        self.height = height
        self.background = parse_color(background)
        self._image = Image.new("RGBA", (width, height), self.background)

    def clear(self):
        """Clear the canvas to the background color."""
        # Reuse the existing image buffer instead of allocating a new one
        if not hasattr(self, '_bg_image'):
            self._bg_image = Image.new("RGBA", (self.width, self.height), self.background)
        self._image.paste(self._bg_image)

    def set_pixel(self, x: int, y: int, color: tuple):
        """Set a single pixel. Silently ignores out-of-bounds coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            # Alpha compositing for semi-transparent pixels
            if len(color) == 4 and color[3] < 255:
                existing = self._image.getpixel((x, y))
                blended = self._alpha_blend(color, existing)
                self._image.putpixel((x, y), blended)
            else:
                self._image.putpixel((x, y), color[:4])

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

        # Crop and paste with alpha mask
        if src_x > 0 or src_y > 0 or crop_w < image.width or crop_h < image.height:
            cropped = image.crop((src_x, src_y, src_x + crop_w, src_y + crop_h))
        else:
            cropped = image

        if cropped.mode == "RGBA":
            self._image.paste(cropped, (dst_x, dst_y), mask=cropped)
        else:
            self._image.paste(cropped, (dst_x, dst_y))

    def get_frame(self, upscale: int = 1) -> Image.Image:
        """Return the canvas as a PIL Image, optionally upscaled.

        Always uses NEAREST resampling to preserve pixel crispness.
        """
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

    @staticmethod
    def _alpha_blend(
        fg: tuple, bg: tuple
    ) -> tuple:
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
