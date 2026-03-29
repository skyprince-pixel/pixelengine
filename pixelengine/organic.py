"""PixelEngine organic animation system — natural, smooth, alive motion.

Provides physics-inspired animations with procedural noise, weight/inertia,
squash-and-stretch, follow-through, and ambient idle motion. Designed to make
every animation feel handcrafted and organic rather than mechanically eased.
"""
import math
import random
from pixelengine.animation import Animation, linear, ease_out, ease_in_out
from pixelengine.pobject import PObject


# ═══════════════════════════════════════════════════════════
#  Simplex Noise (lightweight, zero-dependency)
# ═══════════════════════════════════════════════════════════

class _SimplexNoise:
    """Minimal 1D/2D simplex noise for procedural organic variation."""

    _GRAD = [(1,), (-1,), (1,), (-1,), (1,), (-1,), (1,), (-1,)]
    _PERM = list(range(256))

    def __init__(self, seed: int = 0):
        self._perm = list(self._PERM)
        rng = random.Random(seed)
        rng.shuffle(self._perm)
        self._perm = self._perm + self._perm  # double for wrapping

    def noise1d(self, x: float) -> float:
        """1D simplex noise → [-1, 1]."""
        i0 = math.floor(x)
        x0 = x - i0
        x1 = x0 - 1.0
        i0 = i0 & 255

        t0 = 1.0 - x0 * x0
        t0 = max(0.0, t0)
        t0 *= t0
        n0 = t0 * t0 * (self._perm[i0] % 2 * 2 - 1) * x0

        t1 = 1.0 - x1 * x1
        t1 = max(0.0, t1)
        t1 *= t1
        n1 = t1 * t1 * (self._perm[(i0 + 1) & 255] % 2 * 2 - 1) * x1

        return max(-1.0, min(1.0, (n0 + n1) * 2.5))


_DEFAULT_NOISE = _SimplexNoise(seed=42)


def organic_noise(t: float, frequency: float = 1.0, seed: int = 0) -> float:
    """Get organic noise value at time t. Returns [-1, 1].

    Args:
        t: Time parameter.
        frequency: How fast the noise varies.
        seed: Offset for different noise streams.
    """
    return _DEFAULT_NOISE.noise1d(t * frequency + seed * 17.31)


# ═══════════════════════════════════════════════════════════
#  Motion Feel Presets
# ═══════════════════════════════════════════════════════════

class MotionFeel:
    """Named motion personality — controls how animation *feels*.

    Bundles spring physics, noise, and timing parameters into a single
    reusable preset.

    Usage::

        feel = MotionFeel.bouncy()
        scene.play(OrganicMoveTo(obj, x=200, feel=feel), duration=1.0)

    Or use string shorthand::

        scene.play(OrganicMoveTo(obj, x=200, feel="bouncy"), duration=1.0)
    """

    def __init__(self, stiffness: float = 120.0, damping: float = 12.0,
                 noise_amp: float = 0.0, noise_freq: float = 3.0,
                 overshoot: float = 0.0, settle_time: float = 0.15,
                 anticipation: float = 0.0, secondary_delay: float = 0.0):
        self.stiffness = stiffness
        self.damping = damping
        self.noise_amp = noise_amp
        self.noise_freq = noise_freq
        self.overshoot = overshoot
        self.settle_time = settle_time
        self.anticipation = anticipation
        self.secondary_delay = secondary_delay

    @staticmethod
    def snappy():
        """Quick response, minimal overshoot — like a polished UI element."""
        return MotionFeel(stiffness=300, damping=22, noise_amp=0.005,
                          noise_freq=4, overshoot=0.02, settle_time=0.08)

    @staticmethod
    def bouncy():
        """High overshoot, playful settle — like a rubber ball."""
        return MotionFeel(stiffness=180, damping=8, noise_amp=0.02,
                          noise_freq=3, overshoot=0.25, settle_time=0.3)

    @staticmethod
    def heavy():
        """Slow acceleration, momentum carry — like a boulder."""
        return MotionFeel(stiffness=40, damping=14, noise_amp=0.01,
                          noise_freq=1.5, overshoot=0.05, settle_time=0.4,
                          anticipation=0.08)

    @staticmethod
    def floaty():
        """Dreamy slow motion with organic drift — like underwater."""
        return MotionFeel(stiffness=30, damping=10, noise_amp=0.04,
                          noise_freq=2, overshoot=0.08, settle_time=0.5)

    @staticmethod
    def elastic():
        """Springy overshoot with wobble decay — like jelly."""
        return MotionFeel(stiffness=200, damping=6, noise_amp=0.015,
                          noise_freq=5, overshoot=0.35, settle_time=0.35)

    @staticmethod
    def crisp():
        """Sharp start/stop with micro-settle — like a slide transition."""
        return MotionFeel(stiffness=400, damping=28, noise_amp=0.003,
                          noise_freq=6, overshoot=0.01, settle_time=0.05)


