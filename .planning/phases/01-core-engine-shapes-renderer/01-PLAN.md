---
phase: 1
plan: 01
title: "Config, Color System, and Canvas"
wave: 1
depends_on: []
files_modified:
  - pixelengine/__init__.py
  - pixelengine/config.py
  - pixelengine/color.py
  - pixelengine/canvas.py
  - setup.py
  - pyproject.toml
autonomous: true
requirements: [CORE-05, REND-01, REND-02, REND-04, REND-05, COLR-01, COLR-02, COLR-03]
---

# Plan 01: Config, Color System, and Canvas

<objective>
Create the foundation layer: project package structure, configuration system (resolution, FPS, aspect ratios), color palette system with retro presets, and the pixel-perfect rendering canvas using Pillow. This is the base everything else builds on.
</objective>

## Tasks

<task id="01.1">
<title>Create package structure and setup.py</title>
<read_first>
- (none — greenfield)
</read_first>
<action>
Create the package root with:

1. `setup.py`:
```python
from setuptools import setup, find_packages
setup(
    name="pixelengine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["Pillow>=10.0.0", "numpy>=1.24.0"],
    python_requires=">=3.10",
)
```

2. `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=64.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"
```

3. `pixelengine/__init__.py`:
```python
"""PixelEngine — A code-first pixel art animation engine."""
__version__ = "0.1.0"
```
</action>
<acceptance_criteria>
- `setup.py` contains `name="pixelengine"`
- `setup.py` contains `Pillow>=10.0.0` in install_requires
- `setup.py` contains `numpy>=1.24.0` in install_requires
- `pixelengine/__init__.py` contains `__version__ = "0.1.0"`
- `pip install -e .` completes without errors
</acceptance_criteria>
</task>

<task id="01.2">
<title>Create PixelConfig with resolution presets</title>
<read_first>
- pixelengine/__init__.py
</read_first>
<action>
Create `pixelengine/config.py` with a `PixelConfig` dataclass:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PixelConfig:
    # Canvas dimensions (the low-res pixel art canvas)
    canvas_width: int = 256
    canvas_height: int = 144
    
    # Upscale factor for output (nearest-neighbor)
    upscale: int = 4
    
    # Frames per second
    fps: int = 12
    
    # Output
    output_format: str = "mp4"
    background_color: str = "#000000"
    
    @property
    def output_width(self) -> int:
        return self.canvas_width * self.upscale
    
    @property
    def output_height(self) -> int:
        return self.canvas_height * self.upscale
    
    @classmethod
    def landscape(cls) -> "PixelConfig":
        """16:9 for YouTube standard (256x144 → 1024x576)"""
        return cls(canvas_width=256, canvas_height=144, upscale=4)
    
    @classmethod
    def portrait(cls) -> "PixelConfig":
        """9:16 for YouTube Shorts (144x256 → 576x1024)"""
        return cls(canvas_width=144, canvas_height=256, upscale=4)
    
    @classmethod
    def square(cls) -> "PixelConfig":
        """1:1 square format (192x192 → 768x768)"""
        return cls(canvas_width=192, canvas_height=192, upscale=4)
    
    @classmethod
    def hd(cls) -> "PixelConfig":
        """HD 16:9 (320x180 → 1280x720)"""
        return cls(canvas_width=320, canvas_height=180, upscale=4)

# Global default config
DEFAULT_CONFIG = PixelConfig()
```

Export `PixelConfig` from `__init__.py`.
</action>
<acceptance_criteria>
- `pixelengine/config.py` contains `class PixelConfig`
- `PixelConfig` has `canvas_width`, `canvas_height`, `upscale`, `fps` attributes
- `PixelConfig.landscape()` returns config with `canvas_width=256, canvas_height=144`
- `PixelConfig.portrait()` returns config with `canvas_width=144, canvas_height=256`
- `output_width` property returns `canvas_width * upscale`
- `pixelengine/__init__.py` imports and exports `PixelConfig`
</acceptance_criteria>
</task>

<task id="01.3">
<title>Create color palette system</title>
<read_first>
- pixelengine/config.py
</read_first>
<action>
Create `pixelengine/color.py` with:

1. Color parsing function that accepts hex strings (#FF0000), named colors ("red"), and RGB tuples ((255, 0, 0)):
```python
def parse_color(color) -> tuple:
    """Parse color to (R, G, B, A) tuple."""
