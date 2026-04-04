# API Reference

Complete reference for all PixelEngine classes and functions. Import everything from the root:

```python
from pixelengine import *
```

---

## Configuration

### PixelConfig

```python
PixelConfig(
    canvas_width=480,       # Rendering resolution width
    canvas_height=270,      # Rendering resolution height
    upscale=4,              # Nearest-neighbor upscale factor
    fps=24,                 # Frames per second
    output_format="mp4",    # "mp4", "webm", "gif", "webp", "png_seq"
    background_color="#000000",
    profiling=False         # Enable frame timing analysis
)
```

**Computed properties:** `output_width`, `output_height`

**Presets:** `.retro()`, `.landscape()`, `.portrait()`, `.square()`, `.hd()`, `.full_hd()`, `.qhd()`, `.high_res_portrait()`, `.high_res_landscape()`

---

## Scene

### Scene

```python
class MyScene(Scene):
    def construct(self):   # Required: define your animation here
        pass
```

**Object management:**
- `add(*objects)` -- add PObjects to scene
- `remove(*objects)` -- remove PObjects
- `clear()` -- remove all objects, lights, and camera FX
- `set_background(color: str)` -- set solid background color

**Animation:**
- `play(*animations, duration=1.0)` -- play animations
- `wait(seconds=1.0)` -- hold current frame

**Sound:**
- `play_sound(sfx, at=None)` -- place sound at time
- `play_voiceover(text, voice=None, speed=1.0, engine="kokoro")` -- AI TTS
- `preload_voiceovers(texts, voice=None, speed=1.0, engine="kokoro")` -- pre-cache TTS

**Lighting:**
- `add_light(*lights)`, `remove_light(*lights)`

**Camera FX:**
- `add_camera_fx(*effects)`, `remove_camera_fx(*effects)`

**Timeline:**
- `section(name)` -- mark named section
- `pause_at(name, seconds)` -- pause at section

**Rendering:**
- `render(output_path, sections=None, audio_path=None)`

**Attributes:** `config`, `canvas`, `camera`, `dry_run`, `test_frame_target`, `auto_sound`

### CinematicScene / CleanScene

Pre-configured Scene subclasses with sensible defaults for cinematic content.

### Compose

```python
Compose(config, [Scene1, Scene2, ...]).render("output.mp4")
```

Multi-scene composition with transitions. Supports `render(resume=True)` for checkpoint/resume.

---

## Shapes

### Rect
```python
Rect(width, height, x=0, y=0, color="#FFFFFF", filled=True, border_width=1)
```

### RRect (Rounded Rectangle)
```python
RRect(width, height, radius=4, x=0, y=0, color="#FFFFFF", filled=True, border_width=1)
```

### Circle
```python
Circle(radius, x=0, y=0, color="#FFFFFF", filled=True)
```

### Line
```python
Line(x1, y1, x2, y2, color="#FFFFFF", thickness=1)
```

### Triangle
```python
Triangle(x1, y1, x2, y2, x3, y3, color="#FFFFFF")
```

### Polygon
```python
Polygon(vertices, x=0, y=0, color="#FFFFFF")  # vertices: list of (x, y) tuples
```

---

## Vector Graphics

All vector objects support `Create()`, `Uncreate()`, `DrawBorderThenFill()`, and `VMorph()`.

### VPath
```python
VPath(path_data, x=0, y=0, color="#FFFFFF", stroke_width=1.0, fill_color=None)
```

### VLine
```python
VLine(x1, y1, x2, y2, color="#FFFFFF", stroke_width=1.0)
```

### VCircle
```python
VCircle(cx, cy, radius, color="#FFFFFF", stroke_width=1.0, fill_color=None)
```

### VRect
```python
VRect(x, y, width, height, color="#FFFFFF", stroke_width=1.0, fill_color=None, radius=0)
```

### VPolygon
```python
VPolygon(vertices, x=0, y=0, color="#FFFFFF", stroke_width=1.0, fill_color=None)
```

