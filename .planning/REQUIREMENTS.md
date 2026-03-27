# Requirements: PixelEngine

**Defined:** 2026-03-25
**Core Value:** Users can write a Python script describing an educational animation and render it to a pixel-perfect video file

## v1 Requirements (Complete)

### Core Engine
- [x] **CORE-01**: User can define a scene by subclassing Scene and implementing construct()
- [x] **CORE-02**: User can add and remove pixel objects from a scene using self.add() and self.remove()
- [x] **CORE-03**: User can play animations using self.play(animation, duration=N)
- [x] **CORE-04**: User can hold the current frame using self.wait(seconds)
- [x] **CORE-05**: User can configure canvas resolution, FPS, and upscale factor via PixelConfig

### Rendering
- [x] **REND-01**: Engine renders pixel-perfect frames with no anti-aliasing
- [x] **REND-02**: Engine upscales canvas to output resolution using nearest-neighbor interpolation
- [x] **REND-03**: Engine pipes frames to ffmpeg and produces H.264 MP4 video
- [x] **REND-04**: User can render to 16:9 aspect ratio (YouTube standard)
- [x] **REND-05**: User can render to 9:16 aspect ratio (YouTube Shorts)

### Shapes
- [x] **SHAP-01**: User can create filled and outlined rectangles
- [x] **SHAP-02**: User can create filled and outlined circles (pixel-perfect Bresenham)
- [x] **SHAP-03**: User can create pixel-perfect lines
- [x] **SHAP-04**: User can create triangles and polygons
- [x] **SHAP-05**: User can set color, position, and size of any shape

### Animation
- [x] **ANIM-01**: User can animate objects moving to a position (MoveTo)
- [x] **ANIM-02**: User can animate objects fading in and out (FadeIn, FadeOut)
- [x] **ANIM-03**: User can animate objects scaling up and down (Scale)
- [x] **ANIM-04**: User can choose easing functions (linear, ease_in, ease_out, bounce)
- [x] **ANIM-05**: User can run multiple animations simultaneously (AnimationGroup)

### Text
- [x] **TEXT-01**: User can render pixel text with a built-in bitmap font
- [x] **TEXT-02**: User can set text color, position, and alignment
- [x] **TEXT-03**: User can animate text appearing character by character (TypeWriter)

### Color
- [x] **COLR-01**: User can set colors using hex strings or named colors
- [x] **COLR-02**: User can use built-in retro palettes (PICO-8, GameBoy, NES)
- [x] **COLR-03**: User can define custom color palettes

### Sprites
- [x] **SPRT-01**: User can define sprites inline using ASCII art with color characters
- [x] **SPRT-02**: User can load sprites from PNG image files
- [x] **SPRT-03**: User can create animated sprites from sprite sheets

### Camera
- [x] **CAMR-01**: User can pan the camera to follow action
- [x] **CAMR-02**: User can zoom the camera in and out
- [x] **CAMR-03**: User can make the camera follow a specific object
- [x] **CAMR-04**: User can apply screen shake effect

### Effects
- [x] **EFCT-01**: User can create particle effects with configurable emitters
- [x] **EFCT-02**: User can apply screen transitions between scenes (fade, wipe, pixelate)
- [x] **EFCT-03**: User can apply screen flash and color overlay effects

### Backgrounds
- [x] **BGND-01**: User can create solid color or gradient backgrounds
- [x] **BGND-02**: User can create tilemap-based backgrounds from a grid definition
- [x] **BGND-03**: Backgrounds scroll with camera movement

---

## v2 Requirements

### Manim-like Construction Animations
- [ ] **MANIM-01**: User can animate shapes growing from a single point (GrowFromPoint)
- [ ] **MANIM-02**: User can animate bars/rects extending from an edge (GrowFromEdge)
- [ ] **MANIM-03**: User can animate drawing border then filling (DrawBorderThenFill)
- [ ] **MANIM-04**: User can progressively create/uncreate objects (Create, Uncreate)
- [ ] **MANIM-05**: User can morph one shape into another (MorphTo, ReplacementTransform)
- [ ] **MANIM-06**: User can create and animate math objects (NumberLine, BarChart, Graph, Axes)
- [ ] **MANIM-07**: User can use ValueTracker and updaters for reactive animations

### Texture System
- [ ] **TEX-01**: User can fill shapes with procedural patterns (checkerboard, stripes, dots)
- [ ] **TEX-02**: User can apply dithering between two colors for retro-friendly gradients
- [ ] **TEX-03**: User can use noise-based textures mapped to color palettes
- [ ] **TEX-04**: User can animate textures (scrolling, cycling between frames)
- [ ] **TEX-05**: Textures work with all shape types (Rect, Circle, Triangle, Polygon)

### Pseudo-3D Rendering
- [ ] **3D-01**: User can create wireframe 3D primitives (cube, sphere, pyramid, cylinder)
- [ ] **3D-02**: 3D objects project onto 2D canvas using perspective or isometric projection
- [ ] **3D-03**: User can rotate 3D objects around X, Y, Z axes
- [ ] **3D-04**: User can orbit a 3D camera around objects
- [ ] **3D-05**: User can create custom 3D meshes from vertex/edge data

### Simulation Engine
- [ ] **SIM-01**: User can create physics bodies with mass, velocity, and forces
- [ ] **SIM-02**: Physics world simulates gravity and applies forces each frame
- [ ] **SIM-03**: Collision detection works for AABB and circle-circle
- [ ] **SIM-04**: User can create pre-built simulations (pendulum, spring, orbit)
- [ ] **SIM-05**: User can create rope/chain constraints using Verlet integration
- [ ] **SIM-06**: User can simulate fluid-like particle systems

## Out of Scope

| Feature | Reason |
|---------|--------|
| GUI/visual editor | Code-first philosophy — scope explosion |
| Real-time preview window | Unnecessary complexity for video output workflow |
| Full 3D rendering with lighting/shading | Different domain — pseudo-3D preserves pixel aesthetic |
| Interactive input handling | Not needed for video rendering |
| Plugin/extension system | Premature abstraction |
| Web-based rendering | Python CLI is the target platform |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| MANIM-01..07 | Phase 5 | Pending |
| TEX-01..05 | Phase 6 | Pending |
| 3D-01..05 | Phase 7 | Pending |
| SIM-01..06 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 39 total — all complete ✓
- v2 requirements: 23 total — all pending
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-25*
*Last updated: 2026-03-26 after v2 milestone initialization*
