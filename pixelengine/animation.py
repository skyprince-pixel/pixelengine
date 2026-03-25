"""PixelEngine animation system — easing functions and built-in animations."""
import math
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  Easing Functions
# ═══════════════════════════════════════════════════════════

def linear(t: float) -> float:
    """No easing — constant speed."""
    return t


def ease_in(t: float) -> float:
    """Accelerate from zero velocity."""
    return t * t


def ease_out(t: float) -> float:
    """Decelerate to zero velocity."""
    return 1 - (1 - t) * (1 - t)


def ease_in_out(t: float) -> float:
    """Accelerate then decelerate."""
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - (-2 * t + 2) ** 2 / 2


def bounce(t: float) -> float:
    """Bounce at the end."""
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def elastic(t: float) -> float:
    """Elastic spring effect."""
    if t == 0 or t == 1:
        return t
    return -(2 ** (10 * (t - 1))) * math.sin((t - 1.1) * 5 * math.pi)


def ease_in_cubic(t: float) -> float:
    """Cubic ease in."""
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """Cubic ease out."""
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease in-out."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - (-2 * t + 2) ** 3 / 2


# Map of easing names to functions
EASINGS = {
    "linear": linear,
    "ease_in": ease_in,
    "ease_out": ease_out,
    "ease_in_out": ease_in_out,
    "bounce": bounce,
    "elastic": elastic,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
}


def get_easing(name_or_func):
    """Get an easing function by name or pass through if already a callable."""
    if callable(name_or_func):
        return name_or_func
    if isinstance(name_or_func, str) and name_or_func in EASINGS:
        return EASINGS[name_or_func]
    raise ValueError(f"Unknown easing: {name_or_func!r}. Available: {list(EASINGS.keys())}")


# ═══════════════════════════════════════════════════════════
#  Animation Base Class
# ═══════════════════════════════════════════════════════════

class Animation:
    """Base class for all animations.

    Subclasses override ``update(alpha)`` to modify the target PObject.
    The ``alpha`` parameter goes from 0.0 to 1.0 over the animation's duration.
    """

    def __init__(self, target: PObject, easing=linear):
        self.target = target
        self.easing = get_easing(easing)
        self._started = False

    def interpolate(self, raw_alpha: float):
        """Called each frame with raw alpha (0→1). Applies easing."""
        alpha = max(0.0, min(1.0, raw_alpha))
        eased = self.easing(alpha)
        if not self._started:
            self.on_start()
            self._started = True
        self.update(eased)
        if alpha >= 1.0:
            self.on_complete()

    def on_start(self):
        """Called once when animation begins. Override to capture start state."""
        pass

    def on_complete(self):
        """Called when animation finishes."""
        pass

    def update(self, alpha: float):
        """Override: update target based on eased alpha (0→1)."""
        raise NotImplementedError


# ═══════════════════════════════════════════════════════════
#  Built-in Animations
# ═══════════════════════════════════════════════════════════

class MoveTo(Animation):
    """Animate an object moving to an absolute position."""

    def __init__(self, target: PObject, x: int = None, y: int = None, easing=linear):
        super().__init__(target, easing)
        self.target_x = x
        self.target_y = y
        self.start_x = None
        self.start_y = None

    def on_start(self):
        self.start_x = self.target.x
        self.start_y = self.target.y
        if self.target_x is None:
            self.target_x = self.start_x
        if self.target_y is None:
            self.target_y = self.start_y

    def update(self, alpha: float):
        self.target.x = self.start_x + (self.target_x - self.start_x) * alpha
        self.target.y = self.start_y + (self.target_y - self.start_y) * alpha


class MoveBy(Animation):
    """Animate an object moving by a relative offset."""

    def __init__(self, target: PObject, dx: int = 0, dy: int = 0, easing=linear):
        super().__init__(target, easing)
        self.dx = dx
        self.dy = dy
        self.start_x = None
        self.start_y = None

    def on_start(self):
        self.start_x = self.target.x
        self.start_y = self.target.y

    def update(self, alpha: float):
        self.target.x = self.start_x + self.dx * alpha
        self.target.y = self.start_y + self.dy * alpha


