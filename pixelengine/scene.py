"""PixelEngine Scene — the core orchestrator for animations and sound."""
import os
import tempfile
from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.canvas import Canvas
from pixelengine.camera import Camera
from pixelengine.renderer import Renderer
from pixelengine.sound import SoundFX, SoundTimeline, mux_audio_video
from pixelengine.lighting import LightingEngine
from pixelengine.camerafx import CameraFXPipeline, DepthOfField


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

        # TypeWriter auto-sound state (per-instance, not class-level)
        self._last_tw_char_count: dict = {}

        # Lighting system
        self._lights: list = []
        self._lighting_engine = LightingEngine()

        # Camera post-processing FX pipeline
        self._camera_fx = CameraFXPipeline()

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

    # ── Lighting ────────────────────────────────────────────

    def add_light(self, *lights) -> "Scene":
        """Add one or more lights to the scene.

        Supports AmbientLight, PointLight, DirectionalLight.

        Usage::

            scene.add_light(AmbientLight(intensity=0.2))
            scene.add_light(PointLight(x=128, y=72, radius=60))
        """
        for light in lights:
            if light not in self._lights:
                self._lights.append(light)
                # PointLights are also PObjects — add to scene for animation
                from pixelengine.lighting import PointLight
                if isinstance(light, PointLight):
                    self.add(light)
        return self

    def remove_light(self, *lights) -> "Scene":
        """Remove lights from the scene."""
        for light in lights:
            if light in self._lights:
                self._lights.remove(light)
                from pixelengine.lighting import PointLight
                if isinstance(light, PointLight):
                    self.remove(light)
        return self

    # ── Camera FX ───────────────────────────────────────────

    def add_camera_fx(self, *effects) -> "Scene":
        """Add post-processing effects to the camera FX pipeline.

        Usage::

            scene.add_camera_fx(Vignette(intensity=0.5))
            scene.add_camera_fx(ChromaticAberration(offset=2))
        """
        for fx in effects:
            self._camera_fx.add(fx)
        return self

    def remove_camera_fx(self, *effects) -> "Scene":
        """Remove effects from the camera FX pipeline."""
        for fx in effects:
            self._camera_fx.remove(fx)
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

    def play_voiceover(self, text: str, voice: str = None, speed: float = 1.0, engine: str = "kokoro"):
        """Generate and play an AI voiceover, holding the frame for the duration.

        Supports paralinguistic tags: [laugh], [chuckle], [cough].

        Args:
            text: Text for the voiceover to speak.
            voice: Optional path to a ~10s reference .wav for voice cloning
                   (chatterbox), or voice name like "af_bella" (kokoro).
            speed: Speed multiplier (default 1.0).
            engine: "kokoro" or "chatterbox".
        """
        from pixelengine.voiceover import VoiceOver
        sfx, duration = VoiceOver.generate(text, voice=voice, speed=speed, engine=engine)
        self.play_sound(sfx)
        print(f"[PixelEngine] VoiceOver: '{text[:30]}...' ({duration:.2f}s)")
        self.wait(duration)

    def preload_voiceovers(self, texts: list, voice: str = None,
                           speed: float = 1.0, engine: str = "kokoro"):
        """Pre-generate all voiceovers to populate cache before construct().

        This front-loads TTS work so play_voiceover() calls during
        construct() load from cache instantly.

        Args:
            texts: List of voiceover text strings to pre-generate.
            voice: Optional voice reference for all lines.
            speed: Speed multiplier for all lines.
            engine: "kokoro" or "chatterbox".
        """
        from pixelengine.voiceover import VoiceOver
        VoiceOver.preload(texts, voice=voice, speed=speed, engine=engine)

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

    # _last_tw_char_count is now initialized per-instance in __init__

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

        # Run physics simulation if world exists
        if hasattr(self, 'physics') and self.physics is not None:
            self.physics.step(dt)

        # Run updaters on all objects
        for obj in list(self._objects):
            if hasattr(obj, '_updaters') and obj._updaters:
                for updater in list(obj._updaters):
                    try:
                        updater(obj, dt)
                    except Exception as e:
                        import warnings
                        warnings.warn(
                            f"[PixelEngine] Updater error on {obj.__class__.__name__}: {e}",
                            RuntimeWarning,
                            stacklevel=2,
                        )

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
                self._render_object(obj)
                obj.x, obj.y = orig_x, orig_y
            else:
                self._render_object(obj)

        # ── Lighting pass ──
        if self._lights:
            self._lighting_engine.apply(self.canvas, self._lights, sorted_objects)

        # ── Camera FX pipeline (depth-of-field auto-sync with camera) ──
        if self.camera.has_focus:
            # Auto-create or update DepthOfField from camera focus
            self._sync_camera_focus()

        frame = self.canvas.get_frame(self.config.upscale)

        # Apply camera FX to the upscaled frame
        if self._camera_fx.count > 0:
            frame = self._camera_fx.apply(frame)

        self._frames.append(frame)

    def _render_object(self, obj):
        """Render a single object, applying per-object quality if needed."""
        quality = getattr(obj, 'render_quality', 1.0)
        if abs(quality - 1.0) < 0.01:
            obj.render(self.canvas)
        else:
            # Render to a temporary sub-canvas at adjusted resolution
            from PIL import Image
            w = getattr(obj, 'width', 16) or 16
            h = getattr(obj, 'height', 16) or 16
            # Ensure reasonable size
            w = max(4, min(self.canvas.width, int(w * 1.5)))
            h = max(4, min(self.canvas.height, int(h * 1.5)))
            temp_canvas = Canvas(w, h, "#00000000")
            temp_canvas._image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            orig_x, orig_y = obj.x, obj.y
            obj.x = w // 4  # Offset inside temp canvas
            obj.y = h // 4
            obj.render(temp_canvas)
            obj.x, obj.y = orig_x, orig_y
            # Blit with quality scaling
            self.canvas.blit_quality(
                temp_canvas._image,
                int(orig_x), int(orig_y),
                quality,
            )

    def _sync_camera_focus(self):
        """Sync camera focus point with DepthOfField effect."""
        # Find existing DoF or add one
        dof = None
        for fx in self._camera_fx._effects:
            if isinstance(fx, DepthOfField):
                dof = fx
                break
        if dof is None:
            dof = DepthOfField(enabled=True)
            self._camera_fx.add(dof)

        # Convert world focus to screen coords
        sx, sy = self.camera.world_to_screen(self.camera.focus_x, self.camera.focus_y)
        # Scale to upscaled frame coords
        dof.focus_x = int(sx * self.config.upscale)
        dof.focus_y = int(sy * self.config.upscale)
        dof.focus_radius = int(self.camera.focus_radius * self.config.upscale)

    # ── Video output ────────────────────────────────────────

    def render(self, output_path: str = None):
        """Build the scene and encode to video with audio.

        If `output_path` is None, automatically organizes generated files into:
          outputs/<script_name>/<resolution_fps>/<SceneName>.mp4
          outputs/<script_name>/audio/<SceneName>.wav
          outputs/<script_name>/scripts/<script_name>.py (backup of the source)

        Args:
            output_path: Optional exact path for the output video file. If provided,
                         bypasses the auto-organization system.
        """
        import sys
        import os
        import shutil

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
        self._last_tw_char_count = {}
        self.construct()

        total_seconds = len(self._frames) / self.config.fps
        sound_count = self._sound_timeline.event_count
        print(f"[PixelEngine] Captured {len(self._frames)} frames ({total_seconds:.1f}s)")
        print(f"  Sound events: {sound_count}")

        if not self._frames:
            print("[PixelEngine] Warning: No frames captured!")
            return

        renderer = Renderer(self.config)

        # ── Organize output files ──
        if output_path is None:
            import inspect
            # Find the script that defined this scene subclass
            module = sys.modules.get(self.__class__.__module__)
            script_path = getattr(module, '__file__', sys.argv[0])
            script_name = os.path.splitext(os.path.basename(script_path))[0]
            if not script_name or script_name == "__main__":
                script_name = "project"

            scene_name = self.__class__.__name__
            res_fps = f"{self.config.output_width}x{self.config.output_height}_{self.config.fps}fps"

            base_dir = os.path.join("outputs", script_name)
            video_dir = os.path.join(base_dir, res_fps)
            audio_dir = os.path.join(base_dir, "audio")
            script_dir = os.path.join(base_dir, "scripts")

            os.makedirs(video_dir, exist_ok=True)
            os.makedirs(audio_dir, exist_ok=True)
            os.makedirs(script_dir, exist_ok=True)

            output_path = os.path.join(video_dir, f"{scene_name}.mp4")
            audio_path = os.path.join(audio_dir, f"{scene_name}.wav")

            # Backup the script
            if os.path.exists(script_path):
                shutil.copy2(script_path, os.path.join(script_dir, os.path.basename(script_path)))
        else:
            # If an explicit path is given, we just use a temp dir for audio later
            audio_path = None

        if sound_count > 0:
            if audio_path is None:
                # Use temp directory for manual output_path
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_video = os.path.join(tmpdir, "video_only.mp4")
                    tmp_audio = os.path.join(tmpdir, "audio.wav")
                    renderer.encode(self._frames, tmp_video)
                    self._sound_timeline.save_wav(tmp_audio, total_seconds)
                    mux_audio_video(tmp_video, tmp_audio, output_path)
            else:
                # Use the organized directories
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_video = os.path.join(tmpdir, "video_only.mp4")
                    renderer.encode(self._frames, tmp_video)
                    self._sound_timeline.save_wav(audio_path, total_seconds)
                    mux_audio_video(tmp_video, audio_path, output_path)
            
            size = os.path.getsize(output_path) / 1024
            print(f"  Output: {output_path} ({size:.1f} KB) [video+audio]")
            if audio_path:
                print(f"  Audio:  {audio_path}")
        else:
            renderer.encode(self._frames, output_path)
            size = os.path.getsize(output_path) / 1024
            print(f"  Output: {output_path} ({size:.1f} KB) [video]")

        print(f"[PixelEngine] ✓ Video saved to: {output_path}")
