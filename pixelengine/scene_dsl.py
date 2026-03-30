"""PixelEngine Declarative Scene DSL — zero-coordinate scene building for AI agents.

Instead of writing imperative construct() code with manual coordinate math,
agents describe scenes as structured ``slide()`` declarations. The ``SceneBuilder``
compiles these into the correct sequence of PixelEngine API calls.

Usage::

    from pixelengine import SceneBuilder, slide, equation, text_block, physics_sim

    class MyShort(CinematicScene):
        def construct(self):
            SceneBuilder(self).run([
                slide("intro",
                    atmosphere="dark",
                    title="THE GOLDEN RATIO",
                    subtitle="Nature's Perfect Number",
                    reveal="cyberpunk",
                    narration="Did you know the golden ratio appears everywhere?",
                ),
                slide("explain",
                    content=[
                        equation(r"\\varphi = \\frac{1+\\sqrt{5}}{2}"),
                        text_block("≈ 1.618...", style="highlight"),
                    ],
                    narration="Phi equals one plus root five, divided by two.",
                    transition="glitch",
                ),
            ])
"""


# ── Slide content descriptors ──────────────────────────────

class _ContentItem:
    """Base class for declarative content items within a slide."""
    kind = "base"

    def __init__(self, **kwargs):
        self.params = kwargs


class equation(_ContentItem):  # noqa: N801 — lowercase for DSL ergonomics
    """A LaTeX equation to render with MathTex.

    Usage::

        equation(r"E = mc^2", color="#FFEC27")
    """
    kind = "equation"

    def __init__(self, tex: str, color: str = "#FFEC27", scale: float = 1.0):
        super().__init__(tex=tex, color=color, scale=scale)


class text_block(_ContentItem):  # noqa: N801
    """A text block to render with PixelText.

    Usage::

        text_block("Hello World", style="highlight")
    """
    kind = "text"

    def __init__(self, text: str, color: str = None, scale: float = 1,
                 style: str = "default"):
        # Style presets
        style_colors = {
            "default": "#C2C3C7",
            "highlight": "#FFEC27",
            "accent": "#29ADFF",
            "success": "#00E436",
            "danger": "#FF004D",
            "muted": "#5F574F",
        }
        if color is None:
            color = style_colors.get(style, "#C2C3C7")
        super().__init__(text=text, color=color, scale=scale, style=style)


class shape_item(_ContentItem):  # noqa: N801
    """A shape (circle, rect, etc.) to add to the scene.

    Usage::

        shape_item("circle", radius=20, color="#FF004D")
        shape_item("rect", width=40, height=30, color="#00E436")
    """
    kind = "shape"

    def __init__(self, shape_type: str = "circle", **kwargs):
        super().__init__(shape_type=shape_type, **kwargs)


class object_3d(_ContentItem):  # noqa: N801
    """A 3D object to render.

    Usage::

        object_3d("cube", size=40, color="#FF004D", orbit=True)
    """
    kind = "3d"

    def __init__(self, obj_type: str = "cube", orbit: bool = False,
                 orbit_degrees: float = 360, **kwargs):
        super().__init__(obj_type=obj_type, orbit=orbit,
                         orbit_degrees=orbit_degrees, **kwargs)


class chart_item(_ContentItem):  # noqa: N801
    """A chart/data visualization.

    Usage::

        chart_item("bar", values=[30, 70, 50], labels=["A", "B", "C"])
    """
    kind = "chart"

    def __init__(self, chart_type: str = "bar", values: list = None,
                 labels: list = None, color: str = "#29ADFF", **kwargs):
        super().__init__(chart_type=chart_type, values=values or [],
                         labels=labels or [], color=color, **kwargs)


class vector_item(_ContentItem):  # noqa: N801
    """A vector graphic (VCircle, VRect, etc.).

    Usage::

        vector_item("circle", radius=30, color="#00E436")
    """
    kind = "vector"

    def __init__(self, vtype: str = "circle", **kwargs):
        super().__init__(vtype=vtype, **kwargs)


class physics_sim(_ContentItem):  # noqa: N801
    """A physics simulation setup.

    Usage::

        physics_sim(gravity=200, objects=[
            {"type": "ball", "radius": 10, "color": "#FF004D", "bounce": 0.8},
            {"type": "floor", "y": 450},
        ])
    """
    kind = "physics"

    def __init__(self, gravity: float = 200, objects: list = None,
                 duration: float = 4.0):
        super().__init__(gravity=gravity, objects=objects or [], duration=duration)


