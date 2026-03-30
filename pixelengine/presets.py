"""PixelEngine Scene Presets — pre-built scene templates for common patterns.

Agents select a preset and fill in content, reducing boilerplate by ~60%.

Usage::

    from pixelengine.presets import TitleCardScene, RevealScene, ComparisonScene

    class Intro(TitleCardScene):
        title = "THE GOLDEN RATIO"
        subtitle = "Nature's Perfect Number"
        atmosphere = "dark"
        reveal_style = "cyberpunk"

    class Main(RevealScene):
        items = [
            {"type": "equation", "content": r"\\varphi = \\frac{1+\\sqrt{5}}{2}"},
            {"type": "text", "content": "≈ 1.618"},
        ]
        narration = "The golden ratio is approximately 1.618..."
"""
from pixelengine.cinematic import CinematicScene


class TitleCardScene(CinematicScene):
    """Pre-built title card scene with atmosphere, title, subtitle, and reveal.

    Class attributes to override:
        title: str — main title text
        subtitle: str — subtitle text
        atmosphere: str — "dark", "warm", "cool", "retro", "clean"
        reveal_style: str — "cyberpunk", "hero", "soft"
        title_color: str — hex color for title
        subtitle_color: str — hex color for subtitle
        hold_duration: float — seconds to hold after reveal
    """
    title = "TITLE"
    subtitle = ""
    atmosphere = "normal"
    reveal_style = "soft"
    title_color = "#FFEC27"
    subtitle_color = "#C2C3C7"
    hold_duration = 2.0

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.text import PixelText
        from pixelengine.group import VStack

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        self.setup_atmosphere(self.atmosphere)

        objects = []
        title_obj = PixelText(self.title, scale=2, color=self.title_color)
        title_obj.z_index = 10
        objects.append(title_obj)

        if self.subtitle:
            sub_obj = PixelText(self.subtitle, scale=1, color=self.subtitle_color)
            sub_obj.z_index = 10
            objects.append(sub_obj)

        stack = VStack(objects, spacing=15, align="center")
        stack.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y)
        self.add(stack)

        self.play_cinematic_reveal(objects, style=self.reveal_style, duration=1.5)
        self.wait(self.hold_duration)


class RevealScene(CinematicScene):
    """Progressive content reveal with narration.

    Class attributes to override:
        items: list[dict] — content items, each with "type" and "content" keys
            Supported types: "equation", "text", "shape"
        narration: str — voiceover text
        atmosphere: str — atmosphere preset (only set if not None)
        reveal_feel: str — "bouncy", "elastic", "gentle", "punchy", "floaty"
        item_spacing: int — pixels between items
    """
    items = []
    narration = ""
    atmosphere = None
    reveal_feel = "bouncy"
    item_spacing = 20

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.text import PixelText
        from pixelengine.group import VStack
        from pixelengine.organic import Cascade, OrganicFadeIn

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        if self.atmosphere:
            self.setup_atmosphere(self.atmosphere)

        objects = []
        for item in self.items:
            obj = self._build_item(item, L)
            if obj:
                objects.append(obj)

        if objects:
            stack = VStack(objects, spacing=self.item_spacing, align="center")
            stack.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y)
            self.add(stack)
            self.play(Cascade([OrganicFadeIn(o) for o in objects], feel=self.reveal_feel), duration=1.5)

        if self.narration:
            self.narrate(self.narration)

        self.wait(1.0)

    def _build_item(self, item, L):
        itype = item.get("type", "text")
        content = item.get("content", "")
        color = item.get("color", None)

        if itype == "equation":
            from pixelengine.mathtex import MathTex
            obj = MathTex(content, color=color or "#FFEC27")
            obj.z_index = 10
            return obj
        elif itype == "text":
            from pixelengine.text import PixelText
            obj = PixelText(content, scale=item.get("scale", 1), color=color or "#C2C3C7")
            obj.z_index = 10
            return obj
        elif itype == "shape":
            shape = item.get("shape", "circle")
            if shape == "circle":
                from pixelengine.shapes import Circle
                return Circle(radius=item.get("radius", 20), color=color or "#FF004D")
            else:
                from pixelengine.shapes import Rect
                return Rect(item.get("width", 40), item.get("height", 30), color=color or "#FF004D")
        return None


