# PixelEngine v0.9.0

**PixelEngine** is a specialized, code-first Python framework for generating educational, animated pixel art videos. It renders at a configurable canvas resolution (default **480×270**) and upscales with nearest-neighbor to **1920×1080** (Full HD) for crisp pixel edges.

All rendering is done via **Pillow** images encoded straight into **ffmpeg** with programmatic logic and math. No external graphic files or audio files are required by default.

---

## Technical Stack & Requirements

1. **Python**: 3.8+ (Virtual Environment **highly** recommended)
2. **Core Dependencies**: `Pillow`, `numpy`
3. **Optional High-Performance Packages**: `av` (PyAV for 3x faster video encoding), `pymunk` (for rigid-body physics), `pydub` (for professional audio mixing), `pedalboard` (for premium audio effects like Reverb/Chorus). Install all with `pip install .[perf]`.
4. **Audio Dependencies**: `soundfile`, `kokoro-onnx` (default TTS), `chatterbox-tts`, `torch`, `torchaudio` (optional high-quality TTS)
5. **System Dep**: `ffmpeg` (must be accessible in PATH to mux final MP4s).

---

## 1. Core Architecture (The `Scene`)

Everything happens inside a `Scene`. You override the `construct()` method to place objects (`self.add()`), advance time (`self.wait()`), and interpolate animations (`self.play()`).

```python
from pixelengine import Scene, PixelConfig, Rect, PixelText, TypeWriter

class MyAnimation(Scene):
    def construct(self):
        # 1. Set background colour (covers entire canvas)
        self.set_background("#1D2B53")

        # 2. Add some text
        text = PixelText("HELLO GALAXY", x=240, y=135, align="center")
        self.add(text)

        # 3. Animate TypeWriter taking exactly 2.0 seconds
        self.play(TypeWriter(text), duration=2.0)
        self.wait(1.0)

# Render
if __name__ == "__main__":
    MyAnimation(PixelConfig.landscape()).render("output.mp4")
```

- **Config**: Default canvas is **480×270** upscaled 4x to **1920×1080** at **24 FPS**.
- **Coordinates**: `(0,0)` is top-left. All coordinates are in canvas-space.
- **Z-Index**: Control layering with `.z_index`. Lower draws behind higher.

### Resolution Presets

| Preset | Canvas | Output | Use Case |
|--------|--------|--------|----------|
| `PixelConfig()` | 480×270 | 1920×1080 | Default (Full HD) |
| `PixelConfig.landscape()` | 480×270 | 1920×1080 | YouTube landscape |
| `PixelConfig.portrait()` | 270×480 | 1080×1920 | YouTube Shorts |
| `PixelConfig.retro()` | 256×144 | 1024×576 | Classic 8-bit style |
| `PixelConfig.square()` | 384×384 | 1536×1536 | Square format |
| `PixelConfig.hd()` | 320×180 | 1280×720 | HD 720p |
| `PixelConfig.full_hd()` | 480×270 | 1920×1080 | Full HD 1080p |
| `PixelConfig.qhd()` | 640×360 | 2560×1440 | QHD 2K |

### Layout Templates

Use `Layout` for consistent positioning across videos. Never guess coordinates.

```python
from pixelengine.layout import Layout

L = Layout.portrait()  # 270×480

# Named zones — each returns Zone(x, y, width, height)
L.TITLE_ZONE      # Top area for titles
L.SUBTITLE_ZONE   # Below title
L.MAIN_ZONE       # Center stage
L.LOWER_THIRD     # Lower-third captions
L.FOOTER_ZONE     # Bottom strip

# Safe margins
L.SAFE_LEFT, L.SAFE_RIGHT, L.SAFE_TOP, L.SAFE_BOTTOM

# Helpers
L.center()              # (135, 240)
L.full_bg()             # (270, 480, 135, 240) for Rect
L.grid(rows, cols)      # Grid positions in MAIN_ZONE
L.stack(n)              # Vertical stack in MAIN_ZONE
L.horizontal(n)         # Horizontal row in MAIN_ZONE
```

Available presets: `Layout.portrait()`, `Layout.landscape()`, `Layout.retro()`, `Layout.square()`.

---

