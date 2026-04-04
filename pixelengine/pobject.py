"""PixelEngine PObject — base class for all pixel objects."""
from collections import namedtuple
from pixelengine.color import parse_color

Bounds = namedtuple("Bounds", ["x", "y", "width", "height"])


class PObject:
    """Base class for all pixel objects (analogous to Manim's Mobject).

    Every visual element in PixelEngine inherits from PObject.
    Subclasses must override ``render(canvas)`` to draw themselves.
    """

    def __init__(self, x: int = 0, y: int = 0, color: str = "#FFFFFF"):
        self.x = x
        self.y = y
        self.color = parse_color(color)
        self.opacity: float = 1.0        # 0.0 = invisible, 1.0 = fully opaque
        self.z_index: int = 0            # Higher = drawn on top
        self.visible: bool = True
        self.scale_x: float = 1.0
        self.scale_y: float = 1.0
        self.fill_texture = None         # Texture object for patterned fills
        self.fill_gradient = None        # LinearGradient or RadialGradient
        self._children: list = []
        self._updaters: list = []        # Per-frame update callbacks: fn(obj, dt)

        # Lighting interaction
        self.casts_shadow: bool = False   # Whether this object casts shadows
        self.receives_light: bool = True  # Whether lighting affects this object
        self.shadow_opacity: float = 0.4  # Shadow darkness (0.0–1.0)

        # Per-object quality control
        self.render_quality: float = 1.0  # 0.25=chunky, 1.0=normal, 2.0=smooth

        # Blend mode: "normal", "additive", "multiply", "screen", "overlay"
        self.blend_mode: str = "normal"

    # ── Position ────────────────────────────────────────────

    def move_to(self, x: int, y: int) -> "PObject":
        """Set absolute position."""
        self.x = x
        self.y = y
        return self

    def move_by(self, dx: int, dy: int) -> "PObject":
        """Shift position by (dx, dy)."""
        self.x += dx
        self.y += dy
        return self

    # ── Appearance ──────────────────────────────────────────

    def set_color(self, color) -> "PObject":
        """Set the object's color (hex, named, or tuple)."""
        self.color = parse_color(color)
        return self

    def set_opacity(self, opacity: float) -> "PObject":
        """Set opacity (clamped to 0.0–1.0)."""
        self.opacity = max(0.0, min(1.0, opacity))
        return self

    # ── Rendering ───────────────────────────────────────────

    def render(self, canvas):
        """Draw this object onto the canvas. Override in subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement render()"
        )

    def get_render_color(self) -> tuple:
        """Return the RGBA color with opacity applied to the alpha channel."""
        r, g, b, a = self.color
        return (r, g, b, int(a * self.opacity))

    # ── Geometry helpers ────────────────────────────────────

    @property
    def center_x(self) -> int:
        """X coordinate of center. Override for shapes with width."""
        return int(self.x)

    @property
    def center_y(self) -> int:
        """Y coordinate of center. Override for shapes with height."""
        return int(self.y)

    # ── Bounds (layout engine support) ──────────────────────

    def get_bounds(self) -> Bounds:
        """Return bounding box as (x, y, width, height) where x,y is top-left.

        Subclasses with non-top-left position semantics (e.g. MathTex,
        center-aligned PixelText) MUST override this.
        """
        w = getattr(self, 'width', 0) or 0
        h = getattr(self, 'height', 0) or 0
        return Bounds(x=int(self.x), y=int(self.y), width=int(w), height=int(h))

    def fits_in(self, zone) -> bool:
        """Check if this object fits entirely within a Zone (center-based)."""
        b = self.get_bounds()
        zx = zone.x - zone.width // 2
        zy = zone.y - zone.height // 2
        return (b.x >= zx and b.y >= zy and
                b.x + b.width <= zx + zone.width and
                b.y + b.height <= zy + zone.height)

    def overflow_ratio(self, zone) -> float:
        """How much this object exceeds the zone. <=1.0 means it fits."""
        b = self.get_bounds()
        if b.width == 0 or b.height == 0:
            return 0.0
        w_ratio = b.width / zone.width if zone.width > 0 else float('inf')
        h_ratio = b.height / zone.height if zone.height > 0 else float('inf')
        return max(w_ratio, h_ratio)

    # ── Children (for grouped objects) ──────────────────────

    def add_child(self, child: "PObject") -> "PObject":
        """Add a child object (moves relative to parent)."""
        self._children.append(child)
        return self

    # ── Updaters (v4 Reactive Links) ───────────────────────

    def add_updater(self, updater) -> "PObject":
        """Add a per-frame updater callback.

        Usage::

            obj.add_updater(lambda obj, dt: setattr(obj, 'x', obj.x + 1))
            obj.add_updater(Link(source_obj, properties=["x", "y"]))

        Args:
            updater: A callable ``fn(obj, dt)`` called each frame.
        """
        self._updaters.append(updater)
        return self

    def remove_updater(self, updater) -> "PObject":
        """Remove a previously added updater."""
        if updater in self._updaters:
            self._updaters.remove(updater)
        return self

    def clear_updaters(self) -> "PObject":
        """Remove all updaters from this object."""
        self._updaters.clear()
        return self

    # ── Relative Positioning ──────────────────────────────────

    def relative_to(self, other: "PObject", position: str = "above",
                    offset: int = 10) -> "PObject":
        """Position this object relative to another.

        Args:
            other: The reference PObject.
            position: One of "above", "below", "left_of", "right_of",
                      "centered_on".
            offset: Pixel distance from the reference object.

        Usage::

            label.relative_to(circle, position="above", offset=10)
        """
        ow = getattr(other, 'width', 0) or 0
        oh = getattr(other, 'height', 0) or 0
        sw = getattr(self, 'width', 0) or 0
        sh = getattr(self, 'height', 0) or 0

        if position == "above":
            self.x = other.x + ow // 2 - sw // 2
            self.y = other.y - sh - offset
        elif position == "below":
            self.x = other.x + ow // 2 - sw // 2
            self.y = other.y + oh + offset
        elif position == "left_of":
            self.x = other.x - sw - offset
            self.y = other.y + oh // 2 - sh // 2
        elif position == "right_of":
            self.x = other.x + ow + offset
            self.y = other.y + oh // 2 - sh // 2
        elif position == "centered_on":
            self.x = other.x + ow // 2 - sw // 2
            self.y = other.y + oh // 2 - sh // 2
        return self

    # ── Animation Builder ──────────────────────────────────

    @property
    def animate(self) -> "_AnimationBuilder":
        """Fluent animation builder — Manim-style property animations.

        Usage::

            scene.play(obj.animate.move_to(200, 100).set_opacity(0.5), duration=1.0)
            scene.play(obj.animate.set_color("#FF004D"), duration=0.5)
        """
        return _AnimationBuilder(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"x={self.x}, y={self.y}, "
            f"color={self.color}, "
            f"opacity={self.opacity})"
        )


class _AnimationBuilder:
    """Proxy that records property changes and produces an Animation.

    Not instantiated directly — use ``obj.animate`` instead.
    """

    def __init__(self, target: "PObject"):
        self._target = target
        self._changes = []  # list of (property_name, value) or (method_name, args, kwargs)

    def move_to(self, x: int, y: int) -> "_AnimationBuilder":
        self._changes.append(("_move_to", (x, y)))
        return self

    def move_by(self, dx: int, dy: int) -> "_AnimationBuilder":
        self._changes.append(("_move_by", (dx, dy)))
        return self

    def set_opacity(self, opacity: float) -> "_AnimationBuilder":
        self._changes.append(("opacity", opacity))
        return self

    def set_color(self, color) -> "_AnimationBuilder":
        self._changes.append(("color", parse_color(color)))
        return self

    def scale(self, factor: float) -> "_AnimationBuilder":
        self._changes.append(("_scale", factor))
        return self

    def rotate(self, degrees: float) -> "_AnimationBuilder":
        self._changes.append(("_rotate", degrees))
        return self

    def interpolate(self, raw_alpha: float):
        """Called by scene.play() — interpolates all recorded changes."""
        alpha = max(0.0, min(1.0, raw_alpha))

        if not hasattr(self, '_started') or not self._started:
            self._started = True
            self._start_state = {
                'x': self._target.x,
                'y': self._target.y,
                'opacity': self._target.opacity,
                'color': self._target.color,
                'scale_x': self._target.scale_x,
                'scale_y': self._target.scale_y,
                'angle': getattr(self._target, 'angle', 0),
            }
            self._targets = {}
            self._targets['x'] = self._start_state['x']
            self._targets['y'] = self._start_state['y']
            self._targets['opacity'] = self._start_state['opacity']
            self._targets['color'] = self._start_state['color']
            self._targets['scale_x'] = self._start_state['scale_x']
            self._targets['scale_y'] = self._start_state['scale_y']
            self._targets['angle'] = self._start_state['angle']

            for change in self._changes:
                if change[0] == "_move_to":
                    self._targets['x'] = change[1][0]
                    self._targets['y'] = change[1][1]
                elif change[0] == "_move_by":
                    self._targets['x'] = self._start_state['x'] + change[1][0]
                    self._targets['y'] = self._start_state['y'] + change[1][1]
                elif change[0] == "opacity":
                    self._targets['opacity'] = change[1]
                elif change[0] == "color":
                    self._targets['color'] = change[1]
                elif change[0] == "_scale":
                    self._targets['scale_x'] = self._start_state['scale_x'] * change[1]
                    self._targets['scale_y'] = self._start_state['scale_y'] * change[1]
                elif change[0] == "_rotate":
                    self._targets['angle'] = self._start_state['angle'] + change[1]

        s = self._start_state
        t = self._targets
        a = alpha

        self._target.x = s['x'] + (t['x'] - s['x']) * a
        self._target.y = s['y'] + (t['y'] - s['y']) * a
        self._target.opacity = s['opacity'] + (t['opacity'] - s['opacity']) * a
        self._target.scale_x = s['scale_x'] + (t['scale_x'] - s['scale_x']) * a
        self._target.scale_y = s['scale_y'] + (t['scale_y'] - s['scale_y']) * a

        if t.get('angle') != s.get('angle'):
            self._target.angle = s['angle'] + (t['angle'] - s['angle']) * a

        if t['color'] != s['color']:
            sc, tc = s['color'], t['color']
            self._target.color = (
                int(sc[0] + (tc[0] - sc[0]) * a),
                int(sc[1] + (tc[1] - sc[1]) * a),
                int(sc[2] + (tc[2] - sc[2]) * a),
                int(sc[3] + (tc[3] - sc[3]) * a),
            )


# ═══════════════════════════════════════════════════════════
#  Reactive Animation Factories (v4)
# ═══════════════════════════════════════════════════════════

class Link:
    """Create an updater that makes an object follow another object's properties.

    Usage::

        # Shadow follows player with position delay
        shadow.add_updater(Link(player, delay=0.15, properties=["x", "y"]))

        # Label always above a target
        label.add_updater(Link(target, properties=["x"], offset_y=-15))

    Args:
        source: The PObject to follow.
        delay: Smoothing factor (0 = instant, 0.5 = half-speed follow).
        properties: List of property names to link ("x", "y", "opacity", etc.).
        offset_x: Constant X offset from source.
        offset_y: Constant Y offset from source.
    """

    def __init__(self, source: "PObject", delay: float = 0.0,
                 properties: list = None, offset_x: float = 0, offset_y: float = 0):
        self.source = source
        self.delay = max(0.0, min(0.99, delay))
        self.properties = properties or ["x", "y"]
        self.offset_x = offset_x
        self.offset_y = offset_y

    def __call__(self, obj, dt):
        for prop in self.properties:
            src_val = getattr(self.source, prop, 0)
            # Apply offsets for position properties
            if prop == "x":
                src_val += self.offset_x
            elif prop == "y":
                src_val += self.offset_y

            if self.delay > 0:
                # Smooth follow (exponential easing)
                current = getattr(obj, prop, 0)
                t = 1.0 - self.delay
                new_val = current + (src_val - current) * t
                setattr(obj, prop, new_val)
            else:
                setattr(obj, prop, src_val)

    @staticmethod
    def endpoints(source_a: "PObject", source_b: "PObject"):
        """Create an updater that keeps a Line connected between two objects.

        Usage::

            arrow = Line(0, 0, 0, 0, color="#FFEC27")
            arrow.add_updater(Link.endpoints(dot_a, dot_b))

        Returns:
            An updater function for a Line object.
        """
        def _update(obj, dt):
            obj.x1 = int(source_a.x)
            obj.y1 = int(source_a.y)
            obj.x2 = int(source_b.x)
            obj.y2 = int(source_b.y)
        return _update


class ReactTo:
    """Create an updater that applies a transform function based on a source.

    Usage::

        # Label positioned above target
        label.add_updater(ReactTo(target, lambda t: {"x": t.x, "y": t.y - 15}))

        # Scale based on another object's position
        indicator.add_updater(ReactTo(tracker, lambda t: {"scale_x": t.value / 100}))

    Args:
        source: The PObject to react to.
        transform_fn: A callable that takes the source and returns a dict
                       of {property_name: value} to set on the target.
    """

    def __init__(self, source, transform_fn):
        self.source = source
        self.transform_fn = transform_fn

    def __call__(self, obj, dt):
        result = self.transform_fn(self.source)
        if isinstance(result, dict):
            for prop, val in result.items():
                setattr(obj, prop, val)
