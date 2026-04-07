# PixelEngine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)](CHANGELOG.md)

**A code-first pixel art animation engine for educational videos.**

PixelEngine renders crisp 8-bit animations at low resolution and upscales with nearest-neighbor to produce pixel-perfect videos in Full HD or higher. Think **Manim, but for retro pixel art**.

---

## Features

### Core Rendering
- **Pixel-perfect output** -- render at 256x144 and upscale to 1080p with crisp edges
- **Multiple formats** -- MP4, WebM, GIF, WebP, PNG sequence
- **Resolution presets** -- landscape, portrait, square, HD, Full HD, QHD
- **Multi-scene composition** -- stitch scenes with `Compose`, checkpoint/resume on crash

### Shapes & Graphics
- **Primitives** -- `Rect`, `RRect`, `Circle`, `Line`, `Triangle`, `Polygon`
- **Vector graphics** -- `VPath`, `VCircle`, `VRect`, `VPolygon`, `VArrow`, `Vector`, `SVGMobject`
- **Sprites** -- ASCII art, image files, sprite sheets with named animation states
- **3D wireframe** -- `Cube3D`, `Sphere3D`, `Pyramid3D`, `Cylinder3D`, `Mesh3D` with perspective/isometric projection
- **Procedural pixel art** -- `PixelArtist` generates characters and backgrounds from code

### Animation System (50+ classes)
- **Core** -- `MoveTo`, `FadeIn`, `Scale`, `Rotate`, `ColorShift`, `Blink`
- **Manim-like construction** -- `Create`, `GrowFromPoint`, `DrawBorderThenFill`, `GrowArrow`
- **Organic physics-based** -- `OrganicMoveTo`, `OrganicScale`, `SquashAndStretch`, `Breathe`, `Sway`
- **Transforms** -- `MorphTo`, `ReplacementTransform`, `VMorph`
- **Groups** -- `AnimationGroup`, `Sequence`, `Stagger`, `Wave`, `Cascade`, `Swarm`
- **Modifiers** -- `Delayed`, `Reversed`, `Looped`, `WithNoise`, `WithAnticipation`, `WithSettle`
- **Spring physics** -- `SpringTo`, `SpringScale`
- **Path following** -- `BezierPath`, `CircularPath`, `FollowPath`
- **Keyframes** -- `KeyframeTrack` timeline system
- **Text** -- `TypeWriter`, `PerCharacter`, `PerWord`, `ScrambleReveal`, `TypeWriterPro`
- **20 easing functions** -- `bounce`, `elastic`, `back_in`, `circ_out`, `custom_bezier`, `steps(n)`, ...

### Educational Visualizations
- **Math** -- `NumberLine`, `BarChart`, `PieChart`, `ScatterPlot`, `Histogram`, `Axes`, `Graph`, `Matrix`, `AnimatedNumber`
- **Data structures** -- `DSArray`, `DSStack`, `DSQueue`, `DSLinkedList`, `DSBinaryTree`, `DSHeap`, `DSHashTable`
- **Graph theory** -- `GraphViz`, `BFSAnimation`, `DFSAnimation`, `DijkstraAnimation`
- **Neural networks** -- `NeuralNetwork`, `ForwardPassAnimation`
- **Diagrams** -- `FlowChart`, `StateDiagram`
- **Science** -- `Molecule`, `Circuit`, `CellDiagram`
- **Geography** -- `WorldMap`, `MapRegion`
- **Code** -- `CodeBlock` with syntax highlighting, `CodeTrace`, `DiffView`
- **Annotations** -- `Callout`, `Label`, `Marker`, `HighlightBox`, `PointerArrow`
- **LaTeX** -- `MathTex` renders equations via matplotlib
- **Music notation** -- `MusicStaff`, `Note`

