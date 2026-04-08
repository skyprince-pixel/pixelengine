"""PixelEngine caption/subtitle system — SRT/VTT generation and burn-in rendering.

Provides a CaptionTrack for recording timed text segments during construct(),
with export to .srt and .vtt sidecar files. Supports burned-in pixel text
captions and TikTok-style word-by-word highlighting.

Usage::

    from pixelengine.captions import CaptionTrack, CaptionStyle

    class MyScene(Scene):
        def construct(self):
            self.captions = CaptionTrack(self)

            self.captions.add("Welcome to PixelEngine!", duration=2.0)
            self.wait(2.0)

            self.captions.add("Let's build something cool.", duration=3.0)
            self.wait(3.0)

    scene = MyScene()
    scene.render()
    scene.captions.save_srt("output.srt")
    scene.captions.save_vtt("output.vtt")
"""
from dataclasses import dataclass, field
from typing import List, Optional
import os


@dataclass
class CaptionStyle:
    """Visual style for burned-in captions."""
    color: str = "#FFFFFF"
    background_color: str = "#000000"
    background_opacity: float = 0.6
    font_size: str = "5x7"
    scale: int = 1
    align: str = "center"
    max_width: int = 0  # 0 = auto (80% of canvas width)
    y_position: str = "lower_third"  # "lower_third", "bottom", "top", "center"
    word_highlight_color: str = "#FFEC27"  # For TikTok-style word highlighting


@dataclass
class Caption:
    """A single timed caption segment."""
    text: str
    start_time: float  # seconds
    end_time: float    # seconds
    style: CaptionStyle = field(default_factory=CaptionStyle)
    words: Optional[List[dict]] = None  # word-level timing: [{"word": str, "start": float, "end": float}]


