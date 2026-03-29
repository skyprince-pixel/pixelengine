"""PixelEngine Scene — the core orchestrator for animations and sound."""
import os
import sys
import time
import tempfile
from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.canvas import Canvas
from pixelengine.camera import Camera
from pixelengine.renderer import Renderer
from pixelengine.sound import SoundFX, SoundTimeline, mux_audio_video
from pixelengine.lighting import LightingEngine
from pixelengine.camerafx import CameraFXPipeline, DepthOfField


class SilentExit(Exception):
    """Raised to silently exit rendering (e.g. for --test-frame)."""
    pass


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
        self._frame_count: int = 0
        self._renderer: Renderer = None

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

        # AI Debugging
        self.dry_run: bool = "--dry-run" in sys.argv
        self.test_frame_target: float = None
        for arg in sys.argv:
            if arg.startswith("--test-frame="):
                try:
                    self.test_frame_target = float(arg.split("=")[1])
                except ValueError:
                    pass

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

    def set_background(self, color: str) -> "Scene":
        """Set the canvas background colour.

        This is the recommended way to set a solid background — it covers
        the entire canvas automatically, so you never need to create a
        full-screen ``Rect``.

        Args:
            color: Hex colour string (e.g. ``"#1D2B53"``).

        Usage::

            self.set_background("#1D2B53")  # Dark navy
        """
        from pixelengine.color import parse_color
        self.canvas.background = parse_color(color)
        self.canvas._bg_array[:, :] = self.canvas.background
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
        """Add auto-sounds based on animation types using dynamic SFX."""
        for anim in animations:
            anim_type = type(anim).__name__

            if anim_type == "FadeIn":
                self.play_sound(SoundFX.dynamic("reveal"))
            elif anim_type == "FadeOut":
                self.play_sound(SoundFX.dynamic("dismiss"))
            elif anim_type in ("FadeTransition", "WipeTransition",
                               "IrisTransition", "SlideTransition"):
                self.play_sound(SoundFX.dynamic("transition"))
            elif anim_type == "GlitchTransition":
                self.play_sound(SoundFX.dynamic("impact", intensity=0.6))
            elif anim_type == "ShatterTransition":
                self.play_sound(SoundFX.dynamic("impact", intensity=0.8))

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

        # Progress bar (updated every frame during construct)
        if hasattr(self, '_render_start_time'):
            frame_count = self._frame_count + 1
            elapsed = time.time() - self._render_start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            # We don't know total frames ahead of time, so show a spinner + stats
            spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[frame_count % 10]
            sys.stdout.write(
                f"\r  {spinner} Rendering: {frame_count} frames "
                f"({self._current_time:.1f}s) | {fps:.1f} fps  "
            )
            sys.stdout.flush()

        # Run physics simulation if world exists
        if hasattr(self, 'physics') and self.physics is not None:
            self.physics.step(dt)

        # Run updaters on all objects
        for obj in list(self._objects):
            # Propagate scene FPS to objects that need it
            if hasattr(obj, '_fps'):
                obj._fps = self.config.fps
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

        # AI Debugging: Dry-Run Layout Logging
        if getattr(self, 'dry_run', False):
            prev_sec = int(self._current_time - dt)
            curr_sec = int(self._current_time)
            if curr_sec > prev_sec:
                print(f"\n[PixelEngine Dry-Run] t={curr_sec}s")
                for obj in self._objects:
                    if obj.visible:
                        w = getattr(obj, 'width', 0)
                        h = getattr(obj, 'height', 0)
                        size_str = f", size {w}x{h}" if (w or h) else ""
                        print(f"  - {obj.__class__.__name__} at ({int(obj.x)}, {int(obj.y)}){size_str}, z_index: {obj.z_index}")
            self._frame_count += 1
            return

        sorted_objects = sorted(self._objects, key=lambda o: o.z_index)

        for obj in sorted_objects:
            if not obj.visible:
                continue

            if self.camera.x != 0 or self.camera.y != 0 or self.camera.zoom != 1.0 or \
               self.camera._shake_offset_x != 0 or self.camera._shake_offset_y != 0:
                orig_x, orig_y = obj.x, obj.y
                screen_x, screen_y = self.camera.world_to_screen(obj.x, obj.y)
                obj.x, obj.y = screen_x, screen_y

                # Camera offset delta for multi-coordinate objects
                dx = screen_x - orig_x
                dy = screen_y - orig_y

                # Line: transform x1,y1,x2,y2
                orig_line = None
                if hasattr(obj, 'x1') and hasattr(obj, 'x2'):
                    orig_line = (obj.x1, obj.y1, obj.x2, obj.y2)
                    obj.x1 = int(obj.x1 + dx)
                    obj.y1 = int(obj.y1 + dy)
                    obj.x2 = int(obj.x2 + dx)
                    obj.y2 = int(obj.y2 + dy)

                # Triangle/Polygon: transform points
                orig_points = None
                if hasattr(obj, 'points') and isinstance(getattr(obj, 'points', None), list):
                    orig_points = list(obj.points)
                    obj.points = [(int(px + dx), int(py + dy)) for px, py in obj.points]

                try:
                    self._render_object(obj)
                finally:
                    obj.x, obj.y = orig_x, orig_y
                    if orig_line is not None:
                        obj.x1, obj.y1, obj.x2, obj.y2 = orig_line
                    if orig_points is not None:
                        obj.points = orig_points
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

        if hasattr(self, '_renderer') and self._renderer:
            self._renderer.add_frame(frame)
        self._frame_count += 1

        # AI Debugging: Test Frame Extraction
        if getattr(self, 'test_frame_target', None) is not None:
            if self._current_time >= self.test_frame_target:
                frame.save("test_frame.png")
                print(f"\n[PixelEngine] Test frame saved to root: test_frame.png (t={self._current_time:.2f}s)")
                raise SilentExit()

    def _render_object(self, obj):
        """Render a single object, applying per-object quality if needed."""
        quality = getattr(obj, 'render_quality', 1.0)
        if abs(quality - 1.0) < 0.01:
            obj.render(self.canvas)
        else:
            # Render to a temporary sub-canvas at adjusted resolution
            w = getattr(obj, 'width', 16) or 16
            h = getattr(obj, 'height', 16) or 16
            # Ensure reasonable size
            w = max(4, min(self.canvas.width, int(w * 1.5)))
            h = max(4, min(self.canvas.height, int(h * 1.5)))
            temp_canvas = Canvas(w, h, "#00000000")
            orig_x, orig_y = obj.x, obj.y
            obj.x = w // 4  # Offset inside temp canvas
            obj.y = h // 4
            obj.render(temp_canvas)
            obj.x, obj.y = orig_x, orig_y
            # Blit with quality scaling using Pillow image from temp canvas
            self.canvas.blit_quality(
                temp_canvas._pil_image,
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
        import shutil

        print(f"[PixelEngine] Building scene: {self.__class__.__name__}")
        print(
            f"  Canvas: {self.config.canvas_width}×{self.config.canvas_height} "
            f"→ {self.config.output_width}×{self.config.output_height} "
            f"({self.config.upscale}× upscale)"
        )
        print(f"  FPS: {self.config.fps}")
        print(f"  Auto-sound: {'on' if self.auto_sound else 'off'}")

        self._frame_count = 0
        self._current_time = 0
        self._sound_timeline = SoundTimeline()
        self._last_tw_char_count = {}
        self._render_start_time = time.time()

        # Determine paths
        if output_path is None:
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

            if os.path.exists(script_path):
                shutil.copy2(script_path, os.path.join(script_dir, os.path.basename(script_path)))
        else:
            audio_path = None

        self._renderer = Renderer(self.config)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_video = os.path.join(tmpdir, "video_only.mp4")
            self._renderer.open(tmp_video, self.config.output_width, self.config.output_height)
            
            # RUN CONSTRUCT AND STREAM FRAMES
            try:
                self.construct()
            except SilentExit:
                pass
            
            # Close renderer after all frames
            self._renderer.close()

            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

            total_seconds = self._frame_count / self.config.fps
            sound_count = self._sound_timeline.event_count
            print(f"[PixelEngine] Captured {self._frame_count} frames ({total_seconds:.1f}s)")
            print(f"  Sound events: {sound_count}")

            if self._frame_count == 0:
                print("[PixelEngine] Warning: No frames captured!")
                return

            if sound_count > 0:
                if audio_path is None:
                    tmp_audio = os.path.join(tmpdir, "audio.wav")
                    self._sound_timeline.save_wav(tmp_audio, total_seconds)
                    mux_audio_video(tmp_video, tmp_audio, output_path)
                else:
                    self._sound_timeline.save_wav(audio_path, total_seconds)
                    mux_audio_video(tmp_video, audio_path, output_path)
                
                size = os.path.getsize(output_path) / 1024
                print(f"  Output: {output_path} ({size:.1f} KB) [video+audio]")
                if audio_path:
                    print(f"  Audio:  {audio_path}")
            else:
                shutil.move(tmp_video, output_path)
                size = os.path.getsize(output_path) / 1024
                print(f"  Output: {output_path} ({size:.1f} KB) [video]")

        print(f"[PixelEngine] ✓ Video saved to: {output_path}")