_FEEL_MAP = {
    "snappy": MotionFeel.snappy,
    "bouncy": MotionFeel.bouncy,
    "heavy": MotionFeel.heavy,
    "floaty": MotionFeel.floaty,
    "elastic": MotionFeel.elastic,
    "crisp": MotionFeel.crisp,
}


def _resolve_feel(feel) -> MotionFeel:
    """Resolve a feel argument to a MotionFeel instance."""
    if feel is None:
        return MotionFeel.snappy()
    if isinstance(feel, MotionFeel):
        return feel
    if isinstance(feel, str) and feel in _FEEL_MAP:
        return _FEEL_MAP[feel]()
    return MotionFeel.snappy()


# ═══════════════════════════════════════════════════════════
#  Spring Solver (shared by organic animations)
# ═══════════════════════════════════════════════════════════

def _spring_value(t: float, stiffness: float, damping: float) -> float:
    """Compute damped spring displacement at normalized time t (0→1)."""
    if t >= 1.0:
        return 1.0
    if t <= 0.0:
        return 0.0
    omega = math.sqrt(max(1.0, stiffness))
    zeta = damping / (2.0 * omega)
    if zeta < 1.0:
        omega_d = omega * math.sqrt(1.0 - zeta * zeta)
        decay = math.exp(-zeta * omega * t * 3.0)
        return 1.0 - decay * (math.cos(omega_d * t * 3.0) +
                               (zeta * omega / omega_d) * math.sin(omega_d * t * 3.0))
    else:
        decay = math.exp(-omega * t * 3.0)
        return 1.0 - decay * (1.0 + omega * t * 3.0)


# ═══════════════════════════════════════════════════════════
#  Organic Animations — One-shot
# ═══════════════════════════════════════════════════════════

class OrganicMoveTo(Animation):
    """Move with inertia, follow-through, noise jitter, and spring settle.

    Drop-in replacement for MoveTo with organic physics.

    Usage::

        scene.play(OrganicMoveTo(obj, x=200, y=100, feel="bouncy"), duration=1.5)
    """

    def __init__(self, target: PObject, x=None, y=None,
                 feel=None, easing=linear):
        super().__init__(target, easing=linear)
        self.target_x = x
        self.target_y = y
        self.feel = _resolve_feel(feel)
        self.start_x = None
        self.start_y = None
        self._seed = random.randint(0, 10000)

    def on_start(self):
        self.start_x = self.target.x
        self.start_y = self.target.y
        if self.target_x is None:
            self.target_x = self.start_x
        if self.target_y is None:
            self.target_y = self.start_y

    def update(self, alpha: float):
        f = self.feel
        s = _spring_value(alpha, f.stiffness, f.damping)

        # Add noise micro-jitter (fades out as animation completes)
        noise_fade = max(0.0, 1.0 - alpha * 1.5)
        nx = organic_noise(alpha * 10, f.noise_freq, self._seed) * f.noise_amp * noise_fade
        ny = organic_noise(alpha * 10, f.noise_freq, self._seed + 100) * f.noise_amp * noise_fade

        dx = self.target_x - self.start_x
        dy = self.target_y - self.start_y
        dist = max(1.0, math.sqrt(dx * dx + dy * dy))

        self.target.x = self.start_x + dx * s + nx * dist
        self.target.y = self.start_y + dy * s + ny * dist


