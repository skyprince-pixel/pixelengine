"""PixelEngine data-driven video templates — JSON/YAML input → parameterized video.

Templates accept typed input data and produce parameterized videos.
Enables batch generation, API-driven rendering, and AI agent integration.

Usage::

    from pixelengine.templates import VideoTemplate, TemplateRunner

    class CountdownTemplate(VideoTemplate):
        \"\"\"Countdown timer video.\"\"\"
        schema = {
            "type": "object",
            "required": ["title", "count"],
            "properties": {
                "title": {"type": "string"},
                "count": {"type": "integer", "minimum": 1, "maximum": 60},
                "color": {"type": "string", "default": "#FF004D"},
            },
        }

        def construct(self, data):
            from pixelengine import PixelText, OrganicFadeIn
            title = PixelText(data["title"], x=self.L.cx, y=self.L.TITLE_ZONE.y, align="center")
            self.scene.add(title)
            self.scene.play(OrganicFadeIn(title), duration=0.5)
            self.scene.wait(data["count"])

    # CLI usage:
    #   python -m pixelengine.templates CountdownTemplate --data input.json
    #
    # Programmatic usage:
    TemplateRunner.render(CountdownTemplate, {"title": "GO!", "count": 10})
"""
import json
import os
import sys
from pixelengine.config import PixelConfig
from pixelengine.scene import Scene
from pixelengine.layout import Layout


class VideoTemplate:
    """Base class for data-driven video templates.

    Subclasses define a ``schema`` (JSON Schema dict) and implement
    ``construct(data)`` which receives validated input data.

    The template has access to:
      - ``self.scene`` — the active Scene instance
      - ``self.config`` — the PixelConfig
      - ``self.L`` — the Layout instance
      - ``self.data`` — the validated input data
    """

    # JSON Schema for input validation (override in subclass)
    schema = {"type": "object"}

    def construct(self, data: dict):
        """Build the scene using the provided data.

        Override this in your template subclass.

        Args:
            data: Validated input data matching self.schema.
        """
        raise NotImplementedError("Template must implement construct()")

    def setup(self, scene, config, layout):
        """Called by the runner to wire up the template. Not user-facing."""
        self.scene = scene
        self.config = config
        self.L = layout
        self.data = None


def validate_data(data: dict, schema: dict) -> list:
    """Validate data against a JSON Schema. Returns list of error strings.

    Uses a simple built-in validator (no jsonschema dependency required).
    Checks: required fields, type constraints, enum values, min/max.
    """
    errors = []
    props = schema.get("properties", {})
    required = schema.get("required", [])

    # Check required fields
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    # Check types and constraints
    for key, value in data.items():
        if key not in props:
            continue
        prop = props[key]

        # Type check
        expected_type = prop.get("type")
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        if expected_type and expected_type in type_map:
            if not isinstance(value, type_map[expected_type]):
                errors.append(
                    f"Field '{key}': expected {expected_type}, got {type(value).__name__}"
                )
                continue

        # Numeric constraints
        if isinstance(value, (int, float)):
            if "minimum" in prop and value < prop["minimum"]:
                errors.append(f"Field '{key}': {value} < minimum {prop['minimum']}")
            if "maximum" in prop and value > prop["maximum"]:
                errors.append(f"Field '{key}': {value} > maximum {prop['maximum']}")

        # Enum
        if "enum" in prop and value not in prop["enum"]:
            errors.append(f"Field '{key}': {value!r} not in {prop['enum']}")

    return errors


def _apply_defaults(data: dict, schema: dict) -> dict:
    """Apply default values from schema for missing fields."""
    result = dict(data)
    props = schema.get("properties", {})
    for key, prop in props.items():
        if key not in result and "default" in prop:
            result[key] = prop["default"]
    return result


class _TemplateScene(Scene):
    """Internal Scene wrapper that delegates construct() to a template."""

    def __init__(self, template, data, config=None):
        super().__init__(config=config)
        self._template = template
        self._data = data

    def construct(self):
        self._template.construct(self._data)


