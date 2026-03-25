"""PixelEngine Scene — the core orchestrator for animations and sound."""
import os
import tempfile
from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.canvas import Canvas
from pixelengine.camera import Camera
from pixelengine.renderer import Renderer
from pixelengine.sound import SoundFX, SoundTimeline, mux_audio_video


class Scene:
    """Base scene class. Subclass and override ``construct()`` to build animations.

    Usage::

        class MyScene(Scene):
            def construct(self):
                rect = Rect(20, 10, color="#FF004D")
                self.add(rect)
                self.play_sound(SoundFX.coin())
                self.wait(2.0)

        MyScene().render("output.mp4")

    Auto-sound (enabled by default)::

        scene.auto_sound = True  # TypeWriter → typing clicks, etc.
    """

    def __init__(self, config: PixelConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.canvas = Canvas(
            self.config.canvas_width,
            self.config.canvas_height,
            self.config.background_color,
        )
        self.camera = Camera(self.config.canvas_width, self.config.canvas_height)
        self._objects: list = []
        self._frames: list = []

        # Sound
        self._sound_timeline = SoundTimeline()
        self._current_time: float = 0  # Tracks elapsed time during construct()
        self.auto_sound: bool = True   # Enable auto-generated sounds

    # ── User overrides ──────────────────────────────────────

    def construct(self):
        """Override this method to define your scene."""
        raise NotImplementedError(
            "Subclass Scene and implement construct()"
        )

    # ── Object management ───────────────────────────────────

    def add(self, *objects) -> "Scene":
        """Add one or more PObjects to the scene."""
        for obj in objects:
            if obj not in self._objects:
                self._objects.append(obj)
        return self

    def remove(self, *objects) -> "Scene":
        """Remove PObjects from the scene."""
        for obj in objects:
            if obj in self._objects:
                self._objects.remove(obj)
        return self

    # ── Sound ───────────────────────────────────────────────

    def play_sound(self, sfx: SoundFX, at: float = None):
        """Place a sound effect at a specific time.

        Args:
            sfx: A SoundFX instance (e.g. SoundFX.coin()).
            at: Time in seconds. If None, uses current scene time.
        """
        time = at if at is not None else self._current_time
        self._sound_timeline.add(sfx, time)

    def play_voiceover(self, text: str, voice: str = "af_bella", speed: float = 1.0):
        """Generate and play a Kokoro AI voiceover, holding the frame
        for the duration of the speech.

        Args:
            text: Text for the voiceover to speak.
            voice: Voice ID (default 'af_bella').
            speed: Speed multiplier (default 1.0).
        """
        from pixelengine.voiceover import VoiceOver
        sfx, duration = VoiceOver.generate(text, voice=voice, speed=speed)
        self.play_sound(sfx)
        print(f"[PixelEngine] VoiceOver: '{text[:30]}...' ({duration:.2f}s)")
        self.wait(duration)

    # ── Timing ──────────────────────────────────────────────

    def wait(self, seconds: float = 1.0):
        """Hold the current frame for the given duration."""
        num_frames = max(1, int(seconds * self.config.fps))
        for _ in range(num_frames):
            self._capture_frame()

    def play(self, *animations, duration: float = 1.0, sound: SoundFX = None):
        """Play one or more animations over the given duration.

        Args:
            *animations: Animation objects to play.
            duration: How long the animation runs (seconds).
            sound: Optional SoundFX to play at the start of this animation.
        """
        # Place explicit sound
        if sound is not None:
            self.play_sound(sound)

        # Auto-sound detection
        if self.auto_sound:
            self._auto_sound_for_animations(animations)

        num_frames = max(1, int(duration * self.config.fps))
        for frame_idx in range(num_frames):
            alpha = frame_idx / max(1, num_frames - 1)
            for anim in animations:
                if hasattr(anim, "interpolate"):
                    anim.interpolate(alpha)

                    # TypeWriter auto-sound: click on each new character
                    if self.auto_sound and hasattr(anim, 'target') and \
                       hasattr(anim, 'total_chars'):
                        self._auto_typewriter_sound(anim, alpha, frame_idx)

            self._capture_frame()

    def _auto_sound_for_animations(self, animations):
        """Add auto-sounds based on animation types."""
        for anim in animations:
            anim_type = type(anim).__name__

            if anim_type == "FadeIn":
                self.play_sound(SoundFX.reveal())
            elif anim_type == "FadeOut":
                self.play_sound(SoundFX.dismiss())
            elif anim_type == "FadeTransition":
                self.play_sound(SoundFX.whoosh())
            elif anim_type == "WipeTransition":
                self.play_sound(SoundFX.whoosh())
            elif anim_type == "IrisTransition":
                self.play_sound(SoundFX.whoosh())

    _last_tw_char_count = {}

    def _auto_typewriter_sound(self, anim, alpha, frame_idx):
        """Generate typing clicks for TypeWriter animation."""
        anim_id = id(anim)
        current_chars = getattr(anim.target, 'max_chars', 0) or 0

        prev = self._last_tw_char_count.get(anim_id, 0)
        if current_chars > prev:
            # New character appeared — add a typing click
            char = anim.target.text[current_chars - 1] if current_chars <= len(anim.target.text) else ' '
            if char == '\n':
                self.play_sound(SoundFX.typing_return())
            else:
                self.play_sound(SoundFX.typing_key())
        self._last_tw_char_count[anim_id] = current_chars

    # ── Internal rendering ──────────────────────────────────

    def _capture_frame(self):
        """Render all objects (with camera transform) and capture the frame."""
        dt = 1.0 / self.config.fps
        self._current_time += dt
        self.camera.update(dt)
        self.canvas.clear()

        sorted_objects = sorted(self._objects, key=lambda o: o.z_index)

        for obj in sorted_objects:
            if not obj.visible:
                continue

            if self.camera.x != 0 or self.camera.y != 0 or self.camera.zoom != 1.0 or \
               self.camera._shake_offset_x != 0 or self.camera._shake_offset_y != 0:
                orig_x, orig_y = obj.x, obj.y
                screen_x, screen_y = self.camera.world_to_screen(obj.x, obj.y)
                obj.x, obj.y = screen_x, screen_y
                obj.render(self.canvas)
                obj.x, obj.y = orig_x, orig_y
            else:
                obj.render(self.canvas)

        frame = self.canvas.get_frame(self.config.upscale)
        self._frames.append(frame)

    # ── Video output ────────────────────────────────────────

    def render(self, output_path: str = "output.mp4"):
        """Build the scene and encode to video with audio.

        Calls ``construct()`` to generate frames and sound events,
        then encodes video via ffmpeg, mixes in audio, and produces
        the final MP4.

        Args:
            output_path: Path for the output video file.
        """
        print(f"[PixelEngine] Building scene: {self.__class__.__name__}")
        print(
            f"  Canvas: {self.config.canvas_width}×{self.config.canvas_height} "
            f"→ {self.config.output_width}×{self.config.output_height} "
            f"({self.config.upscale}× upscale)"
        )
        print(f"  FPS: {self.config.fps}")
        print(f"  Auto-sound: {'on' if self.auto_sound else 'off'}")

        self._frames = []
        self._current_time = 0
        self._sound_timeline = SoundTimeline()
        Scene._last_tw_char_count = {}
        self.construct()

        total_seconds = len(self._frames) / self.config.fps
        sound_count = self._sound_timeline.event_count
        print(f"[PixelEngine] Captured {len(self._frames)} frames ({total_seconds:.1f}s)")
        print(f"  Sound events: {sound_count}")

        if not self._frames:
            print("[PixelEngine] Warning: No frames captured!")
            return

        renderer = Renderer(self.config)

        if sound_count > 0:
            # Render video to temp file, then mux with audio
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_video = os.path.join(tmpdir, "video_only.mp4")
                tmp_audio = os.path.join(tmpdir, "audio.wav")

                renderer.encode(self._frames, tmp_video)
                self._sound_timeline.save_wav(tmp_audio, total_seconds)
                mux_audio_video(tmp_video, tmp_audio, output_path)
                size = os.path.getsize(output_path) / 1024
                print(f"  Output: {output_path} ({size:.1f} KB) [video+audio]")
        else:
            renderer.encode(self._frames, output_path)

        print(f"[PixelEngine] ✓ Video saved to: {output_path}")
