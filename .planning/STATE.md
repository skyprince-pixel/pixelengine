# State: PixelEngine

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-26)

**Core value:** Users can write a Python script describing an educational animation and render it to a pixel-perfect video file
**Current focus:** v2 Complete — All 8 phases done

## Progress

| Phase | Status | Progress |
|-------|--------|----------|
| 1. Core Engine + Shapes + Renderer | ✓ Complete | 100% |
| 2. Animation System + Text | ✓ Complete | 100% |
| 3. Sprites + Camera + Backgrounds | ✓ Complete | 100% |
| 4. Effects + Tilemaps + Polish | ✓ Complete | 100% |
| 5. Manim-like Animation System | ✓ Complete | 100% |
| 6. Texture System | ✓ Complete | 100% |
| 7. Pseudo-3D Rendering | ✓ Complete | 100% |
| 8. Simulation Engine | ✓ Complete | 100% |

## Memory

### Decisions Made
- Stack: Python 3.14 / Pillow 12.1.1 / NumPy 2.4.3 / ffmpeg
- API pattern: Manim-style Scene/PObject/Animation
- Rendering: Nearest-neighbor upscaling only, no anti-aliasing
- Output: MP4 H.264, both 9:16 and 16:9
- Venv required: system Python is PEP 668 managed
- pyproject.toml build-backend: setuptools.build_meta (not _legacy)
- 3D approach: Pseudo-3D wireframe projection, not full 3D engine
- Physics approach: Euler integration, simple and fast
- Textures: Procedural-only, no external image files
- Simulations: Self-rendering PObjects that advance physics in render()

### Lessons Learned
- Use `.venv/bin/python3` for all script execution
- Editable install works but scripts must be run from project root or with PYTHONPATH
- GradientBackground doesn't take width/height — uses canvas dimensions automatically

### Roadmap Evolution
- Phase 5 added: Manim-like Animation System — COMPLETE
- Phase 6 added: Texture System — COMPLETE
- Phase 7 added: Pseudo-3D Rendering — COMPLETE
- Phase 8 added: Simulation Engine — COMPLETE

### Deferred Ideas
(None yet)

---
*Last updated: 2026-03-26 after v2 milestone completion*