class TemplateRunner:
    """Renders a VideoTemplate with data input.

    Usage::

        TemplateRunner.render(MyTemplate, {"title": "Hello"}, output_path="out.mp4")

        # From JSON file:
        TemplateRunner.render_from_file(MyTemplate, "data.json")
    """

    @staticmethod
    def render(template_cls, data: dict, config: PixelConfig = None,
               output_path: str = None, **render_kwargs):
        """Render a template with the given data.

        Args:
            template_cls: VideoTemplate subclass (class, not instance).
            data: Input data dict matching the template's schema.
            config: PixelConfig (default: landscape).
            output_path: Output video path (default: auto).
            **render_kwargs: Additional kwargs passed to Scene.render().

        Returns:
            The output file path.
        """
        config = config or PixelConfig.landscape()
        template = template_cls()

        # Validate
        errors = validate_data(data, template.schema)
        if errors:
            raise ValueError(
                f"Template data validation failed:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        # Apply defaults
        data = _apply_defaults(data, template.schema)

        # Build layout
        layout = Layout(config.canvas_width, config.canvas_height)

        # Create scene
        scene = _TemplateScene(template, data, config=config)
        template.setup(scene, config, layout)
        template.data = data

        # Render
        scene.render(output_path=output_path, **render_kwargs)
        return output_path

    @staticmethod
    def render_from_file(template_cls, data_path: str, config: PixelConfig = None,
                         output_path: str = None, **render_kwargs):
        """Render a template with data loaded from a JSON file.

        Args:
            template_cls: VideoTemplate subclass.
            data_path: Path to JSON data file.
            config: PixelConfig (default: landscape).
            output_path: Output video path.
            **render_kwargs: Additional kwargs passed to Scene.render().
        """
        with open(data_path, 'r') as f:
            data = json.load(f)

        return TemplateRunner.render(
            template_cls, data, config=config,
            output_path=output_path, **render_kwargs,
        )


# ═══════════════════════════════════════════════════════════
#  Built-in Templates
# ═══════════════════════════════════════════════════════════

class TitleCard(VideoTemplate):
    """Simple animated title card with subtitle.

    Data schema::

        {
            "title": "My Video Title",
            "subtitle": "Optional subtitle text",
            "duration": 3.0,
            "background": "#1D2B53",
            "title_color": "#FFEC27",
            "subtitle_color": "#C2C3C7"
        }
    """
    schema = {
        "type": "object",
        "required": ["title"],
        "properties": {
            "title": {"type": "string"},
            "subtitle": {"type": "string", "default": ""},
            "duration": {"type": "number", "default": 3.0, "minimum": 0.5},
            "background": {"type": "string", "default": "#1D2B53"},
            "title_color": {"type": "string", "default": "#FFEC27"},
            "subtitle_color": {"type": "string", "default": "#C2C3C7"},
        },
    }

    def construct(self, data):
        from pixelengine.text import PixelText
        from pixelengine.organic import OrganicFadeIn, OrganicFadeOut
        from pixelengine.camerafx import Vignette
        from pixelengine.lighting import AmbientLight

        self.scene.set_background(data["background"])
        self.scene.add_light(AmbientLight(intensity=0.3))
        self.scene.add_camera_fx(Vignette(intensity=0.4))

        cx, cy = self.L.center()

        title = PixelText(
            data["title"], x=cx, y=cy - 10,
            color=data["title_color"], scale=2, align="center",
        )
        self.scene.add(title)
        self.scene.play(OrganicFadeIn(title), duration=0.8)

        if data.get("subtitle"):
            sub = PixelText(
                data["subtitle"], x=cx, y=cy + 15,
                color=data["subtitle_color"], scale=1, align="center",
            )
            self.scene.add(sub)
            self.scene.play(OrganicFadeIn(sub), duration=0.5)

        self.scene.wait(data["duration"])
        self.scene.play(OrganicFadeOut(title), duration=0.5)


class ListReveal(VideoTemplate):
    """Animated bullet list reveal.

    Data schema::

        {
            "title": "Key Points",
            "items": ["First point", "Second point", "Third point"],
            "item_delay": 0.8,
            "background": "#1D2B53"
        }
    """
    schema = {
        "type": "object",
        "required": ["title", "items"],
        "properties": {
            "title": {"type": "string"},
            "items": {"type": "array"},
            "item_delay": {"type": "number", "default": 0.8, "minimum": 0.2},
            "hold_time": {"type": "number", "default": 2.0, "minimum": 0.5},
            "background": {"type": "string", "default": "#1D2B53"},
            "title_color": {"type": "string", "default": "#FFEC27"},
            "item_color": {"type": "string", "default": "#C2C3C7"},
        },
    }

    def construct(self, data):
        from pixelengine.text import PixelText
        from pixelengine.organic import OrganicFadeIn
        from pixelengine.camerafx import Vignette
        from pixelengine.lighting import AmbientLight

        self.scene.set_background(data["background"])
        self.scene.add_light(AmbientLight(intensity=0.3))
        self.scene.add_camera_fx(Vignette(intensity=0.3))

        # Title
        title = PixelText(
            data["title"],
            x=self.L.TITLE_ZONE.x, y=self.L.TITLE_ZONE.y,
            color=data["title_color"], scale=2, align="center",
        )
        self.scene.add(title)
        self.scene.play(OrganicFadeIn(title), duration=0.6)

        # Items
        start_y = self.L.MAIN_ZONE.y - self.L.MAIN_ZONE.height // 2 + 10
        for i, item_text in enumerate(data["items"]):
            text = f"• {item_text}" if isinstance(item_text, str) else f"• {item_text}"
            item = PixelText(
                text,
                x=self.L.SAFE_LEFT + 10,
                y=start_y + i * 16,
                color=data["item_color"], scale=1,
            )
            self.scene.add(item)
            self.scene.play(OrganicFadeIn(item), duration=0.4)
            self.scene.wait(data["item_delay"])

        self.scene.wait(data["hold_time"])


class ChartAnimation(VideoTemplate):
    """Animated bar chart from data.

    Data schema::

        {
            "title": "Sales by Quarter",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [120, 250, 180, 310],
            "bar_color": "#29ADFF",
            "background": "#1D2B53"
        }
    """
    schema = {
        "type": "object",
        "required": ["title", "labels", "values"],
        "properties": {
            "title": {"type": "string"},
            "labels": {"type": "array"},
            "values": {"type": "array"},
            "bar_color": {"type": "string", "default": "#29ADFF"},
            "background": {"type": "string", "default": "#1D2B53"},
            "hold_time": {"type": "number", "default": 3.0, "minimum": 0.5},
        },
    }

    def construct(self, data):
        from pixelengine.text import PixelText
        from pixelengine.mathobjects import BarChart
        from pixelengine.organic import OrganicFadeIn
        from pixelengine.construction import GrowFromEdge
        from pixelengine.camerafx import Vignette
        from pixelengine.lighting import AmbientLight

        self.scene.set_background(data["background"])
        self.scene.add_light(AmbientLight(intensity=0.3))
        self.scene.add_camera_fx(Vignette(intensity=0.3))

        # Title
        cx, _ = self.L.center()
        title = PixelText(
            data["title"],
            x=cx, y=self.L.TITLE_ZONE.y,
            color="#FFEC27", scale=2, align="center",
        )
        self.scene.add(title)
        self.scene.play(OrganicFadeIn(title), duration=0.6)

        # Chart
        chart = BarChart(
            values=data["values"],
            labels=data["labels"],
            x=self.L.MAIN_ZONE.x - self.L.MAIN_ZONE.width // 2 + 20,
            y=self.L.MAIN_ZONE.y + self.L.MAIN_ZONE.height // 2,
            bar_color=data["bar_color"],
        )
        self.scene.add(chart)
        self.scene.play(GrowFromEdge(chart, edge="bottom"), duration=1.5)
        self.scene.wait(data["hold_time"])


# ── Registry of built-in templates ──────────────────────────

BUILTIN_TEMPLATES = {
    "TitleCard": TitleCard,
    "ListReveal": ListReveal,
    "ChartAnimation": ChartAnimation,
}


# ── CLI entry point ─────────────────────────────────────────

def main():
    """CLI: python -m pixelengine.templates <TemplateName> --data <file.json>"""
    if len(sys.argv) < 2:
        print("Usage: python -m pixelengine.templates <TemplateName> --data <file.json>")
        print(f"\nBuilt-in templates: {', '.join(BUILTIN_TEMPLATES.keys())}")
        sys.exit(1)

    template_name = sys.argv[1]
    data_path = None
    output_path = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--data" and i + 1 < len(sys.argv):
            data_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if data_path is None:
        print("Error: --data <file.json> is required")
        sys.exit(1)

    # Find template
    if template_name in BUILTIN_TEMPLATES:
        template_cls = BUILTIN_TEMPLATES[template_name]
    else:
        print(f"Unknown template: {template_name}")
        print(f"Available: {', '.join(BUILTIN_TEMPLATES.keys())}")
        sys.exit(1)

    TemplateRunner.render_from_file(template_cls, data_path, output_path=output_path)


if __name__ == "__main__":
    main()
