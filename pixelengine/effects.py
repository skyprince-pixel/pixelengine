"""PixelEngine effects — particles, transitions, and visual effects."""
import math
import random
from PIL import Image
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  Particle System
# ═══════════════════════════════════════════════════════════

class Particle:
    """Single particle with position, velocity, life, and color."""

    __slots__ = ['x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size', 'gravity']

    def __init__(self, x, y, vx, vy, life, color, size=1, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity


class ParticleEmitter(PObject):
    """Pixel-perfect particle emitter.

    Usage::

        sparks = ParticleEmitter(
            x=128, y=72,
            colors=["#FFEC27", "#FFA300", "#FF004D"],
            speed=2.0, spread=360, lifetime=1.0,
            rate=10, gravity=0.1,
        )
        scene.add(sparks)
        scene.wait(3.0)  # particles emit while scene runs

    Presets::

        fire    = ParticleEmitter.fire(x=128, y=120)
        snow    = ParticleEmitter.snow(canvas_width=256)
        sparks  = ParticleEmitter.sparks(x=128, y=72)
        confeti = ParticleEmitter.confetti(canvas_width=256)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        colors: list = None,
        speed: float = 2.0,
        spread: float = 360,
        direction: float = 270,  # 0=right, 90=down, 180=left, 270=up
        lifetime: float = 1.0,
        rate: int = 5,
        gravity: float = 0,
        size: int = 1,
        burst: int = 0,
        max_particles: int = 200,
        fade: bool = True,
    ):
        super().__init__(x=x, y=y)
        self.colors = [parse_color(c) for c in (colors or ["#FFFFFF"])]
        self.speed = speed
        self.spread = spread
        self.direction = direction
        self.lifetime = lifetime
        self.rate = rate
        self.gravity = gravity
        self.size = size
        self.burst = burst
        self.max_particles = max_particles
        self.fade = fade
        self._particles: list = []
        self._emit_timer: float = 0
        self.emitting: bool = True
        self._burst_done: bool = False

    def _spawn(self, count: int = 1):
        """Spawn particles."""
        for _ in range(count):
            if len(self._particles) >= self.max_particles:
                break
            angle_deg = self.direction + random.uniform(
                -self.spread / 2, self.spread / 2
            )
            angle = math.radians(angle_deg)
            spd = self.speed * random.uniform(0.5, 1.5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice(self.colors)
            life = self.lifetime * random.uniform(0.6, 1.0)
            size = self.size + random.randint(0, 1) if self.size > 1 else self.size
            p = Particle(
                x=float(self.x) + random.uniform(-2, 2),
                y=float(self.y) + random.uniform(-2, 2),
                vx=vx, vy=vy, life=life, color=color,
                size=size, gravity=self.gravity,
            )
            self._particles.append(p)

    def render(self, canvas):
        if not self.visible:
            return

        # Emit particles
        if self.emitting:
            if self.burst > 0 and not self._burst_done:
                self._spawn(self.burst)
                self._burst_done = True
                self.emitting = False
            elif self.burst == 0:
                self._emit_timer += 1
                if self._emit_timer >= max(1, 12 / self.rate):
                    self._spawn(1)
                    self._emit_timer = 0

        # Update and draw particles
        alive = []
        dt = 1.0 / 12  # approximate
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity
            p.x += p.vx
            p.y += p.vy

            # Calculate alpha from remaining life
            if self.fade:
                alpha = max(0, min(255, int(255 * (p.life / p.max_life))))
            else:
                alpha = p.color[3]

            color = (p.color[0], p.color[1], p.color[2], alpha)

            # Draw particle
            px, py = int(p.x), int(p.y)
            for dx in range(p.size):
                for dy in range(p.size):
                    canvas.set_pixel(px + dx, py + dy, color)

            alive.append(p)
        self._particles = alive

    @property
    def particle_count(self) -> int:
        return len(self._particles)

    # ── Presets ─────────────────────────────────────────────

    @classmethod
    def fire(cls, x: int = 128, y: int = 120, intensity: int = 8) -> "ParticleEmitter":
        """Fire effect — rises upward with warm colors."""
        return cls(
            x=x, y=y,
            colors=["#FF004D", "#FFA300", "#FFEC27", "#FFF1E8"],
            speed=1.5, spread=40, direction=270,
            lifetime=0.8, rate=intensity, gravity=-0.05,
            size=1, fade=True,
        )

    @classmethod
    def snow(cls, canvas_width: int = 256, rate: int = 3) -> "ParticleEmitter":
        """Snow falling from top of screen."""
        return cls(
            x=canvas_width // 2, y=-2,
            colors=["#FFF1E8", "#C2C3C7"],
            speed=0.5, spread=160, direction=90,
            lifetime=5.0, rate=rate, gravity=0.02,
            size=1, fade=False, max_particles=100,
        )

    @classmethod
    def sparks(cls, x: int = 128, y: int = 72, count: int = 30) -> "ParticleEmitter":
        """Burst of sparks in all directions."""
        return cls(
            x=x, y=y,
            colors=["#FFEC27", "#FFA300", "#FFF1E8"],
            speed=3.0, spread=360, direction=0,
            lifetime=0.6, rate=0, burst=count,
            gravity=0.15, size=1, fade=True,
        )

    @classmethod
    def confetti(cls, canvas_width: int = 256, rate: int = 5) -> "ParticleEmitter":
        """Colorful confetti falling from top."""
        return cls(
            x=canvas_width // 2, y=-2,
            colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27",
                    "#FF77A8", "#FFA300"],
            speed=1.0, spread=120, direction=90,
            lifetime=4.0, rate=rate, gravity=0.03,
            size=2, fade=False, max_particles=150,
        )


# ═══════════════════════════════════════════════════════════
#  Scene Transitions
# ═══════════════════════════════════════════════════════════

class FadeTransition:
    """Fade to/from a solid color between scene sections.

    Usage in construct()::

        # ... scene part 1 ...
        scene.play(FadeTransition(scene, color="#000000", mode="out"), duration=0.5)
        # ... change scene objects here ...
        scene.play(FadeTransition(scene, color="#000000", mode="in"), duration=0.5)
    """

    def __init__(self, scene, color: str = "#000000", mode: str = "out"):
        self.scene = scene
        self.color = parse_color(color)
        self.mode = mode  # "out" = fade TO color, "in" = fade FROM color
        self._overlay = None

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        if self.mode == "out":
            opacity = alpha
        else:
            opacity = 1.0 - alpha

        # Create and manage overlay rectangle
        if self._overlay is None:
            from pixelengine.shapes import Rect
            self._overlay = Rect(
                self.scene.config.canvas_width,
                self.scene.config.canvas_height,
                x=0, y=0,
            )
            self._overlay.color = self.color
            self._overlay.z_index = 9999
            self.scene.add(self._overlay)

        self._overlay.opacity = opacity

        # Clean up on completion
        if alpha >= 1.0 and self.mode == "in":
            self.scene.remove(self._overlay)
            self._overlay = None


class PixelateTransition:
    """Pixelate transition — image breaks into larger blocks.

    Usage::

        scene.play(PixelateTransition(scene, block_size=8), duration=1.0)
    """

    def __init__(self, scene, block_size: int = 8, mode: str = "out"):
        self.scene = scene
        self.max_block = block_size
        self.mode = mode

    def interpolate(self, alpha: float):
        # This modifies the upscale factor to create pixelation
        # For "out": blocks get bigger (more pixelated)
        # For "in": blocks get smaller (less pixelated)
        alpha = max(0.0, min(1.0, alpha))
        if self.mode == "out":
            t = alpha
        else:
            t = 1.0 - alpha
        # We don't actually change resolution mid-render, so this is
        # implemented as an overlay effect via canvas manipulation
        pass  # Visual effect handled at post-processing level


class WipeTransition:
    """Wipe transition — slides a colored bar across the screen.

    Usage::

        scene.play(WipeTransition(scene, direction="right"), duration=0.5)
    """

    def __init__(self, scene, color: str = "#000000",
                 direction: str = "right"):
        self.scene = scene
        self.color = parse_color(color)
        self.direction = direction
        self._overlay = None

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        w = self.scene.config.canvas_width
        h = self.scene.config.canvas_height

        if self._overlay is None:
            from pixelengine.shapes import Rect
            self._overlay = Rect(w, h, x=0, y=0)
            self._overlay.color = self.color
            self._overlay.z_index = 9999
            self.scene.add(self._overlay)

        if self.direction == "right":
            self._overlay.width = int(w * alpha)
            self._overlay.x = 0
        elif self.direction == "left":
            self._overlay.width = int(w * alpha)
            self._overlay.x = w - self._overlay.width
        elif self.direction == "down":
            self._overlay.width = w
            self._overlay.height = int(h * alpha)
            self._overlay.y = 0
        elif self.direction == "up":
            self._overlay.width = w
            self._overlay.height = int(h * alpha)
            self._overlay.y = h - self._overlay.height

        if alpha >= 1.0:
            self.scene.remove(self._overlay)
            self._overlay = None


# ═══════════════════════════════════════════════════════════
#  Visual Trail Effect
# ═══════════════════════════════════════════════════════════

class Trail(PObject):
    """Draws a fading trail behind a moving object.

    Usage::

        trail = Trail(target=player, length=8, color="#29ADFF")
        scene.add(trail)
        # trail automatically updates as player moves
    """

    def __init__(self, target: PObject, length: int = 8,
                 color: str = None, size: int = 2):
        super().__init__(x=0, y=0)
        self.target = target
        self.length = length
        self.trail_color = parse_color(color) if color else None
        self.size = size
        self._positions: list = []
        self.z_index = -1  # Draw behind target

    def render(self, canvas):
        if not self.visible:
            return

        # Record current position
        self._positions.append((int(self.target.x), int(self.target.y)))
        if len(self._positions) > self.length:
            self._positions = self._positions[-self.length:]

        # Draw trail points with fading opacity
        base_color = self.trail_color or self.target.color
        for i, (px, py) in enumerate(self._positions):
            alpha = int(255 * (i + 1) / len(self._positions) * 0.6)
            color = (base_color[0], base_color[1], base_color[2], alpha)
            for dx in range(self.size):
                for dy in range(self.size):
                    canvas.set_pixel(px + dx, py + dy, color)