### VArrow
```python
VArrow(x1, y1, x2, y2, color="#FFFFFF", stroke_width=1.0, arrow_size=8)
```

### Vector
```python
Vector(x, y, origin_x=0, origin_y=0, color="#FFFFFF", stroke_width=1.0)
```

### SVGMobject
```python
SVGMobject.from_file(path, x=0, y=0, scale=1.0)
```

---

## Text

### PixelText
```python
PixelText(
    text, x=0, y=0, color="#FFFFFF",
    scale=1,              # Size multiplier
    align="left",         # "left", "center", "right"
    shadow=False,         # Drop shadow
    shadow_color="#000000",
    shadow_offset=(1, 1),
    max_chars=None,       # Truncate display
    font_size="5x7"       # "5x7" or "3x5"
)
```

**Properties:** `text`, `display_text`, `text_width`, `text_height`, `width`, `height`

**Fonts:** Built-in 5x7 (uppercase + digits + symbols) and 3x5 (compact).

---

## Sprites

### Sprite
```python
# From ASCII art
sprite = Sprite.from_art(["..WW..", ".WWWW.", "WWWWWW"], x=60, y=80)

# From image file
sprite = Sprite.from_file("character.png", x=60, y=80)

# From sprite sheet
sprite = Sprite.from_sheet("sheet.png", frame_width=16, frame_height=16)
```

**Animation:** `add_frame()`, `add_frames()`, `set_frame()`, `advance_frame()`
**States:** `add_state(name, frame_indices)`, `set_state(name)`
**Properties:** `flip_h`, `flip_v`, `auto_animate`, `frame_duration`, `loop`

### ImageSprite
Import real images with automatic palette quantization.

---

## Camera

### Camera (2D)
```python
scene.camera.pan_to(x, y)
scene.camera.center_on(x, y)
scene.camera.zoom = 2.0
scene.camera.follow(target, smooth=0.1, deadzone=None)
scene.camera.shake(intensity=3.0, duration=0.5)
scene.camera.set_focus(x, y, radius)  # Depth of field
scene.camera.set_bounds(min_x, min_y, max_x, max_y)
```

**Animations:** `CameraPan(camera, x, y)`, `CameraZoom(camera, zoom)`, `CameraCenterOn(camera, x, y)`

### Camera3D
```python
Camera3D(canvas_width, canvas_height, fov=45.0)
IsoCamera(canvas_width, canvas_height)
```

**Animations:** `Orbit3D(camera)`, `Zoom3D(camera)`

---

## 3D Objects

### Cube3D
```python
Cube3D(size, x=0, y=0, z=0, color="#FFFFFF")
```

### Sphere3D
```python
Sphere3D(radius, x=0, y=0, z=0, segments=16, color="#FFFFFF")
```

### Pyramid3D, Cylinder3D
```python
Pyramid3D(base, height, color="#FFFFFF")
Cylinder3D(radius, height, segments=12, color="#FFFFFF")
```

### Mesh3D
```python
Mesh3D(vertices, edges, color="#FFFFFF")
```

### Axes3D
```python
Axes3D(size, color="#FFFFFF")  # RGB-colored XYZ axes
```

**Animation:** `Rotate3D(target, axis="y", degrees=360)`

**Properties:** `rotation_x`, `rotation_y`, `rotation_z`, `obj_scale`, `projection` ("perspective" or "isometric"), `render_faces`, `face_color`, `shading_mode`

---

## Backgrounds

### Background
```python
Background(color="#000000")
```

### GradientBackground
```python
GradientBackground(color_top="#000033", color_bottom="#000000", direction="vertical")
```

### MultiGradientBackground
```python
MultiGradientBackground(stops, direction)  # Multi-color gradient
```

### Starfield
```python
Starfield(star_count=50, color="#FFF1E8", dim_color="#83769C", seed=None, twinkle=True)
```

### ParallaxLayer
```python
ParallaxLayer(image, scroll_speed=0.5, y_offset=0, tile=True)
ParallaxLayer.from_art(art, scroll_speed=0.5, y_offset=0)
```

