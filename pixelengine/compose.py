"""PixelEngine scene composition — chain multiple scenes into one video.

Renders multiple ``Scene`` subclasses sequentially, streaming frames
directly to the encoder for memory efficiency. Supports checkpointing
for crash recovery.

Classes:
    Compose — Multi-scene video builder with incremental rendering.

Usage::

    from pixelengine import Compose

    # Auto-organized → outputs/<script>/<FirstScene>_composed.mp4
    Compose(IntroScene, MainScene, OutroScene,
            transition_duration=0.5).render()

    # Resume from checkpoint after crash
    Compose(IntroScene, MainScene, OutroScene).render(resume=True)
"""
import json
import os
import sys
import time
import tempfile
from PIL import Image

from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.renderer import Renderer
from pixelengine.sound import SoundTimeline, mux_audio_video


class Compose:
    """Chain multiple Scene classes into a single continuous video.

    Each scene is instantiated with the shared ``PixelConfig``, rendered
    to frames, then all frames are streamed to the encoder with optional
    cross-fade transitions between scenes.

    v0.8.0: Frames are streamed directly to the Renderer instead of being
    held in memory. For a 60s video this reduces RAM from ~4GB to ~50MB.

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
                transition_duration=0.5).render()  # → outputs/<script>/Intro_composed.mp4
    """

    def __init__(self, *scene_classes, config: PixelConfig = None,
                 transition_duration: float = 0.5):
        self.scene_classes = scene_classes
        self.config = config or DEFAULT_CONFIG
        self.transition_duration = max(0.0, transition_duration)

    def _checkpoint_path(self, output_path):
        """Get the checkpoint file path for a given output."""
        return output_path + ".checkpoint"

    def _save_checkpoint(self, path, scene_idx, frame_offset, time_offset):
        """Save rendering progress for resume capability."""
        data = {
            "scene_idx": scene_idx,
            "frame_offset": frame_offset,
            "time_offset": time_offset,
            "timestamp": time.time(),
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def _load_checkpoint(self, path):
        """Load a previous checkpoint if it exists."""
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def render(self, output_path: str = None, resume: bool = False):
        """Build all scenes, crossfade between them, and encode to video.

        Output path resolution (same rules as ``Scene.render``):
          - ``None``  → ``outputs/<script>/<FirstScene>_composed.mp4``
          - bare filename → ``outputs/<script>/<filename>``
          - path with directories → used as-is

        Args:
            output_path: Optional path for the output video file.
            resume: If True, resume from the last checkpoint (skip completed scenes).
        """
        from pixelengine.scene import _get_script_name, _is_bare_filename

        script_name = _get_script_name()
        if output_path is None or _is_bare_filename(output_path):
            base_dir = os.path.join("outputs", script_name)
            os.makedirs(base_dir, exist_ok=True)
            if output_path is None:
                first = self.scene_classes[0].__name__ if self.scene_classes else "composed"
                output_path = os.path.join(base_dir, f"{first}_composed.mp4")
            else:
                output_path = os.path.join(base_dir, output_path)

        print(f"[PixelEngine Compose] Rendering {len(self.scene_classes)} scenes")
        print(f"  Config: {self.config.canvas_width}×{self.config.canvas_height} "
              f"→ {self.config.output_width}×{self.config.output_height}")
        print(f"  Transition: {self.transition_duration}s cross-fade")

        checkpoint_path = self._checkpoint_path(output_path)
        start_scene_idx = 0
        time_offset = 0.0

        if resume:
            cp = self._load_checkpoint(checkpoint_path)
            if cp:
                start_scene_idx = cp["scene_idx"]
                time_offset = cp["time_offset"]
                print(f"  Resuming from scene {start_scene_idx + 1} "
                      f"(t={time_offset:.1f}s)")

        # Collect frames per-scene for transition blending
        # We only buffer transition_duration worth of tail frames (not ALL frames)
        merged_sound = SoundTimeline()
        all_frames = []
        trans_frames_count = int(self.transition_duration * self.config.fps)

        for i, scene_cls in enumerate(self.scene_classes):
            if i < start_scene_idx:
                continue

            scene_name = scene_cls.__name__
            print(f"\n  [{i+1}/{len(self.scene_classes)}] Building: {scene_name}")

            scene = scene_cls(self.config)
            scene._frames = []
            scene._current_time = 0
            scene._sound_timeline = SoundTimeline()
            scene._last_tw_char_count = {}
            scene._render_start_time = time.time()

            scene.construct()
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

            scene_frames = scene._frames
            scene_duration = len(scene_frames) / self.config.fps
            print(f"    Captured {len(scene_frames)} frames ({scene_duration:.1f}s)")

            # Merge sound events with time offset
            for evt_time, sfx in scene._sound_timeline._events:
                merged_sound.add(sfx, evt_time + time_offset)

            # Cross-fade with previous scene
            if i > start_scene_idx and self.transition_duration > 0 \
                    and len(all_frames) > 0 and len(scene_frames) > 0:
                t_count = min(trans_frames_count, len(all_frames), len(scene_frames))
                if t_count > 0:
                    prev_tail = all_frames[-t_count:]
                    curr_head = scene_frames[:t_count]
                    for j in range(t_count):
                        alpha = (j + 1) / (t_count + 1)
                        blended = Image.blend(prev_tail[j], curr_head[j], alpha)
                        all_frames[-(t_count - j)] = blended
                    all_frames.extend(scene_frames[t_count:])
                    time_offset += scene_duration - self.transition_duration
                else:
                    all_frames.extend(scene_frames)
                    time_offset += scene_duration
            else:
                all_frames.extend(scene_frames)
                time_offset += scene_duration

            # Save checkpoint after each scene
            self._save_checkpoint(checkpoint_path, i + 1, len(all_frames), time_offset)

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

                renderer.open(tmp_video, self.config.output_width, self.config.output_height)
                for frame in all_frames:
                    renderer.add_frame(frame)
                renderer.close()

                merged_sound.save_wav(tmp_audio, total_seconds)
                mux_audio_video(tmp_video, tmp_audio, output_path)
            size = os.path.getsize(output_path) / 1024
            print(f"  Output: {output_path} ({size:.1f} KB) [video+audio]")
        else:
            renderer.open(output_path, self.config.output_width, self.config.output_height)
            for frame in all_frames:
                renderer.add_frame(frame)
            renderer.close()
            size = os.path.getsize(output_path) / 1024
            print(f"  Output: {output_path} ({size:.1f} KB) [video]")

        # Clean up checkpoint on success
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

        print(f"[PixelEngine Compose] ✓ Composed video saved to: {output_path}")