class OrganicScale(Animation):
    """Scale with squash/stretch feel and spring settle.

    Usage::

        scene.play(OrganicScale(obj, factor=1.5, feel="elastic"), duration=1.0)
    """

    def __init__(self, target: PObject, factor: float = 1.5,
                 feel=None, easing=linear):
        super().__init__(target, easing=linear)
        self.factor = factor
        self.feel = _resolve_feel(feel)
        self.start_sx = None
        self.start_sy = None
        self._seed = random.randint(0, 10000)

    def on_start(self):
        self.start_sx = self.target.scale_x
        self.start_sy = self.target.scale_y

    def update(self, alpha: float):
        f = self.feel
        s = _spring_value(alpha, f.stiffness, f.damping)
        current = 1.0 + (self.factor - 1.0) * s

        # Squash/stretch: when spring overshoots, compress one axis
        overshoot = s - min(1.0, alpha * 1.2)
        sq = 1.0 + overshoot * 0.3 * f.overshoot
        st = 1.0 - overshoot * 0.15 * f.overshoot

        self.target.scale_x = self.start_sx * current * sq
        self.target.scale_y = self.start_sy * current * st

        if hasattr(self.target, '_orig_width'):
            self.target.width = max(1, int(self.target._orig_width * self.target.scale_x))
            self.target.height = max(1, int(self.target._orig_height * self.target.scale_y))


class OrganicFadeIn(Animation):
    """Fade in with breathing rhythm and organic timing.

    Usage::

        scene.play(OrganicFadeIn(obj, feel="floaty"), duration=1.0)
    """

    def __init__(self, target: PObject, feel=None, easing=None):
        super().__init__(target, easing or ease_out)
        self.feel = _resolve_feel(feel)
        self._seed = random.randint(0, 10000)

    def on_start(self):
        self.target.opacity = 0.0

    def update(self, alpha: float):
        f = self.feel
        # Smooth fade with slight breathing pulse
        base = alpha
        breath = organic_noise(alpha * 8, f.noise_freq, self._seed) * f.noise_amp * 2
        self.target.opacity = max(0.0, min(1.0, base + breath))

        # Subtle scale-in for richness
        if alpha < 0.5:
            grow = 0.9 + 0.1 * (alpha / 0.5)
            self.target.scale_x = grow
            self.target.scale_y = grow
        else:
            self.target.scale_x = 1.0
            self.target.scale_y = 1.0


class OrganicFadeOut(Animation):
    """Organic fade out with gentle shrink.

    Usage::

        scene.play(OrganicFadeOut(obj), duration=0.8)
    """

    def __init__(self, target: PObject, feel=None, easing=None):
        super().__init__(target, easing or ease_in_out)
        self.feel = _resolve_feel(feel)

    def on_start(self):
        self.target.opacity = 1.0

    def update(self, alpha: float):
        self.target.opacity = max(0.0, 1.0 - alpha)
        # Gentle shrink as it fades
        shrink = 1.0 - alpha * 0.15
        self.target.scale_x = shrink
        self.target.scale_y = shrink

    def on_complete(self):
        self.target.scale_x = 1.0
        self.target.scale_y = 1.0


class OrganicRotate(Animation):
    """Rotation with momentum and pendulum-style settle.

    Usage::

        scene.play(OrganicRotate(obj, degrees=180, feel="heavy"), duration=2.0)
    """

    def __init__(self, target: PObject, degrees: float = 360,
                 feel=None, easing=linear):
        super().__init__(target, easing=linear)
        self.degrees = degrees
        self.feel = _resolve_feel(feel)
        self.start_angle = 0

    def on_start(self):
        self.start_angle = getattr(self.target, 'angle', 0)

    def update(self, alpha: float):
        f = self.feel
        s = _spring_value(alpha, f.stiffness, f.damping)
        self.target.angle = self.start_angle + self.degrees * s


