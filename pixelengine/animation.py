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


# ── v4 Additional Easing Functions ──────────────────────────


def back_in(t: float) -> float:
    """Pull back before accelerating forward."""
    c = 1.70158
    return (c + 1) * t * t * t - c * t * t


def back_out(t: float) -> float:
    """Overshoot the target then settle back."""
    c = 1.70158
    t -= 1
    return 1 + (c + 1) * t * t * t + c * t * t


def back_in_out(t: float) -> float:
    """Pull back, accelerate, overshoot, then settle."""
    c = 1.70158 * 1.525
    if t < 0.5:
        return (((2 * t) ** 2) * ((c + 1) * 2 * t - c)) / 2
    else:
        return (((2 * t - 2) ** 2) * ((c + 1) * (2 * t - 2) + c) + 2) / 2


def circ_in(t: float) -> float:
    """Circular acceleration from zero."""
    return 1 - math.sqrt(1 - t * t)


def circ_out(t: float) -> float:
    """Circular deceleration to zero."""
    t -= 1
    return math.sqrt(1 - t * t)


def expo_in(t: float) -> float:
    """Exponential acceleration from zero."""
    return 0.0 if t == 0 else 2 ** (10 * (t - 1))


def expo_out(t: float) -> float:
    """Exponential deceleration to zero."""
    return 1.0 if t == 1 else 1 - 2 ** (-10 * t)


def sine_in(t: float) -> float:
    """Sinusoidal acceleration from zero."""
    return 1 - math.cos(t * math.pi / 2)


def sine_out(t: float) -> float:
    """Sinusoidal deceleration to zero."""
    return math.sin(t * math.pi / 2)


def steps(n: int = 4):
    """Step function easing — pixel-art friendly snappy motion.

    Returns an easing function that quantizes into ``n`` discrete steps.

    Usage::

        scene.play(MoveTo(obj, x=200), duration=1.0, easing=steps(8))
    """
    def _steps(t: float) -> float:
        return math.floor(t * n) / n
    return _steps


def custom_bezier(x1: float, y1: float, x2: float, y2: float):
    """Create a custom cubic-bezier easing curve.

    Emulates CSS ``cubic-bezier(x1, y1, x2, y2)``.

    Usage::

        my_ease = custom_bezier(0.68, -0.55, 0.27, 1.55)
        scene.play(MoveTo(obj, x=200), easing=my_ease, duration=1.0)
    """
    def _bezier(t: float) -> float:
        # Newton-Raphson to solve for t on the x-axis, then evaluate y
        # Simple iterative approach for the cubic bezier
        guess = t
        for _ in range(8):
            # x(t) for cubic bezier with p0=0, p3=1
            cx = 3 * x1 * guess * (1 - guess) ** 2 + \
                 3 * x2 * guess ** 2 * (1 - guess) + guess ** 3
            dx = 3 * x1 * (1 - guess) ** 2 + \
                 6 * (x2 - x1) * guess * (1 - guess) + 3 * (1 - x2) * guess ** 2
            if abs(dx) < 1e-9:
                break
            guess -= (cx - t) / dx
            guess = max(0.0, min(1.0, guess))
        # Evaluate y at solved t
        return 3 * y1 * guess * (1 - guess) ** 2 + \
               3 * y2 * guess ** 2 * (1 - guess) + guess ** 3
    return _bezier


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
    # v4 additions
    "back_in": back_in,
    "back_out": back_out,
    "back_in_out": back_in_out,
    "circ_in": circ_in,
    "circ_out": circ_out,
    "expo_in": expo_in,
    "expo_out": expo_out,
    "sine_in": sine_in,
    "sine_out": sine_out,
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
        self._completed = False

    def interpolate(self, raw_alpha: float):
        """Called each frame with raw alpha (0→1). Applies easing."""
        alpha = max(0.0, min(1.0, raw_alpha))
        eased = self.easing(alpha)
        if not self._started:
            self.on_start()
            self._started = True
        self.update(eased)
        if alpha >= 1.0 and not self._completed:
            self._completed = True
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
        # Capture original dimensions before scaling begins
        if hasattr(self.target, 'width') and not hasattr(self.target, '_orig_width'):
            self.target._orig_width = self.target.width
            self.target._orig_height = self.target.height

    def update(self, alpha: float):
        current_factor = 1.0 + (self.factor - 1.0) * alpha
        self.target.scale_x = self.start_scale_x * current_factor
        self.target.scale_y = self.start_scale_y * current_factor
        # For shapes with width/height, update them
        if hasattr(self.target, '_orig_width'):
            self.target.width = int(self.target._orig_width * self.target.scale_x)
            self.target.height = int(self.target._orig_height * self.target.scale_y)


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
        # Finalize all previous animations that haven't been finalized yet
        for i in range(idx):
            if not getattr(self.animations[i], '_seq_finalized', False):
                self.animations[i].interpolate(1.0)
                self.animations[i]._seq_finalized = True
        local_alpha = (alpha - idx * segment) / segment
        local_alpha = max(0.0, min(1.0, local_alpha))
        self.animations[idx].interpolate(local_alpha)