class custom_content(_ContentItem):  # noqa: N801
    """Escape hatch: provide a raw callback for custom imperative code.

    Usage::

        custom_content(callback=lambda scene, L: scene.play(Create(my_obj), duration=1.0))
    """
    kind = "custom"

    def __init__(self, callback=None):
        super().__init__(callback=callback)


# ── Slide descriptor ───────────────────────────────────────


class slide:  # noqa: N801 — lowercase for DSL ergonomics
    """Describes a single visual segment / logical scene.

    Args:
        name: Identifier for the slide (for debugging and checkpoint).
        atmosphere: Optional atmosphere preset ("dark", "warm", "cool", "retro", "clean").
                    Only applied on the first slide that sets it.
        title: Optional title text for TITLE_ZONE.
        subtitle: Optional subtitle text for SUBTITLE_ZONE.
        content: List of _ContentItem descriptors (equation, text_block, etc.).
        reveal: Reveal style ("cyberpunk", "hero", "soft") or None for Cascade.
        narration: Text to speak via TTS (synced with animations).
        transition: Transition effect to play AFTER this slide
                    ("glitch", "shatter", "pixelate", "crossfade", "dissolve").
        duration: Override duration for this slide's main content phase.
        wait: Additional wait time after all content/narration.
        background_color: Override background color for this slide.
        custom_setup: Optional callback(scene, layout) for imperative customization.
        custom_teardown: Optional callback(scene, layout) for cleanup after slide.
    """

    def __init__(self, name: str, *, atmosphere: str = "normal", title: str = None,
                 subtitle: str = None, content: list = None, reveal: str = None,
                 narration: str = None, transition: str = None,
                 duration: float = None, wait: float = 0.5,
                 background_color: str = None, custom_setup=None,
                 custom_teardown=None):
        self.name = name
        self.atmosphere = atmosphere
        self.title = title
        self.subtitle = subtitle
        self.content = content or []
        self.reveal = reveal
        self.narration = narration
        self.transition = transition
        self.duration = duration
        self.wait = wait
        self.background_color = background_color
        self.custom_setup = custom_setup
        self.custom_teardown = custom_teardown


# ── SceneBuilder — compiles slides into construct() calls ──


