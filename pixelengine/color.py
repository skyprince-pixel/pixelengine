"""PixelEngine color system — palettes, parsing, and character shorthand."""
from typing import Union, Tuple, Optional, Dict


# ── Named Colors ────────────────────────────────────────────

NAMED_COLORS: Dict[str, Tuple[int, int, int, int]] = {
    "black":       (0, 0, 0, 255),
    "white":       (255, 255, 255, 255),
    "red":         (255, 0, 0, 255),
    "green":       (0, 255, 0, 255),
    "blue":        (0, 0, 255, 255),
    "yellow":      (255, 255, 0, 255),
    "cyan":        (0, 255, 255, 255),
    "magenta":     (255, 0, 255, 255),
    "orange":      (255, 165, 0, 255),
    "purple":      (128, 0, 128, 255),
    "pink":        (255, 192, 203, 255),
    "gray":        (128, 128, 128, 255),
    "grey":        (128, 128, 128, 255),
    "brown":       (139, 69, 19, 255),
    "transparent": (0, 0, 0, 0),
}


# ── Retro Palettes ──────────────────────────────────────────

PICO8: Dict[str, Tuple[int, int, int, int]] = {
    "black":       (0, 0, 0, 255),
    "dark_blue":   (29, 43, 83, 255),
    "dark_purple": (126, 37, 83, 255),
    "dark_green":  (0, 135, 81, 255),
    "brown":       (171, 82, 54, 255),
    "dark_gray":   (95, 87, 79, 255),
    "light_gray":  (194, 195, 199, 255),
    "white":       (255, 241, 232, 255),
    "red":         (255, 0, 77, 255),
    "orange":      (255, 163, 0, 255),
    "yellow":      (255, 236, 39, 255),
    "green":       (0, 228, 54, 255),
    "blue":        (41, 173, 255, 255),
    "lavender":    (131, 118, 156, 255),
    "pink":        (255, 119, 168, 255),
    "peach":       (255, 204, 170, 255),
}

GAMEBOY: Dict[str, Tuple[int, int, int, int]] = {
    "darkest":  (15, 56, 15, 255),
    "dark":     (48, 98, 48, 255),
    "light":    (139, 172, 15, 255),
    "lightest": (155, 188, 15, 255),
}

NES: Dict[str, Tuple[int, int, int, int]] = {
    "black":        (0, 0, 0, 255),
    "dark_gray":    (88, 88, 88, 255),
    "medium_gray":  (124, 124, 124, 255),
    "light_gray":   (168, 168, 168, 255),
    "white":        (248, 248, 248, 255),
    "dark_red":     (168, 16, 0, 255),
    "red":          (228, 0, 0, 255),
    "light_red":    (248, 120, 88, 255),
    "dark_orange":  (168, 52, 0, 255),
    "orange":       (248, 56, 0, 255),
    "light_orange": (248, 168, 0, 255),
    "dark_yellow":  (168, 88, 0, 255),
    "yellow":       (248, 184, 0, 255),
    "light_yellow": (248, 216, 120, 255),
    "dark_green":   (0, 120, 0, 255),
    "green":        (0, 168, 0, 255),
    "light_green":  (88, 216, 84, 255),
    "dark_cyan":    (0, 120, 56, 255),
    "cyan":         (0, 184, 0, 255),
    "light_cyan":   (88, 248, 152, 255),
    "dark_blue":    (0, 64, 168, 255),
    "blue":         (0, 120, 248, 255),
    "light_blue":   (104, 136, 252, 255),
    "dark_purple":  (68, 0, 168, 255),
    "purple":       (104, 68, 252, 255),
    "light_purple": (152, 120, 248, 255),
    "dark_magenta": (148, 0, 132, 255),
    "magenta":      (216, 0, 204, 255),
    "light_magenta":(248, 120, 248, 255),
    "dark_pink":    (168, 0, 32, 255),
    "pink":         (248, 88, 152, 255),
    "light_pink":   (248, 168, 176, 255),
    "skin_dark":    (168, 100, 16, 255),
    "skin":         (232, 168, 56, 255),
    "skin_light":   (248, 216, 168, 255),
}


# ── Character Shorthand for ASCII Sprites ───────────────────

CHAR_COLORS: Dict[str, Optional[str]] = {
    ".": None,       # transparent
    " ": None,       # transparent (space)
    "R": "#FF004D",  # red (PICO-8)
    "G": "#00E436",  # green (PICO-8)
    "B": "#29ADFF",  # blue (PICO-8)
    "Y": "#FFEC27",  # yellow (PICO-8)
    "W": "#FFF1E8",  # white (PICO-8)
    "K": "#000000",  # black (K for key)
    "O": "#FFA300",  # orange (PICO-8)
    "P": "#FF77A8",  # pink (PICO-8)
    "C": "#83769C",  # cool gray / lavender
    "D": "#5F574F",  # dark gray
    "L": "#C2C3C7",  # light gray
    "N": "#1D2B53",  # navy / dark blue
    "M": "#7E2553",  # magenta / dark purple
    "T": "#008751",  # teal / dark green
    "A": "#AB5236",  # auburn / brown
    "E": "#FFCCAA",  # peach
}


# ── Color Parsing ───────────────────────────────────────────

def parse_color(
    color: Union[str, Tuple[int, ...], list, None]
) -> Tuple[int, int, int, int]:
    """Parse a color value to an (R, G, B, A) tuple.

    Accepts:
      - Hex string: "#FF0000", "#FF0000FF", "#F00"
      - Named color: "red", "blue", "transparent"
      - RGB tuple: (255, 0, 0)
      - RGBA tuple: (255, 0, 0, 255)
      - None: returns transparent (0, 0, 0, 0)
    """
    if color is None:
        return (0, 0, 0, 0)

    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            return (int(color[0]), int(color[1]), int(color[2]), 255)
        elif len(color) == 4:
            return (int(color[0]), int(color[1]), int(color[2]), int(color[3]))
        else:
            raise ValueError(f"Color tuple must have 3 or 4 values, got {len(color)}")

    if isinstance(color, str):
        # Named color lookup
        lower = color.lower().strip()
        if lower in NAMED_COLORS:
            return NAMED_COLORS[lower]

        # Hex string
        hex_str = color.lstrip("#")
        if len(hex_str) == 3:
            # #RGB → #RRGGBB
            hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return (r, g, b, 255)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
            return (r, g, b, a)

    raise ValueError(f"Cannot parse color: {color!r}")
