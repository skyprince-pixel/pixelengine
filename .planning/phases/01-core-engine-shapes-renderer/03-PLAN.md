---
phase: 1
plan: 03
title: "Scene Engine + Video Renderer"
wave: 2
depends_on: [01, 02]
files_modified:
  - pixelengine/scene.py
  - pixelengine/renderer.py
  - pixelengine/__init__.py
  - examples/hello_pixel.py
autonomous: true
requirements: [CORE-01, CORE-02, CORE-03, CORE-04, REND-03]
---

# Plan 03: Scene Engine + Video Renderer

<objective>
Create the Scene class (construct/play/wait/add/remove pattern) and the video renderer that pipes frames to ffmpeg. This connects everything — user writes a Scene script, adds shapes, and gets an MP4 file. Also includes the first working example script.
</objective>

## Tasks

<task id="03.1">
<title>Create Scene class with construct/add/remove/wait</title>
<read_first>
- pixelengine/config.py
- pixelengine/canvas.py
- pixelengine/pobject.py
</read_first>
<action>
Create `pixelengine/scene.py` with the `Scene` class:

```python
from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.canvas import Canvas
from pixelengine.renderer import Renderer

class Scene:
    """Base scene class. Subclass and override construct() to create animations."""
    
    def __init__(self, config: PixelConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.canvas = Canvas(self.config.canvas_width, self.config.canvas_height,
                           self.config.background_color)
        self._objects = []   # List of PObjects in scene
        self._frames = []    # Captured frames
    
    def construct(self):
        """Override this method to define your scene."""
        raise NotImplementedError("Subclass Scene and implement construct()")
    
    def add(self, *objects):
        """Add one or more PObjects to the scene."""
        for obj in objects:
            if obj not in self._objects:
                self._objects.append(obj)
        return self
    
    def remove(self, *objects):
        """Remove PObjects from the scene."""
        for obj in objects:
            if obj in self._objects:
                self._objects.remove(obj)
        return self
    
    def wait(self, seconds: float = 1.0):
        """Hold current frame for N seconds."""
        num_frames = int(seconds * self.config.fps)
        for _ in range(num_frames):
            self._capture_frame()
    
    def play(self, *animations, duration: float = 1.0):
        """Play one or more animations over the given duration.
        For Phase 1, this is a placeholder that just captures frames.
        Full animation support comes in Phase 2."""
        num_frames = max(1, int(duration * self.config.fps))
        for frame_idx in range(num_frames):
            alpha = frame_idx / max(1, num_frames - 1)
            for anim in animations:
                if hasattr(anim, 'interpolate'):
                    anim.interpolate(alpha)
            self._capture_frame()
    
    def _capture_frame(self):
        """Render all objects to canvas and capture the frame."""
        self.canvas.clear()
        # Sort by z_index for proper layering
        sorted_objects = sorted(self._objects, key=lambda o: o.z_index)
        for obj in sorted_objects:
            if obj.visible:
                obj.render(self.canvas)
        frame = self.canvas.get_frame(self.config.upscale)
        self._frames.append(frame)
    
    def render(self, output_path: str = "output.mp4"):
        """Run construct() and encode all frames to video."""
        print(f"[PixelEngine] Building scene...")
        self._frames = []
        self.construct()
        print(f"[PixelEngine] Captured {len(self._frames)} frames")
        
        if not self._frames:
            print("[PixelEngine] Warning: No frames captured!")
            return
        
        renderer = Renderer(self.config)
        renderer.encode(self._frames, output_path)
        print(f"[PixelEngine] Video saved to: {output_path}")
```

Export `Scene` from `__init__.py`.
</action>
<acceptance_criteria>
- `pixelengine/scene.py` contains `class Scene`
- `Scene` has methods: `construct`, `add`, `remove`, `wait`, `play`, `render`, `_capture_frame`
- `Scene.construct` raises `NotImplementedError`
- `Scene.add` appends to `self._objects` (avoids duplicates)
- `Scene.wait` captures `int(seconds * fps)` frames
- `Scene._capture_frame` sorts objects by `z_index` before rendering
- `Scene.render` calls `construct()` then encodes frames
- `Scene` is importable from `pixelengine`
</acceptance_criteria>
</task>

<task id="03.2">
<title>Create Renderer with ffmpeg pipe encoding</title>
<read_first>
- pixelengine/config.py
- pixelengine/canvas.py
</read_first>
<action>
Create `pixelengine/renderer.py`:

