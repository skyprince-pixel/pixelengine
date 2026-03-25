#!/usr/bin/env python3
"""
PixelEngine — Sound Demo

Demonstrates automatic and manual sound effects:
- TypeWriter auto-generates typing clicks
- FadeIn/FadeOut auto-generates reveal/dismiss sounds
- Manual play_sound() for coin, explosion, achievement
- All sounds are procedurally generated — no audio files needed
"""
from pixelengine import (
    Scene, PixelConfig,
    Rect, Circle,
    Sprite, PixelText, TypeWriter,
    GradientBackground, Starfield,
    ParticleEmitter, FadeTransition,
    MoveTo, FadeIn, FadeOut, AnimationGroup,
    CameraZoom, SoundFX,
    ease_out, ease_in_out, bounce,
)


class SoundDemo(Scene):
    def construct(self):
        # ── Background ────────────────────────────
        sky = GradientBackground("#0B0E2A", "#1D2B53")
        self.add(sky)
        stars = Starfield(star_count=60, seed=42)
        self.add(stars)

        # ── 1. Title with typing sounds (auto) ────
        title = PixelText(
            "SOUND ENGINE", x=128, y=20,
            color="#FFD700", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(title)
        self.play(TypeWriter(title), duration=1.5)
        self.wait(0.3)

        # ── 2. Subtitle (auto typing) ────────────
        sub = PixelText(
            "AUTO-GENERATED SFX", x=128, y=45,
            color="#C2C3C7", align="center", max_chars=0,
        )
        self.add(sub)
        self.play(TypeWriter(sub), duration=1.0)
        self.wait(0.5)

        # ── 3. Player appears (auto reveal sound) ─
        player = Sprite.from_art([
            "..WW..",
            ".WWWW.",
            "WWWWWW",
            ".BRRB.",
            ".BRRB.",
            "..BB..",
        ], x=60, y=90)
        self.add(player)
        self.play(FadeIn(player), duration=0.3)
        self.wait(0.3)

        # ── 4. Coin collect (manual sound) ────────
        coin = Circle(3, x=150, y=95, color="#FFEC27")
        self.add(coin)
        self.play(
            MoveTo(player, x=140, y=90, easing=ease_out),
            duration=0.8,
        )
        self.play_sound(SoundFX.coin())
        self.remove(coin)
        self.wait(0.3)

        # ── 5. Jump (manual sound) ────────────────
        self.play_sound(SoundFX.jump())
        self.play(
            MoveTo(player, x=140, y=70, easing=ease_out),
            duration=0.3,
        )
        self.play_sound(SoundFX.land())
        self.play(
            MoveTo(player, x=140, y=90, easing=bounce),
            duration=0.3,
        )
        self.wait(0.3)

        # ── 6. Explosion! ────────────────────────
        self.play_sound(SoundFX.explosion())
        self.camera.shake(intensity=5, duration=0.4)
        sparks = ParticleEmitter.explosion(x=200, y=90, count=40)
        self.add(sparks)
        self.wait(0.8)

        # ── 7. Power up ──────────────────────────
        self.play_sound(SoundFX.powerup())
        self.play(CameraZoom(self.camera, zoom=1.3, easing=ease_out), duration=0.5)
        self.wait(0.3)
        self.play(CameraZoom(self.camera, zoom=1.0, easing=ease_out), duration=0.3)

        # ── 8. Achievement ────────────────────────
        self.play_sound(SoundFX.achievement())
        end = PixelText(
            "ACHIEVEMENT!", x=128, y=55,
            color="#00E436", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(end)
        self.play(TypeWriter(end), duration=1.0)
        self.wait(2.0)


if __name__ == "__main__":
    scene = SoundDemo(PixelConfig.landscape())
    scene.render("sound_demo.mp4")
    print("Done! Open sound_demo.mp4")
