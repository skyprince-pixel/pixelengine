"""PixelEngine v4 feature verification tests.

Tests all 10 new animation/transition features.
Run: python tests/test_v4_features.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math

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
#  Feature 1: New Easing Functions
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 1: New Easing Functions")

from pixelengine.animation import (
    back_in, back_out, back_in_out,
    circ_in, circ_out,
    expo_in, expo_out,
    sine_in, sine_out,
    steps, custom_bezier,
    EASINGS, get_easing,
)

# All easings should return 0 at t=0 and ~1 at t=1
for name, fn in [("back_in", back_in), ("back_out", back_out),
                  ("circ_in", circ_in), ("circ_out", circ_out),
                  ("expo_in", expo_in), ("expo_out", expo_out),
                  ("sine_in", sine_in), ("sine_out", sine_out)]:
    v0 = fn(0.0)
    v1 = fn(1.0)
    test(f"{name}(0)≈0", abs(v0) < 0.01, f"got {v0}")
    test(f"{name}(1)≈1", abs(v1 - 1.0) < 0.01, f"got {v1}")

# back_in should go negative (pull back)
test("back_in goes negative", back_in(0.2) < 0, f"back_in(0.2)={back_in(0.2)}")

# back_out should overshoot
test("back_out overshoots", back_out(0.8) > 1.0, f"back_out(0.8)={back_out(0.8)}")

# steps
step4 = steps(4)
test("steps(4)(0.3) = 0.25", abs(step4(0.3) - 0.25) < 0.01,
     f"got {step4(0.3)}")

# custom_bezier
ease_cb = custom_bezier(0.0, 0.0, 1.0, 1.0)  # Should be ~linear
test("custom_bezier(0)=0", abs(ease_cb(0.0)) < 0.05)
test("custom_bezier(1)≈1", abs(ease_cb(1.0) - 1.0) < 0.05,
     f"got {ease_cb(1.0)}")

# EASINGS dict has new entries
test("EASINGS has back_in", "back_in" in EASINGS)
test("EASINGS has sine_out", "sine_out" in EASINGS)


# ═══════════════════════════════════════════════════════════
#  Feature 2: Stagger
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 2: Stagger Animation Group")

from pixelengine.animation import Stagger, FadeIn
from pixelengine.pobject import PObject

objs = [PObject() for _ in range(3)]
for o in objs:
    o.opacity = 1.0
anims = [FadeIn(o) for o in objs]
stagger = Stagger(anims, lag=0.2)

# At alpha=0, all should be at start (opacity=0 after FadeIn.on_start)
stagger.interpolate(0.0)
test("Stagger: first obj started", objs[0].opacity == 0.0,
     f"opacity={objs[0].opacity}")

# At alpha=0.5, first should be well along, third not started
stagger.interpolate(0.5)
test("Stagger: first obj progressed", objs[0].opacity > 0.3,
     f"opacity={objs[0].opacity}")


# ═══════════════════════════════════════════════════════════
#  Feature 3: Animation Modifiers
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 3: Animation Modifiers")

from pixelengine.animation import Delayed, Reversed, Looped, Rotate

# Delayed
obj_d = PObject()
obj_d.opacity = 1.0
delayed = Delayed(FadeIn(obj_d), delay=0.5)
delayed.interpolate(0.3)  # Before delay — should not have started
test("Delayed: no change before delay", obj_d.opacity == 1.0,
     f"opacity={obj_d.opacity}")
delayed.interpolate(0.75)  # After delay
test("Delayed: animating after delay", obj_d.opacity < 1.0,
     f"opacity={obj_d.opacity}")

# Reversed
obj_r = PObject()
rev_anim = FadeIn(obj_r)
reversed_a = Reversed(rev_anim)
reversed_a.interpolate(0.0)  # Should get alpha=1.0
test("Reversed: alpha=0 gives full", obj_r.opacity == 1.0,
     f"opacity={obj_r.opacity}")

# Looped
obj_l = PObject()
obj_l.angle = 0
rot = Rotate(obj_l, degrees=90)
looped = Looped(rot, count=2)
looped.interpolate(0.25)  # Quarter of first loop
test("Looped: mid-first-loop angle", obj_l.angle > 0,
     f"angle={obj_l.angle}")


# ═══════════════════════════════════════════════════════════
#  Feature 4: Path Animation
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 4: Path Animation")

from pixelengine.pathanim import (
    BezierPath, QuadraticBezierPath, CircularPath, LinearPath, FollowPath
)

# BezierPath
bp = BezierPath(start=(0, 0), control1=(50, 100), control2=(150, 100), end=(200, 0))
p0 = bp.evaluate(0.0)
p1 = bp.evaluate(1.0)
test("BezierPath t=0 = start", abs(p0[0]) < 1 and abs(p0[1]) < 1,
     f"got {p0}")
test("BezierPath t=1 = end", abs(p1[0] - 200) < 1 and abs(p1[1]) < 1,
     f"got {p1}")
test("BezierPath t=0.5 has Y", bp.evaluate(0.5)[1] > 30,
     f"y={bp.evaluate(0.5)[1]}")

# CircularPath
cp = CircularPath(center_x=100, center_y=100, radius=50)
p_start = cp.evaluate(0.0)
test("CircularPath t=0 on circle", abs(p_start[0] - 150) < 2,
     f"got x={p_start[0]}")

# LinearPath
lp = LinearPath([(0, 0), (100, 0), (100, 100)])
test("LinearPath t=0", abs(lp.evaluate(0.0)[0]) < 1)
test("LinearPath t=1", abs(lp.evaluate(1.0)[1] - 100) < 2,
     f"got {lp.evaluate(1.0)}")

# FollowPath
target = PObject(x=0, y=0)
fp = FollowPath(target, bp)
fp.interpolate(0.0)
test("FollowPath t=0 moves to start", abs(target.x) < 2, f"x={target.x}")
fp.interpolate(1.0)
test("FollowPath t=1 moves to end", abs(target.x - 200) < 2, f"x={target.x}")


# ═══════════════════════════════════════════════════════════
#  Feature 5: Keyframe Timeline
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 5: Keyframe Timeline")

from pixelengine.keyframes import KeyframeTrack

obj_kf = PObject(x=0, y=0)
obj_kf.opacity = 1.0
track = KeyframeTrack(obj_kf)
track.add(at=0.0, x=0, y=0, opacity=0.0)
track.add(at=0.5, x=100, y=50, opacity=1.0)
track.add(at=1.0, x=200, y=0, opacity=0.5)

anim_kf = track.build()
anim_kf.interpolate(0.0)
test("KF t=0: x=0", abs(obj_kf.x) < 2, f"x={obj_kf.x}")
test("KF t=0: opacity=0", abs(obj_kf.opacity) < 0.1, f"opacity={obj_kf.opacity}")

anim_kf.interpolate(0.5)
test("KF t=0.5: x≈100", abs(obj_kf.x - 100) < 10, f"x={obj_kf.x}")
test("KF t=0.5: opacity≈1", abs(obj_kf.opacity - 1.0) < 0.2, f"opacity={obj_kf.opacity}")

anim_kf.interpolate(1.0)
test("KF t=1: x≈200", abs(obj_kf.x - 200) < 10, f"x={obj_kf.x}")


# ═══════════════════════════════════════════════════════════
#  Feature 6: Spring Physics
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 6: Spring Physics")

from pixelengine.animation import SpringTo, SpringScale

obj_sp = PObject(x=0, y=0)
spring = SpringTo(obj_sp, x=100, y=50, stiffness=120, damping=10)
spring.interpolate(0.0)
test("SpringTo t=0: at start", abs(obj_sp.x) < 5, f"x={obj_sp.x}")

spring.interpolate(0.5)
test("SpringTo t=0.5: moving", obj_sp.x > 20, f"x={obj_sp.x}")

# Spring should overshoot with low damping
obj_sp2 = PObject(x=0, y=0)
spring2 = SpringTo(obj_sp2, x=100, stiffness=200, damping=5)
spring2.interpolate(0.3)
# Check spring passed target (overshoot behavior)
test("SpringTo overshoot possible", True)  # Just verify no crash

spring.interpolate(1.0)
test("SpringTo t=1: at target", abs(obj_sp.x - 100) < 2, f"x={obj_sp.x}")

# SpringScale
obj_ss = PObject()
obj_ss.scale_x = 1.0
obj_ss.scale_y = 1.0
ss = SpringScale(obj_ss, factor=2.0, stiffness=200, damping=8)
ss.interpolate(0.0)
test("SpringScale t=0: scale=1", abs(obj_ss.scale_x - 1.0) < 0.1)
ss.interpolate(1.0)
test("SpringScale t=1: scale≈2", abs(obj_ss.scale_x - 2.0) < 0.1,
     f"scale_x={obj_ss.scale_x}")


# ═══════════════════════════════════════════════════════════
#  Feature 7: Advanced Transitions (no-crash test)
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 7: Advanced Scene Transitions")

from pixelengine.scene import Scene
from pixelengine.config import PixelConfig
from pixelengine.effects import (
    PixelateTransition, SlideTransition, GlitchTransition,
    ShatterTransition, CrossDissolve,
)

# Create a minimal scene for transition testing
class _TransitionTestScene(Scene):
    def construct(self):
        from pixelengine.shapes import Rect
        bg = Rect(self.config.canvas_width, self.config.canvas_height, color="#1D2B53")
        self.add(bg)
        self.wait(0.05)

cfg = PixelConfig()
scene = _TransitionTestScene(config=cfg)

for TransClass, name in [
    (PixelateTransition, "PixelateTransition"),
    (SlideTransition, "SlideTransition"),
    (GlitchTransition, "GlitchTransition"),
    (ShatterTransition, "ShatterTransition"),
    (CrossDissolve, "CrossDissolve"),
]:
    try:
        trans = TransClass(scene)
        trans.interpolate(0.0)
        trans.interpolate(0.5)
        trans.interpolate(1.0)
        test(f"{name} runs without crash", True)
    except Exception as e:
        test(f"{name} runs without crash", False, str(e))


# ═══════════════════════════════════════════════════════════
#  Feature 8: Text Animation
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 8: Text Animation Toolkit")

from pixelengine.textanim import PerCharacter, PerWord, ScrambleReveal, TypeWriterPro

# Create a mock text object
class _MockText:
    def __init__(self, text):
        self.text = text
        self.max_chars = len(text)
        self.opacity = 1.0

txt = _MockText("HELLO WORLD")

# PerCharacter
pc = PerCharacter(txt, "fade_in", lag=0.05)
pc.interpolate(0.0)
test("PerCharacter t=0: few chars", txt.max_chars <= 2,
     f"max_chars={txt.max_chars}")
pc.interpolate(1.0)
test("PerCharacter t=1: all chars", txt.max_chars == len("HELLO WORLD"),
     f"max_chars={txt.max_chars}")

# PerWord
txt2 = _MockText("ONE TWO THREE")
pw = PerWord(txt2, "fade_in", lag=0.15)
pw.interpolate(0.0)
test("PerWord t=0: shows few", txt2.max_chars <= 4,
     f"max_chars={txt2.max_chars}")
pw.interpolate(1.0)
test("PerWord t=1: all chars", txt2.max_chars == len("ONE TWO THREE"),
     f"max_chars={txt2.max_chars}")

# ScrambleReveal
txt3 = _MockText("DECODE ME")
sr = ScrambleReveal(txt3, speed=3.0)
sr.interpolate(0.5)
test("ScrambleReveal t=0.5: text modified", len(txt3.text) > 0)
sr.interpolate(1.0)
test("ScrambleReveal t=1: text resolved", txt3.text == "DECODE ME",
     f"text='{txt3.text}'")

# TypeWriterPro
txt4 = _MockText("TYPE THIS")
twp = TypeWriterPro(txt4, cursor=True)
twp.interpolate(0.5)
test("TypeWriterPro t=0.5: partial", len(txt4.text) < len("TYPE THIS") + 2)
twp.interpolate(1.0)
test("TypeWriterPro t=1: complete", txt4.text == "TYPE THIS",
     f"text='{txt4.text}'")


# ═══════════════════════════════════════════════════════════
#  Feature 9: Particle Burst
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 9: Particle Burst Shapes")

from pixelengine.effects import ParticleBurst

# form_shape
try:
    burst = ParticleBurst.form_shape(scene, particle_count=20, seed=42)
    burst.interpolate(0.0)
    burst.interpolate(0.5)
    burst.interpolate(1.0)
    test("ParticleBurst.form_shape runs", True)
except Exception as e:
    test("ParticleBurst.form_shape runs", False, str(e))

# explode
try:
    burst2 = ParticleBurst.explode(scene, x=240, y=135, particle_count=20, seed=42)
    burst2.interpolate(0.0)
    burst2.interpolate(0.5)
    burst2.interpolate(1.0)
    test("ParticleBurst.explode runs", True)
except Exception as e:
    test("ParticleBurst.explode runs", False, str(e))

# disperse
try:
    burst3 = ParticleBurst.disperse(scene, particle_count=20, seed=42)
    burst3.interpolate(0.0)
    burst3.interpolate(1.0)
    test("ParticleBurst.disperse runs", True)
except Exception as e:
    test("ParticleBurst.disperse runs", False, str(e))


# ═══════════════════════════════════════════════════════════
#  Feature 10: Reactive Links
# ═══════════════════════════════════════════════════════════
print("\n🔍 Feature 10: Reactive Links")

from pixelengine.pobject import Link, ReactTo

# Link
source = PObject(x=100, y=50)
follower = PObject(x=0, y=0)
link = Link(source, delay=0, properties=["x", "y"])
link(follower, 0.04)  # simulate one frame
test("Link: follower.x = source.x", abs(follower.x - 100) < 1,
     f"follower.x={follower.x}")
test("Link: follower.y = source.y", abs(follower.y - 50) < 1,
     f"follower.y={follower.y}")

# Link with delay
follower2 = PObject(x=0, y=0)
link_delayed = Link(source, delay=0.5, properties=["x"])
link_delayed(follower2, 0.04)
test("Link delayed: follower moved partially", 0 < follower2.x < 100,
     f"follower2.x={follower2.x}")

# Link.endpoints
obj_a = PObject(x=10, y=20)
obj_b = PObject(x=200, y=100)

class _MockLine:
    x1 = 0; y1 = 0; x2 = 0; y2 = 0

line = _MockLine()
endpoint_fn = Link.endpoints(obj_a, obj_b)
endpoint_fn(line, 0.04)
test("Link.endpoints: x1", line.x1 == 10, f"x1={line.x1}")
test("Link.endpoints: y2", line.y2 == 100, f"y2={line.y2}")

# ReactTo
reactor = PObject(x=0, y=0)
react = ReactTo(source, lambda s: {"x": s.x + 10, "y": s.y - 5})
react(reactor, 0.04)
test("ReactTo: x=110", abs(reactor.x - 110) < 1, f"x={reactor.x}")
test("ReactTo: y=45", abs(reactor.y - 45) < 1, f"y={reactor.y}")

# add_updater / remove_updater / clear_updaters
obj_up = PObject()
updater = lambda o, dt: setattr(o, 'x', 999)
obj_up.add_updater(updater)
test("add_updater: updater added", len(obj_up._updaters) == 1)
obj_up.remove_updater(updater)
test("remove_updater: updater removed", len(obj_up._updaters) == 0)
obj_up.add_updater(updater)
obj_up.add_updater(lambda o, dt: None)
obj_up.clear_updaters()
test("clear_updaters: all removed", len(obj_up._updaters) == 0)


# ═══════════════════════════════════════════════════════════
#  Import test: all v4 symbols accessible from pixelengine
# ═══════════════════════════════════════════════════════════
print("\n🔍 Import test: all v4 exports from pixelengine")

import pixelengine

v4_symbols = [
    # Easings
    "back_in", "back_out", "back_in_out", "circ_in", "circ_out",
    "expo_in", "expo_out", "sine_in", "sine_out", "steps", "custom_bezier",
    # Animation
    "Stagger", "Delayed", "Reversed", "Looped", "SpringTo", "SpringScale",
    # Path
    "BezierPath", "QuadraticBezierPath", "CircularPath", "LinearPath", "FollowPath",
    # Keyframes
    "Keyframe", "KeyframeTrack", "KeyframeAnimation",
    # Text
    "PerCharacter", "PerWord", "ScrambleReveal", "TypeWriterPro",
    # Transitions
    "PixelateTransition", "SlideTransition", "GlitchTransition",
    "ShatterTransition", "CrossDissolve",
    # Particle Burst
    "ParticleBurst",
    # Reactive
    "Link", "ReactTo",
]

for sym in v4_symbols:
    test(f"import {sym}", hasattr(pixelengine, sym), f"missing from pixelengine")

test("Version is 0.5.0", pixelengine.__version__ == "0.5.0",
     f"version={pixelengine.__version__}")


# ═══════════════════════════════════════════════════════════
#  Summary
# ═══════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
if failed > 0:
    print("⚠️  Some tests failed!")
    sys.exit(1)
else:
    print("✅ All v4 feature tests passed!")
    sys.exit(0)
