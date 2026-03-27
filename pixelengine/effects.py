"""PixelEngine effects — particles, transitions, visual effects, and helpers."""
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

    __slots__ = [
        'x', 'y', 'vx', 'vy', 'life', 'max_life',
        'color', 'size', 'gravity', 'friction', 'color_end',
    ]

    def __init__(self, x, y, vx, vy, life, color, size=1,
                 gravity=0, friction=1.0, color_end=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.friction = friction
        self.color_end = color_end  # If set, color lerps over lifetime


class ParticleEmitter(PObject):
    """Pixel-perfect particle emitter with color gradients and wind.

    Usage::

        sparks = ParticleEmitter(
            x=128, y=72,
            colors=["#FFEC27", "#FFA300", "#FF004D"],
            speed=2.0, spread=360, lifetime=1.0,
            rate=10, gravity=0.1,
        )
        scene.add(sparks)
        scene.wait(3.0)

    Color gradient over lifetime::

        emitter = ParticleEmitter(
            colors=["#FFEC27"],
            color_end="#FF004D",  # particles shift color as they age
        )

    Presets::

        fire     = ParticleEmitter.fire(x=128, y=120)
        snow     = ParticleEmitter.snow(canvas_width=256)
        sparks   = ParticleEmitter.sparks(x=128, y=72)
        confetti = ParticleEmitter.confetti(canvas_width=256)
        smoke    = ParticleEmitter.smoke(x=128, y=120)
        rain     = ParticleEmitter.rain(canvas_width=256)
        bubbles  = ParticleEmitter.bubbles(x=128, y=120)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        colors: list = None,
        color_end: str = None,
        speed: float = 2.0,
        spread: float = 360,
        direction: float = 270,
        lifetime: float = 1.0,
        rate: int = 5,
        gravity: float = 0,
        wind_x: float = 0,
        wind_y: float = 0,
        friction: float = 1.0,
        size: int = 1,
        size_decay: bool = False,
        burst: int = 0,
        max_particles: int = 200,
        fade: bool = True,
        spawn_radius: float = 2.0,
    ):
        super().__init__(x=x, y=y)
        self.colors = [parse_color(c) for c in (colors or ["#FFFFFF"])]
        self.color_end = parse_color(color_end) if color_end else None
        self.speed = speed
        self.spread = spread
        self.direction = direction
        self.lifetime = lifetime
        self.rate = rate
        self.gravity = gravity
        self.wind_x = wind_x
        self.wind_y = wind_y
        self.friction = friction
        self.size = size
        self.size_decay = size_decay
        self.burst = burst
        self.max_particles = max_particles
        self.fade = fade
        self.spawn_radius = spawn_radius
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
            sr = self.spawn_radius
            p = Particle(
                x=float(self.x) + random.uniform(-sr, sr),
                y=float(self.y) + random.uniform(-sr, sr),
                vx=vx, vy=vy, life=life, color=color,
                size=size, gravity=self.gravity,
                friction=self.friction,
                color_end=self.color_end,
            )
            self._particles.append(p)

    def stop(self):
        """Stop emitting new particles (existing ones continue)."""
        self.emitting = False

    def clear(self):
        """Remove all particles immediately."""
        self._particles.clear()

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
        dt = 1.0 / 12  # Approximate frame time at default FPS
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue

            # Physics
            p.vy += p.gravity
            p.vx += self.wind_x * dt
            p.vy += self.wind_y * dt
            p.vx *= p.friction
            p.vy *= p.friction
            p.x += p.vx
            p.y += p.vy

            life_t = 1.0 - (p.life / p.max_life)  # 0→1 as particle ages

            # Color gradient over lifetime
            if p.color_end is not None:
                r = int(p.color[0] + (p.color_end[0] - p.color[0]) * life_t)
                g = int(p.color[1] + (p.color_end[1] - p.color[1]) * life_t)
                b = int(p.color[2] + (p.color_end[2] - p.color[2]) * life_t)
            else:
                r, g, b = p.color[0], p.color[1], p.color[2]

            # Alpha fade
            if self.fade:
                alpha = max(0, min(255, int(255 * (p.life / p.max_life))))
            else:
                alpha = p.color[3]

            color = (r, g, b, alpha)

            # Size decay over lifetime
            draw_size = p.size
            if self.size_decay:
                draw_size = max(1, int(p.size * (p.life / p.max_life)))

            # Draw particle
            px, py = int(p.x), int(p.y)
            for dx in range(draw_size):
                for dy in range(draw_size):
                    canvas.set_pixel(px + dx, py + dy, color)

            alive.append(p)
        self._particles = alive

    @property
    def particle_count(self) -> int:
        return len(self._particles)

    @property
    def is_alive(self) -> bool:
        """True if still emitting or has active particles."""
        return self.emitting or len(self._particles) > 0

    # ── Presets ─────────────────────────────────────────────

    @classmethod
    def fire(cls, x: int = 128, y: int = 120, intensity: int = 8) -> "ParticleEmitter":
        """Fire effect — rises upward with warm→white gradient."""
        return cls(
            x=x, y=y,
            colors=["#FF004D", "#FFA300", "#FFEC27"],
            color_end="#FFF1E8",
            speed=1.5, spread=40, direction=270,
            lifetime=0.8, rate=intensity, gravity=-0.05,
            size=1, fade=True, friction=0.98,
        )

    @classmethod
    def smoke(cls, x: int = 128, y: int = 120, intensity: int = 4) -> "ParticleEmitter":
        """Smoke rising upward — gray fading particles."""
        return cls(
            x=x, y=y,
            colors=["#5F574F", "#83769C"],
            speed=0.8, spread=50, direction=270,
            lifetime=1.5, rate=intensity, gravity=-0.02,
            size=2, size_decay=True, fade=True,
            friction=0.97, spawn_radius=3,
        )

    @classmethod
    def snow(cls, canvas_width: int = 256, rate: int = 3) -> "ParticleEmitter":
        """Snow falling from top of screen with gentle sway."""
        return cls(
            x=canvas_width // 2, y=-2,
            colors=["#FFF1E8", "#C2C3C7"],
            speed=0.5, spread=160, direction=90,
            lifetime=5.0, rate=rate, gravity=0.02,
            wind_x=0.3,
            size=1, fade=False, max_particles=100,
            spawn_radius=canvas_width // 2,
        )

    @classmethod
    def rain(cls, canvas_width: int = 256, rate: int = 8) -> "ParticleEmitter":
        """Rain falling — fast vertical streaks."""
        return cls(
            x=canvas_width // 2, y=-2,
            colors=["#29ADFF", "#1D2B53"],
            speed=4.0, spread=10, direction=95,
            lifetime=1.0, rate=rate, gravity=0.1,
            size=1, fade=False, max_particles=150,
            spawn_radius=canvas_width // 2,
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
            friction=0.96,
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
            spawn_radius=canvas_width // 2,
        )

    @classmethod
    def bubbles(cls, x: int = 128, y: int = 120, rate: int = 3) -> "ParticleEmitter":
        """Bubbles floating upward."""
        return cls(
            x=x, y=y,
            colors=["#29ADFF", "#C2C3C7", "#FFF1E8"],
            speed=0.8, spread=30, direction=270,
            lifetime=2.0, rate=rate, gravity=-0.03,
            size=2, fade=True, friction=0.99,
            spawn_radius=5,
        )

    @classmethod
    def explosion(cls, x: int = 128, y: int = 72, count: int = 50) -> "ParticleEmitter":
        """Big fiery explosion burst."""
        return cls(
            x=x, y=y,
            colors=["#FF004D", "#FFA300", "#FFEC27"],
            color_end="#5F574F",
            speed=4.0, spread=360, direction=0,
            lifetime=0.8, rate=0, burst=count,
            gravity=0.12, size=2, size_decay=True,
            fade=True, friction=0.95,
        )


# ═══════════════════════════════════════════════════════════
#  Scene Transitions
# ═══════════════════════════════════════════════════════════

class FadeTransition:
    """Fade to/from a solid color between scene sections.

    Usage::

        scene.play(FadeTransition(scene, mode="out"), duration=0.5)
        # ... change scene ...
        scene.play(FadeTransition(scene, mode="in"), duration=0.5)
    """

    def __init__(self, scene, color: str = "#000000", mode: str = "out"):
        self.scene = scene
        self.color = parse_color(color)
        self.mode = mode
        self._overlay = None

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        if self.mode == "out":
            opacity = alpha
        else:
            opacity = 1.0 - alpha

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

        # Clean up overlay when transition completes
        if alpha >= 1.0:
            self.scene.remove(self._overlay)
            self._overlay = None


class WipeTransition:
    """Wipe transition — slides a colored bar across the screen.

    Directions: "right", "left", "down", "up"
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
            self._overlay = Rect(max(1, w), max(1, h), x=0, y=0)
            self._overlay.color = self.color
            self._overlay.z_index = 9999
            self.scene.add(self._overlay)

        if self.direction == "right":
            self._overlay.width = max(1, int(w * alpha))
            self._overlay.x = 0
        elif self.direction == "left":
            self._overlay.width = max(1, int(w * alpha))
            self._overlay.x = w - self._overlay.width
        elif self.direction == "down":
            self._overlay.width = w
            self._overlay.height = max(1, int(h * alpha))
            self._overlay.y = 0
        elif self.direction == "up":
            self._overlay.width = w
            self._overlay.height = max(1, int(h * alpha))
            self._overlay.y = h - self._overlay.height

        if alpha >= 1.0:
            self.scene.remove(self._overlay)
            self._overlay = None


class IrisTransition(PObject):
    """Iris wipe — a circle that expands or contracts to reveal/hide.

    Usage::

        scene.play(IrisTransition(scene, mode="out", cx=128, cy=72), duration=0.8)
    """

    def __init__(self, scene, mode: str = "out",
                 cx: int = None, cy: int = None,
                 color: str = "#000000"):
        super().__init__(x=0, y=0)
        self.scene = scene
        self.mode = mode
        self.iris_color = parse_color(color)
        w = scene.config.canvas_width
        h = scene.config.canvas_height
        self.cx = cx if cx is not None else w // 2
        self.cy = cy if cy is not None else h // 2
        self.max_radius = int(math.sqrt(w * w + h * h) / 2) + 2
        self.z_index = 9998
        self._added = False

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        if not self._added:
            self.scene.add(self)
            self._added = True

        if self.mode == "out":
            # Circle shrinks: start big, end at 0
            self._radius = int(self.max_radius * (1.0 - alpha))
        else:
            # Circle grows: start at 0, end big
            self._radius = int(self.max_radius * alpha)

        if alpha >= 1.0 and self.mode == "in":
            self.scene.remove(self)

    def render(self, canvas):
        if not self.visible:
            return
        r = getattr(self, '_radius', self.max_radius)
        # Use PIL to draw the iris mask efficiently
        w, h = canvas.width, canvas.height
        mask = Image.new("RGBA", (w, h), self.iris_color)
        # Cut out the iris circle by drawing a transparent ellipse
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        cx, cy = self.cx, self.cy
        if r > 0:
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=(0, 0, 0, 0),
            )
        canvas.blit(mask, 0, 0)


