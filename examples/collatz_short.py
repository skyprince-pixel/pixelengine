import os
import sys

# Ensure pixelengine is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pixelengine import (
    Scene, PixelConfig, Rect, PixelText, TypeWriter, FadeIn, FadeOut,
    MoveTo, SoundFX, ease_out, bounce
)
from pixelengine.voiceover import VoiceOver

class CollatzShort(Scene):
    def construct(self):
        # Background
        bg = Rect(width=144, height=256, x=0, y=0, color="#0f0f23")
        bg.z_index = -100
        self.add(bg)

        # Scene 1: The Hook
        title = PixelText("THE 3x+1\nPROBLEM", x=72, y=100, color="#FF004D", align="center", max_chars=0)
        self.add(title)
        
        # Audio & visual
        sfx, dur = VoiceOver.generate("Here is a math problem so simple a child can understand it, yet so difficult that no mathematician has ever solved it. It's called the Collatz Conjecture.")
        self.play(TypeWriter(title), duration=dur, sound=sfx)
        self.wait(0.5)
        self.play(FadeOut(title), duration=0.5)

        # Scene 2: The Rules
        rule1 = PixelText("EVEN -> n/2", x=72, y=100, color="#29ADFF", align="center")
        rule2 = PixelText("ODD -> 3n+1", x=72, y=130, color="#00E436", align="center")
        rule1.opacity = 0
        rule2.opacity = 0
        self.add(rule1)
        self.add(rule2)

        sfx2, dur2 = VoiceOver.generate("Pick any positive integer. If it's even, divide it by two. If it's odd, multiply it by three and add one.")
        
        self.play(FadeIn(rule1), duration=dur2/2, sound=sfx2)
        self.play(FadeIn(rule2), duration=dur2/2)
        self.wait(0.5)
        self.play(FadeOut(rule1), FadeOut(rule2), duration=0.5)

        # Scene 3: The Example setup
        ex_title = PixelText("LET'S TRY: 7", x=72, y=50, color="#FFEC27", align="center")
        self.add(ex_title)
        self.play(FadeIn(ex_title), duration=0.5)

        sfx3, dur3 = VoiceOver.generate("Let's try the number 7. It's odd, so times three plus one makes 22. Even, so half is 11. Odd, so 34.")
        
        self.play_sound(sfx3)
        n_text = PixelText("7", x=72, y=140, color="#FFFFFF", align="center")
        self.add(n_text)
        
        self.wait(dur3 * 0.25)
        self.play_sound(SoundFX.coin())
        n_text.text = "22"
        self.wait(dur3 * 0.25)
        self.play_sound(SoundFX.coin())
        n_text.text = "11"
        self.wait(dur3 * 0.25)
        self.play_sound(SoundFX.coin())
        n_text.text = "34"
        self.wait(dur3 * 0.25)

        self.play(FadeOut(ex_title), FadeOut(n_text), duration=0.5)

        # Scene 4: The Chaotic Path
        chaos_text = PixelText("52... 26... 13...", x=72, y=50, color="#FFA300", align="center")
        self.add(chaos_text)
        
        sfx4, dur4 = VoiceOver.generate("The numbers bounce up and down wildly, like a hailstone in a storm cloud. Look at this chaotic path!")
        
        self.play_sound(sfx4)
        for i in range(10):
            # Shake text mathematically
            chaos_text.x = 72 + (i % 3 - 1) * 3
            chaos_text.y = 50 + (i % 2) * 3
            self.wait(dur4 / 10.0)
        
        self.play(FadeOut(chaos_text), duration=0.5)

        # Scene 5: The Loop (4, 2, 1)
        num4 = PixelText("4", x=72, y=0, color="#FF004D", align="center")
        num2 = PixelText("2", x=72, y=0, color="#00E436", align="center")
        num1 = PixelText("1", x=72, y=0, color="#29ADFF", align="center")
        self.add(num4)
        self.add(num2)
        self.add(num1)

        sfx5, dur5 = VoiceOver.generate("But eventually, something magical happens. The sequence plummets down and hits 4... then 2... then 1. And what happens after 1? It loops back to 4, 2, 1 forever.")
        self.play_sound(sfx5)
        
        self.play(MoveTo(num4, x=72, y=100, easing=bounce), duration=dur5 * 0.25)
        self.play(MoveTo(num2, x=72, y=130, easing=bounce), duration=dur5 * 0.25)
        self.play(MoveTo(num1, x=72, y=160, easing=bounce), duration=dur5 * 0.25)
        
        self.camera.shake(3, dur5 * 0.25)
        self.wait(dur5 * 0.25)

        self.play(FadeOut(num4), FadeOut(num2), FadeOut(num1), duration=0.5)

        # Scene 6: The Mystery
        matrix_bg = PixelText("ALL LEAD\nTO 1", x=72, y=128, color="#FFFFFF", align="center")
        matrix_bg.opacity = 0
        self.add(matrix_bg)
        
        sfx6, dur6 = VoiceOver.generate("Does every number eventually fall into this loop? We've checked up to three hundred quintillion, and yes, they all do. But a true proof? Mathematics may not yet be ready for such a problem.")
        
        self.play(FadeIn(matrix_bg), duration=dur6, sound=sfx6)
        
        self.play(FadeOut(matrix_bg), duration=1.5)
        self.wait(1.0)


if __name__ == "__main__":
    scene = CollatzShort(PixelConfig.portrait())
    scene.render("collatz_short.mp4")
