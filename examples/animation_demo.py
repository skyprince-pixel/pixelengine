#!/usr/bin/env python3
"""
PixelEngine — Animation Demo

Demonstrates: MoveTo, FadeIn, FadeOut, Scale, ColorShift,
              AnimationGroup, easing functions, PixelText, TypeWriter
"""
from pixelengine import (
    Scene, PixelConfig, Rect, Circle, Line, Triangle,
    MoveTo, FadeIn, FadeOut, Scale, ColorShift, Blink,
    AnimationGroup, Sequence,
    PixelText, TypeWriter,
    ease_in, ease_out, ease_in_out, bounce, elastic,
)


class AnimationDemo(Scene):
    def construct(self):
        # ── Title with TypeWriter ─────────────────────────
        title = PixelText(
            "PIXELENGINE", x=128, y=10,
            color="#FFD700", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(title)
        self.play(TypeWriter(title), duration=1.5)
        self.wait(0.5)

        # ── Subtitle ─────────────────────────────────────
        sub = PixelText(
            "ANIMATION DEMO", x=128, y=30,
            color="#C2C3C7", align="center", max_chars=0,
        )
        self.add(sub)
        self.play(TypeWriter(sub), duration=1.0)
        self.wait(0.5)

        # ── FadeIn a rectangle ────────────────────────────
        rect = Rect(30, 20, x=20, y=60, color="#FF004D")
        self.add(rect)
        self.play(FadeIn(rect), duration=0.5)
        self.wait(0.3)

        # ── Move rectangle with ease_out ──────────────────
        self.play(MoveTo(rect, x=200, y=60, easing=ease_out), duration=1.0)
        self.wait(0.3)

        # ── Move rectangle back with bounce ───────────────
        self.play(MoveTo(rect, x=20, y=60, easing=bounce), duration=1.0)
        self.wait(0.3)

        # ── FadeIn a circle ───────────────────────────────
        circle = Circle(12, x=110, y=80, color="#00E436")
        self.add(circle)
        self.play(FadeIn(circle, easing=ease_in), duration=0.5)

        # ── AnimationGroup: move circle + color shift ─────
        self.play(
            AnimationGroup(
                MoveTo(circle, x=200, y=80, easing=ease_in_out),
                ColorShift(circle, to_color="#29ADFF"),
            ),
            duration=1.5,
        )
        self.wait(0.3)

        # ── Blink the rect ───────────────────────────────
        self.play(Blink(rect, blinks=4), duration=1.0)
        self.wait(0.3)

        # ── FadeOut everything ────────────────────────────
        self.play(
            AnimationGroup(
                FadeOut(rect),
                FadeOut(circle),
                FadeOut(title),
                FadeOut(sub),
            ),
            duration=1.0,
        )
        self.wait(0.5)

        # ── Final message ────────────────────────────────
        end_text = PixelText(
            "PIXEL ART\nVIDEOS!", x=128, y=50,
            color="#FFEC27", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(end_text)
        self.play(TypeWriter(end_text), duration=1.5)
        self.wait(2.0)


if __name__ == "__main__":
    scene = AnimationDemo(PixelConfig.landscape())
    scene.render("animation_demo.mp4")
    print("Done! Open animation_demo.mp4")
