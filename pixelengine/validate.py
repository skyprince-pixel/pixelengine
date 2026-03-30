"""PixelEngine Structured Validation — machine-readable scene diagnostics.

Replaces visual --test-frame inspection with structured JSON reports
that AI agents can parse and act on programmatically.

Usage::

    from pixelengine.validate import SceneValidator
    report = SceneValidator.validate(MyScene, config=PixelConfig.portrait(), at=[1.0, 3.0])
"""
import ast
import os


class SceneValidator:
    """Validates a PixelEngine scene and returns structured diagnostics."""

    @classmethod
    def validate(cls, scene_cls, config=None, at=None, source_path=None):
        from pixelengine.config import DEFAULT_CONFIG
        config = config or DEFAULT_CONFIG
        at = at or [1.0, 3.0, 5.0, 8.0]
        cw, ch = config.canvas_width, config.canvas_height

        snapshots, dead_waits = cls._capture(scene_cls, config, at)
        issues = []

        for t, objects in snapshots.items():
            for obj in objects:
                if not obj["visible"]:
                    continue
                x, y, w, h = obj["x"], obj["y"], obj["width"], obj["height"]
                name = obj["class"]

                if x < -w and w > 0:
                    issues.append({"type": "OUT_OF_BOUNDS", "object": name,
                                   "frame_time": t, "position": {"x": x, "y": y},
                                   "bounds": {"x_min": 0, "x_max": cw},
                                   "severity": "error",
                                   "suggestion": f"Move {name} to x >= 0"})
                elif x > cw + w:
                    issues.append({"type": "OUT_OF_BOUNDS", "object": name,
                                   "frame_time": t, "position": {"x": x, "y": y},
                                   "bounds": {"x_min": 0, "x_max": cw},
                                   "severity": "error",
                                   "suggestion": f"Move {name} to x <= {cw}"})
                if y < -h and h > 0:
                    issues.append({"type": "OUT_OF_BOUNDS", "object": name,
                                   "frame_time": t, "position": {"x": x, "y": y},
                                   "bounds": {"y_min": 0, "y_max": ch},
                                   "severity": "error",
                                   "suggestion": f"Move {name} to y >= 0"})
                elif y > ch + h:
                    issues.append({"type": "OUT_OF_BOUNDS", "object": name,
                                   "frame_time": t, "position": {"x": x, "y": y},
                                   "bounds": {"y_min": 0, "y_max": ch},
                                   "severity": "error",
                                   "suggestion": f"Move {name} to y <= {ch}"})

                if obj["opacity"] <= 0 and not obj["has_updaters"]:
                    issues.append({"type": "INVISIBLE", "object": name,
                                   "frame_time": t, "severity": "warning",
                                   "suggestion": f"{name} has opacity=0 with no updaters."})

            visible = [o for o in objects if o["visible"] and o["opacity"] > 0]
            for i in range(len(visible)):
                for j in range(i + 1, len(visible)):
                    a, b = visible[i], visible[j]
                    if a["z_index"] != b["z_index"]:
                        continue
                    aw, ah = max(a["width"], 1), max(a["height"], 1)
                    bw, bh = max(b["width"], 1), max(b["height"], 1)
                    ox = max(0, min(a["x"]+aw//2, b["x"]+bw//2) - max(a["x"]-aw//2, b["x"]-bw//2))
                    oy = max(0, min(a["y"]+ah//2, b["y"]+bh//2) - max(a["y"]-ah//2, b["y"]-bh//2))
                    if ox * oy > 50:
                        issues.append({"type": "OVERLAP", "objects": [a["class"], b["class"]],
                                       "frame_time": t, "overlap_area": ox * oy,
                                       "severity": "warning",
                                       "suggestion": "Adjust z_index or positions."})

        for w in dead_waits:
            issues.append({"type": "DEAD_AIR", "start": w["start"], "end": w["end"],
                           "duration": w["duration"], "severity": "warning",
                           "suggestion": f"Add visual activity during {w['duration']:.1f}s wait."})

        coverage = cls._analyze_coverage(source_path)
        errors = [i for i in issues if i.get("severity") == "error"]
        status = "FAIL" if errors else ("WARN" if issues else "PASS")

        return {"frames_analyzed": len(snapshots), "timestamps": list(snapshots.keys()),
                "issues": issues, "issue_summary": {"errors": len(errors), "warnings": len(issues) - len(errors)},
                "coverage": coverage, "status": status}

    @classmethod
    def _capture(cls, scene_cls, config, timestamps):
        scene = scene_cls(config)
        frame_states = {}
        captured = set()
        dead_waits = []

        original_capture = scene._capture_frame
        original_wait = scene.wait
        original_play = scene.play

        def patched_capture():
            original_capture()
            t = round(scene._current_time, 2)
            for tt in timestamps:
                if abs(t - tt) < (1.0 / scene.config.fps + 0.001) and tt not in captured:
                    captured.add(tt)
                    frame_states[tt] = [
                        {"class": o.__class__.__name__, "x": round(getattr(o, 'x', 0), 1),
                         "y": round(getattr(o, 'y', 0), 1),
                         "width": getattr(o, 'width', 0) or 0,
                         "height": getattr(o, 'height', 0) or 0,
                         "visible": getattr(o, 'visible', True),
                         "opacity": round(getattr(o, 'opacity', 1.0), 2),
                         "z_index": getattr(o, 'z_index', 0),
                         "has_updaters": bool(getattr(o, '_updaters', []))}
                        for o in scene._objects
                    ]

        def patched_wait(seconds=1.0):
            start_t = scene._current_time
            has_activity = any(bool(getattr(o, '_updaters', [])) for o in scene._objects if getattr(o, 'visible', True))
            original_wait(seconds)
            if seconds > 2.0 and not has_activity:
                dead_waits.append({"start": round(start_t, 2), "end": round(scene._current_time, 2), "duration": round(seconds, 2)})

        # Mock VoiceOver to prevent slow TTS initialization during validation
        from pixelengine.voiceover import VoiceOver
        original_generate = VoiceOver.generate

        def patched_generate(text: str, voice: str = None, speed: float = 1.0, *args, **kwargs):
            from pixelengine.sound import SoundFX
            import numpy as np
            # Return a dummy 1-second SoundFX
            sfx = SoundFX(np.zeros(24000, dtype=np.float32), name="dummy_tts")
            # Estimate duration coarsely based on word count
            estimated_duration = max(1.0, len(text.split()) * 0.4)
            return sfx, estimated_duration

        scene._capture_frame = patched_capture
        scene.wait = patched_wait
        scene._renderer = None
        VoiceOver.generate = classmethod(patched_generate)

        try:
            scene.construct()
        except Exception:
            pass
        finally:
            VoiceOver.generate = original_generate

        return frame_states, dead_waits

    @classmethod
    def _analyze_coverage(cls, source_path=None):
        coverage = {"organic_anim": False, "construction_anim": False, "lighting": False,
                    "camera_fx": False, "sound_fx": False, "voiceover": False,
                    "transition": False, "particles": False, "texture": False,
                    "layout": False, "rich_text": False, "vector_graphics": False}
        if not source_path or not os.path.exists(source_path):
            return coverage
        try:
            with open(source_path, "r") as f:
                tree = ast.parse(f.read())
        except (SyntaxError, IOError):
            return coverage

        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    names.add(node.func.attr)

        coverage["organic_anim"] = bool(names & {"OrganicMoveTo", "OrganicScale", "OrganicFadeIn", "Cascade", "Wave", "Swarm"})
        coverage["construction_anim"] = bool(names & {"Create", "DrawBorderThenFill", "GrowFromPoint", "GrowFromEdge"})
        coverage["lighting"] = bool(names & {"PointLight", "AmbientLight", "DirectionalLight", "setup_atmosphere"})
        coverage["camera_fx"] = bool(names & {"Vignette", "ChromaticAberration", "DepthOfField", "ColorGrade"})
        coverage["sound_fx"] = bool(names & {"SoundFX", "dynamic", "piano_note"})
        coverage["voiceover"] = "VoiceOver" in names or "narrate" in names
        coverage["transition"] = bool(names & {"GlitchTransition", "ShatterTransition", "CrossDissolve"})
        coverage["particles"] = bool(names & {"ParticleBurst", "ParticleEmitter"})
        coverage["texture"] = bool(names & {"GradientTexture", "PatternTexture", "NoiseTexture"})
        coverage["layout"] = bool(names & {"Layout", "VStack", "HStack"})
        coverage["rich_text"] = bool(names & {"PerCharacter", "ScrambleReveal", "TypeWriterPro", "DynamicCaption"})
        coverage["vector_graphics"] = bool(names & {"VCircle", "VRect", "VPolygon", "VArrow", "VMorph"})
        return coverage

    @classmethod
    def print_report(cls, report):
        icon = {"PASS": "✅", "WARN": "⚠️ ", "FAIL": "❌"}.get(report["status"], "?")
        print(f"\n{'=' * 60}")
        print(f" {icon} PixelEngine Validation: {report['status']}")
        print(f"{'=' * 60}")
        print(f"  Frames: {report['frames_analyzed']} | Errors: {report['issue_summary']['errors']} | Warnings: {report['issue_summary']['warnings']}")
        for issue in report["issues"]:
            sev = "🔴" if issue["severity"] == "error" else "🟡"
            obj_str = issue.get("object", ", ".join(issue.get("objects", [])))
            t_str = f" at t={issue['frame_time']}s" if "frame_time" in issue else ""
            print(f"  {sev} [{issue['type']}] {obj_str}{t_str}")
            if "suggestion" in issue:
                print(f"     → {issue['suggestion']}")
        cov = report.get("coverage", {})
        if cov:
            used = sum(1 for v in cov.values() if v)
            print(f"\n  Feature Coverage: {used}/{len(cov)}")
            missing = [k for k, v in cov.items() if not v]
            if missing:
                print(f"  Missing: {', '.join(missing)}")
        print()

    @classmethod
    def validate_and_print(cls, scene_cls, config=None, at=None, source_path=None):
        report = cls.validate(scene_cls, config=config, at=at, source_path=source_path)
        cls.print_report(report)
        return report
