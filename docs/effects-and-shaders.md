# Effects & Shaders

## Particle System

### ParticleEmitter

Continuous particle generation with physics:

```python
emitter = ParticleEmitter(
    x=240, y=200,
    colors=["#FF004D", "#FFA300", "#FFEC27"],
    speed=2.0,           # Particle velocity
    spread=60,           # Emission cone angle (degrees)
    direction=270,       # Emission direction (270 = up)
    lifetime=1.0,        # Particle lifetime (seconds)
    rate=10,             # Particles per frame
    gravity=50,          # Downward pull
    wind_x=0, wind_y=0,  # Wind forces
    friction=1.0,        # Velocity damping
    size=1,              # Particle size
    size_decay=False,    # Shrink over lifetime
    burst=0,             # Initial burst count
    max_particles=200,
    fade=True,           # Fade out over lifetime
    spawn_radius=2.0     # Spawn area radius
)
self.add(emitter)
self.wait(3.0)
emitter.stop()
```

### Presets

```python
ParticleEmitter.fire(x=240, y=200, intensity=1.0)     # Flames
ParticleEmitter.smoke(x=240, y=200, intensity=1.0)    # Gray smoke
ParticleEmitter.sparks(x=240, y=200, intensity=1.0)   # Electric sparks
ParticleEmitter.confetti(canvas_width=480, intensity=1.0)  # Falling confetti
ParticleEmitter.snow(canvas_width=480, intensity=1.0)  # Snowfall
ParticleEmitter.rain(canvas_width=480, intensity=1.0)  # Rain
ParticleEmitter.bubbles(x=240, y=200, intensity=1.0)  # Rising bubbles
```

### ParticleBurst

One-shot particle explosions:

```python
self.play(ParticleBurst.explode(scene, x=240, y=135), duration=1.0)
self.play(ParticleBurst.impact(scene, x=100, y=200), duration=0.5)
self.play(ParticleBurst.sparkle(scene, x=200, y=100), duration=0.8)
```

---

## Scene Transitions

Transitions animate between scenes or content sections:

```python
# Fade to black then back
self.play(FadeTransition(self), duration=1.0)

# Directional wipe
self.play(WipeTransition(self, direction="left"), duration=0.5)
# Directions: "left", "right", "up", "down"

# Circular iris reveal/close
self.play(IrisTransition(self), duration=0.8)

# Pixelated dissolve
self.play(DissolveTransition(self), duration=1.0)

# Block pixelation
self.play(PixelateTransition(self), duration=0.5)

# Sliding wipe
self.play(SlideTransition(self), duration=0.5)

# Digital glitch
self.play(GlitchTransition(self, intensity=0.7), duration=0.5)

# Shattering glass
self.play(ShatterTransition(self), duration=0.8)

# Crossfade between two objects
self.play(CrossDissolve(old_obj, new_obj), duration=1.0)
```

---

## Camera Post-Processing (CameraFX)

Applied as a pipeline after rendering each frame:

```python
# Add effects
scene.add_camera_fx(Vignette(intensity=0.5))
scene.add_camera_fx(ChromaticAberration(offset=2.0))
scene.add_camera_fx(DepthOfField(blur_radius=5.0, blur_strength=1.0))
scene.add_camera_fx(FilmGrain(intensity=0.3))
scene.add_camera_fx(Letterbox(bar_height=20, color="#000000"))

# Remove effects
scene.remove_camera_fx(vignette)
```

### Vignette
Darkened edges for cinematic focus.
- `intensity`: 0.0 (none) to 1.0 (heavy)

### ChromaticAberration
RGB channel separation (lens aberration effect).
- `offset`: pixel offset between channels

### DepthOfField
Blur based on distance from camera focus point.
- `blur_radius`: size of blur kernel
- `blur_strength`: intensity of blur

### FilmGrain
Random noise overlay for film-like texture.
- `intensity`: grain visibility

### Letterbox
Cinematic black bars (top/bottom).
- `bar_height`: height of each bar
- `color`: bar color

---

## Per-Pixel Shaders

Applied via the camera FX pipeline:

### CRTScanlines
Retro CRT monitor effect with dark scan lines.
```python
CRTScanlines(line_spacing=2, darkness=0.3)
```

### Ripple
Water ripple distortion emanating from a center point.
```python
Ripple(center_x=240, center_y=135, wavelength=20, amplitude=5, speed=2.0)
```

### HeatShimmer
Vertical wavy distortion simulating rising heat.
```python
HeatShimmer(amplitude=2, frequency=0.1, speed=1.0)
```

### Pixelate
Dynamic mosaic pixelation effect.
```python
Pixelate(block_size=4)
```

### ColorGrade
Color tinting and grading.
```python
ColorGrade(preset="sepia")
ColorGrade(tint="#FFD4A0", strength=0.5)
```
Presets: `"sepia"`, `"cool"`, `"warm"`, `"noir"`, `"cyberpunk"`

---

## Lighting

### Light Types

```python
# Uniform ambient fill
scene.add_light(AmbientLight(intensity=0.5, color="#FFFFFF"))

# Point light with falloff
light = PointLight(x=240, y=135, radius=100, intensity=1.0, color="#FFEC27")
scene.add_light(light)
scene.add(light)  # Also add to scene so it can be animated

# Directional light (sunlight)
scene.add_light(DirectionalLight(angle_deg=45, intensity=1.0, color="#FFFFFF"))
```

### Object Lighting Properties

```python
obj.casts_shadow = True        # Object casts shadows
obj.receives_light = True      # Lighting affects this object
obj.shadow_opacity = 0.4       # Shadow darkness (0.0 to 1.0)
```

---

## Visual Helpers

### Trail
Motion trail behind a moving object:
```python
trail = Trail(target_object)
self.add(trail)
# Trail automatically renders as the target moves
```

### ScreenFlash
Brief screen flash:
```python
self.play(ScreenFlash(color="#FFFFFF"), duration=0.2)
```

### Outline
Highlight border around an object:
```python
outline = Outline(target_object, color="#FFEC27", thickness=1)
self.add(outline)
```

### Grid
Grid overlay for alignment or graph paper effect:
```python
grid = Grid(width=480, height=270, spacing=16, color="#333333")
self.add(grid)
```

---

## Textures

Apply pattern fills to any shape:

```python
obj.fill_texture = PatternTexture("checkerboard", color1="#FFF", color2="#000", cell_size=4)
obj.fill_gradient = LinearGradient("#FF004D", "#29ADFF", direction="vertical")
obj.fill_gradient = RadialGradient("#FFEC27", "#000000")
```

### Available Patterns
`"checkerboard"`, `"stripes_h"`, `"stripes_v"`, `"diagonal"`, `"dots"`, `"crosshatch"`, `"brick"`, `"herringbone"`

### Texture Types
- `PatternTexture` -- repeating geometric patterns
- `DitherTexture` -- ordered dithering between two colors
- `NoiseTexture` -- hash-based random noise
- `GradientTexture` -- linear gradient fill
- `AnimatedTexture` -- frame-based texture animation
- `ScrollingTexture` -- continuously moving texture