## 2. Shapes & Primitives
Primitives cover standard geometry.
- `Rect(width, height, x, y, color, opacity)`
- `Circle(radius, x, y, color)`
- `Line(x_start, y_start, x_end, y_end, color)`
- `Triangle(x1, y1, x2, y2, x3, y3, color)`

*Note*: Colors can be passed as standard `"HEX"` strings. `pixelengine.color` has built-in palettes (`PICO8`, `GAMEBOY`, `NES`).

### Per-Object Quality Control (v3)
Every object has a `render_quality` property that controls its individual pixel resolution:
```python
obj.render_quality = 0.3   # Extra chunky/pixelated (retro style)
obj.render_quality = 1.0   # Normal (default)
obj.render_quality = 2.0   # Smooth, anti-aliased look
```

### Lighting Properties (v3)
Every object has lighting interaction properties:
```python
obj.casts_shadow = True        # Object casts shadows from lights
obj.receives_light = True      # Lighting affects this object
obj.shadow_opacity = 0.4       # Shadow darkness (0.0–1.0)
```

---

## 3. The Animation System
Use `self.play(*animations, duration=X)` to run interpolation frames.
- **Transforms**: `MoveTo`, `MoveBy`, `Scale`, `Rotate`, `ColorShift`.
- **Visibility**: `FadeIn`, `FadeOut`, `Blink`.
- **Text**: `TypeWriter` (Reveals text character by character).
- **Control Flow**: `AnimationGroup` (fires concurrently), `Sequence` (fires linearly), `Stagger` (fires with cascade delay).

**Easing Functions**: Pass `easing=...` into an animation.
Available easings: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `bounce`, `elastic`, `back_in`, `back_out`, `back_in_out`, `circ_in`, `circ_out`, `expo_in`, `expo_out`, `sine_in`, `sine_out`, `steps(n)`, `custom_bezier(x1,y1,x2,y2)`.

---

## 3.1 Manim-like Construction Animations (v2)

- `GrowFromPoint(target, point_x, point_y)` — Object scales from 0 at a point to full size.
- `GrowFromEdge(target, edge="bottom")` — Bar/rect extends from an edge. **Perfect for bar chart animations!**
- `DrawBorderThenFill(target)` — First traces outline, then fills interior.
- `Create(target)` — Progressive construction (sweep reveal).
- `Uncreate(target)` — Reverse of Create.
- `ShowPassingFlash(target)` — Highlight with a sweeping flash.
- `GrowArrow(target)` — Line grows from start to end point.

---

## 3.2 Shape Morphing (v2)

- `MorphTo(source, target_shape)` — Interpolates position, color, size, and vertices.
- `ReplacementTransform(source, target_obj)` — Source fades out, target fades in.
- `TransformMatchingPoints(source, target)` — Morph polygon vertices by index.
- `VMorph(source, target_shape)` — **Vector path morphing** (v0.7.0). Smoothly interpolates SVG path data between two `VectorObject` instances with stroke, fill, and opacity interpolation.

---

## 3.3 Stagger Animation Group (v4)
Animate a list of objects with a wave/cascade effect.

```python
from pixelengine import Stagger, FadeIn, MoveBy

bars = [Rect(20, h, x=30+i*25, y=200-h, color=c) for i, (h, c) in enumerate(data)]
scene.add(*bars)
scene.play(Stagger([FadeIn(b) for b in bars], lag=0.1), duration=2.0)
```

---

## 3.4 Animation Modifiers (v4)

- `Delayed(anim, delay=0.3)` — Delay start by a fraction of total duration.
- `Reversed(anim)` — Play animation in reverse direction.
- `Looped(anim, count=3)` — Repeat animation N times. *(v0.7.1: correctly replays from original state each cycle)*

```python
from pixelengine import Delayed, Reversed, Looped, FadeIn, Rotate

scene.play(Delayed(FadeIn(obj), delay=0.3), duration=2.0)
scene.play(Reversed(GrowFromPoint(obj, 240, 135)), duration=1.0)
scene.play(Looped(Rotate(obj, 360), count=3), duration=3.0)
```

---

## 3.5 Spring Physics Animations (v4)

- `SpringTo(target, x, y, stiffness, damping)` — Spring to position with overshoot.
- `SpringScale(target, factor, stiffness, damping)` — Bouncy scale.

