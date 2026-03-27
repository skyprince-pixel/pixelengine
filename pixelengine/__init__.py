"""PixelEngine — A code-first pixel art animation engine."""
__version__ = "0.3.0"

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

# ── Construction Animations (Manim-like) ───────────────────
from pixelengine.construction import (
    GrowFromPoint,
    GrowFromEdge,
    DrawBorderThenFill,
    Create,
    Uncreate,
    ShowPassingFlash,
    GrowArrow,
)

# ── Transform Animations ───────────────────────────────────
from pixelengine.transform import (
    MorphTo,
    ReplacementTransform,
    TransformMatchingPoints,
)

# ── Math Objects ────────────────────────────────────────────
from pixelengine.mathobjects import (
    ValueTracker,
    NumberLine,
    BarChart,
    Axes,
    Graph,
    Dot,
)

# ── Text ────────────────────────────────────────────────────
from pixelengine.text import PixelText, TypeWriter

# ── Sprite ──────────────────────────────────────────────────
from pixelengine.sprite import Sprite

# ── Camera ──────────────────────────────────────────────
from pixelengine.camera import Camera, CameraPan, CameraZoom, CameraCenterOn

# ── Lighting ────────────────────────────────────────────
from pixelengine.lighting import (
    AmbientLight,
    PointLight,
    DirectionalLight,
    LightingEngine,
)

# ── Camera Effects ──────────────────────────────────────
from pixelengine.camerafx import (
    DepthOfField,
    Vignette,
    ChromaticAberration,
    Letterbox,
    FilmGrain,
    CameraFXPipeline,
)

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
    IrisTransition,
    DissolveTransition,
    Trail,
    ScreenFlash,
    Outline,
    Grid,
)

# ── TileMap ─────────────────────────────────────────────────
from pixelengine.tilemap import TileSet, TileMap

# ── Texture System ─────────────────────────────────────────
from pixelengine.texture import (
    Texture,
    PatternTexture,
    DitherTexture,
    NoiseTexture,
    GradientTexture,
    AnimatedTexture,
    ScrollingTexture,
)

# ── 3D System ──────────────────────────────────────────────
from pixelengine.math3d import Vec3, Mat4
from pixelengine.objects3d import (
    Object3D,
    Cube3D,
    Sphere3D,
    Pyramid3D,
    Cylinder3D,
    Mesh3D,
    Axes3D,
)
from pixelengine.camera3d import Camera3D, IsoCamera, Orbit3D, Zoom3D

# ── Physics / Simulation ──────────────────────────────────
from pixelengine.physics import PhysicsBody, PhysicsWorld
from pixelengine.collision import (
    CollisionCallback,
    StaticBody,
    Bounds,
)
from pixelengine.simulations import (
    Pendulum,
    Spring,
    OrbitalSystem,
    Rope,
    FluidParticles,
)

# ── Sound ───────────────────────────────────────────────────
from pixelengine.sound import SoundFX, SoundTimeline
from pixelengine.voiceover import VoiceOver

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
    # Construction (Manim-like)
    "GrowFromPoint", "GrowFromEdge", "DrawBorderThenFill",
    "Create", "Uncreate", "ShowPassingFlash", "GrowArrow",
    # Transform
    "MorphTo", "ReplacementTransform", "TransformMatchingPoints",
    # Math Objects
    "ValueTracker", "NumberLine", "BarChart", "Axes", "Graph", "Dot",
    # Text
    "PixelText", "TypeWriter",
    # Sprite
    "Sprite",
    # Camera
    "Camera", "CameraPan", "CameraZoom", "CameraCenterOn",
    # Lighting
    "AmbientLight", "PointLight", "DirectionalLight", "LightingEngine",
    # Camera Effects
    "DepthOfField", "Vignette", "ChromaticAberration",
    "Letterbox", "FilmGrain", "CameraFXPipeline",
    # Background
    "Background", "GradientBackground", "Starfield", "ParallaxLayer",
    # Effects
    "ParticleEmitter",
    "FadeTransition", "WipeTransition", "IrisTransition", "DissolveTransition",
    "Trail", "ScreenFlash", "Outline", "Grid",
    # TileMap
    "TileSet", "TileMap",
    # Texture
    "Texture", "PatternTexture", "DitherTexture", "NoiseTexture",
    "GradientTexture", "AnimatedTexture", "ScrollingTexture",
    # 3D
    "Vec3", "Mat4", "Object3D", "Cube3D", "Sphere3D", "Pyramid3D",
    "Cylinder3D", "Mesh3D", "Axes3D",
    "Camera3D", "IsoCamera", "Orbit3D", "Zoom3D",
    # Physics / Simulation
    "PhysicsBody", "PhysicsWorld",
    "CollisionCallback", "StaticBody", "Bounds",
    "Pendulum", "Spring", "OrbitalSystem", "Rope", "FluidParticles",
    # Sound
    "SoundFX", "SoundTimeline", "VoiceOver",
    # Color
    "parse_color", "PICO8", "GAMEBOY", "NES", "CHAR_COLORS",
]
