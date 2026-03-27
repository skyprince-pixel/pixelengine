# PixelEngine v0.3.0

**PixelEngine** is a specialized, code-first Python framework for generating educational, animated pixel art videos. It renders at a configurable canvas resolution (default **480×270**) and upscales with nearest-neighbor to **1920×1080** (Full HD) for crisp pixel edges.

All rendering is done via **Pillow** images encoded straight into **ffmpeg** with programmatic logic and math. No external graphic files or audio files are required by default.

---

## Technical Stack & Requirements

1. **Python**: 3.8+ (Virtual Environment **highly** recommended)
2. **Core Dependencies**: `Pillow`, `numpy`
3. **Audio Dependencies**: `soundfile`, `kokoro-onnx` (default TTS), `chatterbox-tts`, `torch`, `torchaudio` (optional high-quality TTS)
4. **System Dep**: `ffmpeg` (must be accessible in PATH to mux final MP4s).

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
The `Sprite` system runs off an ASCII matrix array, letting you define pixel characters dynamically without `.png` files!

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
The `self.camera` moves the viewport over a virtual world.
- **Transform**: `self.camera.x` / `self.camera.y` / `self.camera.zoom`.
- **Following**: `self.camera.follow(player, deadzone=10)`
- **Shake**: `self.camera.shake(intensity=5, duration=0.4)`
- **Animation**: `CameraPan()`, `CameraZoom()`, `CameraCenterOn()`.

### Camera Focus (v3)
Set a focus point for depth-of-field effect:
```python
self.camera.set_focus(x=240, y=135, radius=30)  # Focus on center
self.camera.clear_focus()                         # Remove focus
```

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

## 8. Lighting & Shadows (v3)

Dynamic lighting with shadow casting.

### Light Types
```python
from pixelengine import AmbientLight, PointLight, DirectionalLight

# Global base illumination
ambient = AmbientLight(intensity=0.2, color="#FFFFFF")
scene.add_light(ambient)

# Radial light source (inherits PObject — can be animated with MoveTo!)
torch = PointLight(x=240, y=135, radius=80, color="#FFA300",
                   intensity=1.2, falloff="quadratic")
torch.visible = True  # Show light source marker
scene.add_light(torch)
scene.play(MoveTo(torch, 100, 50), duration=2.0)  # Animate the light!

# Parallel rays (sun/moon simulation)
sun = DirectionalLight(angle=225, intensity=0.6, color="#FFEC27")
scene.add_light(sun)
```

### Shadow Casting
Objects with `casts_shadow = True` project shadow polygons away from lights:
```python
pillar = Rect(15, 50, x=80, y=60, color="#5F574F")
pillar.casts_shadow = True
pillar.shadow_opacity = 0.6  # How dark the shadows are
scene.add(pillar)
```

### How It Works
1. **Shadow pass**: Compute shadow polygons from each object's silhouette
2. **Light map pass**: Accumulate light contributions (ambient + point + directional)
3. **Composite pass**: Multiply-blend the light map over the canvas

---

## 9. Camera Post-Processing Effects (v3)

Apply cinematic post-processing effects to the camera output.

```python
from pixelengine import Vignette, ChromaticAberration, Letterbox, FilmGrain, DepthOfField

# Vignette — radial edge darkening
scene.add_camera_fx(Vignette(intensity=0.5, radius=0.6))

# Chromatic Aberration — RGB channel offset
scene.add_camera_fx(ChromaticAberration(offset=2))

# Letterbox — cinematic black bars
scene.add_camera_fx(Letterbox(bar_height=20))

# Film Grain — random noise overlay
scene.add_camera_fx(FilmGrain(intensity=0.08))

# Depth of Field — auto-syncs with camera.set_focus()
scene.camera.set_focus(x=240, y=135, radius=30)

# Remove effects
scene.remove_camera_fx(vignette)
```

Effects are applied in order after upscaling, creating a professional post-processing pipeline.

---

## 10. Procedural Audio & TTS

### Audio Quality
- **Sample Rate**: 48kHz (CD-quality)
- **Bit Depth**: 24-bit PCM
- **AAC Bitrate**: 256kbps

Sounds require NO actual MP3/WAV uploads. They are procedurally sine/square/triangle generated in numpy, natively remuxed in ffmpeg at compile time!

### Auto Sounds
`Scene` has auto-sounds enabled natively (`self.auto_sound = True`).

### Manual Event Cues
```python
from pixelengine import SoundFX
self.play_sound(SoundFX.coin())
self.play_sound(SoundFX.explosion())
```

### VoiceOver (Kokoro ONNX — default)
```python
# Default voice (Kokoro — fast, lightweight)
self.play_voiceover("Hello! I'm your AI teacher.")

# Specify Kokoro voice
self.play_voiceover("With a specific voice.", voice="af_bella")
```

