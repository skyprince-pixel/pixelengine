import os
import sys
import math
import numpy as np
import subprocess
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon, Circle, Arc

FPS = 30
W_IN, H_IN = 10.8, 19.2
DPI = 100
BG_COLOR = "#0f0f23"

scenes_text = [
    "Have you ever noticed that every single snowflake has exactly six sides? You will never find a five-sided or seven-sided snowflake in nature. But why?",
    "To understand the secret, we have to look ten million times smaller... at a single water molecule. One oxygen atom, two hydrogen atoms.",
    "Because of quantum mechanics, these atoms connect at a very specific, magical angle: 104.5 degrees.",
    "When water freezes, the molecules lock together using hydrogen bonds. This 104.5-degree angle forces them into a spacious, hexagonal crystal lattice.",
    "As the crystal falls through the clouds, it starts as a tiny hexagonal prism. The six corners stick out the furthest into the humid air.",
    "Because they stick out, these six corners grab moisture faster than the flat sides, growing six identical branches simultaneously.",
    "Every snowflake takes a unique path through the sky, experiencing different temperatures and humidity. But since the flake is so tiny, all six arms experience the exact same conditions.",
    "The breathtaking symmetry of a snowflake isn't magic... it's just the macroscopic reflection of atomic geometry."
]

def ease(t):
    return t * t * (3.0 - 2.0 * t)

def generate_audio():
    print("Generating or loading audio via Kokoro...")
    from kokoro_onnx import Kokoro
    CACHE_DIR = os.path.expanduser("~/.cache/pixelengine/kokoro")
    ONNX_FILE = os.path.join(CACHE_DIR, "kokoro-v0_19.onnx")
    VOICES_FILE = os.path.join(CACHE_DIR, "voices.bin")
    
    if not os.path.exists(ONNX_FILE) or not os.path.exists(VOICES_FILE):
        print("Downloading Kokoro models...")
        os.makedirs(CACHE_DIR, exist_ok=True)
        subprocess.run(["curl", "-L", "-o", ONNX_FILE, "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx"])
        subprocess.run(["curl", "-L", "-o", VOICES_FILE, "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin"])

    kokoro = Kokoro(ONNX_FILE, VOICES_FILE)
    
    audio_chunks = []
    durations = []
    sr = 24000
    
    for i, txt in enumerate(scenes_text):
        out_path = f"scene_{i}.wav"
        if not os.path.exists(out_path):
            if kokoro:
                samples, req_sr = kokoro.create(txt, voice="af_bella", speed=0.95, lang="en-us")
            else:
                samples, req_sr = VoiceOver.generate(txt, voice="af_bella")
            padding = np.zeros(int(0.5 * req_sr), dtype=np.float32)
            final_samples = np.concatenate([samples, padding])
            sf.write(out_path, final_samples, req_sr)
            sr = req_sr
            print(f"Generated {out_path}")
            
        data, req_sr = sf.read(out_path)
        audio_chunks.append(data)
        durations.append(len(data) / req_sr)
        
    full_audio = np.concatenate(audio_chunks)
    sf.write("full_audio.wav", full_audio, sr)
    return durations

