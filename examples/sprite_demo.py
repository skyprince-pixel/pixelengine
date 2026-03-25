#!/usr/bin/env python3
"""
PixelEngine — Refined Sprites + Camera + Backgrounds Demo

Demonstrates: gradient sky, starfield, parallax layers, ASCII sprites
with flipping, camera follow with deadzone, camera shake, zoom.
"""
from pixelengine import (
    Scene, PixelConfig, Rect,
    Sprite, PixelText, TypeWriter,
    GradientBackground, Starfield, ParallaxLayer,
    MoveTo, MoveBy, FadeIn, AnimationGroup,
    CameraPan, CameraZoom,
    ease_out, ease_in_out, bounce,
)


class RefinedDemo(Scene):
    def construct(self):
        # ── Gradient night sky ────────────────────────────
        sky = GradientBackground(
            color_top="#0B0E2A",
            color_bottom="#1D2B53",
        )
        self.add(sky)

        # ── Twinkling stars ───────────────────────────────
        stars = Starfield(star_count=60, seed=42, twinkle=True)
        self.add(stars)
        self.wait(1.0)

        # ── Title ─────────────────────────────────────────
        title = PixelText(
            "PIXEL ADVENTURE", x=128, y=15,
            color="#FFD700", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(title)
        self.play(TypeWriter(title), duration=1.5)
        self.wait(0.5)

        # ── Ground ────────────────────────────────────────
        ground = Rect(256, 24, x=0, y=120, color="#008751")
        ground.z_index = -1
        self.add(ground)
        self.play(FadeIn(ground), duration=0.3)

        # ── Player sprite ─────────────────────────────────
        player = Sprite.from_art([
            "..WW..",
            ".WWWW.",
            "WWWWWW",
            ".BRRB.",
            ".BRRB.",
            "..BB..",
            ".B..B.",
        ], x=30, y=100)
        self.add(player)
        self.play(FadeIn(player), duration=0.3)
        self.wait(0.3)

        # ── Move player right ─────────────────────────────
        self.play(MoveTo(player, x=100, y=100, easing=ease_out), duration=1.0)
        self.wait(0.2)

        # ── Flip player and move back ─────────────────────
        player.flip_h = True
        self.play(MoveTo(player, x=50, y=100, easing=ease_out), duration=0.8)
        player.flip_h = False
        self.wait(0.2)

        # ── Camera shake! ─────────────────────────────────
        self.camera.shake(intensity=5, duration=0.4)
        self.wait(0.5)

        # ── Enemy appears ─────────────────────────────────
        enemy = Sprite.from_art([
            ".RRRR.",
            "RRRRRR",
            "RWRRWR",
            "RRRRRR",
            ".RRRR.",
            "..RR..",
            ".R..R.",
        ], x=220, y=100)
        self.add(enemy)
        self.play(
            AnimationGroup(
                FadeIn(enemy),
                MoveTo(enemy, x=160, y=100, easing=ease_in_out),
            ),
            duration=1.0,
        )
        self.wait(0.3)

        # ── Camera zoom in on action ──────────────────────
        self.play(
            CameraZoom(self.camera, zoom=1.5, easing=ease_out),
            duration=0.8,
        )
        self.wait(0.5)

        # ── Camera zoom back out ──────────────────────────
        self.play(
            CameraZoom(self.camera, zoom=1.0, easing=ease_out),
            duration=0.5,
        )
        self.wait(0.3)

        # ── Camera follow player ──────────────────────────
        self.camera.follow(player, smooth=0.15, deadzone=(20, 10))
        self.play(MoveTo(player, x=180, y=100, easing=ease_out), duration=1.5)
        self.camera.unfollow()
        self.wait(0.3)

        # ── Reset camera ─────────────────────────────────
        self.play(CameraPan(self.camera, x=0, y=0, easing=ease_out), duration=0.5)

        # ── Final message ─────────────────────────────────
        end_text = PixelText(
            "GAME ON!", x=128, y=55,
            color="#00E436", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(end_text)
        self.play(TypeWriter(end_text), duration=1.0)
        self.wait(2.0)


if __name__ == "__main__":
    scene = RefinedDemo(PixelConfig.landscape())
    scene.render("refined_demo.mp4")
    print("Done! Open refined_demo.mp4")
