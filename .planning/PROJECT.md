# PixelEngine

## What This Is

A code-first Python engine for creating pixel art style educational videos. Users write Python scripts defining scenes with animated geometric shapes, pixel sprites, text overlays, and transitions — then render to video. Think Manim, but everything renders in a crunchy pixel art aesthetic. Built for math and science educational content on YouTube (both Shorts and long-form).

## Core Value

Users can write a Python script describing an educational animation and render it to a pixel-perfect video file — the code-to-video pipeline must be simple and reliable.

## Requirements

### Validated

- [x] Code-first scene definition API (Scene class with construct/play/wait)
- [x] Pixel art rendering engine (Pillow-based, nearest-neighbor upscaling)
- [x] Geometric shape primitives (rect, circle, line, polygon, triangle)
- [x] Animation system with easing (move, fade, scale, rotate, morph)
- [x] Pixel text rendering with built-in bitmap font
- [x] Sprite support (inline ASCII art, sprite sheets)
- [x] Camera system (pan, zoom, follow, shake)
- [x] Color palette system with retro presets (PICO-8, GameBoy, NES)
- [x] Video output via ffmpeg (MP4 H.264)
- [x] Support both 9:16 (YouTube Shorts) and 16:9 (YouTube) aspect ratios
- [x] Tilemap/grid backgrounds for scene composition
- [x] Visual effects (particles, screen transitions, flash)
- [x] Procedural audio and SoundFX system
- [x] Kokoro TTS voiceover integration

### Active (v2)

- [ ] Manim-like construction animations (GrowFromPoint, GrowFromEdge, DrawBorderThenFill)
- [ ] Shape morphing and transform animations (MorphTo, TransformMatchingPoints)
- [ ] Math objects (NumberLine, BarChart, Graph, Axes, ValueTracker)
- [ ] Updater system for reactive animations
- [ ] Texture system (procedural patterns, dithering, fill textures)
- [ ] Pseudo-3D wireframe rendering (cube, sphere, pyramid projection)
- [ ] 3D camera system (orbit, isometric, perspective)
- [ ] Physics simulation engine (gravity, velocity, forces)
- [ ] Collision detection (AABB, circle-circle)
- [ ] Pre-built simulations (pendulum, spring, orbit, rope, fluid)

### Out of Scope

- GUI/visual editor — this is code-first only
- Real-time preview/interactive mode — render-to-file only
- Web-based rendering — Python CLI only
- Full 3D engine with shading/lighting — pseudo-3D wireframes only

## Context

- Creator has experience making YouTube Shorts using Python + matplotlib for math/science animations
- Target workflow: write script → run → get video file → upload to YouTube
- Pixel art aesthetic makes educational content more engaging and approachable
- Primary subjects: math (geometry, algebra, calculus visualizations) and science (physics, chemistry)
- Manim is the gold standard for code-driven math animations; this follows similar API patterns but with pixel art rendering instead of vector graphics
- v1 is production-ready with voiceover integration (Kokoro TTS) and has been used to render multiple educational videos

## Constraints

- **Tech stack**: Python 3.10+ with Pillow + NumPy + ffmpeg — no heavy dependencies
- **Performance**: Must render a 60-second video in under 5 minutes on a consumer machine
- **Output quality**: Pixel-perfect rendering — no anti-aliasing, no blurring, nearest-neighbor scaling only
- **Resolution**: Low-res canvas (e.g., 256×144 or 320×180) upscaled to HD via nearest-neighbor

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pillow over pygame for rendering | No window/display needed, pure image rendering for video output | ✓ Working |
| Manim-inspired API (Scene/PObject/Animation) | Familiar pattern for programmatic animation, proven ergonomics | ✓ Working |
| Nearest-neighbor upscaling for pixel crispness | Essential for pixel art — smoothing destroys the aesthetic | ✓ Working |
| ffmpeg for video encoding | Industry standard, widely available, fast encoding | ✓ Working |
| Pseudo-3D via wireframe projection | Full 3D is overkill; wireframes preserve pixel aesthetic | — Pending |
| Physics via Euler integration | Simple, fast, correct enough for educational visualizations | — Pending |

---
*Last updated: 2026-03-26 after v2 milestone initialization*
