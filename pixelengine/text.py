"""PixelEngine text — pixel font text rendering with built-in 5×7 bitmap font."""
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  Built-in 5×7 Bitmap Font
# ═══════════════════════════════════════════════════════════
#  Each glyph is a list of 7 rows, each row is a string of
#  5 characters where '#' = pixel on, '.' = pixel off.

FONT_5X7 = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    '3': [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", "..#..", "..#.."],
    ',': [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '?': [".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."],
    ':': [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    ';': [".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."],
    '-': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '(': ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ')': [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    '/': ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    '*': [".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."],
    '%': ["##..#", "##.#.", "..#..", "..#..", ".#...", ".#.##", "#..##"],
    '#': [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    '@': [".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."],
    '<': ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    '>': [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    '_': [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    '°': [".###.", "#...#", ".###.", ".....", ".....", ".....", "....."],
    '²': [".##..", "...#.", "..#..", ".#...", ".###.", ".....", "....."],
    '³': [".##..", "...#.", "..#..", "...#.", ".##..", ".....", "....."],
    'π': [".....", ".....", "#####", ".#.#.", ".#.#.", ".#..#", ".#..#"],
}

GLYPH_WIDTH = 5
GLYPH_HEIGHT = 7
GLYPH_SPACING = 1   # Pixels between characters
LINE_SPACING = 2     # Extra pixels between lines


def _render_glyph(char: str) -> list:
    """Return the bitmap pattern for a character (list of row strings)."""
    upper = char.upper()
    if upper in FONT_5X7:
        return FONT_5X7[upper]
    # Unknown character: return empty glyph
    return ["....." for _ in range(GLYPH_HEIGHT)]


# ═══════════════════════════════════════════════════════════
#  PixelText PObject
# ═══════════════════════════════════════════════════════════

class PixelText(PObject):
    """Render text using the built-in 5×7 bitmap font.

    Usage::

        title = PixelText("HELLO WORLD", x=10, y=10, color="#FFD700")
        scene.add(title)
    """

    def __init__(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        color: str = "#FFFFFF",
        scale: int = 1,
        align: str = "left",
        shadow: bool = False,
        shadow_color: str = "#000000",
        shadow_offset: tuple = (1, 1),
        max_chars: int = None,
    ):
        super().__init__(x=x, y=y, color=color)
        self.text = text
        self.scale = max(1, scale)
        self.align = align    # "left", "center", "right"
        self.shadow = shadow
        self.shadow_color = parse_color(shadow_color)
        self.shadow_offset = shadow_offset
        self.max_chars = max_chars  # For TypeWriter animation

    @property
    def display_text(self) -> str:
        """Text to actually render (respects max_chars for TypeWriter)."""
        if self.max_chars is not None:
            return self.text[:int(self.max_chars)]
        return self.text

    @property
    def text_width(self) -> int:
        """Width of the full text in pixels (before scaling)."""
        lines = self.display_text.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        return max(0, max_len * (GLYPH_WIDTH + GLYPH_SPACING) - GLYPH_SPACING)

    @property
    def text_height(self) -> int:
        """Height of the full text in pixels (before scaling)."""
        lines = self.display_text.split('\n')
        return max(0, len(lines) * (GLYPH_HEIGHT + LINE_SPACING) - LINE_SPACING)

    @property
    def width(self) -> int:
        return self.text_width * self.scale

    @property
    def height(self) -> int:
        return self.text_height * self.scale

    def render(self, canvas):
        if not self.visible:
            return

        text = self.display_text
        lines = text.split('\n')
        color = self.get_render_color()

        for line_idx, line in enumerate(lines):
            line_y = int(self.y) + line_idx * (GLYPH_HEIGHT + LINE_SPACING) * self.scale

            # Calculate X offset for alignment
            line_width = len(line) * (GLYPH_WIDTH + GLYPH_SPACING) - GLYPH_SPACING
            if self.align == "center":
                x_offset = int(self.x) - (line_width * self.scale) // 2
            elif self.align == "right":
                x_offset = int(self.x) - line_width * self.scale
            else:
                x_offset = int(self.x)

            for char_idx, char in enumerate(line):
                char_x = x_offset + char_idx * (GLYPH_WIDTH + GLYPH_SPACING) * self.scale
                glyph = _render_glyph(char)

                # Draw shadow first (if enabled)
                if self.shadow:
                    sx = char_x + self.shadow_offset[0] * self.scale
                    sy = line_y + self.shadow_offset[1] * self.scale
                    shadow_c = (
                        self.shadow_color[0],
                        self.shadow_color[1],
                        self.shadow_color[2],
                        int(self.shadow_color[3] * self.opacity),
                    )
                    self._draw_glyph(canvas, glyph, sx, sy, shadow_c)

                # Draw character
                self._draw_glyph(canvas, glyph, char_x, line_y, color)

    def _draw_glyph(self, canvas, glyph: list, x: int, y: int, color: tuple):
        """Draw a single glyph at (x, y) with the given color and scale."""
        for row_idx, row in enumerate(glyph):
            for col_idx, pixel in enumerate(row):
                if pixel == '#':
                    px = x + col_idx * self.scale
                    py = y + row_idx * self.scale
                    # Draw scaled pixel (scale × scale block)
                    for sx in range(self.scale):
                        for sy in range(self.scale):
                            canvas.set_pixel(px + sx, py + sy, color)


# ═══════════════════════════════════════════════════════════
#  TypeWriter Animation
# ═══════════════════════════════════════════════════════════

class TypeWriter:
    """Animate text appearing character by character.

    Works with PixelText's ``max_chars`` property.

    Usage::

        title = PixelText("HELLO WORLD", x=10, y=10, max_chars=0)
        scene.add(title)
        scene.play(TypeWriter(title), duration=2.0)
    """

    def __init__(self, target: PixelText, easing=None):
        self.target = target
        self.total_chars = len(target.text)

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        self.target.max_chars = int(self.total_chars * alpha)
