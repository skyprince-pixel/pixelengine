# PixelEngine

**PixelEngine** is a specialized, code-first Python framework for generating educational, animated, 8-bit style pixel art videos. It is inspired by tools like Manim but acts exclusively in low-resolution coordinate space (e.g., 256×144), using purely nearest-neighbor upscale routing to keep a crisp, retro aesthetic.

All rendering is done via **Pillow** images encoded straight into **ffmpeg** with programmatic logic and math. No external graphic files or audio files are required by default.

---

## Technical Stack & Requirements

1. **Python**: 3.8+ (Virtual Environment **highly** recommended)
2. **Core Dependencies**: `Pillow`, `numpy`
3. **Audio Dependencies**: `soundfile`, `chatterbox-tts`, `torch`, `torchaudio` (for Voiceover TTS)
4. **System Dep**: `ffmpeg` (must be accessible in PATH to mux final MP4s).

---

## 1. Core Architecture (The `Scene`)

Everything happens inside a `Scene`. You override the `construct()` method to place objects (`self.add()`), advance time (`self.wait()`), and interpolate animations (`self.play()`).

```python
from pixelengine import Scene, PixelConfig, Rect, PixelText, TypeWriter

class MyAnimation(Scene):
    def construct(self):
        # 1. Place static object
        bg = Rect(width=256, height=144, color="#1D2B53")
        self.add(bg)

        # 2. Add some text
        text = PixelText("HELLO GALAXY", x=128, y=72, align="center")
        self.add(text)

        # 3. Animate TypeWriter taking exactly 2.0 seconds
        self.play(TypeWriter(text), duration=2.0)
        self.wait(1.0)

# Render
if __name__ == "__main__":
    MyAnimation(PixelConfig.landscape()).render("output.mp4")
```

- **Config**: The default canvas is precisely **256×144** upscale rendering 4x to 1024x576 at `12 FPS`. Every coordinate and element should be treated logically in `256x144` screen-space.
- **Coordinates**: `(0,0)` is top-left.
- **Z-Index**: Control layering with `.z_index`. Lower draws behind higher.

---

## 2. Shapes & Primitives
Primitives cover standard geometry.
- `Rect(width, height, x, y, color, opacity)`
- `Circle(radius, x, y, color)`
- `Line(x_start, y_start, x_end, y_end, color)`
- `Triangle(x1, y1, x2, y2, x3, y3, color)`

*Note*: Colors can be passed as standard `"HEX"` strings. `pixelengine.color` has built-in palettes (`PICO8`, `GAMEBOY`, `NES`).

---

## 3. The Animation System
Use `self.play(*animations, duration=X)` to run interpolation frames.
- **Transforms**: `MoveTo`, `MoveBy`, `Scale`, `Rotate`, `ColorShift`.
- **Visibility**: `FadeIn`, `FadeOut`, `Blink`.
- **Text**: `TypeWriter` (Reveals text character by character).
- **Control Flow**: `AnimationGroup` (fires concurrently), `Sequence` (fires linearly).

**Easing Functions**: Pass `easing=...` into an animation.
Available easings: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `bounce`, `elastic`.

---

## 3.1 Manim-like Construction Animations (v2)
Build shapes gradually — inspired by Manim's Create/Transform pattern.

- `GrowFromPoint(target, point_x, point_y)` — Object scales from 0 at a point to full size.
- `GrowFromEdge(target, edge="bottom")` — Bar/rect extends from an edge (bottom, top, left, right). **Perfect for bar chart animations!**
- `DrawBorderThenFill(target)` — First traces outline, then fills interior.
- `Create(target)` — Progressive construction (sweep reveal).
- `Uncreate(target)` — Reverse of Create.
- `ShowPassingFlash(target)` — Highlight with a sweeping flash.
- `GrowArrow(target)` — Line grows from start to end point.

```python
bar = Rect(20, 60, x=50, y=40, color="#00E436")
scene.add(bar)
scene.play(GrowFromEdge(bar, edge="bottom"), duration=1.0)
```

---

## 3.2 Shape Morphing (v2)
Transform one shape into another smoothly.

- `MorphTo(source, target_shape)` — Interpolates position, color, size, and vertices.
- `ReplacementTransform(source, target_obj)` — Source fades out, target fades in.
- `TransformMatchingPoints(source, target)` — Morph polygon vertices by index.

```python
square = Rect(30, 30, x=50, y=50, color="#FF004D")
scene.play(MorphTo(square, target_shape=Circle(15, x=150, y=50, color="#29ADFF")),
           duration=1.5)
```

---

## 3.3 Math Objects (v2)
Educational primitives for data visualization.

- `NumberLine(min_val, max_val, step, x, y, width)` — Number line with ticks and labels.
- `BarChart(data, labels, colors, x, y, width, height)` — Animated bar chart.
- `Axes(x_range, y_range, x, y, width, height)` — 2D coordinate axes.
- `Graph(func, axes, color)` — Plot function with `graph.animate_draw()`.
- `Dot(x, y, radius, color)` — Point marker.
- `ValueTracker(value)` — Track animatable values for reactive animations.

