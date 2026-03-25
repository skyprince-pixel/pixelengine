"""PixelEngine camera — viewport control with pan, zoom, follow, and shake."""
import math
import random
from pixelengine.pobject import PObject


class Camera:
    """Virtual camera that controls the viewport into the scene world.

    Features:
      - Pan to absolute position or center on coordinates
      - Smooth follow with deadzone
      - Zoom in/out
      - Screen shake with intensity decay
      - World bounds clamping

    Usage in Scene::

        self.camera.pan_to(100, 50)
        self.camera.zoom = 2.0
        self.camera.follow(player, smooth=0.15, deadzone=(20, 15))
        self.camera.shake(intensity=3, duration=0.5)
        self.camera.set_bounds(0, 0, 512, 288)
    """

    def __init__(self, canvas_width: int, canvas_height: int):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Camera position (top-left of viewport in world coords)
        self.x: float = 0
        self.y: float = 0

        # Zoom level (1.0 = normal, 2.0 = 2× zoomed in)
        self.zoom: float = 1.0

        # Follow
        self._follow_target: PObject = None
        self._follow_smooth: float = 0.1
        self._follow_deadzone_x: float = 0
        self._follow_deadzone_y: float = 0

        # World bounds (None = no clamping)
        self._bounds: tuple = None  # (min_x, min_y, max_x, max_y)

        # Shake state
        self._shake_intensity: float = 0
        self._shake_duration: float = 0
        self._shake_timer: float = 0
        self._shake_offset_x: float = 0
        self._shake_offset_y: float = 0
        self._shake_frequency: float = 30.0  # Higher = faster vibrations

    # ── Position ────────────────────────────────────────────

    def pan_to(self, x: float, y: float):
        """Set camera position (top-left corner in world coords)."""
        self.x = x
        self.y = y
        self._clamp_bounds()

    def center_on(self, x: float, y: float):
        """Center the camera on world coordinates."""
        self.x = x - self.canvas_width / (2 * self.zoom)
        self.y = y - self.canvas_height / (2 * self.zoom)
        self._clamp_bounds()

    def reset(self):
        """Reset camera to origin with default zoom."""
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self._shake_offset_x = 0
        self._shake_offset_y = 0

    # ── Bounds ──────────────────────────────────────────────

    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float):
        """Set world bounds — camera won't pan beyond these limits.

        Args:
            min_x, min_y: Top-left corner of the world.
            max_x, max_y: Bottom-right corner of the world.
        """
        self._bounds = (min_x, min_y, max_x, max_y)
        self._clamp_bounds()

    def clear_bounds(self):
        """Remove world bounds."""
        self._bounds = None

    def _clamp_bounds(self):
        """Clamp camera position to world bounds."""
        if self._bounds is None:
            return
        min_x, min_y, max_x, max_y = self._bounds
        view_w = self.canvas_width / self.zoom
        view_h = self.canvas_height / self.zoom
        self.x = max(min_x, min(self.x, max_x - view_w))
        self.y = max(min_y, min(self.y, max_y - view_h))

    # ── Follow ──────────────────────────────────────────────

    def follow(self, target: PObject, smooth: float = 0.1,
               deadzone: tuple = None):
        """Make the camera follow a PObject.

        Args:
            target: The PObject to follow.
            smooth: Smoothing factor (0.01=snappy, 1.0=very laggy).
            deadzone: Optional (width, height) — camera doesn't move if
                      target is within this rectangle around screen center.
        """
        self._follow_target = target
        self._follow_smooth = max(0.01, min(1.0, smooth))
        if deadzone:
            self._follow_deadzone_x = deadzone[0]
            self._follow_deadzone_y = deadzone[1]
        else:
            self._follow_deadzone_x = 0
            self._follow_deadzone_y = 0

    def unfollow(self):
        """Stop following any target."""
        self._follow_target = None

    # ── Shake ───────────────────────────────────────────────

    def shake(self, intensity: float = 3.0, duration: float = 0.5,
              frequency: float = 30.0):
        """Start a screen shake effect.

        Args:
            intensity: Maximum pixel offset per frame.
            duration: How long the shake lasts (seconds).
            frequency: Vibration speed (higher = faster shake).
        """
        self._shake_intensity = intensity
        self._shake_duration = duration
        self._shake_timer = 0
        self._shake_frequency = frequency

    @property
    def is_shaking(self) -> bool:
        """Whether the camera is currently shaking."""
        return self._shake_timer < self._shake_duration and self._shake_intensity > 0

    # ── Update (called each frame) ──────────────────────────

    def update(self, dt: float):
        """Update camera state. Called once per frame.

        Args:
            dt: Time delta (1/fps).
        """
        # Follow target with deadzone
        if self._follow_target is not None:
            target_x = self._follow_target.center_x - self.canvas_width / (2 * self.zoom)
            target_y = self._follow_target.center_y - self.canvas_height / (2 * self.zoom)

            dx = target_x - self.x
            dy = target_y - self.y

            # Deadzone: only move if target is outside deadzone
            if abs(dx) > self._follow_deadzone_x:
                move_x = dx - (self._follow_deadzone_x if dx > 0 else -self._follow_deadzone_x)
                self.x += move_x * self._follow_smooth
            if abs(dy) > self._follow_deadzone_y:
                move_y = dy - (self._follow_deadzone_y if dy > 0 else -self._follow_deadzone_y)
                self.y += move_y * self._follow_smooth

            self._clamp_bounds()

        # Shake with sinusoidal decay
        if self._shake_timer < self._shake_duration:
            self._shake_timer += dt
            progress = self._shake_timer / self._shake_duration
            decay = 1.0 - progress  # Linear decay
            # Use random for organic feel, scaled by decay
            self._shake_offset_x = random.uniform(
                -self._shake_intensity, self._shake_intensity
            ) * decay
            self._shake_offset_y = random.uniform(
                -self._shake_intensity, self._shake_intensity
            ) * decay
        else:
            self._shake_offset_x = 0
            self._shake_offset_y = 0

    # ── Transform ───────────────────────────────────────────

    def world_to_screen(self, world_x: float, world_y: float) -> tuple:
        """Convert world coordinates to screen (canvas) coordinates."""
        screen_x = (world_x - self.x) * self.zoom + self._shake_offset_x
        screen_y = (world_y - self.y) * self.zoom + self._shake_offset_y
        return (int(screen_x), int(screen_y))

    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple:
        """Convert screen (canvas) coordinates to world coordinates."""
        world_x = (screen_x - self._shake_offset_x) / self.zoom + self.x
        world_y = (screen_y - self._shake_offset_y) / self.zoom + self.y
        return (world_x, world_y)

    @property
    def viewport(self) -> tuple:
        """Return the visible world rectangle (x, y, width, height)."""
        w = self.canvas_width / self.zoom
        h = self.canvas_height / self.zoom
        return (self.x, self.y, w, h)

    @property
    def offset_x(self) -> float:
        """Total X offset (position + shake)."""
        return self.x - self._shake_offset_x

    @property
    def offset_y(self) -> float:
        """Total Y offset (position + shake)."""
        return self.y - self._shake_offset_y