```

2. Named color dictionary with at least: black, white, red, green, blue, yellow, cyan, magenta, orange, purple, pink, gray, brown, transparent.

3. Built-in retro palettes as dictionaries:

- **PICO8** (16 colors): #000000, #1D2B53, #7E2553, #008751, #AB5236, #5F574F, #C2C3C7, #FFF1E8, #FF004D, #FFA300, #FFEC27, #00E436, #29ADFF, #83769C, #FF77A8, #FFCCAA

- **GAMEBOY** (4 colors): #0F380F, #306230, #8BAC0F, #9BBC0F

- **NES** (full 54-color palette): include the standard NES color palette

4. Single-char color shorthand for ASCII sprite art:
```python
CHAR_COLORS = {
    '.': None,  # transparent
    'R': '#FF004D',  # red
    'G': '#00E436',  # green
    'B': '#29ADFF',  # blue
    'Y': '#FFEC27',  # yellow
    'W': '#FFF1E8',  # white
    'K': '#000000',  # black (K for key)
    'O': '#FFA300',  # orange
    'P': '#FF77A8',  # pink
    'C': '#83769C',  # cool gray
    'D': '#5F574F',  # dark gray
    'L': '#C2C3C7',  # light gray
    'N': '#1D2B53',  # navy
    'M': '#7E2553',  # magenta
    'T': '#008751',  # teal
    'A': '#AB5236',  # auburn
}
```

Export `parse_color`, `PICO8`, `GAMEBOY`, `NES`, `CHAR_COLORS` from `__init__.py`.
</action>
<acceptance_criteria>
- `pixelengine/color.py` contains `def parse_color(`
- `parse_color("#FF0000")` returns `(255, 0, 0, 255)`
- `parse_color("red")` returns a valid RGBA tuple
- `parse_color((255, 0, 0))` returns `(255, 0, 0, 255)`
- `PICO8` dict has exactly 16 entries
- `GAMEBOY` dict has exactly 4 entries
- `CHAR_COLORS` dict has entry `'.'` mapping to `None`
- `CHAR_COLORS` dict has entry `'R'` mapping to `'#FF004D'`
</acceptance_criteria>
</task>

<task id="01.4">
<title>Create Canvas rendering surface</title>
<read_first>
- pixelengine/config.py
- pixelengine/color.py
</read_first>
<action>
Create `pixelengine/canvas.py` with a `Canvas` class:

```python
from PIL import Image
import numpy as np

class Canvas:
    def __init__(self, width: int, height: int, background: str = "#000000"):
        self.width = width
        self.height = height
        self.background = parse_color(background)
        self._image = Image.new("RGBA", (width, height), self.background)
        self._pixels = np.array(self._image)
    
    def clear(self):
        """Clear canvas to background color."""
    
    def set_pixel(self, x: int, y: int, color: tuple):
        """Set a single pixel. Bounds-checked."""
    
    def blit(self, image: Image.Image, x: int, y: int):
        """Paste an image (with alpha) at position."""
    
    def get_frame(self, upscale: int = 1) -> Image.Image:
        """Return canvas as PIL Image, optionally upscaled with NEAREST."""
    
    def get_raw_bytes(self, upscale: int = 1) -> bytes:
        """Return raw RGB bytes for ffmpeg pipe."""
```

Key rules:
- All coordinates are integer-only (round before drawing)
- Alpha compositing uses PIL's `paste` with mask
- `get_frame(upscale=4)` uses `Image.NEAREST` resampling (NOT BILINEAR)
- `get_raw_bytes()` converts RGBA→RGB before returning
- Bounds checking on `set_pixel` — silently ignore out-of-bounds pixels
</action>
<acceptance_criteria>
- `pixelengine/canvas.py` contains `class Canvas`
- `Canvas.__init__` creates a PIL Image with mode "RGBA"
- `Canvas.set_pixel` includes bounds checking (`if 0 <= x < self.width and 0 <= y < self.height`)
- `Canvas.get_frame` uses `Image.NEAREST` or `Image.Resampling.NEAREST`
- `Canvas.get_raw_bytes` converts to RGB mode before returning bytes
- `Canvas.clear` resets to background color
</acceptance_criteria>
</task>

## Verification

- `python -c "from pixelengine import PixelConfig; c = PixelConfig.portrait(); print(c.output_width, c.output_height)"` prints `576 1024`
- `python -c "from pixelengine.color import parse_color, PICO8; print(parse_color('#FF0000')); print(len(PICO8))"` prints `(255, 0, 0, 255)` and `16`
- `python -c "from pixelengine.canvas import Canvas; c = Canvas(32, 32); c.set_pixel(10, 10, (255, 0, 0, 255)); f = c.get_frame(4); print(f.size)"` prints `(128, 128)`

## must_haves
- [ ] Package installs with `pip install -e .`
- [ ] PixelConfig supports both landscape (16:9) and portrait (9:16) presets
- [ ] Canvas renders pixels and upscales with nearest-neighbor (no smoothing)
- [ ] Color system parses hex, named, and tuple colors
- [ ] Retro palettes (PICO8, GAMEBOY) are accessible
