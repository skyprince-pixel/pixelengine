---
phase: 1
plan: 02
title: "PObject Base + Geometric Shapes"
wave: 1
depends_on: []
files_modified:
  - pixelengine/pobject.py
  - pixelengine/shapes.py
autonomous: true
requirements: [SHAP-01, SHAP-02, SHAP-03, SHAP-04, SHAP-05]
---

# Plan 02: PObject Base + Geometric Shapes

<objective>
Create the PObject base class (the equivalent of Manim's Mobject) and pixel-perfect geometric shape primitives: Rect, Circle, Line, Triangle, Polygon. These are the building blocks for all visual elements.
</objective>

## Tasks

<task id="02.1">
<title>Create PObject base class</title>
<read_first>
- pixelengine/config.py
- pixelengine/color.py
- pixelengine/canvas.py
</read_first>
<action>
Create `pixelengine/pobject.py` with the base `PObject` class:

```python
from pixelengine.color import parse_color

class PObject:
    """Base class for all pixel objects (like Manim's Mobject)."""
    
    def __init__(self, x: int = 0, y: int = 0, color: str = "#FFFFFF"):
        self.x = x
        self.y = y
        self.color = parse_color(color)
        self.opacity = 1.0      # 0.0 to 1.0
        self.z_index = 0        # Higher = drawn on top
        self.visible = True
        self.scale_x = 1.0
        self.scale_y = 1.0
        self._children = []     # For grouped objects
    
    def move_to(self, x: int, y: int) -> "PObject":
        """Set absolute position."""
        self.x = x
        self.y = y
        return self
    
    def move_by(self, dx: int, dy: int) -> "PObject":
        """Relative position shift."""
        self.x += dx
        self.y += dy
        return self
    
    def set_color(self, color) -> "PObject":
        """Set the object's color."""
        self.color = parse_color(color)
        return self
    
    def set_opacity(self, opacity: float) -> "PObject":
        self.opacity = max(0.0, min(1.0, opacity))
        return self
    
    def render(self, canvas):
        """Override in subclasses. Draw self onto canvas."""
        raise NotImplementedError
    
    @property
    def center_x(self) -> int:
        return self.x
    
    @property
    def center_y(self) -> int:
        return self.y
    
    def get_render_color(self) -> tuple:
        """Return color with opacity applied to alpha channel."""
        r, g, b, a = self.color
        return (r, g, b, int(a * self.opacity))
```

Export `PObject` from `__init__.py`.
</action>
<acceptance_criteria>
- `pixelengine/pobject.py` contains `class PObject`
- `PObject` has attributes: `x`, `y`, `color`, `opacity`, `z_index`, `visible`, `scale_x`, `scale_y`
- `PObject.move_to` sets x and y and returns self
- `PObject.render` raises `NotImplementedError`
- `PObject.get_render_color` applies opacity to alpha channel
- `PObject` is importable from `pixelengine`
</acceptance_criteria>
</task>

<task id="02.2">
<title>Create Rect shape</title>
<read_first>
- pixelengine/pobject.py
- pixelengine/canvas.py
</read_first>
<action>
Create `pixelengine/shapes.py` starting with `Rect`:

```python
from PIL import Image, ImageDraw
from pixelengine.pobject import PObject

class Rect(PObject):
    """Pixel-perfect rectangle."""
    
    def __init__(self, width: int, height: int, x: int = 0, y: int = 0,
                 color: str = "#FFFFFF", filled: bool = True, border_width: int = 1):
        super().__init__(x=x, y=y, color=color)
        self.width = width
        self.height = height
        self.filled = filled
        self.border_width = border_width
    
    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if self.filled:
            draw.rectangle([0, 0, self.width - 1, self.height - 1], fill=color)
        else:
            for i in range(self.border_width):
                draw.rectangle([i, i, self.width - 1 - i, self.height - 1 - i], outline=color)
        canvas.blit(img, int(self.x), int(self.y))
    
    @property
    def center_x(self) -> int:
        return int(self.x + self.width // 2)
    
    @property
    def center_y(self) -> int:
        return int(self.y + self.height // 2)
```
</action>
<acceptance_criteria>
- `pixelengine/shapes.py` contains `class Rect(PObject)`
- `Rect.__init__` accepts `width`, `height`, `x`, `y`, `color`, `filled`, `border_width`
- `Rect.render` creates a PIL Image and blits to canvas
- `Rect.render` checks `self.visible` before drawing
- `Rect` supports both filled and outlined modes
</acceptance_criteria>
</task>

<task id="02.3">
<title>Create Circle shape with Bresenham algorithm</title>
<read_first>
- pixelengine/shapes.py
- pixelengine/pobject.py
</read_first>
<action>
Add `Circle` class to `pixelengine/shapes.py`:

```python
class Circle(PObject):
    """Pixel-perfect circle using Bresenham's midpoint algorithm."""
    
    def __init__(self, radius: int, x: int = 0, y: int = 0,
                 color: str = "#FFFFFF", filled: bool = True):
        super().__init__(x=x, y=y, color=color)
        self.radius = radius
    
    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        size = self.radius * 2 + 1
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        cx, cy = self.radius, self.radius
        
        if self.filled:
            # Fill circle using midpoint algorithm
            for dy in range(-self.radius, self.radius + 1):
                for dx in range(-self.radius, self.radius + 1):
                    if dx * dx + dy * dy <= self.radius * self.radius:
                        px, py = cx + dx, cy + dy
                        if 0 <= px < size and 0 <= py < size:
                            img.putpixel((px, py), color)
        else:
            # Bresenham circle outline
            self._bresenham_circle(img, cx, cy, self.radius, color)
        
        canvas.blit(img, int(self.x), int(self.y))
    
    @staticmethod
    def _bresenham_circle(img, cx, cy, r, color):
        x, y = 0, r
        d = 3 - 2 * r
        while x <= y:
            for px, py in [(cx+x, cy+y), (cx-x, cy+y), (cx+x, cy-y), (cx-x, cy-y),
                           (cx+y, cy+x), (cx-y, cy+x), (cx+y, cy-x), (cx-y, cy-x)]:
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1
```
</action>
<acceptance_criteria>
- `pixelengine/shapes.py` contains `class Circle(PObject)`
- `Circle.__init__` accepts `radius`, `x`, `y`, `color`, `filled`
- `Circle` has `_bresenham_circle` static method
- Circle render checks `self.visible` before drawing
- Filled circle uses `dx*dx + dy*dy <= radius*radius` test
</acceptance_criteria>
</task>

<task id="02.4">
<title>Create Line, Triangle, and Polygon shapes</title>
<read_first>
- pixelengine/shapes.py
- pixelengine/pobject.py
</read_first>
<action>
Add `Line`, `Triangle`, and `Polygon` classes to `pixelengine/shapes.py`:

```python
class Line(PObject):
    """Pixel-perfect line using Bresenham's algorithm."""
    
    def __init__(self, x1: int, y1: int, x2: int, y2: int,
                 color: str = "#FFFFFF", thickness: int = 1):
        super().__init__(x=min(x1, x2), y=min(y1, y2), color=color)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
    
    def render(self, canvas):
        """Draw line directly onto canvas using Bresenham's."""
        if not self.visible:
            return
        color = self.get_render_color()
        # Bresenham line algorithm — draw pixels directly on canvas
        dx = abs(self.x2 - self.x1)
        dy = abs(self.y2 - self.y1)
        sx = 1 if self.x1 < self.x2 else -1
        sy = 1 if self.y1 < self.y2 else -1
        err = dx - dy
        x, y = self.x1, self.y1
        while True:
            for tx in range(-self.thickness//2, self.thickness//2 + 1):
                for ty in range(-self.thickness//2, self.thickness//2 + 1):
                    canvas.set_pixel(x + tx, y + ty, color)
            if x == self.x2 and y == self.y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy


class Triangle(PObject):
    """Filled or outlined triangle from 3 vertices."""
    
    def __init__(self, points: list, color: str = "#FFFFFF", filled: bool = True):
        """points: [(x1,y1), (x2,y2), (x3,y3)]"""
        super().__init__(x=0, y=0, color=color)
        self.points = points
        self.filled = filled
    
    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        if self.filled:
            self._fill_triangle(canvas, color)
        else:
            pts = self.points
            for i in range(3):
                line = Line(pts[i][0], pts[i][1], pts[(i+1)%3][0], pts[(i+1)%3][1])
                line.color = self.color
                line.opacity = self.opacity
                line.render(canvas)
    
    def _fill_triangle(self, canvas, color):
        """Scanline fill algorithm for triangle."""
        pts = sorted(self.points, key=lambda p: p[1])
        # ... scanline fill implementation
        # Uses horizontal line fills between edge intersections


class Polygon(PObject):
    """Filled or outlined polygon from N vertices."""
    
    def __init__(self, points: list, color: str = "#FFFFFF", filled: bool = True):
        super().__init__(x=0, y=0, color=color)
        self.points = points
        self.filled = filled
    
    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        if self.filled:
            # Use PIL ImageDraw for filled polygon
            min_x = min(p[0] for p in self.points)
            min_y = min(p[1] for p in self.points)
            max_x = max(p[0] for p in self.points)
            max_y = max(p[1] for p in self.points)
            w = max_x - min_x + 1
            h = max_y - min_y + 1
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            local_pts = [(p[0] - min_x, p[1] - min_y) for p in self.points]
            draw.polygon(local_pts, fill=color)
            canvas.blit(img, min_x, min_y)
        else:
            for i in range(len(self.points)):
                p1 = self.points[i]
                p2 = self.points[(i + 1) % len(self.points)]
                line = Line(p1[0], p1[1], p2[0], p2[1])
                line.color = self.color
                line.opacity = self.opacity
                line.render(canvas)
```

Export all shapes from `__init__.py`: `Rect`, `Circle`, `Line`, `Triangle`, `Polygon`.
</action>
<acceptance_criteria>
- `pixelengine/shapes.py` contains `class Line(PObject)`
- `pixelengine/shapes.py` contains `class Triangle(PObject)`
- `pixelengine/shapes.py` contains `class Polygon(PObject)`
- `Line` uses Bresenham's algorithm (has `dx`, `dy`, `sx`, `sy`, `err` variables)
- `Triangle` accepts `points` list of 3 tuples
- `Polygon` accepts `points` list of N tuples
- All shapes check `self.visible` before rendering
- All shapes are importable from `pixelengine`
</acceptance_criteria>
</task>

## Verification

- `python -c "from pixelengine import Rect, Circle, Line, Triangle, Polygon; r = Rect(20, 10, color='#FF0000'); print(r.width, r.height, r.color)"`
- `python -c "from pixelengine.canvas import Canvas; from pixelengine import Rect; c = Canvas(64, 64); r = Rect(20, 10, x=5, y=5, color='#FF0000'); r.render(c); f = c.get_frame(); print(f.getpixel((10, 10)))"` — red pixel at (10, 10)
- `python -c "from pixelengine import Circle; c = Circle(10, color='#00FF00'); print(c.radius)"` prints `10`

## must_haves
- [ ] PObject base class with position, color, opacity, z_index, visible
- [ ] Rect draws filled and outlined rectangles
- [ ] Circle draws pixel-perfect circles (Bresenham for outline)
- [ ] Line draws pixel-perfect lines (Bresenham)
- [ ] Triangle and Polygon render from vertex lists
