__version__ = "0.7.0"

# ── Configuration ───────────────────────────────────────────
from pixelengine.config import PixelConfig

# ── Layout Templates ───────────────────────────────────────
from pixelengine.layout import Layout, Zone

# ── Color System ────────────────────────────────────────────
from pixelengine.color import (
    parse_color,
    PICO8,
    GAMEBOY,
    NES,
    CHAR_COLORS,
)

# ── Base Class ──────────────────────────────────────────────
from pixelengine.pobject import PObject, Link, ReactTo

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
    # v4 Easing
    back_in,
    back_out,
    back_in_out,
    circ_in,
    circ_out,
    expo_in,
    expo_out,
    sine_in,
    sine_out,
    steps,
    custom_bezier,
    # v4 Stagger
    Stagger,
    # v4 Modifiers
    Delayed,
    Reversed,
    Looped,
    # v4 Spring Physics
    SpringTo,
    SpringScale,
)

# ── Organic Animation System (default) ─────────────────────
from pixelengine.organic import (
    MotionFeel, organic_noise,
    # Organic one-shot animations
    OrganicMoveTo, OrganicScale, OrganicFadeIn, OrganicFadeOut, OrganicRotate,
    Breathe, Sway, Float, Jitter, Pulse,
    SquashAndStretch, Wobble, Drift, Anticipate, Settle, RubberBand,
    # Organic modifiers
    WithNoise, WithFollow, WithAnticipation, WithSettle, WithSquashStretch,
    # Organic groups
    Wave, Cascade, Swarm,
    # Continuous motion updaters
    alive, hover, orbit_idle, wind_sway,
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
    VMorph,
)

# ── Path Animation (v4) ────────────────────────────────────
from pixelengine.pathanim import (
    BezierPath,
    QuadraticBezierPath,
    CircularPath,
    LinearPath,
    FollowPath,
)

# ── Keyframe Timeline (v4) ─────────────────────────────────
from pixelengine.keyframes import (
    Keyframe,
    KeyframeTrack,
    KeyframeAnimation,
)

# ── Text Animation (v4) ────────────────────────────────────
from pixelengine.textanim import (
    PerCharacter,
    PerWord,
    ScrambleReveal,
    TypeWriterPro,
    DynamicCaption,
    DynamicCaptionTrack,
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
from pixelengine.sprite import Sprite, ImageSprite

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

# ── Vector Graphics (v0.6.0) ───────────────────────────────
from pixelengine.vector import (
    VectorObject, SVGMobject,
    VPath, VLine, VCircle, VRect, VPolygon, VArrow, Vector,
)

# ── MathTex (v0.7.0) ───────────────────────────────────────
from pixelengine.mathtex import MathTex

# ── Scene Composition (v0.7.0) ─────────────────────────────
from pixelengine.compose import Compose

# ── Terrain (v0.7.0) ───────────────────────────────────────
from pixelengine.terrain import Terrain

# ── Shaders (v0.7.0) ───────────────────────────────────────
from pixelengine.shaders import (
    PixelShader, CRTScanlines, Ripple, HeatShimmer, Pixelate, ColorGrade,
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
    # v4 Transitions
    PixelateTransition,
    SlideTransition,
    GlitchTransition,
    ShatterTransition,
    CrossDissolve,
    # v4 Particle Burst
    ParticleBurst,
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
    NetworkGraph,
)

# ── Sound ───────────────────────────────────────────────────
from pixelengine.sound import SoundFX, SoundTimeline, note_freq
from pixelengine.voiceover import VoiceOver

# ── Pixel Art Generation ───────────────────────────────────
from pixelengine.pixelart import PixelArtist, PALETTES, SKIN_TONES

# ── Scene ───────────────────────────────────────────────────
from pixelengine.scene import Scene

__all__ = [
    # Core
    "PixelConfig", "Scene", "PObject",
    # Layout
    "Layout", "Zone",
    # Shapes
    "Rect", "Circle", "Line", "Triangle", "Polygon",
    # Organic Animation System (default)
    "MotionFeel", "organic_noise",
    "OrganicMoveTo", "OrganicScale", "OrganicFadeIn", "OrganicFadeOut", "OrganicRotate",
    "Breathe", "Sway", "Float", "Jitter", "Pulse",
    "SquashAndStretch", "Wobble", "Drift", "Anticipate", "Settle", "RubberBand",
    "WithNoise", "WithFollow", "WithAnticipation", "WithSettle", "WithSquashStretch",
    "Wave", "Cascade", "Swarm",
    "alive", "hover", "orbit_idle", "wind_sway",
    # Animation (classic)
    "Animation", "MoveTo", "MoveBy",
    "FadeIn", "FadeOut", "Scale", "Rotate",
    "Blink", "ColorShift",
    "AnimationGroup", "Sequence",
    # v4 Animation Groups & Modifiers
    "Stagger", "Delayed", "Reversed", "Looped",
    # v4 Spring Physics
    "SpringTo", "SpringScale",
    # Easing
    "linear", "ease_in", "ease_out", "ease_in_out",
    "bounce", "elastic",
    "back_in", "back_out", "back_in_out",
    "circ_in", "circ_out", "expo_in", "expo_out",
    "sine_in", "sine_out", "steps", "custom_bezier",
    # Construction (Manim-like)
    "GrowFromPoint", "GrowFromEdge", "DrawBorderThenFill",
    "Create", "Uncreate", "ShowPassingFlash", "GrowArrow",
    # Transform
    "MorphTo", "ReplacementTransform", "TransformMatchingPoints", "VMorph",
    # v4 Path Animation
    "BezierPath", "QuadraticBezierPath", "CircularPath",
    "LinearPath", "FollowPath",
    # v4 Keyframe Timeline
    "Keyframe", "KeyframeTrack", "KeyframeAnimation",
    # v4 Text Animation
    "PerCharacter", "PerWord", "ScrambleReveal", "TypeWriterPro",
    "DynamicCaption", "DynamicCaptionTrack",
    # Math Objects
    "ValueTracker", "NumberLine", "BarChart", "Axes", "Graph", "Dot",
    # Vector
    "VectorObject", "SVGMobject",
    "VPath", "VLine", "VCircle", "VRect", "VPolygon", "VArrow", "Vector",
    # v0.7.0
    "MathTex", "Compose", "Terrain",
    "PixelShader", "CRTScanlines", "Ripple", "HeatShimmer", "Pixelate", "ColorGrade",
    # Text
    "PixelText", "TypeWriter",
    # Sprite
    "Sprite", "ImageSprite",
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
    # v4 Transitions
    "PixelateTransition", "SlideTransition", "GlitchTransition",
    "ShatterTransition", "CrossDissolve",
    # v4 Particle Burst
    "ParticleBurst",
    # v4 Reactive Links
    "Link", "ReactTo",
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
    "Pendulum", "Spring", "OrbitalSystem", "Rope", "FluidParticles", "NetworkGraph",
    # Sound
    "SoundFX", "SoundTimeline", "note_freq", "VoiceOver",
    # Pixel Art Generation
    "PixelArtist", "PALETTES", "SKIN_TONES",
    # Color
    "parse_color", "PICO8", "GAMEBOY", "NES", "CHAR_COLORS",
]
