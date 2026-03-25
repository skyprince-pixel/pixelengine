# Stack Research: Pixel Art Animation Engine

## Recommended Stack (2025)

### Core Runtime
- **Python 3.11+** — Primary language
  - Rationale: User's existing ecosystem, mature library support, excellent for scripting-style APIs
  - Confidence: ★★★★★

### Rendering
- **Pillow (PIL Fork) 10.x** — 2D image rendering
  - Rationale: Pure Python image library, perfect for pixel-level manipulation, no display window needed
  - NOT pygame (requires display init), NOT cairo (overkill for pixel art)
  - Confidence: ★★★★★

- **NumPy 1.26+** — Array operations for batch pixel manipulation
  - Rationale: Performance-critical for frame compositing, palette operations, bulk transforms
  - Confidence: ★★★★★

### Video Encoding
- **ffmpeg (system binary)** — Video encoding
  - Rationale: Industry standard, supports H.264/H.265, pipe-based input (no temp files needed)
  - Pattern: PIL Image → raw bytes → ffmpeg stdin → MP4
  - Confidence: ★★★★★

### Package Structure
- **setuptools + pyproject.toml** — Package management
  - Simple `pip install -e .` for development
  - Confidence: ★★★★☆

## What NOT to Use

| Library | Why Not |
|---------|---------|
| pygame | Requires display initialization, designed for interactive apps not rendering |
| OpenCV | Heavy dependency, designed for computer vision not pixel art |
| MoviePy | Adds unnecessary abstraction layer, ffmpeg direct is simpler |
| Matplotlib | Not designed for pixel-perfect rendering, anti-aliases everything |
| Cairo/Skia | Vector graphics engines — antithetical to pixel art |

## Architecture Implication

The stack is intentionally minimal: PIL for pixels, NumPy for speed, ffmpeg for video. No framework overhead.
