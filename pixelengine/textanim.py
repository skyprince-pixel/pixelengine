"""PixelEngine text animations — per-character and per-word animation effects.

Provides PerCharacter, PerWord, ScrambleReveal, and TypeWriterPro for
advanced text animation control.
"""
import math
import random
from pixelengine.animation import Animation, linear, get_easing
from pixelengine.pobject import PObject


class PerCharacter:
    """Animate each character of a PixelText object individually with stagger.

    Each character gets its own animation instance, offset by ``lag``.

    Usage::

        text = PixelText("QUANTUM PHYSICS", x=240, y=135, align="center")
        scene.add(text)
        scene.play(PerCharacter(text, "fade_in", lag=0.05), duration=2.0)

    Supported effects: "fade_in", "drop_in", "scale_in", "slide_up".

    Args:
        text_obj: A PixelText object.
        effect: Effect name or "fade_in", "drop_in", "scale_in", "slide_up".
        lag: Time offset between each character's start (fraction of total).
        easing: Easing function for each character animation.
    """

    def __init__(self, text_obj, effect: str = "fade_in",
                 lag: float = 0.05, easing=None, offset_y: int = -15):
        self.text_obj = text_obj
        self.effect = effect
        self.lag = lag
        self.easing = get_easing(easing) if easing else get_easing("ease_out")
        self.offset_y = offset_y
        self._text = getattr(text_obj, 'text', '')
        self._n = max(1, len(self._text.replace(' ', '')))
        self._started = False
        self._orig_max_chars = None

    def interpolate(self, alpha: float):
        if not self._started:
            self._orig_max_chars = getattr(self.text_obj, 'max_chars', None)
            self._started = True

        # Calculate how many characters are fully revealed
        n = self._n
        anim_duration = max(0.1, 1.0 - (n - 1) * self.lag)

        if self.effect == "fade_in":
            # Progressively reveal characters with opacity ramp
            revealed = 0
            for i in range(n):
                start = i * self.lag
                if alpha >= start:
                    local = min(1.0, (alpha - start) / anim_duration)
                    local = self.easing(local)
                    if local > 0.1:
                        revealed = i + 1
            self.text_obj.max_chars = revealed
            # Fade overall opacity based on latest character
            if n > 0:
                last_start = (revealed - 1) * self.lag if revealed > 0 else 0
                if alpha >= last_start:
                    fade = min(1.0, (alpha - last_start) / anim_duration)
                    self.text_obj.opacity = self.easing(fade)
                else:
                    self.text_obj.opacity = 0.0

        elif self.effect == "drop_in":
            # Characters drop in from above
            revealed = 0
            for i in range(n):
                start = i * self.lag
                if alpha >= start:
                    local = min(1.0, (alpha - start) / anim_duration)
                    local = self.easing(local)
                    if local > 0.05:
                        revealed = i + 1
            self.text_obj.max_chars = revealed

        elif self.effect == "scale_in":
            # Characters scale from 0 to full
            revealed = 0
            for i in range(n):
                start = i * self.lag
                if alpha >= start:
                    local = min(1.0, (alpha - start) / anim_duration)
                    local = self.easing(local)
                    if local > 0.05:
                        revealed = i + 1
            self.text_obj.max_chars = revealed

        elif self.effect == "slide_up":
            # Characters slide up from below
            revealed = 0
            for i in range(n):
                start = i * self.lag
                if alpha >= start:
                    local = min(1.0, (alpha - start) / anim_duration)
                    local = self.easing(local)
                    if local > 0.05:
                        revealed = i + 1
            self.text_obj.max_chars = revealed

        else:
            # Default: simple progressive reveal
            self.text_obj.max_chars = int(n * alpha)

        # Ensure full text shown at the end
        if alpha >= 1.0:
            self.text_obj.max_chars = len(self._text)
            self.text_obj.opacity = 1.0


