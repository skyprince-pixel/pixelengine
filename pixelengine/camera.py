"""PixelEngine camera — viewport control with pan, zoom, follow, and shake."""
import math
import random
from pixelengine.pobject import PObject


class Camera:
    """Virtual camera that controls the viewport into the scene world.

    The camera defines which portion of the world is visible on the canvas.
    Objects are rendered relative to the camera position.

    Usage in Scene::

        self.camera.pan_to(100, 50)
        self.camera.zoom = 2.0
        self.camera.follow(player_sprite)
        self.camera.shake(intensity=3, duration=0.5)
    """

    def __init__(self, canvas_width: int, canvas_height: int):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Camera position (top-left of viewport in world coords)
        self.x: float = 0
        self.y: float = 0

        # Zoom level (1.0 = normal, 2.0 = 2× zoomed in)
        self.zoom: float = 1.0

        # Follow target
        self._follow_target: PObject = None
        self._follow_smooth: float = 0.1  # 0=instant, 1=no movement

        # Shake state
        self._shake_intensity: float = 0
        self._shake_duration: float = 0
        self._shake_timer: float = 0
        self._shake_offset_x: float = 0
        self._shake_offset_y: float = 0

    # ── Position ────────────────────────────────────────────

    def pan_to(self, x: float, y: float):
        """Set camera position (top-left corner in world coords)."""
        self.x = x
        self.y = y

    def center_on(self, x: float, y: float):
        """Center the camera on world coordinates."""
        self.x = x - self.canvas_width / (2 * self.zoom)
        self.y = y - self.canvas_height / (2 * self.zoom)

    # ── Follow ──────────────────────────────────────────────

    def follow(self, target: PObject, smooth: float = 0.1):
        """Make the camera follow a PObject.

        Args:
            target: The PObject to follow.
            smooth: Smoothing factor (0=instant snap, higher=smoother).
        """
        self._follow_target = target
        self._follow_smooth = max(0.01, min(1.0, smooth))

    def unfollow(self):
        """Stop following any target."""
        self._follow_target = None

    # ── Shake ───────────────────────────────────────────────

    def shake(self, intensity: float = 3.0, duration: float = 0.5):
        """Start a screen shake effect.

        Args:
            intensity: Maximum pixel offset per frame.
            duration: How long the shake lasts (seconds).
        """
        self._shake_intensity = intensity
        self._shake_duration = duration
        self._shake_timer = 0

    # ── Update (called each frame) ──────────────────────────

    def update(self, dt: float):
        """Update camera state. Called once per frame.

        Args:
            dt: Time delta (1/fps).
        """
        # Follow target
        if self._follow_target is not None:
            target_x = self._follow_target.center_x - self.canvas_width / (2 * self.zoom)
            target_y = self._follow_target.center_y - self.canvas_height / (2 * self.zoom)
            self.x += (target_x - self.x) * self._follow_smooth
            self.y += (target_y - self.y) * self._follow_smooth

        # Shake
        if self._shake_timer < self._shake_duration:
            self._shake_timer += dt
            # Decay intensity over time
            progress = self._shake_timer / self._shake_duration
            decay = 1.0 - progress
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