```python
import subprocess
import shutil
from pathlib import Path
from PIL import Image
from pixelengine.config import PixelConfig

class Renderer:
    """Encodes frames to video using ffmpeg."""
    
    def __init__(self, config: PixelConfig):
        self.config = config
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Verify ffmpeg is available."""
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "ffmpeg not found! Install it:\n"
                "  macOS: brew install ffmpeg\n"
                "  Linux: sudo apt install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )
    
    def encode(self, frames: list, output_path: str):
        """Encode list of PIL Images to MP4 video."""
        if not frames:
            raise ValueError("No frames to encode")
        
        output = Path(output_path)
        width = self.config.output_width
        height = self.config.output_height
        fps = self.config.fps
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "rgb24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "18",
            output_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        
        for i, frame in enumerate(frames):
            # Convert RGBA to RGB
            if frame.mode == "RGBA":
                rgb_frame = Image.new("RGB", frame.size, (0, 0, 0))
                rgb_frame.paste(frame, mask=frame.split()[3])
                frame = rgb_frame
            elif frame.mode != "RGB":
                frame = frame.convert("RGB")
            
            # Write raw bytes
            process.stdin.write(frame.tobytes())
            
            # Progress indicator
            if (i + 1) % (fps * 5) == 0 or i == len(frames) - 1:
                seconds = (i + 1) / fps
                print(f"  Encoding: {seconds:.1f}s ({i+1}/{len(frames)} frames)")
        
        process.stdin.close()
        process.wait()
        
        if process.returncode != 0:
            stderr = process.stderr.read().decode()
            raise RuntimeError(f"ffmpeg encoding failed:\n{stderr}")
        
        file_size = output.stat().st_size / 1024
        print(f"  Output: {output_path} ({file_size:.0f} KB)")
```
</action>
<acceptance_criteria>
- `pixelengine/renderer.py` contains `class Renderer`
- `Renderer._check_ffmpeg` uses `shutil.which("ffmpeg")`
- `Renderer.encode` uses `subprocess.Popen` with `-f rawvideo` and `-pix_fmt rgb24`
- `Renderer.encode` converts RGBA frames to RGB before writing bytes
- `Renderer.encode` uses `libx264` codec with `yuv420p` pixel format
- ffmpeg command includes `-y` flag (overwrite output)
- Progress is printed during encoding
</acceptance_criteria>
</task>

<task id="03.3">
<title>Create hello_pixel.py example script</title>
<read_first>
- pixelengine/scene.py
- pixelengine/shapes.py
- pixelengine/config.py
</read_first>
<action>
Create `examples/hello_pixel.py`:

```python
"""
PixelEngine — Hello World Example
Draws shapes on screen, holds for a few seconds, renders to MP4.
"""
from pixelengine import Scene, PixelConfig, Rect, Circle, Line, Triangle

class HelloPixel(Scene):
    def construct(self):
        # Red rectangle
        rect = Rect(40, 30, x=20, y=20, color="#FF004D")
        self.add(rect)
        self.wait(1.0)
        
        # Green circle
        circle = Circle(15, x=100, y=50, color="#00E436")
        self.add(circle)
        self.wait(1.0)
        
        # Blue line
        line = Line(10, 120, 240, 30, color="#29ADFF")
        self.add(line)
        self.wait(1.0)
        
        # Yellow triangle
        tri = Triangle([(150, 20), (130, 60), (170, 60)], color="#FFEC27")
        self.add(tri)
        self.wait(2.0)

if __name__ == "__main__":
    scene = HelloPixel(PixelConfig.landscape())
    scene.render("hello_pixel.mp4")
    print("Done! Open hello_pixel.mp4 to see the result.")
```
</action>
<acceptance_criteria>
- `examples/hello_pixel.py` exists
- Script imports from `pixelengine` (Scene, PixelConfig, Rect, Circle, Line, Triangle)
- `HelloPixel` subclasses `Scene` and implements `construct()`
- Script uses `PixelConfig.landscape()` configuration
- Script renders to `hello_pixel.mp4`
- Running `python examples/hello_pixel.py` produces a valid MP4 file
</acceptance_criteria>
</task>

<task id="03.4">
<title>Update __init__.py with all public exports</title>
<read_first>
- pixelengine/__init__.py
- pixelengine/config.py
- pixelengine/color.py
- pixelengine/canvas.py
- pixelengine/pobject.py
- pixelengine/shapes.py
- pixelengine/scene.py
</read_first>
<action>
Update `pixelengine/__init__.py` to export everything users need:

```python
"""PixelEngine — A code-first pixel art animation engine."""
__version__ = "0.1.0"

from pixelengine.config import PixelConfig
from pixelengine.color import parse_color, PICO8, GAMEBOY, CHAR_COLORS
from pixelengine.pobject import PObject
from pixelengine.shapes import Rect, Circle, Line, Triangle, Polygon
from pixelengine.scene import Scene

__all__ = [
    "PixelConfig", "Scene", "PObject",
    "Rect", "Circle", "Line", "Triangle", "Polygon",
    "parse_color", "PICO8", "GAMEBOY", "CHAR_COLORS",
]
```
</action>
<acceptance_criteria>
- `pixelengine/__init__.py` imports `Scene` from `pixelengine.scene`
- `pixelengine/__init__.py` imports all shapes: `Rect, Circle, Line, Triangle, Polygon`
- `pixelengine/__init__.py` imports `PixelConfig`
- `pixelengine/__init__.py` has `__all__` list
- `python -c "from pixelengine import Scene, Rect, Circle, PixelConfig"` succeeds
</acceptance_criteria>
</task>

## Verification

- `pip install -e .` in project root succeeds
- `python examples/hello_pixel.py` produces `hello_pixel.mp4` without errors
- `hello_pixel.mp4` plays and shows crisp pixel shapes (no blurring)
- `python -c "from pixelengine import Scene, Rect, Circle, Line, Triangle, Polygon, PixelConfig; print('All imports OK')"` prints "All imports OK"

## must_haves
- [ ] Scene.construct() pattern works (subclass + override)
- [ ] Scene.add/remove manages PObjects
- [ ] Scene.wait() holds frames for specified duration
- [ ] Scene.render() produces MP4 via ffmpeg
- [ ] hello_pixel.py example runs end-to-end and produces valid video
