# PixelEngine

**PixelEngine** is a specialized, code-first Python framework for generating educational, animated, 8-bit style pixel art videos. It is inspired by tools like Manim but acts exclusively in low-resolution coordinate space (e.g., 256×144), using purely nearest-neighbor upscale routing to keep a crisp, retro aesthetic.

All rendering is done via **Pillow** images encoded straight into **ffmpeg** with programmatic logic and math. No external graphic files or audio files are required by default.

---

## Technical Stack & Requirements

1. **Python**: 3.8+ (Virtual Environment **highly** recommended)
2. **Core Dependencies**: `Pillow`, `numpy`
3. **Audio Dependencies**: `soundfile`, `kokoro-onnx` (for Voiceover TTS)
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

## 4. Sprites
The `Sprite` system runs off an ASCII matrix array, letting you define 8-bit characters dynamically without `.png` files!
The engine maps pixel character data against the standard Picol-8 / NES color maps.

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
- A `TypeWriter` text prints typing ticks.
- A `FadeIn` makes a shimmer noise.
- A `FadeTransition` adds a whoosh noise.

### Manual Event Cues
```python
from pixelengine import SoundFX
self.play_sound(SoundFX.coin())
self.play_sound(SoundFX.explosion())
self.play_sound(SoundFX.jump())
self.play_sound(SoundFX.powerup())
self.play_sound(SoundFX.correct()) # Learning app cues
```

### VoiceOver (Kokoro TTS)
Perfectly timed, synchronized TTS using the `Kokoro-ONNX` runtime.

```python
# Generates audio, syncs timeline, holds Scene frame execution!
self.play_voiceover(
    "Hello! I'm Adam, the AI teacher. Here is math trick #1.", 
    voice="am_adam"
)
```
You don't need `duration=` or manual `self.wait()`. The engine measures the length of the speech exactly!

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
       SoundFX, Grid, ParticleEmitter, TileMap, TileSet
   )
   ```
5. **No File dependencies**: Do **not** try to load `.png`, `.wav`, or `.json` to make scenes. Utilize ASCII Sprite generation (`Sprite.from_art()`), raw math logic strings, TileMaps (`TileSet.add_color_tile()`), and `SoundFX.coin()`. Rely on the procedurally generated assets 100% of the time to maintain absolute hermetic execution. 
6. **VoiceOver Speed / Blockers**: Utilizing `self.play_voiceover` is blocking logic. It intrinsically waits for the dialogue to finish. Do **not** write `self.play(MoveTo(...))` *below* a `play_voiceover` sequentially if you want them to happen together!
   Instead, if you want an animation running *WHILE* speaking, do it like this:
   ```python
   # Correct!
   from pixelengine.voiceover import VoiceOver
   
   # 1. Generate VoiceOver Object manually natively
   speech_sfx, speech_dur = VoiceOver.generate("Look at me move!")
   
   # 2. Play motion *alongside* sound timeline cue, using EXACT dynamic length
   self.play(MoveTo(character, x=200), duration=speech_dur, sound=speech_sfx)
   ```
7. **Educational Context**: Make extensive use of `Grid(cell_size=16)`, `Outline()`, `TypeWriter`, and `SoundFX.correct()` / `SoundFX.incorrect()` when generating visual Math/Science tutorial scenarios per user prompts.
