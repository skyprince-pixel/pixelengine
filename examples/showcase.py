#!/usr/bin/env python3
"""
PixelEngine — Full Showcase

Demonstrates every major feature: gradient backgrounds, starfield,
tilemaps, sprites, particles, camera effects, transitions, text,
animations. This is the "everything working together" example.
"""
from pixelengine import (
    Scene, PixelConfig,
    Rect, Circle, Line,
    Sprite, PixelText, TypeWriter,
    GradientBackground, Starfield,
    TileSet, TileMap,
    ParticleEmitter, FadeTransition, WipeTransition, Trail,
    MoveTo, MoveBy, FadeIn, FadeOut, AnimationGroup,
    CameraPan, CameraZoom,
    ease_out, ease_in_out, bounce,
)


class Showcase(Scene):
    def construct(self):
        # ═══ ACT 1: Night Sky ═══════════════════════════
        sky = GradientBackground(
            color_top="#0B0E2A",
            color_bottom="#1D2B53",
        )
        self.add(sky)

        stars = Starfield(star_count=80, seed=42)
        self.add(stars)

        title = PixelText(
            "PIXELENGINE", x=128, y=25,
            color="#FFD700", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        self.add(title)
        self.play(TypeWriter(title), duration=1.5)

        sub = PixelText(
            "A CODE-FIRST ENGINE", x=128, y=50,
            color="#C2C3C7", align="center", max_chars=0,
        )
        self.add(sub)
        self.play(TypeWriter(sub), duration=1.0)
        self.wait(1.0)

        # ═══ ACT 2: Wipe Transition ═════════════════════
        self.play(WipeTransition(self, direction="right"), duration=0.4)
        self.remove(title, sub)

        # ═══ ACT 3: Tilemap Level ═══════════════════════
        tiles = TileSet(tile_size=8)
        tiles.add_color_tile('.', "#1D2B53")  # sky
        tiles.add_color_tile('#', "#5F574F")  # stone
        tiles.add_color_tile('G', "#008751")  # grass
        tiles.add_color_tile('D', "#AB5236")  # dirt

        level = [
            "................................",
            "................................",
            "................................",
            "................................",
            "................................",
            "................................",
            "................................",
            "................................",
            "................................",
            "................................",
            "........####.........####.......",
            "................................",
            "....####........####............",
            "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
            "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
            "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
            "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
            "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
        ]
        tilemap = TileMap(tiles, level)
        self.add(tilemap)
        self.play(FadeIn(tilemap), duration=0.3)

        # ═══ ACT 4: Player + Movement ═══════════════════
        player = Sprite.from_art([
            "..WW..",
            ".WWWW.",
            "WWWWWW",
            ".BRRB.",
            ".BRRB.",
            "..BB..",
            ".B..B.",
        ], x=30, y=97)
        self.add(player)

        trail = Trail(target=player, length=10, color="#29ADFF", size=1)
        trail.z_index = -1
        self.add(trail)

        self.play(FadeIn(player), duration=0.3)

        # Move across the level
        self.play(
            MoveTo(player, x=120, y=97, easing=ease_out),
            duration=1.5,
        )
        self.wait(0.2)

        # ═══ ACT 5: Sparks! ═════════════════════════════
        sparks = ParticleEmitter.sparks(x=120, y=100, count=25)
        self.add(sparks)
        self.wait(0.8)

        # ═══ ACT 6: Camera Follow ═══════════════════════
        self.camera.follow(player, smooth=0.15)
        self.play(
            MoveTo(player, x=200, y=97, easing=ease_in_out),
            duration=1.5,
        )
        self.camera.unfollow()
        self.play(
            CameraPan(self.camera, x=0, y=0, easing=ease_out),
            duration=0.5,
        )
        self.wait(0.3)

        # ═══ ACT 7: Fire effect ═════════════════════════
        fire = ParticleEmitter.fire(x=80, y=103, intensity=10)
        self.add(fire)

        fire_label = PixelText("FIRE", x=80, y=90,
                               color="#FFA300", align="center")
        self.add(fire_label)
        self.wait(2.0)
        self.remove(fire, fire_label)

        # ═══ ACT 8: Camera Shake + Zoom ═════════════════
        self.camera.shake(intensity=4, duration=0.4)
        self.wait(0.5)
        self.play(CameraZoom(self.camera, zoom=1.5, easing=ease_out), duration=0.6)
        self.wait(0.5)
        self.play(CameraZoom(self.camera, zoom=1.0, easing=ease_out), duration=0.4)

        # ═══ ACT 9: Fade Out + End Card ═════════════════
        self.play(FadeTransition(self, mode="out"), duration=0.5)

        end = PixelText(
            "MADE WITH\nPIXELENGINE", x=128, y=50,
            color="#FFD700", scale=2, align="center",
            shadow=True, max_chars=0,
        )
        end.z_index = 10000
        self.add(end)
        self.play(TypeWriter(end), duration=1.5)
        self.wait(2.0)


if __name__ == "__main__":
    scene = Showcase(PixelConfig.landscape())
    scene.render("showcase.mp4")
    print("Done! Open showcase.mp4")