class SquashAndStretch(Animation):
    """Anticipation → launch → squash-on-land — the classic Disney principle.

    Squash compresses Y and expands X, stretch does the opposite.
    Applied automatically during velocity changes.

    Usage::

        scene.play(SquashAndStretch(obj, x=200, y=300, intensity=0.4), duration=1.5)
    """

    def __init__(self, target: PObject, x=None, y=None,
                 intensity: float = 0.3, feel=None, easing=linear):
        super().__init__(target, easing=linear)
        self.dest_x = x
        self.dest_y = y
        self.intensity = max(0.0, min(1.0, intensity))
        self.feel = _resolve_feel(feel or "bouncy")
        self.start_x = None
        self.start_y = None
        self.start_sx = None
        self.start_sy = None

    def on_start(self):
        self.start_x = self.target.x
        self.start_y = self.target.y
        self.start_sx = self.target.scale_x
        self.start_sy = self.target.scale_y
        if self.dest_x is None:
            self.dest_x = self.start_x
        if self.dest_y is None:
            self.dest_y = self.start_y

    def update(self, alpha: float):
        f = self.feel
        s = _spring_value(alpha, f.stiffness, f.damping)
        inten = self.intensity

        # Position
        self.target.x = self.start_x + (self.dest_x - self.start_x) * s
        self.target.y = self.start_y + (self.dest_y - self.start_y) * s

        # Phase-based squash/stretch
        if alpha < 0.15:
            # Anticipation: squash down
            t = alpha / 0.15
            sq = 1.0 + t * inten * 0.5
            st = 1.0 - t * inten * 0.3
            self.target.scale_x = self.start_sx * sq
            self.target.scale_y = self.start_sy * st
        elif alpha < 0.5:
            # Stretch (moving fast)
            t = (alpha - 0.15) / 0.35
            sq = 1.0 - t * inten * 0.3
            st = 1.0 + t * inten * 0.5
            self.target.scale_x = self.start_sx * sq
            self.target.scale_y = self.start_sy * st
        elif alpha < 0.7:
            # Impact squash
            t = (alpha - 0.5) / 0.2
            sq = 1.0 + (1.0 - t) * inten * 0.6
            st = 1.0 - (1.0 - t) * inten * 0.35
            self.target.scale_x = self.start_sx * sq
            self.target.scale_y = self.start_sy * st
        else:
            # Settle back to normal with spring
            t = (alpha - 0.7) / 0.3
            settle = _spring_value(t, 200, 10)
            # Current distortion → 1.0
            self.target.scale_x = self.start_sx * (1.0 + (1.0 - settle) * inten * 0.1)
            self.target.scale_y = self.start_sy * (1.0 + (1.0 - settle) * inten * 0.05)

    def on_complete(self):
        self.target.scale_x = self.start_sx
        self.target.scale_y = self.start_sy


class Breathe(Animation):
    """Continuous subtle scale oscillation — makes objects look alive.

    Usage::

        scene.play(Breathe(obj, amplitude=0.05, cycles=3), duration=3.0)
    """

    def __init__(self, target: PObject, amplitude: float = 0.05,
                 cycles: float = 2, easing=linear):
        super().__init__(target, easing=linear)
        self.amplitude = amplitude
        self.cycles = cycles
        self.base_sx = None
        self.base_sy = None

    def on_start(self):
        self.base_sx = self.target.scale_x
        self.base_sy = self.target.scale_y

    def update(self, alpha: float):
        breath = math.sin(alpha * self.cycles * 2 * math.pi) * self.amplitude
        self.target.scale_x = self.base_sx * (1.0 + breath)
        self.target.scale_y = self.base_sy * (1.0 + breath * 0.7)


class Sway(Animation):
    """Gentle lateral oscillation with noise — like swaying in wind.

    Usage::

        scene.play(Sway(obj, amplitude=8, cycles=2), duration=3.0)
    """

    def __init__(self, target: PObject, amplitude: float = 8.0,
                 cycles: float = 2, easing=linear):
        super().__init__(target, easing=linear)
        self.amplitude = amplitude
        self.cycles = cycles
        self.base_x = None
        self._seed = random.randint(0, 10000)

    def on_start(self):
        self.base_x = self.target.x

    def update(self, alpha: float):
        wave = math.sin(alpha * self.cycles * 2 * math.pi) * self.amplitude
        noise = organic_noise(alpha * 6, 3, self._seed) * self.amplitude * 0.3
        self.target.x = self.base_x + wave + noise

    def on_complete(self):
        self.target.x = self.base_x


class Float(Animation):
    """Smooth vertical drift up/down — like floating in air or water.

    Usage::

        scene.play(Float(obj, amplitude=6, cycles=2), duration=4.0)
    """

    def __init__(self, target: PObject, amplitude: float = 6.0,
                 cycles: float = 1.5, easing=linear):
        super().__init__(target, easing=linear)
        self.amplitude = amplitude
        self.cycles = cycles
        self.base_y = None
        self._phase = random.uniform(0, math.pi * 2)

    def on_start(self):
        self.base_y = self.target.y

    def update(self, alpha: float):
        wave = math.sin(alpha * self.cycles * 2 * math.pi + self._phase) * self.amplitude
        self.target.y = self.base_y + wave

    def on_complete(self):
        self.target.y = self.base_y


