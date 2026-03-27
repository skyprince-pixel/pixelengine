# Roadmap: PixelEngine

**Created:** 2026-03-25
**Updated:** 2026-03-26
**Phases:** 8 (4 complete, 4 pending)
**Requirements:** 62 mapped

## Phase Overview

| # | Phase | Goal | Requirements | Status |
|---|-------|------|--------------|--------|
| 1 | Core Engine + Shapes + Renderer | End-to-end pipeline: scene → shapes → MP4 | CORE-01..05, REND-01..05, SHAP-01..05, COLR-01..03 | ✓ Complete |
| 2 | Animation System + Text | Smooth animated movements, easing, pixel text | ANIM-01..05, TEXT-01..03 | ✓ Complete |
| 3 | Sprites + Camera + Backgrounds | Sprites, camera movements, backgrounds | SPRT-01..03, CAMR-01..04, BGND-01 | ✓ Complete |
| 4 | Effects + Tilemaps + Polish | Particles, transitions, tilemaps, examples | EFCT-01..03, BGND-02..03 | ✓ Complete |
| 5 | Manim-like Animation System | Construction animations, shape morphing, math objects | MANIM-01..07 | ○ Pending |
| 6 | Texture System | Procedural textures, dithering, texture mapping | TEX-01..05 | ○ Pending |
| 7 | Pseudo-3D Rendering | Wireframe 3D projection, camera orbit, isometric | 3D-01..05 | ○ Pending |
| 8 | Simulation Engine | Physics bodies, collisions, pre-built simulations | SIM-01..06 | ○ Pending |

---

## Phase Details

### Phase 5: Manim-like Animation System
**Goal:** Shapes and graphs that build themselves gradually — bars growing, triangles drawing edges, charts animating — inspired by Manim's construction patterns.

**Requirements:** MANIM-01, MANIM-02, MANIM-03, MANIM-04, MANIM-05, MANIM-06, MANIM-07

**Success Criteria:**
1. User can animate a Rect growing from bottom edge to full height (bar chart effect)
2. Triangle draws its border stroke-by-stroke then fills interior
3. One shape morphs into another shape smoothly
4. NumberLine and BarChart render correctly and animate construction
5. ValueTracker drives reactive animations via updaters

**New Files:** `construction.py`, `transform.py`, `mathobjects.py`
**Modified:** `animation.py`, `__init__.py`

---

### Phase 6: Texture System
**Goal:** Fill shapes with pixel-art-friendly patterns and textures instead of flat colors.

**Requirements:** TEX-01, TEX-02, TEX-03, TEX-04, TEX-05

**Depends on:** Phase 1 (shapes)

**Success Criteria:**
1. Rect, Circle, Triangle, Polygon all support fill_texture
2. Built-in patterns render correctly (checkerboard, stripes, dots, crosshatch)
3. Dithering produces clean retro-style color blending
4. Animated textures scroll/cycle correctly over time

**New Files:** `texture.py`
**Modified:** `pobject.py`, `shapes.py`, `__init__.py`

---

### Phase 7: Pseudo-3D Rendering
**Goal:** Wireframe 3D shapes projected onto the 2D pixel canvas for educational geometry content.

**Requirements:** 3D-01, 3D-02, 3D-03, 3D-04, 3D-05

**Depends on:** Phase 1 (shapes, canvas)

**Success Criteria:**
1. Cube3D renders as wireframe on canvas and rotates smoothly
2. Perspective and isometric projection modes work correctly
3. Camera orbit animation rotates view around 3D objects
4. Custom Mesh3D from vertex/edge data renders correctly

**New Files:** `math3d.py`, `objects3d.py`, `camera3d.py`
**Modified:** `scene.py`, `__init__.py`

---

### Phase 8: Simulation Engine
**Goal:** Physics simulations recorded as video — bouncing balls, pendulums, springs, orbits.

**Requirements:** SIM-01, SIM-02, SIM-03, SIM-04, SIM-05, SIM-06

**Depends on:** Phase 1 (shapes), Phase 2 (animation)

**Success Criteria:**
1. PhysicsBody with gravity produces correct parabolic trajectories
2. AABB and circle collisions detect and respond correctly
3. Pendulum simulation matches expected oscillation
4. Rope/chain simulation hangs and swings realistically

**New Files:** `physics.py`, `collision.py`, `simulations.py`
**Modified:** `scene.py`, `__init__.py`

---

*Roadmap created: 2026-03-25*
*Updated: 2026-03-26 — v2 milestone phases 5-8 added*
