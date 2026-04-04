"""PixelEngine music -- musical staff notation for music education videos."""
from __future__ import annotations

import math
from PIL import Image, ImageDraw
from pixelengine.pobject import PObject
from pixelengine.color import parse_color
from pixelengine.text import PixelText


# =====================================================================
#  Note -- musical note data
# =====================================================================

class Note:
    """A musical note with pitch and duration.

    Stores the pitch name (e.g. ``"C4"``), the rhythmic duration
    (e.g. ``"quarter"``), and computes a vertical staff position
    expressed as semitone offset from middle C.

    Usage::

        n = Note("E4", "half")
        print(n.staff_position)  # 2
    """

    # Pitch positions on the staff (semitones from middle C)
    PITCHES: dict[str, int] = {
        "C4": 0, "D4": 1, "E4": 2, "F4": 3, "G4": 4, "A4": 5, "B4": 6,
        "C5": 7, "D5": 8, "E5": 9, "F5": 10, "G5": 11, "A5": 12, "B5": 13,
    }

    # Duration values in quarter-note beats
    DURATIONS: dict[str, float] = {
        "whole": 4.0,
        "half": 2.0,
        "quarter": 1.0,
        "eighth": 0.5,
        "sixteenth": 0.25,
    }

    def __init__(self, pitch: str = "C4", duration: str = "quarter"):
        self.pitch = pitch
        self.duration = duration
        self.staff_position: int = self.PITCHES.get(pitch, 0)
        self.beat_value: float = self.DURATIONS.get(duration, 1.0)

    def __repr__(self) -> str:
        return f"Note({self.pitch!r}, {self.duration!r})"


# =====================================================================
#  _StaffBuild -- progressive reveal animation
# =====================================================================

class _StaffBuild:
    """Animation that reveals MusicStaff notes from left to right.

    Created by :meth:`MusicStaff.animate_build` -- not instantiated
    directly.
    """

    def __init__(self, staff: "MusicStaff"):
        self._staff = staff
        self._started: bool = False

    def interpolate(self, raw_alpha: float) -> None:
        alpha = max(0.0, min(1.0, raw_alpha))
        if not self._started:
            self._staff._build_progress = 0.0
            self._started = True
        self._staff._build_progress = alpha


# =====================================================================
#  MusicStaff -- 5-line music staff with notes
# =====================================================================

