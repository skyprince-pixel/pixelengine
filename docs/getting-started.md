# Getting Started

## Requirements

- **Python 3.10+**
- **FFmpeg** -- must be installed and available in your PATH ([download](https://ffmpeg.org/download.html))

## Installation

```bash
# Clone and install
git clone https://github.com/akashkumarnayak/pixelengine.git
cd pixelengine
pip install -e .

# Optional: AI voiceover support
pip install -e ".[voiceover]"

# Optional: development tools
pip install -e ".[dev]"
```

### Dependencies

| Package | Purpose |
|---------|---------|
| Pillow | Image rendering |
| numpy | Numerical computation |
| svgelements | SVG/vector graphics |
| matplotlib | LaTeX rendering, plotting |
| FFmpeg (system) | Video encoding |

**Optional voiceover extras:** scipy, kokoro-onnx, soundfile, chatterbox-tts, torch, huggingface-hub

---

## Core Concepts

### Scene

Everything happens inside a `Scene`. Override `construct()` to define your animation:

```python
from pixelengine import *

class MyScene(Scene):
    def construct(self):
        rect = Rect(40, 20, x=100, y=60, color="#FF004D")
        self.add(rect)
        self.play(FadeIn(rect), duration=0.5)
        self.wait(1.0)

MyScene(PixelConfig.landscape()).render("output.mp4")
```

### Coordinate System

- `(0, 0)` is the **top-left** corner
- All coordinates are in **canvas space** (low resolution, before upscaling)
- Default canvas: 480x270 pixels (upscaled 4x to 1920x1080)

### Objects (PObject)

All visual elements inherit from `PObject`. Common properties:

```python
obj.x, obj.y           # Position
obj.opacity             # 0.0 (invisible) to 1.0 (fully visible)
obj.scale_x, obj.scale_y  # Scale factors
obj.visible             # Show/hide
obj.z_index             # Layer depth (higher = on top)
obj.blend_mode          # "normal", "additive", "multiply", "screen", "overlay"
```

### Scene Lifecycle

```python
class MyScene(Scene):
    def construct(self):
        # 1. Create objects
        obj = Rect(40, 20, x=100, y=60)

        # 2. Add to scene
        self.add(obj)

        # 3. Animate
        self.play(FadeIn(obj), duration=0.5)
        self.play(MoveTo(obj, x=200), duration=1.0)

        # 4. Wait (hold current frame)
        self.wait(1.0)

        # 5. Remove
        self.remove(obj)
```

---

## Your First Scene

```python
from pixelengine import *

class HelloWorld(Scene):
    def construct(self):
        self.set_background("#1D2B53")

        # Title text
        title = PixelText("HELLO WORLD!", x=240, y=100,
                          color="#FFEC27", scale=2, align="center")
        self.add(title)
        self.play(TypeWriter(title), duration=1.5)

        # Animated rectangle
        box = Rect(60, 30, x=210, y=140, color="#FF004D")
        self.add(box)
        self.play(OrganicFadeIn(box, feel="bouncy"), duration=0.5)
        self.play(OrganicMoveTo(box, x=300, feel="snappy"), duration=1.0)

        # Particle celebration
        sparks = ParticleEmitter.sparks(x=330, y=155)
        self.add(sparks)
        self.wait(1.0)
        sparks.stop()
        self.wait(0.5)

# Render Full HD landscape
HelloWorld(PixelConfig.landscape()).render("hello.mp4")
```

Run it:
```bash
python hello.py
```

Output is saved to `outputs/hello/`.

---

## Resolution Presets

Choose a preset based on your target platform:

```python
# YouTube landscape (16:9)
MyScene(PixelConfig.landscape()).render("output.mp4")

# YouTube Shorts / TikTok (9:16)
MyScene(PixelConfig.portrait()).render("short.mp4")

# Instagram square (1:1)
MyScene(PixelConfig.square()).render("square.mp4")

# Classic retro (smaller canvas, chunkier pixels)
MyScene(PixelConfig.retro()).render("retro.mp4")

# Custom resolution
config = PixelConfig(canvas_width=400, canvas_height=300, upscale=3, fps=30)
MyScene(config).render("custom.mp4")
```

| Preset | Canvas | Output | Aspect |
|--------|--------|--------|--------|
| `PixelConfig()` | 480x270 | 1920x1080 | 16:9 |
| `PixelConfig.landscape()` | 480x270 | 1920x1080 | 16:9 |
| `PixelConfig.portrait()` | 270x480 | 1080x1920 | 9:16 |
| `PixelConfig.retro()` | 256x144 | 1024x576 | 16:9 |
| `PixelConfig.square()` | 384x384 | 1536x1536 | 1:1 |
| `PixelConfig.hd()` | 320x180 | 1280x720 | 16:9 |
| `PixelConfig.full_hd()` | 480x270 | 1920x1080 | 16:9 |
| `PixelConfig.qhd()` | 640x360 | 2560x1440 | 16:9 |

---

## Layout Templates

Use `Layout` for consistent positioning -- avoid hardcoding coordinates:

```python
from pixelengine.layout import Layout

L = Layout.portrait()  # 270x480

# Named zones
L.TITLE_ZONE      # Top area for titles
L.SUBTITLE_ZONE   # Below title
L.MAIN_ZONE       # Center stage
L.LOWER_THIRD     # Lower-third captions
L.FOOTER_ZONE     # Bottom strip

# Helpers
L.center()              # Center point of canvas
L.grid(rows, cols)      # Grid positions in MAIN_ZONE
L.stack(n)              # Vertical stack in MAIN_ZONE
L.horizontal(n)         # Horizontal row in MAIN_ZONE
```

Available: `Layout.portrait()`, `Layout.landscape()`, `Layout.retro()`, `Layout.square()`.

---

## Rendering Options

```python
# Basic render
scene.render("output.mp4")

# Render specific sections
scene.render("output.mp4", sections=["intro", "content"])

# Render with external audio
scene.render("output.mp4", audio_path="narration.wav")

# Test frame (render single frame for preview)
python my_scene.py --test-frame=2.0

# Validation
python my_scene.py --validate

# Dry run (no video output)
python my_scene.py --dry-run
```

---

## Next Steps

- [Animation Guide](animation-guide.md) -- master the animation system
- [API Reference](api-reference.md) -- full class and method reference
- [Educational Features](educational-features.md) -- math, data structures, graphs
- [Effects & Shaders](effects-and-shaders.md) -- particles, transitions, camera FX
- [Agent Guide](agent-guide.md) -- build scenes with AI agents