class ComparisonScene(CinematicScene):
    """Side-by-side comparison between two concepts.

    Class attributes to override:
        left: dict — {"label": str, "items": list[str], "color": str}
        right: dict — {"label": str, "items": list[str], "color": str}
        vs_text: str — text between columns (default "VS")
        narration: str — voiceover text
        atmosphere: str — atmosphere preset
    """
    left = {"label": "A", "items": [], "color": "#29ADFF"}
    right = {"label": "B", "items": [], "color": "#FF004D"}
    vs_text = "VS"
    narration = ""
    atmosphere = "normal"

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.text import PixelText
        from pixelengine.group import VStack, HStack
        from pixelengine.organic import Cascade, OrganicFadeIn
        from pixelengine.construction import Create

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        if self.atmosphere:
            self.setup_atmosphere(self.atmosphere)

        left_objs = [PixelText(self.left["label"], scale=2, color=self.left.get("color", "#29ADFF"))]
        for item in self.left.get("items", []):
            left_objs.append(PixelText(str(item), scale=1, color="#C2C3C7"))

        right_objs = [PixelText(self.right["label"], scale=2, color=self.right.get("color", "#FF004D"))]
        for item in self.right.get("items", []):
            right_objs.append(PixelText(str(item), scale=1, color="#C2C3C7"))

        left_stack = VStack(left_objs, spacing=10, align="center")
        right_stack = VStack(right_objs, spacing=10, align="center")
        vs_label = PixelText(self.vs_text, scale=1, color="#FFEC27")

        row = HStack([left_stack, vs_label, right_stack], spacing=20, align="center")
        row.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y)
        self.add(row)

        all_objs = left_objs + [vs_label] + right_objs
        self.play(Cascade([OrganicFadeIn(o) for o in all_objs], feel="bouncy"), duration=2.0)

        if self.narration:
            self.narrate(self.narration)
        self.wait(1.0)


class TimelineScene(CinematicScene):
    """Chronological events displayed on a timeline.

    Class attributes to override:
        events: list[dict] — [{"time": "1687", "label": "Newton's Laws"}, ...]
        narration: str — voiceover
        atmosphere: str — atmosphere preset
        timeline_color: str — color of the timeline line
    """
    events = []
    narration = ""
    atmosphere = "normal"
    timeline_color = "#29ADFF"

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.text import PixelText
        from pixelengine.shapes import Line, Circle
        from pixelengine.organic import Cascade, OrganicFadeIn
        from pixelengine.construction import Create

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        if self.atmosphere:
            self.setup_atmosphere(self.atmosphere)

        cx = L.MAIN_ZONE.x
        n = len(self.events)
        if n == 0:
            return

        y_start = L.MAIN_ZONE.y - L.MAIN_ZONE.height // 2 + 20
        y_end = L.MAIN_ZONE.y + L.MAIN_ZONE.height // 2 - 20
        spacing = (y_end - y_start) // max(n - 1, 1) if n > 1 else 0

        timeline = Line(cx, y_start - 10, cx, y_end + 10, color=self.timeline_color)
        timeline.z_index = 5
        self.add(timeline)
        self.play(Create(timeline), duration=0.8)

        all_objs = []
        for i, event in enumerate(self.events):
            y = y_start + i * spacing
            dot = Circle(radius=3, x=cx, y=y, color="#FFEC27")
            dot.z_index = 8
            self.add(dot)

            time_label = PixelText(str(event.get("time", "")), scale=1, color="#FFEC27")
            time_label.move_to(cx - 40, y)
            time_label.z_index = 10
            self.add(time_label)

            desc = PixelText(str(event.get("label", "")), scale=1, color="#C2C3C7")
            desc.move_to(cx + 40, y)
            desc.z_index = 10
            self.add(desc)

            all_objs.extend([dot, time_label, desc])

        self.play(Cascade([OrganicFadeIn(o) for o in all_objs], feel="gentle"), duration=2.0)

        if self.narration:
            self.narrate(self.narration)
        self.wait(1.0)