```python
from pixelengine import SpringTo, SpringScale
scene.play(SpringTo(obj, x=240, y=135, stiffness=120, damping=10), duration=2.0)
scene.play(SpringScale(obj, factor=1.5, stiffness=200, damping=8), duration=1.0)
```

---

## 3.6 Organic Animation System (v0.7.0)

Physics-inspired animations that feel natural and alive. Every animation supports a `MotionFeel` (preset: `"snappy"`, `"bouncy"`, `"heavy"`, `"floaty"`, `"elastic"`, `"mechanical"`, `"gentle"`, `"punchy"`).

### One-Shot Organic Animations
- `OrganicMoveTo(target, x, y, feel="bouncy")` — Spring-driven movement.
- `OrganicScale(target, factor, feel="elastic")` — Organic scaling.
- `OrganicFadeIn(target)` / `OrganicFadeOut(target)` — Noise-textured fades.
- `Breathe(target)`, `Sway(target)`, `Float(target)`, `Jitter(target)`, `Pulse(target)` — Expressive motions.
- `SquashAndStretch(target, intensity)`, `Wobble(target)`, `Drift(target)` — Deformation animations.
- `Anticipate(target)` — Pull back before action. `Settle(target)` — Come to rest. `RubberBand(target)` — Stretch and snap.

### Organic Modifiers (wrap any animation)
- `WithNoise(anim, amount)` — Add organic noise to movement.
- `WithFollow(anim)` — Follow-through overshoot.
- `WithAnticipation(anim)` — Wind-up before action.
- `WithSettle(anim, oscillations=3)` — Dampened settling after. *(v0.7.1: uses absolute positioning)*
- `WithSquashStretch(anim, intensity)` — Deformation during motion.

### Organic Groups
- `Wave(animations, delay)` — Ripple effect across objects.
- `Cascade(animations, feel, lag)` — Sequential entrance with momentum.
- `Swarm(animations, cx, cy, spread)` — Drift outward from a center.

### Continuous Motion Updaters
Attach to any object for persistent ambient motion:
```python
from pixelengine import alive, hover, orbit_idle, wind_sway

obj.add_updater(alive())         # Gentle breathing + micro-drift (v0.7.1: no positional drift)
obj.add_updater(hover(height=6)) # Smooth up/down oscillation
obj.add_updater(orbit_idle())    # Slow circular drift
obj.add_updater(wind_sway())     # Lateral push with gusts
```

---

## 3.7 Path Animation (v4)

- `BezierPath(start, control1, control2, end)` — Cubic Bézier curve.
- `QuadraticBezierPath(start, control, end)` — Simpler quadratic Bézier.
- `CircularPath(center_x, center_y, radius)` — Circular orbit.
- `LinearPath(points)` — Polyline through multiple points.
- `FollowPath(target, path, rotate_along=False, loops=1)` — Move along path.

```python
from pixelengine import BezierPath, FollowPath, CircularPath

path = BezierPath(start=(50, 200), control1=(150, 20),
                  control2=(300, 20), end=(400, 200))
scene.play(FollowPath(ball, path, rotate_along=True), duration=2.0)

orbit = CircularPath(center_x=240, center_y=135, radius=80)
scene.play(FollowPath(dot, orbit, loops=2), duration=4.0)
```

---

## 3.8 Keyframe Timeline (v4)

```python
from pixelengine import KeyframeTrack

track = KeyframeTrack(obj)
track.add(at=0.0, x=50, y=200, opacity=0.0)
track.add(at=0.3, x=240, y=135, opacity=1.0, easing="ease_out")
track.add(at=0.7, x=240, y=135, scale_x=1.5)
track.add(at=1.0, x=400, y=50, opacity=0.0, easing="ease_in")
scene.play(track.build(), duration=3.0)
```

---

## 3.9 Text Animation Toolkit (v4)

- `PerCharacter(text, effect, lag)` — Staggered per-character reveal (`"fade_in"`, `"drop_in"`, `"scale_in"`, `"slide_up"`).
- `PerWord(text, effect, lag)` — Staggered per-word reveal.
- `ScrambleReveal(text, charset, speed)` — Matrix-style random decode.
- `TypeWriterPro(text, cursor=True)` — Enhanced typewriter with blinking cursor.

