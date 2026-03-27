"""PixelEngine MathTex — render LaTeX equations as pixel-art objects.

Uses matplotlib's built-in ``mathtext`` parser to rasterize LaTeX strings
into crisp bitmap images.  No external LaTeX installation required.

Classes:
    MathTex — A PObject that displays a LaTeX math expression.

Usage::

    from pixelengine import MathTex, Create

    eq = MathTex(r"E = mc^2", x=240, y=135, color="#FFEC27", scale=2.0)
    scene.add(eq)
    scene.play(Create(eq), duration=1.5)
"""
import io
import numpy as np
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color

# matplotlib is a core dependency as of v0.7.0
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


class MathTex(PObject):
    """Render a LaTeX math expression as a pixel-art PObject.

    The expression is rasterized once at creation time and cached as a
    PIL Image.  Supports ``Create()``, ``FadeIn()``, and all standard
    PObject animations.

    Args:
        tex: LaTeX math string (e.g. ``r"\\frac{1}{2}"``, ``r"E=mc^2"``).
        x, y: Position (center of the rendered expression).
        color: Foreground colour for the equation text.
        scale: Size multiplier (1.0 = default matplotlib DPI, 2.0 = 2×).
        dpi: Base rendering DPI before scale is applied.
        align: ``"center"`` (default), ``"left"``, or ``"right"``.

    Usage::

        eq = MathTex(r"\\int_0^1 x^2\\,dx = \\frac{1}{3}",
                     x=240, y=135, color="#FFEC27", scale=1.5)
        scene.add(eq)
        scene.play(Create(eq), duration=2.0)
    """

    def __init__(self, tex: str, x: int = 0, y: int = 0,
                 color: str = "#FFFFFF", scale: float = 1.0,
                 dpi: int = 120, align: str = "center"):
        super().__init__(x=x, y=y, color=color)
        self.tex = tex
        self.scale = scale
        self.dpi = dpi
        self.align = align
        self._rendered: Image.Image | None = None
        self._render_tex()

    # ── Internal rendering ──────────────────────────────────

    def _render_tex(self):
        """Rasterize the LaTeX string into a PIL Image."""
        effective_dpi = int(self.dpi * self.scale)
        fg_color = self.get_render_color()
        # Normalize to 0-1 for matplotlib
        fg_rgb = (fg_color[0] / 255.0, fg_color[1] / 255.0,
                  fg_color[2] / 255.0)

        # Use matplotlib figure for rendering
        fig, ax = plt.subplots(figsize=(0.01, 0.01), dpi=effective_dpi)
        ax.set_axis_off()
        fig.patch.set_alpha(0.0)

        # Render the math text
        text_obj = ax.text(
            0.5, 0.5, f"${self.tex}$",
            fontsize=14 * self.scale,
            color=fg_rgb,
            ha="center", va="center",
            transform=ax.transAxes,
        )

        # Tight bounding box
        fig.canvas.draw()
        bbox = text_obj.get_window_extent(fig.canvas.get_renderer())
        # Add small padding
        pad = max(2, int(4 * self.scale))
        bbox = bbox.expanded(1.15, 1.25)

        fig.set_size_inches(bbox.width / effective_dpi,
                            bbox.height / effective_dpi)
        ax.set_position([0, 0, 1, 1])

        # Render to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=effective_dpi,
                    transparent=True, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)

        buf.seek(0)
        img = Image.open(buf).convert("RGBA")

        # Threshold to crisp pixel art: any pixel with alpha > 50 becomes
        # fully solid foreground color; the rest become transparent.
        arr = np.array(img)
        alpha_mask = arr[:, :, 3] > 50

        # Tint all visible pixels to the desired color
        result = np.zeros_like(arr)
        result[alpha_mask, 0] = fg_color[0]
        result[alpha_mask, 1] = fg_color[1]
        result[alpha_mask, 2] = fg_color[2]
        result[alpha_mask, 3] = 255
        # Keep transparent pixels transparent
        result[~alpha_mask, 3] = 0

        self._rendered = Image.fromarray(result, mode="RGBA")
        self.width = self._rendered.width
        self.height = self._rendered.height

    # ── PObject rendering ───────────────────────────────────

    def render(self, canvas):
        if not self.visible or self._rendered is None:
            return

        draw_alpha = getattr(self, '_create_progress', 1.0)
        if draw_alpha <= 0:
            return

        img = self._rendered.copy()

        # Apply opacity
        if self.opacity < 1.0 or draw_alpha < 1.0:
            arr = np.array(img)
            arr[:, :, 3] = (arr[:, :, 3].astype(np.float32)
                            * self.opacity * draw_alpha).astype(np.uint8)
            img = Image.fromarray(arr, "RGBA")

        # Create progress: reveal left-to-right
        if draw_alpha < 0.99:
            w = img.width
            crop_w = max(1, int(w * draw_alpha))
            cropped = img.crop((0, 0, crop_w, img.height))
            full = Image.new("RGBA", img.size, (0, 0, 0, 0))
            full.paste(cropped, (0, 0))
            img = full

        # Position based on alignment
        if self.align == "center":
            blit_x = int(self.x - img.width / 2)
            blit_y = int(self.y - img.height / 2)
        elif self.align == "right":
            blit_x = int(self.x - img.width)
            blit_y = int(self.y - img.height / 2)
        else:  # left
            blit_x = int(self.x)
            blit_y = int(self.y - img.height / 2)

        canvas.blit(img, blit_x, blit_y)

    # ── Utilities ───────────────────────────────────────────

    def set_tex(self, tex: str):
        """Update the LaTeX expression and re-render."""
        self.tex = tex
        self._render_tex()
        return self

    @property
    def center_x(self) -> int:
        return int(self.x)

    @property
    def center_y(self) -> int:
        return int(self.y)

    def __repr__(self):
        return f"MathTex({self.tex!r}, x={self.x}, y={self.y})"
