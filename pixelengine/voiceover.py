"""PixelEngine VoiceOver — AI Text-to-Speech using Kokoro.

This module provides high-quality TTS using the Kokoro ONNX model.
It auto-downloads the required models on first use.

Usage::

    # Generate speech
    audio, duration = VoiceOver.generate("Welcome to PixelEngine!", voice="af_bella")

    # In a Scene
    self.play_voiceover("Welcome to PixelEngine!", voice="af_bella")
"""
import os
import urllib.request
import numpy as np

# Lazy load Kokoro to avoid slow imports if unused
_kokoro_instance = None
_sample_rate = 22050  # Kokoro models generally output 22050 or 24000
                      # kokoro-onnx outputs 24000 actually. We'll resample if needed.

# We will store models in ~/.cache/pixelengine/kokoro
CACHE_DIR = os.path.expanduser("~/.cache/pixelengine/kokoro")
ONNX_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin"
ONNX_FILE = os.path.join(CACHE_DIR, "kokoro-v0_19.onnx")
VOICES_FILE = os.path.join(CACHE_DIR, "voices.bin")


def _download_file(url: str, dest: str):
    """Download a file with a simple progress print."""
    if os.path.exists(dest):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"[VoiceOver] Downloading {os.path.basename(dest)}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"[VoiceOver] Download complete: {dest}")
    except Exception as e:
        if os.path.exists(dest):
            os.remove(dest)
        raise RuntimeError(f"Failed to download {url}: {e}")


def _get_kokoro():
    """Get or initialize the Kokoro instance."""
    global _kokoro_instance, _sample_rate
    if _kokoro_instance is not None:
        return _kokoro_instance

    _download_file(ONNX_URL, ONNX_FILE)
    _download_file(VOICES_URL, VOICES_FILE)

    try:
        from kokoro_onnx import Kokoro
        _kokoro_instance = Kokoro(ONNX_FILE, VOICES_FILE)
        return _kokoro_instance
    except ImportError:
        raise ImportError(
            "kokoro-onnx is not installed. Run: pip install kokoro-onnx soundfile"
        )


class VoiceOver:
    """Generates synthetic speech using Kokoro."""

    @classmethod
    def generate(cls, text: str, voice: str = "af_bella", speed: float = 1.0) -> tuple:
        """Generate speech from text.

        Available voices: af_bella, af_sarah, am_adam, am_michael,
                          bf_emma, bm_george, etc. (Default: af_bella)

        Args:
            text: The text to speak.
            voice: Voice name.
            speed: Speech speed (default 1.0).

        Returns:
            Tuple of (SoundFX, duration_in_seconds)
        """
        k = _get_kokoro()
        
        # kokoro-onnx create() returns (samples, sample_rate)
        # samples is a flat float32 numpy array
        samples, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
        
        from pixelengine.sound import SoundFX, SAMPLE_RATE
        
        # If Kokoro's sample rate doesn't match ours (it's usually 24000 vs 22050),
        # we need to do a simple linear pitch/resample or just change the SoundFX sr.
        # Actually, SoundFX assumes pixelengine.sound.SAMPLE_RATE (22050).
        # We can perform a basic nearest-neighbor or linear resample to 22050.
        if sr != SAMPLE_RATE:
            duration = len(samples) / sr
            target_len = int(duration * SAMPLE_RATE)
            indices = np.linspace(0, len(samples) - 1, target_len).astype(int)
            resampled = samples[indices]
            sfx = SoundFX(resampled, name=f"voiceover_{voice}")
        else:
            sfx = SoundFX(samples, name=f"voiceover_{voice}")
            
        return sfx, sfx.duration