```python
from pixelengine import PerCharacter, ScrambleReveal, TypeWriterPro

scene.play(PerCharacter(text, "fade_in", lag=0.05), duration=2.0)
scene.play(ScrambleReveal(text, charset="ABCXYZ0123"), duration=1.5)
scene.play(TypeWriterPro(text, cursor=True, cursor_blink_rate=2), duration=2.0)
```

---

## 3.10 Math Objects (v2)

- `NumberLine`, `BarChart`, `Axes`, `Graph`, `Dot`, `ValueTracker`.

```python
tracker = ValueTracker(0)
bar = Rect(10, 50, x=100, y=60, color="#FF004D")
bar.add_updater(lambda obj, dt: setattr(obj, 'height', max(1, int(50 * tracker.value / 100))))
scene.add(bar)
scene.play(tracker.animate_to(100), duration=2.0)
```

---

## 3.11 Rigid-Body Physics (v0.5.0)

PixelEngine natively supports 2D rigid-body physics via the `pymunk` backend. Objects can fall, bounce, and collide realistically.

*(v0.7.1: Friction is now frame-rate independent — consistent behavior at 24fps, 30fps, and 60fps.)*

```python
from pixelengine import PhysicsWorld, PhysicsBody

# Create a physics world with gravity pulling down
physics = PhysicsWorld(gravity_y=200, bounds=(0, 0, 480, 270))

ball = Circle(radius=10, x=240, y=50, color="#FF004D")
# Create a physics body wrapping the visual object
body = PhysicsBody(ball, mass=1.0, restitution=0.8)

scene.add(ball)
physics.add_body(body)

# The physics world automatically step()s during wait() or play()
scene.wait(3.0) 
```

---

## 4. Sprites

```python
player = Sprite.from_art([
    "..WW..", ".WWWW.", "WWWWWW", ".BRRB.", ".BRRB.", "..BB..",
], x=60, y=80)
```

---

## 5. Camera Control

- `self.camera.x/y/zoom`, `self.camera.follow(player)`, `self.camera.shake()`
- Animations: `CameraPan()`, `CameraZoom()`, `CameraCenterOn()`
- Focus: `self.camera.set_focus(x, y, radius)` for depth-of-field.

*(v0.7.1: Camera coordinate restoration is now exception-safe.)*

---

## 6. Backgrounds & TileMaps

`ParallaxLayer`, `GradientBackground`, `Starfield`, `TileMap`, `TileSet`.

---

## 7. Visual Effects (VFX)

- **Transitions**: `FadeTransition`, `WipeTransition`, `IrisTransition`, `DissolveTransition`.
- **v4 Transitions**: `PixelateTransition`, `SlideTransition`, `GlitchTransition`, `ShatterTransition`, `CrossDissolve`.
  *(v0.7.1: GlitchTransition and ShatterTransition ~100x faster via numpy vectorization.)*
- **Particles**: `ParticleEmitter.sparks()`, `.fire()`, `.snow()`, `.explosion()`, `.rain()`, `.bubbles()`.
- **Particle Bursts (v4)**: `ParticleBurst.form_shape()`, `.explode()`, `.disperse()`.
- **Trail**, **ScreenFlash**, **Grid**, **Outline**.

```python
from pixelengine import PixelateTransition, GlitchTransition, ParticleBurst

scene.play(GlitchTransition(scene, intensity=0.7), duration=0.5)
scene.play(ParticleBurst.explode(scene, x=240, y=135), duration=1.0)
```

---

## 8. Lighting & Shadows (v3)

`AmbientLight`, `PointLight`, `DirectionalLight`. Objects with `casts_shadow = True` project shadows.

---

## 9. Camera Post-Processing Effects (v3)

`Vignette`, `ChromaticAberration`, `Letterbox`, `FilmGrain`, `DepthOfField`.

---

## 10. Reactive Links (v4)

```python
from pixelengine import Link, ReactTo

shadow.add_updater(Link(player, delay=0.15, properties=["x", "y"]))
label.add_updater(ReactTo(target, lambda t: {"x": t.x, "y": t.y - 15}))
arrow.add_updater(Link.endpoints(dot_a, dot_b))
```

---

## 11. Procedural Audio & TTS

PixelEngine uses advanced procedural audio synthesis with ADSR envelopes and optional studio-grade effects via Spotify's **Pedalboard** library.

