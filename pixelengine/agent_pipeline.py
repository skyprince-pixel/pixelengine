"""PixelEngine Agent Pipeline — end-to-end lint→validate→render orchestration.

Combines lint, validation, test-frame, and render into a single programmable
pipeline that AI agents can invoke and parse results from.

Usage::

    from pixelengine.agent_pipeline import AgentPipeline

    result = AgentPipeline.run(
        script_path="examples/my_short.py",
        steps=["lint", "validate@2.0", "test_frame@2.0", "render"],
    )
    print(result.status)      # "SUCCESS" | "LINT_FAIL" | "VALIDATE_FAIL" | "RENDER_FAIL"
    print(result.output_path)
    print(result.issues)
"""
import importlib.util
import json
import os
import sys
import time
import traceback

from pixelengine.log import logger


class PipelineResult:
    """Structured result from an AgentPipeline run."""

    def __init__(self):
        self.status = "PENDING"  # SUCCESS, LINT_FAIL, VALIDATE_FAIL, RENDER_FAIL, ERROR
        self.output_path = None
        self.test_frame_path = None
        self.issues = []
        self.lint_result = None
        self.validation_report = None
        self.duration = 0.0
        self.steps_completed = []
        self.steps_failed = []
        self.error = None

    def to_dict(self):
        return {
            "status": self.status,
            "output_path": self.output_path,
            "test_frame_path": self.test_frame_path,
            "issues": self.issues,
            "lint_passed": self.lint_result.get("passed", False) if self.lint_result else None,
            "validation_status": self.validation_report.get("status") if self.validation_report else None,
            "duration": round(self.duration, 2),
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "error": self.error,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self):
        return f"PipelineResult(status={self.status!r}, issues={len(self.issues)})"