class DissolveTransition:
    """Random pixel dissolve — pixels randomly appear/disappear.

    Usage::

        scene.play(DissolveTransition(scene, mode="out", seed=42), duration=1.0)
    """

    def __init__(self, scene, color: str = "#000000", mode: str = "out",
                 seed: int = None):
        self.scene = scene
        self.color = parse_color(color)
        self.mode = mode
        self._rng = random.Random(seed)
        self._overlay_obj = None
        self._pixel_order = None

    def interpolate(self, alpha: float):
        alpha = max(0.0, min(1.0, alpha))
        w = self.scene.config.canvas_width
        h = self.scene.config.canvas_height

        # Build randomized pixel order on first call
        if self._pixel_order is None:
            self._pixel_order = [(x, y) for y in range(h) for x in range(w)]
            self._rng.shuffle(self._pixel_order)
            self._overlay_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            self._overlay_obj = _ImageOverlay(self._overlay_img, z_index=9999)
            self.scene.add(self._overlay_obj)

        total = len(self._pixel_order)
        if self.mode == "out":
            count = int(total * alpha)
        else:
            count = int(total * (1.0 - alpha))

        # Reset and draw
        self._overlay_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for i in range(count):
            px, py = self._pixel_order[i]
            self._overlay_img.putpixel((px, py), self.color)
        self._overlay_obj._image = self._overlay_img

        if alpha >= 1.0:
            self.scene.remove(self._overlay_obj)


