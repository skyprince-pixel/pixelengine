"""Layout templates for consistent video composition.

Provides named zones, safe margins, and helper methods so AI agents
never have to guess coordinate positions when building videos.
"""

from collections import namedtuple

Zone = namedtuple("Zone", ["x", "y", "width", "height"])


class Layout:
    """Pre-built layout templates with named zones for video composition.

    Usage::

        from pixelengine.layout import Layout

        L = Layout.portrait()
        title = PixelText("HELLO", x=L.TITLE_ZONE.x, y=L.TITLE_ZONE.y)
        main_obj = Circle(radius=20, x=L.MAIN_ZONE.x, y=L.MAIN_ZONE.y)
    """

    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        cx = canvas_width // 2
        cy = canvas_height // 2

        # ── Safe margins (10% inset on each side) ──────────────
        margin_x = max(10, int(canvas_width * 0.08))
        margin_y = max(15, int(canvas_height * 0.06))
        self.SAFE_LEFT = margin_x
        self.SAFE_RIGHT = canvas_width - margin_x
        self.SAFE_TOP = margin_y
        self.SAFE_BOTTOM = canvas_height - margin_y

        safe_w = self.SAFE_RIGHT - self.SAFE_LEFT
        safe_h = self.SAFE_BOTTOM - self.SAFE_TOP

        # ── Named zones ────────────────────────────────────────
        # TITLE: top ~12% of safe area
        title_h = max(20, int(safe_h * 0.12))
        self.TITLE_ZONE = Zone(
            x=cx,
            y=self.SAFE_TOP + title_h // 2,
            width=safe_w,
            height=title_h,
        )

        # SUBTITLE: just below title, ~8%
        sub_h = max(15, int(safe_h * 0.08))
        self.SUBTITLE_ZONE = Zone(
            x=cx,
            y=self.TITLE_ZONE.y + title_h // 2 + sub_h // 2 + 5,
            width=safe_w,
            height=sub_h,
        )

        # MAIN: center stage, ~50% of safe area
        main_h = max(60, int(safe_h * 0.50))
        self.MAIN_ZONE = Zone(
            x=cx,
            y=cy,
            width=safe_w,
            height=main_h,
        )

        # LOWER THIRD: classic lower-third overlay, ~15%
        lt_h = max(25, int(safe_h * 0.15))
        self.LOWER_THIRD = Zone(
            x=cx,
            y=self.SAFE_BOTTOM - lt_h - int(safe_h * 0.08),
            width=safe_w,
            height=lt_h,
        )

        # FOOTER: bottom strip
        footer_h = max(15, int(safe_h * 0.08))
        self.FOOTER_ZONE = Zone(
            x=cx,
            y=self.SAFE_BOTTOM - footer_h // 2,
            width=safe_w,
            height=footer_h,
        )

    # ── Factory presets ────────────────────────────────────────

    @classmethod
    def portrait(cls):
        """270×480 — YouTube Shorts layout."""
        return cls(270, 480)

    @classmethod
    def landscape(cls):
        """480×270 — Standard YouTube layout."""
        return cls(480, 270)

    @classmethod
    def retro(cls):
        """256×144 — Classic 8-bit layout."""
        return cls(256, 144)

    @classmethod
    def square(cls):
        """384×384 — Square format layout."""
        return cls(384, 384)

    # ── Helpers ────────────────────────────────────────────────

    def center(self):
        """Return (x, y) of canvas center."""
        return (self.canvas_width // 2, self.canvas_height // 2)

    def full_bg(self):
        """Return (width, height, x, y) for a full-canvas background Rect."""
        return (self.canvas_width, self.canvas_height, 0, 0)

    def grid(self, rows, cols, zone=None):
        """Return a list of (x, y) positions arranged in a grid within a zone.

        Args:
            rows: Number of rows.
            cols: Number of columns.
            zone: A Zone namedtuple. Defaults to MAIN_ZONE.

        Returns:
            List of (x, y) tuples, row-major order.
        """
        if zone is None:
            zone = self.MAIN_ZONE

        positions = []
        for r in range(rows):
            for c in range(cols):
                px = zone.x - zone.width // 2 + int(zone.width * (c + 0.5) / cols)
                py = zone.y - zone.height // 2 + int(zone.height * (r + 0.5) / rows)
                positions.append((px, py))
        return positions

    def stack(self, n, zone=None, spacing=None):
        """Return a list of (x, y) positions stacked vertically within a zone.

        Args:
            n: Number of items to stack.
            zone: A Zone namedtuple. Defaults to MAIN_ZONE.
            spacing: Pixels between each item. Auto-calculated if None.

        Returns:
            List of (x, y) tuples, top to bottom.
        """
        if zone is None:
            zone = self.MAIN_ZONE

        if spacing is None:
            spacing = zone.height // max(n, 1)

        total_height = spacing * (n - 1)
        start_y = zone.y - total_height // 2

        return [(zone.x, start_y + i * spacing) for i in range(n)]

    def horizontal(self, n, zone=None, spacing=None):
        """Return a list of (x, y) positions arranged horizontally within a zone.

        Args:
            n: Number of items.
            zone: A Zone namedtuple. Defaults to MAIN_ZONE.
            spacing: Pixels between each item. Auto-calculated if None.

        Returns:
            List of (x, y) tuples, left to right.
        """
        if zone is None:
            zone = self.MAIN_ZONE

        if spacing is None:
            spacing = zone.width // max(n, 1)

        total_width = spacing * (n - 1)
        start_x = zone.x - total_width // 2

        return [(start_x + i * spacing, zone.y) for i in range(n)]

    def __repr__(self):
        return (
            f"Layout({self.canvas_width}x{self.canvas_height})\n"
            f"  TITLE_ZONE:    {self.TITLE_ZONE}\n"
            f"  SUBTITLE_ZONE: {self.SUBTITLE_ZONE}\n"
            f"  MAIN_ZONE:     {self.MAIN_ZONE}\n"
            f"  LOWER_THIRD:   {self.LOWER_THIRD}\n"
            f"  FOOTER_ZONE:   {self.FOOTER_ZONE}\n"
            f"  Safe area:     ({self.SAFE_LEFT}, {self.SAFE_TOP}) → "
            f"({self.SAFE_RIGHT}, {self.SAFE_BOTTOM})"
        )


# ═══════════════════════════════════════════════════════════
#  Advanced Layout Engine (pretext-inspired two-phase model)
# ═══════════════════════════════════════════════════════════

class LayoutEngine:
    """Two-phase layout engine: measure objects, then place them.

    Handles auto-scaling, zone-fitting, and constraint validation.
    Eliminates all manual coordinate math for AI agents.

    Usage::

        L = Layout.landscape()
        engine = LayoutEngine(L)

        eq = MathTex(r"E=mc^2", color="#FFEC27")
        engine.place_in_zone(eq, L.MAIN_ZONE)  # auto-scales and centers
    """

    def __init__(self, layout: Layout):
        self.layout = layout
        self.cw = layout.canvas_width
        self.ch = layout.canvas_height

    # ── Core: Place a single object in a zone ────────────���

    def place_in_zone(self, obj, zone: Zone, padding: float = 0.1,
                      align: str = "center", valign: str = "center"):
        """Place a single object within a zone, auto-scaling if needed.

        Args:
            obj: Any PObject instance.
            zone: Target Zone namedtuple (x,y = center).
            padding: Fraction of zone reserved as padding (0.1 = 10% each side).
            align: "left", "center", "right" horizontal alignment.
            valign: "top", "center", "bottom" vertical alignment.
        """
        usable_w = int(zone.width * (1 - 2 * padding))
        usable_h = int(zone.height * (1 - 2 * padding))

        # ── Fit phase: auto-scale oversized objects ──
        self._fit_object(obj, usable_w, usable_h)

        # ── Position phase ──
        b = obj.get_bounds()
        zone_left = zone.x - zone.width // 2
        zone_top = zone.y - zone.height // 2

        # Horizontal
        if align == "left":
            target_x = zone_left + int(zone.width * padding)
        elif align == "right":
            target_x = zone_left + zone.width - int(zone.width * padding) - b.width
        else:  # center
            target_x = zone.x - b.width // 2

        # Vertical
        if valign == "top":
            target_y = zone_top + int(zone.height * padding)
        elif valign == "bottom":
            target_y = zone_top + zone.height - int(zone.height * padding) - b.height
        else:  # center
            target_y = zone.y - b.height // 2

        # Apply position based on object's alignment semantics
        self._set_position(obj, target_x, target_y, b)

    def _fit_object(self, obj, max_w: int, max_h: int):
        """Auto-scale an object to fit within max_w x max_h."""
        cls_name = type(obj).__name__

        if cls_name == "MathTex":
            obj.max_width = max_w
            obj.max_height = max_h
            obj._auto_fit()
        elif cls_name == "PixelText":
            if obj.width > max_w:
                from pixelengine.text import wrap_text
                obj.text = wrap_text(obj.text, max_w, obj.font_size, obj.scale)
            # If still too tall after wrapping, reduce scale
            while obj.height > max_h and obj.scale > 1:
                obj.scale -= 1
                if obj.max_width is not None or obj.width > max_w:
                    from pixelengine.text import wrap_text
                    obj.text = wrap_text(obj.text, max_w, obj.font_size, obj.scale)
        else:
            b = obj.get_bounds()
            if b.width > 0 and b.height > 0:
                ratio = min(max_w / b.width, max_h / b.height)
                if ratio < 1.0:
                    obj.scale_x *= ratio
                    obj.scale_y *= ratio

    def _set_position(self, obj, target_x: int, target_y: int, bounds):
        """Set position accounting for the object's alignment semantics."""
        cls_name = type(obj).__name__

        if cls_name == "MathTex":
            # MathTex x,y is center-based (for align="center")
            if obj.align == "center":
                obj.x = target_x + bounds.width // 2
                obj.y = target_y + bounds.height // 2
            elif obj.align == "right":
                obj.x = target_x + bounds.width
                obj.y = target_y + bounds.height // 2
            else:
                obj.x = target_x
                obj.y = target_y + bounds.height // 2
        elif cls_name == "PixelText":
            if obj.align == "center":
                obj.x = target_x + bounds.width // 2
                obj.y = target_y
            elif obj.align == "right":
                obj.x = target_x + bounds.width
                obj.y = target_y
            else:
                obj.x = target_x
                obj.y = target_y
        else:
            # Top-left based objects (Rect, etc.)
            obj.x = target_x
            obj.y = target_y

    # ── Fit multiple items into a zone ────────────────────

    def fit_content(self, items: list, zone: Zone, spacing: int = 8,
                    direction: str = "vertical"):
        """Fit multiple objects into a zone as a stack.

        Auto-scales each item, then arranges with spacing.
        Returns a VStack or HStack positioned at zone center.

        Args:
            items: List of PObject instances.
            zone: Target Zone.
            spacing: Pixels between items.
            direction: "vertical" or "horizontal".
        """
        from pixelengine.group import VStack, HStack

        if not items:
            return VStack([], x=zone.x, y=zone.y)

        usable_w = int(zone.width * 0.9)
        usable_h = int(zone.height * 0.9)
        total_spacing = spacing * (len(items) - 1)

        if direction == "vertical":
            per_item_h = max(10, (usable_h - total_spacing) // len(items))
            for item in items:
                self._fit_object(item, usable_w, per_item_h)
            stack = VStack(items, spacing=spacing, align="center")
        else:
            per_item_w = max(10, (usable_w - total_spacing) // len(items))
            for item in items:
                self._fit_object(item, per_item_w, usable_h)
            stack = HStack(items, spacing=spacing, align="center")

        stack.move_to(zone.x, zone.y)
        return stack

    # ── Full-screen auto-layout ──────────────────────────

    def auto_layout(self, title: str = None, subtitle: str = None,
                    content: list = None, footer: str = None,
                    title_color: str = "#FFEC27",
                    subtitle_color: str = "#C2C3C7",
                    content_color: str = "#FFFFFF",
                    footer_color: str = "#5F574F") -> list:
        """Auto-layout a full screen with title, subtitle, content, footer.

        Returns a list of positioned PObjects for scene.add().
        """
        from pixelengine.text import PixelText

        L = self.layout
        objects = []

        if title:
            t = PixelText(title, color=title_color, scale=2, align="center",
                          max_width=int(L.TITLE_ZONE.width * 0.9))
            self.place_in_zone(t, L.TITLE_ZONE)
            objects.append(t)

        if subtitle:
            s = PixelText(subtitle, color=subtitle_color, scale=1,
                          align="center",
                          max_width=int(L.SUBTITLE_ZONE.width * 0.9))
            self.place_in_zone(s, L.SUBTITLE_ZONE)
            objects.append(s)

        if content:
            stack = self.fit_content(content, L.MAIN_ZONE, spacing=10)
            objects.append(stack)

        if footer:
            f = PixelText(footer, color=footer_color, scale=1,
                          align="center",
                          max_width=int(L.FOOTER_ZONE.width * 0.9))
            self.place_in_zone(f, L.FOOTER_ZONE)
            objects.append(f)

        return objects

    # ── Pre-render validation ────────────────────────────

    def validate_layout(self, objects: list) -> list:
        """Check all objects for overflow BEFORE rendering.

        Returns list of issue dicts with suggestions.
        """
        issues = []
        for obj in objects:
            b = obj.get_bounds()
            cls = type(obj).__name__
            if b.x < 0 or b.y < 0 or b.x + b.width > self.cw or b.y + b.height > self.ch:
                issues.append({
                    "type": "OUT_OF_BOUNDS",
                    "object": cls,
                    "bounds": {"x": b.x, "y": b.y, "w": b.width, "h": b.height},
                    "canvas": {"w": self.cw, "h": self.ch},
                    "severity": "error",
                    "suggestion": f"Use engine.place_in_zone({cls.lower()}, zone) to auto-fit",
                })
        return issues


# ═══════════════════════════════════════════════════════════
#  Layout Presets — professional layouts for common patterns
# ═══════════════════════════════════════════════════════════

class LayoutPresets:
    """Pre-built layout configurations for common video patterns.

    Usage::

        engine = LayoutEngine(Layout.landscape())
        objects = LayoutPresets.equation_explainer(
            engine, equation=r"E = mc^2",
            explanation="ENERGY EQUALS MASS TIMES SPEED OF LIGHT SQUARED",
        )
        for obj in objects: scene.add(obj)
    """

    @staticmethod
    def equation_explainer(engine: LayoutEngine, equation: str,
                           explanation: str, title: str = None,
                           eq_color: str = "#FFEC27",
                           text_color: str = "#C2C3C7",
                           title_color: str = "#00E436") -> list:
        """Large equation top-center, explanation text below."""
        from pixelengine.mathtex import MathTex
        from pixelengine.text import PixelText

        L = engine.layout
        objects = []

        if title:
            t = PixelText(title, color=title_color, scale=1, align="center",
                          max_width=int(L.TITLE_ZONE.width * 0.9))
            engine.place_in_zone(t, L.TITLE_ZONE)
            objects.append(t)

        # Equation in upper portion of MAIN_ZONE
        eq_zone = Zone(
            x=L.MAIN_ZONE.x,
            y=L.MAIN_ZONE.y - L.MAIN_ZONE.height // 6,
            width=L.MAIN_ZONE.width,
            height=int(L.MAIN_ZONE.height * 0.55),
        )
        eq = MathTex(equation, color=eq_color,
                     max_width=int(eq_zone.width * 0.85),
                     max_height=int(eq_zone.height * 0.85))
        engine.place_in_zone(eq, eq_zone)
        objects.append(eq)

        # Explanation in lower portion of MAIN_ZONE
        expl_zone = Zone(
            x=L.MAIN_ZONE.x,
            y=L.MAIN_ZONE.y + L.MAIN_ZONE.height // 3,
            width=L.MAIN_ZONE.width,
            height=int(L.MAIN_ZONE.height * 0.35),
        )
        expl = PixelText(explanation, color=text_color, scale=1,
                         align="center",
                         max_width=int(expl_zone.width * 0.9))
        engine.place_in_zone(expl, expl_zone)
        objects.append(expl)

        return objects

    @staticmethod
    def comparison(engine: LayoutEngine, left_items: list,
                   right_items: list, left_title: str = "",
                   right_title: str = "",
                   left_color: str = "#FF004D",
                   right_color: str = "#29ADFF") -> list:
        """Side-by-side comparison with optional titles."""
        from pixelengine.text import PixelText
        from pixelengine.shapes import Line

        L = engine.layout
        zone = L.MAIN_ZONE
        half_w = zone.width // 2 - 8
        objects = []

        left_zone = Zone(
            x=zone.x - zone.width // 4,
            y=zone.y,
            width=half_w,
            height=zone.height,
        )
        right_zone = Zone(
            x=zone.x + zone.width // 4,
            y=zone.y,
            width=half_w,
            height=zone.height,
        )

        # Divider line
        div = Line(zone.x, zone.y - zone.height // 2 + 5,
                   zone.x, zone.y + zone.height // 2 - 5,
                   color="#5F574F")
        objects.append(div)

        if left_title:
            lt = PixelText(left_title, color=left_color, scale=1,
                           align="center")
            lt_zone = Zone(left_zone.x, left_zone.y - left_zone.height // 3,
                           left_zone.width, 20)
            engine.place_in_zone(lt, lt_zone)
            objects.append(lt)

        if right_title:
            rt = PixelText(right_title, color=right_color, scale=1,
                           align="center")
            rt_zone = Zone(right_zone.x, right_zone.y - right_zone.height // 3,
                           right_zone.width, 20)
            engine.place_in_zone(rt, rt_zone)
            objects.append(rt)

        # Fit left content
        if left_items:
            content_zone = Zone(left_zone.x, left_zone.y + 5,
                                left_zone.width, int(left_zone.height * 0.6))
            left_stack = engine.fit_content(left_items, content_zone, spacing=6)
            objects.append(left_stack)

        # Fit right content
        if right_items:
            content_zone = Zone(right_zone.x, right_zone.y + 5,
                                right_zone.width, int(right_zone.height * 0.6))
            right_stack = engine.fit_content(right_items, content_zone, spacing=6)
            objects.append(right_stack)

        return objects

    @staticmethod
    def step_by_step(engine: LayoutEngine, steps: list,
                     title: str = None,
                     step_color: str = "#FFFFFF",
                     num_color: str = "#FFEC27",
                     title_color: str = "#00E436") -> list:
        """Numbered vertical list of steps."""
        from pixelengine.text import PixelText

        L = engine.layout
        objects = []

        if title:
            t = PixelText(title, color=title_color, scale=2, align="center",
                          max_width=int(L.TITLE_ZONE.width * 0.9))
            engine.place_in_zone(t, L.TITLE_ZONE)
            objects.append(t)

        max_w = int(L.MAIN_ZONE.width * 0.85)
        step_items = []
        for i, step in enumerate(steps, 1):
            txt = PixelText(f"{i}. {step}", color=step_color, scale=1,
                            align="left", max_width=max_w)
            step_items.append(txt)

        if step_items:
            stack = engine.fit_content(step_items, L.MAIN_ZONE, spacing=6)
            objects.append(stack)

        return objects

    @staticmethod
    def chart_with_title(engine: LayoutEngine, chart,
                         title: str, subtitle: str = None,
                         title_color: str = "#FFEC27",
                         subtitle_color: str = "#C2C3C7") -> list:
        """Title on top, chart centered below."""
        from pixelengine.text import PixelText

        L = engine.layout
        objects = []

        t = PixelText(title, color=title_color, scale=2, align="center",
                      max_width=int(L.TITLE_ZONE.width * 0.9))
        engine.place_in_zone(t, L.TITLE_ZONE)
        objects.append(t)

        if subtitle:
            s = PixelText(subtitle, color=subtitle_color, scale=1,
                          align="center",
                          max_width=int(L.SUBTITLE_ZONE.width * 0.9))
            engine.place_in_zone(s, L.SUBTITLE_ZONE)
            objects.append(s)

        engine.place_in_zone(chart, L.MAIN_ZONE, padding=0.05)
        objects.append(chart)

        return objects

    @staticmethod
    def definition(engine: LayoutEngine, term: str,
                   definition_text: str, equation: str = None,
                   term_color: str = "#FFEC27",
                   def_color: str = "#C2C3C7",
                   eq_color: str = "#FFEC27") -> list:
        """Term as title, definition wrapped, optional equation."""
        from pixelengine.mathtex import MathTex
        from pixelengine.text import PixelText

        L = engine.layout
        objects = []

        t = PixelText(term, color=term_color, scale=2, align="center",
                      max_width=int(L.TITLE_ZONE.width * 0.9))
        engine.place_in_zone(t, L.TITLE_ZONE)
        objects.append(t)

        content_items = []
        if equation:
            eq = MathTex(equation, color=eq_color,
                         max_width=int(L.MAIN_ZONE.width * 0.85))
            content_items.append(eq)

        defn = PixelText(definition_text, color=def_color, scale=1,
                         align="center",
                         max_width=int(L.MAIN_ZONE.width * 0.85))
        content_items.append(defn)

        if content_items:
            stack = engine.fit_content(content_items, L.MAIN_ZONE, spacing=12)
            objects.append(stack)

        return objects