def render_video(durations):
    total_duration = sum(durations)
    total_frames = int(total_duration * FPS) + 30
    
    fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=DPI, facecolor=BG_COLOR)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    
    scene_start_times = [0]
    for d in durations[:-1]:
        scene_start_times.append(scene_start_times[-1] + d)
        
    def get_scene_t(time_sec):
        for i in range(len(scene_start_times)-1):
            if scene_start_times[i] <= time_sec < scene_start_times[i+1]:
                return i, (time_sec - scene_start_times[i]) / durations[i]
        i = len(scene_start_times) - 1
        if time_sec >= scene_start_times[i]:
            return i, min(1.0, (time_sec - scene_start_times[i]) / durations[i])
        return 0, 0.0

    def draw_molecule(x, y, scale=1.0, alpha=1.0, show_angle=False, angle_t=0.0):
        O_r = 0.4 * scale
        H_r = 0.2 * scale
        r = 1.0 * scale
        th1 = math.radians(90 - 104.5/2)
        th2 = math.radians(90 + 104.5/2)
        hx1, hy1 = x + r * math.cos(th1), y + r * math.sin(th1)
        hx2, hy2 = x + r * math.cos(th2), y + r * math.sin(th2)
        
        ax.plot([x, hx1], [y, hy1], color="#ffffff", lw=4*scale, alpha=np.clip(alpha,0,1), zorder=1)
        ax.plot([x, hx2], [y, hy2], color="#ffffff", lw=4*scale, alpha=np.clip(alpha,0,1), zorder=1)
        ax.add_patch(Circle((x, y), O_r, color="#ff4444", alpha=np.clip(alpha,0,1), zorder=2))
        ax.add_patch(Circle((hx1, hy1), H_r, color="#ddddff", alpha=np.clip(alpha,0,1), zorder=2))
        ax.add_patch(Circle((hx2, hy2), H_r, color="#ddddff", alpha=np.clip(alpha,0,1), zorder=2))
        
        if show_angle and angle_t > 0:
            arc_radius = 0.6 * scale
            arc = Arc((x, y), arc_radius*2, arc_radius*2, angle=0, theta1=90-104.5/2, theta2=90+104.5/2, 
                      color="#00ffff", lw=3, alpha=np.clip(alpha*angle_t,0,1))
            ax.add_patch(arc)
            ax.text(x, y + 0.8*scale, "104.5°", color="#00ffff", ha="center", va="center", 
                    fontsize=20*scale, alpha=np.clip(alpha*angle_t,0,1), fontweight="bold")

    def draw_branch(x, y, angle, length, depth, max_depth, t_growth):
        if depth > max_depth or t_growth <= 0: return []
        actual_len = length * t_growth
        ex, ey = x + actual_len * math.cos(angle), y + actual_len * math.sin(angle)
        lines = [[(x, y), (ex, ey)]]
        
        if depth < max_depth and t_growth > 0.5:
            sub_t = (t_growth - 0.5) * 2.0
            nl = length * 0.4
            for fraction in [0.4, 0.7]:
                sx, sy = x + (actual_len * fraction) * math.cos(angle), y + (actual_len * fraction) * math.sin(angle)
                lines += draw_branch(sx, sy, angle + math.pi/3, nl, depth+1, max_depth, sub_t)
                lines += draw_branch(sx, sy, angle - math.pi/3, nl, depth+1, max_depth, sub_t)
        return lines

    def update(frame):
        ax.clear()
        ax.set_facecolor(BG_COLOR)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-16, 16)
        ax.axis("off")
        
        time_sec = frame / FPS
        scene_idx, t = get_scene_t(time_sec)
        t_e = ease(t)
        
        if scene_idx == 0:
            rot = t * 2 * math.pi
            alpha = np.clip(min(1.0, t*4), 0, 1)
            lines = []
            for i in range(6):
                a = rot + i * math.pi / 3
                ex, ey = 5 * math.cos(a), 5 * math.sin(a)
                lines.append([(0,0), (ex, ey)])
                for fract in [0.4, 0.7]:
                    sx, sy = fract * ex, fract * ey
                    lines.append([(sx,sy), (sx+1.5*math.cos(a+math.pi/3), sy+1.5*math.sin(a+math.pi/3))])
                    lines.append([(sx,sy), (sx+1.5*math.cos(a-math.pi/3), sy+1.5*math.sin(a-math.pi/3))])
            lc = LineCollection(lines, color="#ffffff", lw=2, alpha=alpha)
            ax.add_collection(lc)
            
        elif scene_idx == 1:
            alpha = np.clip(min(t*4, (1-t)*10 + 1), 0, 1)
            draw_molecule(0, 0, scale=1.0 + t_e * 2.0, alpha=alpha)
            
        elif scene_idx == 2:
            draw_molecule(0, 0, scale=3.0, alpha=1.0, show_angle=True, angle_t=np.clip(t_e*2,0,1))
            
        elif scene_idx == 3:
            alpha_mol = np.clip(1.0 - t_e*2, 0, 1)
            if alpha_mol > 0:
                draw_molecule(0, 0, scale=3.0, show_angle=True, angle_t=alpha_mol, alpha=alpha_mol)
            grid_alpha = np.clip((t - 0.3) * 2.0, 0, 1)
            if grid_alpha > 0:
                for hex_x in [-2, 0, 2]:
                    for hex_y in [-2, 0, 2]:
                        cx, cy = hex_x * 3, hex_y * 1.732 * 2
                        if abs(hex_x) % 2 == 1: cy += 1.732
                        for i in range(6):
                            a1, a2 = i * math.pi/3, (i+1) * math.pi/3
                            x1, y1 = cx + math.cos(a1)*1.5, cy + math.sin(a1)*1.5
                            x2, y2 = cx + math.cos(a2)*1.5, cy + math.sin(a2)*1.5
                            ax.plot([x1, x2], [y1, y2], color="#aaaaaa", lw=3, alpha=grid_alpha, zorder=0)
                            ax.add_patch(Circle((x1, y1), 0.3, color="#ff4444", alpha=grid_alpha, zorder=1))
                            
        elif scene_idx == 4:
            grid_alpha = np.clip(1.0 - t_e * 2.0, 0, 1)
            poly_alpha = np.clip(t_e * 2.0 - 0.5, 0, 1) * 0.4
            y_offset = -3 * t_e
            pts = [[4.0 * math.cos(i * math.pi/3), y_offset + 4.0 * math.sin(i * math.pi/3)] for i in range(6)]
            ax.add_patch(Polygon(pts, closed=True, facecolor="#00ffff", edgecolor="#ffffff", lw=4, alpha=poly_alpha))
            corner_alpha = np.clip((t - 0.5)*2.0, 0, 1)
            if corner_alpha > 0:
                for px, py in pts: ax.add_patch(Circle((px, py), 0.6, color="#ffffff", alpha=corner_alpha*0.8))
        
        elif scene_idx == 5:
            pts = [[4.0 * math.cos(i * math.pi/3), -3 + 4.0 * math.sin(i * math.pi/3)] for i in range(6)]
            ax.add_patch(Polygon(pts, closed=True, facecolor="#00ffff", edgecolor="#ffffff", lw=4, alpha=0.4))
            for i in range(6):
                angle = i * math.pi/3
                px, py = 4.0 * math.cos(angle), -3 + 4.0 * math.sin(angle)
                lines = draw_branch(px, py, angle, length=4.0, depth=0, max_depth=1, t_growth=np.clip(t_e,0,1))
                ax.add_collection(LineCollection(lines, color="#ffffff", lw=3, alpha=np.clip(t_e*2, 0, 1)))
                
        elif scene_idx == 6:
            rot = math.sin(t * math.pi) * 0.1
            lines = []
            for i in range(6):
                lines += draw_branch(0, -3, rot + i * math.pi/3, length=8.0, depth=0, max_depth=2, t_growth=np.clip(0.3 + 0.7*t_e,0,1))
            ax.add_collection(LineCollection(lines, color="#ffffff", lw=2, alpha=1.0))
            env_color = plt.cm.Blues(0.2 + 0.3 * math.sin(t * math.pi * 4))
            ax.set_facecolor(env_color)

        elif scene_idx >= 7:
            alpha_flake = np.clip(1.0 - t_e*2.0, 0, 1)
            if alpha_flake > 0:
                lines = []
                for i in range(6): lines += draw_branch(0, -3, i * math.pi/3, length=8.0, depth=0, max_depth=2, t_growth=1.0)
                ax.add_collection(LineCollection(lines, color="#ffffff", lw=2, alpha=alpha_flake))
                
            np.random.seed(42)
            fl = []
            for f in range(50):
                fx = (np.random.rand() - 0.5) * 20
                fy = 20 - (np.random.rand() * 40 + t_e * 20) % 40
                fs = 0.5 + np.random.rand() * 1.5
                for i in range(6):
                    a = i * math.pi/3 + t * 2
                    fl.append([(fx, fy), (fx + fs*math.cos(a), fy + fs*math.sin(a))])
            ax.add_collection(LineCollection(fl, color="#ffffff", lw=1, alpha=np.clip(t_e * 2.0, 0, 1)*0.5))

    print("Rendering video frames...")
    anim = FuncAnimation(fig, update, frames=total_frames, interval=1000/FPS)
    anim.save("raw_video.mp4", fps=FPS, progress_callback=lambda i, n: print(f"Frame {i}/{n} ({(i/n)*100:.1f}%)", end="\r"))
    plt.close(fig)
    print("\nRendering complete.")

def main():
    durations = generate_audio()
    render_video(durations)
    print("Muxing final video...")
    subprocess.run(["ffmpeg", "-y", "-i", "raw_video.mp4", "-i", "full_audio.wav", "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", "snowflake_short.mp4"])
    print("Done. Saved as snowflake_short.mp4")

if __name__ == "__main__":
    main()
