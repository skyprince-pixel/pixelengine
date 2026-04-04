# Agent Guide

PixelEngine includes specialized tools for AI agents to build, validate, and render scenes programmatically.

---

## Scene DSL (Declarative Builder)

The `SceneBuilder` API lets agents construct scenes without coordinate math:

```python
from pixelengine import SceneBuilder, PixelConfig

builder = SceneBuilder(PixelConfig.portrait())

# Build slides declaratively
builder.slide("intro") \
    .text_block("INTEGERS", position="center", scale=2, color="#FFEC27") \
    .text_block("A visual guide", position="below", scale=1) \
    .transition("fade")

builder.slide("content") \
    .equation(r"a + b = c", position="top") \
    .shape_item("rect", width=40, height=20, color="#FF004D") \
    .chart_item("bar", data=[10, 30, 50], labels=["A", "B", "C"]) \
    .transition("wipe")

# Render
builder.render("output.mp4")
```

### Slide Helpers

| Method | Description |
|--------|-------------|
| `text_block(text, position, scale, color)` | Add text at named position |
| `equation(latex, position)` | Add LaTeX equation |
| `shape_item(type, **kwargs)` | Add primitive shape |
| `object_3d(type, **kwargs)` | Add 3D object |
| `chart_item(type, data, labels)` | Add chart |
| `vector_item(**kwargs)` | Add vector graphic |
| `physics_sim(type, **kwargs)` | Add physics simulation |
| `custom_content(cls, **kwargs)` | Add custom PObject |
| `transition(type)` | Set slide transition |

---

## Agent Pipeline

End-to-end workflow for automated scene creation:

```python
from pixelengine import AgentPipeline

result = AgentPipeline.run(
    script_path="my_scene.py",
    config=PixelConfig.portrait(),
    lint=True,          # Run linter first
    validate=True,      # Run validation
    test_frame=2.0,     # Generate test frame at t=2s
    render=True         # Render final video
)

# Check results
print(result.status)           # "success" or "failed"
print(result.lint_passed)      # bool
print(result.validation)       # dict with diagnostics
print(result.test_frame_path)  # path to test frame PNG
print(result.output_path)      # path to rendered video
```

### Pipeline Steps

1. **Lint** -- check for anti-patterns and suggest improvements
2. **Validate** -- structural analysis (bounds, overlaps, dead air)
3. **Test Frame** -- render a single frame for visual preview
4. **Render** -- encode full video

---

## Scene Validation

Machine-readable diagnostics:

```python
from pixelengine import SceneValidator

report = SceneValidator.validate(
    scene_cls=MyScene,
    config=PixelConfig.portrait(),
    at=2.0,                    # Timestamp to analyze
    source_path="my_scene.py"  # For feature coverage analysis
)

# Report structure
{
    "frames_analyzed": 48,
    "timestamps": [2.0],
    "issues": [...],           # List of detected problems
    "issue_summary": {...},    # Counts by category
    "coverage": {...},         # Feature usage analysis
    "status": "pass"           # "pass" or "fail"
}

# Pretty print
SceneValidator.print_report(report)
```

### CLI Validation

```bash
# Validate at default timestamp
python my_scene.py --validate

# Validate at specific time
python my_scene.py --validate=3.0
```

---

## Inline Linter

Check code for anti-patterns without running it:

```python
from pixelengine.cli_lint import lint_source

result = lint_source("""
from pixelengine import *

class MyScene(Scene):
    def construct(self):
        self.play(MoveTo(obj, x=200), duration=1.0)
""")

print(result["passed"])            # bool
print(result["violations"])        # List of issues
print(result["suggestions"])       # Improvement suggestions
print(result["feature_coverage"])  # Dict of feature usage
```

### CLI Linter

```bash
pixelengine-lint my_scene.py
```

### What It Detects

**Anti-patterns:**
- `MoveTo` when `OrganicMoveTo` would be better
- `FadeIn` when `OrganicFadeIn` would be better
- `TypeWriter` when `TypeWriterPro` would be better

