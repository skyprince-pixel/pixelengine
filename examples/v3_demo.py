"""PixelEngine v3 Demo — Lighting, Shadows, Quality Control & Camera Effects.

Demonstrates all new v3 features:
- AmbientLight, PointLight, DirectionalLight with shadows
- Per-object render_quality (chunky and smooth)
- Camera DepthOfField, Vignette, ChromaticAberration, Letterbox
"""
from pixelengine import (
    Scene, PixelConfig, Rect, Circle, PixelText,
    AmbientLight, PointLight, DirectionalLight,
    Vignette, ChromaticAberration, Letterbox,
    MoveTo, FadeIn, ease_in_out,
    GradientBackground,
)


class LightingDemo(Scene):
    """Showcases the lighting and shadow system."""

    def construct(self):
        # ── Background ──
        bg = GradientBackground(
            color_top="#0D0221", color_bottom="#1A0533",
        )
        self.add(bg)

        # ── Ambient light (dim base illumination) ──
        ambient = AmbientLight(intensity=0.15, color="#4466AA")
        self.add_light(ambient)

        # ── Objects that cast shadows ──
        pillar1 = Rect(12, 40, x=60, y=50, color="#5F574F")
        pillar1.casts_shadow = True
        pillar1.shadow_opacity = 0.7

        pillar2 = Rect(12, 30, x=150, y=60, color="#5F574F")
        pillar2.casts_shadow = True
        pillar2.shadow_opacity = 0.7

        ball = Circle(8, x=110, y=70, color="#FF004D")
        ball.casts_shadow = True
        ball.shadow_opacity = 0.6

        self.add(pillar1, pillar2, ball)

        # ── Point light (warm torch) ──
        torch = PointLight(
            x=100, y=40, radius=90,
            color="#FFA300", intensity=1.5, falloff="linear",
        )
        torch.visible = True  # Show the light source
        self.add_light(torch)

        # ── Directional light (moonlight from top-left) ──
        moon = DirectionalLight(angle=225, intensity=0.3, color="#88AAFF")
        self.add_light(moon)

        # Hold and admire the lit scene
        self.wait(2.0)

        # ── Animate the point light moving across ──
        self.play(MoveTo(torch, 200, 40), duration=3.0)
        self.wait(1.0)
        self.play(MoveTo(torch, 50, 80), duration=2.0)
        self.wait(1.0)


class QualityDemo(Scene):
    """Demonstrates per-object pixel quality control."""

    def construct(self):
        bg = GradientBackground(
            color_top="#1D2B53", color_bottom="#000000",
        )
        self.add(bg)

        # Label
        title = PixelText("Quality Control", x=60, y=10, color="#FFEC27")
        self.add(title)

        # Normal quality (1.0x)
        normal_label = PixelText("1.0x", x=30, y=40, color="#C2C3C7")
        normal_rect = Rect(30, 30, x=25, y=55, color="#29ADFF")
        normal_rect.render_quality = 1.0

        # Low quality (0.3x — extra chunky)
        low_label = PixelText("0.3x", x=95, y=40, color="#C2C3C7")
        low_rect = Rect(30, 30, x=90, y=55, color="#00E436")
        low_rect.render_quality = 0.3

        # High quality (2.0x — smooth)
        high_label = PixelText("2.0x", x=160, y=40, color="#C2C3C7")
        high_rect = Rect(30, 30, x=155, y=55, color="#FF004D")
        high_rect.render_quality = 2.0

        # Ultra-low quality (0.15x — extremely pixelated)
        ultra_label = PixelText("0.15x", x=220, y=40, color="#C2C3C7")
        ultra_circle = Circle(15, x=220, y=55, color="#FFA300")
        ultra_circle.render_quality = 0.15

        self.add(normal_label, normal_rect)
        self.add(low_label, low_rect)
        self.add(high_label, high_rect)
        self.add(ultra_label, ultra_circle)

        self.play(FadeIn(title), duration=0.5)
        self.wait(3.0)


class CameraFXDemo(Scene):
    """Demonstrates camera post-processing effects."""

    def construct(self):
        bg = GradientBackground(
            color_top="#1A0533", color_bottom="#0D0221",
        )
        self.add(bg)

        # Scene objects
        hero = Circle(10, x=118, y=62, color="#FF004D")
        box1 = Rect(20, 20, x=40, y=60, color="#29ADFF")
        box2 = Rect(15, 15, x=200, y=70, color="#00E436")
        text = PixelText("Camera FX", x=80, y=15, color="#FFEC27")

        self.add(hero, box1, box2, text)

        # ── Phase 1: Vignette ──
        vig = Vignette(intensity=0.6, radius=0.6)
        self.add_camera_fx(vig)
        self.wait(2.0)

        # ── Phase 2: Add depth-of-field (focus on hero) ──
        self.camera.set_focus(128, 72, radius=25)
        self.wait(2.0)

        # ── Phase 3: Add chromatic aberration ──
        chroma = ChromaticAberration(offset=2)
        self.add_camera_fx(chroma)
        self.wait(1.5)

        # ── Phase 4: Letterbox cinematic bars ──
        bars = Letterbox(bar_height=15)
        self.add_camera_fx(bars)
        self.wait(2.0)

        # ── Phase 5: Remove effects one by one ──
        self.remove_camera_fx(chroma)
        self.wait(1.0)
        self.camera.clear_focus()
        self.wait(1.0)


# ── Run all demos ──
if __name__ == "__main__":
    config = PixelConfig.landscape()
    config.fps = 12

    print("═" * 50)
    print("  PixelEngine v3 Demo")
    print("═" * 50)

    print("\n▶ Demo 1: Lighting & Shadows")
    LightingDemo(config).render()

    print("\n▶ Demo 2: Per-Object Quality")
    QualityDemo(config).render()

    print("\n▶ Demo 3: Camera Effects")
    CameraFXDemo(config).render()

    print("\n✓ All demos complete!")
