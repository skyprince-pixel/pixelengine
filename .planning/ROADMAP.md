# Roadmap: PixelEngine

**Created:** 2026-03-25
**Phases:** 4
**Requirements:** 39 mapped

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Core Engine + Shapes + Renderer | Working end-to-end pipeline: write scene → render shapes → get MP4 | CORE-01..05, REND-01..05, SHAP-01..05, COLR-01..03 | 5 |
| 2 | Animation System + Text | Smooth animated movements, easing, and pixel text rendering | ANIM-01..05, TEXT-01..03 | 4 |
| 3 | Sprites + Camera + Backgrounds | Full scene composition with sprites, camera movements, backgrounds | SPRT-01..03, CAMR-01..04, BGND-01 | 4 |
| 4 | Effects + Tilemaps + Polish | Particles, transitions, tilemaps, and production examples | EFCT-01..03, BGND-02..03 | 3 |

---

## Phase Details

### Phase 1: Core Engine + Shapes + Renderer
**Goal:** Working end-to-end pipeline — user writes a Scene script, defines shapes with colors, runs it, gets an MP4 video file with pixel-perfect rendering.

**Requirements:** CORE-01, CORE-02, CORE-03, CORE-04, CORE-05, REND-01, REND-02, REND-03, REND-04, REND-05, SHAP-01, SHAP-02, SHAP-03, SHAP-04, SHAP-05, COLR-01, COLR-02, COLR-03

**Success Criteria:**
1. User can write a Python script with a Scene subclass, add Rect and Circle objects, and render to MP4
2. Output video shows pixel-crisp graphics with no anti-aliasing or blurring
3. Both 16:9 and 9:16 output modes produce correctly proportioned video
4. Colors render correctly using hex strings and retro palette presets
5. `pip install -e .` installs the package with all dependencies

---

### Phase 2: Animation System + Text
**Goal:** Objects can move, fade, scale with smooth easing. Pixel text renders with built-in font. Scene `play()` drives animations frame-by-frame.

**Requirements:** ANIM-01, ANIM-02, ANIM-03, ANIM-04, ANIM-05, TEXT-01, TEXT-02, TEXT-03

**Success Criteria:**
1. User can animate shapes moving across screen with different easing curves
2. FadeIn/FadeOut create smooth opacity transitions
3. AnimationGroup runs multiple animations in parallel within a single play() call
4. PixelText renders readable text at small pixel sizes with configurable color and alignment

---

### Phase 3: Sprites + Camera + Backgrounds
**Goal:** Full scene composition — sprites defined inline or from files, camera follows action, solid-color backgrounds.

**Requirements:** SPRT-01, SPRT-02, SPRT-03, CAMR-01, CAMR-02, CAMR-03, CAMR-04, BGND-01

**Success Criteria:**
1. User can define a sprite using ASCII art with color characters and animate it
2. Camera can pan and zoom smoothly during animation
3. Camera follow mode tracks a moving object
4. Screen shake effect is visually impactful without breaking rendering

---

### Phase 4: Effects + Tilemaps + Polish
**Goal:** Visual polish — particle effects, scene transitions, tilemap backgrounds, and production-ready example scripts.

**Requirements:** EFCT-01, EFCT-02, EFCT-03, BGND-02, BGND-03

**Success Criteria:**
1. Particle emitter creates visually appealing effects (sparks, stars, etc.)
2. Scene transitions (fade, wipe, pixelate) work between different scene sections
3. Tilemap backgrounds render correctly and scroll with camera

---

*Roadmap created: 2026-03-25*
