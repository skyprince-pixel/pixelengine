"""PixelEngine sound — vintage high-quality procedural sound synthesis.

Generates rich instrument-quality SFX using additive synthesis with
ADSR envelopes and studio-grade effects via Spotify's Pedalboard library.
All sounds are procedural — no external audio files needed.

Features:
- **Piano/instrument synthesis**: Additive harmonics + ADSR envelopes
- **Pedalboard FX**: Reverb, chorus, delay, compression, EQ
- **Dynamic SFX**: Contextual sound generation based on situation
- **Pydub**: Professional audio mixing (optional)
- **PyAV**: In-memory audio/video muxing (optional)

Usage::

    # Preset sounds (vintage but high quality)
    scene.play_sound(SoundFX.coin(), at=2.5)

    # Dynamic contextual sounds
    scene.play_sound(SoundFX.dynamic("success"), at=3.0)
    scene.play_sound(SoundFX.dynamic("impact", intensity=0.8))

    # Custom instrument note
    scene.play_sound(SoundFX.piano_note("C4", duration=0.5))
"""
import math
import struct
import wave
import io
import os
import subprocess
import tempfile
import numpy as np

# Optional: Pydub for advanced audio mixing
try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

# Optional: PyAV for in-memory audio/video muxing
try:
    import av
    HAS_PYAV = True
except ImportError:
    HAS_PYAV = False

# Optional: Pedalboard for studio-grade effects
try:
    from pedalboard import (
        Pedalboard, Reverb, Chorus, Delay, Compressor, Gain,
        HighpassFilter, LowpassFilter, Limiter, Bitcrush,
    )
    HAS_PEDALBOARD = True
except ImportError:
    HAS_PEDALBOARD = False


SAMPLE_RATE = 48000  # 48 kHz high-quality audio

# ── Note frequency lookup ───────────────────────────────────
_NOTE_FREQS = {}
_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
for _oct in range(0, 9):
    for _i, _name in enumerate(_NOTE_NAMES):
        _midi = (_oct + 1) * 12 + _i
        _NOTE_FREQS[f"{_name}{_oct}"] = 440.0 * (2.0 ** ((_midi - 69) / 12.0))


def note_freq(name: str) -> float:
    """Get frequency for a note name like 'C4', 'A#3', 'F5'."""
    return _NOTE_FREQS.get(name, 440.0)


# ═══════════════════════════════════════════════════════════
#  ADSR Envelope
# ═══════════════════════════════════════════════════════════

def _adsr(length: int, attack: float = 0.01, decay: float = 0.05,
          sustain: float = 0.6, release: float = 0.1) -> np.ndarray:
    """Generate an ADSR amplitude envelope.

    Args:
        length: Total number of samples.
        attack: Attack time in seconds.
        decay: Decay time in seconds.
        sustain: Sustain level (0.0–1.0).
        release: Release time in seconds.
    """
    a_len = int(attack * SAMPLE_RATE)
    d_len = int(decay * SAMPLE_RATE)
    r_len = int(release * SAMPLE_RATE)
    s_len = max(0, length - a_len - d_len - r_len)

    env = np.concatenate([
        np.linspace(0.0, 1.0, max(1, a_len)),           # Attack
        np.linspace(1.0, sustain, max(1, d_len)),        # Decay
        np.full(max(0, s_len), sustain),                  # Sustain
        np.linspace(sustain, 0.0, max(1, r_len)),        # Release
    ])
    # Trim or pad to exact length
    if len(env) > length:
        env = env[:length]
    elif len(env) < length:
        env = np.pad(env, (0, length - len(env)))
    return env


# ═══════════════════════════════════════════════════════════
#  Waveform Generators (enhanced)
# ═══════════════════════════════════════════════════════════

def _sine(freq: float, duration: float, volume: float = 0.5,
          fade_out: bool = True) -> np.ndarray:
    """Generate a sine wave."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    w = np.sin(2 * np.pi * freq * t) * volume
    if fade_out:
        w *= np.linspace(1.0, 0.0, n)
    return w


def _square(freq: float, duration: float, volume: float = 0.3,
            duty: float = 0.5, fade_out: bool = True) -> np.ndarray:
    """Generate a band-limited square wave (anti-aliased)."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Band-limited: sum odd harmonics up to Nyquist
    w = np.zeros(n)
    for k in range(1, 20, 2):
        if k * freq > SAMPLE_RATE / 2:
            break
        w += np.sin(2 * np.pi * k * freq * t) / k
    w *= (4 / np.pi) * volume
    if fade_out:
        w *= np.linspace(1.0, 0.0, n)
    return w


def _triangle(freq: float, duration: float, volume: float = 0.4,
              fade_out: bool = True) -> np.ndarray:
    """Generate a band-limited triangle wave."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    w = np.zeros(n)
    for k in range(0, 10):
        h = 2 * k + 1
        if h * freq > SAMPLE_RATE / 2:
            break
        w += ((-1) ** k) * np.sin(2 * np.pi * h * freq * t) / (h * h)
    w *= (8 / (np.pi ** 2)) * volume
    if fade_out:
        w *= np.linspace(1.0, 0.0, n)
    return w


def _saw(freq: float, duration: float, volume: float = 0.3,
         fade_out: bool = True) -> np.ndarray:
    """Generate a band-limited sawtooth wave."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    w = np.zeros(n)
    for k in range(1, 25):
        if k * freq > SAMPLE_RATE / 2:
            break
        w += ((-1) ** (k + 1)) * np.sin(2 * np.pi * k * freq * t) / k
    w *= (2 / np.pi) * volume
    if fade_out:
        w *= np.linspace(1.0, 0.0, n)
    return w


