"""PixelEngine code block — syntax-highlighted code display for education videos."""
import re
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color
from pixelengine.text import FONT_5X7


# Simple keyword sets for common languages
_KEYWORDS = {
    "python": {"def", "class", "if", "elif", "else", "for", "while", "return",
               "import", "from", "as", "with", "try", "except", "finally",
               "raise", "yield", "lambda", "pass", "break", "continue",
               "and", "or", "not", "in", "is", "None", "True", "False",
               "async", "await", "self", "print"},
    "javascript": {"function", "const", "let", "var", "if", "else", "for",
                    "while", "return", "class", "new", "this", "import",
                    "export", "from", "async", "await", "try", "catch",
                    "throw", "true", "false", "null", "undefined",
                    "console", "typeof"},
    "generic": {"if", "else", "for", "while", "return", "class", "def",
                "function", "var", "let", "const", "true", "false", "null",
                "import", "from"},
}

# Default syntax highlighting colors (pixel-art friendly)
_THEME = {
    "background": "#1D2B53",
    "text": "#FFF1E8",
    "keyword": "#FF004D",
    "string": "#00E436",
    "comment": "#83769C",
    "number": "#FFEC27",
    "line_number": "#5F574F",
    "border": "#29ADFF",
}


class CodeBlock(PObject):
    """Syntax-highlighted code block for programming education videos.

    Usage::

        code = CodeBlock(
            code=\"\"\"def hello():
    print("world")
\"\"\",
            language="python",
            x=30, y=30,
        )
        scene.add(code)
        scene.play(Create(code), duration=1.0)
    """

    def __init__(
        self,
        code: str,
        language: str = "python",
        x: int = 0,
        y: int = 0,
        scale: int = 1,
        show_line_numbers: bool = True,
        theme: dict = None,
        padding: int = 4,
        max_chars: int = None,
    ):
        super().__init__(x=x, y=y)
        self.code = code.rstrip("\n")
        self.language = language
        self.scale = scale
        self.show_line_numbers = show_line_numbers
        self.theme = {**_THEME, **(theme or {})}
        self.padding = padding
        self.max_chars = max_chars  # For TypeWriter-like reveal
        self.z_index = 5

        self._lines = self.code.split("\n")
        self._keywords = _KEYWORDS.get(language, _KEYWORDS["generic"])

        # Calculate dimensions
        char_w = 6 * scale  # 5px char + 1px spacing
        char_h = 8 * scale  # 7px char + 1px spacing
        max_line_len = max((len(line) for line in self._lines), default=0)
        ln_width = (len(str(len(self._lines))) + 1) * char_w if show_line_numbers else 0

        self.width = ln_width + max_line_len * char_w + padding * 2
        self.height = len(self._lines) * char_h + padding * 2

    def _tokenize_line(self, line):
        """Simple tokenizer returning (text, token_type) pairs."""
        tokens = []
        i = 0
        while i < len(line):
            # Comment
            if line[i] == '#' or (i + 1 < len(line) and line[i:i+2] == '//'):
                tokens.append((line[i:], "comment"))
                break
            # String (single or double quote)
            if line[i] in ('"', "'"):
                quote = line[i]
                j = i + 1
                while j < len(line) and line[j] != quote:
                    if line[j] == '\\':
                        j += 1
                    j += 1
                j = min(j + 1, len(line))
                tokens.append((line[i:j], "string"))
                i = j
                continue
            # Number
            if line[i].isdigit() or (line[i] == '.' and i + 1 < len(line) and line[i+1].isdigit()):
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == '.'):
                    j += 1
                tokens.append((line[i:j], "number"))
                i = j
                continue
            # Word (identifier or keyword)
            if line[i].isalpha() or line[i] == '_':
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                    j += 1
                word = line[i:j]
                token_type = "keyword" if word in self._keywords else "text"
                tokens.append((word, token_type))
                i = j
                continue
            # Other character
            tokens.append((line[i], "text"))
            i += 1
        return tokens

    def _draw_char(self, img, ch, px, py, color, scale):
        """Draw a single character from the bitmap font."""
        glyph = FONT_5X7.get(ch, FONT_5X7.get('?'))
        if glyph is None:
            return
        for row_idx, row in enumerate(glyph):
            for col_idx, bit in enumerate(row):
                if bit:
                    for sy in range(scale):
                        for sx in range(scale):
                            x = px + col_idx * scale + sx
                            y = py + row_idx * scale + sy
                            if 0 <= x < img.width and 0 <= y < img.height:
                                img.putpixel((x, y), color)

    def render(self, canvas):
        if not self.visible:
            return

        bg_color = parse_color(self.theme["background"])
        bg_color = (*bg_color[:3], int(bg_color[3] * self.opacity))

        img = Image.new("RGBA", (self.width, self.height), bg_color)

        char_w = 6 * self.scale
        char_h = 8 * self.scale
        pad = self.padding
        ln_chars = len(str(len(self._lines))) + 1 if self.show_line_numbers else 0
        ln_width = ln_chars * char_w

        total_chars = 0
        max_chars = self.max_chars

        for line_idx, line in enumerate(self._lines):
            y = pad + line_idx * char_h

            # Line number
            if self.show_line_numbers:
                ln_str = str(line_idx + 1).rjust(ln_chars - 1)
                ln_color = parse_color(self.theme["line_number"])
                ln_color = (*ln_color[:3], int(ln_color[3] * self.opacity))
                for ci, ch in enumerate(ln_str):
                    self._draw_char(img, ch, pad + ci * char_w, y, ln_color, self.scale)

            # Code tokens
            col = 0
            tokens = self._tokenize_line(line)
            for text, token_type in tokens:
                color = parse_color(self.theme.get(token_type, self.theme["text"]))
                color = (*color[:3], int(color[3] * self.opacity))
                for ch in text:
                    if max_chars is not None and total_chars >= max_chars:
                        break
                    px = pad + ln_width + col * char_w
                    self._draw_char(img, ch, px, y, color, self.scale)
                    col += 1
                    total_chars += 1
                if max_chars is not None and total_chars >= max_chars:
                    break
            if max_chars is not None and total_chars >= max_chars:
                break

        canvas.blit(img, int(self.x), int(self.y))
