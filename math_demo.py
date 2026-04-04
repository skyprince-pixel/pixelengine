#!/usr/bin/env python3
"""Math Demo — an educational pixel art video using the advanced layout engine."""
import math
from pixelengine import *


class MathDemo(Scene):
    def construct(self):
        self.set_background("#1D2B53")
        L = Layout.landscape()
        engine = LayoutEngine(L)

        # ─── INTRO ───────────────────────────────────────────
        intro = engine.auto_layout(
            title="THE BEAUTY OF MATH",
            subtitle="a pixelengine demo",
        )
        for obj in intro:
            self.add(obj)
        self.play(TypeWriter(intro[0]), duration=1.5)
        if len(intro) > 1:
            self.play(FadeIn(intro[1]), duration=0.5)
        self.play_voiceover("Welcome to the beauty of math. Let's explore some of the most elegant equations ever discovered.", speed=1.1)
        self.play(*[FadeOut(o) for o in intro], duration=0.5)

        # ─── PART 1: PYTHAGOREAN THEOREM ─────────────────────
        header1 = PixelText("1. PYTHAGOREAN THEOREM", color="#00E436",
                            scale=1, align="center")
        engine.place_in_zone(header1, L.TITLE_ZONE)
        self.add(header1)
        self.play(FadeIn(header1), duration=0.3)

        # Triangle on the left side
        tri = Triangle([(100, 200), (200, 200), (100, 130)], color="#29ADFF")
        self.add(tri)
        self.play(Create(tri), duration=1.0)

        lbl_a = PixelText("a=3", x=88, y=163, color="#FF004D", scale=1)
        lbl_b = PixelText("b=4", x=140, y=205, color="#FF004D", scale=1)
        lbl_c = PixelText("c=5", x=155, y=153, color="#FFEC27", scale=1)
        self.add(lbl_a, lbl_b, lbl_c)
        self.play(FadeIn(lbl_a), FadeIn(lbl_b), FadeIn(lbl_c), duration=0.5)

        # Equations on the right — auto-scaled to fit
        eq_zone = Zone(x=360, y=100, width=200, height=50)
        eq1 = MathTex(r"a^2 + b^2 = c^2", color="#FFEC27",
                      max_width=190, max_height=45)
        engine.place_in_zone(eq1, eq_zone)
        self.add(eq1)
        self.play(Create(eq1), duration=1.0)

        self.play_voiceover("The Pythagorean theorem tells us that in a right triangle, a squared plus b squared equals c squared.", speed=1.1)

        eq1b_zone = Zone(x=360, y=150, width=200, height=35)
        eq1b = MathTex(r"3^2 + 4^2 = 5^2", color="#C2C3C7",
                       max_width=190, max_height=30)
        engine.place_in_zone(eq1b, eq1b_zone)
        self.add(eq1b)
        self.play(FadeIn(eq1b), duration=0.5)

        eq1c_zone = Zone(x=360, y=190, width=200, height=35)
        eq1c = MathTex(r"9 + 16 = 25", color="#C2C3C7",
                       max_width=190, max_height=30)
        engine.place_in_zone(eq1c, eq1c_zone)
        self.add(eq1c)
        self.play(FadeIn(eq1c), duration=0.5)

        self.play_voiceover("Three squared is nine, four squared is sixteen, and together they give us twenty five, which is five squared. Beautiful!", speed=1.1)

        self.play(FadeOut(header1), FadeOut(tri), FadeOut(lbl_a), FadeOut(lbl_b),
                  FadeOut(lbl_c), FadeOut(eq1), FadeOut(eq1b), FadeOut(eq1c), duration=0.5)

        # ─── PART 2: EULER'S IDENTITY ────────────────────────
        header2 = PixelText("2. EULER'S IDENTITY", color="#00E436",
                            scale=1, align="center")
        engine.place_in_zone(header2, L.TITLE_ZONE)
        self.add(header2)
        self.play(FadeIn(header2), duration=0.3)

        euler = MathTex(r"e^{i\pi} + 1 = 0", color="#FFEC27",
                        max_width=int(L.MAIN_ZONE.width * 0.8),
                        max_height=int(L.MAIN_ZONE.height * 0.5))
        euler_zone = Zone(x=L.MAIN_ZONE.x, y=L.MAIN_ZONE.y - 20,
                          width=L.MAIN_ZONE.width, height=int(L.MAIN_ZONE.height * 0.5))
        engine.place_in_zone(euler, euler_zone)
        self.add(euler)
        self.play(Create(euler), duration=1.5)

        self.play_voiceover("Euler's identity is often called the most beautiful equation in all of mathematics. It connects five fundamental constants: e, i, pi, one, and zero.", speed=1.1)

        # Constants labels — spread across lower third
        labels = [
            ("e = 2.718...", "#FF004D"),
            ("i = sqrt(-1)", "#29ADFF"),
            ("pi = 3.14...", "#00E436"),
            ("1", "#FFA300"),
            ("0", "#FFEC27"),
        ]
        positions = L.horizontal(5, zone=L.LOWER_THIRD)
        label_objs = []
        for (txt, lc), (lx, ly) in zip(labels, positions):
            lbl = PixelText(txt, x=lx, y=ly, color=lc, scale=1, align="center")
            label_objs.append(lbl)
            self.add(lbl)
            self.play(FadeIn(lbl), duration=0.3)

        self.play_voiceover("Each of these numbers comes from a completely different area of math, yet they combine into this one simple, perfect equation.", speed=1.1)

        all_euler = [header2, euler] + label_objs
        self.play(*[FadeOut(o) for o in all_euler], duration=0.5)

        # ─── PART 3: GRAPHING A FUNCTION ──────────────────────
        header3 = PixelText("3. GRAPHING SINE", color="#00E436",
                            scale=1, align="center")
        engine.place_in_zone(header3, L.TITLE_ZONE)
        self.add(header3)
        self.play(FadeIn(header3), duration=0.3)

        # Axes fit within safe area
        axes = Axes(x_range=(-7, 7, 1), y_range=(-2, 2, 1),
                    x=L.SAFE_LEFT + 5, y=L.SAFE_TOP + 30,
                    width=L.SAFE_RIGHT - L.SAFE_LEFT - 10,
                    height=150, color="#5F574F")
        graph = Graph(func=math.sin, axes=axes, color="#FF004D", thickness=1)
        self.add(axes)
        self.play(FadeIn(axes), duration=0.5)

        eq_sin = MathTex(r"f(x) = \sin(x)", color="#FFEC27",
                         max_width=int(L.FOOTER_ZONE.width * 0.6))
        engine.place_in_zone(eq_sin, L.FOOTER_ZONE)
        self.add(eq_sin)
        self.play(Create(eq_sin), duration=0.5)

        self.add(graph)
        self.play(graph.animate_draw(), duration=2.0)

        self.play_voiceover("The sine function creates this beautiful wave that repeats forever. It describes sound waves, light waves, and the rhythm of the tides.", speed=1.1)

        # Tracking dot
        dot = Dot(x=axes.val_to_screen(-7, 0)[0],
                  y=axes.val_to_screen(0, math.sin(-7))[1],
                  radius=3, color="#FFEC27")
        self.add(dot)
        tracker = ValueTracker(-7)
        dot.add_updater(lambda obj, dt: (
            setattr(obj, 'x', axes.val_to_screen(tracker.value, 0)[0]),
            setattr(obj, 'y', axes.val_to_screen(0, math.sin(tracker.value))[1]),
        ))
        self.play(tracker.animate_to(7), duration=3.0)

        self.play_voiceover("Watch how the dot traces along the curve, rising and falling in a perfect rhythm.", speed=1.1)

        self.play(FadeOut(header3), FadeOut(axes), FadeOut(graph),
                  FadeOut(eq_sin), FadeOut(dot), duration=0.5)

        # ─── PART 4: QUADRATIC FORMULA ────────────────────────
        # Use the equation_explainer preset
        quad_objs = LayoutPresets.equation_explainer(
            engine,
            title="4. QUADRATIC FORMULA",
            equation=r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
            explanation="SOLVES ANY EQUATION OF THE FORM AX^2 + BX + C = 0",
        )
        for obj in quad_objs:
            self.add(obj)
            self.play(FadeIn(obj), duration=0.4)

        self.play_voiceover("The quadratic formula can solve any equation of the form a x squared plus b x plus c equals zero. It's one of the first powerful tools every math student learns.", speed=1.1)

        # Example
        ex = PixelText("Example: x^2 - 5x + 6 = 0", color="#C2C3C7",
                        scale=1, align="center",
                        max_width=int(L.LOWER_THIRD.width * 0.9))
        engine.place_in_zone(ex, L.LOWER_THIRD)
        self.add(ex)
        self.play(FadeIn(ex), duration=0.5)

        sol = PixelText("Solutions: x = 2  and  x = 3", color="#29ADFF",
                         scale=1, align="center",
                         max_width=int(L.FOOTER_ZONE.width * 0.9))
        engine.place_in_zone(sol, L.FOOTER_ZONE)
        self.add(sol)
        self.play(FadeIn(sol), duration=0.5)

        self.play_voiceover("For x squared minus five x plus six equals zero, the formula gives us x equals two and x equals three.", speed=1.1)

        self.play(*[FadeOut(o) for o in quad_objs + [ex, sol]], duration=0.5)

        # ─── OUTRO ────────────────────────────────────────────
        outro_objs = engine.auto_layout(
            title="MATH IS BEAUTIFUL",
            subtitle="made with pixelengine",
            subtitle_color="#7E7587",
        )
        for obj in outro_objs:
            self.add(obj)
        self.play(TypeWriter(outro_objs[0]), duration=1.2)
        if len(outro_objs) > 1:
            self.play(FadeIn(outro_objs[1]), duration=0.5)

        self.play_voiceover("Math is the language of the universe. Keep exploring, and you'll find beauty everywhere.", speed=1.1)
        self.wait(1.0)
        self.play(*[FadeOut(o) for o in outro_objs], duration=1.0)
        self.wait(0.5)


if __name__ == "__main__":
    MathDemo(PixelConfig.landscape()).render("math_demo.mp4")
