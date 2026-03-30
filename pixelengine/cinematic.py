"""PixelEngine Cinematic Macros & Scene Templates for AI Agents.

Provides CinematicScene, CleanScene, and EducationalTemplate subclasses
that encapsulate advanced lighting, particle bursts, camera shake routines,
voiceover sync, and physics setup into simple macro methods.
"""
from pixelengine.scene import Scene
from pixelengine.sound import SoundFX
from pixelengine.effects import ParticleBurst, GlitchTransition
from pixelengine.camerafx import ChromaticAberration, DepthOfField, Vignette
from pixelengine.organic import Cascade, OrganicFadeIn
from pixelengine.lighting import PointLight, AmbientLight


class CinematicScene(Scene):
    """An AI-friendly Scene that provides high-level 'magic' macros.
    
    Instead of manually orchestrating 6 different effects, simply call methods
    like `play_cinematic_reveal` to automatically generate premium visuals.
    
    Also provides convenience methods for common tasks:
    - `enable_physics()` — one-line physics world setup
    - `narrate()` — voiceover + synced animation in one call
    - `add_captions()` — auto-synced subtitles in LOWER_THIRD
    - `transition()` — easy scene transitions
    """

    def play_cinematic_reveal(self, objects, style="normal", duration=1.5):
        """Perform a highly complex reveal animation tailored by style.
        
        Args:
            objects: A list of objects or a single object to reveal.
            style: The thematic style ("normal", "cyberpunk", "soft", "hero").
                   Default is "normal" — a clean cascade with no extra FX.
            duration: The duration of the reveal.
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
            
        if style not in ("normal",):
            # Add basic vignette and DoF only for cinematic styles
            has_vignette = any(isinstance(fx, Vignette) for fx in self._camera_fx._effects)
            if not has_vignette:
                self.add_camera_fx(Vignette(intensity=0.5))

        if style == "cyberpunk":
            # 1. Add Chromatic Aberration
            chroma = ChromaticAberration(offset=4)
            self.add_camera_fx(chroma)
            # 2. Trigger particles and screen shake
            center_x = sum(o.x for o in objects) // len(objects)
            center_y = sum(o.y for o in objects) // len(objects)
            self.play(ParticleBurst.explode(self, x=center_x, y=center_y), duration=0.1, sound=SoundFX.dynamic("impact", intensity=0.8))
            self.camera.shake(intensity=10, duration=0.3)
            # 3. Add point light
            light = PointLight(x=center_x, y=center_y, radius=150, color="#FF004D", intensity=1.5)
            self.add_light(light)
            # 4. Glitch transition into Cascade organic reveal
            self.play(GlitchTransition(self, intensity=0.6), duration=0.3)
            self.play(Cascade([OrganicFadeIn(o) for o in objects], feel="punchy"), duration=duration - 0.4)
            # Turn off chroma after effect
            self.remove_camera_fx(chroma)

        elif style == "hero":
            # 1. Bright light
            center_x = sum(o.x for o in objects) // len(objects)
            center_y = sum(o.y for o in objects) // len(objects)
            light = PointLight(x=center_x, y=center_y, radius=200, color="#FFF1E8", intensity=2.0)
            self.add_light(light)
            # 2. Bouncy Cascade
            self.play(ParticleBurst.disperse(self, x=center_x, y=center_y), duration=0.2, sound=SoundFX.dynamic("reveal", intensity=1.0))
            self.play(Cascade([OrganicFadeIn(o) for o in objects], feel="bouncy", lag=0.15), duration=duration - 0.2)

        elif style == "normal":
            # Normal Cascade fade-in with no sound or extra effects
            self.play(Cascade([OrganicFadeIn(o) for o in objects], feel="floaty", lag=0.2), duration=duration)

        else: # "soft"
            # 1. Smooth cascade
            self.play(Cascade([OrganicFadeIn(o) for o in objects], feel="floaty", lag=0.2), duration=duration, sound=SoundFX.dynamic("wonder", intensity=0.6))

    # ── Convenience Helper Methods ──────────────────────────

    def enable_physics(self, gravity=200, bounds=None):
        """One-line physics world setup. The world auto-steps during wait/play.
        
        Args:
            gravity: Downward gravitational acceleration (pixels/s²). Default 200.
            bounds: (x_min, y_min, x_max, y_max) world bounds. Auto-detected from config.
        
        Returns:
            The PhysicsWorld instance for adding bodies.
        
        Usage::
        
            physics = self.enable_physics(gravity=200)
            body = PhysicsBody(ball, mass=1.0, restitution=0.8)
            physics.add_body(body)
        """
        from pixelengine.physics import PhysicsWorld
        if bounds is None:
            bounds = (0, 0, self.config.canvas_width, self.config.canvas_height)
        self.physics = PhysicsWorld(gravity_y=gravity, bounds=bounds)
        return self.physics

    def narrate(self, text, animate=None, voice=None, engine="kokoro", sfx_context=None):
        """Voiceover + synced animation in one call.
        
        Pre-generates the speech, then plays the given animations synced
        to the exact voiceover duration. Much simpler than the manual
        VoiceOver.generate() + self.play() pattern.
        
        Args:
            text: The text to speak.
            animate: A single animation or list of animations to play during speech.
                     If None, just plays the voiceover with a wait.
            voice: Optional voice name or reference path.
            engine: TTS engine ("kokoro" or "chatterbox").
            sfx_context: Optional SoundFX context like "reveal" to play alongside.
        
        Usage::
        
            self.narrate("Gravity pulls objects downward.",
                         animate=OrganicMoveTo(ball, x=135, y=400, feel="heavy"))
        """
        from pixelengine.voiceover import VoiceOver
        sfx, dur = VoiceOver.generate(text, voice=voice, engine=engine)

        if sfx_context:
            context_sfx = SoundFX.dynamic(sfx_context)
            self.play_sound(context_sfx)

        if animate is None:
            self.play_sound(sfx)
            self.wait(dur)
        else:
            if not isinstance(animate, (list, tuple)):
                animate = [animate]
            from pixelengine.animation import AnimationGroup
            self.play(AnimationGroup(*animate), duration=dur, sound=sfx)

    def add_captions(self, text, zone="LOWER_THIRD"):
        """Add auto-synced subtitles using DynamicCaption.
        
        Args:
            text: The full subtitle text.
            zone: Layout zone name. Default "LOWER_THIRD".
        
        Returns:
            The DynamicCaption object (call self.play(cap.track(), duration=X)).
        
        Usage::
        
            cap = self.add_captions("Look at this beautiful 3D cube!")
            sfx, dur = VoiceOver.generate("Look at this beautiful 3D cube!")
            self.play(cap.track(), duration=dur, sound=sfx)
        """
        from pixelengine.layout import Layout
        from pixelengine.textanim import DynamicCaption

        # Auto-detect layout from config
        if self.config.canvas_height > self.config.canvas_width:
            L = Layout.portrait()
        else:
            L = Layout.landscape()

        z = getattr(L, zone, L.LOWER_THIRD)
        cap = DynamicCaption(text, x=z.x, y=z.y)
        cap.z_index = 20
        self.add(cap)
        return cap

    def transition(self, style="glitch", intensity=0.7, duration=0.5):
        """Easy scene transition between logical sections.
        
        Args:
            style: "glitch", "shatter", "pixelate", "crossfade", or "dissolve".
            intensity: Effect strength (0.0–1.0).
            duration: Transition duration in seconds.
        
        Usage::
        
            # ... end of scene 1 ...
            self.transition("glitch")
            # ... start of scene 2 ...
        """
        from pixelengine.effects import (
            GlitchTransition, ShatterTransition, PixelateTransition,
            CrossDissolve, DissolveTransition,
        )

        style_map = {
            "glitch": lambda: GlitchTransition(self, intensity=intensity),
            "shatter": lambda: ShatterTransition(self, pieces=max(5, int(20 * intensity))),
            "pixelate": lambda: PixelateTransition(self),
            "crossfade": lambda: CrossDissolve(self),
            "dissolve": lambda: DissolveTransition(self),
        }

        anim_fn = style_map.get(style, style_map["glitch"])
        self.play(anim_fn(), duration=duration, sound=SoundFX.dynamic("transition"))

    def setup_atmosphere(self, style="dark", gradient=True, grid=True):
        """One-call atmosphere setup: background, lighting, camera FX.
        
        Args:
            style: "dark" (navy/black), "warm" (amber tones), "cool" (blue tones),
                   "retro" (CRT scanlines), "clean" (minimal white).
            gradient: Whether to add a gradient background.
            grid: Whether to add a subtle background grid.
        
        Usage::
        
            self.setup_atmosphere("dark")
        """
        from pixelengine.shapes import Rect
        from pixelengine.texture import GradientTexture
        from pixelengine.effects import Grid
        from pixelengine.shaders import CRTScanlines, ColorGrade

        cw, ch = self.config.canvas_width, self.config.canvas_height
        cx, cy = cw // 2, ch // 2

        presets = {
            "dark": {
                "bg": "#0B0C10", "grad": ("#0B0C10", "#1F2833"),
                "accent": "#29ADFF", "tint": "#FFF1E8", "ambient": 0.25,
            },
            "warm": {
                "bg": "#1A0A00", "grad": ("#1A0A00", "#3D1C02"),
                "accent": "#FFEC27", "tint": "#FFD4A0", "ambient": 0.3,
            },
            "cool": {
                "bg": "#0A0A2A", "grad": ("#0A0A2A", "#1A1A4A"),
                "accent": "#7DF9FF", "tint": "#E0F0FF", "ambient": 0.2,
            },
            "retro": {
                "bg": "#1D2B53", "grad": ("#1D2B53", "#29366F"),
                "accent": "#FF004D", "tint": "#FFF1E8", "ambient": 0.2,
            },
            "normal": {
                "bg": "#0B0C10", "grad": ("#0B0C10", "#1F2833"),
                "accent": "#29ADFF", "tint": None, "ambient": 1.0,
            },
            "clean": {
                "bg": "#EAEAEA", "grad": ("#F5F5F5", "#DCDCDC"),
                "accent": "#FF004D", "tint": None, "ambient": 1.0,
            },
        }

        p = presets.get(style, presets["dark"])
        self.set_background(p["bg"])

        if gradient:
            bg_rect = Rect(cw, ch, x=0, y=0, color="#FFFFFF")
            bg_rect.fill_texture = GradientTexture(
                direction="diagonal", color1=p["grad"][0], color2=p["grad"][1]
            )
            bg_rect.z_index = -10
            self.add(bg_rect)

        if style != "normal":
            if grid and style != "clean":
                g = Grid(cell_size=20, canvas_width=cw, canvas_height=ch, color="#FFFFFF")
                g.opacity = 0.04
                g.z_index = -9
                self.add(g)

            # Camera FX
            self.add_camera_fx(Vignette(intensity=0.45))
            if p["tint"]:
                from pixelengine.color import parse_color as _pc
                tint_rgb = _pc(p["tint"])[:3]
                self.add_camera_fx(ColorGrade(preset=None, tint=tint_rgb, strength=0.12))

            if style == "retro":
                self.add_camera_fx(CRTScanlines(line_spacing=2, darkness=0.25))

            # Lighting
            self.add_light(AmbientLight(intensity=p["ambient"]))
            self._accent_light = PointLight(
                x=cx, y=cy, radius=int(max(cw, ch) * 0.55),
                color=p["accent"], intensity=1.2
            )
            self.add_light(self._accent_light)
        else:
            # "normal" mode: skip lighting entirely for maximum performance
            pass


class CleanScene(Scene):
    """An AI-friendly Scene that prioritizes a minimalist pixel-art style.
    
    This class omits high-overhead lighting passes and ChromaticAberration,
    instead prioritizing pristine, high-resolution layout and gentle organic transitions.
    Requires use of `PixelConfig.high_res_portrait()` or equivalent for best results.
    """

    def play_clean_reveal(self, objects, duration=1.5):
        """Reveal objects with soft smoothing, no heavy VFX, and piano audio.
        
        Args:
            objects: A list of objects or a single object to reveal.
            duration: The duration of the reveal.
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
            
        # Play a smooth piano arpeggio dynamically
        self.play_sound(SoundFX.piano_note("E4"))
        self.play_sound(SoundFX.piano_note("G4"), at=self._current_time + 0.1)
        self.play_sound(SoundFX.piano_note("C5"), at=self._current_time + 0.2)
        
        # Use a buttery-smooth gentle organic cascade without light scattering or screen shake
        self.play(
            Cascade([OrganicFadeIn(o) for o in objects], feel="floaty", lag=0.2), 
            duration=duration
        )
