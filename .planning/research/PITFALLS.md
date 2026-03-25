# Pitfalls Research: Pixel Art Animation Engine

## Critical Pitfalls

### 1. Anti-aliasing Contamination
**Warning signs:** Blurry edges on shapes, smooth gradients where there should be hard pixel edges
**Prevention:** Never use PIL's `ImageDraw` with anti-alias. Use only integer coordinates. Upscale with `Image.NEAREST` (not BILINEAR/BICUBIC). Test every primitive visually.
**Phase:** Phase 1 (Canvas + Shapes)

### 2. Floating-point Position Drift
**Warning signs:** Sprites jittering or landing between pixels during animation
**Prevention:** Always round positions to integers before rendering. Animation system can interpolate with floats, but snap to int at render time.
**Phase:** Phase 2 (Animation System)

### 3. ffmpeg Pipe Encoding Issues
**Warning signs:** Corrupted video, wrong colors, wrong frame rate, hanging process
**Prevention:** Use raw RGB pipe format (`-f rawvideo -pix_fmt rgb24`), flush frequently, handle subprocess lifecycle properly. Always specify input frame size and rate.
**Phase:** Phase 1 (Renderer)

### 4. Performance Death by Per-Pixel Python
**Warning signs:** 60-second video takes 30+ minutes to render
**Prevention:** Use NumPy arrays for bulk operations. PIL `paste()` instead of `putpixel()` loops. Pre-render static backgrounds. Cache sprite images.
**Phase:** Phase 1 (Canvas)

### 5. Scope Creep via Feature Requests
**Warning signs:** Adding GUI, real-time preview, audio, 3D before core works
**Prevention:** Ship working Scene → Video pipeline first. Everything else is polish.
**Phase:** All phases

### 6. Overengineered API Before Usage
**Warning signs:** Complex class hierarchies, multiple inheritance, abstract base classes everywhere
**Prevention:** Write example scripts FIRST, then design API to make those scripts clean. Let usage drive design.
**Phase:** Phase 1 (API Design)
