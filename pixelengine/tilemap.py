"""PixelEngine tilemap — grid-based tile rendering for backgrounds and levels."""
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color, CHAR_COLORS


class TileSet:
    """A collection of tile images, each identified by a character key.

    Tiles can be defined inline via ASCII art or loaded from a tileset image.

    Usage::

        tiles = TileSet(tile_size=8)
        tiles.add_tile('#', art=[
            "DDDDDDDD",
            "DAAADDDD",
            "DDDDDDAD",
            "DDDADDDD",
            "DDDDDDDD",
            "DADDDADD",
            "DDDDDDDD",
            "DDDDDDDD",
        ])
        tiles.add_color_tile('.', color="#87CEEB")  # sky tile
    """

    def __init__(self, tile_size: int = 8):
        self.tile_size = tile_size
        self._tiles: dict = {}

    def add_tile(self, key: str, art: list, color_map: dict = None):
        """Add a tile from ASCII art.

        Args:
            key: Single character identifier for this tile.
            art: List of strings (tile_size rows, each tile_size chars wide).
            color_map: Optional custom char→color mapping.
        """
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
        """Add a solid-color tile.

        Args:
            key: Single character identifier.
            color: Color string (hex, named, etc.).
        """
        c = parse_color(color)
        img = Image.new("RGBA", (self.tile_size, self.tile_size), c)
        self._tiles[key] = img

    def add_image_tile(self, key: str, image: Image.Image):
        """Add a tile from a PIL Image (resized to tile_size if needed)."""
        if image.width != self.tile_size or image.height != self.tile_size:
            image = image.resize(
                (self.tile_size, self.tile_size), Image.Resampling.NEAREST
            )
        self._tiles[key] = image.convert("RGBA")

    def get_tile(self, key: str) -> Image.Image:
        """Get the tile image for a given key. Returns None if not found."""
        return self._tiles.get(key)

    @property
    def tile_count(self) -> int:
        return len(self._tiles)


class TileMap(PObject):
    """A grid of tiles rendered as a background or level.

    Usage::

        level_data = [
            "................",
            "................",
            "....####........",
            "................",
            "..####....####..",
            "################",
        ]
        tilemap = TileMap(tileset, level_data, x=0, y=0)
        scene.add(tilemap)
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
        self.map_data = map_data
        self.z_index = -10  # Behind sprites, above backgrounds

        # Pre-render the full map image for performance
        self._rendered_map: Image.Image = None
        self._dirty = True

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

    def set_tile(self, col: int, row: int, key: str):
        """Change a tile at (col, row) in the map data."""
        if 0 <= row < len(self.map_data):
            line = list(self.map_data[row])
            if 0 <= col < len(line):
                line[col] = key
                self.map_data[row] = ''.join(line)
                self._dirty = True

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

        # Re-render if dirty
        if self._dirty or self._rendered_map is None:
            self._render_map()

        if self._rendered_map is not None:
            # Apply opacity
            if self.opacity < 1.0:
                img = self._rendered_map.copy()
                alpha = img.split()[3]
                alpha = alpha.point(lambda a: int(a * self.opacity))
                img.putalpha(alpha)
                canvas.blit(img, int(self.x), int(self.y))
            else:
                canvas.blit(self._rendered_map, int(self.x), int(self.y))