# ═══════════════════════════════════════════════════════════
#  Camera Animations
# ═══════════════════════════════════════════════════════════

class CameraPan:
    """Animate camera panning to a position."""

    def __init__(self, camera: Camera, x: float, y: float, easing=None):
        self.camera = camera
        self.target_x = x
        self.target_y = y
        self.start_x = None
        self.start_y = None
        self.easing = easing or (lambda t: t)
        self._started = False

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        if not self._started:
            self.start_x = self.camera.x
            self.start_y = self.camera.y
            self._started = True
        t = self.easing(alpha)
        self.camera.x = self.start_x + (self.target_x - self.start_x) * t
        self.camera.y = self.start_y + (self.target_y - self.start_y) * t


class CameraZoom:
    """Animate camera zoom level."""

    def __init__(self, camera: Camera, zoom: float, easing=None):
        self.camera = camera
        self.target_zoom = zoom
        self.start_zoom = None
        self.easing = easing or (lambda t: t)
        self._started = False

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        if not self._started:
            self.start_zoom = self.camera.zoom
            self._started = True
        t = self.easing(alpha)
        self.camera.zoom = self.start_zoom + (self.target_zoom - self.start_zoom) * t


class CameraCenterOn:
    """Animate camera centering on world coordinates."""

    def __init__(self, camera: Camera, x: float, y: float, easing=None):
        self.camera = camera
        self.world_x = x
        self.world_y = y
        self.start_x = None
        self.start_y = None
        self.easing = easing or (lambda t: t)
        self._started = False

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        if not self._started:
            self.start_x = self.camera.x
            self.start_y = self.camera.y
            self._started = True
        target_x = self.world_x - self.camera.canvas_width / (2 * self.camera.zoom)
        target_y = self.world_y - self.camera.canvas_height / (2 * self.camera.zoom)
        t = self.easing(alpha)
        self.camera.x = self.start_x + (target_x - self.start_x) * t
        self.camera.y = self.start_y + (target_y - self.start_y) * t
