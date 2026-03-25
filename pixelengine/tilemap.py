"""PixelEngine tilemap — grid-based tile rendering for backgrounds and levels."""
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color, CHAR_COLORS


class TileSet:
    """A collection of tile images, each identified by a character key.

    Standard tiles::

        tiles = TileSet(tile_size=8)
        tiles.add_color_tile('.', "#87CEEB")
        tiles.add_tile('#', art=["DDDDDDDD", ...])

    Animated tiles::

        tiles.add_animated_tile('~', arts=[wave1, wave2, wave3], fps=4)
    """

    def __init__(self, tile_size: int = 8):
        self.tile_size = tile_size
        self._tiles: dict = {}
        self._animated: dict = {}     # key → (frames_list, fps)
        self._frame_counter: int = 0

    def add_tile(self, key: str, art: list, color_map: dict = None):
        """Add a tile from ASCII art."""
        cmap = {**CHAR_COLORS}
        if color_map:
            cmap.update(color_map)

        img = Image.new("RGBA", (self.tile_size, self.tile_size), (0, 0, 0, 0))
        for row_idx, row in enumerate(art):
            for col_idx, char in enumerate(row):
                if row_idx < self.tile_size and col_idx < self.tile_size:
                    hex_color = cmap.get(char)
                    if hex_color is not None:
                        color = parse_color(hex_color)
                        img.putpixel((col_idx, row_idx), color)
        self._tiles[key] = img

    def add_color_tile(self, key: str, color: str):
        """Add a solid-color tile."""
        c = parse_color(color)
        img = Image.new("RGBA", (self.tile_size, self.tile_size), c)
        self._tiles[key] = img

    def add_gradient_tile(self, key: str, color_top: str, color_bottom: str):
        """Add a vertical gradient tile."""
        c1 = parse_color(color_top)
        c2 = parse_color(color_bottom)
        img = Image.new("RGBA", (self.tile_size, self.tile_size))
        for y in range(self.tile_size):
            t = y / max(1, self.tile_size - 1)
            c = (
                int(c1[0] + (c2[0] - c1[0]) * t),
                int(c1[1] + (c2[1] - c1[1]) * t),
                int(c1[2] + (c2[2] - c1[2]) * t),
                int(c1[3] + (c2[3] - c1[3]) * t),
            )
            for x in range(self.tile_size):
                img.putpixel((x, y), c)
        self._tiles[key] = img

    def add_image_tile(self, key: str, image: Image.Image):
        """Add a tile from a PIL Image (resized to tile_size if needed)."""
        if image.width != self.tile_size or image.height != self.tile_size:
            image = image.resize(
                (self.tile_size, self.tile_size), Image.Resampling.NEAREST
            )
        self._tiles[key] = image.convert("RGBA")

    def add_animated_tile(self, key: str, arts: list,
                          fps: int = 4, color_map: dict = None):
        """Add an animated tile with multiple frames.

        Args:
            key: Character key for this tile.
            arts: List of ASCII art frames (each is a list of strings).
            fps: Frames per second for animation.
        """
        frames = []
        cmap = {**CHAR_COLORS}
        if color_map:
            cmap.update(color_map)

        for art in arts:
            img = Image.new("RGBA", (self.tile_size, self.tile_size), (0, 0, 0, 0))
            for row_idx, row in enumerate(art):
                for col_idx, char in enumerate(row):
                    if row_idx < self.tile_size and col_idx < self.tile_size:
                        hex_color = cmap.get(char)
                        if hex_color is not None:
                            color = parse_color(hex_color)
                            img.putpixel((col_idx, row_idx), color)
            frames.append(img)

        # Use first frame as static fallback
        self._tiles[key] = frames[0]
        self._animated[key] = (frames, fps)

    def get_tile(self, key: str) -> Image.Image:
        """Get the tile image for a given key (animated tiles return current frame)."""
        if key in self._animated:
            frames, fps = self._animated[key]
            # 12 FPS base rate / tile fps = frames between changes
            frame_idx = (self._frame_counter // max(1, 12 // fps)) % len(frames)
            return frames[frame_idx]
        return self._tiles.get(key)

    def advance_frame(self):
        """Advance the global animation frame counter."""
        self._frame_counter += 1

    @property
    def tile_count(self) -> int:
        return len(self._tiles)

    @property
    def animated_count(self) -> int:
        return len(self._animated)


class TileMap(PObject):
    """A grid of tiles rendered as a background or level.

    Usage::

        level_data = [
            "................",
            "....####........",
            "################",
        ]
        tilemap = TileMap(tileset, level_data)
        scene.add(tilemap)

    Tile queries::

        tile = tilemap.get_tile_at(col=5, row=2)
        col, row = tilemap.world_to_tile(pixel_x=45, pixel_y=20)
        is_solid = tilemap.get_tile_at(col, row) == '#'
    """

    def __init__(
        self,
        tileset: TileSet,
        map_data: list,
        x: int = 0,
        y: int = 0,
    ):
        super().__init__(x=x, y=y)
        self.tileset = tileset
        self.map_data = [row for row in map_data]  # copy
        self.z_index = -10

        # Cache
        self._rendered_map: Image.Image = None
        self._dirty = True
        self._has_animated = bool(tileset._animated)

    @classmethod
    def from_file(cls, tileset: TileSet, path: str,
                  x: int = 0, y: int = 0) -> "TileMap":
        """Load tilemap from a text file (one row per line).

        Args:
            tileset: The TileSet to use for rendering.
            path: Path to a text file with the map data.
        """
        with open(path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        return cls(tileset, lines, x=x, y=y)

    # ── Properties ──────────────────────────────────────────

    @property
    def map_width(self) -> int:
        """Width in tiles."""
        return max(len(row) for row in self.map_data) if self.map_data else 0

    @property
    def map_height(self) -> int:
        """Height in tiles."""
        return len(self.map_data)

    @property
    def pixel_width(self) -> int:
        """Width in pixels."""
        return self.map_width * self.tileset.tile_size

    @property
    def pixel_height(self) -> int:
        """Height in pixels."""
        return self.map_height * self.tileset.tile_size

    # ── Tile Access ─────────────────────────────────────────

    def get_tile_at(self, col: int, row: int) -> str:
        """Get the tile character at (col, row). Returns None if out of bounds."""
        if 0 <= row < len(self.map_data):
            line = self.map_data[row]
            if 0 <= col < len(line):
                return line[col]
        return None

    def set_tile(self, col: int, row: int, key: str):
        """Change a tile at (col, row) in the map data."""
        if 0 <= row < len(self.map_data):
            line = list(self.map_data[row])
            if 0 <= col < len(line):
                line[col] = key
                self.map_data[row] = ''.join(line)
                self._dirty = True

    def world_to_tile(self, world_x: float, world_y: float) -> tuple:
        """Convert world pixel coordinates to tile (col, row)."""
        ts = self.tileset.tile_size
        col = int((world_x - self.x) // ts)
        row = int((world_y - self.y) // ts)
        return (col, row)

    def tile_to_world(self, col: int, row: int) -> tuple:
        """Convert tile (col, row) to world pixel coordinates (top-left)."""
        ts = self.tileset.tile_size
        return (int(self.x) + col * ts, int(self.y) + row * ts)

    def find_tiles(self, key: str) -> list:
        """Find all tile positions matching a key. Returns list of (col, row)."""
        positions = []
        for row_idx, row in enumerate(self.map_data):
            for col_idx, char in enumerate(row):
                if char == key:
                    positions.append((col_idx, row_idx))
        return positions

    # ── Rendering ───────────────────────────────────────────

    def _render_map(self):
        """Pre-render the entire tilemap to a single image."""
        ts = self.tileset.tile_size
        w = self.map_width * ts
        h = self.map_height * ts
        if w <= 0 or h <= 0:
            self._rendered_map = None
            return

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for row_idx, row in enumerate(self.map_data):
            for col_idx, char in enumerate(row):
                tile_img = self.tileset.get_tile(char)
                if tile_img is not None:
                    px = col_idx * ts
                    py = row_idx * ts
                    img.paste(tile_img, (px, py), mask=tile_img)

        self._rendered_map = img
        self._dirty = False

    def render(self, canvas):
        if not self.visible:
            return

        # Animated tiles: always re-render + advance frame counter
        if self._has_animated:
            self.tileset.advance_frame()
            self._dirty = True

        if self._dirty or self._rendered_map is None:
            self._render_map()

        if self._rendered_map is not None:
            if self.opacity < 1.0:
                img = self._rendered_map.copy()
                alpha = img.split()[3]
                alpha = alpha.point(lambda a: int(a * self.opacity))
                img.putalpha(alpha)
                canvas.blit(img, int(self.x), int(self.y))
            else:
                canvas.blit(self._rendered_map, int(self.x), int(self.y))
