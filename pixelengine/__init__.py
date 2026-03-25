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

# ── Animation ───────────────────────────────────────────────
from pixelengine.animation import (
    Animation,
    MoveTo,
    MoveBy,
    FadeIn,
    FadeOut,
    Scale,
    Rotate,
    Blink,
    ColorShift,
    AnimationGroup,
    Sequence,
    linear,
    ease_in,
    ease_out,
    ease_in_out,
    bounce,
    elastic,
)

# ── Text ────────────────────────────────────────────────────
from pixelengine.text import PixelText, TypeWriter

# ── Sprite ──────────────────────────────────────────────────
from pixelengine.sprite import Sprite

# ── Camera ──────────────────────────────────────────────────
from pixelengine.camera import Camera, CameraPan, CameraZoom, CameraCenterOn

# ── Background ──────────────────────────────────────────────
from pixelengine.background import (
    Background,
    GradientBackground,
    Starfield,
    ParallaxLayer,
)

# ── Effects ─────────────────────────────────────────────────
from pixelengine.effects import (
    ParticleEmitter,
    FadeTransition,
    WipeTransition,
    Trail,
)

# ── TileMap ─────────────────────────────────────────────────
from pixelengine.tilemap import TileSet, TileMap

# ── Scene ───────────────────────────────────────────────────
from pixelengine.scene import Scene

__all__ = [
    # Core
    "PixelConfig", "Scene", "PObject",
    # Shapes
    "Rect", "Circle", "Line", "Triangle", "Polygon",
    # Animation
    "Animation", "MoveTo", "MoveBy",
    "FadeIn", "FadeOut", "Scale", "Rotate",
    "Blink", "ColorShift",
    "AnimationGroup", "Sequence",
    # Easing
    "linear", "ease_in", "ease_out", "ease_in_out",
    "bounce", "elastic",
    # Text
    "PixelText", "TypeWriter",
    # Sprite
    "Sprite",
    # Camera
    "Camera", "CameraPan", "CameraZoom", "CameraCenterOn",
    # Background
    "Background", "GradientBackground", "Starfield", "ParallaxLayer",
    # Effects
    "ParticleEmitter", "FadeTransition", "WipeTransition", "Trail",
    # TileMap
    "TileSet", "TileMap",
    # Color
    "parse_color", "PICO8", "GAMEBOY", "NES", "CHAR_COLORS",
]
