"""PixelEngine bug fix verification tests.

Tests all 13 bugs identified in the deep scan.
Run: python tests/test_bugs.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import io
import wave
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
#  Bug 1: on_complete() fires exactly once
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 1: Animation.on_complete() fires exactly once")

from pixelengine.animation import Animation, linear
from pixelengine.pobject import PObject

class _CountingAnim(Animation):
    complete_count = 0
    def update(self, alpha): pass
    def on_complete(self): _CountingAnim.complete_count += 1

target = PObject()
anim = _CountingAnim(target)
anim.interpolate(0.5)
anim.interpolate(1.0)
anim.interpolate(1.0)  # Should NOT fire again
anim.interpolate(1.0)  # Should NOT fire again
test("on_complete fires once", _CountingAnim.complete_count == 1,
     f"fired {_CountingAnim.complete_count} times")


# ═══════════════════════════════════════════════════════════
#  Bug 2: Sequence finalizes previous animations
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 2: Sequence finalizes previous sub-animations")

from pixelengine.animation import Sequence, Blink

t1 = PObject()
t2 = PObject()
blink1 = Blink(t1, blinks=2)
blink2 = Blink(t2, blinks=2)
seq = Sequence(blink1, blink2)

# Jump to second animation (alpha > 0.5)
seq.interpolate(0.75)
# First animation should have been finalized with alpha=1.0
test("Previous animation finalized",
     getattr(blink1, '_seq_finalized', False),
     "blink1 was not finalized")
test("First target visible after finalization",
     t1.visible == True,
     f"visible={t1.visible}")


# ═══════════════════════════════════════════════════════════
#  Bug 3-7: FPS propagation
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bugs 3-7: FPS attribute defaults and propagation")

from pixelengine.effects import ParticleEmitter, ScreenFlash
from pixelengine.simulations import Pendulum, Spring, OrbitalSystem, Rope, FluidParticles
from pixelengine.sprite import Sprite
from PIL import Image

# Check defaults
pe = ParticleEmitter()
test("ParticleEmitter has _fps", hasattr(pe, '_fps'), "missing _fps")
test("ParticleEmitter default FPS=24", pe._fps == 24, f"_fps={pe._fps}")

sf = ScreenFlash()
test("ScreenFlash has _fps", hasattr(sf, '_fps'), "missing _fps")

pend = Pendulum()
test("Pendulum has _fps", hasattr(pend, '_fps'), "missing _fps")

spr = Spring()
test("Spring has _fps", hasattr(spr, '_fps'), "missing _fps")

orb = OrbitalSystem()
test("OrbitalSystem has _fps", hasattr(orb, '_fps'), "missing _fps")

rope = Rope()
test("Rope has _fps", hasattr(rope, '_fps'), "missing _fps")

fluid = FluidParticles()
test("FluidParticles has _fps", hasattr(fluid, '_fps'), "missing _fps")

dummy_img = Image.new("RGBA", (8, 8), (255, 0, 0, 255))
sprite = Sprite(dummy_img)
test("Sprite has _fps", hasattr(sprite, '_fps'), "missing _fps")

# FPS propagation via Scene
from pixelengine.scene import Scene
from pixelengine.config import PixelConfig

class _FPSTestScene(Scene):
    def construct(self):
        pe = ParticleEmitter(x=10, y=10)
        self.add(pe)
        self.wait(0.1)  # This triggers _capture_frame which propagates _fps
        self._test_pe = pe

cfg = PixelConfig(fps=30)
scene = _FPSTestScene(config=cfg)
scene._frames = []
scene._current_time = 0
scene._sound_timeline = __import__('pixelengine.sound', fromlist=['SoundTimeline']).SoundTimeline()
scene._last_tw_char_count = {}
scene.construct()
test("Scene propagates FPS to objects",
     scene._test_pe._fps == 30,
     f"_fps={scene._test_pe._fps}")


# ═══════════════════════════════════════════════════════════
#  Bug 8: Vectorized WAV serialization
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 8: Vectorized WAV serialization")

from pixelengine.sound import SoundFX, SoundTimeline, SAMPLE_RATE

# Generate a simple sine wave
t = np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1), endpoint=False)
samples = np.sin(2 * np.pi * 440 * t).astype(np.float32) * 0.5

sfx = SoundFX(samples, "test")
wav_bytes = sfx.to_wav_bytes()
test("WAV bytes non-empty", len(wav_bytes) > 100, f"len={len(wav_bytes)}")

# Verify it's a valid WAV file
buf = io.BytesIO(wav_bytes)
with wave.open(buf, 'rb') as wf:
    test("WAV channels=1", wf.getnchannels() == 1)
    test("WAV samplewidth=3 (24-bit)", wf.getsampwidth() == 3)
    test("WAV framerate", wf.getframerate() == SAMPLE_RATE)
    test("WAV frame count", wf.getnframes() == len(samples),
         f"got {wf.getnframes()} expected {len(samples)}")

# Test SoundTimeline too
timeline = SoundTimeline()
timeline.add(sfx, 0.0)
tl_bytes = timeline.to_wav_bytes(0.1)
test("Timeline WAV non-empty", len(tl_bytes) > 100)


# ═══════════════════════════════════════════════════════════
#  Bug 9-10: VoiceOver imports & file handle
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 9-10: VoiceOver cleanup")

# Check no redundant imports (read the source)
voiceover_path = os.path.join(os.path.dirname(__file__), "..", "pixelengine", "voiceover.py")
with open(voiceover_path) as f:
    src = f.read()
import_count = src.count("import hashlib")
test("hashlib imported only once", import_count == 1, f"found {import_count}")
test("No bare open() in _cache_key",
     'hashlib.sha256(open(' not in src,
     "found unclosed open()")


# ═══════════════════════════════════════════════════════════
#  Bug 11: PhysicsBody live geometry
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 11: PhysicsBody live geometry")

from pixelengine.physics import PhysicsBody
from pixelengine.shapes import Rect, Circle

rect = Rect(20, 30, x=10, y=10)
body = PhysicsBody(rect)
test("Initial width", body._width == 20)
test("Initial height", body._height == 30)

# Simulate animation changing width
rect.width = 40
rect.height = 50
test("Updated width", body._width == 40, f"got {body._width}")
test("Updated height", body._height == 50, f"got {body._height}")

circ = Circle(15, x=50, y=50)
body_c = PhysicsBody(circ)
test("Circle radius", body_c._radius == 15)
circ.radius = 25
test("Updated radius", body_c._radius == 25, f"got {body_c._radius}")


# ═══════════════════════════════════════════════════════════
#  Bug 12: GrowFromPoint sets _base_width
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 12: GrowFromPoint sets _base_width/_base_height")

from pixelengine.construction import GrowFromPoint

rect = Rect(40, 20, x=100, y=60)
anim = GrowFromPoint(rect)
anim.on_start()
test("_base_width set", hasattr(rect, '_base_width') and rect._base_width == 40,
     f"_base_width={getattr(rect, '_base_width', 'MISSING')}")
test("_base_height set", hasattr(rect, '_base_height') and rect._base_height == 20,
     f"_base_height={getattr(rect, '_base_height', 'MISSING')}")


# ═══════════════════════════════════════════════════════════
#  Bug 13: BarChart labels render letters
# ═══════════════════════════════════════════════════════════
print("\n🔍 Bug 13: BarChart labels render alphabetic characters")

from pixelengine.mathobjects import BarChart
from pixelengine.canvas import Canvas

chart = BarChart(
    data=[30, 50, 70],
    labels=["A", "B", "C"],
    x=5, y=5, width=60, height=30,
)
canvas = Canvas(80, 50)

# Render should not crash
try:
    chart.render(canvas)
    test("BarChart renders with letter labels", True)
except Exception as e:
    test("BarChart renders with letter labels", False, str(e))

# Verify pixels were drawn in the label area (below bars)
base_y = 5 + 30  # y + height
has_label_pixels = False
for y in range(base_y + 2, base_y + 10):
    for x in range(80):
        px = canvas._image.getpixel((x, y))
        if px[3] > 0 and px != canvas.background:
            has_label_pixels = True
            break
    if has_label_pixels:
        break
test("Label pixels rendered", has_label_pixels, "no label pixels found")


# ═══════════════════════════════════════════════════════════
#  Summary
# ═══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
if failed > 0:
    print("⚠️  Some tests failed!")
    sys.exit(1)
else:
    print("✅ All tests passed!")
    sys.exit(0)
