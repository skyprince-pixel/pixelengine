# Features Research: Pixel Art Animation Engine

## Table Stakes (Must Have)

| Feature | Complexity | Notes |
|---------|-----------|-------|
| Scene-based API (construct/play/wait) | Medium | Core developer experience — Manim pattern |
| Geometric primitives (rect, circle, line, triangle) | Medium | Pixel-perfect Bresenham algorithms required |
| Animation tweening with easing | Medium | Linear, ease-in/out, bounce — standard easing curves |
| Text rendering | Medium | Built-in bitmap font — no system font dependency |
| Color management | Low | Hex colors, named colors, palettes |
| Video output (MP4) | Medium | ffmpeg integration, H.264 encoding |
| Configurable resolution and FPS | Low | Canvas size, upscale factor, frame rate |

## Differentiators (Competitive Advantage)

| Feature | Complexity | Notes |
|---------|-----------|-------|
| Retro color palettes (PICO-8, GameBoy, NES) | Low | Instant pixel art aesthetic without color picking |
| Inline ASCII art sprite definition | Low | Define sprites in code with color characters |
| Camera system (pan, zoom, follow) | Medium | Smooth camera for scene composition |
| Sprite sheet animation | Medium | Load and animate from sprite sheets |
| Tilemap backgrounds | Medium | Grid-based scene building |
| Particle effects | High | Configurable emitters for visual flair |
| Scene transitions | Medium | Fade, wipe, pixelate between scenes |
| Dual aspect ratio (9:16 + 16:9) | Low | Config-driven resolution presets |

## Anti-Features (Do NOT Build)

| Feature | Why |
|---------|-----|
| GUI editor | Destroys code-first philosophy, massive scope |
| Real-time preview window | Complexity explosion, not needed for video output |
| 3D support | Different domain entirely |
| Audio/TTS | External tools handle this better (ffmpeg merge) |
| Plugin system | Premature abstraction, YAGNI for v1 |
