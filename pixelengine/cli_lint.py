"""PixelEngine Custom Linter & Feature Suggester for AI Agent Enforcement.

This script parses the Abstract Syntax Tree (AST) of a PixelEngine script to:
1. Catch bad patterns (basic animations when organic ones exist).
2. Suggest missing premium features that would elevate the video quality.
3. Map topic-relevant features the AI may not know about.

Run: pixelengine-lint script.py
"""
import ast
import sys
import os


# ── Feature detection sets ──────────────────────────────────────────
ORGANIC_ANIMS = {
    "OrganicMoveTo", "OrganicScale", "OrganicFadeIn", "OrganicFadeOut",
    "OrganicRotate", "Breathe", "Sway", "Float", "Jitter", "Pulse",
    "SquashAndStretch", "Wobble", "Drift", "Anticipate", "Settle",
    "RubberBand", "WithNoise", "WithFollow", "WithAnticipation",
    "WithSettle", "WithSquashStretch", "Wave", "Cascade", "Swarm",
}
CONSTRUCTION_ANIMS = {
    "Create", "Uncreate", "DrawBorderThenFill", "GrowFromPoint",
    "GrowFromEdge", "GrowArrow", "ShowPassingFlash",
}
ADVANCED_ANIMS = {
    "SpringTo", "SpringScale", "FollowPath", "KeyframeTrack",
    "MorphTo", "VMorph", "ReplacementTransform",
}
TRANSITION_CLASSES = {
    "GlitchTransition", "ShatterTransition", "PixelateTransition",
    "CrossDissolve", "FadeTransition", "WipeTransition",
    "IrisTransition", "SlideTransition", "DissolveTransition",
}
PARTICLE_CLASSES = {
    "ParticleEmitter", "ParticleBurst",
}
TEXT_ANIMS = {
    "PerCharacter", "PerWord", "ScrambleReveal", "TypeWriterPro",
    "DynamicCaption",
}
CAMERA_FX_CLASSES = {
    "Vignette", "ChromaticAberration", "FilmGrain", "DepthOfField",
    "Letterbox", "CRTScanlines", "Ripple", "HeatShimmer", "Pixelate",
    "ColorGrade",
}
LIGHTING_CLASSES = {
    "AmbientLight", "PointLight", "DirectionalLight",
}
TEXTURE_CLASSES = {
    "PatternTexture", "GradientTexture", "DitherTexture", "NoiseTexture",
}
BG_ELEMENTS = {
    "Grid", "Starfield", "ParallaxLayer", "Terrain",
}
UPDATER_FUNCS = {
    "alive", "hover", "orbit_idle", "wind_sway",
}
LAYOUT_USAGE = {
    "Layout", "VStack", "HStack",
}

# Topic → Feature suggestions
TOPIC_HINTS = {
    "physics": ["PhysicsWorld", "PhysicsBody", "Pendulum", "Spring"],
    "gravity": ["PhysicsWorld", "PhysicsBody"],
    "math": ["MathTex", "Axes", "NumberLine", "Graph"],
    "equation": ["MathTex", "Create"],
    "chart": ["BarChart", "GrowFromEdge", "ValueTracker"],
    "graph": ["Axes", "Graph", "NetworkGraph"],
    "3d": ["Cube3D", "Sphere3D", "Orbit3D"],
    "orbit": ["OrbitalSystem", "CircularPath", "FollowPath"],
    "vector": ["Vector", "VArrow", "VCircle", "VRect"],
    "morph": ["VMorph", "MorphTo"],
    "network": ["NetworkGraph"],
    "pixel": ["PixelArtist"],
    "terrain": ["Terrain"],
    "pendulum": ["Pendulum"],
    "spring": ["Spring"],
    "fluid": ["FluidParticles"],
    "rope": ["Rope"],
}