- **Dynamic Contextual SFX**: `SoundFX.dynamic("success", intensity=0.7)` — Generates a unique piano/instrument sound based on the situation (e.g. `success`, `error`, `reveal`, `transition`, `typing`, `impact`, `wonder`, `tension`).
- **Vintage-Premium Presets**: `SoundFX.coin()`, `.explosion()`, `.jump()` — Classic API names, but completely rebuilt using high-quality piano, bell, and mallet synthesis instead of raw 8-bit waveforms.
- **Custom Instrument Notes**: `SoundFX.piano_note("C4")`, `SoundFX.bell_note("E5")`, `SoundFX.mallet_note("G5")`.
- **Voiceovers**: `self.play_voiceover("text")` — Kokoro (default) or Chatterbox TTS.
- **Animation Sync**: `VoiceOver.generate()` returns `(sfx, duration)` to sync animations with speech.

*(v0.7.1: Fixed audio clipping when sounds overlap at negative time offsets.)*

```python
# Create a magical reveal sound with heavy reverb
self.play_sound(SoundFX.dynamic("reveal", intensity=0.8), at=2.0)

# Play a piano chord
self.play_sound(SoundFX.piano_note("C4"))
self.play_sound(SoundFX.piano_note("E4"))
self.play_sound(SoundFX.piano_note("G4"))
```

---

## 12-14. Textures, 3D, Simulations

See v2 docs. `PatternTexture`, `Cube3D`, `Pendulum`, `PhysicsWorld`, etc.

---

## 15-17. v0.6.0 Features

### 15. Auto-Captions (DynamicKaraoke)
Automatically split and animate words in sync with `VoiceOver`.
```python
captions = DynamicCaption("Hello world!", x=L.LOWER_THIRD.x, y=L.LOWER_THIRD.y)
scene.add(captions)
scene.play(captions.track(), duration=2.0)
```

### 16. Image Importer with Palette Quantization
Bring real world photos into the pixel art aesthetic.
```python
from pixelengine.color import PICO8
photo = ImageSprite("dog.jpg", x=L.MAIN_ZONE.x, y=L.MAIN_ZONE.y, width=150, palette=PICO8)
scene.add(photo)
```

### 17. Physics-Based Mind Maps
```python
graph = NetworkGraph(x=L.MAIN_ZONE.x, y=L.MAIN_ZONE.y)
graph.add_node("A", label="AI")
graph.add_node("B", label="ML")
graph.add_edge("A", "B")
scene.add(graph)
```

---

## 18. Outputs & File Organization

All output files are auto-organized into a flat `outputs/<script>/` directory.
Bare filenames (e.g. `render("demo.mp4")`) are redirected there too.
Only paths with explicit directories (e.g. `render("path/to/file.mp4")`) bypass this.
 
 ---
 
 ## 19. Vector Graphics (v0.6.0)
 
 High-performance, resolution-independent shapes based on `svgelements`. These paths are sampled at render-time, allowing for perfectly smooth curves and progressive drawing animations.
 
 - `VPath(path_data, ...)` — Arbitrary SVG path string or object.
 - `VLine(x1, y1, x2, y2, ...)` — Smooth parametric line.
 - `VCircle(radius, cx, cy, ...)` — Smooth parametric circle/arc.
 - `VRect(width, height, rx, x, y, ...)` — Smooth rectangle with rounded corners.
 - `VPolygon(points, ...)` — Closed polygon from vertex list.
 - `VArrow(x1, y1, x2, y2, ...)` — Line with a triangular arrowhead.
 - `Vector(dx, dy, origin_x, origin_y, ...)` — Mathematical arrow with optional label.
 - `SVGMobject(file_path, ...)` — Load and render external SVG files.
 
 **Animation Compatibility**:
 All `VectorObject` types support `Create()`, `Uncreate()`, `DrawBorderThenFill()`, and `VMorph()` for progressive reveals and morphing.
 
 ```python
 from pixelengine import VCircle, DrawBorderThenFill, VMorph
 
 circle = VCircle(radius=50, cx=240, cy=135, color="#00E436", fill_color="#006622")
 scene.add(circle)
 scene.play(DrawBorderThenFill(circle), duration=2.0)
 
 # Morph one vector shape into another
 square = VRect(80, 80, x=200, y=95, color="#FF004D")
 scene.play(VMorph(circle, square), duration=1.5)
 ```