class Jitter(Animation):
    """Subtle random position micro-shake — nervousness or energy.

    Usage::

        scene.play(Jitter(obj, intensity=2.0), duration=1.0)
    """

    def __init__(self, target: PObject, intensity: float = 2.0, easing=linear):
        super().__init__(target, easing=linear)
        self.intensity = intensity
        self.base_x = None
        self.base_y = None
        self._seed = random.randint(0, 10000)

    def on_start(self):
        self.base_x = self.target.x
        self.base_y = self.target.y

    def update(self, alpha: float):
        freq = 20.0
        jx = organic_noise(alpha * freq, 8, self._seed) * self.intensity
        jy = organic_noise(alpha * freq, 8, self._seed + 50) * self.intensity
        self.target.x = self.base_x + jx
        self.target.y = self.base_y + jy

    def on_complete(self):
        self.target.x = self.base_x
        self.target.y = self.base_y


class Pulse(Animation):
    """Scale throb on a heartbeat rhythm.

    Usage::

        scene.play(Pulse(obj, intensity=0.15, beats=3), duration=2.0)
    """

    def __init__(self, target: PObject, intensity: float = 0.15,
                 beats: float = 2, easing=linear):
        super().__init__(target, easing=linear)
        self.intensity = intensity
        self.beats = beats
        self.base_sx = None
        self.base_sy = None

    def on_start(self):
        self.base_sx = self.target.scale_x
        self.base_sy = self.target.scale_y

    def update(self, alpha: float):
        # Heartbeat: sharp rise, slow fall
        cycle = (alpha * self.beats) % 1.0
        if cycle < 0.15:
            beat = (cycle / 0.15) ** 0.5
        elif cycle < 0.4:
            beat = 1.0 - ((cycle - 0.15) / 0.25) ** 2
        else:
            beat = 0.0
        scale = 1.0 + beat * self.intensity
        self.target.scale_x = self.base_sx * scale
        self.target.scale_y = self.base_sy * scale

    def on_complete(self):
        self.target.scale_x = self.base_sx
        self.target.scale_y = self.base_sy


class Wobble(Animation):
    """Rotational oscillation with decay — like a bobblehead settling.

    Usage::

        scene.play(Wobble(obj, angle=15, oscillations=4), duration=1.5)
    """

    def __init__(self, target: PObject, angle: float = 15.0,
                 oscillations: int = 4, easing=linear):
        super().__init__(target, easing=linear)
        self.angle = angle
        self.oscillations = oscillations
        self.base_angle = 0

    def on_start(self):
        self.base_angle = getattr(self.target, 'angle', 0)

    def update(self, alpha: float):
        decay = math.exp(-alpha * 4)
        wobble = math.sin(alpha * self.oscillations * 2 * math.pi) * self.angle * decay
        self.target.angle = self.base_angle + wobble

    def on_complete(self):
        self.target.angle = self.base_angle


class Drift(Animation):
    """Noise-driven wandering motion — like a leaf in the wind.

    Usage::

        scene.play(Drift(obj, radius=20), duration=4.0)
    """

    def __init__(self, target: PObject, radius: float = 15.0,
                 speed: float = 2.0, easing=linear):
        super().__init__(target, easing=linear)
        self.radius = radius
        self.speed = speed
        self.base_x = None
        self.base_y = None
        self._seed = random.randint(0, 10000)

    def on_start(self):
        self.base_x = self.target.x
        self.base_y = self.target.y

    def update(self, alpha: float):
        t = alpha * self.speed * 10
        dx = organic_noise(t, 1.5, self._seed) * self.radius
        dy = organic_noise(t, 1.5, self._seed + 200) * self.radius
        self.target.x = self.base_x + dx
        self.target.y = self.base_y + dy

    def on_complete(self):
        self.target.x = self.base_x
        self.target.y = self.base_y


class Anticipate(Animation):
    """Wind-up pull-back before motion — prepares the eye.

    Usage::

        scene.play(Anticipate(obj, dx=-10, dy=5), duration=0.3)
    """

    def __init__(self, target: PObject, dx: float = -10, dy: float = 0,
                 easing=None):
        super().__init__(target, easing or ease_in_out)
        self.dx = dx
        self.dy = dy
        self.base_x = None
        self.base_y = None

    def on_start(self):
        self.base_x = self.target.x
        self.base_y = self.target.y

    def update(self, alpha: float):
        # Pull back then return
        if alpha < 0.6:
            t = alpha / 0.6
            self.target.x = self.base_x + self.dx * t
            self.target.y = self.base_y + self.dy * t
        else:
            t = (alpha - 0.6) / 0.4
            self.target.x = self.base_x + self.dx * (1.0 - t)
            self.target.y = self.base_y + self.dy * (1.0 - t)

    def on_complete(self):
        self.target.x = self.base_x
        self.target.y = self.base_y