class PhysicsDemoScene(CinematicScene):
    """Physics simulation with narration.

    Class attributes to override:
        gravity: float — gravitational acceleration
        balls: list[dict] — [{"radius": 10, "color": "#FF004D", "bounce": 0.8, "x": 135, "y": 50}]
        sim_duration: float — simulation length in seconds
        narration: str — voiceover
        atmosphere: str — atmosphere preset
    """
    gravity = 200
    balls = [{"radius": 10, "color": "#FF004D", "bounce": 0.8}]
    sim_duration = 4.0
    narration = ""
    atmosphere = "normal"

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.physics import PhysicsWorld, PhysicsBody
        from pixelengine.shapes import Circle, Rect

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        if self.atmosphere:
            self.setup_atmosphere(self.atmosphere)

        cw, ch = self.config.canvas_width, self.config.canvas_height
        physics = self.enable_physics(gravity=self.gravity)

        floor = Rect(cw, 10, x=cw // 2, y=ch - 20, color="#29ADFF")
        floor_body = PhysicsBody(floor, mass=0)
        self.add(floor)
        physics.add_body(floor_body)

        for ball_cfg in self.balls:
            ball = Circle(
                radius=ball_cfg.get("radius", 10),
                x=ball_cfg.get("x", cw // 2),
                y=ball_cfg.get("y", 50),
                color=ball_cfg.get("color", "#FF004D"),
            )

            body = PhysicsBody(ball, mass=ball_cfg.get("mass", 1.0),
                               restitution=ball_cfg.get("bounce", 0.8))
            self.add(ball)
            physics.add_body(body)

        if self.narration:
            self.narrate(self.narration)

        self.wait(self.sim_duration)


class MathProofScene(CinematicScene):
    """Step-by-step equation derivation with progressive reveals.

    Class attributes to override:
        steps: list[str] — LaTeX strings for each step
        narrations: list[str] — voiceover for each step (optional, same length as steps)
        atmosphere: str
        step_duration: float — seconds per step reveal
    """
    steps = []
    narrations = []
    atmosphere = "normal"
    step_duration = 2.0

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.mathtex import MathTex
        from pixelengine.construction import Create
        from pixelengine.organic import OrganicFadeOut
        from pixelengine.sound import SoundFX

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        if self.atmosphere:
            self.setup_atmosphere(self.atmosphere)

        prev_eq = None
        for i, step in enumerate(self.steps):
            eq = MathTex(step, x=L.MAIN_ZONE.x, y=L.MAIN_ZONE.y, color="#FFEC27")
            eq.z_index = 10
            self.add(eq)

            if prev_eq:
                self.play(OrganicFadeOut(prev_eq), duration=0.3)
                self.remove(prev_eq)

            self.play(Create(eq), duration=self.step_duration, sound=SoundFX.dynamic("reveal"))

            if i < len(self.narrations) and self.narrations[i]:
                self.narrate(self.narrations[i])
            else:
                self.wait(1.0)

            prev_eq = eq

        self.wait(1.0)


class DataVizScene(CinematicScene):
    """Animated chart/graph scene.

    Class attributes to override:
        chart_type: str — "bar" (more types coming)
        values: list[float]
        labels: list[str]
        chart_color: str
        narration: str
        atmosphere: str
    """
    chart_type = "bar"
    values = [30, 70, 50, 90, 40]
    labels = ["A", "B", "C", "D", "E"]
    chart_color = "#29ADFF"
    narration = ""
    atmosphere = "normal"

    def construct(self):
        from pixelengine.layout import Layout
        from pixelengine.mathobjects import BarChart
        from pixelengine.construction import GrowFromEdge
        from pixelengine.sound import SoundFX

        L = Layout.portrait() if self.config.canvas_height > self.config.canvas_width else Layout.landscape()

        if self.atmosphere:
            self.setup_atmosphere(self.atmosphere)

        chart = BarChart(
            values=self.values, labels=self.labels,
            x=L.MAIN_ZONE.x, y=L.MAIN_ZONE.y,
            width=L.MAIN_ZONE.width - 40, height=L.MAIN_ZONE.height - 40,
            color=self.chart_color,
        )
        chart.z_index = 5
        self.add(chart)

        self.play(GrowFromEdge(chart, edge="bottom"), duration=2.0, sound=SoundFX.dynamic("reveal"))

        if self.narration:
            self.narrate(self.narration)
        self.wait(1.0)