### NoiseBackground
```python
NoiseBackground(palette, octaves, seed, style)  # "clouds", "nebula", "organic"
```

### WeatherBackground
```python
WeatherBackground(style, canvas_width, canvas_height, intensity, seed)  # "rain", "snow", "fog"
```

### AnimatedGradientBackground
```python
AnimatedGradientBackground(color_top_start, color_top_end, color_bottom_start, color_bottom_end, cycle_seconds)
```

### Terrain
```python
Terrain(width, height, x=0, y=0, style="mountains", seed=0, animate=False)
# Styles: "mountains", "desert", "ocean", "forest", "caves"
```

### SceneBackground Presets
```python
SceneBackground.preset("night_sky", width, height)
# Presets: night_sky, classroom_board, code_editor, paper, ocean_floor, sunset, forest
```

---

## Color System

### parse_color
```python
parse_color("#FF004D")     # Hex
parse_color("red")         # Named color
parse_color((255, 0, 77))  # RGB tuple
parse_color((255, 0, 77, 128))  # RGBA tuple
```

### Palettes

```python
PICO8["red"]       # PICO-8 16-color palette
GAMEBOY["light"]   # Game Boy 4-color palette
NES["blue"]        # NES extended palette
```

### Gradients
```python
LinearGradient(start_color, end_color, direction="vertical")
RadialGradient(center_color, edge_color)
```

### Utilities
```python
lerp_color(c1, c2, t)                  # Interpolate between colors
generate_palette(base_color, count=8)   # Generate palette from base
PaletteMap(source, target)              # Map between palettes
PaletteShift(obj, palette_map)          # Animate palette shift
```

---

## Effects

### ParticleEmitter
```python
ParticleEmitter(x=0, y=0, colors=None, speed=2.0, spread=360, direction=270,
                lifetime=1.0, rate=5, gravity=0, size=1, max_particles=200)
```

**Presets:** `.fire(x, y)`, `.smoke(x, y)`, `.sparks(x, y)`, `.confetti(width)`, `.snow(width)`, `.rain(width)`, `.bubbles(x, y)`

**Control:** `stop()`, `clear()`, `emitting`, `particle_count`, `is_alive`

### ParticleBurst
One-shot particle explosion. Presets: `.explode()`, `.impact()`, `.sparkle()`

### Trail
```python
Trail(target)  # Motion trail behind moving object
```

### ScreenFlash
```python
ScreenFlash(color="#FFFFFF", duration=0.2)
```

### Outline
```python
Outline(target, color="#FFFFFF", thickness=1)
```

### Grid
```python
Grid(width, height, spacing, color="#333333")
```

---

## Camera Post-Processing

```python
scene.add_camera_fx(Vignette(intensity=0.5))
scene.add_camera_fx(ChromaticAberration(offset=2.0))
scene.add_camera_fx(DepthOfField(blur_radius=5.0))
scene.add_camera_fx(FilmGrain(intensity=0.3))
scene.add_camera_fx(Letterbox(width=20))
```

---

## Shaders

```python
scene.add_camera_fx(CRTScanlines(line_spacing=2, darkness=0.3))
scene.add_camera_fx(Ripple(center_x=240, center_y=135, wavelength=20, amplitude=5))
scene.add_camera_fx(HeatShimmer(amplitude=2, frequency=0.1))
scene.add_camera_fx(Pixelate(block_size=4))
scene.add_camera_fx(ColorGrade(preset="sepia"))
# ColorGrade presets: "sepia", "cool", "warm", "noir", "cyberpunk"
```

---

## Lighting

```python
scene.add_light(AmbientLight(intensity=0.5, color="#FFFFFF"))
scene.add_light(PointLight(x=240, y=135, radius=100, intensity=1.0, color="#FFFFFF"))
scene.add_light(DirectionalLight(angle_deg=45, intensity=1.0, color="#FFFFFF"))
```

---

## Physics

### PhysicsWorld
```python
physics = PhysicsWorld(gravity_x=0, gravity_y=100, bounds=(0, 0, 480, 270))
physics.add_body(body)
physics.remove_body(body)
physics.step(dt)
```

