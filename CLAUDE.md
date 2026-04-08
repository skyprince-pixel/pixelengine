# PixelEngine v0.10.0

## Token Optimization — READ THIS FIRST

When generating PixelEngine videos, read `llms.txt` ONLY (596 lines). It contains everything you need:
golden rules, quick-start template, 15+ copy-paste patterns, debug commands, and sound effects.

**DO NOT** read source files in `pixelengine/` unless:
1. Debugging a runtime error with a traceback pointing to a specific file
2. The user explicitly asks you to examine engine internals
3. You need to verify a specific class signature not covered in llms.txt

## Reading Priority
1. `llms.txt` — complete AI cookbook (read this for ANY video task)
2. `docs/agent-guide.md` — only if you need agent pipeline details
3. Source code — only for debugging engine bugs

## DO NOT READ (token waste)
- `pixelengine/*.py` — internal source code, not needed for video creation
- `llms-full.txt` — older, less curated version
- `PIXELENGINE_MANUAL.md` — human-oriented manual, redundant with llms.txt
- `README.md` — project overview, not needed for video creation
- `docs/api-reference.md` — redundant with llms.txt patterns

## Quick Commands
```bash
python script.py --test-frame=2.0   # Visual check (saves test_frame.png)
python script.py --validate          # Structured validation report
pixelengine-lint script.py           # Lint for bad patterns
python script.py                     # Full render
```

## Key Conventions
- Canvas: 270x480 (portrait) or 480x270 (landscape), upscaled 4x
- Coordinate system: (0,0) top-left, center at (135, 240) portrait
- Use `Layout.portrait()` / `Layout.landscape()` for positioning — never hardcode
- Use `OrganicMoveTo` / `OrganicFadeIn` over `MoveTo` / `FadeIn`
- Use `VStack` / `HStack` for grouping
- Reveal with `Create(obj)` not bare `self.add(obj)`
