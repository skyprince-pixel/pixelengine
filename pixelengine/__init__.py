__version__ = "0.7.2"

# ── Configuration ───────────────────────────────────────────
from pixelengine.config import PixelConfig

# ── Layout Templates ───────────────────────────────────────
# TIP: Always use Layout.portrait() or Layout.landscape() for positioning.
#      Never hardcode coordinates. Access L.TITLE_ZONE, L.MAIN_ZONE, etc.
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
# TIP: Prefer OrganicMoveTo/OrganicFadeIn over MoveTo/FadeIn for natural motion.
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

# ── Organic Animation System (PREFER THESE over classic) ───
# TIP: These produce natural, physics-inspired motion. Use OrganicMoveTo
#      instead of MoveTo, Cascade for group reveals, alive() for ambient life.
from pixelengine.organic import (
    MotionFeel, organic_noise,
    # Organic one-shot animations
    OrganicMoveTo, OrganicScale, OrganicFadeIn, OrganicFadeOut, OrganicRotate,
    Breathe, Sway, Float, Jitter, Pulse,
    SquashAndStretch, Wobble, Drift, Anticipate, Settle, RubberBand,
    # Organic modifiers (wrap any animation)
    WithNoise, WithFollow, WithAnticipation, WithSettle, WithSquashStretch,
    # Organic groups (use for multi-object reveals)
    Wave, Cascade, Swarm,
    # Continuous motion updaters (attach to objects for ambient life)
    alive, hover, orbit_idle, wind_sway,
)

# ── Construction Animations (Manim-like reveals) ───────────
# TIP: Never just self.add(obj). Always reveal with Create, DrawBorderThenFill,
#      or GrowFromPoint for progressive, cinematic construction.
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
# TIP: Use VMorph to smoothly morph one VectorObject into another.
from pixelengine.transform import (
    MorphTo,
    ReplacementTransform,
    TransformMatchingPoints,
    VMorph,
)

# ── Path Animation (v4) ────────────────────────────────────
# TIP: Use FollowPath + BezierPath for curved motion instead of linear MoveTo.
from pixelengine.pathanim import (
    BezierPath,
    QuadraticBezierPath,
    CircularPath,
    LinearPath,
    FollowPath,
)

# ── Keyframe Timeline (v4) ─────────────────────────────────
# TIP: For complex multi-property animations, build a KeyframeTrack timeline.
from pixelengine.keyframes import (
    Keyframe,
    KeyframeTrack,
    KeyframeAnimation,
)

# ── Text Animation (v4) ────────────────────────────────────
# TIP: Use DynamicCaption for voiceover-synced subtitles.
#      Use PerCharacter or ScrambleReveal instead of plain TypeWriter.
from pixelengine.textanim import (
    PerCharacter,
    PerWord,
    ScrambleReveal,
    TypeWriterPro,
    DynamicCaption,
    DynamicCaptionTrack,
)

# ── Math Objects ────────────────────────────────────────────
# TIP: Use BarChart + GrowFromEdge for animated chart reveals.
#      Use ValueTracker for smoothly interpolating numeric values.
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
# TIP: Use ImageSprite to import real images with palette quantization.
from pixelengine.sprite import Sprite, ImageSprite

# ── Camera ──────────────────────────────────────────────
# TIP: Use self.camera.shake(intensity=8) on reveals for impact.
#      Use self.camera.set_focus(x, y, radius) for depth-of-field blur.
from pixelengine.camera import Camera, CameraPan, CameraZoom, CameraCenterOn

# ── Lighting ────────────────────────────────────────────
# TIP: Always use at least AmbientLight + one PointLight for depth.
#      Set obj.casts_shadow = True for realistic shadows.
from pixelengine.lighting import (
    AmbientLight,
    PointLight,
    DirectionalLight,
    LightingEngine,
)

# ── Camera Effects ──────────────────────────────────────
# TIP: Vignette + ColorGrade is the minimum for cinematic quality.
#      Use ChromaticAberration on impact/glitch moments.
from pixelengine.camerafx import (
    DepthOfField,
    Vignette,
    ChromaticAberration,
    Letterbox,
    FilmGrain,
    CameraFXPipeline,
)

# ── Vector Graphics (v0.6.0) ───────────────────────────────
# TIP: VectorObjects are resolution-independent. Use them for smooth curves
#      and mathematical diagrams. Support Create, DrawBorderThenFill, VMorph.
from pixelengine.vector import (
    VectorObject, SVGMobject,
    VPath, VLine, VCircle, VRect, VPolygon, VArrow, Vector,
)

# ── MathTex (v0.7.0) ───────────────────────────────────────
# TIP: Render LaTeX equations as pixel art: MathTex(r"E = mc^2")
from pixelengine.mathtex import MathTex

# ── Scene Composition (v0.7.0) ─────────────────────────────
from pixelengine.compose import Compose

# ── Terrain (v0.7.0) ───────────────────────────────────────
# TIP: Procedural landscape backgrounds — no image files needed.
from pixelengine.terrain import Terrain

# ── Shaders (v0.7.0) ───────────────────────────────────────
# TIP: Add as camera FX. CRTScanlines for retro, ColorGrade for tinting.
from pixelengine.shaders import (
    PixelShader, CRTScanlines, Ripple, HeatShimmer, Pixelate, ColorGrade,
)

# ── Background ──────────────────────────────────────────────
# TIP: Use Starfield for space scenes, ParallaxLayer for scrolling BGs.
from pixelengine.background import (
    Background,
    GradientBackground,
    Starfield,
    ParallaxLayer,
)

# ── Effects ─────────────────────────────────────────────────
# TIP: Use GlitchTransition or ShatterTransition between scenes.
#      Use ParticleBurst.explode() on dramatic reveals.
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
# TIP: Never use flat hex colors alone! Apply GradientTexture or
#      PatternTexture to Rect backgrounds for visual richness.
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
# TIP: Use Cube3D/Sphere3D for 3D objects. Orbit3D for camera orbits.
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
# TIP: Use PhysicsWorld for realistic gravity/bounce. Set self.physics = world
#      and it auto-steps during wait(). Or use self.enable_physics() shortcut.
#      Pendulum, Spring, Rope are ready-made simulations.
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
# TIP: SoundFX.dynamic("reveal"), SoundFX.dynamic("impact") etc. generate
#      context-aware sounds. Use on every key visual moment!
from pixelengine.sound import SoundFX, SoundTimeline, note_freq
from pixelengine.voiceover import VoiceOver

# ── Pixel Art Generation ───────────────────────────────────
# TIP: Generate characters/backgrounds procedurally — no image files needed.
#      PixelArtist.character(style="knight", palette="pico8")
from pixelengine.pixelart import PixelArtist, PALETTES, SKIN_TONES

# ── Scene ───────────────────────────────────────────────────
# TIP: Use CinematicScene (not bare Scene) for access to helper methods:
#      setup_atmosphere(), narrate(), enable_physics(), transition()
from pixelengine.scene import Scene
from pixelengine.cinematic import CinematicScene, CleanScene

# ── Declarative Layouts (v0.7.1) ───────────────────────────
# TIP: Use VStack/HStack to auto-arrange children. Never manually compute offsets.
from pixelengine.group import Group, VStack, HStack

__all__ = [
    # Core
    "PixelConfig", "Scene", "CinematicScene", "CleanScene", "PObject",
    # Layout
    "Layout", "Zone", "Group", "VStack", "HStack",
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