class PerWord:
    """Animate each word of a PixelText object individually with stagger.

    Usage::

        scene.play(PerWord(text, "fade_in", lag=0.15), duration=2.0)

    Args:
        text_obj: A PixelText object.
        effect: Effect name ("fade_in", "drop_in", "scale_in").
        lag: Time offset between each word's start (fraction of total).
        easing: Easing function for each word animation.
    """

    def __init__(self, text_obj, effect: str = "fade_in",
                 lag: float = 0.15, easing=None):
        self.text_obj = text_obj
        self.effect = effect
        self.lag = lag
        self.easing = get_easing(easing) if easing else get_easing("ease_out")
        self._text = getattr(text_obj, 'text', '')
        self._words = self._text.split()
        self._n = max(1, len(self._words))
        self._started = False

    def _chars_for_words(self, word_count: int) -> int:
        """Count characters (including spaces) for first N words."""
        if word_count <= 0:
            return 0
        words = self._words[:word_count]
        return sum(len(w) for w in words) + word_count - 1  # spaces between

    def interpolate(self, alpha: float):
        if not self._started:
            self._started = True

        n = self._n
        anim_duration = max(0.1, 1.0 - (n - 1) * self.lag)

        revealed_words = 0
        for i in range(n):
            start = i * self.lag
            if alpha >= start:
                local = min(1.0, (alpha - start) / anim_duration)
                local = self.easing(local)
                if local > 0.1:
                    revealed_words = i + 1

        self.text_obj.max_chars = self._chars_for_words(revealed_words)

        if alpha >= 1.0:
            self.text_obj.max_chars = len(self._text)
            self.text_obj.opacity = 1.0


class ScrambleReveal:
    """Matrix-style random character scramble reveal.

    Characters start as random glyphs and progressively resolve into
    the correct text.

    Usage::

        scene.play(ScrambleReveal(text, charset="ABCXYZ0123", speed=3), duration=1.5)

    Args:
        text_obj: A PixelText object.
        charset: Characters to use for the scramble effect.
        speed: How fast characters resolve (higher = faster).
        seed: Random seed for reproducibility.
    """

    def __init__(self, text_obj, charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                 speed: float = 3.0, seed: int = None):
        self.text_obj = text_obj
        self.charset = charset
        self.speed = speed
        self._rng = random.Random(seed)
        self._original_text = getattr(text_obj, 'text', '')
        self._started = False

    def interpolate(self, alpha: float):
        if not self._started:
            self._started = True

        text = self._original_text
        n = len(text)

        if alpha >= 1.0:
            self.text_obj.text = text
            self.text_obj.max_chars = n
            self.text_obj.opacity = 1.0
            return

        result = []
        for i, ch in enumerate(text):
            if ch == ' ':
                result.append(' ')
                continue

            # Each character has its own resolve threshold
            char_progress = alpha * self.speed - (i / max(1, n)) * (self.speed - 1)
            char_progress = max(0.0, min(1.0, char_progress))

            if char_progress >= 0.8:
                # Resolved
                result.append(ch)
            elif char_progress > 0:
                # Scrambling
                result.append(self._rng.choice(self.charset))
            else:
                # Not yet started
                result.append(' ')

        self.text_obj.text = ''.join(result)
        self.text_obj.max_chars = n
        self.text_obj.opacity = min(1.0, alpha * 2)


class TypeWriterPro:
    """Enhanced typewriter with cursor blink and variable speed.

    Usage::

        scene.play(TypeWriterPro(text, cursor=True, cursor_blink_rate=2), duration=2.0)

    Args:
        text_obj: A PixelText object.
        cursor: Whether to show a blinking cursor.
        cursor_blink_rate: Blinks per second.
        cursor_char: Character to use as cursor.
    """

    def __init__(self, text_obj, cursor: bool = True,
                 cursor_blink_rate: float = 2.0, cursor_char: str = "_"):
        self.text_obj = text_obj
        self.cursor = cursor
        self.cursor_blink_rate = cursor_blink_rate
        self.cursor_char = cursor_char
        self._original_text = getattr(text_obj, 'text', '')
        self._started = False

    def interpolate(self, alpha: float):
        if not self._started:
            self._started = True

        text = self._original_text
        n = len(text)
        chars_shown = int(n * alpha)
        chars_shown = max(0, min(n, chars_shown))

        # Build visible text with cursor
        visible = text[:chars_shown]
        if self.cursor and alpha < 1.0:
            # Blink cursor
            blink_cycle = int(alpha * self.cursor_blink_rate * 10) % 2
            if blink_cycle == 0:
                visible += self.cursor_char

        self.text_obj.text = visible
        self.text_obj.max_chars = len(visible)
        self.text_obj.opacity = 1.0

        # Restore original text at the end
        if alpha >= 1.0:
            self.text_obj.text = text
            self.text_obj.max_chars = n