class MusicStaff(PObject):
    """Musical staff notation display for music education.

    Draws the five horizontal staff lines, a simplified treble clef on
    the left, and note heads / stems / flags positioned according to
    pitch and sequence order.

    Usage::

        staff = MusicStaff(x=10, y=40, width=200)
        staff.add_note("C4", "quarter")
        staff.add_note("E4", "quarter")
        staff.add_note("G4", "half")
        scene.add(staff)
        scene.play(staff.animate_build(), duration=2.0)
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        line_spacing: int = 4,
        note_spacing: int = 16,
        color: str = "#5F574F",
        note_color: str = "#FFF1E8",
    ):
        super().__init__(x=x, y=y, color=color)
        self.width = width
        self.line_spacing = line_spacing
        self.note_spacing = note_spacing
        self.note_color = parse_color(note_color)
        self._notes: list[Note] = []
        self._build_progress: float = 1.0  # 0.0 = nothing, 1.0 = all shown

        # Staff geometry: 5 lines, 4 gaps
        self.height = 8 * self.line_spacing  # 5 lines = 4 gaps + 4 extra room
        self._clef_width = 12  # space reserved for the treble-clef symbol

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def add_note(self, pitch: str, duration: str = "quarter") -> "MusicStaff":
        """Append a note to the staff.

        Args:
            pitch: Note name, e.g. ``"C4"``, ``"G5"``.
            duration: Rhythmic value -- ``"whole"``, ``"half"``,
                      ``"quarter"``, ``"eighth"``, or ``"sixteenth"``.
        """
        self._notes.append(Note(pitch, duration))
        return self

    def animate_build(self) -> _StaffBuild:
        """Return an animation that reveals notes left-to-right."""
        return _StaffBuild(self)

    # ------------------------------------------------------------------
    #  Internal drawing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _draw_filled_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int,
                            r: int, color: tuple) -> None:
        """Draw a filled circle (note head)."""
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    @staticmethod
    def _draw_hollow_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int,
                            r: int, color: tuple) -> None:
        """Draw an outlined circle (half / whole note head)."""
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color)

    def _note_y(self, note: Note, staff_top: int) -> int:
        """Compute the Y centre of a note head on the staff.

        Middle B (B4, staff_position=6) sits on the middle (third) line.
        Each staff_position step moves half a line_spacing.
        """
        # Third line from top is the reference for B4 (position 6)
        mid_line_y = staff_top + 2 * self.line_spacing
        # Each step in staff_position moves up by half a line_spacing
        return mid_line_y - int((note.staff_position - 6) * self.line_spacing * 0.5)

    def _draw_clef(self, draw: ImageDraw.ImageDraw, x0: int, staff_top: int,
                   color: tuple) -> None:
        """Draw a simplified pixel-art treble clef symbol."""
        ls = self.line_spacing
        # A minimal treble clef: vertical line with a curl
        cx = x0 + 4
        # Vertical line spanning beyond the staff
        for dy in range(-ls, 4 * ls + ls + 1):
            draw.point((cx, staff_top + dy), fill=color)
        # Small curl at bottom (rightward bump)
        bottom = staff_top + 4 * ls
        for dx in range(1, 4):
            draw.point((cx + dx, bottom + dx), fill=color)
        draw.point((cx + 3, bottom + 2), fill=color)
        # Small curl at top (leftward bump)
        top = staff_top - ls
        for dx in range(1, 3):
            draw.point((cx - dx, top - dx), fill=color)
        draw.point((cx - 2, top), fill=color)
        # Dot at very top
        draw.point((cx, top - 3), fill=color)

    # ------------------------------------------------------------------
    #  Render
    # ------------------------------------------------------------------

    def render(self, canvas) -> None:
        if not self.visible:
            return

        staff_color = self.get_render_color()
        nc = (*self.note_color[:3], int(self.note_color[3] * self.opacity))
        ls = self.line_spacing

        # Extra vertical room for notes above / below staff
        v_pad = ls * 3
        img_h = 4 * ls + 2 * v_pad + 1
        img = Image.new("RGBA", (self.width, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        staff_top = v_pad  # y of the first staff line inside the image

        # -- 5 horizontal staff lines --------------------------------
        for i in range(5):
            ly = staff_top + i * ls
            draw.line([(0, ly), (self.width - 1, ly)], fill=staff_color)

        # -- Treble clef ---------------------------------------------
        self._draw_clef(draw, 1, staff_top, staff_color)

        # -- Notes ---------------------------------------------------
        note_start_x = self._clef_width + 6
        visible_count = max(0, int(len(self._notes) * self._build_progress + 0.5))

        for idx, note in enumerate(self._notes[:visible_count]):
            nx = note_start_x + idx * self.note_spacing
            if nx + 4 > self.width:
                break  # clip if beyond staff width

            ny = self._note_y(note, staff_top)
            head_r = max(1, ls // 2)

            # -- Note head ------------------------------------------
            if note.duration in ("whole", "half"):
                self._draw_hollow_circle(draw, nx, ny, head_r, nc)
            else:
                self._draw_filled_circle(draw, nx, ny, head_r, nc)

            # -- Stem (not for whole notes) -------------------------
            if note.duration != "whole":
                stem_len = ls * 3
                if note.staff_position >= 6:
                    # Stem goes down (note is on or above middle line)
                    sx = nx + head_r
                    for sy in range(ny, ny + stem_len + 1):
                        if 0 <= sy < img_h:
                            draw.point((sx, sy), fill=nc)
                else:
                    # Stem goes up
                    sx = nx - head_r
                    for sy in range(ny - stem_len, ny + 1):
                        if 0 <= sy < img_h:
                            draw.point((sx, sy), fill=nc)

            # -- Flag (eighth / sixteenth) --------------------------
            if note.duration in ("eighth", "sixteenth"):
                if note.staff_position >= 6:
                    fx = nx + head_r
                    fy = ny + ls * 3
                    for fi in range(ls):
                        draw.point((fx + fi + 1, fy - fi), fill=nc)
                    if note.duration == "sixteenth":
                        for fi in range(ls):
                            draw.point((fx + fi + 1, fy - fi - ls), fill=nc)
                else:
                    fx = nx - head_r
                    fy = ny - ls * 3
                    for fi in range(ls):
                        draw.point((fx + fi + 1, fy + fi), fill=nc)
                    if note.duration == "sixteenth":
                        for fi in range(ls):
                            draw.point((fx + fi + 1, fy + fi + ls), fill=nc)

            # -- Ledger lines for notes above / below the staff -----
            if ny < staff_top:
                # Above staff -- draw ledger lines downward to note
                lly = staff_top - ls
                while lly >= ny - 1:
                    draw.line([(nx - head_r - 2, lly), (nx + head_r + 2, lly)], fill=staff_color)
                    lly -= ls
            elif ny > staff_top + 4 * ls:
                # Below staff -- draw ledger lines upward to note
                lly = staff_top + 5 * ls
                while lly <= ny + 1:
                    draw.line([(nx - head_r - 2, lly), (nx + head_r + 2, lly)], fill=staff_color)
                    lly += ls

        canvas.blit(img, int(self.x), int(self.y) - v_pad)
