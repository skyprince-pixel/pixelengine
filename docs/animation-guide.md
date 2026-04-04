# Animation Guide

PixelEngine has 50+ animation classes organized into categories. All animations are played via `self.play()`:

```python
self.play(animation, duration=1.0)           # Single animation
self.play(anim1, anim2, duration=1.0)        # Multiple in parallel
```

---

## Core Animations

### Movement

```python
MoveTo(obj, x=200, y=100)         # Absolute position
MoveBy(obj, dx=50, dy=-20)        # Relative offset
```

### Visibility

```python
FadeIn(obj)                        # Fade from transparent to opaque
FadeOut(obj)                       # Fade from opaque to transparent
Blink(obj, blinks=3)              # Blink on/off
```

### Transform

```python
Scale(obj, factor=2.0)            # Scale up/down
Rotate(obj, degrees=90)           # Rotate by degrees
ColorShift(obj, to_color="#00E436")  # Animate color change
```

---

## Easing Functions

Control the acceleration curve of any animation:

```python
self.play(MoveTo(obj, x=200, easing=ease_out), duration=1.0)
```

| Easing | Description |
|--------|-------------|
| `linear` | Constant speed (default) |
| `ease_in` | Start slow, end fast |
| `ease_out` | Start fast, end slow |
| `ease_in_out` | Slow at both ends |
| `bounce` | Bounce at the end |
| `elastic` | Elastic overshoot |
| `back_in`, `back_out`, `back_in_out` | Overshoot pull-back |
| `circ_in`, `circ_out` | Circular curve |
| `expo_in`, `expo_out` | Exponential curve |
| `sine_in`, `sine_out` | Sinusoidal curve |
| `steps(n)` | Quantized to n steps |
| `custom_bezier(x1, y1, x2, y2)` | Custom cubic bezier |

---

## Organic Animations

Physics-inspired animations that feel natural. Each accepts an optional `feel` parameter:

| Feel | Description |
|------|-------------|
| `"snappy"` | Fast, minimal overshoot |
| `"bouncy"` | High overshoot, rubber-ball |
| `"heavy"` | Slow, momentum-driven |
| `"floaty"` | Dreamy, drifting |
| `"elastic"` | Springy wobble |
| `"crisp"` | Sharp transitions |

### One-Shot

```python
OrganicMoveTo(obj, x=200, y=100, feel="bouncy")
OrganicScale(obj, factor=1.5, feel="elastic")
OrganicFadeIn(obj, feel="snappy")
OrganicFadeOut(obj)
OrganicRotate(obj, degrees=45, feel="heavy")
```

### Expressive Motion

```python
SquashAndStretch(obj, squash_factor=0.5)  # Cartoon deformation
Breathe(obj)                               # Gentle pulsing
Sway(obj, amplitude=5)                     # Side-to-side
Float(obj, amplitude=3)                    # Up/down floating
Jitter(obj, amount=2)                      # Micro-vibration
Pulse(obj)                                 # Scale pulsing
Wobble(obj)                                # Rotational wobble
Drift(obj, velocity_x=1)                   # Constant drift
Anticipate(obj)                            # Wind-up before action
Settle(obj)                                # Spring settling
RubberBand(obj)                            # Stretch and snap
```

### Organic Modifiers

Wrap any animation to add organic qualities:

```python
WithNoise(FadeIn(obj), amount=2)           # Add random jitter
WithAnticipation(MoveTo(obj, x=200))       # Wind-up before motion
WithSettle(Scale(obj, 2.0))                # Spring settling after
WithSquashStretch(MoveTo(obj, x=200))      # Deformation during motion
WithFollow(MoveTo(obj, x=200))             # Follow-through overshoot
```

### Continuous Updaters

Attach persistent ambient motion to objects:

```python
obj.add_updater(alive())           # Gentle breathing + micro-drift
obj.add_updater(hover(height=6))   # Smooth up/down oscillation
obj.add_updater(orbit_idle())      # Slow circular drift
obj.add_updater(wind_sway())       # Lateral push with gusts
```

---

## Construction Animations

Manim-style progressive reveal:

```python
Create(obj, direction="right")              # Sweep reveal
Uncreate(obj)                               # Reverse sweep
GrowFromPoint(obj, point_x=100, point_y=50)  # Scale from a point
GrowFromEdge(obj, edge="bottom")            # Extend from edge
DrawBorderThenFill(obj)                     # Trace outline, then fill
GrowArrow(arrow)                            # Arrow grows from start to end
ShowPassingFlash(obj)                       # Flash highlight sweep
RevealCircular(obj)                         # Circular reveal
RevealRect(obj)                             # Rectangular reveal
```

---

## Transform Animations

Morph between shapes:

```python
MorphTo(source, target_shape)               # Interpolate size/color/position
ReplacementTransform(source, target_obj)    # Fade source out, target in
TransformMatchingPoints(source, target)     # Vertex-by-vertex morph
VMorph(source_vector, target_vector)        # SVG path morphing
```

