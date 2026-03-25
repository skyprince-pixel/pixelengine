# Research Summary: PixelEngine

## Key Findings

**Stack:** Python 3.11+ / Pillow 10.x / NumPy 1.26+ / ffmpeg (system). Deliberately minimal — no pygame, OpenCV, or other heavy frameworks.

**Table Stakes:** Scene API (construct/play/wait), geometric primitives, animation with easing, text rendering, video output (MP4), configurable resolution.

**Differentiators:** Retro color palettes (PICO-8, GameBoy), inline ASCII art sprites, camera system, dual aspect ratio (9:16 + 16:9), particle effects, scene transitions.

**Watch Out For:**
- Anti-aliasing contamination (never use smooth scaling, always nearest-neighbor)
- Float-to-pixel rounding (snap to int at render time)
- ffmpeg pipe reliability (use raw RGB format, proper subprocess handling)
- Performance (use NumPy arrays, avoid per-pixel Python loops)
- Scope creep (ship core pipeline before polish)

## Build Order

Config/Color → Canvas → PObject → Shapes → Sprite/Text → Animation → Camera → Scene → Renderer → Effects/TileMap

## Architecture Pattern

Manim-style: `Scene.construct()` → `self.play()` → Animation ticks PObjects → Camera transforms → Canvas composites → Frames pipe to ffmpeg → MP4 output.
