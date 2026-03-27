"""PixelEngine sprites — define sprites with ASCII art or load from image files."""
from PIL import Image, ImageOps
from pixelengine.pobject import PObject
from pixelengine.color import parse_color, CHAR_COLORS


class Sprite(PObject):
    """A pixel art sprite defined by ASCII art or a PIL Image.

    ASCII art mode::

        player = Sprite.from_art([
            "..GG..",
            ".GGGG.",
            "RRRRRR",
            ".RYYJ.",
        ], x=50, y=50)

    With flipping and auto-animation::

        player.flip_h = True          # mirror horizontally
        player.auto_animate = True    # advance frames automatically
        player.frame_duration = 0.15  # seconds per frame
    """

    def __init__(self, image: Image.Image, x: int = 0, y: int = 0):
        super().__init__(x=x, y=y)
        self._image = image.convert("RGBA")
        self.width = image.width
        self.height = image.height

        # Animation
        self._frames: list = []
        self._current_frame: int = 0
        self._frame_timer: float = 0
        self.frame_duration: float = 0.2
        self.auto_animate: bool = False
        self.loop: bool = True
        self._animation_finished: bool = False

        # Transform
        self._fps: int = 24  # Set by Scene to actual FPS
        self.flip_h: bool = False
        self.flip_v: bool = False
        self.anchor_x: float = 0.0   # 0=left, 0.5=center, 1=right
        self.anchor_y: float = 0.0   # 0=top, 0.5=center, 1=bottom

        # Named animation states (e.g. idle, walk, attack)
        self._states: dict = {}
        self._current_state: str = None

    # ── Factory Methods ─────────────────────────────────────

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
        img = cls._art_to_image(art, color_map)
        return cls(img, x=x, y=y)

    @classmethod
    def from_file(cls, path: str, x: int = 0, y: int = 0) -> "Sprite":
        """Load a sprite from an image file (PNG recommended)."""
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
        """Load an animated sprite from a sprite sheet.

        Args:
            path: Path to the sprite sheet image.
            frame_width: Width of each frame in pixels.
            frame_height: Height of each frame in pixels.
            frame_count: Number of frames (auto-detected from sheet if None).
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
        sprite.auto_animate = True
        return sprite

    # ── Animation Frames ────────────────────────────────────

    def add_frame(self, art: list, color_map: dict = None):
        """Add an animation frame from ASCII art."""
        img = self._art_to_image(art, color_map)
        self._frames.append(img)
        # First added frame also becomes the base image if none exist
        if len(self._frames) == 1:
            self._image = img

    def add_frames(self, art_list: list, color_map: dict = None):
        """Add multiple animation frames at once."""
        for art in art_list:
            self.add_frame(art, color_map)

    def set_frame(self, index: int):
        """Manually switch to a specific animation frame."""
        if self._frames and 0 <= index < len(self._frames):
            self._current_frame = index
            self._image = self._frames[index]

    def advance_frame(self):
        """Advance to the next animation frame."""
        if not self._frames:
            return
        if self.loop:
            self._current_frame = (self._current_frame + 1) % len(self._frames)
        else:
            if self._current_frame < len(self._frames) - 1:
                self._current_frame += 1
            else:
                self._animation_finished = True
        self._image = self._frames[self._current_frame]

    @property
    def frame_count(self) -> int:
        """Total number of animation frames."""
        return len(self._frames) if self._frames else 1

    @property
    def is_animated(self) -> bool:
        """Whether this sprite has multiple frames."""
        return len(self._frames) > 1

    # ── Named States ────────────────────────────────────────

    def add_state(self, name: str, frame_indices: list):
        """Define a named animation state (e.g. 'idle', 'walk', 'attack').

        Args:
            name: State name.
            frame_indices: List of frame indices for this state.
        """
        self._states[name] = frame_indices

    def set_state(self, name: str):
        """Switch to a named animation state."""
        if name in self._states and name != self._current_state:
            self._current_state = name
            indices = self._states[name]
            self._current_frame = 0
            self._frame_timer = 0
            self._animation_finished = False
            # Set to first frame of state
            if self._frames and indices:
                self._image = self._frames[indices[0]]

    # ── Rendering ───────────────────────────────────────────

    def render(self, canvas):
        if not self.visible:
            return

        # Auto-animate: advance frame based on timer
        if self.auto_animate and self._frames and len(self._frames) > 1:
            self._frame_timer += 1  # incremented each render call
            if self._frame_timer >= self.frame_duration * self._fps:  # FPS-aware timing
                self._frame_timer = 0
                if self._current_state and self._states:
                    # State-based animation
                    indices = self._states.get(self._current_state, [0])
                    state_pos = indices.index(self._current_frame) if self._current_frame in indices else 0
                    state_pos = (state_pos + 1) % len(indices)
                    self._current_frame = indices[state_pos]
                    self._image = self._frames[self._current_frame]
                else:
                    # Simple sequential animation
                    self.advance_frame()

        img = self._image.copy()

        # Apply flipping
        if self.flip_h:
            img = ImageOps.mirror(img)
        if self.flip_v:
            img = ImageOps.flip(img)

        # Apply opacity
        if self.opacity < 1.0:
            alpha = img.split()[3]
            alpha = alpha.point(lambda a: int(a * self.opacity))
            img.putalpha(alpha)

        # Calculate render position with anchor
        render_x = int(self.x - self.width * self.anchor_x)
        render_y = int(self.y - self.height * self.anchor_y)
        canvas.blit(img, render_x, render_y)

    # ── Helpers ─────────────────────────────────────────────

    @staticmethod
    def _art_to_image(art: list, color_map: dict = None) -> Image.Image:
        """Convert ASCII art rows to a PIL Image."""
        cmap = {**CHAR_COLORS}
        if color_map:
            cmap.update(color_map)

        height = len(art)
        width = max(len(row) for row in art) if art else 1
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        for row_idx, row in enumerate(art):
            for col_idx, char in enumerate(row):
                hex_color = cmap.get(char)
                if hex_color is not None:
                    color = parse_color(hex_color)
                    img.putpixel((col_idx, row_idx), color)
        return img

    @property
    def center_x(self) -> int:
        return int(self.x + self.width // 2)

    @property
    def center_y(self) -> int:
        return int(self.y + self.height // 2)

    def __repr__(self) -> str:
        frames = len(self._frames) if self._frames else 1
        state = f", state={self._current_state}" if self._current_state else ""
        return f"Sprite({self.width}×{self.height}, frames={frames}{state}, at ({self.x},{self.y}))"