class _ImageOverlay(PObject):
    """Internal helper: renders a PIL Image as an overlay."""

    def __init__(self, image: Image.Image, z_index: int = 9999):
        super().__init__(x=0, y=0)
        self._image = image
        self.z_index = z_index

    def render(self, canvas):
        if not self.visible:
            return
        canvas.blit(self._image, 0, 0)


# ═══════════════════════════════════════════════════════════
#  Visual Effects
# ═══════════════════════════════════════════════════════════

class Trail(PObject):
    """Draws a fading trail behind a moving object.

    Usage::

        trail = Trail(target=player, length=8, color="#29ADFF")
        scene.add(trail)
    """

    def __init__(self, target: PObject, length: int = 8,
                 color: str = None, size: int = 2,
                 style: str = "dots"):
        super().__init__(x=0, y=0)
        self.target = target
        self.length = length
        self.trail_color = parse_color(color) if color else None
        self.size = size
        self.style = style  # "dots", "line", "fade"
        self._positions: list = []
        self.z_index = -1

    def render(self, canvas):
        if not self.visible:
            return

        # Record current position
        self._positions.append((int(self.target.x), int(self.target.y)))
        if len(self._positions) > self.length:
            self._positions = self._positions[-self.length:]

        base_color = self.trail_color or self.target.color
        n = len(self._positions)

        if self.style == "line" and n >= 2:
            # Draw connected line segments
            for i in range(n - 1):
                x1, y1 = self._positions[i]
                x2, y2 = self._positions[i + 1]
                alpha = int(255 * (i + 1) / n * 0.6)
                color = (base_color[0], base_color[1], base_color[2], alpha)
                # Simple line between points
                steps = max(abs(x2 - x1), abs(y2 - y1), 1)
                for s in range(steps + 1):
                    t = s / steps
                    px = int(x1 + (x2 - x1) * t)
                    py = int(y1 + (y2 - y1) * t)
                    canvas.set_pixel(px, py, color)
        else:
            # Dots style (default)
            for i, (px, py) in enumerate(self._positions):
                alpha = int(255 * (i + 1) / n * 0.6)
                color = (base_color[0], base_color[1], base_color[2], alpha)
                for dx in range(self.size):
                    for dy in range(self.size):
                        canvas.set_pixel(px + dx, py + dy, color)


