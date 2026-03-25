"""PixelEngine sprites — define sprites with ASCII art or load from image files."""
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color, CHAR_COLORS


class Sprite(PObject):
    """A pixel art sprite defined by ASCII art or a PIL Image.

    ASCII art mode uses single-character color codes from CHAR_COLORS::

        sprite = Sprite.from_art([
            "..RR..",
            ".RRRR.",
            "RRRRRR",
            ".RYYJ.",
            "..YY..",
        ], x=50, y=50)

    Image file mode::

        sprite = Sprite.from_file("player.png", x=50, y=50)
    """

    def __init__(self, image: Image.Image, x: int = 0, y: int = 0):
        super().__init__(x=x, y=y)
        self._image = image.convert("RGBA")
        self.width = image.width
        self.height = image.height
        self._frames: list = []          # For animated sprites
        self._current_frame: int = 0
        self._frame_timer: float = 0
        self.frame_duration: float = 0.2  # Seconds per frame

    @classmethod
    def from_art(
        cls,
        art: list,
        x: int = 0,
        y: int = 0,
        color_map: dict = None,
    ) -> "Sprite":
        """Create a sprite from ASCII art rows.

        Args:
            art: List of strings, each character mapped via color_map or CHAR_COLORS.
            x, y: Position on canvas.
            color_map: Optional custom char→color mapping (overrides CHAR_COLORS).
        """
        cmap = {**CHAR_COLORS}
        if color_map:
            cmap.update(color_map)

        height = len(art)
        width = max(len(row) for row in art) if art else 0
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for row_idx, row in enumerate(art):
            for col_idx, char in enumerate(row):
                hex_color = cmap.get(char)
                if hex_color is not None:
                    color = parse_color(hex_color)
                    img.putpixel((col_idx, row_idx), color)

        return cls(img, x=x, y=y)

    @classmethod
    def from_file(cls, path: str, x: int = 0, y: int = 0) -> "Sprite":
        """Load a sprite from an image file (PNG recommended).

        The image is used as-is at its native resolution — no scaling.
        Use small pixel art images for best results.
        """
        img = Image.open(path).convert("RGBA")
        return cls(img, x=x, y=y)

    @classmethod
    def from_sheet(
        cls,
        path: str,
        frame_width: int,
        frame_height: int,
        frame_count: int = None,
        x: int = 0,
        y: int = 0,
    ) -> "Sprite":
        """Load an animated sprite from a horizontal sprite sheet.

        Args:
            path: Path to the sprite sheet image.
            frame_width: Width of each frame in pixels.
            frame_height: Height of each frame in pixels.
            frame_count: Number of frames (auto-detected if None).
        """
        sheet = Image.open(path).convert("RGBA")
        cols = sheet.width // frame_width
        rows = sheet.height // frame_height
        count = frame_count or (cols * rows)

        frames = []
        for i in range(count):
            col = i % cols
            row = i // cols
            box = (
                col * frame_width,
                row * frame_height,
                (col + 1) * frame_width,
                (row + 1) * frame_height,
            )
            frames.append(sheet.crop(box))

        sprite = cls(frames[0], x=x, y=y)
        sprite._frames = frames
        return sprite

    def add_frame(self, art: list, color_map: dict = None):
        """Add an animation frame from ASCII art."""
        cmap = {**CHAR_COLORS}
        if color_map:
            cmap.update(color_map)

        height = len(art)
        width = max(len(row) for row in art) if art else 0
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for row_idx, row in enumerate(art):
            for col_idx, char in enumerate(row):
                hex_color = cmap.get(char)
                if hex_color is not None:
                    color = parse_color(hex_color)
                    img.putpixel((col_idx, row_idx), color)

        self._frames.append(img)

    def set_frame(self, index: int):
        """Manually switch to a specific animation frame."""
        if self._frames and 0 <= index < len(self._frames):
            self._current_frame = index
            self._image = self._frames[index]

    def advance_frame(self):
        """Advance to the next animation frame (loops)."""
        if self._frames:
            self._current_frame = (self._current_frame + 1) % len(self._frames)
            self._image = self._frames[self._current_frame]

    def render(self, canvas):
        if not self.visible:
            return

        img = self._image.copy()

        # Apply opacity
        if self.opacity < 1.0:
            alpha = img.split()[3]
            alpha = alpha.point(lambda a: int(a * self.opacity))
            img.putalpha(alpha)

        canvas.blit(img, int(self.x), int(self.y))

    @property
    def center_x(self) -> int:
        return int(self.x + self.width // 2)

    @property
    def center_y(self) -> int:
        return int(self.y + self.height // 2)

    def __repr__(self) -> str:
        frames = len(self._frames) if self._frames else 1
        return f"Sprite({self.width}×{self.height}, frames={frames}, at ({self.x},{self.y}))"