### Visual Effects
- **Particles** -- `ParticleEmitter` with presets: fire, smoke, sparks, confetti, snow, rain, bubbles
- **Transitions** -- fade, wipe, iris, dissolve, pixelate, glitch, shatter, slide, cross-dissolve
- **Camera FX** -- `Vignette`, `ChromaticAberration`, `DepthOfField`, `FilmGrain`, `Letterbox`
- **Shaders** -- `CRTScanlines`, `Ripple`, `HeatShimmer`, `Pixelate`, `ColorGrade`
- **Lighting** -- `AmbientLight`, `PointLight`, `DirectionalLight` with shadows
- **Textures** -- checkerboard, stripes, dithering, noise, animated, scrolling
- **Backgrounds** -- gradient, starfield, parallax, weather (rain/snow/fog), terrain, animated gradient

### Physics & Simulation
- **Physics engine** -- `PhysicsWorld`, `PhysicsBody` with gravity, collisions, friction
- **Simulations** -- `Pendulum`, `Spring`, `OrbitalSystem`, `Rope`, `FluidParticles`, `NetworkGraph`

### Audio
- **23 procedural SFX** -- `SoundFX.coin()`, `.explosion()`, `.whoosh()`, `.jump()`, `.laser()`, ...
- **Instrument synthesis** -- `SoundFX.piano_note("C4")`, `.bell_note()`, `.mallet_note()`
- **Dynamic contextual SFX** -- `SoundFX.dynamic("reveal")` auto-generates matching sounds
- **AI voiceover** -- TTS via Kokoro (fast) or Chatterbox Turbo (high-quality cloning)
- **Auto-sound** -- animations automatically trigger matching sound effects

### Developer Tools
- **Scene DSL** -- `SceneBuilder` for declarative, agent-friendly scene construction
- **Agent pipeline** -- `AgentPipeline.run()` orchestrates lint, validate, test frame, render
- **Validation** -- `SceneValidator` returns structured JSON diagnostics
- **Linter** -- `pixelengine-lint` CLI and `lint_source()` API
- **Preview** -- live tkinter preview window with playback controls
- **Plugin system** -- extend with custom objects, animations, and sounds
- **Scene presets** -- `TitleCardScene`, `RevealScene`, `ComparisonScene`, `TimelineScene`, ...
- **Reactive links** -- `Link`, `ReactTo` for object-following and reactive updates

### Color & Palettes
- **Retro palettes** -- PICO-8, Game Boy, NES built-in
- **Color utilities** -- hex, named colors, gradients, palette generation
- **Palette mapping** -- `PaletteMap`, `PaletteShift` animation

---

## Installation

