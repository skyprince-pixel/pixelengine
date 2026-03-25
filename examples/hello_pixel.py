#!/usr/bin/env python3
"""
PixelEngine — Hello World Example

Draws colored shapes on a dark canvas and renders to MP4.
Demonstrates: Rect, Circle, Line, Triangle, wait()
"""
from pixelengine import Scene, PixelConfig, Rect, Circle, Line, Triangle


class HelloPixel(Scene):
    def construct(self):
        # ── Frame 1: Red rectangle ──────────────────────────
        rect = Rect(40, 30, x=20, y=20, color="#FF004D")
        self.add(rect)
        self.wait(1.0)

        # ── Frame 2: Add green circle ──────────────────────
        circle = Circle(15, x=100, y=50, color="#00E436")
        self.add(circle)
        self.wait(1.0)

        # ── Frame 3: Add blue diagonal line ────────────────
        line = Line(10, 120, 240, 30, color="#29ADFF")
        self.add(line)
        self.wait(1.0)

        # ── Frame 4: Add yellow triangle ───────────────────
        tri = Triangle(
            [(150, 20), (130, 60), (170, 60)],
            color="#FFEC27",
        )
        self.add(tri)
        self.wait(1.0)

        # ── Frame 5: Orange outlined rectangle ─────────────
        outline = Rect(60, 40, x=180, y=90, color="#FFA300", filled=False, border_width=2)
        self.add(outline)
        self.wait(1.0)

        # ── Hold final composition ─────────────────────────
        self.wait(2.0)


if __name__ == "__main__":
    scene = HelloPixel(PixelConfig.landscape())
    scene.render("hello_pixel.mp4")
    print("Done! Open hello_pixel.mp4 to see the result.")