class Stagger:
    """Run animations with a staggered time offset between each.

    Creates a wave/cascade effect where each animation starts ``lag``
    fraction of the total duration after the previous one.

    Usage::

        bars = [Rect(20, h, x=30+i*25, y=200-h) for i, h in enumerate(data)]
        scene.play(Stagger([FadeIn(b) for b in bars], lag=0.1), duration=2.0)

    Args:
        animations: List of Animation objects.
        lag: Time ratio (0-1) between each animation's start.
             E.g. lag=0.1 means each starts 10% of total duration after the previous.
        easing: Optional easing applied to each individual animation.
    """

    def __init__(self, animations, lag: float = 0.1, easing=None):
        self.animations = list(animations)
        self.lag = lag
        if easing is not None:
            for anim in self.animations:
                if hasattr(anim, 'easing'):
                    anim.easing = get_easing(easing)

    def interpolate(self, alpha: float):
        n = len(self.animations)
        if n == 0:
            return
        # Each animation starts at offset i * lag and has duration (1 - (n-1)*lag)
        anim_duration = max(0.1, 1.0 - (n - 1) * self.lag)
        for i, anim in enumerate(self.animations):
            start = i * self.lag
            if alpha < start:
                local_alpha = 0.0
            elif alpha >= start + anim_duration:
                local_alpha = 1.0
            else:
                local_alpha = (alpha - start) / anim_duration
            anim.interpolate(max(0.0, min(1.0, local_alpha)))


# ═══════════════════════════════════════════════════════════
#  Animation Modifiers (v4)
# ═══════════════════════════════════════════════════════════

class Delayed:
    """Delay the start of an animation by a fraction of total duration.

    Usage::

        scene.play(Delayed(FadeIn(obj), delay=0.3), duration=2.0)

    Args:
        animation: The wrapped animation.
        delay: Fraction of total duration to wait (0.0–0.9).
    """

    def __init__(self, animation, delay: float = 0.3):
        self.animation = animation
        self.delay = max(0.0, min(0.9, delay))

    def interpolate(self, alpha: float):
        if alpha < self.delay:
            return
        local = (alpha - self.delay) / (1.0 - self.delay)
        self.animation.interpolate(max(0.0, min(1.0, local)))


class Reversed:
    """Play an animation in reverse (alpha goes 1→0).

    Usage::

        scene.play(Reversed(GrowFromPoint(obj, 240, 135)), duration=1.0)
    """

    def __init__(self, animation):
        self.animation = animation

    def interpolate(self, alpha: float):
        self.animation.interpolate(1.0 - alpha)


class Looped:
    """Loop an animation multiple times within the total duration.

    Usage::

        scene.play(Looped(Rotate(obj, 360), count=3), duration=3.0)

    Args:
        animation: The wrapped animation.
        count: Number of times to loop.
    """

    def __init__(self, animation, count: int = 2):
        self.animation = animation
        self.count = max(1, count)
        self._prev_cycle = -1

    def interpolate(self, alpha: float):
        cycle_alpha = (alpha * self.count) % 1.0
        current_cycle = int(alpha * self.count)
        # Reset animation state at cycle boundaries
        if current_cycle != self._prev_cycle and current_cycle > 0:
            if hasattr(self.animation, '_started'):
                self.animation._started = False
                self.animation._completed = False
            self._prev_cycle = current_cycle
        # At the very end, ensure we hit 1.0
        if alpha >= 1.0:
            cycle_alpha = 1.0
        self.animation.interpolate(cycle_alpha)


