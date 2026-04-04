"""PixelEngine text — pixel font text rendering with built-in 5×7 bitmap font."""
from pixelengine.pobject import PObject, Bounds
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

# ── Compact 3×5 Font (for labels and small text) ──────────

FONT_3X5 = {
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
    'C': [".##", "#..", "#..", "#..", ".##"],
    'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'E': ["###", "#..", "##.", "#..", "###"],
    'F': ["###", "#..", "##.", "#..", "#.."],
    'G': [".##", "#..", "#.#", "#.#", ".##"],
    'H': ["#.#", "#.#", "###", "#.#", "#.#"],
    'I': ["###", ".#.", ".#.", ".#.", "###"],
    'J': ["..#", "..#", "..#", "#.#", ".#."],
    'K': ["#.#", "#.#", "##.", "#.#", "#.#"],
    'L': ["#..", "#..", "#..", "#..", "###"],
    'M': ["#.#", "###", "###", "#.#", "#.#"],
    'N': ["#.#", "###", "###", "#.#", "#.#"],
    'O': [".#.", "#.#", "#.#", "#.#", ".#."],
    'P': ["##.", "#.#", "##.", "#..", "#.."],
    'Q': [".#.", "#.#", "#.#", ".#.", "..#"],
    'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'S': [".##", "#..", ".#.", "..#", "##."],
    'T': ["###", ".#.", ".#.", ".#.", ".#."],
    'U': ["#.#", "#.#", "#.#", "#.#", ".#."],
    'V': ["#.#", "#.#", "#.#", ".#.", ".#."],
    'W': ["#.#", "#.#", "###", "###", "#.#"],
    'X': ["#.#", "#.#", ".#.", "#.#", "#.#"],
    'Y': ["#.#", "#.#", ".#.", ".#.", ".#."],
    'Z': ["###", "..#", ".#.", "#..", "###"],
    '0': [".#.", "#.#", "#.#", "#.#", ".#."],
    '1': [".#.", "##.", ".#.", ".#.", "###"],
    '2': [".#.", "#.#", "..#", ".#.", "###"],
    '3': ["##.", "..#", ".#.", "..#", "##."],
    '4': ["#.#", "#.#", "###", "..#", "..#"],
    '5': ["###", "#..", "##.", "..#", "##."],
    '6': [".##", "#..", "##.", "#.#", ".#."],
    '7': ["###", "..#", ".#.", ".#.", ".#."],
    '8': [".#.", "#.#", ".#.", "#.#", ".#."],
    '9': [".#.", "#.#", ".##", "..#", "##."],
    ' ': ["...", "...", "...", "...", "..."],
    '.': ["...", "...", "...", "...", ".#."],
    ',': ["...", "...", "...", ".#.", "#.."],
    '!': [".#.", ".#.", ".#.", "...", ".#."],
    '?': [".#.", "#.#", "..#", "...", ".#."],
    ':': ["...", ".#.", "...", ".#.", "..."],
    '-': ["...", "...", "###", "...", "..."],
    '+': ["...", ".#.", "###", ".#.", "..."],
    '=': ["...", "###", "...", "###", "..."],
    '(': [".#.", "#..", "#..", "#..", ".#."],
    ')': [".#.", "..#", "..#", "..#", ".#."],
    '/': ["..#", "..#", ".#.", "#..", "#.."],
}


