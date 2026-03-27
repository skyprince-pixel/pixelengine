import sys
from pixelengine import (
    Scene, PixelConfig, Rect, PixelText, TypeWriter,
    Circle, MoveTo, FadeIn, FadeOut, Sequence, ease_out,
    SoundFX, Grid, ParticleEmitter, ValueTracker,
    GrowFromEdge, DrawBorderThenFill, Create,
    MorphTo, PatternTexture, Trail, Line, MoveBy, AnimationGroup,
    WipeTransition
)

class CollatzShort(Scene):
    def construct(self):
        # 0. Setup Grid
        grid = Grid(cell_size=16, color="#1D2B53") # dark blue grid
        self.add(grid)
        
        # 1. Intro (0-10s)
        # Portrait Short: 144x256
        title_top = PixelText("THE COLLATZ", x=72, y=30, align="center")
        title_bot = PixelText("CONJECTURE", x=72, y=45, align="center")
        self.add(title_top, title_bot)
        
        self.play(TypeWriter(title_top), duration=1.0)
        self.play(TypeWriter(title_bot), duration=1.0)
        
        self.play_voiceover("The Collatz Conjecture is the most famous impossible math problem.")
        
        n_text = PixelText("N = ?", x=72, y=100, align="center", color="#FF004D") # Red
        self.add(n_text)
        self.play(GrowFromEdge(n_text, "bottom"), duration=1.0)
        
        self.play_voiceover("Pick any positive integer.")
        
        self.play(FadeOut(n_text), FadeOut(title_top), FadeOut(title_bot), duration=1.0)
        
        # 2. Rules Explanation (10-25s)
        rules_title = PixelText("THE RULES", x=72, y=20, align="center", color="#00E436") # Green
        self.add(rules_title)
        self.play(FadeIn(rules_title), duration=0.5)
        
        rule1 = PixelText("IF EVEN:", x=72, y=60, align="center", color="#29ADFF") # Blue
        rule1_action = PixelText("N / 2", x=72, y=80, align="center", color="#FFFFFF")
        self.add(rule1)
        self.play(TypeWriter(rule1), duration=1.0)
        self.add(rule1_action)
        self.play(GrowFromEdge(rule1_action, "bottom"), duration=0.5)
        
        self.play_voiceover("If the number is even, divide it by two.")
        
        rule2 = PixelText("IF ODD:", x=72, y=140, align="center", color="#FFEC27") # Yellow
        rule2_action = PixelText("3N + 1", x=72, y=160, align="center", color="#FFFFFF")
        
        self.add(rule2)
        self.play(TypeWriter(rule2), duration=1.0)
        self.add(rule2_action)
        self.play(GrowFromEdge(rule2_action, "bottom"), duration=0.5)
        
        self.play_voiceover("If it's odd, multiply by three and add one.")
        
        self.play(
            FadeOut(rule1), FadeOut(rule1_action),
            FadeOut(rule2), FadeOut(rule2_action),
            FadeOut(rules_title),
            duration=1.0
        )
        
        # 3. Path Visualization for N = 7
        self.play_voiceover("Let's try this with the number seven.")
        
        # Start at 7.
        current_num = 7
        
        # Visual number
        num_display = PixelText("7", x=72, y=30, align="center", color="#FFA300")
        
        # A bouncing circle representing the path
        ball = Circle(radius=4, x=20, y=200, color="#FF004D") # Start low
        try:
            trail = Trail(target=ball, length=8, color="#FF004D")
            self.add(trail)
        except Exception:
            pass # In case Trail is not exported
            
        self.add(num_display, ball)
        self.play(FadeIn(ball), FadeIn(num_display), duration=0.5)
        
        self.play_voiceover("Seven is odd, so it becomes twenty-two.", speed=1.1)
        
        # Path sequence for 7:
        seq = [22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
        
        self.play_voiceover("It goes up and down wildly like a hailstone.", speed=1.1)
        
        step_x = 100 / len(seq) # width=144, 20 to 120
        current_x = 20
        
        for num in seq:
            # calculate height mapping roughly
            # max is 52 (y=60), min is 1 (y=210)
            target_y = 210 - (num / 52.0) * 150
            current_x += step_x
            
            # Animate ball moving and number updating
            num_display.text = str(num)
            if num % 2 == 0:
                num_display.color = "#29ADFF" # Even -> Blue
                ball.color = "#29ADFF"
            else:
                num_display.color = "#FFEC27" # Odd -> Yellow
                ball.color = "#FFEC27"
                
            sound_effect = SoundFX.jump() if num % 2 != 0 else SoundFX.hit()
            self.play(MoveTo(ball, x=current_x, y=target_y), duration=0.25, sound=sound_effect)
            
        self.play_voiceover("But eventually, no matter what number you start with...")
        
        # Final loop 4-2-1
        self.play_voiceover("It always falls into the four, two, one loop.", speed=1.0)
        
        num_4 = PixelText("4", x=40, y=100, align="center", color="#29ADFF")
        num_2 = PixelText("2", x=72, y=140, align="center", color="#29ADFF")
        num_1 = PixelText("1", x=104, y=100, align="center", color="#FFEC27")
        self.add(num_4, num_2, num_1)
        
        self.play(AnimationGroup(FadeIn(num_4), FadeIn(num_2), FadeIn(num_1)), duration=0.5)
        
        for _ in range(2):
            self.play(MoveTo(ball, x=40, y=100), duration=0.3, sound=SoundFX.jump())
            self.play(MoveTo(ball, x=72, y=140), duration=0.3, sound=SoundFX.hit())
            self.play(MoveTo(ball, x=104, y=100), duration=0.3, sound=SoundFX.laser())
            
        self.play(FadeOut(ball), FadeOut(num_display), duration=0.5)
        
        # 5. Outro (55-60s)
        unsolved = PixelText("UNSOLVED", x=72, y=128, align="center", color="#FF004D")
        self.add(unsolved)
        self.play(GrowFromEdge(unsolved, "bottom"), duration=1.0)
        
        confetti = ParticleEmitter.confetti(x=72, y=128)
        self.add(confetti)
        
        self.play_voiceover("To this day, mathematics cannot definitively prove it is true for every number.")
        
        sub_text = PixelText("SUBSCRIBE!", x=72, y=180, align="center", color="#FFFFFF")
        self.add(sub_text)
        self.play(TypeWriter(sub_text), duration=1.0)
        self.wait(1.5)

if __name__ == "__main__":
    from pixelengine.config import PixelConfig
    # Portrait short 144x256
    scene = CollatzShort(PixelConfig.portrait())
    scene.render()
