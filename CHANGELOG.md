# Changelog

All notable changes to PixelEngine will be documented in this file.

## [0.8.0] — 2026-03-30

### Added — Agentic Workflow Optimization
- **Declarative Scene DSL** (`scene_dsl.py`): `SceneBuilder` + `slide()` for zero-coordinate-math scene construction. Agents describe slides as structured data with `equation()`, `text_block()`, `shape_item()`, `object_3d()`, `chart_item()`, `vector_item()`, `physics_sim()`, and `custom_content()` helpers.
- **Structured Validation** (`validate.py`): `SceneValidator.validate()` returns machine-readable JSON diagnostics — bounds checking, overlap detection, dead air detection, and feature coverage analysis. Replaces visual `--test-frame` PNG inspection.
- **Scene Presets** (`presets.py`): 7 pre-built scene templates — `TitleCardScene`, `RevealScene`, `ComparisonScene`, `TimelineScene`, `PhysicsDemoScene`, `MathProofScene`, `DataVizScene`. Configure via class attributes to reduce boilerplate ~60%.
- **Agent Pipeline** (`agent_pipeline.py`): `AgentPipeline.run()` orchestrates lint → validate → test_frame → render in a single programmable API call. Returns structured `PipelineResult` with status, issues, and diagnostics.
- **Inline Linter API**: `lint_source(code_string)` function returns structured dict (`{violations, suggestions, passed, feature_coverage}`) for programmatic linting — agents can lint before writing files.
- **`--validate` CLI flag**: `python script.py --validate` runs structural validation and prints JSON report. Supports `--validate=3.0` for specific timestamps.
- **`lint=True` render option**: `Scene.render(lint=True)` runs the linter before encoding — halts on violations.

### Improved
- **Compose checkpoint/resume**: `Compose.render(resume=True)` resumes from last-completed scene after crashes. Checkpoints saved as `.checkpoint` JSON files.

 ## [0.6.0] — 2026-03-27
 
 ### Added
 - **Resolution-independent Vector Graphics**: `VPath`, `VCircle`, `VRect`, `VPolygon`, `VArrow`, `Vector`
 - **SVG Support**: `SVGMobject(file_path)` for importing and rendering external SVG files
 - Full integration of Vector objects with construction animations (`Create`, `Uncreate`, `DrawBorderThenFill`)
 - **Advanced Procedural Audio**: Rebuilt sound module from scratch with Piano, Bell, and Mallet synthesis + ADSR envelopes.
 - **Pedalboard FX**: Studio-grade Reverb, Chorus, Compressor, Delay via Spotify's Pedalboard library.
 - **Dynamic SFX**: `SoundFX.dynamic(situation)` to auto-generate contextual sounds (e.g. `success`, `error`, `wonder`, `tension`).
 
 ### Fixed
 - Render quality sync for child-objects in `Scene._render_object`
 - `AmbientLight` default intensity now correctly applied across all surfaces
 
 ## [0.2.0] — 2026-03-27

### Added
- **Manim-like construction animations**: `Create`, `Uncreate`, `GrowFromPoint`, `GrowFromEdge`, `DrawBorderThenFill`, `ShowPassingFlash`, `GrowArrow`
- **Transform animations**: `MorphTo`, `ReplacementTransform`, `TransformMatchingPoints`
- **Texture system**: `PatternTexture`, `DitherTexture`, `NoiseTexture`, `GradientTexture`, `AnimatedTexture`, `ScrollingTexture`
- **Pseudo-3D wireframe rendering**: `Vec3`, `Mat4`, `Cube3D`, `Sphere3D`, `Pyramid3D`, `Cylinder3D`, `Mesh3D`, `Axes3D`
- **3D camera system**: `Camera3D`, `IsoCamera`, `Orbit3D`, `Zoom3D`
- **Physics engine**: `PhysicsBody`, `PhysicsWorld`, `StaticBody`, `Bounds`, `CollisionCallback`
- **Physics simulations**: `Pendulum`, `Spring`, `OrbitalSystem`, `Rope`, `FluidParticles`
- **Math objects**: `ValueTracker`, `NumberLine`, `BarChart`, `Axes`, `Graph`, `Dot`
- **Chatterbox Turbo TTS** voiceover system (`VoiceOver.generate()`)
- Additional easing functions: `ease_in_cubic`, `ease_out_cubic`, `ease_in_out_cubic`

### Fixed
- Class-level `_last_tw_char_count` state leak between Scene instances
- Missing `_updaters` initialization in `PObject` causing AttributeError
- Silent exception swallowing in scene updaters (now warns)
- `import math` inside render loop in `Starfield`
- `Scale` animation capturing dimensions in `on_complete` instead of `on_start`

### Improved
- `Canvas.clear()` reuses image buffer instead of allocating new one each frame
- `GradientBackground` caches rendered gradient image
- `IrisTransition`, `ScreenFlash`, `Outline` use PIL bulk operations instead of pixel loops
- Consolidated `setup.py` into modern `pyproject.toml`
- Comprehensive `.gitignore` for GitHub publishing

## [0.1.0] — 2026-03-25

### Added
- Core engine: `PixelConfig`, `Canvas`, `Scene`, `Renderer`
- Shapes: `Rect`, `Circle`, `Line`, `Triangle`, `Polygon`
- Animations: `MoveTo`, `MoveBy`, `FadeIn`, `FadeOut`, `Scale`, `Rotate`, `Blink`, `ColorShift`
- Animation groups: `AnimationGroup`, `Sequence`
- Easing functions: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `bounce`, `elastic`
- Text rendering: `PixelText` with built-in 5×7 bitmap font, `TypeWriter`
- Sprites: `Sprite` with ASCII art, file loading, sprite sheets, and animation states
- Camera system: `Camera` with pan, zoom, follow, shake
- Backgrounds: `Background`, `GradientBackground`, `Starfield`, `ParallaxLayer`
- Effects: `ParticleEmitter`, `FadeTransition`, `WipeTransition`, `IrisTransition`, `DissolveTransition`, `Trail`, `ScreenFlash`, `Outline`, `Grid`
- Tile system: `TileSet`, `TileMap`
- Sound: `SoundFX` with 23 procedural presets, `SoundTimeline`, auto-sound for animations
- Color system: `PICO8`, `GAMEBOY`, `NES` palettes, `CHAR_COLORS` for ASCII sprites
- FFmpeg-based video encoding with audio muxing