# Font metadata per font size
FONT_SPECS = {
    "3x5": {"font": FONT_3X5, "width": 3, "height": 5, "spacing": 1, "line_spacing": 1},
    "5x7": {"font": FONT_5X7, "width": 5, "height": 7, "spacing": 1, "line_spacing": 2},
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
#  Text Measurement (pretext-inspired: measure without creating objects)
# ═══════════════════════════════════════════════════════════

def measure_text_width(text: str, font_size: str = "5x7", scale: int = 1) -> int:
    """Measure the pixel width of a text string without creating a PixelText."""
    spec = FONT_SPECS.get(font_size, FONT_SPECS["5x7"])
    gw, gs = spec["width"], spec["spacing"]
    lines = text.split('\n')
    max_len = max((len(line) for line in lines), default=0)
    return max(0, max_len * (gw + gs) - gs) * scale


def measure_text_height(text: str, font_size: str = "5x7", scale: int = 1) -> int:
    """Measure the pixel height of a text string without creating a PixelText."""
    spec = FONT_SPECS.get(font_size, FONT_SPECS["5x7"])
    gh, ls = spec["height"], spec["line_spacing"]
    lines = text.split('\n')
    return max(0, len(lines) * (gh + ls) - ls) * scale


def wrap_text(text: str, max_width: int, font_size: str = "5x7", scale: int = 1) -> str:
    """Word-wrap text to fit within max_width pixels. Returns wrapped string."""
    spec = FONT_SPECS.get(font_size, FONT_SPECS["5x7"])
    gw, gs = spec["width"], spec["spacing"]
    char_w = (gw + gs) * scale

    result_lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip() if current_line else word
            test_width = len(test_line) * char_w - gs * scale
            if test_width <= max_width or not current_line:
                current_line = test_line
            else:
                result_lines.append(current_line)
                current_line = word
        if current_line:
            result_lines.append(current_line)
        elif not words or not paragraph:
            result_lines.append("")
    return '\n'.join(result_lines)


# ═══════════════════════════════════════════════════════════
#  PixelText PObject
# ═══════════════════════════════════════════════════════════

class PixelText(PObject):
    """Render text using a built-in bitmap font.

    Usage::

        title = PixelText("HELLO WORLD", x=10, y=10, color="#FFD700")
        small = PixelText("label", x=10, y=50, font_size="3x5")
        scene.add(title, small)
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
        font_size: str = "5x7",
        max_width: int = None,
    ):
        super().__init__(x=x, y=y, color=color)
        self.scale = max(1, scale)
        self.align = align    # "left", "center", "right"
        self.shadow = shadow
        self.shadow_color = parse_color(shadow_color)
        self.shadow_offset = shadow_offset
        self.max_chars = max_chars  # For TypeWriter animation
        self.font_size = font_size  # "3x5" or "5x7"
        self.max_width = max_width
        # Apply word-wrap if max_width is set
        if max_width is not None:
            self.text = wrap_text(text, max_width, font_size, self.scale)
        else:
            self.text = text

    @property
    def display_text(self) -> str:
        """Text to actually render (respects max_chars for TypeWriter)."""
        if self.max_chars is not None:
            return self.text[:int(self.max_chars)]
        return self.text

    @property
    def _font_spec(self):
        return FONT_SPECS.get(self.font_size, FONT_SPECS["5x7"])

    @property
    def text_width(self) -> int:
        """Width of the full text in pixels (before scaling)."""
        spec = self._font_spec
        gw = spec["width"]
        gs = spec["spacing"]
        lines = self.display_text.split('\n')
        max_len = max(len(line) for line in lines) if lines else 0
        return max(0, max_len * (gw + gs) - gs)

    @property
    def text_height(self) -> int:
        """Height of the full text in pixels (before scaling)."""
        spec = self._font_spec
        gh = spec["height"]
        ls = spec["line_spacing"]
        lines = self.display_text.split('\n')
        return max(0, len(lines) * (gh + ls) - ls)

    @property
    def width(self) -> int:
        return self.text_width * self.scale

    @property
    def height(self) -> int:
        return self.text_height * self.scale

    def get_bounds(self) -> Bounds:
        w, h = self.width, self.height
        if self.align == "center":
            return Bounds(int(self.x - w / 2), int(self.y), w, h)
        elif self.align == "right":
            return Bounds(int(self.x - w), int(self.y), w, h)
        return Bounds(int(self.x), int(self.y), w, h)

    def _get_glyph(self, char: str) -> list:
        """Get glyph for a character from the active font."""
        spec = self._font_spec
        font = spec["font"]
        upper = char.upper()
        if upper in font:
            return font[upper]
        empty_row = "." * spec["width"]
        return [empty_row for _ in range(spec["height"])]

    def render(self, canvas):
        if not self.visible:
            return

        spec = self._font_spec
        gw = spec["width"]
        gh = spec["height"]
        gs = spec["spacing"]
        ls = spec["line_spacing"]

        text = self.display_text
        lines = text.split('\n')
        color = self.get_render_color()

        for line_idx, line in enumerate(lines):
            line_y = int(self.y) + line_idx * (gh + ls) * self.scale

            # Calculate X offset for alignment
            line_width = len(line) * (gw + gs) - gs
            if self.align == "center":
                x_offset = int(self.x) - (line_width * self.scale) // 2
            elif self.align == "right":
                x_offset = int(self.x) - line_width * self.scale
            else:
                x_offset = int(self.x)

            for char_idx, char in enumerate(line):
                char_x = x_offset + char_idx * (gw + gs) * self.scale
                glyph = self._get_glyph(char)

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
