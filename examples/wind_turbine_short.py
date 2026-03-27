#!/usr/bin/env python3
"""
Why Wind Turbines Only Have Three Blades Instead of Four or Five (V2)
A pixelart YouTube Short created with PixelEngine and Kokoro TTS.
Features: 2-person dialogue, camera animations, and environmental props.
"""

import os
import sys
import math
import random

# Ensure pixelengine is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pixelengine import (
    Scene, PixelConfig, Sprite, PixelText, TypeWriter,
    FadeIn, FadeOut, MoveTo, AnimationGroup, Scale, Blink, ColorShift, Rotate,
    ease_in, ease_out, ease_in_out, bounce
)
from pixelengine.camera import CameraPan, CameraZoom, CameraCenterOn
from pixelengine.pobject import PObject
from PIL import Image, ImageDraw


# ═══════════════════════════════════════════════════════════
#  Custom PObjects for the animation
# ═══════════════════════════════════════════════════════════

class Turbine(PObject):
    """Custom pixel-art wind turbine that auto-rotates and handles yaw/stress."""
    def __init__(self, x, y, blades=3, radius=40, color="#FFFFFF", speed=5.0):
        super().__init__(x, y, color=color)
        self.blades = blades
        self.radius = radius
        self.angle = 0.0          # Current rotation angle
        self.speed = speed        # Degrees per frame
        self.yaw_scale = 1.0      # 1.0 = face on, 0.2 = side on
        self.width = radius * 2 + 10
        self.height = radius * 2 + 10
        self.stress = 0.0         # 0.0 to 1.0, adds red jitter
        
    def render(self, canvas):
        if not self.visible:
            return
            
        # Spin!
        self.angle += self.speed
        
        # Create a temporary image for this frame
        img = Image.new("RGBA", (self.width, self.height * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        cx, cy = self.width // 2, self.height
        
        # Jitter based on stress
        jx = int(random.uniform(-3, 3) * self.stress)
        jy = int(random.uniform(-3, 3) * self.stress)
        
        # Tower
        tower_color = (150, 150, 150, int(255 * self.opacity))
        if self.stress > 0.0:
            # Shift towards red based on stress
            r = int(150 + 105 * self.stress)
            g = int(150 - 100 * self.stress)
            b = int(150 - 100 * self.stress)
            tower_color = (r, g, b, int(255 * self.opacity))
            
        draw.line([(cx + jx, cy + jy), (cx + jx, self.height * 2)], fill=tower_color, width=4)
        
        # Hub
        draw.ellipse([cx - 4 + jx, cy - 4 + jy, cx + 4 + jx, cy + 4 + jy], fill=(200, 200, 200, int(255 * self.opacity)))
        
        # Blades
        blade_color = self.get_render_color()
        if self.blades >= 4:
            blade_color = (255, 50, 50, int(255 * self.opacity))
            
        for i in range(self.blades):
            theta = math.radians(self.angle + (360 / self.blades) * i)
            # Apply yaw scaling to x-axis
            bx = cx + math.sin(theta) * self.radius * self.yaw_scale
            by = cy - math.cos(theta) * self.radius
            
            draw.line([(cx + jx, cy + jy), (int(bx) + jx, int(by) + jy)], fill=blade_color, width=3)
            
        # Draw stress vectors if stress is high
        if self.stress > 0.5:
            stress_alpha = int(255 * self.opacity * self.stress * ((math.sin(self.angle * 0.2) + 1) / 2))
            draw.line([(cx - 20, cy), (cx - 40, cy)], fill=(255, 0, 0, stress_alpha), width=2)
            draw.line([(cx + 20, cy), (cx + 40, cy)], fill=(255, 0, 0, stress_alpha), width=2)
            draw.line([(cx - 35, cy - 5), (cx - 40, cy), (cx - 35, cy + 5)], fill=(255, 0, 0, stress_alpha), width=2)
            draw.line([(cx + 35, cy - 5), (cx + 40, cy), (cx + 35, cy + 5)], fill=(255, 0, 0, stress_alpha), width=2)

        # Blit centered at (x, y) = hub location
        canvas.blit(img, self.x - cx, self.y - cy)


class WakeParticles(PObject):
    """Generates wind wake trailing the turbine."""
    def __init__(self, turbine):
        super().__init__(0, 0)
        self.turbine = turbine
        self.particles = []
        self.z_index = -1 # Draw behind turbine
        
    def render(self, canvas):
        if not self.visible:
            return
            
        if self.turbine.blades >= 4:
            if len(self.particles) < 60:
                for _ in range(4):
                    px = self.turbine.x + random.uniform(-self.turbine.radius, self.turbine.radius)
                    py = self.turbine.y + random.uniform(-self.turbine.radius, self.turbine.radius)
                    self.particles.append([px, py, random.uniform(-3, 3), random.uniform(-1, 3), 255, (255, 50, 50)])
        else:
            if len(self.particles) < 30:
                for _ in range(2):
                    px = self.turbine.x + random.uniform(-self.turbine.radius*1.5, -self.turbine.radius)
                    py = self.turbine.y + random.uniform(-self.turbine.radius, self.turbine.radius)
                    self.particles.append([px, py, random.uniform(1, 3), 0, 255, (50, 255, 50)])
                    
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 5
            
            if p[4] > 0:
                c = p[5]
                alpha = int(p[4] * self.turbine.opacity)
                canvas.set_pixel(int(p[0]), int(p[1]), (c[0], c[1], c[2], alpha))
            else:
                if self.turbine.blades >= 4:
                    p[0] = self.turbine.x + random.uniform(-self.turbine.radius, self.turbine.radius)
                    p[1] = self.turbine.y + random.uniform(-self.turbine.radius, self.turbine.radius)
                    p[4] = 255
                    p[5] = (255, 50, 50)
                else:
                    p[0] = self.turbine.x + random.uniform(-self.turbine.radius*1.5, -self.turbine.radius)
                    p[1] = self.turbine.y + random.uniform(-self.turbine.radius, self.turbine.radius)
                    p[4] = 255
                    p[5] = (50, 255, 50)


class InteractiveBarChart(PObject):
    """A pixel art bar chart for efficiency."""
    def __init__(self, x, y, width=120, height=80):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.bars = [0.0, 0.0, 0.0, 0.0]
        self.target_bars = [0.2, 0.6, 0.9, 0.95]
        self.labels = ["1", "2", "3", "4+"]
        
    def render(self, canvas):
        if not self.visible:
            return
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        draw.line([(10, 0), (10, self.height-10)], fill=(200, 200, 200, int(255*self.opacity)), width=1)
        draw.line([(10, self.height-10), (self.width, self.height-10)], fill=(200, 200, 200, int(255*self.opacity)), width=1)
        
        for i in range(4):
            self.bars[i] += (self.target_bars[i] - self.bars[i]) * 0.1
            
        bar_w = 15
        spacing = 25
        for i in range(4):
            bx = 20 + i * spacing
            bh = int(self.bars[i] * (self.height - 20))
            by = self.height - 10 - bh
            
            color = (50, 255, 50, int(255*self.opacity)) if i == 2 else (100, 100, 255, int(255*self.opacity))
            if i == 3: color = (255, 100, 100, int(255*self.opacity))
            if i == 0: color = (255, 50, 50, int(255*self.opacity))
                
            draw.rectangle([bx, by, bx+bar_w, self.height-10], fill=color)
        canvas.blit(img, self.x, self.y)


class Cloud(PObject):
    def __init__(self, x, y, speed=0.5):
        super().__init__(x, y, color="#FFFFFF")
        self.speed = speed
        
    def render(self, canvas):
        self.x += self.speed
        if self.x > 180:
            self.x = -40
            self.y = random.randint(10, 80)
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (40, 20), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        color = (200, 200, 255, int(150 * self.opacity))
        draw.ellipse([0, 5, 20, 15], fill=color)
        draw.ellipse([10, 0, 30, 15], fill=color)
        draw.ellipse([20, 5, 40, 15], fill=color)
        canvas.blit(img, self.x, self.y)

class Bird(PObject):
    def __init__(self, x, y, speed=1.0):
        super().__init__(x, y, color="#000000")
        self.speed = speed
        self.flap = 0.0
        
    def render(self, canvas):
        if not self.visible: return
        self.x -= self.speed
        self.flap += 0.2
        if self.x < -10:
            self.x = 160
            self.y = random.randint(20, 100)
            
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (14, 10), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        c = (0, 0, 0, int(255 * self.opacity))
        # Wing flap animation
        wy = 4 + int(math.sin(self.flap) * 3)
        draw.line([0, wy, 6, 5], fill=c, width=1)
        draw.line([6, 5, 12, wy], fill=c, width=1)
        canvas.blit(img, self.x, self.y)


# ═══════════════════════════════════════════════════════════
#  Main Scene
# ═══════════════════════════════════════════════════════════

class WindTurbineShort(Scene):
    def construct(self):
        # 0. Setup Environment
        self.config.background_color = "#87CEEB" # Sky blue
        
        cloud1 = Cloud(20, 30, speed=0.1)
        cloud2 = Cloud(90, 60, speed=0.15)
        bird = Bird(140, 40, speed=0.8)
        self.add(cloud1, cloud2, bird)
        
        # 1. SCENE 1: Hook
        title = PixelText("WHY 3 BLADES?", x=72, y=30, color="#FFFFFF", scale=1, align="center")
        self.add(title)
        
        turbine = Turbine(x=72, y=160, blades=3, radius=45)
        self.add(turbine)
        
        wake = WakeParticles(turbine)
        self.add(wake)
        wake.opacity = 0 
        
        self.camera.zoom = 1.0
        self.play(TypeWriter(title), duration=1.0)
        
        # Voice: Bella
        self.play_voiceover(
            "Have you ever looked at a massive wind turbine and wondered... why exactly three blades? "
            "Why not four to catch more wind, or just two to save money?",
            voice="af_bella"
        )
        
        # Voice: Adam
        self.play_voiceover(
            "Intuitively, more blades should mean more power, right? Let's look at a six-blade design.",
            voice="am_adam"
        )
        
        # 2. SCENE 2: Wake Effect
        self.play(FadeOut(title), duration=0.5)
        
        # Move camera in, morph to 6 blades
        turbine.blades = 6
        wake.opacity = 1.0
        
        self.play(
            CameraPan(self.camera, x=36, y=70, easing=ease_in_out),
            CameraZoom(self.camera, zoom=1.5, easing=ease_in_out),
            duration=1.5
        )
        self.camera.shake(intensity=1, duration=2.0)
        
        # Voice: Bella
        self.play_voiceover(
            "But fluid dynamics says otherwise! Every rotating blade creates a turbulent wake behind it. "
            "If blades are too close, they slam into the disturbed air, massively dropping efficiency.",
            voice="af_bella"
        )
        
        # 3. SCENE 3: Efficiency Curve
        self.play(
            CameraPan(self.camera, x=0, y=0, easing=ease_out),
            CameraZoom(self.camera, zoom=1.0, easing=ease_out),
            FadeOut(turbine), FadeOut(wake),
            duration=1.0
        )
        
        # Change sky to dark for chart
        self.config.background_color = "#0a0a1a"
        cloud1.visible = False; cloud2.visible = False; bird.visible = False
        
        chart_title = PixelText("AERODYNAMIC EFFICIENCY", x=72, y=40, color="#FFFFFF", scale=1, align="center")
        chart = InteractiveBarChart(x=12, y=80, width=120, height=100)
        self.add(chart_title, chart)
        self.play(FadeIn(chart_title), FadeIn(chart), duration=1.0)
        
        # Voice: Adam
        self.play_voiceover(
            "Ah, the wake effect. Going from two to three blades gives a huge boost. "
            "But four blades barely adds anything, while drastically increasing weight and cost.",
            voice="am_adam"
        )
        
        self.play(FadeOut(chart_title), FadeOut(chart), duration=1.0)
        self.remove(chart_title, chart)
        
        # 4. SCENE 4: Yaw Dynamics
        self.config.background_color = "#87CEEB" # Restore sky
        cloud1.visible = True; cloud2.visible = True
        
        turbine.blades = 2
        turbine.color = (255, 255, 255, 255)
        turbine.opacity = 1.0
        wake.opacity = 0.0
        turbine.yaw_scale = 1.0
        self.play(FadeIn(turbine), duration=1.0)
        
        # Voice: Bella
        self.play_voiceover(
            "Okay, so what about two blades? They’re cheaper and lighter! Let's test it.",
            voice="af_bella"
        )
        
        class YawAnimation(PObject):
            def interpolate(self, alpha):
                turbine.yaw_scale = max(0.1, 1.0 - alpha * 0.8)
                turbine.stress = alpha * 0.5
        
        # Camera zoom onto the tower hub while yawing
        self.play(
            YawAnimation(0,0),
            CameraPan(self.camera, x=36, y=100, easing=ease_in_out),
            CameraZoom(self.camera, zoom=1.5, easing=ease_in_out),
            duration=2.0
        )
        
        # Voice: Adam
        self.play_voiceover(
            "The problem is gyroscopic precession. When the wind direction changes, the turbine has to pivot—or yaw—to face it.",
            voice="am_adam"
        )
        
        # 5. SCENE 5: The Hammer
        turbine.stress = 1.0
        self.camera.shake(intensity=4, duration=8.0)
        
        # Voice: Bella
        self.play_voiceover(
            "Exactly. A two-blade rotor has vastly different inertia when horizontal compared to when vertical. "
            "It fights the yaw motor, violently hammering the tower!",
            voice="af_bella"
        )
        
        # 6. SCENE 6: The Goldilocks Zone
        self.play(
            CameraPan(self.camera, x=0, y=0, easing=ease_out),
            CameraZoom(self.camera, zoom=1.0, easing=ease_out),
            duration=1.0
        )
        
        turbine.blades = 3
        turbine.stress = 0.0
        turbine.yaw_scale = 1.0
        wake.opacity = 1.0
        self.camera._shake_offset_x = 0; self.camera._shake_offset_y = 0
        
        # Voice: Adam
        self.play_voiceover(
            "But with three blades, we get polar symmetry. The moment of inertia remains perfectly constant. "
            "It can yaw smoothly without ripping itself apart.",
            voice="am_adam"
        )
        
        # 7. SCENE 7: Conclusion
        self.config.background_color = "#0a0a1a" # Final dark starlit
        cloud1.visible = False; cloud2.visible = False
        final_text = PixelText("ENGINEERING\nPERFECTION", x=72, y=60, color="#00E436", align="center", max_chars=0)
        self.add(final_text)
        
        self.play(TypeWriter(final_text), duration=1.0)
        
        # Voice: Bella
        self.play_voiceover(
            "So perfectly balancing aerodynamic efficiency, structural stability, and cost... "
            "three blades isn't just a trend.",
            voice="af_bella"
        )
        
        # Voice: Adam
        self.play_voiceover("It's the engineering sweet spot.", voice="am_adam")
        
        self.wait(1.5)
        self.play(FadeOut(turbine), FadeOut(wake), FadeOut(final_text), duration=1.5)

if __name__ == "__main__":
    config = PixelConfig.portrait()
    config.upscale = 4
    
    scene = WindTurbineShort(config)
    output_path = os.path.join(os.path.dirname(__file__), "wind_turbine_yt_short_v2.mp4")
    scene.render(output_path)
    print(f"✅ V2 Video successfully encoded at {output_path}")