class SceneBuilder:
    """Compiles a list of ``slide`` descriptors into PixelEngine API calls.

    Usage::

        class MyScene(CinematicScene):
            def construct(self):
                SceneBuilder(self).run([
                    slide("intro", title="HELLO", atmosphere="dark"),
                    slide("main", content=[equation(r"E=mc^2")], narration="..."),
                ])
    """

    def __init__(self, scene):
        """
        Args:
            scene: The Scene (or CinematicScene) instance to build into.
        """
        self.scene = scene
        self._layout = None
        self._atmosphere_set = False
        self._created_objects = []  # Track objects for cleanup between slides

    def _get_layout(self):
        """Auto-detect layout from scene config."""
        if self._layout is None:
            from pixelengine.layout import Layout
            cfg = self.scene.config
            if cfg.canvas_height > cfg.canvas_width:
                self._layout = Layout.portrait()
            else:
                self._layout = Layout.landscape()
        return self._layout

    def run(self, slides: list):
        """Execute all slides sequentially.

        Args:
            slides: List of ``slide`` descriptor objects.
        """
        for i, s in enumerate(slides):
            print(f"[SceneBuilder] Building slide {i+1}/{len(slides)}: '{s.name}'")
            self._build_slide(s, is_first=(i == 0), is_last=(i == len(slides) - 1))

    def _build_slide(self, s: slide, is_first: bool = False, is_last: bool = False):
        """Compile a single slide into scene API calls."""
        L = self._get_layout()
        scene = self.scene

        # ── 1. Background / Atmosphere ──
        if s.background_color:
            scene.set_background(s.background_color)

        if s.atmosphere and not self._atmosphere_set:
            if hasattr(scene, 'setup_atmosphere'):
                scene.setup_atmosphere(s.atmosphere)
            self._atmosphere_set = True

        # ── 2. Custom setup callback ──
        if s.custom_setup:
            s.custom_setup(scene, L)

        # ── 3. Build content objects ──
        slide_objects = []

        # Title
        if s.title:
            from pixelengine.text import PixelText
            title_obj = PixelText(s.title, scale=2, color="#FFEC27")
            title_obj.z_index = 10
            slide_objects.append(("title", title_obj))

        # Subtitle
        if s.subtitle:
            from pixelengine.text import PixelText
            sub_obj = PixelText(s.subtitle, scale=1, color="#C2C3C7")
            sub_obj.z_index = 10
            slide_objects.append(("subtitle", sub_obj))

        # Content items
        content_objects = []
        physics_items = []
        for item in s.content:
            built = self._build_content_item(item, L)
            if built is not None:
                if item.kind == "physics":
                    physics_items.append((item, built))
                elif item.kind == "custom":
                    # Custom callbacks handled separately
                    pass
                else:
                    content_objects.append(built)

        # ── 4. Layout with VStack ──
        all_visual_objects = []
        for _, obj in slide_objects:
            all_visual_objects.append(obj)
        all_visual_objects.extend(content_objects)

        if all_visual_objects:
            from pixelengine.group import VStack
            stack = VStack(all_visual_objects, spacing=15, align="center")
            stack.move_to(L.MAIN_ZONE.x, L.MAIN_ZONE.y)
            scene.add(stack)
            self._created_objects.append(stack)

        # ── 5. Reveal animation ──
        if all_visual_objects:
            if s.reveal and hasattr(scene, 'play_cinematic_reveal'):
                scene.play_cinematic_reveal(all_visual_objects, style=s.reveal,
                                            duration=s.duration or 1.5)
            else:
                if hasattr(scene, 'play_cinematic_reveal'):
                    scene.play_cinematic_reveal(all_visual_objects, style="normal",
                                                duration=s.duration or 1.5)
                else:
                    from pixelengine.organic import Cascade, OrganicFadeIn
                    scene.play(
                        Cascade([OrganicFadeIn(o) for o in all_visual_objects],
                                feel="floaty"),
                        duration=s.duration or 1.5,
                    )

        # ── 6. Physics simulation ──
        for item, built_objects in physics_items:
            self._run_physics(item, built_objects, L)

        # ── 7. Custom content callbacks ──
        for item in s.content:
            if item.kind == "custom" and item.params.get("callback"):
                item.params["callback"](scene, L)

        # ── 8. Narration (synced with wait) ──
        if s.narration:
            if hasattr(scene, 'narrate'):
                scene.narrate(s.narration)
            else:
                scene.play_voiceover(s.narration)

        # ── 9. Wait ──
        if s.wait > 0:
            scene.wait(s.wait)

        # ── 10. Custom teardown ──
        if s.custom_teardown:
            s.custom_teardown(scene, L)

        # ── 11. Transition to next slide ──
        if s.transition and not is_last:
            if hasattr(scene, 'transition'):
                scene.transition(s.transition)
            else:
                from pixelengine.effects import GlitchTransition
                scene.play(GlitchTransition(scene, intensity=0.7), duration=0.5)

        # ── 12. Clean up slide objects for next slide ──
        self._cleanup_slide()

    def _build_content_item(self, item: _ContentItem, L):
        """Build a single content item into a PObject."""
        p = item.params

        if item.kind == "equation":
            from pixelengine.mathtex import MathTex
            obj = MathTex(p["tex"], color=p.get("color", "#FFEC27"))
            obj.z_index = 10
            return obj

        elif item.kind == "text":
            from pixelengine.text import PixelText
            obj = PixelText(p["text"], scale=p.get("scale", 1),
                            color=p.get("color", "#C2C3C7"))
            obj.z_index = 10
            return obj

        elif item.kind == "shape":
            shape_type = p.get("shape_type", "circle")
            color = p.get("color", "#FF004D")
            if shape_type == "circle":
                from pixelengine.shapes import Circle
                obj = Circle(radius=p.get("radius", 20), color=color)
            elif shape_type == "rect":
                from pixelengine.shapes import Rect
                obj = Rect(p.get("width", 40), p.get("height", 30), color=color)
            elif shape_type == "triangle":
                from pixelengine.shapes import Triangle
                s_size = p.get("size", 30)
                # Generate equilateral triangle points from size
                obj = Triangle([(0, 0), (s_size, 0), (s_size // 2, -s_size)], color=color)
            else:
                from pixelengine.shapes import Rect
                obj = Rect(40, 30, color=color)
            obj.z_index = 5
            return obj

        elif item.kind == "3d":
            obj_type = p.get("obj_type", "cube")
            color = p.get("color", "#FF004D")
            size = p.get("size", 40)
            if obj_type == "cube":
                from pixelengine.objects3d import Cube3D
                obj = Cube3D(size=size, color=color)
            elif obj_type == "sphere":
                from pixelengine.objects3d import Sphere3D
                obj = Sphere3D(radius=size // 2, color=color)
            elif obj_type == "pyramid":
                from pixelengine.objects3d import Pyramid3D
                obj = Pyramid3D(base=size, color=color)
            else:
                from pixelengine.objects3d import Cube3D
                obj = Cube3D(size=size, color=color)
            obj.z_index = 5

            # Store orbit flag for later use
            obj._dsl_orbit = p.get("orbit", False)
            obj._dsl_orbit_degrees = p.get("orbit_degrees", 360)
            return obj

        elif item.kind == "chart":
            chart_type = p.get("chart_type", "bar")
            if chart_type == "bar":
                from pixelengine.mathobjects import BarChart
                obj = BarChart(
                    values=p.get("values", [30, 70, 50]),
                    labels=p.get("labels", []),
                    width=p.get("width", 200),
                    height=p.get("height", 120),
                    color=p.get("color", "#29ADFF"),
                )
            else:
                from pixelengine.mathobjects import BarChart
                obj = BarChart(values=p.get("values", [30, 70, 50]),
                               color=p.get("color", "#29ADFF"))
            obj.z_index = 5
            return obj

        elif item.kind == "vector":
            vtype = p.get("vtype", "circle")
            color = p.get("color", "#00E436")
            if vtype == "circle":
                from pixelengine.vector import VCircle
                obj = VCircle(radius=p.get("radius", 30), color=color,
                              fill_color=p.get("fill_color", None))
            elif vtype == "rect":
                from pixelengine.vector import VRect
                obj = VRect(p.get("width", 60), p.get("height", 40), color=color)
            elif vtype == "arrow":
                from pixelengine.vector import VArrow
                obj = VArrow(dx=p.get("dx", 50), dy=p.get("dy", 0), color=color)
            else:
                from pixelengine.vector import VCircle
                obj = VCircle(radius=30, color=color)
            obj.z_index = 5
            return obj

        elif item.kind == "physics":
            # Physics is handled separately in _run_physics
            return item.params.get("objects", [])

        elif item.kind == "custom":
            # Custom items are callback-based, no object returned
            return None

        return None

    def _run_physics(self, item, built_objects, L):
        """Set up and run a physics simulation."""
        scene = self.scene
        p = item.params
        gravity = p.get("gravity", 200)
        duration = p.get("duration", 4.0)

        from pixelengine.physics import PhysicsWorld, PhysicsBody
        from pixelengine.shapes import Circle, Rect

        cw = scene.config.canvas_width
        ch = scene.config.canvas_height
        physics = PhysicsWorld(gravity_y=gravity, bounds=(0, 0, cw, ch))
        scene.physics = physics

        objects_cfg = p.get("objects", [])
        for obj_cfg in objects_cfg:
            if isinstance(obj_cfg, dict):
                obj_type = obj_cfg.get("type", "ball")
                if obj_type == "ball":
                    ball = Circle(
                        radius=obj_cfg.get("radius", 10),
                        x=obj_cfg.get("x", L.MAIN_ZONE.x),
                        y=obj_cfg.get("y", 50),
                        color=obj_cfg.get("color", "#FF004D"),
                    )
                    body = PhysicsBody(
                        ball,
                        mass=obj_cfg.get("mass", 1.0),
                        restitution=obj_cfg.get("bounce", 0.8),
                    )
                    scene.add(ball)
                    physics.add_body(body)
                    self._created_objects.append(ball)

                elif obj_type == "floor":
                    floor = Rect(
                        cw, 10,
                        x=cw // 2,
                        y=obj_cfg.get("y", ch - 30),
                        color=obj_cfg.get("color", "#29ADFF"),
                    )
                    floor_body = PhysicsBody(floor, mass=0)
                    scene.add(floor)
                    physics.add_body(floor_body)
                    self._created_objects.append(floor)

                elif obj_type == "wall":
                    wall = Rect(
                        10, obj_cfg.get("height", ch),
                        x=obj_cfg.get("x", 0),
                        y=ch // 2,
                        color=obj_cfg.get("color", "#5F574F"),
                    )
                    wall_body = PhysicsBody(wall, mass=0)
                    scene.add(wall)
                    physics.add_body(wall_body)
                    self._created_objects.append(wall)

        scene.wait(duration)

    def _cleanup_slide(self):
        """Remove objects added by the previous slide."""
        for obj in self._created_objects:
            self.scene.remove(obj)
        self._created_objects.clear()
