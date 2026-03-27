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
