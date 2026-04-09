"""Demo video exercising all 5 bug fixes: bounds, lint detection, audio sync."""
from pixelengine import (
    CinematicScene, PixelConfig, Layout, VStack, HStack,
    PixelText, Rect, Circle, Triangle, Polygon,
    OrganicMoveTo, OrganicFadeIn, OrganicFadeOut, OrganicScale,
    Cascade, Wave, WithSettle,
    alive, hover,
    Create, DrawBorderThenFill, GrowFromPoint,
    AnimationGroup, Stagger,
    SoundFX,
)


class BugfixDemo(CinematicScene):
    def construct(self):
        L = Layout.portrait()

        # Background
        self.setup_atmosphere("dark")

        # ═══ SECTION 1: Shapes — tests Triangle/Polygon get_bounds() fix ═══
        title = PixelText("SHAPES", scale=2, color="#FFEC27", align="center")
        title.move_to(L.TITLE_ZONE.x, L.TITLE_ZONE.y)
        self.add(title)
        title.add_updater(alive())

        # Triangle — relies on correct get_bounds() for VStack centering
        tri = Triangle(
            [
                (L.MAIN_ZONE.x - 25, L.MAIN_ZONE.y - 50),
                (L.MAIN_ZONE.x + 25, L.MAIN_ZONE.y - 50),
                (L.MAIN_ZONE.x, L.MAIN_ZONE.y - 80),
            ],
            color="#FF004D",
        )

        # Polygon (pentagon) — also relies on correct get_bounds()
        cx, cy = L.MAIN_ZONE.x, L.MAIN_ZONE.y + 10
        poly = Polygon(
            [
                (cx - 25, cy + 15),
                (cx + 25, cy + 15),
                (cx + 35, cy + 45),
                (cx, cy + 60),
                (cx - 35, cy + 45),
            ],
            color="#29ADFF",
        )

        # Reveal shapes with synced animation + sound
        self.play(
            AnimationGroup(Create(tri), Create(poly)),
            duration=1.5,
            sound=SoundFX.dynamic("reveal"),
        )

        tri.add_updater(hover(height=3))
        poly.add_updater(alive())

        self.wait(1.5)

        # Clean exit
        self.play(
            AnimationGroup(
                OrganicFadeOut(title),
                OrganicFadeOut(tri),
                OrganicFadeOut(poly),
            ),
            duration=0.5,
        )
        self.transition("glitch", duration=0.4)

        # ═══ SECTION 2: Sounds — tests lint_source() coin/explosion/jump ═══
        snd_title = PixelText("SOUNDS", scale=2, color="#00E436", align="center")
        snd_title.move_to(L.TITLE_ZONE.x, L.TITLE_ZONE.y)
        self.add(snd_title)
        snd_title.add_updater(alive())

        # coin — exercises Bug 1 fix (lint_source now detects this)
        coin = Circle(radius=12, color="#FFEC27")
        coin.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y - 30)
        self.play(Create(coin), duration=0.5, sound=SoundFX.coin())
        coin.add_updater(hover(height=4))

        # jump
        jump_dot = Circle(radius=10, color="#00E436")
        jump_dot.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y + 10)
        self.play(OrganicFadeIn(jump_dot), duration=0.5, sound=SoundFX.jump())
        jump_dot.add_updater(alive())

        # explosion
        boom = Circle(radius=15, color="#FF004D")
        boom.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y + 50)
        self.play(Create(boom), duration=0.5, sound=SoundFX.explosion())
        boom.add_updater(hover(height=3))

        # Animate title with sound
        self.play(
            OrganicScale(snd_title, factor=1.05, feel="gentle"),
            duration=1.5,
            sound=SoundFX.dynamic("success"),
        )

        # Clean exit
        self.play(
            AnimationGroup(
                *[OrganicFadeOut(o) for o in [snd_title, coin, jump_dot, boom]]
            ),
            duration=0.5,
        )


if __name__ == "__main__":
    BugfixDemo(PixelConfig.portrait()).render()