### PhysicsBody
```python
body = PhysicsBody(pobject, mass=1.0, vx=0, vy=0, restitution=0.8, friction=0.99, is_static=False)
body.apply_force(fx, fy)
body.apply_impulse(ix, iy)
```

### Simulations
```python
Pendulum(pivot_x, pivot_y, length, angle_deg, color)
Spring(anchor_x, anchor_y, mass, stiffness, damping, color)
OrbitalSystem(bodies, x, y, width, height)
Rope(x1, y1, x2, y2, segments, gravity, friction)
FluidParticles(x, y, width, height, particle_count)
NetworkGraph(nodes, edges, x, y, width, height)
```

---

## Sound

### SoundFX
```python
# Presets
SoundFX.coin()      SoundFX.explosion()   SoundFX.whoosh()
SoundFX.jump()      SoundFX.land()        SoundFX.pickup()
SoundFX.laser()     SoundFX.hit()         SoundFX.powerup()
SoundFX.levelup()   SoundFX.door()        SoundFX.water()
SoundFX.beep()      SoundFX.boop()

# Instruments
SoundFX.piano_note("C4", duration=0.5)
SoundFX.bell_note("E5")
SoundFX.mallet_note("G4")

# Dynamic contextual
SoundFX.dynamic("reveal", intensity=0.8)
# Contexts: "success", "error", "reveal", "transition", "typing", "impact", "wonder", "tension"

# Custom
SoundFX.pitch_slide(freq_start=440, freq_end=880, duration=0.5)
```

### VoiceOver
```python
sfx, duration = VoiceOver.generate(text, voice=None, speed=1.0, engine="kokoro")
VoiceOver.preload(texts, voice=None, speed=1.0, engine="kokoro")
VoiceOver.clear_cache()
```

Engines: `"kokoro"` (fast, local) or `"chatterbox"` (high-quality voice cloning)

---

## Textures

```python
PatternTexture(pattern="checkerboard", color1="#FFF", color2="#000", cell_size=4)
# Patterns: "checkerboard", "stripes_h", "stripes_v", "diagonal", "dots", "crosshatch", "brick", "herringbone"

DitherTexture(color1="#FFF", color2="#000", density=0.5)
NoiseTexture(colors=None, scale=4, seed=42)
GradientTexture(color1="#FFF", color2="#000", direction="horizontal", width=64, height=64)
AnimatedTexture(frames)
ScrollingTexture(texture, speed_x, speed_y)
```

Apply: `obj.fill_texture = PatternTexture("checkerboard")`

---

## Groups & Layout

### Group
```python
group = Group(obj1, obj2, obj3, x=100, y=50)
```

### VStack / HStack
```python
VStack(children, spacing=10, align="center")   # Vertical stack
HStack(children, spacing=10, align="center")   # Horizontal stack
```

---

## Tilemap

### TileSet
```python
tileset = TileSet(tile_size=16)
tileset.add_tile("G", art, color_map)
tileset.add_color_tile("W", "#29ADFF")
tileset.add_animated_tile("~", arts, fps=4)
```

### TileMap
```python
tilemap = TileMap(tileset, map_data, x=0, y=0)
# map_data: list of strings, each char maps to a tile key

tilemap = TileMap.from_file(tileset, "level.txt")
tilemap.get_tile_at(col, row)
tilemap.set_tile(col, row, key)
tilemap.world_to_tile(world_x, world_y)
```

---

## Exceptions

```python
PixelEngineError        # Base exception
RenderError             # Video encoding failures
ConfigurationError      # Invalid configuration
DependencyError         # Missing dependencies
ValidationError         # Scene validation failures
AssetError              # File/image loading failures
```

---

## Plugin System

```python
from pixelengine import register_object, register_animation, register_sound, load_plugins

register_object("my_widget", MyWidgetClass)
register_animation("my_anim", MyAnimClass)
register_sound("my_sfx", my_sfx_factory)
load_plugins()  # Auto-load via entry_points
```