class ScreenFlash(PObject):
    """Full-screen flash that fades out over time.

    Usage::

        flash = ScreenFlash(color="#FFFFFF", duration=0.3)
        scene.add(flash)
        scene.wait(0.5)
    """

    def __init__(self, color: str = "#FFFFFF", duration: float = 0.3):
        super().__init__(x=0, y=0, color=color)
        self.duration = duration
        self._timer: float = 0
        self.z_index = 9990

    def render(self, canvas):
        if not self.visible:
            return

        self._timer += 1.0 / 12  # approx frame time
        if self._timer >= self.duration:
            self.visible = False
            return

        t = self._timer / self.duration
        alpha = int(255 * (1.0 - t))
        color = (*self.color[:3], alpha)
        # Use PIL image blit instead of pixel-by-pixel
        overlay = Image.new("RGBA", (canvas.width, canvas.height), color)
        canvas.blit(overlay, 0, 0)


class Outline(PObject):
    """Draw a pixel outline border around the canvas or a region.

    Useful for highlighting areas in educational videos.

    Usage::

        border = Outline(x=10, y=10, width=50, height=30,
                         color="#FF004D", thickness=1)
        scene.add(border)
    """

    def __init__(self, x: int = 0, y: int = 0,
                 width: int = 0, height: int = 0,
                 color: str = "#FFFFFF", thickness: int = 1):
        super().__init__(x=x, y=y, color=color)
        self.width = width
        self.height = height
        self.thickness = thickness
        self.z_index = 100

    def render(self, canvas):
        if not self.visible or self.width <= 0 or self.height <= 0:
            return
        color = self.get_render_color()
        # Use PIL ImageDraw for efficient border rendering
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for t in range(self.thickness):
            draw.rectangle(
                [t, t, self.width - 1 - t, self.height - 1 - t],
                outline=color,
            )
        canvas.blit(img, int(self.x), int(self.y))


class Grid(PObject):
    """Draw a pixel grid overlay — great for educational content.

    Usage::

        grid = Grid(cell_size=16, color="#1D2B53", canvas_width=256, canvas_height=144)
        scene.add(grid)
    """

    def __init__(
        self,
        cell_size: int = 16,
        canvas_width: int = 256,
        canvas_height: int = 144,
        color: str = "#1D2B53",
        x: int = 0,
        y: int = 0,
    ):
        super().__init__(x=x, y=y, color=color)
        self.cell_size = cell_size
        self.grid_width = canvas_width
        self.grid_height = canvas_height
        self.z_index = 90

    def render(self, canvas):
        if not self.visible:
            return
        color = self.get_render_color()
        ox, oy = int(self.x), int(self.y)

        # Vertical lines
        for gx in range(0, self.grid_width + 1, self.cell_size):
            for gy in range(self.grid_height):
                canvas.set_pixel(ox + gx, oy + gy, color)

        # Horizontal lines
        for gy in range(0, self.grid_height + 1, self.cell_size):
            for gx in range(self.grid_width):
                canvas.set_pixel(ox + gx, oy + gy, color)