```python
chart = BarChart(data=[30, 70, 50, 90], colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27"],
                 x=30, y=20, width=200, height=100)
scene.add(chart)
scene.play(chart.animate_build(), duration=2.0)
```

**ValueTracker + Updaters**:
```python
tracker = ValueTracker(0)
bar = Rect(10, 50, x=100, y=60, color="#FF004D")
bar.add_updater(lambda obj, dt: setattr(obj, 'height', max(1, int(50 * tracker.value / 100))))
scene.add(bar)
scene.play(tracker.animate_to(100), duration=2.0)
```

---

## 4. Sprites
The `Sprite` system runs off an ASCII matrix array, letting you define 8-bit characters dynamically without `.png` files!

```python
player = Sprite.from_art([
    "..WW..",  # White
    ".WWWW.",
    "WWWWWW",
    ".BRRB.",  # Blue, Red
    ".BRRB.",
    "..BB..",
], x=60, y=80)
```
- **Flipping**: `player.flip_h = True` to face left.
- **Animations**: `sprite.add_frames("walk", [frame1, frame2], fps=4)`
- **Anchor point**: Specify `.anchor_x` / `.anchor_y` for transform offsets.

---

## 5. Camera Control
The `self.camera` moves the 256x144 viewport mapping over a virtual world.
- **Transform**: `self.camera.x` / `self.camera.y` / `self.camera.zoom`.
- **Following**: `self.camera.follow(player, deadzone=10)`
- **Shake**: `self.camera.shake(intensity=5, duration=0.4)`
- **Animation**: `CameraPan()`, `CameraZoom()`, `CameraCenterOn()`.

---

## 6. Backgrounds & TileMaps
**Parallax Scrolling**:
`ParallaxLayer(art_rows, speed_factor=0.5)` auto-scrolls background images infinitely when the camera moves!
Available backdrops: `GradientBackground`, `Starfield` (auto-twinkles).

**TileMap**:
Render dynamic grid block levels.
```python
ts = TileSet(tile_size=8)
ts.add_color_tile("#", "#83769C")  # Wall block
map_data = [
    "################",
    "#..............#",
]
level = TileMap(ts, map_data)
level.get_tile_at(col=5, row=1) # query tile logic
```

---

## 7. Visual Effects (VFX)
All visual effects are procedurally coded! Add them to `self.add()`.
- **Transitions**: `FadeTransition(mode="out")`, `WipeTransition()`, `IrisTransition()`, `DissolveTransition()`.
- **Particles**: `sparks = ParticleEmitter.sparks(x=128, y=72)`. (Includes `.snow()`, `.fire()`, `.explosion()`, `.rain()`, `.bubbles()`).
- **Trail**: `Trail(target=player, length=8)` draws "motion blur" steps!
- **Grid Overlay**: `Grid(cell_size=16)` for explicit math tutorials.

---

## 8. Procedural Audio & TTS!
Sounds require NO actual MP3/WAV uploads. They are procedurally sine/square/triangle generated in numpy, natively remuxed in ffmpeg at compile time!

### Auto Sounds
`Scene` has auto-sounds enabled natively (`self.auto_sound = True`).

### Manual Event Cues
```python
from pixelengine import SoundFX
self.play_sound(SoundFX.coin())
self.play_sound(SoundFX.explosion())
```

### VoiceOver (Chatterbox Turbo TTS)
```python
# Default voice (no reference clip needed)
self.play_voiceover(
    "Hello! I'm your AI teacher. Here is math trick number one."
)

# With voice cloning (provide a ~10s reference .wav)
self.play_voiceover(
    "Hello! [chuckle] Let me show you something amazing.",
    voice="path/to/reference_clip.wav"
)
```

---

## 9. Texture System (v2)
Fill shapes with pixel-art-friendly patterns instead of flat colors.

**Built-in patterns**: `checkerboard`, `stripes_h`, `stripes_v`, `diagonal`, `dots`, `crosshatch`, `brick`, `herringbone`.

```python
from pixelengine import PatternTexture, DitherTexture, GradientTexture

rect = Rect(60, 40, x=50, y=30, color="#FFFFFF")
rect.fill_texture = PatternTexture("checkerboard", cell_size=4,
                                    color1="#FF004D", color2="#1D2B53")
scene.add(rect)
```

- `DitherTexture(color1, color2, density)` — Bayer-matrix ordered dithering.
- `NoiseTexture(colors, scale)` — Hash-based noise mapped to palette.
- `GradientTexture(color1, color2, direction)` — Linear gradient fill.
- `AnimatedTexture(textures, fps)` — Cycles between textures.
- `ScrollingTexture(texture, dx, dy)` — Texture scrolls over time.

---

## 10. Pseudo-3D Rendering (v2)
Wireframe 3D shapes projected onto the 2D pixel canvas. Perfect for geometry education.

