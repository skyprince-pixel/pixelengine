# Changelog

All notable changes to PixelEngine will be documented in this file.

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