---

## Group Animations

### Parallel

```python
AnimationGroup(FadeIn(a), FadeIn(b), FadeIn(c))  # All at once
```

### Sequential

```python
Sequence(MoveTo(obj, 200, 100), Scale(obj, 2.0))  # One after another
```

### Chaining

```python
MoveTo(obj, 200, 100).then(Scale(obj, 2.0), weight=0.5)  # Fluent chaining
```

### Staggered

```python
Stagger([FadeIn(a), FadeIn(b), FadeIn(c)], lag=0.1)  # Cascading start
```

### Organic Groups

```python
Wave([FadeIn(a), FadeIn(b), FadeIn(c)])                    # Ripple reveal
Cascade([OrganicFadeIn(a), OrganicFadeIn(b)], feel="bouncy")  # Momentum cascade
Swarm([FadeIn(a), FadeIn(b), FadeIn(c)])                   # Scatter from center
```

---

## Animation Modifiers

```python
Delayed(FadeIn(obj), delay=0.3)     # Delay start (fraction of duration)
Reversed(GrowFromPoint(obj))        # Play in reverse
Looped(Rotate(obj, 360), count=3)   # Repeat N times
```

---

## Spring Physics

```python
SpringTo(obj, x=240, y=135, stiffness=120, damping=10)  # Bounce to position
SpringScale(obj, factor=1.5, stiffness=200, damping=8)   # Bouncy scale
```

---

## Path Animation

Define curves and move objects along them:

```python
# Cubic bezier
path = BezierPath(start=(50, 200), control1=(150, 20),
                  control2=(300, 20), end=(400, 200))
self.play(FollowPath(obj, path, rotate_along=True), duration=2.0)

# Circular orbit
orbit = CircularPath(center_x=240, center_y=135, radius=80)
self.play(FollowPath(dot, orbit, loops=2), duration=4.0)

# Quadratic bezier
qpath = QuadraticBezierPath(start=(50, 200), control=(200, 20), end=(350, 200))

# Polyline through points
linear = LinearPath([(50, 200), (150, 50), (250, 200), (350, 50)])
```

---

## Keyframe Timeline

Define property values at specific points in time:

```python
track = KeyframeTrack(obj)
track.add(at=0.0, x=50, y=200, opacity=0.0)
track.add(at=0.3, x=240, y=135, opacity=1.0, easing="ease_out")
track.add(at=0.7, x=240, y=135, scale_x=1.5)
track.add(at=1.0, x=400, y=50, opacity=0.0, easing="ease_in")
self.play(track.build(), duration=3.0)
```

---

## Text Animations

```python
TypeWriter(text)                                        # Classic typewriter
TypeWriterPro(text, cursor=True, cursor_blink_rate=2)  # With blinking cursor
PerCharacter(text, "fade_in", lag=0.05)                # Per-character reveal
PerWord(text, "drop_in", lag=0.1)                      # Per-word reveal
ScrambleReveal(text, charset="ABCXYZ0123")             # Matrix-style decode
```

Effects for `PerCharacter`/`PerWord`: `"fade_in"`, `"drop_in"`, `"scale_in"`, `"slide_up"`

---

## Transitions

Scene transitions between content:

```python
FadeTransition(scene)                           # Fade to black
WipeTransition(scene, direction="left")         # Directional wipe
IrisTransition(scene)                           # Circular iris
DissolveTransition(scene)                       # Pixelated dissolve
PixelateTransition(scene)                       # Block pixelation
SlideTransition(scene)                          # Sliding wipe
GlitchTransition(scene, intensity=0.7)          # Digital glitch
ShatterTransition(scene)                        # Shattering glass
CrossDissolve(source_obj, target_obj)           # Object crossfade
```

---

## Reactive Links

Make objects follow or react to other objects:

```python
# Follow another object's position with delay
shadow.add_updater(Link(player, delay=0.15, properties=["x", "y"]))

# Custom reactive transform
label.add_updater(ReactTo(target, lambda t: {"x": t.x, "y": t.y - 15}))

# Link arrow endpoints to two dots
arrow.add_updater(Link.endpoints(dot_a, dot_b))
```

---

## Animation Lifecycle Hooks

```python
anim = MoveTo(obj, x=200)
anim.on(at=0.5, callback=lambda: print("Halfway!"))

# Override lifecycle methods in custom animations
class MyAnim(Animation):
    def on_start(self):
        pass  # Called when animation begins

    def update(self, alpha):
        pass  # Called each frame with eased alpha [0, 1]

    def on_complete(self):
        pass  # Called when animation finishes
```

---

## Property Animator

Fluent API for simple property animation:

```python
# Animate any PObject property
self.play(obj.animate.move_to(200, 100), duration=1.0)
```
