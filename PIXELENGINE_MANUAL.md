# PixelEngine v0.5.0

**PixelEngine** is a specialized, code-first Python framework for generating educational, animated pixel art videos. It renders at a configurable canvas resolution (default **480×270**) and upscales with nearest-neighbor to **1920×1080** (Full HD) for crisp pixel edges.

All rendering is done via **Pillow** images encoded straight into **ffmpeg** with programmatic logic and math. No external graphic files or audio files are required by default.

---

## Technical Stack & Requirements

1. **Python**: 3.8+ (Virtual Environment **highly** recommended)
2. **Core Dependencies**: `Pillow`, `numpy`
3. **Optional High-Performance Packages**: `av` (PyAV for 3x faster video encoding), `pymunk` (for rigid-body physics), `pydub` (for professional audio mixing). Install all with `pip install .[perf]`.
4. **Audio Dependencies**: `soundfile`, `kokoro-onnx` (default TTS), `chatterbox-tts`, `torch`, `torchaudio` (optional high-quality TTS)
5. **System Dep**: `ffmpeg` (must be accessible in PATH to mux final MP4s).

---

## 1. Core Architecture (The `Scene`)

Everything happens inside a `Scene`. You override the `construct()` method to place objects (`self.add()`), advance time (`self.wait()`), and interpolate animations (`self.play()`).

```python
from pixelengine import Scene, PixelConfig, Rect, PixelText, TypeWriter

class MyAnimation(Scene):
    def construct(self):
        # 1. Place static object
        bg = Rect(width=480, height=270, color="#1D2B53")
        self.add(bg)

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
- `Looped(anim, count=3)` — Repeat animation N times.

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

## 3.6 Path Animation (v4)

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

## 3.7 Keyframe Timeline (v4)

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

## 3.8 Text Animation Toolkit (v4)

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

## 3.9 Math Objects (v2)

- `NumberLine`, `BarChart`, `Axes`, `Graph`, `Dot`, `ValueTracker`.

```python
tracker = ValueTracker(0)
bar = Rect(10, 50, x=100, y=60, color="#FF004D")
bar.add_updater(lambda obj, dt: setattr(obj, 'height', max(1, int(50 * tracker.value / 100))))
scene.add(bar)
scene.play(tracker.animate_to(100), duration=2.0)
```

---

## 3.10 Rigid-Body Physics (v0.5.0)

PixelEngine natively supports 2D rigid-body physics via the `pymunk` backend. Objects can fall, bounce, and collide realistically.

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

---

## 6. Backgrounds & TileMaps

`ParallaxLayer`, `GradientBackground`, `Starfield`, `TileMap`, `TileSet`.

---

## 7. Visual Effects (VFX)

- **Transitions**: `FadeTransition`, `WipeTransition`, `IrisTransition`, `DissolveTransition`.
- **v4 Transitions**: `PixelateTransition`, `SlideTransition`, `GlitchTransition`, `ShatterTransition`, `CrossDissolve`.
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

- `SoundFX.coin()`, `.explosion()`, etc. — procedural synthesis
- `self.play_voiceover("text")` — Kokoro (default) or Chatterbox TTS
- Animation during speech: `VoiceOver.generate()` returns `(sfx, duration)`

---

## 12-14. Textures, 3D, Simulations

See v2 docs. `PatternTexture`, `Cube3D`, `Pendulum`, `PhysicsWorld`, etc.

---

## 15. Outputs & File Organization

`scene.render()` auto-organizes to `outputs/<script>/`.

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
   )
   ```
5. **No File dependencies**: Use procedural generation only.
6. **VoiceOver** is blocking. For simultaneous animation + speech, use `VoiceOver.generate()`.
7. **Stagger (v4)**: Use `Stagger([anim1, anim2, ...], lag=0.1)` for wave/cascade effects.
8. **Springs (v4)**: Use `SpringTo`/`SpringScale` for organic bouncy motion.
9. **Paths (v4)**: Use `FollowPath(obj, BezierPath(...))` for curved motion. `rotate_along=True` auto-rotates.
10. **Keyframes (v4)**: Use `KeyframeTrack(obj).add(at=0.0, ...).add(at=1.0, ...).build()` for timeline animations.
11. **Text Animations (v4)**: `PerCharacter(text, "fade_in", lag=0.05)` for staggered text. `ScrambleReveal` for Matrix-style.
12. **Reactive Links (v4)**: `obj.add_updater(Link(source))` for following. `ReactTo(source, fn)` for custom reactions.
13. **Performance (v0.5.0)**: Don't hesitate to use dense particle effects, dynamic lighting, and real rigid-body `PhysicsWorld` + `PhysicsBody` dynamics. PyAV and Pymunk handle it effortlessly.
