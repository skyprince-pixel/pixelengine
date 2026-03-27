"""PixelEngine scene composition — chain multiple scenes into one video.

Renders multiple ``Scene`` subclasses sequentially, optionally blending
their boundaries with transitions, and outputs a single MP4.

Classes:
    Compose — Multi-scene video builder.

Usage::

    from pixelengine import Compose

    Compose(IntroScene, MainScene, OutroScene,
            transition_duration=0.5).render("full_video.mp4")
"""
import os
import sys
import time
import tempfile
from PIL import Image
import numpy as np

from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.renderer import Renderer
from pixelengine.sound import SoundTimeline, mux_audio_video


class Compose:
    """Chain multiple Scene classes into a single continuous video.

    Each scene is instantiated with the shared ``PixelConfig``, rendered
    to frames, then all frames are concatenated with optional cross-fade
    transitions between scenes.

    Args:
        *scene_classes: Scene subclasses (not instances) to render in order.
        config: Shared PixelConfig for all scenes.
        transition_duration: Seconds of cross-fade between scenes (0 = cut).

    Usage::

        class Intro(Scene):
            def construct(self): ...

        class Main(Scene):
            def construct(self): ...

        Compose(Intro, Main, config=PixelConfig.portrait(),
                transition_duration=0.5).render("output.mp4")
    """

    def __init__(self, *scene_classes, config: PixelConfig = None,
                 transition_duration: float = 0.5):
        self.scene_classes = scene_classes
        self.config = config or DEFAULT_CONFIG
        self.transition_duration = max(0.0, transition_duration)

    def render(self, output_path: str = "composed_output.mp4"):
        """Build all scenes, crossfade between them, and encode to video."""
        print(f"[PixelEngine Compose] Rendering {len(self.scene_classes)} scenes")
        print(f"  Config: {self.config.canvas_width}×{self.config.canvas_height} "
              f"→ {self.config.output_width}×{self.config.output_height}")
        print(f"  Transition: {self.transition_duration}s cross-fade")

        all_frames = []
        merged_sound = SoundTimeline()
        time_offset = 0.0  # Cumulative time for audio offset

        for i, scene_cls in enumerate(self.scene_classes):
            scene_name = scene_cls.__name__
            print(f"\n  [{i+1}/{len(self.scene_classes)}] Building: {scene_name}")

            # Instantiate and build the scene
            scene = scene_cls(self.config)
            scene._frames = []
            scene._current_time = 0
            scene._sound_timeline = SoundTimeline()
            scene._last_tw_char_count = {}
            scene._render_start_time = time.time()

            # Temporarily suppress auto-sound for cleaner composition
            scene.construct()
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

            scene_frames = scene._frames
            scene_duration = len(scene_frames) / self.config.fps
            print(f"    Captured {len(scene_frames)} frames ({scene_duration:.1f}s)")

            # Merge sound events with time offset
            for evt_time, sfx in scene._sound_timeline._events:
                merged_sound.add(sfx, evt_time + time_offset)

            # Cross-fade transition with previous scene
            if i > 0 and self.transition_duration > 0 and len(all_frames) > 0 and len(scene_frames) > 0:
                trans_frames = int(self.transition_duration * self.config.fps)
                trans_frames = min(trans_frames, len(all_frames), len(scene_frames))

                if trans_frames > 0:
                    # Pop tail frames from previous scene
                    prev_tail = all_frames[-trans_frames:]

                    # Head frames from current scene
                    curr_head = scene_frames[:trans_frames]

                    # Blend them
                    for j in range(trans_frames):
                        alpha = (j + 1) / (trans_frames + 1)
                        blended = Image.blend(prev_tail[j], curr_head[j], alpha)
                        all_frames[-(trans_frames - j)] = blended

                    # Add remaining current frames (skip the head we already blended)
                    all_frames.extend(scene_frames[trans_frames:])
                    # Adjust time offset (subtract overlap)
                    time_offset += scene_duration - self.transition_duration
                else:
                    all_frames.extend(scene_frames)
                    time_offset += scene_duration
            else:
                all_frames.extend(scene_frames)
                time_offset += scene_duration

        total_seconds = len(all_frames) / self.config.fps
        print(f"\n[PixelEngine Compose] Total: {len(all_frames)} frames ({total_seconds:.1f}s)")

        if not all_frames:
            print("[PixelEngine Compose] Warning: No frames captured!")
            return

        renderer = Renderer(self.config)
        sound_count = merged_sound.event_count

        if sound_count > 0:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_video = os.path.join(tmpdir, "video_only.mp4")
                tmp_audio = os.path.join(tmpdir, "audio.wav")
                renderer.encode(all_frames, tmp_video)
                merged_sound.save_wav(tmp_audio, total_seconds)
                mux_audio_video(tmp_video, tmp_audio, output_path)
            size = os.path.getsize(output_path) / 1024
            print(f"  Output: {output_path} ({size:.1f} KB) [video+audio]")
        else:
            renderer.encode(all_frames, output_path)
            size = os.path.getsize(output_path) / 1024
            print(f"  Output: {output_path} ({size:.1f} KB) [video]")

        print(f"[PixelEngine Compose] ✓ Composed video saved to: {output_path}")
