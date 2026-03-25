"""PixelEngine — A code-first pixel art animation engine."""
__version__ = "0.1.0"

# ── Configuration ───────────────────────────────────────────
from pixelengine.config import PixelConfig

# ── Color System ────────────────────────────────────────────
from pixelengine.color import (
    parse_color,
    PICO8,
    GAMEBOY,
    NES,
    CHAR_COLORS,
)

# ── Base Class ──────────────────────────────────────────────
from pixelengine.pobject import PObject

# ── Shapes ──────────────────────────────────────────────────
from pixelengine.shapes import Rect, Circle, Line, Triangle, Polygon

# ── Scene ───────────────────────────────────────────────────
from pixelengine.scene import Scene

__all__ = [
    # Core
    "PixelConfig",
    "Scene",
    "PObject",
    # Shapes
    "Rect",
    "Circle",
    "Line",
    "Triangle",
    "Polygon",
    # Color
    "parse_color",
    "PICO8",
    "GAMEBOY",
    "NES",
    "CHAR_COLORS",
]