class Settle(Animation):
    """Dampened oscillation to reach rest position from current offset.

    Usage::

        scene.play(Settle(obj, oscillations=3), duration=1.0)
    """

    def __init__(self, target: PObject, oscillations: int = 3,
                 amplitude: float = 8, easing=linear):
        super().__init__(target, easing=linear)
        self.oscillations = oscillations
        self.amplitude = amplitude
        self.base_x = None
        self.base_y = None

    def on_start(self):
        self.base_x = self.target.x
        self.base_y = self.target.y

    def update(self, alpha: float):
        decay = math.exp(-alpha * 5)
        osc = math.sin(alpha * self.oscillations * 2 * math.pi) * self.amplitude * decay
        self.target.x = self.base_x + osc
        self.target.y = self.base_y + osc * 0.5

    def on_complete(self):
        self.target.x = self.base_x
        self.target.y = self.base_y


class RubberBand(Animation):
    """Elastic snap between current and target — like a rubber band release.

    Usage::

        scene.play(RubberBand(obj, x=200, y=100, elasticity=0.4), duration=1.0)
    """

    def __init__(self, target: PObject, x=None, y=None,
                 elasticity: float = 0.3, easing=linear):
        super().__init__(target, easing=linear)
        self.dest_x = x
        self.dest_y = y
        self.elasticity = elasticity
        self.start_x = None
        self.start_y = None

    def on_start(self):
        self.start_x = self.target.x
        self.start_y = self.target.y
        if self.dest_x is None:
            self.dest_x = self.start_x
        if self.dest_y is None:
            self.dest_y = self.start_y

    def update(self, alpha: float):
        # Spring with high overshoot
        s = _spring_value(alpha, 250, 7)
        self.target.x = self.start_x + (self.dest_x - self.start_x) * s
        self.target.y = self.start_y + (self.dest_y - self.start_y) * s


# ═══════════════════════════════════════════════════════════
#  Organic Modifiers (wrap any existing animation)
# ═══════════════════════════════════════════════════════════

class WithNoise:
    """Add simplex noise jitter to any animation.

    Usage::

        scene.play(WithNoise(MoveTo(obj, x=200), amplitude=3), duration=1.0)
    """

    def __init__(self, animation, amplitude: float = 2.0, freq: float = 5.0):
        self.animation = animation
        self.amplitude = amplitude
        self.freq = freq
        self._seed = random.randint(0, 10000)
        self._base_x = None
        self._base_y = None
        self._started = False

    def interpolate(self, alpha: float):
        if not self._started:
            self._started = True
            if hasattr(self.animation, 'target'):
                self._base_x = self.animation.target.x
                self._base_y = self.animation.target.y

        self.animation.interpolate(alpha)

        if hasattr(self.animation, 'target'):
            target = self.animation.target
            fade = max(0.0, 1.0 - alpha * 1.3)
            nx = organic_noise(alpha * 10, self.freq, self._seed) * self.amplitude * fade
            ny = organic_noise(alpha * 10, self.freq, self._seed + 77) * self.amplitude * fade
            target.x += nx
            target.y += ny


class WithFollow:
    """Add follow-through/secondary motion delay to any animation.

    Usage::

        scene.play(WithFollow(MoveTo(obj, x=200), delay=0.15), duration=1.5)
    """

    def __init__(self, animation, delay: float = 0.15, damping: float = 0.8):
        self.animation = animation
        self.delay = delay
        self.damping = damping

    def interpolate(self, alpha: float):
        # Apply the animation with a lagged alpha
        lagged = max(0.0, (alpha - self.delay) / (1.0 - self.delay))
        smoothed = lagged ** self.damping
        self.animation.interpolate(smoothed)


class WithAnticipation:
    """Prepend a wind-up phase before any animation.

    Usage::

        scene.play(WithAnticipation(MoveTo(obj, x=200), pullback=0.1), duration=1.5)
    """

    def __init__(self, animation, pullback: float = 0.1, wind_up_ratio: float = 0.2):
        self.animation = animation
        self.pullback = pullback
        self.wind_up_ratio = wind_up_ratio

    def interpolate(self, alpha: float):
        if alpha < self.wind_up_ratio:
            # Wind-up: slight reverse
            t = alpha / self.wind_up_ratio
            self.animation.interpolate(-self.pullback * math.sin(t * math.pi / 2))
        else:
            # Main animation
            real_alpha = (alpha - self.wind_up_ratio) / (1.0 - self.wind_up_ratio)
            self.animation.interpolate(real_alpha)


