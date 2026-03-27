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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"x={self.x}, y={self.y}, "
            f"color={self.color}, "
            f"opacity={self.opacity})"
        )
