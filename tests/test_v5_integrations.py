"""PixelEngine v5 integration verification tests.

Tests all 4 package integrations: NumPy canvas, PyAV, Pymunk, Pydub.
Run: python tests/test_v5_integrations.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

passed = 0
failed = 0

def test(name, condition, msg=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {msg}")
        failed += 1


# ═══════════════════════════════════════════════════════════
#  1. NumPy Canvas Acceleration
# ═══════════════════════════════════════════════════════════
print("\n🔍 1. NumPy Canvas Acceleration")

from pixelengine.canvas import Canvas

c = Canvas(32, 32, "#000000")

# Check internal buffer is numpy
test("Internal buffer is numpy array", isinstance(c._pixels, np.ndarray))
test("Shape is (H, W, 4)", c._pixels.shape == (32, 32, 4))
test("Dtype is uint8", c._pixels.dtype == np.uint8)

# set_pixel works
c.set_pixel(5, 5, (255, 0, 0, 255))
test("set_pixel: red at (5,5)", list(c._pixels[5, 5]) == [255, 0, 0, 255])

# Alpha compositing
c.set_pixel(5, 5, (0, 255, 0, 128))  # Semi-transparent green over red
pixel = c._pixels[5, 5]
test("Alpha blend: green channel present", pixel[1] > 100,
     f"pixel={list(pixel)}")
test("Alpha blend: red channel reduced", pixel[0] < 200,
     f"pixel={list(pixel)}")

# clear()
c.clear()
test("clear(): pixels zeroed", c._pixels[5, 5].sum() == c._bg_array[5, 5].sum())

# get_frame() returns PIL Image
frame = c.get_frame(1)
from PIL import Image
test("get_frame returns PIL Image", isinstance(frame, Image.Image))
test("get_frame correct size", frame.size == (32, 32))

# Upscaled frame
frame_up = c.get_frame(4)
test("Upscale 4x frame size", frame_up.size == (128, 128))

# blit() with numpy composite
c.clear()
overlay = Image.new("RGBA", (10, 10), (0, 0, 255, 200))
c.blit(overlay, 2, 2)
test("blit: blue pixels written", c._pixels[3, 3, 2] > 150,
     f"blue={c._pixels[3, 3, 2]}")

# _pil_image property
pil = c._pil_image
test("_pil_image is a PIL Image", isinstance(pil, Image.Image))


# ═══════════════════════════════════════════════════════════
#  2. PyAV Renderer
# ═══════════════════════════════════════════════════════════
print("\n🔍 2. PyAV Renderer")

from pixelengine.renderer import Renderer, HAS_PYAV
from pixelengine.config import PixelConfig

test("PyAV is available", HAS_PYAV)

if HAS_PYAV:
    import tempfile
    cfg = PixelConfig()
    renderer = Renderer(cfg)

    # Create test frames
    frames = []
    for i in range(24):  # 1 second at 24fps
        img = Image.new("RGB", (cfg.output_width, cfg.output_height), (i*10, 0, 0))
        frames.append(img)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as f:
        renderer.encode(frames, f.name)
        size = os.path.getsize(f.name)
        test("PyAV encoded video exists", size > 0, f"size={size}")
        test("PyAV encoded video >100 bytes", size > 100, f"size={size}")
else:
    print("  ⚠️ PyAV not installed, skipping encoder test")


# ═══════════════════════════════════════════════════════════
#  3. Pymunk Physics
# ═══════════════════════════════════════════════════════════
print("\n🔍 3. Pymunk Physics")

from pixelengine.physics import PhysicsBody, PhysicsWorld, HAS_PYMUNK

test("Pymunk is available", HAS_PYMUNK)

if HAS_PYMUNK:
    from pixelengine.shapes import Circle, Rect

    # Create world
    world = PhysicsWorld(gravity_x=0, gravity_y=100)
    test("PhysicsWorld uses Pymunk", world._use_pymunk)
    test("Pymunk space created", world._space is not None)

    # Add a circle body
    ball = Circle(5, x=100, y=10, color="#FF004D")
    body = PhysicsBody(ball, mass=1.0, restitution=0.8)
    world.add_body(body)
    test("Body added to world", len(world.bodies) == 1)
    test("Pymunk body created", body._pm_body is not None)
    test("Pymunk shape created", body._pm_shape is not None)

    # Step simulation
    initial_y = ball.y
    for _ in range(24):  # 1 second
        world.step(1/24)
    test("Ball fell due to gravity", ball.y > initial_y,
         f"initial_y={initial_y}, current_y={ball.y}")

    # Add bounds — Pymunk uses wall segments
    world2 = PhysicsWorld(gravity_y=200, bounds=(0, 0, 256, 144))
    ball2 = Circle(3, x=128, y=10, color="#00E436")
    body2 = PhysicsBody(ball2, mass=1.0, restitution=0.5)
    world2.add_body(body2)
    for _ in range(48):  # 2 seconds
        world2.step(1/24)
    # With Pymunk, ball should have interacted with wall segments
    # The ball falls due to gravity and should bounce off the bottom wall
    test("Ball fell under gravity (Pymunk)", ball2.y > 10,
         f"y={ball2.y}")

    # Collision callback
    collisions = []
    def on_collide(a, b):
        collisions.append((a, b))
    world2.add_collision_callback(on_collide)
    test("Collision callback registered", len(world2._callbacks) == 1)

    # Remove body
    world.remove_body(body)
    test("Body removed from world", len(world.bodies) == 0)
else:
    print("  ⚠️ Pymunk not installed, skipping physics test")

# Test Euler fallback still works
from pixelengine.pobject import PObject

world_euler = PhysicsWorld.__new__(PhysicsWorld)
world_euler.gravity_x = 0
world_euler.gravity_y = 100
world_euler.bodies = []
world_euler.bounds = None
world_euler._callbacks = []
world_euler._use_pymunk = False  # Force fallback
world_euler._space = None

obj_e = PObject(x=50, y=10)
body_e = PhysicsBody(obj_e, mass=1.0)
world_euler.bodies.append(body_e)
initial_y_e = obj_e.y
world_euler._step_euler(1/24)
test("Euler fallback: ball moved", obj_e.y > initial_y_e,
     f"y={obj_e.y}")


# ═══════════════════════════════════════════════════════════
#  4. Pydub Audio Mixing
# ═══════════════════════════════════════════════════════════
print("\n🔍 4. Pydub Audio Mixing")

from pixelengine.sound import SoundFX, SoundTimeline, HAS_PYDUB, HAS_PYAV as SOUND_HAS_PYAV

test("Pydub is available", HAS_PYDUB)

# Create timeline
tl = SoundTimeline()
tl.add(SoundFX.coin(), at=0.0)
tl.add(SoundFX.typing_key(), at=0.5)
tl.add(SoundFX.explosion(), at=1.0)

if HAS_PYDUB:
    mixed = tl._mix_pydub(2.0)
    test("Pydub mix: non-empty result", len(mixed) > 0)
    test("Pydub mix: float32 array", mixed.dtype == np.float32)
    test("Pydub mix: values in [-1,1]", np.max(np.abs(mixed)) <= 1.01,
         f"max={np.max(np.abs(mixed))}")

# Numpy fallback always works
mixed_np = tl._mix_numpy(2.0)
test("NumPy mix: non-empty result", len(mixed_np) > 0)
test("NumPy mix: float32 array", mixed_np.dtype == np.float32)

# Full mix() call dispatches correctly
mixed_full = tl.mix(2.0)
test("mix() returns data", len(mixed_full) > 0)

# WAV export
wav_bytes = tl.to_wav_bytes(2.0)
test("WAV export: has data", len(wav_bytes) > 44)  # WAV header is 44 bytes

# PyAV mux function exists
test("Sound module has PyAV support", SOUND_HAS_PYAV == HAS_PYAV)


# ═══════════════════════════════════════════════════════════
#  5. Import & Version
# ═══════════════════════════════════════════════════════════
print("\n🔍 5. Import & Version Check")

import pixelengine
test("Version is 0.5.0", pixelengine.__version__ == "0.5.0",
     f"version={pixelengine.__version__}")

# All v4 symbols still accessible
v4_symbols = [
    "Stagger", "Delayed", "Reversed", "Looped",
    "SpringTo", "SpringScale",
    "BezierPath", "FollowPath",
    "KeyframeTrack", "KeyframeAnimation",
    "PerCharacter", "ScrambleReveal",
    "PixelateTransition", "CrossDissolve",
    "ParticleBurst", "Link", "ReactTo",
]
for sym in v4_symbols:
    test(f"v4 export {sym}", hasattr(pixelengine, sym))


# ═══════════════════════════════════════════════════════════
#  Summary
# ═══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
if failed > 0:
    print("⚠️  Some tests failed!")
    sys.exit(1)
else:
    print("✅ All v5 integration tests passed!")
    sys.exit(0)