def _format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_vtt_time(seconds: float) -> str:
    """Format seconds as VTT timestamp: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


class CaptionTrack:
    """Records timed caption segments and exports to subtitle formats.

    Attach to a Scene to record captions during construct(). After rendering,
    export to .srt or .vtt files, or use burn-in rendering.

    Usage::

        class MyScene(Scene):
            def construct(self):
                self.captions = CaptionTrack(self)
                self.captions.add("Hello world!", duration=2.0)
                self.wait(2.0)
                self.captions.add("Goodbye!", duration=1.5)
                self.wait(1.5)

        scene = MyScene()
        scene.render()
        scene.captions.save_srt("output.srt")

    Integration with voiceover::

        captions = CaptionTrack(scene)
        captions.add_voiceover("This is narrated text.", engine="kokoro")
        # Automatically: generates TTS, adds caption, holds frame for duration
    """

    def __init__(self, scene=None, style: CaptionStyle = None):
        self.scene = scene
        self.default_style = style or CaptionStyle()
        self._captions: List[Caption] = []
        self._burn_in_objects: list = []

    @property
    def captions(self) -> List[Caption]:
        """All recorded caption segments."""
        return list(self._captions)

    def add(self, text: str, duration: float = None, start: float = None,
            end: float = None, style: CaptionStyle = None,
            words: list = None) -> Caption:
        """Add a caption segment.

        Args:
            text: Caption text.
            duration: Duration in seconds (uses scene time for start if scene attached).
            start: Explicit start time in seconds.
            end: Explicit end time in seconds.
            style: Override style for this caption.
            words: Word-level timing list: [{"word": str, "start": float, "end": float}].

        Returns:
            The created Caption object.
        """
        if start is None and self.scene is not None:
            start = self.scene._current_time
        elif start is None:
            start = self._captions[-1].end_time if self._captions else 0.0

        if end is None and duration is not None:
            end = start + duration
        elif end is None:
            end = start + 2.0  # default 2 seconds

        caption = Caption(
            text=text,
            start_time=start,
            end_time=end,
            style=style or self.default_style,
            words=words,
        )
        self._captions.append(caption)
        return caption

    def add_voiceover(self, text: str, voice: str = None, speed: float = 1.0,
                      engine: str = "kokoro", style: CaptionStyle = None) -> Caption:
        """Generate TTS voiceover and add a synced caption.

        Combines play_voiceover() with automatic captioning. Holds the frame
        for the voiceover duration.

        Args:
            text: Text for voiceover and caption.
            voice: Voice name or reference wav.
            speed: TTS speed multiplier.
            engine: "kokoro" or "chatterbox".
            style: Override caption style.

        Returns:
            The created Caption object.
        """
        if self.scene is None:
            raise RuntimeError("CaptionTrack.add_voiceover() requires a scene")

        from pixelengine.voiceover import VoiceOver
        sfx, duration = VoiceOver.generate(text, voice=voice, speed=speed, engine=engine)
        self.scene.play_sound(sfx)

        caption = self.add(text, duration=duration, style=style)

        print(f"[PixelEngine] VoiceOver+Caption: '{text[:30]}...' ({duration:.2f}s)")
        self.scene.wait(duration)
        return caption

    # ── Export Formats ──────────────────────────────────────────

    def save_srt(self, path: str):
        """Export captions as SRT subtitle file.

        Args:
            path: Output file path (e.g. "output.srt").
        """
        lines = []
        for i, cap in enumerate(self._captions, 1):
            lines.append(str(i))
            lines.append(
                f"{_format_srt_time(cap.start_time)} --> {_format_srt_time(cap.end_time)}"
            )
            lines.append(cap.text)
            lines.append("")

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[PixelEngine] SRT saved: {path} ({len(self._captions)} captions)")

    def save_vtt(self, path: str):
        """Export captions as WebVTT subtitle file.

        Args:
            path: Output file path (e.g. "output.vtt").
        """
        lines = ["WEBVTT", ""]
        for i, cap in enumerate(self._captions, 1):
            lines.append(str(i))
            lines.append(
                f"{_format_vtt_time(cap.start_time)} --> {_format_vtt_time(cap.end_time)}"
            )
            lines.append(cap.text)
            lines.append("")

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[PixelEngine] VTT saved: {path} ({len(self._captions)} captions)")

    def save_json(self, path: str):
        """Export captions as JSON (useful for programmatic consumption).

        Args:
            path: Output file path (e.g. "captions.json").
        """
        import json
        data = []
        for cap in self._captions:
            entry = {
                "text": cap.text,
                "start": round(cap.start_time, 3),
                "end": round(cap.end_time, 3),
            }
            if cap.words:
                entry["words"] = cap.words
            data.append(entry)

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[PixelEngine] Captions JSON saved: {path}")

    def save_all(self, base_path: str):
        """Export captions in all formats (SRT + VTT + JSON).

        Args:
            base_path: Base path without extension (e.g. "outputs/scene/MyScene").
        """
        self.save_srt(f"{base_path}.srt")
        self.save_vtt(f"{base_path}.vtt")
        self.save_json(f"{base_path}.captions.json")

    # ── Burn-in Rendering ───────────────────────────────────────

    def create_burn_in(self, canvas_width: int, canvas_height: int):
        """Create PixelText objects for burn-in caption rendering.

        Returns a list of (Caption, PObject) pairs. Add the updater
        returned by ``burn_in_updater()`` to control visibility.

        Args:
            canvas_width: Scene canvas width.
            canvas_height: Scene canvas height.

        Returns:
            List of PObject caption display objects.
        """
        from pixelengine.text import PixelText
        from pixelengine.shapes import Rect

        objects = []
        for cap in self._captions:
            style = cap.style
            max_w = style.max_width if style.max_width > 0 else int(canvas_width * 0.8)

            # Position based on style
            if style.y_position == "lower_third":
                y = int(canvas_height * 0.78)
            elif style.y_position == "bottom":
                y = int(canvas_height * 0.88)
            elif style.y_position == "top":
                y = int(canvas_height * 0.08)
            elif style.y_position == "center":
                y = int(canvas_height * 0.5)
            else:
                y = int(canvas_height * 0.78)

            x = canvas_width // 2

            txt = PixelText(
                cap.text, x=x, y=y,
                color=style.color,
                scale=style.scale,
                align="center",
                font_size=style.font_size,
                max_width=max_w,
                shadow=True,
            )
            txt.visible = False
            txt.z_index = 999
            txt._caption_start = cap.start_time
            txt._caption_end = cap.end_time
            objects.append(txt)

        self._burn_in_objects = objects
        return objects

    def burn_in_updater(self):
        """Return an updater function that shows/hides burn-in captions based on time.

        Attach to any object via ``obj.add_updater(captions.burn_in_updater())``,
        or call directly in ``on_frame()``.

        Usage::

            captions = CaptionTrack(self)
            # ... add captions ...
            burn_in = captions.create_burn_in(self.config.canvas_width, self.config.canvas_height)
            for obj in burn_in:
                self.add(obj)

            # In on_frame or via updater:
            updater = captions.burn_in_updater()
            # Use in on_frame:
            def on_frame(self, t, dt):
                updater(None, dt, t=t)
        """
        objects = self._burn_in_objects

        def _update(obj, dt, t=None):
            if t is None:
                return
            for txt in objects:
                start = getattr(txt, '_caption_start', 0)
                end = getattr(txt, '_caption_end', 0)
                txt.visible = start <= t < end

        return _update

    # ── Utilities ───────────────────────────────────────────────

    @property
    def total_duration(self) -> float:
        """Total duration spanned by all captions."""
        if not self._captions:
            return 0.0
        return max(c.end_time for c in self._captions)

    @property
    def count(self) -> int:
        """Number of caption segments."""
        return len(self._captions)

    def get_caption_at(self, time: float) -> Optional[Caption]:
        """Get the active caption at a given time, or None."""
        for cap in self._captions:
            if cap.start_time <= time < cap.end_time:
                return cap
        return None

    def __repr__(self) -> str:
        return f"CaptionTrack({len(self._captions)} captions, {self.total_duration:.1f}s)"