```python
from pixelengine import Cube3D, Vec3
from pixelengine.objects3d import Rotate3D

cube = Cube3D(size=2.0, color="#29ADFF")
cube.position = Vec3(0, 0, 5)
scene.add(cube)
scene.play(Rotate3D(cube, axis="y", degrees=360), duration=3.0)
```

**3D Primitives**: `Cube3D`, `Sphere3D`, `Pyramid3D`, `Cylinder3D`, `Mesh3D`, `Axes3D`.
**Projections**: `perspective` (default) or `isometric`.
**Camera**: `Camera3D(fov, distance, elevation, azimuth)`, `IsoCamera(scale)`.
**Animations**: `Rotate3D(obj, axis, degrees)`, `Orbit3D(camera, degrees)`, `Zoom3D(camera, target_distance)`.

---

## 11. Simulation Engine (v2)
Physics simulations rendered as video — gravity, collisions, pendulums, springs, orbits.

### Self-contained Simulations
```python
from pixelengine import Pendulum, Spring, Rope, OrbitalSystem, FluidParticles

pend = Pendulum(pivot_x=128, pivot_y=30, length=60, angle=45, color="#FF004D")
scene.add(pend)
scene.wait(5)  # Physics auto-advances during render
```

### Physics World (Custom)
```python
from pixelengine import PhysicsWorld, PhysicsBody, Circle

physics = PhysicsWorld(gravity_y=100)
physics.bounds = (0, 0, 256, 144)
scene.physics = physics  # Auto-stepped each frame

ball = Circle(5, x=128, y=20, color="#FF004D")
body = PhysicsBody(ball, mass=1.0, restitution=0.8)
physics.add_body(body)
scene.add(ball)
scene.wait(5)
```

**Simulations**: `Pendulum`, `Spring`, `OrbitalSystem` (N-body gravity), `Rope` (Verlet chain), `FluidParticles` (SPH-like).
**Physics**: `PhysicsBody`, `PhysicsWorld`, `StaticBody`, `Bounds`, `CollisionCallback`.

---

## 12. Outputs & File Organization

By default, PixelEngine now automatically organizes generated scripts, audio, and videos into an `outputs/` folder. It uses the name of the python script you run as the project name.

For example, if you run a script named `my_video.py`, PixelEngine will generate:
```
outputs/
└── my_video/
    ├── 1024x576_12fps/
    │   └── MyScene.mp4     # The final rendered video
    ├── audio/
    │   └── MyScene.wav     # The isolated audio track
    └── scripts/
        └── my_video.py     # A backup copy of the script state for reference
```

To use this feature, simply call `scene.render()` with no arguments.

```python
if __name__ == "__main__":
    scene = MyScene(PixelConfig.landscape())
    scene.render()  # Auto-organizes to outputs/my_video/
```
*(If you pass an explicit path like `scene.render("video.mp4")`, it will bypass organization and output directly to that path).*

---
<br>

# 🤖 Special Guide for AI Agents
**If an AI Agent is tasked with using `PixelEngine` to code a video, STRICTLY REMEMBER:**

1. **Resolution Scale**: Keep sizes strictly micro-dimensioned (e.g., maximum `x=256` maximum `y=144`). Do not tell `Rect` to draw at width `1920`. It is 4x scaled via `.config` at compilation.
2. **Audio Volume Bug / Sync Rules**: Do not mess with `sleep` or real-world `time.time()`. Only use `self.wait(2.0)`. The renderer executes synchronously offline at `12 FPS`.
3. **Typography**: The font maps to a `5x7` character limitation array inside `text.py`. It is purely uppercase logic.
4. **Imports**: Import ONLY from the engine facade `pixelengine` root:
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
       # v2 3D (also from pixelengine.objects3d for Rotate3D)
       Cube3D, Sphere3D, Vec3,
       # v2 Simulations
       Pendulum, Spring, Rope, PhysicsWorld, PhysicsBody,
   )
   ```
5. **No File dependencies**: Do **not** try to load `.png`, `.wav`, or `.json`. Use procedural generation.
6. **VoiceOver** is blocking. Uses Chatterbox Turbo TTS (auto-detects MPS/CPU). For simultaneous animation + speech, generate manually:
   ```python
   from pixelengine.voiceover import VoiceOver
   speech_sfx, speech_dur = VoiceOver.generate("Look at me move!")
   self.play(MoveTo(character, x=200), duration=speech_dur, sound=speech_sfx)
   ```
   Supports paralinguistic tags: `[laugh]`, `[chuckle]`, `[cough]` for natural realism.
7. **Textures**: Set `shape.fill_texture = PatternTexture(...)` before adding to scene.
8. **3D Objects**: Position in 3D via `obj.position = Vec3(x, y, z)` and set `obj.rotation_x/y/z` for rotation. Use `Rotate3D` animation for smooth rotation.
9. **Simulations**: Self-contained objects like `Pendulum` and `Rope` auto-advance physics during `self.wait()`. For custom physics, create a `PhysicsWorld` and assign to `scene.physics`.
