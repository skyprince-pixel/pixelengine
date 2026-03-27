"""PixelEngine sound — procedural high-quality sound effect synthesis.

All sounds are generated purely from math (sine, square, noise, etc.)
using NumPy. No external audio files needed. Sounds are mixed into a
timeline and muxed into the final MP4 via ffmpeg.

Usage::

    # Manual sound placement
    scene.play_sound(SoundFX.coin(), at=2.5)

    # Auto-sounds (enabled by default)
    scene.auto_sound = True  # TypeWriter → typing sound, etc.
"""
import math
import struct
import wave
import io
import os
import subprocess
import tempfile
import numpy as np


SAMPLE_RATE = 48000  # High-quality audio (48kHz CD-quality)


# ═══════════════════════════════════════════════════════════
#  Waveform Generators
# ═══════════════════════════════════════════════════════════

def _sine(freq: float, duration: float, volume: float = 0.5,
          fade_out: bool = True) -> np.ndarray:
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * volume
    if fade_out:
        envelope = np.linspace(1.0, 0.0, len(wave))
        wave *= envelope
    return wave


def _square(freq: float, duration: float, volume: float = 0.3,
            duty: float = 0.5, fade_out: bool = True) -> np.ndarray:
    """Generate a square wave (classic 8-bit sound)."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * freq * t))
    # Apply duty cycle
    phase = (t * freq) % 1.0
    wave = np.where(phase < duty, volume, -volume)
    if fade_out:
        envelope = np.linspace(1.0, 0.0, len(wave))
        wave *= envelope
    return wave


def _triangle(freq: float, duration: float, volume: float = 0.4,
              fade_out: bool = True) -> np.ndarray:
    """Generate a triangle wave."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    phase = (t * freq) % 1.0
    wave = 4 * np.abs(phase - 0.5) - 1.0
    wave *= volume
    if fade_out:
        envelope = np.linspace(1.0, 0.0, len(wave))
        wave *= envelope
    return wave


def _noise(duration: float, volume: float = 0.3,
           fade_out: bool = True) -> np.ndarray:
    """Generate white noise."""
    samples = int(SAMPLE_RATE * duration)
    wave = np.random.uniform(-1, 1, samples) * volume
    if fade_out:
        envelope = np.linspace(1.0, 0.0, samples)
        wave *= envelope
    return wave


