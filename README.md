# 🎮 PixelEngine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)

**A code-first pixel art animation engine for educational videos.**

PixelEngine renders crisp 8-bit animations at low resolution (256×144) and upscales with nearest-neighbor to produce pixel-perfect videos. Think Manim, but for retro pixel art.

https://github.com/user-attachments/assets/placeholder

---

## ✨ Features

- **Shapes** — `Rect`, `Circle`, `Line`, `Triangle`, `Polygon`
- **Vector Graphics** — `VPath`, `VCircle`, `VRect`, `VPolygon`, `VArrow`, `Vector`
- **Animations** — `MoveTo`, `FadeIn`, `Scale`, `Rotate`, `ColorShift`, `Sequence`, `AnimationGroup`
- **Manim-like construction** — `Create`, `Uncreate`, `GrowFromPoint`, `DrawBorderThenFill`, `GrowArrow`
- **Transform animations** — `MorphTo`, `ReplacementTransform`
- **Text** — Built-in 5×7 bitmap font with `PixelText` and `TypeWriter`
- **Sprites** — ASCII art, image files, sprite sheets with animation states
- **Camera** — Pan, zoom, follow, screen shake
- **Backgrounds** — Solid, gradient, starfield, parallax layers
- **Effects** — Particles, transitions (fade/wipe/iris/dissolve), trails, screen flash
- **Textures** — Checkerboard, stripes, dithering, noise, gradients, animated & scrolling
- **3D Wireframe** — Cubes, spheres, pyramids, meshes with perspective/isometric projection
- **Physics** — Gravity, collisions, pendulums, springs, orbits, ropes, fluids
- **Sound** — 23 procedural 8-bit sound effects with auto-sound for animations
- **Voiceover** — AI text-to-speech via Chatterbox Turbo (optional)
- **Retro palettes** — PICO-8, Game Boy, NES color palettes built-in
- **Video output** — FFmpeg encoding to MP4 with audio muxing

## 📦 Installation

**Prerequisites:** [FFmpeg](https://ffmpeg.org/download.html) must be installed and available in your PATH.

```bash
# From source
git clone https://github.com/akashkumarnayak/pixelengine.git
cd pixelengine
pip install -e .

# With AI voiceover support (optional)
pip install -e ".[voiceover]"
```

## 🚀 Quickstart

```python
from pixelengine import *

class MyScene(Scene):
    def construct(self):
        # Create a rectangle
        rect = Rect(40, 20, x=50, y=60, color="#FF004D")
        self.add(rect)

        # Animate it
        self.play(FadeIn(rect), duration=0.5)
        self.play(MoveTo(rect, x=180, y=60, easing=ease_out), duration=1.0)

        # Add text
        title = PixelText("HELLO PIXEL!", x=72, y=30, color="#FFEC27", scale=2)
        self.add(title)
        self.play(TypeWriter(title), duration=1.5)

        self.wait(1.0)

# Render as YouTube Short (9:16)
MyScene(PixelConfig.portrait()).render()
```

Output is saved to `outputs/<script_name>/` with organized video, audio, and script backup.

## 🎨 Resolution Presets

| Preset | Canvas | Output | Aspect |
|--------|--------|--------|--------|
| `PixelConfig.landscape()` | 256×144 | 1024×576 | 16:9 |
| `PixelConfig.portrait()` | 144×256 | 576×1024 | 9:16 |
| `PixelConfig.square()` | 192×192 | 768×768 | 1:1 |
| `PixelConfig.hd()` | 320×180 | 1280×720 | 16:9 |
| `PixelConfig.full_hd()` | 480×270 | 1920×1080 | 16:9 |

## 📁 Project Structure

```
pixelengine/
├── pixelengine/       # Core engine package
│   ├── __init__.py    # Public API exports
│   ├── scene.py       # Scene orchestrator
│   ├── canvas.py      # Low-res rendering surface
│   ├── renderer.py    # FFmpeg video encoder
│   ├── config.py      # Resolution & FPS config
│   ├── pobject.py     # Base class for all objects
│   ├── shapes.py      # Geometric primitives
│   ├── animation.py   # Animation system & easing
│   ├── construction.py # Manim-like build animations
│   ├── transform.py   # Morph/transform animations
│   ├── text.py        # Bitmap font text
│   ├── sprite.py      # Sprite system
│   ├── camera.py      # 2D camera
│   ├── camera3d.py    # 3D camera
│   ├── background.py  # Background systems
│   ├── effects.py     # Particles & transitions
│   ├── color.py       # Color palettes & parsing
│   ├── texture.py     # Procedural textures
│   ├── math3d.py      # 3D math (Vec3, Mat4)
│   ├── objects3d.py   # 3D wireframe objects
│   ├── physics.py     # Physics engine
│   ├── collision.py   # Collision utilities
│   ├── simulations.py # Pre-built simulations
│   ├── sound.py       # Procedural sound FX
│   ├── voiceover.py   # AI TTS voiceover
│   └── tilemap.py     # Tile system
├── examples/          # Example scripts
├── pyproject.toml     # Package config
├── LICENSE            # MIT License
├── CHANGELOG.md       # Version history
└── PIXELENGINE_MANUAL.md  # Detailed manual
```

## 🔊 Sound Effects

All sounds are procedurally generated — no audio files needed:

```python
# Auto-sound (default): animations trigger matching sounds
self.play(FadeIn(obj), duration=0.5)  # → reveal sound

# Manual placement
self.play_sound(SoundFX.coin())
self.play_sound(SoundFX.explosion())
self.play_sound(SoundFX.whoosh())
```

## 🎙️ AI Voiceover (Optional)

```python
# Requires: pip install -e ".[voiceover]"
self.play_voiceover("Welcome to PixelEngine!")
```

Uses [Chatterbox Turbo](https://github.com/resemble-ai/chatterbox) for local, high-quality TTS. Models auto-download on first use.

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
