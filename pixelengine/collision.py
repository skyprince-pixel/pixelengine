"""PixelEngine collision — additional collision utilities.

Provides StaticBody, Bounds, and CollisionCallback helpers
for the physics system.
"""
from pixelengine.pobject import PObject
from pixelengine.physics import PhysicsBody


class StaticBody(PhysicsBody):
    """An immovable collision boundary.

    Static bodies participate in collisions but never move.
    Use for walls, floors, and platforms.

    Usage::

        floor = Rect(256, 5, x=0, y=139, color="#5F574F")
        floor_body = StaticBody(floor)
        physics.add_body(floor_body)
    """

    def __init__(self, pobject: PObject, restitution: float = 0.8):
        super().__init__(
            pobject, mass=999999, vx=0, vy=0,
            restitution=restitution, is_static=True,
        )


class Bounds:
    """Keep all physics bodies within rectangular bounds.

    Convenience wrapper — just sets PhysicsWorld.bounds.

    Usage::

        bounds = Bounds(0, 0, 256, 144)
        physics.bounds = bounds.as_tuple()
    """

    def __init__(self, x_min: int = 0, y_min: int = 0,
                 x_max: int = 256, y_max: int = 144):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def as_tuple(self) -> tuple:
        return (self.x_min, self.y_min, self.x_max, self.y_max)


class CollisionCallback:
    """Register a callback for when two specific bodies collide.

    Usage::

        def on_hit(a, b):
            scene.play_sound(SoundFX.coin())

        cb = CollisionCallback(ball_body, wall_body, on_hit)
        physics.add_collision_callback(cb.check)
    """

    def __init__(self, body_a: PhysicsBody = None,
                 body_b: PhysicsBody = None,
                 on_collide=None):
        self.body_a = body_a
        self.body_b = body_b
        self.on_collide = on_collide

    def check(self, a: PhysicsBody, b: PhysicsBody):
        """Check if this collision matches and fire callback."""
        if self.on_collide is None:
            return
        if self.body_a is None and self.body_b is None:
            # Match any collision
            self.on_collide(a, b)
            return
        if ((a is self.body_a and b is self.body_b) or
            (a is self.body_b and b is self.body_a)):
            self.on_collide(a, b)