class FadeIn(Animation):
    """Fade an object from transparent to fully opaque."""

    def __init__(self, target: PObject, easing=linear):
        super().__init__(target, easing)

    def on_start(self):
        self.target.opacity = 0.0

    def update(self, alpha: float):
        self.target.opacity = alpha


class FadeOut(Animation):
    """Fade an object from fully opaque to transparent."""

    def __init__(self, target: PObject, easing=linear):
        super().__init__(target, easing)

    def on_start(self):
        self.target.opacity = 1.0

    def update(self, alpha: float):
        self.target.opacity = 1.0 - alpha


class Scale(Animation):
    """Animate scaling an object (changes width/height for shapes)."""

    def __init__(self, target: PObject, factor: float = 2.0, easing=linear):
        super().__init__(target, easing)
        self.factor = factor
        self.start_scale_x = None
        self.start_scale_y = None

    def on_start(self):
        self.start_scale_x = self.target.scale_x
        self.start_scale_y = self.target.scale_y

    def update(self, alpha: float):
        current_factor = 1.0 + (self.factor - 1.0) * alpha
        self.target.scale_x = self.start_scale_x * current_factor
        self.target.scale_y = self.start_scale_y * current_factor
        # For shapes with width/height, update them
        if hasattr(self.target, '_orig_width'):
            self.target.width = int(self.target._orig_width * self.target.scale_x)
            self.target.height = int(self.target._orig_height * self.target.scale_y)

    def on_complete(self):
        # Store original dimensions for future scaling
        if hasattr(self.target, 'width') and not hasattr(self.target, '_orig_width'):
            self.target._orig_width = self.target.width
            self.target._orig_height = self.target.height


class Rotate(Animation):
    """Animate rotation (stores angle for render-time use)."""

    def __init__(self, target: PObject, degrees: float = 360, easing=linear):
        super().__init__(target, easing)
        self.degrees = degrees
        self.start_angle = 0

    def on_start(self):
        self.start_angle = getattr(self.target, 'angle', 0)

    def update(self, alpha: float):
        self.target.angle = self.start_angle + self.degrees * alpha


class Blink(Animation):
    """Make an object blink (toggle visibility)."""

    def __init__(self, target: PObject, blinks: int = 3, easing=linear):
        super().__init__(target, easing)
        self.blinks = blinks

    def update(self, alpha: float):
        cycle = int(alpha * self.blinks * 2)
        self.target.visible = (cycle % 2 == 0)

    def on_complete(self):
        self.target.visible = True


class ColorShift(Animation):
    """Animate color transition from current to target color."""

    def __init__(self, target: PObject, to_color, easing=linear):
        super().__init__(target, easing)
        self.to_color = parse_color(to_color)
        self.from_color = None

    def on_start(self):
        self.from_color = self.target.color

    def update(self, alpha: float):
        r = int(self.from_color[0] + (self.to_color[0] - self.from_color[0]) * alpha)
        g = int(self.from_color[1] + (self.to_color[1] - self.from_color[1]) * alpha)
        b = int(self.from_color[2] + (self.to_color[2] - self.from_color[2]) * alpha)
        a = int(self.from_color[3] + (self.to_color[3] - self.from_color[3]) * alpha)
        self.target.color = (r, g, b, a)


# ═══════════════════════════════════════════════════════════
#  Animation Groups
# ═══════════════════════════════════════════════════════════

class AnimationGroup:
    """Run multiple animations simultaneously (parallel)."""

    def __init__(self, *animations):
        self.animations = list(animations)

    def interpolate(self, alpha: float):
        for anim in self.animations:
            anim.interpolate(alpha)


class Sequence:
    """Run multiple animations one after another (serial).

    Each animation gets an equal share of the total duration.
    """

    def __init__(self, *animations):
        self.animations = list(animations)

    def interpolate(self, alpha: float):
        n = len(self.animations)
        if n == 0:
            return
        # Find which animation is active
        segment = 1.0 / n
        idx = min(int(alpha / segment), n - 1)
        local_alpha = (alpha - idx * segment) / segment
        local_alpha = max(0.0, min(1.0, local_alpha))
        self.animations[idx].interpolate(local_alpha)
