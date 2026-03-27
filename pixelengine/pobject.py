"""PixelEngine PObject — base class for all pixel objects."""
from pixelengine.color import parse_color


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
        self._children: list = []
        self._updaters: list = []        # Per-frame update callbacks: fn(obj, dt)

        # Lighting interaction
        self.casts_shadow: bool = False   # Whether this object casts shadows
        self.receives_light: bool = True  # Whether lighting affects this object
        self.shadow_opacity: float = 0.4  # Shadow darkness (0.0–1.0)

        # Per-object quality control
        self.render_quality: float = 1.0  # 0.25=chunky, 1.0=normal, 2.0=smooth

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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"x={self.x}, y={self.y}, "
            f"color={self.color}, "
            f"opacity={self.opacity})"
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