---

## 20. v0.7.0 Features

### 20.1 MathTex — LaTeX Rendering
Render LaTeX equations as pixel-art objects.
```python
from pixelengine import MathTex

eq = MathTex(r"E = mc^2", x=135, y=240, color="#FFEC27")
scene.add(eq)
scene.play(Create(eq), duration=1.5)
```

### 20.2 Scene Composition (Compose)
Layer multiple sub-scenes or layouts together.
```python
from pixelengine import Compose

comp = Compose(scene, layout="split_horizontal")
comp.add_panel(left_scene)
comp.add_panel(right_scene)
```

### 20.3 Procedural Terrain
Generate landscape terrain backgrounds.
```python
from pixelengine import Terrain

ground = Terrain(width=270, height=100, x=0, y=380, seed=42, color="#1D2B53")
scene.add(ground)
```

### 20.4 Per-Pixel Shaders
Apply full-screen post-processing shader effects:
- `CRTScanlines` — Retro CRT monitor lines.
- `Ripple` — Water ripple distortion.
- `HeatShimmer` — Heat haze effect.
- `Pixelate` — Dynamic pixelation.
- `ColorGrade` — Color grading (tint, contrast, saturation).

```python
from pixelengine import CRTScanlines, ColorGrade

scene.add_camera_fx(CRTScanlines(gap=2, opacity=0.3))
scene.add_camera_fx(ColorGrade(tint="#FFD4A0", contrast=1.1))
```

### 20.5 Pixel Art Generation (v0.7.0)
Procedurally generate pixel art characters, backgrounds, and effects — no external image files needed.

```python
from pixelengine import PixelArtist

# Generate a character sprite
character = PixelArtist.character(
    style="knight", palette="pico8",
    base_size=16, x=135, y=240
)
scene.add(character)

# Generate a background
bg = PixelArtist.background(
    style="forest", palette="gameboy",
    width=270, height=480
)
scene.add(bg)
```

Available palettes: `"pico8"`, `"gameboy"`, `"nes"`, `"pastel"`, `"neon"`, `"earth"`, `"ocean"`.

---

## 21. v0.7.1 Bug Fixes

Key stability improvements in this release:

| Area | Fix |
|------|-----|
| **Physics** | Friction is now frame-rate independent (`friction**dt`). |
| **Animation** | `Looped` correctly replays from original state each cycle. |
| **Animation** | `Sequence` cleans up internal state for reuse. |
| **Effects** | GlitchTransition & ShatterTransition ~100x faster (numpy). |
| **Scene** | Camera coordinate restoration is exception-safe. |
| **Sound** | Fixed audio clipping at negative time offsets. |
| **Organic** | `alive()` no longer drifts; `WithSettle` uses absolute positioning. |
| **Transform** | `VMorph` safely cleans up on interrupted animations. |

---
<br>

# 🤖 Special Guide for AI Agents

**If an AI Agent is tasked with using `PixelEngine` to code a video, STRICTLY REMEMBER:**