def _noise(duration: float, volume: float = 0.3,
           fade_out: bool = True) -> np.ndarray:
    """Generate white noise."""
    n = int(SAMPLE_RATE * duration)
    w = np.random.uniform(-1, 1, n) * volume
    if fade_out:
        w *= np.linspace(1.0, 0.0, n)
    return w


def _filtered_noise(duration: float, volume: float = 0.3,
                    cutoff_hz: float = 2000.0, fade_out: bool = True) -> np.ndarray:
    """Generate low-pass filtered noise for smoother textures."""
    raw = _noise(duration, volume, fade_out=False)
    if HAS_PEDALBOARD:
        audio = raw.astype(np.float32).reshape(1, -1)
        board = Pedalboard([LowpassFilter(cutoff_frequency_hz=cutoff_hz)])
        out = board(audio, SAMPLE_RATE)
        raw = out.flatten()
    else:
        # Simple moving-average fallback
        k = max(1, int(SAMPLE_RATE / cutoff_hz))
        kernel = np.ones(k) / k
        raw = np.convolve(raw, kernel, mode='same')
    if fade_out:
        raw *= np.linspace(1.0, 0.0, len(raw))
    return raw * volume / max(0.01, np.max(np.abs(raw)))


def _sweep(freq_start: float, freq_end: float, duration: float,
           volume: float = 0.4, waveform: str = "sine",
           fade_out: bool = True) -> np.ndarray:
    """Generate a frequency sweep."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freqs = np.linspace(freq_start, freq_end, n)
    phase = np.cumsum(freqs / SAMPLE_RATE) * 2 * np.pi
    if waveform == "square":
        w = np.sign(np.sin(phase)) * volume
    elif waveform == "triangle":
        w = (2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1) * volume
    else:
        w = np.sin(phase) * volume
    if fade_out:
        w *= np.linspace(1.0, 0.0, n)
    return w


# ═══════════════════════════════════════════════════════════
#  Instrument Synthesis
# ═══════════════════════════════════════════════════════════

def _piano_tone(freq: float, duration: float, velocity: float = 0.7) -> np.ndarray:
    """Synthesize a piano-like tone using additive harmonics + ADSR.

    Uses 8 harmonics with piano-characteristic amplitude falloff
    and a percussive ADSR envelope with fast attack and natural decay.
    """
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    # Piano harmonic amplitudes (empirical model of a struck string)
    harmonic_amps = [1.0, 0.55, 0.35, 0.15, 0.08, 0.05, 0.03, 0.02]
    # Slight inharmonicity (real piano strings aren't perfect)
    inharmonicity = 0.0004

    w = np.zeros(n)
    for h_idx, amp in enumerate(harmonic_amps):
        h = h_idx + 1
        # Inharmonic partial frequency
        partial_freq = freq * h * math.sqrt(1 + inharmonicity * h * h)
        if partial_freq > SAMPLE_RATE / 2:
            break
        # Higher harmonics decay faster
        decay_rate = 1.0 + h_idx * 0.8
        harmonic_env = np.exp(-decay_rate * t / duration)
        w += amp * np.sin(2 * np.pi * partial_freq * t) * harmonic_env

    # ADSR: fast attack, moderate decay, low sustain, smooth release
    attack = min(0.005, duration * 0.05)
    decay = min(0.15, duration * 0.3)
    release = min(0.2, duration * 0.4)
    env = _adsr(n, attack=attack, decay=decay, sustain=0.25, release=release)
    w *= env * velocity

    # Normalize
    peak = np.max(np.abs(w))
    if peak > 0:
        w /= peak
    return w * velocity


def _bell_tone(freq: float, duration: float, volume: float = 0.5) -> np.ndarray:
    """Synthesize a bell/chime tone with metallic harmonics."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Bell partials are non-harmonic
    ratios = [1.0, 2.0, 2.76, 3.69, 4.23, 5.4, 6.2, 7.0]
    amps = [1.0, 0.6, 0.45, 0.3, 0.2, 0.15, 0.1, 0.06]
    w = np.zeros(n)
    for ratio, amp in zip(ratios, amps):
        partial = freq * ratio
        if partial > SAMPLE_RATE / 2:
            break
        decay = np.exp(-ratio * 1.5 * t / duration)
        w += amp * np.sin(2 * np.pi * partial * t) * decay
    env = _adsr(n, attack=0.002, decay=0.1, sustain=0.3, release=duration * 0.5)
    w *= env * volume
    peak = np.max(np.abs(w))
    if peak > 0:
        w /= peak
    return w * volume


