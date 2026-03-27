"""The Secretary Problem — YouTube Short (PixelEngine + Kokoro TTS)

A story-driven 60s educational short about the mathematical 37% rule
for optimal stopping — applied to finding your perfect life partner.
"""
from pixelengine import (
    Scene, PixelConfig, Rect, Circle, PixelText, TypeWriter, Line,
    MoveTo, MoveBy, FadeIn, FadeOut, AnimationGroup, Sequence,
    SoundFX, GradientBackground, Starfield, ParticleEmitter,
    GrowFromEdge, Create, ColorShift,
    AmbientLight, PointLight,
    Vignette, Letterbox,
    Sprite,
    ease_in_out, ease_out,
)
from pixelengine.voiceover import VoiceOver


# ── Portrait Short: 270×480 canvas ──
W, H = 270, 480
CX, CY = W // 2, H // 2  # Center: 135, 240


def heart_sprite(x, y, color="#FF004D", z=5):
    """Small pixel-art heart."""
    s = Sprite.from_art([
        "..RR..RR..",
        ".RRRRRRRR.",
        "RRRRRRRRRR",
        "RRRRRRRRRR",
        ".RRRRRRRR.",
        "..RRRRRR..",
        "...RRRR...",
        "....RR....",
    ], x=x, y=y, color_map={"R": color})
    s.z_index = z
    return s


def person_sprite(x, y, color="#29ADFF", z=3):
    """Simple stick-figure person."""
    s = Sprite.from_art([
        "..WW..",
        ".WWWW.",
        "..WW..",
        ".WWWW.",
        "WWWWWW",
        ".WWWW.",
        ".W..W.",
        ".W..W.",
    ], x=x, y=y, color_map={"W": color})
    s.z_index = z
    return s