### VoiceOver (Chatterbox Turbo — high-quality)
```python
# Voice cloning with reference audio
self.play_voiceover(
    "Hello! [chuckle] Let me show you something amazing.",
    voice="path/to/reference_clip.wav",
    engine="chatterbox"
)
```

### Batch Preload (Recommended)
```python
from pixelengine import VoiceOver
VoiceOver.preload(["Line one.", "Line two.", "Line three."])
```

### Animation During Speech
```python
from pixelengine.voiceover import VoiceOver
sfx, dur = VoiceOver.generate("Look at me move!", engine="kokoro")
self.play(MoveTo(character, x=200), duration=dur, sound=sfx)
```

---

## 11. Texture System (v2)
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

## 12. Pseudo-3D Rendering (v2)
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

## 13. Simulation Engine (v2)
Physics simulations rendered as video — gravity, collisions, pendulums, springs, orbits.

### Self-contained Simulations
```python
from pixelengine import Pendulum, Spring, Rope, OrbitalSystem, FluidParticles

pend = Pendulum(pivot_x=240, pivot_y=50, length=80, angle=45, color="#FF004D")
scene.add(pend)
scene.wait(5)  # Physics auto-advances during render
```

### Physics World (Custom)
```python
from pixelengine import PhysicsWorld, PhysicsBody, Circle

physics = PhysicsWorld(gravity_y=100)
physics.bounds = (0, 0, 480, 270)
scene.physics = physics  # Auto-stepped each frame

ball = Circle(5, x=240, y=20, color="#FF004D")
body = PhysicsBody(ball, mass=1.0, restitution=0.8)
physics.add_body(body)
scene.add(ball)
scene.wait(5)
```

**Simulations**: `Pendulum`, `Spring`, `OrbitalSystem` (N-body gravity), `Rope` (Verlet chain), `FluidParticles` (SPH-like).
**Physics**: `PhysicsBody`, `PhysicsWorld`, `StaticBody`, `Bounds`, `CollisionCallback`.

---

## 14. Outputs & File Organization

By default, PixelEngine now automatically organizes generated scripts, audio, and videos into an `outputs/` folder.

```
outputs/
└── my_video/
    ├── 1920x1080_24fps/
    │   └── MyScene.mp4     # The final rendered video
    ├── audio/
    │   └── MyScene.wav     # The isolated audio track
    └── scripts/
        └── my_video.py     # A backup copy of the script
```

To use this feature, simply call `scene.render()` with no arguments.

```python
if __name__ == "__main__":
    scene = MyScene(PixelConfig.landscape())
    scene.render()  # Auto-organizes to outputs/my_video/
```

---
<br>

# 🤖 Special Guide for AI Agents
**If an AI Agent is tasked with using `PixelEngine` to code a video, STRICTLY REMEMBER:**

1. **Resolution Scale**: Default canvas is **480×270** (landscape) or **270×480** (portrait). For retro style use `PixelConfig.retro()` (256×144). Do NOT make shapes at output resolution (1920×1080).
2. **Audio Volume Bug / Sync Rules**: Do not mess with `sleep` or real-world `time.time()`. Only use `self.wait(2.0)`. The renderer executes synchronously offline at `24 FPS`.
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
       # v3 Lighting
       AmbientLight, PointLight, DirectionalLight,
       # v3 Camera Effects
       Vignette, ChromaticAberration, Letterbox, FilmGrain, DepthOfField,
   )
   ```
5. **No File dependencies**: Do **not** try to load `.png`, `.wav`, or `.json`. Use procedural generation.
6. **VoiceOver** is blocking. Default engine is **Kokoro ONNX** (fast). For simultaneous animation + speech, generate manually:
   ```python
   from pixelengine.voiceover import VoiceOver
   speech_sfx, speech_dur = VoiceOver.generate("Look at me move!")
   self.play(MoveTo(character, x=200), duration=speech_dur, sound=speech_sfx)
   ```
   Supports paralinguistic tags: `[laugh]`, `[chuckle]`, `[cough]` for natural realism.
7. **Textures**: Set `shape.fill_texture = PatternTexture(...)` before adding to scene.
8. **3D Objects**: Position in 3D via `obj.position = Vec3(x, y, z)` and set `obj.rotation_x/y/z` for rotation. Use `Rotate3D` animation for smooth rotation.
9. **Simulations**: Self-contained objects like `Pendulum` and `Rope` auto-advance physics during `self.wait()`. For custom physics, create a `PhysicsWorld` and assign to `scene.physics`.
10. **Lighting (v3)**: Use `scene.add_light()` / `scene.remove_light()`. PointLights are PObjects and can be animated with `MoveTo`. Set `obj.casts_shadow = True` for shadow casting.
11. **Camera Effects (v3)**: Use `scene.add_camera_fx()` / `scene.remove_camera_fx()`. Effects are applied post-upscale. Use `self.camera.set_focus()` for automatic depth-of-field.
12. **Quality Control (v3)**: Set `obj.render_quality` per object. Values < 1.0 = chunkier, > 1.0 = smoother.
