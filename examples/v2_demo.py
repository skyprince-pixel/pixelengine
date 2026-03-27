"""v2 Feature Demo — tests all new PixelEngine capabilities.

Renders a showcase video demonstrating:
- Phase 5: Manim-like animations (GrowFromEdge, DrawBorderThenFill, BarChart, Graph)
- Phase 6: Textures (checkerboard, dithering, gradient)
- Phase 7: 3D (Cube3D rotation)
- Phase 8: Simulations (Pendulum, Rope)
"""
import math
from pixelengine import (
    Scene, PixelConfig, Rect, Circle, Triangle, Line, PixelText, TypeWriter,
    GradientBackground, FadeIn, FadeOut, FadeTransition, MoveTo, AnimationGroup,
    GrowFromPoint, GrowFromEdge, DrawBorderThenFill, Create, GrowArrow,
    MorphTo, ReplacementTransform,
    ValueTracker, NumberLine, BarChart, Axes, Graph, Dot,
    PatternTexture, DitherTexture, GradientTexture,
    Pendulum, Rope, ease_out,
)
from pixelengine.objects3d import Cube3D, Rotate3D, Axes3D
from pixelengine.math3d import Vec3


class V2Demo(Scene):
    def construct(self):
        # ── Background ──────────────────────────────────────
        bg = GradientBackground(
            color_top="#0D1B2A", color_bottom="#1B2838",
        )
        self.add(bg)

        # ════════════════════════════════════════════════════
        #  SCENE 1: Manim-like Construction Animations
        # ════════════════════════════════════════════════════
        title = PixelText("MANIM ANIMATIONS", x=128, y=10, align="center",
                          color="#FFEC27")
        self.add(title)
        self.play(TypeWriter(title), duration=1.0)
        self.wait(0.3)

        # GrowFromEdge — bar chart style
        bar1 = Rect(15, 50, x=40, y=80, color="#FF004D")
        bar2 = Rect(15, 70, x=65, y=60, color="#00E436")
        bar3 = Rect(15, 40, x=90, y=90, color="#29ADFF")
        bar4 = Rect(15, 85, x=115, y=45, color="#FFEC27")
        self.add(bar1, bar2, bar3, bar4)

        self.play(
            GrowFromEdge(bar1, edge="bottom"),
            GrowFromEdge(bar2, edge="bottom"),
            GrowFromEdge(bar3, edge="bottom"),
            GrowFromEdge(bar4, edge="bottom"),
            duration=1.5,
        )
        self.wait(0.5)

        # GrowArrow
        arrow = Line(145, 100, 230, 100, color="#FF77A8", thickness=1)
        self.add(arrow)
        self.play(GrowArrow(arrow), duration=0.8)
        self.wait(0.3)

        # DrawBorderThenFill
        tri = Triangle([(170, 90), (200, 40), (230, 90)], color="#FFA300")
        self.add(tri)
        self.play(DrawBorderThenFill(tri), duration=1.2)
        self.wait(0.5)

        # Clean up
        self.play(FadeTransition(self, mode="out"), duration=0.3)
        self.remove(title, bar1, bar2, bar3, bar4, arrow, tri)
        self.play(FadeTransition(self, mode="in"), duration=0.3)

        # ════════════════════════════════════════════════════
        #  SCENE 2: Math Objects (BarChart + Graph)
        # ════════════════════════════════════════════════════
        title2 = PixelText("MATH OBJECTS", x=128, y=10, align="center",
                           color="#FFEC27")
        self.add(title2)
        self.play(TypeWriter(title2), duration=0.8)

        # BarChart
        chart = BarChart(
            data=[30, 70, 50, 90, 40, 65],
            labels=["1", "2", "3", "4", "5", "6"],
            colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27",
                    "#FF77A8", "#FFA300"],
            x=10, y=25, width=100, height=70,
        )
        self.add(chart)
        self.play(chart.animate_build(), duration=1.5)
        self.wait(0.5)

        # Graph with axes
        axes = Axes(x_range=(-4, 4, 1), y_range=(-1.5, 1.5, 0.5),
                    x=120, y=25, width=120, height=70,
                    color="#5F574F")
        graph = Graph(func=math.sin, axes=axes, color="#FF004D",
                      thickness=1)
        self.add(axes)
        self.add(graph)
        self.play(graph.animate_draw(), duration=1.5)
        self.wait(0.5)

        # NumberLine
        nline = NumberLine(min_val=0, max_val=10, step=2,
                           x=20, y=115, width=210, color="#29ADFF")
        self.add(nline)
        self.wait(0.8)

        # Clean
        self.play(FadeTransition(self, mode="out"), duration=0.3)
        self.remove(title2, chart, axes, graph, nline)
        self.play(FadeTransition(self, mode="in"), duration=0.3)

        # ════════════════════════════════════════════════════
        #  SCENE 3: Textures
        # ════════════════════════════════════════════════════
        title3 = PixelText("TEXTURE FILLS", x=128, y=10, align="center",
                           color="#FFEC27")
        self.add(title3)
        self.play(TypeWriter(title3), duration=0.8)

        # Checkerboard texture
        r1 = Rect(50, 40, x=15, y=35, color="#FFFFFF")
        r1.fill_texture = PatternTexture("checkerboard", cell_size=4,
                                          color1="#FF004D", color2="#1D2B53")
        self.add(r1)
        self.play(FadeIn(r1), duration=0.5)

        # Dither texture
        r2 = Rect(50, 40, x=75, y=35, color="#FFFFFF")
        r2.fill_texture = DitherTexture(color1="#FFEC27", color2="#00E436",
                                         density=0.5)
        self.add(r2)
        self.play(FadeIn(r2), duration=0.5)

        # Gradient texture
        r3 = Rect(50, 40, x=135, y=35, color="#FFFFFF")
        r3.fill_texture = GradientTexture(color1="#29ADFF", color2="#FF004D",
                                           direction="horizontal", width=50)
        self.add(r3)
        self.play(FadeIn(r3), duration=0.5)

        # Stripes on triangle
        tri2 = Triangle([(200, 75), (225, 35), (250, 75)], color="#FFA300")
        tri2.fill_texture = PatternTexture("stripes_v", cell_size=3,
                                            color1="#FFA300", color2="#AB5236")
        self.add(tri2)
        self.play(FadeIn(tri2), duration=0.5)

        # Labels
        l1 = PixelText("CHECK", x=25, y=80, color="#C2C3C7")
        l2 = PixelText("DITHER", x=82, y=80, color="#C2C3C7")
        l3 = PixelText("GRADIENT", x=137, y=80, color="#C2C3C7")
        l4 = PixelText("STRIPES", x=202, y=80, color="#C2C3C7")
        self.add(l1, l2, l3, l4)
        self.wait(1.0)

        # Clean
        self.play(FadeTransition(self, mode="out"), duration=0.3)
        self.remove(title3, r1, r2, r3, tri2, l1, l2, l3, l4)
        self.play(FadeTransition(self, mode="in"), duration=0.3)

        # ════════════════════════════════════════════════════
        #  SCENE 4: 3D Wireframes
        # ════════════════════════════════════════════════════
        title4 = PixelText("3D WIREFRAMES", x=128, y=10, align="center",
                           color="#FFEC27")
        self.add(title4)
        self.play(TypeWriter(title4), duration=0.8)

        cube = Cube3D(size=2.0, color="#29ADFF")
        cube.position = Vec3(0, 0, 5)
        cube.rotation_x = 20
        self.add(cube)

        axes3d = Axes3D(size=1.5)
        axes3d.position = Vec3(0, 0, 5)
        axes3d.rotation_x = 20
        axes3d.rotation_y = cube.rotation_y
        self.add(axes3d)

        # Rotate cube
        self.play(Rotate3D(cube, axis="y", degrees=360), duration=3.0)
        self.wait(0.5)

        # Clean
        self.play(FadeTransition(self, mode="out"), duration=0.3)
        self.remove(title4, cube, axes3d)
        self.play(FadeTransition(self, mode="in"), duration=0.3)

        # ════════════════════════════════════════════════════
        #  SCENE 5: Simulations
        # ════════════════════════════════════════════════════
        title5 = PixelText("SIMULATIONS", x=128, y=10, align="center",
                           color="#FFEC27")
        self.add(title5)
        self.play(TypeWriter(title5), duration=0.8)

        # Pendulum
        pend = Pendulum(pivot_x=70, pivot_y=30, length=50, angle=60,
                        bob_radius=4, color="#FF004D", string_color="#C2C3C7")
        self.add(pend)

        # Rope
        rope = Rope(start_x=140, start_y=30, end_x=230, end_y=30,
                    segments=12, color="#FFA300")
        self.add(rope)

        # Let simulations run
        self.wait(4.0)

        # Final fade
        self.play(FadeTransition(self, mode="out"), duration=0.5)


if __name__ == "__main__":
    scene = V2Demo(PixelConfig.landscape())
    scene.render()
