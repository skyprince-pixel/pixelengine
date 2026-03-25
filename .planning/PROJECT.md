# PixelEngine

## What This Is

A code-first Python engine for creating pixel art style educational videos. Users write Python scripts defining scenes with animated geometric shapes, pixel sprites, text overlays, and transitions — then render to video. Think Manim, but everything renders in a crunchy pixel art aesthetic. Built for math and science educational content on YouTube (both Shorts and long-form).

## Core Value

Users can write a Python script describing an educational animation and render it to a pixel-perfect video file — the code-to-video pipeline must be simple and reliable.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Code-first scene definition API (Scene class with construct/play/wait)
- [ ] Pixel art rendering engine (Pillow-based, nearest-neighbor upscaling)
- [ ] Geometric shape primitives (rect, circle, line, polygon, triangle)
- [ ] Animation system with easing (move, fade, scale, rotate, morph)
- [ ] Pixel text rendering with built-in bitmap font
- [ ] Sprite support (inline ASCII art, image loading, sprite sheets)
- [ ] Camera system (pan, zoom, follow, shake)
- [ ] Color palette system with retro presets (PICO-8, GameBoy, NES)
- [ ] Video output via ffmpeg (MP4 H.264)
- [ ] Support both 9:16 (YouTube Shorts) and 16:9 (YouTube) aspect ratios
- [ ] Tilemap/grid backgrounds for scene composition
- [ ] Visual effects (particles, screen transitions, flash)

### Out of Scope

- GUI/visual editor — this is code-first only
- Real-time preview/interactive mode — render-to-file only for v1
- Audio/TTS integration — video only, audio added externally
- 3D rendering — strictly 2D pixel art
- Web-based rendering — Python CLI only

## Context

- Creator has experience making YouTube Shorts using Python + matplotlib for math/science animations
- Target workflow: write script → run → get video file → upload to YouTube
- Pixel art aesthetic makes educational content more engaging and approachable
- Primary subjects: math (geometry, algebra, calculus visualizations) and science (physics, chemistry)
- Manim is the gold standard for code-driven math animations; this follows similar API patterns but with pixel art rendering instead of vector graphics

## Constraints

- **Tech stack**: Python 3.10+ with Pillow + NumPy + ffmpeg — no heavy dependencies
- **Performance**: Must render a 60-second video in under 5 minutes on a consumer machine
- **Output quality**: Pixel-perfect rendering — no anti-aliasing, no blurring, nearest-neighbor scaling only
- **Resolution**: Low-res canvas (e.g., 256×144 or 320×180) upscaled to HD via nearest-neighbor

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pillow over pygame for rendering | No window/display needed, pure image rendering for video output | — Pending |
| Manim-inspired API (Scene/PObject/Animation) | Familiar pattern for programmatic animation, proven ergonomics | — Pending |
| Nearest-neighbor upscaling for pixel crispness | Essential for pixel art — smoothing destroys the aesthetic | — Pending |
| ffmpeg for video encoding | Industry standard, widely available, fast encoding | — Pending |

---
*Last updated: 2026-03-25 after initialization*