# ═══════════════════════════════════════════════════════════
#  Spring Physics Animations (v4)
# ═══════════════════════════════════════════════════════════

class SpringTo(Animation):
    """Move an object to a target position with spring physics.

    Produces natural overshoot and settle motion using a damped spring.

    Usage::

        scene.play(SpringTo(obj, x=240, y=135, stiffness=120, damping=10), duration=2.0)

    Args:
        stiffness: Spring constant (higher = snappier). Default 120.
        damping: Damping factor (higher = less oscillation). Default 12.
    """

    def __init__(self, target: PObject, x: int = None, y: int = None,
                 stiffness: float = 120.0, damping: float = 12.0, easing=linear):
        super().__init__(target, easing=linear)  # Spring does its own easing
        self.target_x = x
        self.target_y = y
        self.stiffness = stiffness
        self.damping = damping
        self.start_x = None
        self.start_y = None

    def _spring_value(self, t: float) -> float:
        """Compute spring displacement at normalized time t (0→1).

        Uses underdamped spring equation for natural overshoot.
        """
        if t >= 1.0:
            return 1.0
        if t <= 0.0:
            return 0.0
        omega = math.sqrt(self.stiffness)
        zeta = self.damping / (2.0 * omega)
        if zeta < 1.0:
            # Underdamped — oscillates
            omega_d = omega * math.sqrt(1.0 - zeta * zeta)
            decay = math.exp(-zeta * omega * t * 3.0)
            return 1.0 - decay * (math.cos(omega_d * t * 3.0) +
                                   (zeta * omega / omega_d) * math.sin(omega_d * t * 3.0))
        else:
            # Critically/overdamped — no oscillation
            decay = math.exp(-omega * t * 3.0)
            return 1.0 - decay * (1.0 + omega * t * 3.0)

    def on_start(self):
        self.start_x = self.target.x
        self.start_y = self.target.y
        if self.target_x is None:
            self.target_x = self.start_x
        if self.target_y is None:
            self.target_y = self.start_y

    def update(self, alpha: float):
        s = self._spring_value(alpha)
        self.target.x = self.start_x + (self.target_x - self.start_x) * s
        self.target.y = self.start_y + (self.target_y - self.start_y) * s


class SpringScale(Animation):
    """Scale an object with spring bounce physics.

    Usage::

        scene.play(SpringScale(obj, factor=1.5, stiffness=200, damping=8), duration=1.0)
    """

    def __init__(self, target: PObject, factor: float = 1.5,
                 stiffness: float = 200.0, damping: float = 8.0, easing=linear):
        super().__init__(target, easing=linear)
        self.factor = factor
        self.stiffness = stiffness
        self.damping = damping
        self.start_scale_x = None
        self.start_scale_y = None

    def _spring_value(self, t: float) -> float:
        if t >= 1.0:
            return 1.0
        if t <= 0.0:
            return 0.0
        omega = math.sqrt(self.stiffness)
        zeta = self.damping / (2.0 * omega)
        if zeta < 1.0:
            omega_d = omega * math.sqrt(1.0 - zeta * zeta)
            decay = math.exp(-zeta * omega * t * 3.0)
            return 1.0 - decay * (math.cos(omega_d * t * 3.0) +
                                   (zeta * omega / omega_d) * math.sin(omega_d * t * 3.0))
        else:
            decay = math.exp(-omega * t * 3.0)
            return 1.0 - decay * (1.0 + omega * t * 3.0)

    def on_start(self):
        self.start_scale_x = self.target.scale_x
        self.start_scale_y = self.target.scale_y

    def update(self, alpha: float):
        s = self._spring_value(alpha)
        current_factor = 1.0 + (self.factor - 1.0) * s
        self.target.scale_x = self.start_scale_x * current_factor
        self.target.scale_y = self.start_scale_y * current_factor
        if hasattr(self.target, '_orig_width'):
            self.target.width = max(1, int(self.target._orig_width * self.target.scale_x))
            self.target.height = max(1, int(self.target._orig_height * self.target.scale_y))
