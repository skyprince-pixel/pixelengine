#!/usr/bin/env python3
"""
The Mathematical Secret Behind Why Snowflakes Are Always Hexagonal And Symmetrical
A pixelart YouTube Short created natively with PixelEngine and Kokoro TTS.
"""

import os
import sys
import math
import random
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pixelengine import (
    Scene, PixelConfig, Sprite, PixelText, TypeWriter,
    FadeIn, FadeOut, MoveTo, AnimationGroup, Scale, Blink, ColorShift, Rotate,
    ease_in, ease_out, ease_in_out, bounce
)
from pixelengine.camera import CameraPan, CameraZoom
from pixelengine.pobject import PObject

class Molecule(PObject):
    def __init__(self, x, y, scale=1.0, show_angle=False):
        super().__init__(x, y)
        self.scale = scale
        self.show_angle = show_angle
        self.angle_progress = 0.0
        
    def render(self, canvas):
        if not self.visible: return
        w = int(40 * self.scale)
        if w <= 0: return
        img = Image.new("RGBA", (w, w), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        cx, cy = w//2, w//2
        r_O = int(6 * self.scale)
        r_H = int(4 * self.scale)
        bond_len = 12 * self.scale
        
        a1 = math.radians(90 - 52.25)
        a2 = math.radians(90 + 52.25)
        
        hx1, hy1 = cx + bond_len * math.cos(a1), cy + bond_len * math.sin(a1)
        hx2, hy2 = cx + bond_len * math.cos(a2), cy + bond_len * math.sin(a2)
        
        draw.line([cx, cy, hx1, hy1], fill=(200, 200, 200, int(255*self.opacity)), width=max(1, int(2*self.scale)))
        draw.line([cx, cy, hx2, hy2], fill=(200, 200, 200, int(255*self.opacity)), width=max(1, int(2*self.scale)))
        
        o_color = (255, 60, 60, int(255*self.opacity))
        h_color = (200, 200, 255, int(255*self.opacity))
        draw.ellipse([cx-r_O, cy-r_O, cx+r_O, cy+r_O], fill=o_color)
        draw.ellipse([hx1-r_H, hy1-r_H, hx1+r_H, hy1+r_H], fill=h_color)
        draw.ellipse([hx2-r_H, hy2-r_H, hx2+r_H, hy2+r_H], fill=h_color)
        
        if self.show_angle and self.angle_progress > 0:
            arc_r = int(8 * self.scale)
            arc_alpha = int(255 * self.opacity * self.angle_progress)
            draw.arc([cx-arc_r, cy-arc_r, cx+arc_r, cy+arc_r], start=90-52.25, end=90+52.25, fill=(0, 255, 255, arc_alpha), width=max(1, int(1*self.scale)))
            
        canvas.blit(img, self.x - w//2, self.y - w//2)

class HexGrid(PObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.progress = 0.0
        self.prism_progress = 0.0
        self.w, self.h = 144, 144
        
    def render(self, canvas):
        if not self.visible or (self.progress <= 0 and self.prism_progress <= 0): return
        
        img = Image.new("RGBA", (self.w, self.h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        cx, cy = self.w//2, self.h//2
        
        alpha_grid = int(255 * self.opacity * self.progress * (1.0 - self.prism_progress))
        if alpha_grid > 0:
            radius = 12
            for q in range(-3, 4):
                for r in range(-3, 4):
                    if abs(q+r) > 3: continue
                    px = cx + radius * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
                    py = cy + radius * (3/2 * r)
                    for i in range(6):
                        a1 = math.pi/3 * i
                        a2 = math.pi/3 * (i+1)
                        lx1, ly1 = px + radius/1.732 * math.cos(a1), py + radius/1.732 * math.sin(a1)
                        lx2, ly2 = px + radius/1.732 * math.cos(a2), py + radius/1.732 * math.sin(a2)
                        draw.line([lx1, ly1, lx2, ly2], fill=(150, 150, 150, alpha_grid), width=1)
                        
            for q in range(-3, 4):
                for r in range(-3, 4):
                    if abs(q+r) > 3: continue
                    px = cx + radius * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
                    py = cy + radius * (3/2 * r)
                    o_c = (255, 60, 60, alpha_grid)
                    draw.ellipse([px-2, py-2, px+2, py+2], fill=o_c)
        
        alpha_prism = int(255 * self.opacity * self.prism_progress)
        if alpha_prism > 0:
            prism_r = 40
            pts = []
            for i in range(6):
                px = cx + prism_r * math.cos(math.pi/3 * i)
                py = cy + prism_r * math.sin(math.pi/3 * i)
                pts.append((px, py))
            draw.polygon(pts, fill=(0, 200, 255, int(alpha_prism * 0.5)), outline=(255,255,255,alpha_prism))
            for px, py in pts:
                draw.ellipse([px-2, py-2, px+2, py+2], fill=(255,255,255,alpha_prism))
                
        canvas.blit(img, self.x - cx, self.y - cy)

class SnowflakeFractal(PObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.growth = 0.0
        self.complexity = 0.0
        self.rotation = 0.0
        self.w, self.h = 100, 100
        
    def render(self, canvas):
        if not self.visible or self.growth <= 0: return
        img = Image.new("RGBA", (self.w, self.h), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        cx, cy = self.w//2, self.h//2
        alpha = int(255 * self.opacity)
        color = (255, 255, 255, alpha)
        
        def draw_branch(bx, by, angle, length, depth, max_depth, t_growth):
            if depth > max_depth or t_growth <= 0: return
            actual_len = length * t_growth
            ex = bx + actual_len * math.cos(angle)
            ey = by + actual_len * math.sin(angle)
            draw.line([bx, by, ex, ey], fill=color, width=max(1, 2-depth))
            
            if depth < max_depth and t_growth > 0.5:
                sub_t = (t_growth - 0.5) * 2.0
                nl = length * 0.4
                for frac in [0.4, 0.7]:
                    sx = bx + actual_len * frac * math.cos(angle)
                    sy = by + actual_len * frac * math.sin(angle)
                    draw_branch(sx, sy, angle + math.pi/3, nl, depth+1, max_depth, sub_t * self.complexity)
                    draw_branch(sx, sy, angle - math.pi/3, nl, depth+1, max_depth, sub_t * self.complexity)
        
        for i in range(6):
            a = self.rotation + i * math.pi/3
            draw_branch(cx, cy, a, 35.0, 0, 2, self.growth)
            
        canvas.blit(img, self.x - cx, self.y - cy)

class SimpleSnowflake(PObject):
    def __init__(self, x, y, radius=10):
        super().__init__(x, y)
        self.radius = radius
        self.rotation = 0.0
        self.w = radius*2+4
        
    def render(self, canvas):
        if not self.visible: return
        self.rotation += 0.02
        img = Image.new("RGBA", (self.w, self.w), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        cx, cy = self.w//2, self.w//2
        c = (255,255,255, int(255 * self.opacity))
        for i in range(6):
            a = self.rotation + i * math.pi/3
            ex, ey = cx + self.radius * math.cos(a), cy + self.radius * math.sin(a)
            draw.line([cx, cy, ex, ey], fill=c, width=1)
        canvas.blit(img, self.x - cx, self.y - cy)

class SnowflakeShort(Scene):
    def construct(self):
        self.config.background_color = "#0a0a1a"
        
        # SCENE 1: Hook
        flake = SimpleSnowflake(72, 120, radius=20)
        self.add(flake)
        title = PixelText("6 SIDES?", x=72, y=60, color="#ffffff", align="center", max_chars=0)
        self.add(title)
        
        self.play(FadeIn(flake), TypeWriter(title), duration=1.0)
        self.play_voiceover("Have you ever noticed that every single snowflake has exactly six sides? You will never find a five-sided or seven-sided snowflake in nature. But why?", voice="af_bella")
        
        # SCENE 2: The Molecule
        self.play(FadeOut(flake), FadeOut(title), duration=0.5)
        self.remove(flake, title)
        
        mol = Molecule(72, 128, scale=0.1)
        self.add(mol)
        
        self.play(FadeIn(mol), duration=0.5)
        
        class MolScale(PObject):
            def interpolate(self, alpha):
                mol.scale = 0.1 + ease_out(alpha) * 1.9
                mol.y = 128 - alpha*28
                
        self.play(MolScale(0,0), duration=1.5)
        self.play_voiceover("To understand the secret, we have to look ten million times smaller... at a single water molecule. One oxygen atom, two hydrogen atoms.", voice="af_bella")
        
        # SCENE 3: The Angle
        class MolAngle(PObject):
            def interpolate(self, alpha):
                mol.show_angle = True
                mol.angle_progress = alpha
        label = PixelText("104.5 DEG", x=72, y=50, color="#00ffff", align="center", max_chars=0)
        self.add(label)
        self.play(TypeWriter(label), MolAngle(0,0), duration=1.0)
        self.play_voiceover("Because of quantum mechanics, these atoms connect at a very specific, magical angle: 104.5 degrees.", voice="af_bella")
        
        # SCENE 4: The Lattice
        self.play(FadeOut(mol), FadeOut(label), duration=0.5)
        self.remove(mol, label)
        
        grid = HexGrid(72, 128)
        self.add(grid)
        
        class GridFade(PObject):
            def interpolate(self, alpha):
                grid.progress = alpha
        self.play(GridFade(0,0), duration=1.0)
        self.play_voiceover("When water freezes, the molecules lock together using hydrogen bonds. This 104.5-degree angle forces them into a spacious, hexagonal crystal lattice.", voice="af_bella")
        
        # SCENE 5: The Prism
        class PrismForm(PObject):
            def interpolate(self, alpha):
                grid.prism_progress = alpha
        self.play(PrismForm(0,0), duration=1.5)
        self.play_voiceover("As the crystal falls through the clouds, it starts as a tiny hexagonal prism. The six corners stick out the furthest into the humid air.", voice="af_bella")
        
        # SCENE 6: Symmetrical Growth
        self.play(FadeOut(grid), duration=0.5)
        
        final_flake = SnowflakeFractal(72, 128)
        self.add(final_flake)
        
        class FlakeGrow(PObject):
            def interpolate(self, alpha):
                final_flake.growth = alpha
                final_flake.complexity = 0.0
        self.play(FlakeGrow(0,0), duration=2.0)
        self.play_voiceover("Because they stick out, these six corners grab moisture faster than the flat sides, growing six identical branches simultaneously.", voice="af_bella")
        
        # SCENE 7: Uniqueness
        parent_scene = self
        class FlakeComplex(PObject):
            def interpolate(self, alpha):
                final_flake.complexity = alpha
                final_flake.rotation = math.sin(alpha * math.pi) * 0.2
                r = min(255, int(10 + math.sin(alpha*math.pi)*20))
                g = min(255, int(10 + math.sin(alpha*math.pi)*40))
                b = min(255, int(26 + math.sin(alpha*math.pi)*60))
                parent_scene.config.background_color = f"#{r:02x}{g:02x}{b:02x}"
                
        self.play(FlakeComplex(0,0), duration=3.0)
        self.play_voiceover("Every snowflake takes a unique path through the sky, experiencing different temperatures and humidity. But since the flake is so tiny, all six arms experience the exact same conditions at the exact same time.", voice="af_bella")
        
        # SCENE 8: Conclusion
        self.play(
            CameraZoom(self.camera, zoom=0.5, easing=ease_out),
            CameraPan(self.camera, x=36, y=64, easing=ease_out),
            duration=1.5
        )
        
        self.config.background_color = "#0a0a1a"
        end_text = PixelText("NATURES GEOMETRY", x=72, y=200, color="#55ff55", align="center", max_chars=0)
        self.add(end_text)
        self.play(TypeWriter(end_text), duration=1.0)
        
        self.play_voiceover("The breathtaking symmetry of a snowflake isn't magic... it's just the macroscopic reflection of atomic geometry.", voice="af_bella")
        
        self.wait(1.5)
        self.play(FadeOut(final_flake), FadeOut(end_text), duration=1.0)

if __name__ == "__main__":
    config = PixelConfig.portrait()
    config.upscale = 4
    scene = SnowflakeShort(config)
    output_path = os.path.join(os.path.dirname(__file__), "snowflake_pixelengine_short.mp4")
    scene.render(output_path)
    print(f"✅ Video successfully encoded at {output_path}")