def _sweep(freq_start: float, freq_end: float, duration: float,
           volume: float = 0.4, waveform: str = "sine",
           fade_out: bool = True) -> np.ndarray:
    """Generate a frequency sweep (pitch up/down)."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freqs = np.linspace(freq_start, freq_end, len(t))
    phase = np.cumsum(freqs / SAMPLE_RATE) * 2 * np.pi
    if waveform == "square":
        wave = np.sign(np.sin(phase)) * volume
    elif waveform == "triangle":
        wave = (2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1) * volume
    else:
        wave = np.sin(phase) * volume
    if fade_out:
        envelope = np.linspace(1.0, 0.0, len(wave))
        wave *= envelope
    return wave


def _mix(*waves) -> np.ndarray:
    """Mix multiple waveforms together, padding shorter ones."""
    if not waves:
        return np.array([])
    max_len = max(len(w) for w in waves)
    result = np.zeros(max_len)
    for w in waves:
        result[:len(w)] += w
    # Clamp to [-1, 1]
    peak = np.max(np.abs(result))
    if peak > 1.0:
        result /= peak
    return result


def _concat(*waves) -> np.ndarray:
    """Concatenate waveforms sequentially."""
    return np.concatenate(waves)


def _repeat(wave: np.ndarray, times: int) -> np.ndarray:
    """Repeat a waveform N times."""
    return np.tile(wave, times)


# ═══════════════════════════════════════════════════════════
#  SoundFX — Preset Sound Effects
# ═══════════════════════════════════════════════════════════

class SoundFX:
    """A generated sound effect stored as float32 sample data.

    Create sounds using class methods (presets)::

        click = SoundFX.typing_key()
        boom  = SoundFX.explosion()
        ding  = SoundFX.coin()
    """

    def __init__(self, samples: np.ndarray, name: str = "sfx"):
        self.samples = samples.astype(np.float32)
        self.name = name
        self.sample_rate = SAMPLE_RATE

    @property
    def duration(self) -> float:
        return len(self.samples) / self.sample_rate

    def to_wav_bytes(self) -> bytes:
        """Export as 24-bit WAV file bytes."""
        buf = io.BytesIO()
        # 24-bit PCM: scale to 24-bit range and pack as 3 bytes per sample
        pcm_32 = (self.samples * 8388607).astype(np.int32)  # 2^23 - 1
        raw = bytearray()
        for s in pcm_32:
            # Pack as little-endian 3-byte signed integer
            b = int(s) & 0xFFFFFF
            raw.extend(b.to_bytes(3, byteorder='little'))
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(3)  # 24-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(bytes(raw))
        return buf.getvalue()

    def save(self, path: str):
        """Save to a WAV file."""
        with open(path, 'wb') as f:
            f.write(self.to_wav_bytes())

    # ── Typing / UI ─────────────────────────────────────────

    @classmethod
    def typing_key(cls) -> "SoundFX":
        """Single keypress click — short, sharp square wave blip."""
        w = _square(800 + np.random.randint(-100, 100), 0.03, volume=0.15)
        return cls(w, "typing_key")

    @classmethod
    def typing_return(cls) -> "SoundFX":
        """Carriage return / newline sound — descending blip."""
        w = _sweep(600, 300, 0.06, volume=0.15, waveform="square")
        return cls(w, "typing_return")

    @classmethod
    def ui_select(cls) -> "SoundFX":
        """UI selection / menu item hover."""
        w = _sine(1200, 0.05, volume=0.2)
        return cls(w, "ui_select")

    @classmethod
    def ui_confirm(cls) -> "SoundFX":
        """UI confirmation — ascending two-tone."""
        w = _concat(
            _square(600, 0.06, volume=0.2, fade_out=False),
            _square(900, 0.08, volume=0.2),
        )
        return cls(w, "ui_confirm")

    @classmethod
    def ui_cancel(cls) -> "SoundFX":
        """UI cancel — descending two-tone."""
        w = _concat(
            _square(500, 0.06, volume=0.2, fade_out=False),
            _square(300, 0.08, volume=0.2),
        )
        return cls(w, "ui_cancel")

    # ── Game Events ─────────────────────────────────────────

    @classmethod
    def coin(cls) -> "SoundFX":
        """Coin / item collect — classic ascending bloop."""
        w = _concat(
            _square(987, 0.06, volume=0.25, fade_out=False),
            _square(1318, 0.12, volume=0.25),
        )
        return cls(w, "coin")

    @classmethod
    def jump(cls) -> "SoundFX":
        """Jump sound — quick pitch-up sweep."""
        w = _sweep(200, 800, 0.12, volume=0.25, waveform="square")
        return cls(w, "jump")

    @classmethod
    def land(cls) -> "SoundFX":
        """Landing thud — low frequency burst with noise."""
        w = _mix(
            _sine(80, 0.08, volume=0.3),
            _noise(0.05, volume=0.15),
        )
        return cls(w, "land")

    @classmethod
    def hit(cls) -> "SoundFX":
        """Hit / damage — sharp noise burst."""
        w = _mix(
            _noise(0.08, volume=0.3),
            _square(200, 0.06, volume=0.2),
        )
        return cls(w, "hit")

    @classmethod
    def powerup(cls) -> "SoundFX":
        """Power-up — ascending arpeggio."""
        notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
        parts = [_square(n, 0.08, volume=0.2, fade_out=False) for n in notes]
        parts[-1] = _square(notes[-1], 0.15, volume=0.2)
        return cls(_concat(*parts), "powerup")

    @classmethod
    def death(cls) -> "SoundFX":
        """Death / game over — descending pitch."""
        w = _sweep(800, 100, 0.4, volume=0.3, waveform="square")
        return cls(w, "death")

    # ── Nature / Ambient ────────────────────────────────────

    @classmethod
    def explosion(cls) -> "SoundFX":
        """Explosion — noise burst with low rumble."""
        w = _mix(
            _noise(0.3, volume=0.4),
            _sine(60, 0.4, volume=0.3),
            _sweep(400, 50, 0.3, volume=0.2),
        )
        return cls(w, "explosion")

    @classmethod
    def fire_crackle(cls) -> "SoundFX":
        """Fire crackling — short noise bursts."""
        parts = []
        for _ in range(5):
            gap = np.zeros(int(SAMPLE_RATE * np.random.uniform(0.02, 0.08)))
            crackle = _noise(np.random.uniform(0.01, 0.03), volume=0.15)
            parts.extend([gap, crackle])
        return cls(_concat(*parts), "fire_crackle")

    @classmethod
    def wind(cls, duration: float = 1.0) -> "SoundFX":
        """Wind — filtered noise with slow modulation."""
        raw = _noise(duration, volume=0.2, fade_out=False)
        # Simple low-pass via moving average
        kernel_size = 50
        kernel = np.ones(kernel_size) / kernel_size
        filtered = np.convolve(raw, kernel, mode='same')
        # Modulate volume
        t = np.linspace(0, duration, len(filtered))
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)
        filtered *= modulation
        return cls(filtered, "wind")

    @classmethod
    def rain_drop(cls) -> "SoundFX":
        """Single rain drop — short high-frequency ping."""
        freq = np.random.uniform(2000, 4000)
        w = _sine(freq, 0.04, volume=0.1)
        return cls(w, "rain_drop")

    @classmethod
    def water_splash(cls) -> "SoundFX":
        """Water splash — noise with resonance."""
        w = _mix(
            _noise(0.15, volume=0.25),
            _sine(300, 0.1, volume=0.1),
        )
        return cls(w, "water_splash")

    # ── Transitions ─────────────────────────────────────────

    @classmethod
    def whoosh(cls) -> "SoundFX":
        """Whoosh — for transitions and fast movement."""
        w = _mix(
            _sweep(200, 2000, 0.2, volume=0.15),
            _noise(0.15, volume=0.1),
        )
        return cls(w, "whoosh")

    @classmethod
    def reveal(cls) -> "SoundFX":
        """Reveal / appearance — shimmer sweep up."""
        w = _sweep(400, 2000, 0.3, volume=0.2, waveform="sine")
        return cls(w, "reveal")

    @classmethod
    def dismiss(cls) -> "SoundFX":
        """Dismiss / disappear — sweep down."""
        w = _sweep(1500, 200, 0.2, volume=0.15, waveform="sine")
        return cls(w, "dismiss")

    # ── Educational ─────────────────────────────────────────

    @classmethod
    def correct(cls) -> "SoundFX":
        """Correct answer — pleasant ascending chime."""
        w = _concat(
            _sine(523, 0.08, volume=0.25, fade_out=False),
            _sine(659, 0.08, volume=0.25, fade_out=False),
            _sine(784, 0.15, volume=0.25),
        )
        return cls(w, "correct")

    @classmethod
    def incorrect(cls) -> "SoundFX":
        """Incorrect answer — dissonant buzz."""
        w = _mix(
            _square(200, 0.2, volume=0.2),
            _square(210, 0.2, volume=0.2),
        )
        return cls(w, "incorrect")

    @classmethod
    def tick(cls) -> "SoundFX":
        """Tick — for timers, counting."""
        w = _square(1000, 0.02, volume=0.15)
        return cls(w, "tick")

    @classmethod
    def achievement(cls) -> "SoundFX":
        """Achievement unlocked — fanfare-style arpeggio."""
        notes = [523, 659, 784, 1047, 1318]
        parts = []
        for i, n in enumerate(notes):
            dur = 0.07 if i < len(notes) - 1 else 0.2
            fo = i == len(notes) - 1
            parts.append(_triangle(n, dur, volume=0.25, fade_out=fo))
        return cls(_concat(*parts), "achievement")


# ═══════════════════════════════════════════════════════════
#  Sound Timeline
# ═══════════════════════════════════════════════════════════

class SoundTimeline:
    """Collects sound events placed at specific times, then mixes them
    into a single audio track for muxing with video.

    This is managed by the Scene — users don't interact with it directly.
    """

    def __init__(self):
        self._events: list = []  # [(time_seconds, SoundFX), ...]

    def add(self, sfx: SoundFX, at: float):
        """Place a sound effect at a specific time (seconds)."""
        self._events.append((at, sfx))

    @property
    def event_count(self) -> int:
        return len(self._events)

    def mix(self, total_duration: float) -> np.ndarray:
        """Mix all sound events into a single audio timeline.

        Args:
            total_duration: Total video duration in seconds.

        Returns:
            Float32 numpy array of mixed audio samples.
        """
        total_samples = int(total_duration * SAMPLE_RATE)
        if total_samples <= 0:
            return np.array([], dtype=np.float32)

        mix_buf = np.zeros(total_samples, dtype=np.float32)

        for time_s, sfx in self._events:
            start_idx = int(time_s * SAMPLE_RATE)
            end_idx = start_idx + len(sfx.samples)
            if start_idx < 0:
                start_idx = 0
            if start_idx >= total_samples:
                continue
            end_idx = min(end_idx, total_samples)
            src_len = end_idx - start_idx
            
            # Lower default SFX volume by 50%, keep voiceovers normal
            sfx_samples = sfx.samples
            if not sfx.name.startswith("voiceover_"):
                sfx_samples = sfx.samples * 0.5
                
            mix_buf[start_idx:end_idx] += sfx_samples[:src_len]

        # Clamp
        peak = np.max(np.abs(mix_buf))
        if peak > 1.0:
            mix_buf /= peak

        return mix_buf

    def to_wav_bytes(self, total_duration: float) -> bytes:
        """Mix and export as 24-bit WAV bytes."""
        mixed = self.mix(total_duration)
        buf = io.BytesIO()
        # 24-bit PCM
        pcm_32 = (mixed * 8388607).astype(np.int32)
        raw = bytearray()
        for s in pcm_32:
            b = int(s) & 0xFFFFFF
            raw.extend(b.to_bytes(3, byteorder='little'))
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(3)  # 24-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(bytes(raw))
        return buf.getvalue()

    def save_wav(self, path: str, total_duration: float):
        """Save mixed audio to a WAV file."""
        with open(path, 'wb') as f:
            f.write(self.to_wav_bytes(total_duration))


# ═══════════════════════════════════════════════════════════
#  Audio Muxing with Video
# ═══════════════════════════════════════════════════════════

def mux_audio_video(video_path: str, audio_wav_path: str,
                    output_path: str):
    """Combine a video file with an audio WAV file using ffmpeg.

    Args:
        video_path: Path to the video-only MP4.
        audio_wav_path: Path to the WAV audio file.
        output_path: Path for the final MP4 with audio.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_wav_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        output_path,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[PixelEngine] Audio mux warning: {result.stderr[:200]}")