1. **Resolution Scale**: Default canvas is **480×270** (landscape) or **270×480** (portrait). Do NOT make shapes at output resolution.
2. **Audio/Sync**: Only use `self.wait(2.0)`. The renderer executes synchronously offline at `24 FPS`.
3. **Typography**: `5x7` uppercase-only font.
4. **Imports**: Import from `pixelengine` root:
   ```python
   from pixelengine import (
       Scene, PixelConfig, CameraZoom, Rect, Circle, Sprite,
       MoveTo, FadeIn, Sequence, ease_out, PixelText, TypeWriter,
       SoundFX, Grid, ParticleEmitter, TileMap, TileSet,
       # v2 Manim-like
       GrowFromPoint, GrowFromEdge, DrawBorderThenFill, Create,
       MorphTo, ValueTracker, NumberLine, BarChart, Axes, Graph,
       # v2 Textures
       PatternTexture, DitherTexture, GradientTexture,
       # v2 3D
       Cube3D, Sphere3D, Vec3,
       # v2 Simulations
       Pendulum, Spring, Rope, PhysicsWorld, PhysicsBody,
       # v3 Lighting
       AmbientLight, PointLight, DirectionalLight,
       # v3 Camera Effects
       Vignette, ChromaticAberration, Letterbox, FilmGrain, DepthOfField,
       # v4 Animation
       Stagger, Delayed, Reversed, Looped,
       SpringTo, SpringScale,
       back_in, back_out, circ_out, expo_out, sine_out, steps, custom_bezier,
       # v4 Path Animation
       BezierPath, CircularPath, LinearPath, FollowPath,
       # v4 Keyframes
       KeyframeTrack,
       # v4 Text Animation
       PerCharacter, PerWord, ScrambleReveal, TypeWriterPro,
       # v4 Transitions
       PixelateTransition, GlitchTransition, ShatterTransition, CrossDissolve,
       # v4 Particle Bursts
       ParticleBurst,
       # v4 Reactive Links
       Link, ReactTo,
       # v0.6.0 Vector Graphics
       VPath, VLine, VCircle, VRect, VPolygon, VArrow, Vector, SVGMobject,
       VMorph,
       # v0.7.0 New Features
       MathTex, Compose, Terrain,
       CRTScanlines, Ripple, HeatShimmer, Pixelate, ColorGrade,
       PixelArtist,
       # v0.7.0 Organic Animation System
       OrganicMoveTo, OrganicScale, OrganicFadeIn, OrganicFadeOut,
       Breathe, Sway, Float, Jitter, Pulse,
       SquashAndStretch, Wobble, Drift, Anticipate, Settle, RubberBand,
       WithNoise, WithFollow, WithAnticipation, WithSettle, WithSquashStretch,
       Wave, Cascade, Swarm,
       alive, hover, orbit_idle, wind_sway,
   )
   ```
5. **No File dependencies**: Use procedural generation only. Use `PixelArtist` for pixel art assets.
6. **VoiceOver** is blocking. For simultaneous animation + speech, use `VoiceOver.generate()`.
7. **Stagger (v4)**: Use `Stagger([anim1, anim2, ...], lag=0.1)` for wave/cascade effects.
8. **Springs (v4)**: Use `SpringTo`/`SpringScale` for organic bouncy motion.
9. **Paths (v4)**: Use `FollowPath(obj, BezierPath(...))` for curved motion. `rotate_along=True` auto-rotates.
10. **Keyframes (v4)**: Use `KeyframeTrack(obj).add(at=0.0, ...).add(at=1.0, ...).build()` for timeline animations.
11. **Text Animations (v4)**: `PerCharacter(text, "fade_in", lag=0.05)` for staggered text. `ScrambleReveal` for Matrix-style.
12. **Reactive Links (v4)**: `obj.add_updater(Link(source))` for following. `ReactTo(source, fn)` for custom reactions.
13. **Performance (v0.5.0)**: Don't hesitate to use dense particle effects, dynamic lighting, and real rigid-body `PhysicsWorld` + `PhysicsBody` dynamics. PyAV and Pymunk handle it effortlessly.
14. **Layout (v0.5.0)**: ALWAYS use `Layout.portrait()` or `Layout.landscape()` for positioning. Access named zones via `L.TITLE_ZONE`, `L.MAIN_ZONE`, `L.LOWER_THIRD`, etc. Never hardcode coordinates.
   ```python
   from pixelengine.layout import Layout
   L = Layout.portrait()
   title = PixelText("HELLO", x=L.TITLE_ZONE.x, y=L.TITLE_ZONE.y, align="center")
   ```
15. **Organic Animations (v0.7.0)**: Prefer organic animations over basic ones for natural feel:
   - Use `OrganicMoveTo` instead of `MoveTo` for spring-driven movement.
   - Use `WithSettle(anim)` to add dampened settling after any animation.
   - Use `Wave([...])` or `Cascade([...])` for group animations instead of `Stagger`.
   - Attach `alive()`, `hover()`, or `wind_sway()` updaters to ambient objects.
16. **Pixel Art (v0.7.0)**: Use `PixelArtist.character()` and `PixelArtist.background()` to generate visual assets procedurally.
17. **Shaders (v0.7.0)**: Use `CRTScanlines`, `ColorGrade`, etc. as camera FX for cinematic quality.
18. **MathTex (v0.7.0)**: Use `MathTex(r"E = mc^2")` for LaTeX equations in educational videos.