class SecretaryProblem(Scene):
    def construct(self):
        # ── Preload all voiceover lines ──
        lines = [
            "Mathematics has a formula for finding your perfect life partner.",
            "It's called the Secretary Problem.",
            "Imagine you can date exactly ten people in your lifetime.",
            "But there's a catch.",
            "Once you reject someone, they're gone forever.",
            "And you can't go back to anyone you already said no to.",
            "So how do you pick the best one?",
            "Mathematicians solved this in nineteen sixty three.",
            "The answer is the thirty seven percent rule.",
            "Reject the first thirty seven percent of your options completely.",
            "That means the first three or four people, you just let them go.",
            "Then, pick the very next person who is better than everyone you've seen so far.",
            "This simple rule gives you a thirty seven percent chance of finding the absolute best partner.",
            "And that thirty seven percent comes from one divided by e, Euler's number.",
            "The beautiful thing? This works for any decision, jobs, apartments, even parking spots.",
            "Math doesn't just solve equations. It solves life.",
        ]
        VoiceOver.preload(lines)

        # ══════════════════════════════════════════════════
        #  SCENE 1: HOOK (0-8s)
        # ══════════════════════════════════════════════════
        bg = GradientBackground(color_top="#0D0221", color_bottom="#1A0533")
        bg.z_index = -10
        self.add(bg)

        stars = Starfield(star_count=40, color="#FFFFFF")
        stars.z_index = -9
        self.add(stars)

        # Dim ambient + warm accent light
        self.add_light(AmbientLight(intensity=0.15, color="#6644AA"))
        glow = PointLight(x=CX, y=180, radius=120, color="#FF77A8",
                          intensity=1.0, falloff="linear")
        self.add_light(glow)

        # Vignette for cinematic feel
        self.add_camera_fx(Vignette(intensity=0.5, radius=0.65))

        # Heart
        heart = heart_sprite(CX - 5, 140, color="#FF004D")
        self.add(heart)
        self.play(FadeIn(heart), duration=0.8)

        # Title
        title1 = PixelText("THE MATH OF", x=CX, y=200, align="center", color="#FFEC27")
        title2 = PixelText("FINDING LOVE", x=CX, y=215, align="center", color="#FF004D")
        self.add(title1, title2)
        self.play(TypeWriter(title1), duration=0.8)
        self.play(TypeWriter(title2), duration=0.8)

        self.play_voiceover(lines[0])

        # Subtitle
        sub = PixelText("THE SECRETARY PROBLEM", x=CX, y=250, align="center", color="#C2C3C7")
        self.add(sub)
        self.play(FadeIn(sub), duration=0.5)

        self.play_voiceover(lines[1])

        # Clear scene
        self.play(FadeOut(heart), FadeOut(title1), FadeOut(title2), FadeOut(sub), duration=0.8)

        # ══════════════════════════════════════════════════
        #  SCENE 2: THE SETUP — 10 people (8-20s)
        # ══════════════════════════════════════════════════
        setup_title = PixelText("THE SETUP", x=CX, y=30, align="center", color="#00E436")
        self.add(setup_title)
        self.play(FadeIn(setup_title), duration=0.4)

        self.play_voiceover(lines[2])

        # Show 10 people in 2 rows of 5
        people = []
        colors = ["#29ADFF", "#FF004D", "#00E436", "#FFA300", "#FF77A8",
                  "#FFEC27", "#AB5236", "#C2C3C7", "#7E2553", "#83769C"]
        for i in range(10):
            row = i // 5
            col = i % 5
            px = 30 + col * 50
            py = 100 + row * 80
            p = person_sprite(px, py, color=colors[i])
            people.append(p)
            self.add(p)
            self.play(FadeIn(p), duration=0.15, sound=SoundFX.tick())

        self.wait(0.3)

        # The catch
        catch_text = PixelText("THE CATCH:", x=CX, y=280, align="center", color="#FF004D")
        self.add(catch_text)
        self.play(FadeIn(catch_text), duration=0.4)

        self.play_voiceover(lines[3])

        rule1 = PixelText("NO GOING BACK", x=CX, y=310, align="center", color="#FFEC27")
        self.add(rule1)
        self.play(TypeWriter(rule1), duration=0.6)

        self.play_voiceover(lines[4])
        self.play_voiceover(lines[5])

        # Question
        q_text = PixelText("HOW DO YOU PICK", x=CX, y=370, align="center", color="#FFFFFF")
        q_text2 = PixelText("THE BEST ONE?", x=CX, y=385, align="center", color="#FFEC27")
        self.add(q_text, q_text2)
        self.play(FadeIn(q_text), FadeIn(q_text2), duration=0.4)

        self.play_voiceover(lines[6])

        # Clear
        all_scene2 = [setup_title, catch_text, rule1, q_text, q_text2] + people
        self.play(*[FadeOut(o) for o in all_scene2], duration=0.6)

        # ══════════════════════════════════════════════════
        #  SCENE 3: THE SOLUTION — 37% Rule (20-40s)
        # ══════════════════════════════════════════════════
        self.play(MoveTo(glow, CX, 250), duration=0.3)
        glow.color = (255, 236, 39, 255)

        sol_title = PixelText("THE SOLUTION", x=CX, y=30, align="center", color="#FFEC27")
        self.add(sol_title)
        self.play(FadeIn(sol_title), duration=0.4)

        self.play_voiceover(lines[7])

        # Big "37%" text
        big37 = PixelText("37%", x=CX, y=90, align="center", color="#00E436")
        big37.scale_x = 2.0
        big37.scale_y = 2.0
        rule_text = PixelText("RULE", x=CX, y=120, align="center", color="#00E436")
        self.add(big37, rule_text)
        self.play(FadeIn(big37), FadeIn(rule_text), duration=0.5,
                  sound=SoundFX.powerup())

        self.play_voiceover(lines[8])

        # Visual: 10 people as circles in a line, first 4 are RED (rejected)
        reject_label = PixelText("REJECT FIRST 37%", x=CX, y=170, align="center", color="#FF004D")
        self.add(reject_label)
        self.play(FadeIn(reject_label), duration=0.3)

        dots = []
        for i in range(10):
            dx = 25 + i * 23
            dot = Circle(6, x=dx, y=210, color="#29ADFF")
            num = PixelText(str(i + 1), x=dx + 3, y=225, align="center", color="#C2C3C7")
            dots.append((dot, num))
            self.add(dot, num)
            self.play(FadeIn(dot), duration=0.1)

        self.play_voiceover(lines[9])

        # Reject first 4 (turn red with X)
        self.play_voiceover(lines[10])
        for i in range(4):
            dot, num = dots[i]
            self.play(ColorShift(dot, "#FF004D"), duration=0.2, sound=SoundFX.hit())
            x_mark = PixelText("X", x=dot.x + 3, y=dot.y - 2, align="center", color="#FF004D")
            x_mark.z_index = 10
            self.add(x_mark)

        # Highlight #5 as the pick (turn green)
        pick_label = PixelText("PICK NEXT BEST!", x=CX, y=260, align="center", color="#00E436")
        self.add(pick_label)
        self.play(FadeIn(pick_label), duration=0.3)

        self.play_voiceover(lines[11])

        dot5, num5 = dots[4]
        self.play(ColorShift(dot5, "#00E436"), duration=0.3, sound=SoundFX.coin())

        sparks = ParticleEmitter.sparks(x=dot5.x + 6, y=dot5.y)
        self.add(sparks)
        self.wait(0.8)

        # Probability text
        prob = PixelText("P(BEST) = 37%", x=CX, y=320, align="center", color="#FFEC27")
        self.add(prob)
        self.play(FadeIn(prob), duration=0.4)

        self.play_voiceover(lines[12])

        # Clear scene 3
        scene3_objs = [sol_title, big37, rule_text, reject_label, pick_label, prob, sparks]
        for d, n in dots:
            scene3_objs.extend([d, n])
        self.play(*[FadeOut(o) for o in scene3_objs], duration=0.6)

        # ══════════════════════════════════════════════════
        #  SCENE 4: WHY 37%? Euler's number (40-50s)
        # ══════════════════════════════════════════════════
        self.play(MoveTo(glow, CX, 200), duration=0.3)
        glow.color = (41, 173, 255, 255)

        why_title = PixelText("WHY 37%?", x=CX, y=40, align="center", color="#29ADFF")
        self.add(why_title)
        self.play(FadeIn(why_title), duration=0.4)

        # Formula
        formula1 = PixelText("1 / E", x=CX, y=120, align="center", color="#FFEC27")
        formula1.scale_x = 2.0
        formula1.scale_y = 2.0
        self.add(formula1)
        self.play(FadeIn(formula1), duration=0.5, sound=SoundFX.reveal())

        e_val = PixelText("E = 2.71828...", x=CX, y=170, align="center", color="#C2C3C7")
        self.add(e_val)
        self.play(TypeWriter(e_val), duration=0.8)

        result = PixelText("1/E = 0.3679 = 37%", x=CX, y=210, align="center", color="#00E436")
        self.add(result)
        self.play(FadeIn(result), duration=0.5, sound=SoundFX.correct())

        self.play_voiceover(lines[13])

        # Clear
        self.play(FadeOut(why_title), FadeOut(formula1), FadeOut(e_val), FadeOut(result),
                  duration=0.6)

        # ══════════════════════════════════════════════════
        #  SCENE 5: REAL LIFE (50-58s)
        # ══════════════════════════════════════════════════
        self.play(MoveTo(glow, CX, 300), duration=0.3)
        glow.color = (255, 163, 0, 255)

        real_title = PixelText("IT WORKS FOR", x=CX, y=60, align="center", color="#FFA300")
        real_title2 = PixelText("EVERYTHING", x=CX, y=75, align="center", color="#FFA300")
        self.add(real_title, real_title2)
        self.play(FadeIn(real_title), FadeIn(real_title2), duration=0.4)

        self.play_voiceover(lines[14])

        # Icons for different applications
        items = [
            ("JOBS", "#29ADFF", 120),
            ("APARTMENTS", "#00E436", 180),
            ("PARKING", "#FF77A8", 240),
            ("DATING", "#FF004D", 300),
        ]
        item_objs = []
        for label, color, ypos in items:
            heart_icon = heart_sprite(CX - 30, ypos, color=color, z=5)
            text = PixelText(label, x=CX + 10, y=ypos + 3, align="center", color=color)
            self.add(heart_icon, text)
            self.play(FadeIn(heart_icon), FadeIn(text), duration=0.3, sound=SoundFX.ui_select())
            item_objs.extend([heart_icon, text])

        self.wait(0.5)

        # Clear
        self.play(*[FadeOut(o) for o in item_objs + [real_title, real_title2]], duration=0.5)

        # ══════════════════════════════════════════════════
        #  SCENE 6: OUTRO (58-65s)
        # ══════════════════════════════════════════════════
        self.play(MoveTo(glow, CX, 200), duration=0.3)
        glow.color = (255, 0, 77, 255)

        final1 = PixelText("MATH DOESN'T JUST", x=CX, y=160, align="center", color="#FFFFFF")
        final2 = PixelText("SOLVE EQUATIONS", x=CX, y=175, align="center", color="#FFFFFF")
        self.add(final1, final2)
        self.play(TypeWriter(final1), duration=0.6)
        self.play(TypeWriter(final2), duration=0.6)

        self.play_voiceover(lines[15])

        final3 = PixelText("IT SOLVES LIFE.", x=CX, y=220, align="center", color="#FFEC27")
        final3.scale_x = 2.0
        final3.scale_y = 2.0
        self.add(final3)
        self.play(FadeIn(final3), duration=0.5, sound=SoundFX.achievement())

        confetti = ParticleEmitter.confetti(canvas_width=W)
        self.add(confetti)

        heart_final = heart_sprite(CX - 5, 270, color="#FF004D")
        self.add(heart_final)
        self.play(FadeIn(heart_final), duration=0.4)

        # Subscribe CTA
        sub_text = PixelText("FOLLOW FOR MORE", x=CX, y=340, align="center", color="#C2C3C7")
        self.add(sub_text)
        self.play(TypeWriter(sub_text), duration=0.6)

        self.wait(2.0)


if __name__ == "__main__":
    config = PixelConfig.portrait()
    scene = SecretaryProblem(config)
    scene.render()
