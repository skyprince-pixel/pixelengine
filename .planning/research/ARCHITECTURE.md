# Architecture Research: Pixel Art Animation Engine

## Component Overview

```
User Script (MyScene) 
    → Scene Engine (orchestrator)
        → PObject Registry (what's on screen)
        → Animation System (what's changing)
        → Camera (viewport transform)
        → Canvas (pixel rendering surface)
            → Frame Buffer (PIL Images)
                → Renderer (ffmpeg video output)
```

## Major Components

### 1. Scene Engine (Orchestrator)
- Manages the lifecycle: setup → construct → teardown
- Processes `play()` calls: advances time, ticks animations, captures frames
- Processes `wait()` calls: holds current state for N seconds worth of frames
- Owns the timeline and frame clock

### 2. PObject System (Scene Graph)
- Base `PObject` class: position, size, opacity, z_index, color, visible
- Subclasses: `Sprite`, `Rect`, `Circle`, `Line`, `Triangle`, `Polygon`, `PixelText`, `TileMap`
- Scene maintains ordered list of PObjects, sorted by z_index
- Each PObject knows how to render itself to a canvas region

### 3. Animation System
- `Animation` base: target PObject, duration, easing function
- `interpolate(alpha)` pattern — alpha goes 0→1 over duration
- Concrete animations: `MoveTo`, `MoveBy`, `FadeIn`, `FadeOut`, `Scale`, `Rotate`, `Blink`, `ColorShift`
- `AnimationGroup` for parallel, `Sequence` for serial
- Easing library: linear, ease_in, ease_out, ease_in_out, bounce, elastic

### 4. Camera
- Virtual viewport with position, zoom level
- Transforms PObject world coordinates to screen coordinates
- `pan()`, `zoom()`, `follow()`, `shake()`
- Smooth interpolation between camera states

### 5. Canvas (Rendering Surface)
- Low-res PIL Image (e.g., 256×144 for 16:9)
- Per-frame compositing: clear → draw background → draw PObjects (z-sorted) → apply effects
- No anti-aliasing anywhere — nearest-neighbor only
- Supports transparency via RGBA mode

### 6. Renderer (Video Output)
- Collects frames from canvas
- Upscales each frame (nearest-neighbor) to output resolution
- Pipes to ffmpeg for H.264 MP4 encoding
- Supports configurable FPS and output path

## Data Flow

```
construct() → play(animation) → animation ticks → PObjects update
    → camera transforms → canvas composites → frame captured
    → all frames piped → ffmpeg → MP4 file
```

## Build Order (Dependencies)

1. **Config + Color** — no dependencies
2. **Canvas** — depends on Config, Color
3. **PObject base** — depends on Canvas (for render)
4. **Shapes** — depends on PObject
5. **Sprite + Text** — depends on PObject
6. **Animation** — depends on PObject
7. **Camera** — depends on Config
8. **Scene** — depends on all above
9. **Renderer** — depends on Scene, Canvas
10. **TileMap, Effects** — depends on PObject, Animation