class WithSettle:
    """Append a dampened settling oscillation after any animation.

    Usage::

        scene.play(WithSettle(MoveTo(obj, x=200), oscillations=3), duration=2.0)
    """

    def __init__(self, animation, oscillations: int = 3,
                 amplitude: float = 5, settle_ratio: float = 0.3):
        self.animation = animation
        self.oscillations = oscillations
        self.amplitude = amplitude
        self.settle_ratio = settle_ratio
        self._final_x = None
        self._final_y = None

    def interpolate(self, alpha: float):
        main_end = 1.0 - self.settle_ratio
        if alpha <= main_end:
            self.animation.interpolate(alpha / main_end)
        else:
            self.animation.interpolate(1.0)
            # Capture final position once after main animation completes
            if self._final_x is None and hasattr(self.animation, 'target'):
                self._final_x = self.animation.target.x
                self._final_y = self.animation.target.y
            # Apply settling oscillation as absolute offset from final position
            settle_alpha = (alpha - main_end) / self.settle_ratio
            decay = math.exp(-settle_alpha * 5)
            osc = math.sin(settle_alpha * self.oscillations * 2 * math.pi) * self.amplitude * decay
            if hasattr(self.animation, 'target') and self._final_x is not None:
                self.animation.target.x = self._final_x + osc
                self.animation.target.y = self._final_y + osc * 0.5


class WithSquashStretch:
    """Apply squash/stretch deformation during velocity changes.

    Usage::

        scene.play(WithSquashStretch(MoveTo(obj, y=300), intensity=0.3), duration=1.0)
    """

    def __init__(self, animation, intensity: float = 0.2):
        self.animation = animation
        self.intensity = intensity
        self._prev_x = None
        self._prev_y = None

    def interpolate(self, alpha: float):
        self.animation.interpolate(alpha)

        if not hasattr(self.animation, 'target'):
            return

        target = self.animation.target
        cx, cy = target.x, target.y

        if self._prev_x is not None:
            vx = cx - self._prev_x
            vy = cy - self._prev_y
            speed = math.sqrt(vx * vx + vy * vy)

            # Stretch in direction of motion, squash perpendicular
            stretch = min(0.5, speed * 0.01 * self.intensity)
            if abs(vy) > abs(vx):
                target.scale_x = 1.0 - stretch * 0.5
                target.scale_y = 1.0 + stretch
            else:
                target.scale_x = 1.0 + stretch
                target.scale_y = 1.0 - stretch * 0.5
        self._prev_x = cx
        self._prev_y = cy


# ═══════════════════════════════════════════════════════════
#  Organic Groups
# ═══════════════════════════════════════════════════════════

class Wave:
    """Animations ripple through like a smooth wave.

    Usage::

        scene.play(Wave([FadeIn(obj) for obj in objects], delay=0.1), duration=2.0)
    """

    def __init__(self, animations, delay: float = 0.1, phase: float = 0.0):
        self.animations = list(animations)
        self.delay = delay
        self.phase = phase

    def interpolate(self, alpha: float):
        n = len(self.animations)
        if n == 0:
            return
        anim_dur = max(0.1, 1.0 - (n - 1) * self.delay)
        for i, anim in enumerate(self.animations):
            # Smooth sine-wave offset
            offset = i * self.delay + math.sin(i * 0.5 + self.phase) * self.delay * 0.3
            start = max(0.0, offset)
            if alpha < start:
                local = 0.0
            elif alpha >= start + anim_dur:
                local = 1.0
            else:
                local = (alpha - start) / anim_dur
            anim.interpolate(max(0.0, min(1.0, local)))


class Cascade:
    """Sequential entrance where each element inherits momentum feel.

    Usage::

        scene.play(Cascade([FadeIn(o) for o in objects], feel="bouncy"), duration=2.0)
    """

    def __init__(self, animations, feel=None, lag: float = 0.12):
        self.animations = list(animations)
        self.feel = _resolve_feel(feel or "bouncy")
        self.lag = lag

    def interpolate(self, alpha: float):
        n = len(self.animations)
        if n == 0:
            return
        anim_dur = max(0.1, 1.0 - (n - 1) * self.lag)
        for i, anim in enumerate(self.animations):
            start = i * self.lag
            if alpha < start:
                local = 0.0
            elif alpha >= start + anim_dur:
                local = 1.0
            else:
                local = (alpha - start) / anim_dur
                local = _spring_value(local, self.feel.stiffness, self.feel.damping)
            anim.interpolate(max(0.0, min(1.0, local)))