**Prerequisites:** [FFmpeg](https://ffmpeg.org/download.html) must be installed and in your PATH.

```bash
# From source
git clone https://github.com/akashkumarnayak/pixelengine.git
cd pixelengine
pip install -e .

# With AI voiceover support
pip install -e ".[voiceover]"

# With dev tools
pip install -e ".[dev]"
```

---

## Quickstart

```python
from pixelengine import *

class MyScene(Scene):
    def construct(self):
        # Background
        self.set_background("#1D2B53")

        # Create objects
        rect = Rect(40, 20, x=50, y=60, color="#FF004D")
        title = PixelText("HELLO PIXEL!", x=72, y=30, color="#FFEC27", scale=2)

        # Add to scene
        self.add(rect, title)

        # Animate with organic motion
        self.play(OrganicFadeIn(rect, feel="bouncy"), duration=0.5)
        self.play(OrganicMoveTo(rect, x=180, feel="snappy"), duration=1.0)
        self.play(TypeWriter(title), duration=1.5)

        self.wait(1.0)

# Render as YouTube Short (9:16 portrait)
MyScene(PixelConfig.portrait()).render("output.mp4")
```

Output is auto-organized into `outputs/<script_name>/` — video, audio, test frames, and a script backup all go in one flat directory.

---

## Resolution Presets

| Preset | Canvas | Output | Aspect | Use Case |
|--------|--------|--------|--------|----------|
| `PixelConfig()` | 480x270 | 1920x1080 | 16:9 | Default Full HD |
| `PixelConfig.landscape()` | 480x270 | 1920x1080 | 16:9 | YouTube landscape |
| `PixelConfig.portrait()` | 270x480 | 1080x1920 | 9:16 | YouTube Shorts |
| `PixelConfig.retro()` | 256x144 | 1024x576 | 16:9 | Classic 8-bit |
| `PixelConfig.square()` | 384x384 | 1536x1536 | 1:1 | Instagram/social |
| `PixelConfig.hd()` | 320x180 | 1280x720 | 16:9 | HD 720p |
| `PixelConfig.full_hd()` | 480x270 | 1920x1080 | 16:9 | Full HD 1080p |
| `PixelConfig.qhd()` | 640x360 | 2560x1440 | 16:9 | QHD 2K |
| `PixelConfig.high_res_portrait()` | 540x960 | 1080x1920 | 9:16 | HQ Shorts |
| `PixelConfig.high_res_landscape()` | 960x540 | 1920x1080 | 16:9 | HQ Landscape |

---

## Examples

### Data Visualization

```python
from pixelengine import *

class ChartDemo(Scene):
    def construct(self):
        chart = BarChart(x=50, y=30, width=180, height=100,
                         data=[30, 70, 50, 90],
                         labels=["Q1", "Q2", "Q3", "Q4"],
                         colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27"])
        self.add(chart)
        self.play(chart.animate_build(), duration=2.0)
        self.wait(1.0)
```

### Physics Simulation

```python
from pixelengine import *

class PhysicsDemo(Scene):
    def construct(self):
        physics = PhysicsWorld(gravity_y=200, bounds=(0, 0, 480, 270))
        ball = Circle(radius=10, x=240, y=50, color="#FF004D")
        body = PhysicsBody(ball, mass=1.0, restitution=0.8)
        self.add(ball)
        physics.add_body(body)
        self.wait(3.0)
```

### Graph Algorithm

```python
from pixelengine import *

class GraphDemo(Scene):
    def construct(self):
        graph = GraphViz(
            edges=[(0,1), (1,2), (2,3), (0,3), (1,3)],
            node_count=4, x=50, y=30, width=180, height=120
        )
        self.add(graph)
        self.play(BFSAnimation(graph, start_node=0), duration=3.0)
        self.wait(1.0)
```

### 3D Wireframe

```python
from pixelengine import *

class CubeDemo(Scene):
    def construct(self):
        cube = Cube3D(size=60, x=240, y=135, color="#29ADFF")
        self.add(cube)
        self.play(Rotate3D(cube, axis="y", degrees=360), duration=3.0)
```

### Neural Network

```python
from pixelengine import *

class NNDemo(Scene):
    def construct(self):
        nn = NeuralNetwork(layers=[3, 4, 4, 2], x=40, y=30, width=200, height=120)
        self.add(nn)
        self.play(nn.animate_build(), duration=1.5)
        self.play(ForwardPassAnimation(nn, input_values=[0.5, 0.8, 0.3]), duration=2.0)
```

### Multi-Scene Composition

```python
from pixelengine import *

class Intro(Scene):
    def construct(self):
        title = PixelText("CHAPTER 1", x=135, y=230, align="center", scale=2)
        self.add(title)
        self.play(ScrambleReveal(title), duration=1.5)
        self.wait(1.0)

class Content(Scene):
    def construct(self):
        # ... your content scene
        self.wait(2.0)

# Stitch scenes with transitions
Compose(PixelConfig.portrait(), [Intro, Content]).render("video.mp4")
```

---

## Sound Effects

All sounds are procedurally generated -- no audio files needed:

```python
# Auto-sound: animations trigger matching sounds automatically
self.play(FadeIn(obj), duration=0.5)  # triggers reveal sound

# Manual placement
self.play_sound(SoundFX.coin())
self.play_sound(SoundFX.explosion())
self.play_sound(SoundFX.dynamic("reveal", intensity=0.8))

# Instrument synthesis
self.play_sound(SoundFX.piano_note("C4"))
self.play_sound(SoundFX.bell_note("E5"))
```

---

## AI Voiceover

```python
# Requires: pip install -e ".[voiceover]"

# Simple (blocking -- waits for speech to finish)
self.play_voiceover("Welcome to PixelEngine!")

# Advanced (sync animations with speech)
sfx, duration = VoiceOver.generate("This is a test", engine="kokoro")
self.play_sound(sfx)
self.play(FadeIn(obj), duration=duration)
```

Engines: **Kokoro** (fast, local) or **Chatterbox Turbo** (high-quality voice cloning). Models auto-download on first use.

---

## Project Structure

```
pixelengine/
├── pixelengine/            # Core engine package (60+ modules)
│   ├── __init__.py         # Public API (180+ exports)
│   ├── scene.py            # Scene orchestrator
│   ├── canvas.py           # Low-res rendering surface
│   ├── renderer.py         # FFmpeg video encoder
│   ├── config.py           # Resolution & FPS config
│   ├── pobject.py          # Base class for all objects
│   ├── shapes.py           # Geometric primitives
│   ├── vector.py           # Resolution-independent vector graphics
│   ├── sprite.py           # Sprite system
│   ├── animation.py        # Core animation system & easing
│   ├── organic.py          # Organic physics-based animations
│   ├── construction.py     # Manim-like build animations
│   ├── transform.py        # Morph/transform animations
│   ├── text.py             # Bitmap font rendering
│   ├── textanim.py         # Text animation toolkit
│   ├── camera.py           # 2D camera system
│   ├── camera3d.py         # 3D camera system
│   ├── background.py       # Background systems
│   ├── effects.py          # Particles & transitions
│   ├── camerafx.py         # Camera post-processing
│   ├── shaders.py          # Per-pixel shader effects
│   ├── lighting.py         # Dynamic lighting engine
│   ├── color.py            # Color palettes & parsing
│   ├── texture.py          # Procedural textures
│   ├── math3d.py           # 3D math (Vec3, Mat4)
│   ├── objects3d.py        # 3D wireframe objects
│   ├── physics.py          # Physics engine
│   ├── simulations.py      # Pre-built simulations
│   ├── sound.py            # Procedural sound FX
│   ├── voiceover.py        # AI TTS voiceover
│   ├── music.py            # Music notation
│   ├── mathobjects.py      # Charts, graphs, math viz
│   ├── mathtex.py          # LaTeX equation rendering
│   ├── codeblock.py        # Syntax-highlighted code
│   ├── diffview.py         # Side-by-side code comparison
│   ├── annotations.py      # Educational annotations
│   ├── datastructures.py   # DS visualization (array, tree, heap...)
│   ├── graphtheory.py      # Graph algorithms & visualization
│   ├── diagrams.py         # Flowcharts & state diagrams
│   ├── neuralnet.py        # Neural network visualization
│   ├── geography.py        # World map visualization
│   ├── science.py          # Molecule, circuit, cell diagrams
│   ├── terrain.py          # Procedural terrain generation
│   ├── tilemap.py          # Tile-based level system
│   ├── scene_dsl.py        # Declarative scene builder (agents)
│   ├── agent_pipeline.py   # Agent workflow orchestrator
│   ├── validate.py         # Scene validation & diagnostics
│   ├── cli_lint.py         # CLI linter
│   ├── presets.py          # Pre-built scene templates
│   ├── plugin.py           # Plugin system
│   ├── preview.py          # Live preview window
│   ├── compose.py          # Multi-scene composition
│   ├── log.py              # Logging config
│   └── exceptions.py       # Custom exceptions
├── tests/                  # Test suite (218 tests)
├── docs/                   # Documentation
├── pyproject.toml          # Package config
├── LICENSE                 # MIT License
└── CHANGELOG.md            # Version history
```

---

## Documentation

- **[Getting Started](docs/getting-started.md)** -- installation, first scene, core concepts
- **[Animation Guide](docs/animation-guide.md)** -- complete animation system reference
- **[API Reference](docs/api-reference.md)** -- all classes, methods, and parameters
- **[Educational Features](docs/educational-features.md)** -- math, data structures, graphs, science
- **[Effects & Shaders](docs/effects-and-shaders.md)** -- particles, transitions, camera FX, shaders
- **[Agent Guide](docs/agent-guide.md)** -- DSL, validation, pipeline, presets for AI agents
- **[Full Manual](PIXELENGINE_MANUAL.md)** -- comprehensive technical reference

---

## Contributing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check pixelengine/
```

---

## License

MIT -- see [LICENSE](LICENSE) for details.
