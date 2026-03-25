#!/usr/bin/env python3
"""
PixelEngine — VoiceOver Demo

Demonstrates the Kokoro ONNX Text-to-Speech integration.
Characters speak automatically and the scene waits for the exact required duration.
"""
import os
import sys

# Ensure pixelengine module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pixelengine import (
    Scene, PixelConfig, Sprite, PixelText, TypeWriter,
    FadeIn, MoveTo, AnimationGroup, SoundFX, ease_out, bounce
)

class VoiceoverDemo(Scene):
    def construct(self):
        # 1. Title
        title = PixelText("PIXELENGINE VOICEOVER", x=128, y=20, color="#FFD700", align="center", max_chars=0)
        self.add(title)
        self.play(TypeWriter(title), duration=1.0)
        self.wait(0.5)

        # 2. Character 1 (Bella)
        bella = Sprite.from_art([
            "..RR..",
            ".RRRR.",
            "RRRRRR",
            ".B..B.",
            ".B..B.",
            "..WW..",
        ], x=60, y=80)
        self.add(bella)
        self.play(FadeIn(bella), duration=0.5)
        
        # Bella speaks
        self.play_voiceover(
            "Hello! I am Bella. I am powered by Kokoro ONNX, "
            "running entirely locally on your machine.", 
            voice="af_bella"
        )
        self.wait(0.5)

        # 3. Character 2 (Adam)
        adam = Sprite.from_art([
            "..BB..",
            ".BBBB.",
            "BBBBBB",
            ".W..W.",
            ".W..W.",
            "..RR..",
        ], x=190, y=80)
        self.add(adam)
        self.play(FadeIn(adam), duration=0.5)
        self.play(MoveTo(adam, x=150, y=80, easing=ease_out), duration=0.5)
        
        # Adam speaks
        self.play_voiceover(
            "And I'm Adam. The engine calculates the exact duration of the generated audio "
            "and automatically holds the frame so the animation matches the voiceover perfectly.",
            voice="am_adam"
        )
        self.wait(0.5)
        
        # 4. End with explosion
        self.play_voiceover("Let me show you a trick!", voice="af_bella")
        self.camera.shake(intensity=4, duration=0.5)
        self.play_sound(SoundFX.explosion())
        self.play(MoveTo(adam, x=150, y=20, easing=bounce), duration=0.8)
        self.wait(2.0)


if __name__ == "__main__":
    scene = VoiceoverDemo(PixelConfig.landscape())
    # Note: On first run, this will download ~300MB of ONNX models automatically.
    scene.render("voiceover_demo.mp4")
    print("Done! Open voiceover_demo.mp4")