class Swarm:
    """Objects drift outward from a center with noise-driven paths.

    Usage::

        scene.play(Swarm([FadeIn(o) for o in objects], cx=135, cy=240), duration=2.0)
    """

    def __init__(self, animations, cx: float = 135, cy: float = 240,
                 spread: float = 50):
        self.animations = list(animations)
        self.cx = cx
        self.cy = cy
        self.spread = spread
        self._seeds = [random.randint(0, 10000) for _ in animations]

    def interpolate(self, alpha: float):
        for i, anim in enumerate(self.animations):
            anim.interpolate(alpha)
            if hasattr(anim, 'target'):
                angle = (i / max(1, len(self.animations))) * 2 * math.pi
                noise_r = organic_noise(alpha * 5, 2, self._seeds[i]) * self.spread * 0.3
                r = alpha * self.spread + noise_r
                anim.target.x += math.cos(angle) * r * (1.0 - alpha * 0.3)
                anim.target.y += math.sin(angle) * r * (1.0 - alpha * 0.3)


# ═══════════════════════════════════════════════════════════
#  Continuous Motion Updaters (attach via add_updater)
# ═══════════════════════════════════════════════════════════

def alive(amplitude: float = 0.03, speed: float = 1.5):
    """Gentle breathing + micro-drift. Makes any object look alive.

    Usage::

        obj.add_updater(alive())
    """
    seed = random.randint(0, 10000)
    _state = {"time": 0.0, "base_x": None, "base_y": None,
              "base_sx": None, "base_sy": None}

    def _update(obj, dt):
        _state["time"] += dt * speed
        t = _state["time"]
        # Capture base state on first call
        if _state["base_x"] is None:
            _state["base_x"] = obj.x
            _state["base_y"] = obj.y
            _state["base_sx"] = obj.scale_x
            _state["base_sy"] = obj.scale_y
        # Breathing scale (absolute, not accumulating)
        breath = math.sin(t * 2.0) * amplitude
        obj.scale_x = _state["base_sx"] + breath
        obj.scale_y = _state["base_sy"] + breath * 0.7
        # Micro position drift (absolute offset from base)
        obj.x = _state["base_x"] + organic_noise(t, 2, seed) * amplitude * 5
        obj.y = _state["base_y"] + organic_noise(t, 2, seed + 50) * amplitude * 3

    return _update


def hover(height: float = 4.0, speed: float = 1.0):
    """Smooth hover up/down oscillation.

    Usage::

        obj.add_updater(hover(height=6))
    """
    _state = {"base_y": None, "time": 0.0, "phase": random.uniform(0, math.pi * 2)}

    def _update(obj, dt):
        if _state["base_y"] is None:
            _state["base_y"] = obj.y
        _state["time"] += dt * speed
        t = _state["time"]
        obj.y = _state["base_y"] + math.sin(t * 2 + _state["phase"]) * height

    return _update


def orbit_idle(radius: float = 5.0, speed: float = 0.5):
    """Slow circular drift around rest position.

    Usage::

        obj.add_updater(orbit_idle(radius=8))
    """
    _state = {"base_x": None, "base_y": None, "time": 0.0,
              "phase": random.uniform(0, math.pi * 2)}

    def _update(obj, dt):
        if _state["base_x"] is None:
            _state["base_x"] = obj.x
            _state["base_y"] = obj.y
        _state["time"] += dt * speed
        t = _state["time"]
        obj.x = _state["base_x"] + math.cos(t + _state["phase"]) * radius
        obj.y = _state["base_y"] + math.sin(t * 1.3 + _state["phase"]) * radius * 0.7

    return _update


def wind_sway(intensity: float = 3.0, gust_freq: float = 0.5):
    """Wind-like lateral push with gusts.

    Usage::

        obj.add_updater(wind_sway(intensity=5))
    """
    seed = random.randint(0, 10000)
    _state = {"base_x": None, "time": 0.0}

    def _update(obj, dt):
        if _state["base_x"] is None:
            _state["base_x"] = obj.x
        _state["time"] += dt
        t = _state["time"]
        # Base wind
        wind = math.sin(t * gust_freq * 2) * intensity
        # Gusts (noise bursts)
        gust = organic_noise(t, gust_freq * 3, seed) * intensity * 1.5
        obj.x = _state["base_x"] + wind + gust

    return _update