def _mallet_tone(freq: float, duration: float, volume: float = 0.5) -> np.ndarray:
    """Synthesize a marimba/xylophone mallet hit."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Marimba: mostly fundamental with quick decay
    w = np.sin(2 * np.pi * freq * t)
    w += 0.3 * np.sin(2 * np.pi * freq * 3.98 * t)  # Non-harmonic partial
    w += 0.1 * np.sin(2 * np.pi * freq * 9.01 * t)
    # Very fast attack, quick exponential decay
    env = _adsr(n, attack=0.001, decay=0.08, sustain=0.1, release=duration * 0.6)
    strike = np.exp(-30 * t)  # Hard transient
    w *= env * (0.7 + 0.3 * strike) * volume
    peak = np.max(np.abs(w))
    if peak > 0:
        w /= peak
    return w * volume


# ═══════════════════════════════════════════════════════════
#  Pedalboard Effects Processing
# ═══════════════════════════════════════════════════════════

def _apply_fx(samples: np.ndarray, effects: list = None) -> np.ndarray:
    """Apply a chain of pedalboard effects to audio samples.

    Args:
        samples: 1D float32 numpy array of audio samples.
        effects: List of pedalboard effect instances. If None, applies
                 a subtle default chain (light compression + limiter).

    Returns:
        Processed audio as 1D float32 numpy array.
    """
    if not HAS_PEDALBOARD:
        return samples

    if effects is None:
        effects = [Compressor(threshold_db=-12, ratio=3.0), Limiter(threshold_db=-1.0)]

    audio = samples.astype(np.float32).reshape(1, -1)
    board = Pedalboard(effects)
    out = board(audio, SAMPLE_RATE)
    return out.flatten()


def _fx_reverb(room: float = 0.3, wet: float = 0.2, damping: float = 0.7):
    """Create a Reverb effect."""
    if HAS_PEDALBOARD:
        return Reverb(room_size=room, wet_level=wet, damping=damping)
    return None


def _fx_chorus(rate: float = 1.5, depth: float = 0.3, mix: float = 0.3):
    """Create a Chorus effect."""
    if HAS_PEDALBOARD:
        return Chorus(rate_hz=rate, depth=depth, mix=mix)
    return None


def _fx_delay(delay_sec: float = 0.15, mix: float = 0.2):
    """Create a Delay effect."""
    if HAS_PEDALBOARD:
        return Delay(delay_seconds=delay_sec, mix=mix)
    return None


def _fx_compress(threshold: float = -15.0, ratio: float = 4.0):
    """Create a Compressor effect."""
    if HAS_PEDALBOARD:
        return Compressor(threshold_db=threshold, ratio=ratio)
    return None


def _fx_bitcrush(bit_depth: float = 8):
    """Create a Bitcrush effect for retro flavor."""
    if HAS_PEDALBOARD:
        return Bitcrush(bit_depth=bit_depth)
    return None


def _fx_highpass(cutoff: float = 80.0):
    """Create a HighpassFilter for removing rumble."""
    if HAS_PEDALBOARD:
        return HighpassFilter(cutoff_frequency_hz=cutoff)
    return None


def _fx_lowpass(cutoff: float = 8000.0):
    """Create a LowpassFilter."""
    if HAS_PEDALBOARD:
        return LowpassFilter(cutoff_frequency_hz=cutoff)
    return None


# ═══════════════════════════════════════════════════════════
#  Mixing Utilities
# ═══════════════════════════════════════════════════════════

def _mix(*waves) -> np.ndarray:
    """Mix multiple waveforms together, padding shorter ones."""
    if not waves:
        return np.array([])
    max_len = max(len(w) for w in waves)
    result = np.zeros(max_len)
    for w in waves:
        result[:len(w)] += w
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


def _silence(duration: float) -> np.ndarray:
    """Generate silence for a given duration."""
    return np.zeros(int(SAMPLE_RATE * duration))


# ═══════════════════════════════════════════════════════════
#  SoundFX — Premium Vintage Preset Sound Effects
# ═══════════════════════════════════════════════════════════

class SoundFX:
    """A generated sound effect stored as float32 sample data.

    All presets use instrument-quality synthesis with ADSR envelopes
    and optional pedalboard effects for studio polish.

    Presets::

        click = SoundFX.typing_key()
        boom  = SoundFX.explosion()
        ding  = SoundFX.coin()

    Dynamic contextual sounds::

        sfx = SoundFX.dynamic("success", intensity=0.7)
        sfx = SoundFX.dynamic("error")
        sfx = SoundFX.dynamic("transition")

    Custom instrument notes::

        sfx = SoundFX.piano_note("C4", duration=0.5)
        sfx = SoundFX.bell_note("E5", duration=0.3)
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
        pcm_32 = (self.samples * 8388607).astype(np.int32)
        pcm_bytes = pcm_32.astype('<i4').tobytes()
        raw = bytearray(len(pcm_32) * 3)
        raw[0::3] = pcm_bytes[0::4]
        raw[1::3] = pcm_bytes[1::4]
        raw[2::3] = pcm_bytes[2::4]
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(3)
            wf.setframerate(self.sample_rate)
            wf.writeframes(bytes(raw))
        return buf.getvalue()

    def save(self, path: str):
        """Save to a WAV file."""
        with open(path, 'wb') as f:
            f.write(self.to_wav_bytes())

    # ── Custom Instrument Notes ────────────────────────────

    @classmethod
    def piano_note(cls, note: str = "C4", duration: float = 0.5,
                   velocity: float = 0.7) -> "SoundFX":
        """Play a single piano note by name (e.g. 'C4', 'A#3')."""
        freq = note_freq(note)
        w = _piano_tone(freq, duration, velocity)
        fx = [e for e in [_fx_reverb(0.2, 0.15), _fx_compress()] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, f"piano_{note}")

    @classmethod
    def bell_note(cls, note: str = "E5", duration: float = 0.4,
                  volume: float = 0.5) -> "SoundFX":
        """Play a single bell/chime note."""
        freq = note_freq(note)
        w = _bell_tone(freq, duration, volume)
        fx = [e for e in [_fx_reverb(0.4, 0.25), _fx_highpass(200)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, f"bell_{note}")

    @classmethod
    def mallet_note(cls, note: str = "C5", duration: float = 0.3,
                    volume: float = 0.5) -> "SoundFX":
        """Play a single marimba/mallet note."""
        freq = note_freq(note)
        w = _mallet_tone(freq, duration, volume)
        fx = [e for e in [_fx_reverb(0.15, 0.1)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, f"mallet_{note}")

    # ── Typing / UI ─────────────────────────────────────────

    @classmethod
    def typing_key(cls) -> "SoundFX":
        """Keypress — short piano staccato with micro-randomization."""
        note_idx = np.random.choice([60, 62, 64, 65, 67])  # C D E F G
        freq = 440.0 * (2.0 ** ((note_idx - 69) / 12.0))
        w = _piano_tone(freq, 0.04, velocity=0.2)
        # Mix small transient click
        click = _noise(0.003, volume=0.08, fade_out=True)
        w = _mix(w, click)
        fx = [e for e in [_fx_highpass(300), _fx_compress(-20, 3)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "typing_key")

    @classmethod
    def typing_return(cls) -> "SoundFX":
        """Carriage return — descending piano grace note."""
        w = _concat(
            _piano_tone(note_freq("E4"), 0.03, 0.2),
            _piano_tone(note_freq("C4"), 0.06, 0.15),
        )
        fx = [e for e in [_fx_highpass(200)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "typing_return")

    @classmethod
    def ui_select(cls) -> "SoundFX":
        """UI hover/select — gentle bell ping."""
        w = _bell_tone(note_freq("E6"), 0.08, volume=0.2)
        fx = [e for e in [_fx_reverb(0.2, 0.15)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "ui_select")

    @classmethod
    def ui_confirm(cls) -> "SoundFX":
        """UI confirm — ascending piano dyad with sparkle."""
        w = _concat(
            _piano_tone(note_freq("C5"), 0.07, 0.25),
            _piano_tone(note_freq("E5"), 0.1, 0.3),
        )
        fx = [e for e in [_fx_reverb(0.25, 0.2), _fx_compress()] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "ui_confirm")

    @classmethod
    def ui_cancel(cls) -> "SoundFX":
        """UI cancel — descending minor 2nd with soft damping."""
        w = _concat(
            _piano_tone(note_freq("E4"), 0.06, 0.2),
            _piano_tone(note_freq("D#4"), 0.1, 0.2),
        )
        fx = [e for e in [_fx_reverb(0.15, 0.1), _fx_lowpass(3000)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "ui_cancel")

    # ── Game Events ─────────────────────────────────────────

    @classmethod
    def coin(cls) -> "SoundFX":
        """Coin collect — bright ascending bell dyad."""
        w = _concat(
            _bell_tone(note_freq("B5"), 0.07, 0.3),
            _bell_tone(note_freq("E6"), 0.14, 0.35),
        )
        fx = [e for e in [_fx_reverb(0.2, 0.15), _fx_highpass(400)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "coin")

    @classmethod
    def jump(cls) -> "SoundFX":
        """Jump — quick ascending piano gliss with air."""
        w = _sweep(200, 900, 0.12, volume=0.25, waveform="sine")
        air = _filtered_noise(0.08, volume=0.06, cutoff_hz=4000)
        w = _mix(w, air)
        env = _adsr(len(w), attack=0.003, decay=0.04, sustain=0.3, release=0.04)
        w *= env
        fx = [e for e in [_fx_highpass(150), _fx_compress()] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "jump")

    @classmethod
    def land(cls) -> "SoundFX":
        """Landing thud — low piano hammer + floor rumble."""
        bass = _piano_tone(note_freq("C2"), 0.12, velocity=0.35)
        thud = _filtered_noise(0.06, volume=0.2, cutoff_hz=500)
        w = _mix(bass, thud)
        fx = [e for e in [_fx_lowpass(1500), _fx_compress(-10, 4)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "land")

    @classmethod
    def hit(cls) -> "SoundFX":
        """Hit/damage — dissonant piano cluster + noise transient."""
        cluster = _mix(
            _piano_tone(note_freq("C3"), 0.08, 0.3),
            _piano_tone(note_freq("C#3"), 0.08, 0.25),
            _noise(0.05, volume=0.2),
        )
        fx = [e for e in [_fx_compress(-8, 5), _fx_highpass(100)] if e]
        w = _apply_fx(cluster, fx) if fx else cluster
        return cls(w, "hit")

    @classmethod
    def powerup(cls) -> "SoundFX":
        """Power-up — ascending major arpeggio on piano."""
        notes = ["C5", "E5", "G5", "C6"]
        parts = []
        for i, n in enumerate(notes):
            dur = 0.06 if i < len(notes) - 1 else 0.18
            parts.append(_piano_tone(note_freq(n), dur, 0.3))
        w = _concat(*parts)
        fx = [e for e in [_fx_reverb(0.3, 0.2), _fx_compress()] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "powerup")

    @classmethod
    def death(cls) -> "SoundFX":
        """Death/game over — descending chromatic piano with reverb."""
        notes = ["G4", "F#4", "F4", "E4", "D#4", "D4"]
        parts = []
        for i, n in enumerate(notes):
            dur = 0.07 + i * 0.015
            vel = 0.3 - i * 0.03
            parts.append(_piano_tone(note_freq(n), dur, max(0.1, vel)))
        w = _concat(*parts)
        fx = [e for e in [_fx_reverb(0.5, 0.35), _fx_lowpass(4000)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "death")

    # ── Nature / Ambient ────────────────────────────────────

    @classmethod
    def explosion(cls) -> "SoundFX":
        """Explosion — layered noise burst + low piano rumble."""
        rumble = _piano_tone(note_freq("C1"), 0.5, velocity=0.4)
        burst = _noise(0.15, volume=0.5, fade_out=True)
        crackle = _filtered_noise(0.3, volume=0.2, cutoff_hz=3000)
        sweep = _sweep(400, 40, 0.35, volume=0.25)
        w = _mix(rumble, burst, crackle, sweep)
        fx = [e for e in [_fx_compress(-6, 6), _fx_lowpass(6000)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "explosion")

    @classmethod
    def fire_crackle(cls) -> "SoundFX":
        """Fire crackling — randomized micro-bursts with warmth."""
        parts = []
        for _ in range(6):
            gap = _silence(np.random.uniform(0.015, 0.06))
            pop = _filtered_noise(np.random.uniform(0.008, 0.025),
                                  volume=0.15, cutoff_hz=4000)
            parts.extend([gap, pop])
        w = _concat(*parts)
        fx = [e for e in [_fx_lowpass(5000), _fx_reverb(0.1, 0.08)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "fire_crackle")

    @classmethod
    def wind(cls, duration: float = 1.0) -> "SoundFX":
        """Wind — filtered modulated noise."""
        raw = _noise(duration, volume=0.2, fade_out=False)
        t = np.linspace(0, duration, len(raw))
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t)
        raw *= mod
        fx = [e for e in [_fx_lowpass(1500), _fx_reverb(0.4, 0.3)] if e]
        w = _apply_fx(raw, fx) if fx else raw
        return cls(w, "wind")

    @classmethod
    def rain_drop(cls) -> "SoundFX":
        """Rain drop — high bell ping with random pitch."""
        freq = np.random.uniform(2500, 5000)
        w = _bell_tone(freq, 0.06, volume=0.1)
        return cls(w, "rain_drop")

    @classmethod
    def water_splash(cls) -> "SoundFX":
        """Water splash — noise burst with resonant filter."""
        w = _mix(
            _filtered_noise(0.15, volume=0.25, cutoff_hz=3000),
            _bell_tone(300, 0.1, volume=0.08),
        )
        fx = [e for e in [_fx_reverb(0.3, 0.2)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "water_splash")

    # ── Transitions ─────────────────────────────────────────

    @classmethod
    def whoosh(cls) -> "SoundFX":
        """Whoosh — sweep + filtered noise for transitions."""
        sweep = _sweep(200, 2500, 0.2, volume=0.15)
        air = _filtered_noise(0.18, volume=0.12, cutoff_hz=6000)
        w = _mix(sweep, air)
        fx = [e for e in [_fx_reverb(0.2, 0.15), _fx_highpass(150)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "whoosh")

    @classmethod
    def reveal(cls) -> "SoundFX":
        """Reveal/appearance — ascending piano shimmer."""
        w = _concat(
            _piano_tone(note_freq("C5"), 0.06, 0.2),
            _piano_tone(note_freq("E5"), 0.06, 0.22),
            _piano_tone(note_freq("G5"), 0.06, 0.24),
            _bell_tone(note_freq("C6"), 0.2, 0.2),
        )
        fx = [e for e in [_fx_reverb(0.35, 0.25), _fx_chorus()] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "reveal")

    @classmethod
    def dismiss(cls) -> "SoundFX":
        """Dismiss/disappear — descending piano with fade."""
        w = _concat(
            _piano_tone(note_freq("G5"), 0.06, 0.2),
            _piano_tone(note_freq("E5"), 0.06, 0.18),
            _piano_tone(note_freq("C5"), 0.12, 0.15),
        )
        fx = [e for e in [_fx_reverb(0.25, 0.2), _fx_lowpass(5000)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "dismiss")

    # ── Educational ─────────────────────────────────────────

    @classmethod
    def correct(cls) -> "SoundFX":
        """Correct answer — bright ascending major triad chime."""
        w = _concat(
            _bell_tone(note_freq("C5"), 0.09, 0.25),
            _bell_tone(note_freq("E5"), 0.09, 0.28),
            _bell_tone(note_freq("G5"), 0.16, 0.3),
        )
        fx = [e for e in [_fx_reverb(0.3, 0.2), _fx_highpass(300)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "correct")

    @classmethod
    def incorrect(cls) -> "SoundFX":
        """Incorrect answer — dissonant minor 2nd buzz on piano."""
        w = _mix(
            _piano_tone(note_freq("E3"), 0.2, 0.25),
            _piano_tone(note_freq("F3"), 0.2, 0.25),
        )
        fx = [e for e in [_fx_lowpass(3000), _fx_compress(-10, 4)] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "incorrect")

    @classmethod
    def tick(cls) -> "SoundFX":
        """Tick — short mallet tap for timers/counting."""
        w = _mallet_tone(note_freq("G5"), 0.03, volume=0.15)
        return cls(w, "tick")

    @classmethod
    def achievement(cls) -> "SoundFX":
        """Achievement — fanfare arpeggio on piano with reverb."""
        notes = ["C5", "E5", "G5", "C6", "E6"]
        parts = []
        for i, n in enumerate(notes):
            dur = 0.06 if i < len(notes) - 1 else 0.25
            vel = 0.2 + i * 0.03
            parts.append(_piano_tone(note_freq(n), dur, vel))
        w = _concat(*parts)
        fx = [e for e in [_fx_reverb(0.4, 0.3), _fx_chorus(1.0, 0.2, 0.15),
                          _fx_compress()] if e]
        w = _apply_fx(w, fx) if fx else w
        return cls(w, "achievement")

    # ═══════════════════════════════════════════════════════
    #  Dynamic Contextual SFX Generator
    # ═══════════════════════════════════════════════════════

    @classmethod
    def dynamic(cls, situation: str, intensity: float = 0.5,
                key: str = "C", mode: str = "major") -> "SoundFX":
        """Generate a unique sound effect based on the situation.

        Dynamically composes instrument notes and effects to match the
        emotional context. Each call produces a slightly varied result.

        Args:
            situation: Context string. Supported:
                'success', 'error', 'warning', 'info',
                'reveal', 'dismiss', 'transition', 'impact',
                'typing', 'hover', 'click', 'celebration',
                'tension', 'mystery', 'wonder', 'sadness'
            intensity: Effect intensity 0.0–1.0 (affects note count,
                       velocity, reverb depth, etc.)
            key: Musical key root note (default "C").
            mode: 'major' or 'minor'.

        Returns:
            A unique SoundFX instance.
        """
        # Build scale from key
        root_midi = 60  # C4 default
        for note_name, midi_num in [("C", 60), ("D", 62), ("E", 64),
                                     ("F", 65), ("G", 67), ("A", 69), ("B", 71)]:
            if key == note_name:
                root_midi = midi_num
                break

        if mode == "minor":
            intervals = [0, 2, 3, 5, 7, 8, 10, 12]  # Natural minor
        else:
            intervals = [0, 2, 4, 5, 7, 9, 11, 12]  # Major

        scale_freqs = [440.0 * (2.0 ** ((root_midi + iv - 69) / 12.0))
                       for iv in intervals]

        vel = 0.15 + intensity * 0.35
        sit = situation.lower().strip()

        # ── Map situations to sound recipes ───
        if sit in ("success", "correct", "win"):
            # Ascending major arpeggio — bright and satisfying
            n_notes = 3 + int(intensity * 3)
            parts = []
            for i in range(min(n_notes, len(scale_freqs))):
                dur = 0.05 + np.random.uniform(-0.005, 0.005)
                parts.append(_piano_tone(scale_freqs[i], dur, vel))
            # Sustain last note
            parts.append(_bell_tone(scale_freqs[min(n_notes - 1, len(scale_freqs) - 1)],
                                    0.2 + intensity * 0.15, vel))
            w = _concat(*parts)
            fx_chain = [_fx_reverb(0.25 + intensity * 0.2, 0.2), _fx_compress()]

        elif sit in ("error", "incorrect", "fail"):
            # Dissonant cluster — minor 2nd clash
            f1 = scale_freqs[0] * (0.5 if intensity > 0.5 else 1.0)
            f2 = f1 * (16 / 15)  # Minor second
            w = _mix(
                _piano_tone(f1, 0.15 + intensity * 0.1, vel),
                _piano_tone(f2, 0.15 + intensity * 0.1, vel * 0.9),
            )
            fx_chain = [_fx_lowpass(2000 + intensity * 2000), _fx_compress(-8, 5)]

        elif sit in ("warning", "alert", "caution"):
            # Repeated bell pings — attention-grabbing
            freq = scale_freqs[4]  # 5th scale degree
            parts = [_bell_tone(freq, 0.08, vel) for _ in range(2 + int(intensity * 2))]
            gap = _silence(0.04)
            interleaved = []
            for p in parts:
                interleaved.extend([p, gap])
            w = _concat(*interleaved[:-1])
            fx_chain = [_fx_reverb(0.15, 0.1), _fx_highpass(400)]

        elif sit in ("reveal", "appear", "show"):
            # Ascending shimmer with chorus
            idxs = [0, 2, 4, 7][:2 + int(intensity * 2)]
            parts = [_piano_tone(scale_freqs[i], 0.06, vel) for i in idxs]
            parts.append(_bell_tone(scale_freqs[idxs[-1]], 0.2, vel * 0.8))
            w = _concat(*parts)
            fx_chain = [_fx_reverb(0.3 + intensity * 0.2, 0.25), _fx_chorus()]

        elif sit in ("dismiss", "hide", "disappear"):
            # Descending with damping
            idxs = [4, 2, 0][:2 + int(intensity)]
            parts = [_piano_tone(scale_freqs[i], 0.06, vel * (1 - idx * 0.1))
                     for idx, i in enumerate(idxs)]
            w = _concat(*parts)
            fx_chain = [_fx_reverb(0.2, 0.15), _fx_lowpass(4000)]

        elif sit in ("transition", "whoosh", "swipe"):
            # Sweep + air texture
            sweep = _sweep(200 + intensity * 200, 1500 + intensity * 1000,
                           0.15 + intensity * 0.1, volume=vel * 0.6)
            air = _filtered_noise(0.15, volume=vel * 0.3, cutoff_hz=5000)
            w = _mix(sweep, air)
            fx_chain = [_fx_reverb(0.2, 0.15), _fx_highpass(100)]

        elif sit in ("impact", "hit", "collision"):
            # Low piano + noise transient
            w = _mix(
                _piano_tone(scale_freqs[0] * 0.5, 0.1 + intensity * 0.05,
                            vel * (0.5 + intensity * 0.5)),
                _noise(0.04, volume=vel * 0.5),
                _filtered_noise(0.08, volume=vel * 0.3, cutoff_hz=2000),
            )
            fx_chain = [_fx_compress(-6, 6), _fx_lowpass(4000)]

        elif sit in ("typing", "keystroke", "input"):
            # Quick staccato piano tap
            idx = np.random.randint(0, min(5, len(scale_freqs)))
            w = _piano_tone(scale_freqs[idx], 0.035, vel * 0.4)
            click = _noise(0.003, volume=0.05)
            w = _mix(w, click)
            fx_chain = [_fx_highpass(300)]

        elif sit in ("hover", "focus", "select"):
            # Gentle bell ping
            w = _bell_tone(scale_freqs[4], 0.07, vel * 0.5)
            fx_chain = [_fx_reverb(0.2, 0.12)]

        elif sit in ("click", "tap", "press"):
            # Mallet tap
            w = _mallet_tone(scale_freqs[0], 0.05, vel * 0.5)
            fx_chain = [_fx_highpass(200)]

        elif sit in ("celebration", "victory", "fanfare"):
            # Full ascending arpeggio with sustain
            notes_to_play = scale_freqs[:min(6, len(scale_freqs))]
            parts = []
            for i, f in enumerate(notes_to_play):
                dur = 0.055 if i < len(notes_to_play) - 1 else 0.3
                parts.append(_piano_tone(f, dur, vel + i * 0.02))
            w = _concat(*parts)
            fx_chain = [_fx_reverb(0.4, 0.3), _fx_chorus(1.0, 0.2, 0.15),
                        _fx_compress()]

        elif sit in ("tension", "suspense", "danger"):
            # Low tremolo with minor 2nd
            f = scale_freqs[0] * 0.5
            n = int(SAMPLE_RATE * (0.3 + intensity * 0.2))
            t = np.linspace(0, 0.3 + intensity * 0.2, n, endpoint=False)
            tremolo = 0.5 + 0.5 * np.sin(2 * np.pi * 8 * t)
            w = _piano_tone(f, 0.3 + intensity * 0.2, vel)
            w[:n] *= tremolo[:len(w)]
            w2 = _piano_tone(f * (16 / 15), 0.2, vel * 0.4)
            w = _mix(w, w2)
            fx_chain = [_fx_reverb(0.4, 0.3), _fx_lowpass(3000)]

        elif sit in ("mystery", "curiosity", "question"):
            # Whole-tone scale snippet — dreamlike
            wt_intervals = [0, 2, 4, 6, 8, 10]
            wt_freqs = [440.0 * (2.0 ** ((root_midi + iv - 69) / 12.0))
                        for iv in wt_intervals]
            idxs = np.random.choice(len(wt_freqs), size=3, replace=False)
            parts = [_bell_tone(wt_freqs[i], 0.1, vel * 0.6) for i in sorted(idxs)]
            w = _concat(*parts)
            fx_chain = [_fx_reverb(0.5, 0.35), _fx_chorus(0.8, 0.3, 0.25)]

        elif sit in ("wonder", "awe", "magic"):
            # Wide arpeggiated chord with lush reverb
            chord = [scale_freqs[0], scale_freqs[2], scale_freqs[4],
                     scale_freqs[0] * 2]
            parts = [_bell_tone(f, 0.08, vel * 0.7) for f in chord]
            w = _concat(*parts)
            sustain = _mix(*[_piano_tone(f, 0.3, vel * 0.3) for f in chord])
            w = _concat(w, sustain)
            fx_chain = [_fx_reverb(0.6, 0.4), _fx_chorus(0.6, 0.25, 0.2)]

        elif sit in ("sadness", "loss", "melancholy"):
            # Descending minor with slow decay
            minor_freqs = [440.0 * (2.0 ** ((root_midi + iv - 69) / 12.0))
                           for iv in [0, 3, 7, 12]]
            parts = [_piano_tone(f, 0.12, vel * 0.6) for f in reversed(minor_freqs)]
            w = _concat(*parts)
            fx_chain = [_fx_reverb(0.5, 0.35), _fx_lowpass(4000)]

        else:
            # Fallback: single bell note
            w = _bell_tone(scale_freqs[0], 0.15, vel)
            fx_chain = [_fx_reverb(0.2, 0.15)]

        # Apply effects chain
        fx_chain = [e for e in fx_chain if e is not None]
        if fx_chain:
            w = _apply_fx(w, fx_chain)

        return cls(w, f"dynamic_{sit}")


# ═══════════════════════════════════════════════════════════
#  Sound Timeline
# ═══════════════════════════════════════════════════════════

class SoundTimeline:
    """Collects sound events placed at specific times, then mixes them
    into a single audio track for muxing with video.
    """

    def __init__(self):
        self._events: list = []

    def add(self, sfx: SoundFX, at: float):
        """Place a sound effect at a specific time (seconds)."""
        self._events.append((at, sfx))

    @property
    def event_count(self) -> int:
        return len(self._events)

    def mix(self, total_duration: float) -> np.ndarray:
        """Mix all events into a single audio timeline."""
        if HAS_PYDUB:
            return self._mix_pydub(total_duration)
        return self._mix_numpy(total_duration)

    def _mix_pydub(self, total_duration: float) -> np.ndarray:
        """Mix using Pydub for higher quality audio processing."""
        total_ms = int(total_duration * 1000)
        if total_ms <= 0:
            return np.array([], dtype=np.float32)
        base = AudioSegment.silent(duration=total_ms, frame_rate=SAMPLE_RATE)
        for time_s, sfx in self._events:
            position_ms = int(time_s * 1000)
            if position_ms >= total_ms:
                continue
            pcm_16 = (sfx.samples * 32767).astype(np.int16)
            segment = AudioSegment(
                pcm_16.tobytes(), frame_rate=SAMPLE_RATE,
                sample_width=2, channels=1,
            )
            if not sfx.name.startswith("voiceover_"):
                segment = segment - 6
            base = base.overlay(segment, position=position_ms)
        base = base.normalize()
        raw = np.frombuffer(base.raw_data, dtype=np.int16)
        return raw.astype(np.float32) / 32767.0

    def _mix_numpy(self, total_duration: float) -> np.ndarray:
        """Fallback: mix using numpy array operations."""
        total_samples = int(total_duration * SAMPLE_RATE)
        if total_samples <= 0:
            return np.array([], dtype=np.float32)
        mix_buf = np.zeros(total_samples, dtype=np.float32)
        for time_s, sfx in self._events:
            start_idx = int(time_s * SAMPLE_RATE)
            end_idx = start_idx + len(sfx.samples)
            # Source offset: skip samples if the sound starts before t=0
            src_offset = 0
            if start_idx < 0:
                src_offset = -start_idx
                start_idx = 0
            if start_idx >= total_samples:
                continue
            end_idx = min(end_idx, total_samples)
            src_len = end_idx - start_idx
            if src_len <= 0 or src_offset >= len(sfx.samples):
                continue
            sfx_samples = sfx.samples
            if not sfx.name.startswith("voiceover_"):
                sfx_samples = sfx.samples * 0.5
            mix_buf[start_idx:end_idx] += sfx_samples[src_offset:src_offset + src_len]
        peak = np.max(np.abs(mix_buf))
        if peak > 1.0:
            mix_buf /= peak
        return mix_buf

    def to_wav_bytes(self, total_duration: float) -> bytes:
        """Mix and export as 24-bit WAV bytes."""
        mixed = self.mix(total_duration)
        buf = io.BytesIO()
        pcm_32 = (mixed * 8388607).astype(np.int32)
        pcm_bytes = pcm_32.astype('<i4').tobytes()
        raw = bytearray(len(pcm_32) * 3)
        raw[0::3] = pcm_bytes[0::4]
        raw[1::3] = pcm_bytes[1::4]
        raw[2::3] = pcm_bytes[2::4]
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(3)
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
    """Combine a video file with an audio WAV file."""
    if HAS_PYAV:
        _mux_pyav(video_path, audio_wav_path, output_path)
    else:
        _mux_ffmpeg(video_path, audio_wav_path, output_path)


def _mux_pyav(video_path: str, audio_wav_path: str, output_path: str):
    """Mux video and audio using PyAV."""
    try:
        video_in = av.open(video_path)
        audio_in = av.open(audio_wav_path)
        output = av.open(output_path, 'w')
        video_stream = output.add_stream_from_template(video_in.streams.video[0])
        audio_stream = output.add_stream('aac', rate=SAMPLE_RATE)
        audio_stream.bit_rate = 256000
        for packet in video_in.demux(video_in.streams.video[0]):
            if packet.dts is None:
                continue
            packet.stream = video_stream
            output.mux(packet)
        for frame in audio_in.decode(audio=0):
            frame.pts = None
            for packet in audio_stream.encode(frame):
                output.mux(packet)
        for packet in audio_stream.encode():
            output.mux(packet)
        output.close()
        video_in.close()
        audio_in.close()
    except Exception as e:
        print(f"[PixelEngine] PyAV mux failed, falling back to ffmpeg: {e}")
        _mux_ffmpeg(video_path, audio_wav_path, output_path)


def _mux_ffmpeg(video_path: str, audio_wav_path: str, output_path: str):
    """Fallback: mux video and audio using ffmpeg subprocess."""
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
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[PixelEngine] Audio mux warning: {result.stderr[:200]}")