def check_script(filepath):
    """Analyze a python file for bad patterns AND suggest missing premium features."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[PixelEngineLint] FATAL Syntax Error parsing {filepath}: {e}")
        return False

    warnings = []
    suggestions = []
    has_scene = False

    # Track which feature categories are present
    found = {
        "organic_anim": False,
        "construction_anim": False,
        "advanced_anim": False,
        "transition": False,
        "particles": False,
        "rich_text_anim": False,
        "camera_fx": False,
        "lighting": False,
        "texture": False,
        "bg_elements": False,
        "updaters": False,
        "layout": False,
        "voiceover": False,
        "sound_fx": False,
        "camera_shake": False,
        "set_background": False,
        "setup_atmosphere": False,
    }

    # Collect all names used in source for quick keyword search
    all_names = set()
    all_strings = set()

    for node in ast.walk(tree):
        # ── Scene detection ──
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in (
                    "Scene", "CinematicScene", "CleanScene",
                ):
                    has_scene = True

        # ── Name collection ──
        if isinstance(node, ast.Name):
            all_names.add(node.id)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            all_strings.add(node.value.lower())

        # ── Function / class call detection ──
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name:
                # Feature category tracking
                if func_name in ORGANIC_ANIMS:
                    found["organic_anim"] = True
                if func_name in CONSTRUCTION_ANIMS:
                    found["construction_anim"] = True
                if func_name in ADVANCED_ANIMS:
                    found["advanced_anim"] = True
                if func_name in TRANSITION_CLASSES:
                    found["transition"] = True
                if func_name in PARTICLE_CLASSES:
                    found["particles"] = True
                if func_name in TEXT_ANIMS:
                    found["rich_text_anim"] = True
                if func_name in CAMERA_FX_CLASSES:
                    found["camera_fx"] = True
                if func_name in LIGHTING_CLASSES:
                    found["lighting"] = True
                if func_name in TEXTURE_CLASSES:
                    found["texture"] = True
                if func_name in BG_ELEMENTS:
                    found["bg_elements"] = True
                if func_name in UPDATER_FUNCS:
                    found["updaters"] = True
                if func_name in LAYOUT_USAGE:
                    found["layout"] = True
                if func_name in ("play_voiceover", "generate", "narrate") or "VoiceOver" in all_names:
                    found["voiceover"] = True
                if func_name == "dynamic" or func_name in (
                    "piano_note", "bell_note", "mallet_note",
                    "coin", "explosion", "jump",
                ):
                    found["sound_fx"] = True
                if func_name == "shake":
                    found["camera_shake"] = True
                if func_name == "set_background":
                    found["set_background"] = True
                if func_name == "setup_atmosphere":
                    found["setup_atmosphere"] = True

                # ── Anti-pattern detection ──
                if func_name == "MoveTo":
                    warnings.append(
                        f"Line {node.lineno}: Detected 'MoveTo'. "
                        "Use 'OrganicMoveTo(target, x, y, feel=\"bouncy\")' or "
                        "'SpringTo(target, x, y)' instead for natural motion."
                    )
                elif func_name == "FadeIn":
                    warnings.append(
                        f"Line {node.lineno}: Detected 'FadeIn'. "
                        "Use 'OrganicFadeIn(target)' or 'DrawBorderThenFill(target)' "
                        "for a progressive reveal."
                    )
                elif func_name == "TypeWriter":
                    warnings.append(
                        f"Line {node.lineno}: Detected 'TypeWriter'. "
                        "Use 'TypeWriterPro(text, cursor=True)' or "
                        "'PerCharacter(text, \"fade_in\", lag=0.05)' for richer text animation."
                    )
                elif func_name == "FadeOut":
                    warnings.append(
                        f"Line {node.lineno}: Detected 'FadeOut'. "
                        "Use 'OrganicFadeOut(target)' for smoother exit animation."
                    )

                # ── Audio sync anti-pattern ──
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "play_sound"
                ):
                    warnings.append(
                        f"Line {node.lineno}: Detected 'self.play_sound()'. "
                        "For voiceover, use 'self.play(anim, duration=dur, sound=sfx)' "
                        "or 'self.narrate(text, animate=anim)' to keep audio and visuals in sync."
                    )

                # ── Bare self.remove() anti-pattern ──
                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "remove"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "self"
                ):
                    warnings.append(
                        f"Line {node.lineno}: Detected 'self.remove()'. "
                        "Use 'OrganicFadeOut(obj)' before removing to avoid objects "
                        "vanishing abruptly at scene boundaries."
                    )

            # ── Hardcoded coordinate detection ──
            if isinstance(node.func, ast.Name) and node.func.id in (
                "Rect", "Circle", "PixelText", "MathTex",
            ):
                for kw in node.keywords:
                    if kw.arg in ("x", "y"):
                        if isinstance(kw.value, ast.Constant) and isinstance(
                            kw.value.value, (int, float)
                        ):
                            warnings.append(
                                f"Line {node.lineno}: Hardcoded `{kw.arg}={kw.value.value}` "
                                f"in '{node.func.id}'. "
                                "Use Layout zones (L.MAIN_ZONE.x) or VStack/HStack instead."
                            )

    if not has_scene:
        warnings.append(
            "Script does not contain a Scene subclass extending "
            "'Scene', 'CinematicScene', or 'CleanScene'."
        )

    # ── Missing feature suggestions (core — always recommend) ──
    if not found["construction_anim"]:
        suggestions.append(
            "🏗️  No construction animations found. Don't just self.add(obj).\n"
            "     Use: self.play(Create(obj), duration=1.0)\n"
            "     Or:  self.play(DrawBorderThenFill(obj), duration=1.5)\n"
            "     Or:  self.play(GrowFromPoint(obj, x, y), duration=1.0)"
        )

    if not found["organic_anim"]:
        suggestions.append(
            "🌿 No organic animations found. Motion feels robotic.\n"
            "     Replace MoveTo with OrganicMoveTo(obj, x, y, feel=\"bouncy\")\n"
            "     Use Cascade([OrganicFadeIn(o) for o in items]) for group reveals\n"
            "     Attach ambient motion: obj.add_updater(alive())"
        )

    if not found["sound_fx"]:
        suggestions.append(
            "🔊 No sound effects. Add impact sounds on key visual moments:\n"
            "     self.play_sound(SoundFX.dynamic(\"reveal\"))\n"
            "     self.play_sound(SoundFX.dynamic(\"impact\"))"
        )

    if not found["rich_text_anim"]:
        suggestions.append(
            "📝 Using basic text. Consider rich text animation:\n"
            "     self.play(PerCharacter(text, \"fade_in\", lag=0.05), duration=2.0)\n"
            "     Or: self.play(ScrambleReveal(text), duration=1.5)\n"
            "     Or: cap = DynamicCaption(text, x=..., y=...)"
        )

    # ── Optional polish (only hint, not prescriptive) ──
    optional_missing = []
    if not found["lighting"] and not found["setup_atmosphere"]:
        optional_missing.append("PointLight/AmbientLight")
    if not found["camera_fx"] and not found["setup_atmosphere"]:
        optional_missing.append("Vignette/ColorGrade")
    if not found["transition"]:
        optional_missing.append("GlitchTransition/CrossDissolve")
    if not found["particles"]:
        optional_missing.append("ParticleBurst/ParticleEmitter")
    if not found["bg_elements"]:
        optional_missing.append("Grid/Starfield/Terrain")

    if optional_missing:
        items = ", ".join(optional_missing)
        suggestions.append(
            f"💎 Optional polish (add only if the scene benefits): {items}\n"
            "     Use self.setup_atmosphere(\"dark\") to add lighting + FX in one call."
        )

    # ── Topic-based feature hints ──
    topic_suggestions = []
    source_lower = source.lower()
    for keyword, features in TOPIC_HINTS.items():
        if keyword in source_lower:
            for feat in features:
                if feat not in all_names:
                    topic_suggestions.append(f"{feat}")

    if topic_suggestions:
        unique = list(dict.fromkeys(topic_suggestions))[:6]
        suggestions.append(
            f"🎯 Based on your topic, consider using: {', '.join(unique)}\n"
            "     Import from pixelengine and use in your construct() method."
        )

    # ── Output ──
    has_issues = bool(warnings)
    has_suggestions = bool(suggestions)

    if has_issues:
        print("\n" + "=" * 60)
        print(f"🚨 [PixelEngineLint] {len(warnings)} violation(s) in {os.path.basename(filepath)}")
        print("=" * 60)
        for w in warnings:
            print(f"  ✗ {w}")
        print("=" * 60)

    if has_suggestions:
        print("\n" + "─" * 60)
        print(f"💡 [PixelEngineLint] {len(suggestions)} suggestion(s) for premium quality:")
        print("─" * 60)
        for s in suggestions:
            print(f"\n  {s}")
        print("\n" + "─" * 60)

    if not has_issues and not has_suggestions:
        print(
            f"✅ [PixelEngineLint] {os.path.basename(filepath)} — "
            "Premium quality! All major features utilized. 🎬"
        )
        return True

    if has_issues:
        print("\nPlease fix violations before final render.")
        return False

    # Suggestions only (no violations) — still passes
    print("\nNo violations found. Consider the suggestions above for even better quality.")
    return True


def lint_source(source: str) -> dict:
    """Lint a Python source string and return structured results.

    This is the programmatic API for AI agents. Instead of printing
    to stdout and returning a boolean, it returns a machine-readable dict.

    Args:
        source: Python source code string to analyze.

    Returns:
        Dict with keys:
          - violations: list of violation message strings
          - suggestions: list of suggestion message strings
          - passed: bool — True if no violations
          - feature_coverage: dict of feature name → bool

    Usage::

        from pixelengine.cli_lint import lint_source

        result = lint_source(code_string)
        if not result["passed"]:
            for v in result["violations"]:
                print(v)
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {
            "violations": [f"Syntax Error: {e}"],
            "suggestions": [],
            "passed": False,
            "feature_coverage": {},
        }

    warnings = []
    suggestions = []
    has_scene = False

    found = {
        "organic_anim": False, "construction_anim": False,
        "advanced_anim": False, "transition": False, "particles": False,
        "rich_text_anim": False, "camera_fx": False, "lighting": False,
        "texture": False, "bg_elements": False, "updaters": False,
        "layout": False, "voiceover": False, "sound_fx": False,
        "camera_shake": False, "set_background": False,
        "setup_atmosphere": False,
    }

    all_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in (
                    "Scene", "CinematicScene", "CleanScene",
                ):
                    has_scene = True

        if isinstance(node, ast.Name):
            all_names.add(node.id)

        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name:
                if func_name in ORGANIC_ANIMS:
                    found["organic_anim"] = True
                if func_name in CONSTRUCTION_ANIMS:
                    found["construction_anim"] = True
                if func_name in ADVANCED_ANIMS:
                    found["advanced_anim"] = True
                if func_name in TRANSITION_CLASSES:
                    found["transition"] = True
                if func_name in PARTICLE_CLASSES:
                    found["particles"] = True
                if func_name in TEXT_ANIMS:
                    found["rich_text_anim"] = True
                if func_name in CAMERA_FX_CLASSES:
                    found["camera_fx"] = True
                if func_name in LIGHTING_CLASSES:
                    found["lighting"] = True
                if func_name in TEXTURE_CLASSES:
                    found["texture"] = True
                if func_name in BG_ELEMENTS:
                    found["bg_elements"] = True
                if func_name in UPDATER_FUNCS:
                    found["updaters"] = True
                if func_name in LAYOUT_USAGE:
                    found["layout"] = True
                if func_name in ("play_voiceover", "generate", "narrate"):
                    found["voiceover"] = True
                if func_name == "dynamic" or func_name in (
                    "piano_note", "bell_note", "mallet_note",
                    "coin", "explosion", "jump",
                ):
                    found["sound_fx"] = True
                if func_name == "shake":
                    found["camera_shake"] = True
                if func_name == "set_background":
                    found["set_background"] = True
                if func_name == "setup_atmosphere":
                    found["setup_atmosphere"] = True

                if func_name == "MoveTo":
                    warnings.append(
                        f"Line {node.lineno}: 'MoveTo' → use 'OrganicMoveTo' instead."
                    )
                elif func_name == "FadeIn":
                    warnings.append(
                        f"Line {node.lineno}: 'FadeIn' → use 'OrganicFadeIn' instead."
                    )
                elif func_name == "TypeWriter":
                    warnings.append(
                        f"Line {node.lineno}: 'TypeWriter' → use 'TypeWriterPro' instead."
                    )
                elif func_name == "FadeOut":
                    warnings.append(
                        f"Line {node.lineno}: 'FadeOut' → use 'OrganicFadeOut' instead."
                    )

                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "play_sound"
                ):
                    warnings.append(
                        f"Line {node.lineno}: 'self.play_sound()' → use "
                        "'self.play(anim, duration=dur, sound=sfx)' or 'self.narrate()' for sync."
                    )

                if (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "remove"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "self"
                ):
                    warnings.append(
                        f"Line {node.lineno}: 'self.remove()' → use 'OrganicFadeOut' "
                        "before removing to avoid visual pops."
                    )

    if not has_scene:
        warnings.append("No Scene subclass found.")

    if not found["construction_anim"]:
        suggestions.append("Add construction animations (Create, DrawBorderThenFill).")
    if not found["organic_anim"]:
        suggestions.append("Add organic animations (OrganicMoveTo, Cascade).")
    if not found["sound_fx"]:
        suggestions.append("Add sound effects (SoundFX.dynamic()).")

    return {
        "violations": warnings,
        "suggestions": suggestions,
        "passed": len(warnings) == 0,
        "feature_coverage": found,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: pixelengine-lint <script.py>")
        print("\nAnalyzes your PixelEngine script for:")
        print("  - Anti-patterns (basic animations, hardcoded coordinates)")
        print("  - Missing premium features (lighting, particles, transitions)")
        print("  - Topic-relevant feature suggestions")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        sys.exit(1)
        
    success = check_script(filepath)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