**Feature coverage:**
- Organic animations, construction animations, transitions
- Particles, sound FX, voiceover
- Lighting, camera FX

**Topic-based suggestions:**
- Physics, gravity, math, charts, 3D, vectors, etc.

---

## Scene Presets

Pre-built scene templates configurable via class attributes:

### TitleCardScene

```python
class MyTitle(TitleCardScene):
    title = "THE UNIVERSE"
    subtitle = "A visual exploration"
    atmosphere = "cosmic"
    reveal_style = "slam"
    title_color = "#FFEC27"
    hold_duration = 2.0
```

### RevealScene

```python
class MyReveal(RevealScene):
    items = ["First point", "Second point", "Third point"]
    narration = "Let me walk you through..."
    atmosphere = "clean"
    reveal_feel = "bouncy"
    item_spacing = 30
```

### ComparisonScene

```python
class MyCompare(ComparisonScene):
    left = "Python"
    right = "JavaScript"
    vs_text = "VS"
    narration = "Let's compare..."
```

### Other Presets

- `TimelineScene` -- chronological events
- `PhysicsDemoScene` -- physics simulation demo
- `MathProofScene` -- mathematical proof walkthrough
- `DataVizScene` -- data visualization
- `QuizScene` -- interactive quiz format

---

## Multi-Scene Composition

Combine multiple scenes into a single video:

```python
from pixelengine import Compose

comp = Compose(PixelConfig.portrait(), [
    IntroScene,
    ContentScene,
    OutroScene
])
comp.render("full_video.mp4")

# Resume from crash (uses checkpoint files)
comp.render("full_video.mp4", resume=True)
```

---

## Agent Tips

1. **Always use Layout** -- `Layout.portrait()` or `Layout.landscape()` for positioning
2. **Prefer organic animations** -- `OrganicMoveTo` over `MoveTo` for natural feel
3. **Use construction anims** -- `Create()`, `GrowFromPoint()` for reveals
4. **Group with Cascade** -- `Cascade([...], feel="bouncy")` for staggered reveals
5. **Add ambient motion** -- `obj.add_updater(alive())` for living feel
6. **Preload voiceovers** -- `self.preload_voiceovers([...])` before `construct()`
7. **Test before render** -- use `--test-frame=2.0` to preview without full render
8. **Validate** -- run `SceneValidator.validate()` to catch issues early
9. **Font is 5x7** -- uppercase only, plan text accordingly
10. **Canvas coordinates** -- all positions are in low-res canvas space, not output resolution

### Import Template

```python
from pixelengine import (
    # Core
    Scene, PixelConfig, Compose,
    # Shapes
    Rect, RRect, Circle, Line, Triangle, Polygon,
    # Vector
    VPath, VCircle, VRect, VPolygon, VArrow, Vector,
    # Text
    PixelText, TypeWriter, TypeWriterPro, PerCharacter, ScrambleReveal,
    # Animation
    MoveTo, FadeIn, FadeOut, Scale, Rotate, ColorShift,
    AnimationGroup, Sequence, Stagger,
    # Organic
    OrganicMoveTo, OrganicScale, OrganicFadeIn, OrganicFadeOut,
    Cascade, Wave, alive, hover,
    # Construction
    Create, GrowFromPoint, GrowFromEdge, DrawBorderThenFill,
    # Effects
    ParticleEmitter, ScreenFlash,
    # Transitions
    FadeTransition, WipeTransition, GlitchTransition,
    # Camera
    Vignette, CRTScanlines, ColorGrade,
    # Sound
    SoundFX, VoiceOver,
    # Math
    NumberLine, BarChart, Axes, Graph, ValueTracker,
    # Education
    CodeBlock, MathTex, NeuralNetwork, GraphViz,
    # Background
    GradientBackground, Starfield, Terrain,
    # Easing
    ease_in, ease_out, ease_in_out, bounce, elastic,
)
```
