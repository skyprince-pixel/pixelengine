"""PixelEngine Scene — the core orchestrator for animations."""
from pixelengine.config import PixelConfig, DEFAULT_CONFIG
from pixelengine.canvas import Canvas
from pixelengine.camera import Camera
from pixelengine.renderer import Renderer


class Scene:
    """Base scene class. Subclass and override ``construct()`` to build animations.

    Usage::

        class MyScene(Scene):
            def construct(self):
                rect = Rect(20, 10, color="#FF004D")
                self.add(rect)
                self.wait(2.0)

        MyScene().render("output.mp4")
    """

    def __init__(self, config: PixelConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.canvas = Canvas(
            self.config.canvas_width,
            self.config.canvas_height,
            self.config.background_color,
        )
        self.camera = Camera(self.config.canvas_width, self.config.canvas_height)
        self._objects: list = []      # PObjects currently in the scene
        self._frames: list = []       # Captured PIL Image frames

    # ── User overrides ──────────────────────────────────────

    def construct(self):
        """Override this method to define your scene.

        Use ``self.add()``, ``self.play()``, and ``self.wait()``
        to compose your animation.
        """
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

    # ── Timing ──────────────────────────────────────────────

    def wait(self, seconds: float = 1.0):
        """Hold the current frame for the given duration.

        Args:
            seconds: Duration to hold (converted to frames at config.fps).
        """
        num_frames = max(1, int(seconds * self.config.fps))
        for _ in range(num_frames):
            self._capture_frame()

    def play(self, *animations, duration: float = 1.0):
        """Play one or more animations over the given duration.

        Each animation's ``interpolate(alpha)`` is called with alpha
        going from 0.0 to 1.0 over the duration.

        Args:
            *animations: Animation objects to play.
            duration: How long the animation runs (seconds).
        """
        num_frames = max(1, int(duration * self.config.fps))
        for frame_idx in range(num_frames):
            alpha = frame_idx / max(1, num_frames - 1)
            for anim in animations:
                if hasattr(anim, "interpolate"):
                    anim.interpolate(alpha)
            self._capture_frame()

    # ── Internal rendering ──────────────────────────────────

    def _capture_frame(self):
        """Render all objects (with camera transform) and capture the frame."""
        dt = 1.0 / self.config.fps
        self.camera.update(dt)
        self.canvas.clear()

        # Z-sort: lower z_index drawn first (behind)
        sorted_objects = sorted(self._objects, key=lambda o: o.z_index)

        for obj in sorted_objects:
            if not obj.visible:
                continue

            # Apply camera transform: shift object's render position
            if self.camera.x != 0 or self.camera.y != 0 or self.camera.zoom != 1.0 or \
               self.camera._shake_offset_x != 0 or self.camera._shake_offset_y != 0:
                # Save original position
                orig_x, orig_y = obj.x, obj.y
                # Convert world pos to screen pos
                screen_x, screen_y = self.camera.world_to_screen(obj.x, obj.y)
                obj.x, obj.y = screen_x, screen_y
                obj.render(self.canvas)
                # Restore original position
                obj.x, obj.y = orig_x, orig_y
            else:
                obj.render(self.canvas)

        frame = self.canvas.get_frame(self.config.upscale)
        self._frames.append(frame)

    # ── Video output ────────────────────────────────────────

    def render(self, output_path: str = "output.mp4"):
        """Build the scene and encode to video.

        Calls ``construct()`` to generate frames, then encodes
        all frames to MP4 via ffmpeg.

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

        self._frames = []
        self.construct()

        total_seconds = len(self._frames) / self.config.fps
        print(f"[PixelEngine] Captured {len(self._frames)} frames ({total_seconds:.1f}s)")

        if not self._frames:
            print("[PixelEngine] Warning: No frames captured!")
            return

        renderer = Renderer(self.config)
        renderer.encode(self._frames, output_path)
        print(f"[PixelEngine] ✓ Video saved to: {output_path}")