class AgentPipeline:
    """End-to-end pipeline for AI agent video creation.

    Orchestrates: lint → validate → test_frame → render → verify.

    Usage::

        result = AgentPipeline.run("examples/my_short.py")
        result = AgentPipeline.run("examples/my_short.py",
            steps=["lint", "validate@2.0", "render"],
            on_failure="report"
        )
    """

    @classmethod
    def run(cls, script_path, config=None, steps=None, on_failure="report",
            scene_cls=None, scene_name=None):
        """Execute the full pipeline.

        Args:
            script_path: Path to the Python script.
            config: Optional PixelConfig override.
            steps: List of pipeline steps. Default: ["lint", "validate", "render"].
                   Supported: "lint", "validate", "validate@T", "test_frame@T", "render".
            on_failure: "report" (continue and report), "abort" (stop at first failure).
            scene_cls: Optional Scene class (if already imported).
            scene_name: Name of Scene class in the script. Auto-detected if None.

        Returns:
            PipelineResult with structured diagnostics.
        """
        result = PipelineResult()
        start_time = time.time()

        if steps is None:
            steps = ["lint", "validate", "render"]

        if not os.path.exists(script_path):
            result.status = "ERROR"
            result.error = f"Script not found: {script_path}"
            return result

        logger.info("Starting pipeline: %s", os.path.basename(script_path))
        logger.info("Steps: %s", " -> ".join(steps))
        logger.info("On failure: %s", on_failure)

        for step in steps:
            step_name, _, step_arg = step.partition("@")

            try:
                if step_name == "lint":
                    success = cls._step_lint(script_path, result)
                    if not success and on_failure == "abort":
                        result.status = "LINT_FAIL"
                        break

                elif step_name == "validate":
                    ts = float(step_arg) if step_arg else None
                    success = cls._step_validate(script_path, config, result,
                                                  scene_cls, scene_name,
                                                  at=[ts] if ts else None)
                    if not success and on_failure == "abort":
                        result.status = "VALIDATE_FAIL"
                        break

                elif step_name == "test_frame":
                    ts = float(step_arg) if step_arg else 2.0
                    cls._step_test_frame(script_path, config, result,
                                         scene_cls, scene_name, at=ts)

                elif step_name == "render":
                    success = cls._step_render(script_path, config, result,
                                                scene_cls, scene_name)
                    if not success:
                        result.status = "RENDER_FAIL"

                else:
                    logger.warning("Unknown step: %s", step)

                result.steps_completed.append(step)

            except Exception as e:
                result.steps_failed.append(step)
                result.error = f"{step}: {str(e)}"
                result.issues.append({
                    "type": "PIPELINE_ERROR",
                    "step": step,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })
                if on_failure == "abort":
                    result.status = "ERROR"
                    break

        # Final status determination
        if result.status == "PENDING":
            if result.steps_failed:
                result.status = "ERROR"
            elif any(i.get("severity") == "error" for i in result.issues):
                result.status = "VALIDATE_FAIL"
            else:
                result.status = "SUCCESS"

        result.duration = time.time() - start_time
        logger.info("Pipeline complete: %s (%.1fs)", result.status, result.duration)
        return result

    @classmethod
    def _step_lint(cls, script_path, result):
        """Run the linter and capture results."""
        logger.info("[1/4] Linting...")
        from pixelengine.cli_lint import lint_source

        with open(script_path, "r") as f:
            source = f.read()

        lint_result = lint_source(source)
        result.lint_result = lint_result

        for v in lint_result.get("violations", []):
            result.issues.append({
                "type": "LINT_VIOLATION",
                "severity": "error",
                "message": v,
            })
        for s in lint_result.get("suggestions", []):
            result.issues.append({
                "type": "LINT_SUGGESTION",
                "severity": "info",
                "message": s,
            })

        passed = lint_result.get("passed", True)
        n_violations = len(lint_result.get("violations", []))
        n_suggestions = len(lint_result.get("suggestions", []))
        logger.info("Lint %s: %d violations, %d suggestions",
                     "passed" if passed else "failed", n_violations, n_suggestions)
        return passed

    @classmethod
    def _step_validate(cls, script_path, config, result,
                       scene_cls=None, scene_name=None, at=None):
        """Run structural validation."""
        logger.info("[2/4] Validating...")
        from pixelengine.validate import SceneValidator

        if scene_cls is None:
            scene_cls = cls._load_scene(script_path, scene_name)
        if scene_cls is None:
            result.issues.append({
                "type": "VALIDATE_ERROR",
                "severity": "error",
                "message": "Could not find Scene class in script.",
            })
            return False

        if config is None:
            from pixelengine.config import PixelConfig
            config = PixelConfig.portrait()

        report = SceneValidator.validate(scene_cls, config=config, at=at,
                                          source_path=script_path)
        result.validation_report = report

        for issue in report.get("issues", []):
            result.issues.append(issue)

        status = report.get("status", "FAIL")
        logger.info("Validation %s: errors=%d, warnings=%d",
                     status, report['issue_summary']['errors'],
                     report['issue_summary']['warnings'])

        return status != "FAIL"

    @classmethod
    def _step_test_frame(cls, script_path, config, result,
                         scene_cls=None, scene_name=None, at=2.0):
        """Generate a test frame."""
        logger.info("[3/4] Test frame at t=%ss...", at)

        if scene_cls is None:
            scene_cls = cls._load_scene(script_path, scene_name)
        if scene_cls is None:
            return

        if config is None:
            from pixelengine.config import PixelConfig
            config = PixelConfig.portrait()

        # Inject test-frame target
        scene = scene_cls(config)
        scene.test_frame_target = at
        scene._renderer = None

        try:
            scene.construct()
        except Exception:
            pass  # SilentExit is expected

        module_name = os.path.splitext(os.path.basename(script_path))[0]
        tf_path = os.path.join("outputs", module_name, "test_frame.png")

        if os.path.exists(tf_path):
            result.test_frame_path = tf_path
            logger.debug("Test frame saved: %s", tf_path)
        else:
            logger.warning("Test frame not generated (scene may be shorter than %ss)", at)

    @classmethod
    def _step_render(cls, script_path, config, result,
                     scene_cls=None, scene_name=None):
        """Full render."""
        logger.info("[4/4] Rendering...")

        if scene_cls is None:
            scene_cls = cls._load_scene(script_path, scene_name)
        if scene_cls is None:
            result.issues.append({
                "type": "RENDER_ERROR",
                "severity": "error",
                "message": "Could not find Scene class in script.",
            })
            return False

        if config is None:
            from pixelengine.config import PixelConfig
            config = PixelConfig.portrait()

        try:
            scene = scene_cls(config)
            scene.render()

            # Find the output path from the auto-organized output dir
            module_name = os.path.splitext(os.path.basename(script_path))[0]
            outputs_dir = os.path.join("outputs", module_name)
            if os.path.exists(outputs_dir):
                for f in os.listdir(outputs_dir):
                    if f.endswith(".mp4"):
                        result.output_path = os.path.join(outputs_dir, f)
                        break

            if result.output_path:
                size = os.path.getsize(result.output_path) / 1024
                logger.debug("Output: %s (%.1f KB)", result.output_path, size)
            return True
        except Exception as e:
            result.issues.append({
                "type": "RENDER_ERROR",
                "severity": "error",
                "message": str(e),
            })
            logger.error("Render failed: %s", e)
            return False

    @classmethod
    def _load_scene(cls, script_path, scene_name=None):
        """Dynamically load a Scene class from a script file."""
        try:
            spec = importlib.util.spec_from_file_location("_agent_script", script_path)
            mod = importlib.util.module_from_spec(spec)

            # Prevent the script from auto-rendering
            old_argv = sys.argv
            sys.argv = [script_path, "--dry-run"]

            try:
                spec.loader.exec_module(mod)
            finally:
                sys.argv = old_argv

            # Find Scene subclass
            from pixelengine.scene import Scene
            for name in dir(mod):
                obj = getattr(mod, name)
                if (isinstance(obj, type) and issubclass(obj, Scene)
                        and obj is not Scene and name != "Scene"):
                    if obj.__module__ == mod.__name__:
                        if scene_name is None or name == scene_name:
                            return obj

        except Exception as e:
            logger.error("Could not load scene from %s: %s", script_path, e)
        return None

    @classmethod
    def quick(cls, script_path, config=None):
        """Quick pipeline: lint + render (skip validation for speed).

        Usage::

            result = AgentPipeline.quick("examples/my_short.py")
        """
        return cls.run(script_path, config=config,
                       steps=["lint", "render"], on_failure="report")

    @classmethod
    def full(cls, script_path, config=None):
        """Full pipeline: lint + validate + test_frame + render.

        Usage::

            result = AgentPipeline.full("examples/my_short.py")
        """
        return cls.run(script_path, config=config,
                       steps=["lint", "validate", "test_frame@2.0", "render"],
                       on_failure="report")
