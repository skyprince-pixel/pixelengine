#!/usr/bin/env python3
"""
PixelEngine — Sprites + Camera Demo

Demonstrates: ASCII art sprites, camera pan, camera shake,
              camera follow, and scene composition.
"""
from pixelengine import (
    Scene, PixelConfig, Rect, Circle,
    Sprite, PixelText, TypeWriter,
    MoveTo, FadeIn, AnimationGroup,
    CameraPan, CameraZoom,
    ease_out, ease_in_out, bounce,
)


class SpriteDemo(Scene):
    def construct(self):
        # ── Background elements ────────────────────────────
        ground = Rect(256, 20, x=0, y=124, color="#008751")
        ground.z_index = -1
        self.add(ground)

        # Stars in the sky
        for pos in [(30, 10), (80, 25), (150, 8), (200, 30), (240, 15),
                    (60, 35), (120, 18), (180, 5), (220, 28), (45, 22)]:
            star = Rect(1, 1, x=pos[0], y=pos[1], color="#FFF1E8")
            star.z_index = -2
            self.add(star)

        self.wait(0.5)

        # ── Create a pixel art character sprite ────────────
        player = Sprite.from_art([
            "..GG..",
            ".GGGG.",
            "GGGGGG",
            ".WBBW.",
            ".BRRB.",
            "..BB..",
            ".B..B.",
        ], x=20, y=105)
        self.add(player)
        self.play(FadeIn(player), duration=0.5)
        self.wait(0.3)

        # ── Title text ────────────────────────────────────
        title = PixelText(
            "ADVENTURE", x=128, y=50,
            color="#FFD700", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(title)
        self.play(TypeWriter(title), duration=1.0)
        self.wait(0.5)

        # ── Move player across screen ─────────────────────
        self.play(MoveTo(player, x=120, y=105, easing=ease_out), duration=1.5)
        self.wait(0.3)

        # ── Camera shake (something dramatic!) ────────────
        self.camera.shake(intensity=4, duration=0.5)
        self.wait(0.6)

        # ── Create an enemy sprite ────────────────────────
        enemy = Sprite.from_art([
            ".RRRR.",
            "RRRRRR",
            "R.RR.R",
            "RRRRRR",
            ".RRRR.",
            "..RR..",
            ".R..R.",
        ], x=220, y=105)
        self.add(enemy)
        self.play(FadeIn(enemy), duration=0.3)

        # ── Move enemy toward player ──────────────────────
        self.play(
            MoveTo(enemy, x=150, y=105, easing=ease_in_out),
            duration=1.0,
        )
        self.wait(0.3)

        # ── Camera pan to follow action ──────────────────
        self.play(
            CameraPan(self.camera, x=30, y=0, easing=ease_out),
            duration=1.0,
        )
        self.wait(0.3)

        # ── Camera pan back ──────────────────────────────
        self.play(
            CameraPan(self.camera, x=0, y=0, easing=ease_out),
            duration=0.8,
        )

        # ── Create a tree sprite ──────────────────────────
        tree = Sprite.from_art([
            "...TT...",
            "..TTTT..",
            ".TTTTTT.",
            "TTTTTTTT",
            "...AA...",
            "...AA...",
        ], x=80, y=100)
        tree.z_index = -1
        self.add(tree)
        self.play(FadeIn(tree), duration=0.5)

        self.wait(1.0)

        # ── Final text ───────────────────────────────────
        end = PixelText(
            "PIXEL WORLD", x=128, y=60,
            color="#FFEC27", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(end)
        self.play(TypeWriter(end), duration=1.0)
        self.wait(2.0)


if __name__ == "__main__":
    scene = SpriteDemo(PixelConfig.landscape())
    scene.render("sprite_demo.mp4")
    print("Done! Open sprite_demo.mp4")
