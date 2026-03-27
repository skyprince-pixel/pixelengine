"""PixelEngine 3D camera — perspective and isometric camera systems.

Provides Camera3D for perspective viewing and IsoCamera for
axonometric projections. Includes orbit and zoom animations.
"""
import math
from pixelengine.math3d import Vec3


class Camera3D:
    """Perspective camera for 3D scenes.

    Controls the viewpoint for all Object3D projections.
    Objects use the camera's position to calculate their projection.

    Usage::

        cam = Camera3D(fov=60, distance=5)
        cam.elevation = 30  # Look down 30°
        cam.azimuth = 45    # Rotate 45° around
    """

    def __init__(self, fov: float = 60, distance: float = 5,
                 elevation: float = 20, azimuth: float = 30):
        self.fov = fov
        self.distance = distance
        self.elevation = elevation    # Degrees above horizon
        self.azimuth = azimuth        # Degrees rotation around Y
        self.target = Vec3(0, 0, 0)   # Look-at point
        self.near = 0.1
        self.far = 100

    def get_view_position(self) -> Vec3:
        """Calculate camera world position from orbit parameters."""
        elev_rad = math.radians(self.elevation)
        azim_rad = math.radians(self.azimuth)
        x = self.distance * math.cos(elev_rad) * math.sin(azim_rad) + self.target.x
        y = self.distance * math.sin(elev_rad) + self.target.y
        z = self.distance * math.cos(elev_rad) * math.cos(azim_rad) + self.target.z
        return Vec3(x, y, z)


class IsoCamera:
    """Isometric/axonometric camera.

    Sets up isometric projection parameters for 3D objects.

    Usage::

        cam = IsoCamera(scale=10, rotation=45)
    """

    def __init__(self, scale: float = 10, rotation: float = 45):
        self.iso_scale = scale
        self.rotation = rotation  # Rotation around Y axis
        self.elevation = 35.264   # Standard isometric angle


# ═══════════════════════════════════════════════════════════
#  Camera Animations
# ═══════════════════════════════════════════════════════════

class Orbit3D:
    """Animate camera orbiting around a target point.

    Usage::

        scene.play(Orbit3D(camera3d, degrees=360), duration=4.0)
    """

    def __init__(self, camera, degrees: float = 360, easing=None):
        from pixelengine.animation import linear
        self.camera = camera
        self.degrees = degrees
        self.easing = easing or linear
        self._started = False
        self.start_azimuth = 0

    def interpolate(self, raw_alpha: float):
        from pixelengine.animation import get_easing
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self._started = True
            self.start_azimuth = self.camera.azimuth
            self.easing_fn = get_easing(self.easing)
        eased = self.easing_fn(alpha)
        self.camera.azimuth = self.start_azimuth + self.degrees * eased


class Zoom3D:
    """Animate camera zoom by changing distance.

    Usage::

        scene.play(Zoom3D(camera3d, target_distance=3), duration=1.5)
    """

    def __init__(self, camera, target_distance: float = 3, easing=None):
        from pixelengine.animation import ease_in_out
        self.camera = camera
        self.target_dist = target_distance
        self.easing = easing or ease_in_out
        self._started = False
        self.start_dist = 0

    def interpolate(self, raw_alpha: float):
        from pixelengine.animation import get_easing
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self._started = True
            self.start_dist = self.camera.distance
            self.easing_fn = get_easing(self.easing)
        eased = self.easing_fn(alpha)
        self.camera.distance = self.start_dist + (self.target_dist - self.start_dist) * eased
