"""PixelEngine VoiceOver — AI Text-to-Speech using Chatterbox Turbo.

This module provides high-quality TTS using Resemble AI's Chatterbox Turbo model.
Models are auto-downloaded from HuggingFace on first use (~1.5 GB).

Features:
  - Disk cache: generated audio is cached to ~/.cache/pixelengine/tts/
    keyed by text+voice+speed. Repeat runs are near-instant.
  - Proper resampling via scipy for accurate duration and zero aliasing.
  - Batch pre-generation for preloading all voiceovers before construct().

Usage::

    # Generate speech (default voice)
    audio, duration = VoiceOver.generate("Welcome to PixelEngine!")

    # Generate speech with voice cloning (provide a ~10s reference .wav)
    audio, duration = VoiceOver.generate("Welcome!", voice="ref_clip.wav")

    # In a Scene
    self.play_voiceover("Welcome to PixelEngine!")

    # Batch pre-generate (populate cache before construct)
    VoiceOver.preload(["Line one.", "Line two.", "Line three."])
"""
import hashlib
import os
import time
import numpy as np
try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

# ── Cache directory ─────────────────────────────────────────
_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "pixelengine", "tts")

# Chatterbox globals
_chatterbox_instance = None
_chatterbox_sr = None

# Kokoro globals
_kokoro_instance = None
_kokoro_sr = 24000


def _get_device() -> str:
    """Auto-detect best available device: mps (Apple Silicon) > cpu."""
    if not HAS_TORCH:
        return "cpu"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _get_chatterbox():
    """Get or initialize the Chatterbox Turbo model."""
    global _chatterbox_instance, _chatterbox_sr
    if _chatterbox_instance is not None:
        return _chatterbox_instance

    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS, REPO_ID
        from huggingface_hub import snapshot_download
    except ImportError:
        raise ImportError(
            "chatterbox-tts is not installed. Run: pip install chatterbox-tts"
        )

    device = _get_device()
    print(f"[VoiceOver] Downloading/Loading Chatterbox Turbo on device: {device}")

    local_path = snapshot_download(
        repo_id=REPO_ID,
        token=False,  
        allow_patterns=["*.safetensors", "*.json", "*.txt", "*.pt", "*.model"]
    )

    _chatterbox_instance = ChatterboxTurboTTS.from_local(local_path, device=device)
    _chatterbox_sr = _chatterbox_instance.sr
    print(f"[VoiceOver] Chatterbox loaded (sample rate: {_chatterbox_sr})")
    return _chatterbox_instance


def _get_kokoro():
    """Get or initialize the Kokoro model."""
    global _kokoro_instance
    if _kokoro_instance is not None:
        return _kokoro_instance
        
    kokoro_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "pixelengine", "kokoro")
    onnx_file = os.path.join(kokoro_cache_dir, "kokoro-v0_19.onnx")
    voices_file = os.path.join(kokoro_cache_dir, "voices.bin")
    
    if not os.path.exists(onnx_file) or not os.path.exists(voices_file):
        print("[VoiceOver] Downloading Kokoro models...")
        os.makedirs(kokoro_cache_dir, exist_ok=True)
        import urllib.request
        urllib.request.urlretrieve("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx", onnx_file)
        urllib.request.urlretrieve("https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin", voices_file)

    try:
        from kokoro_onnx import Kokoro
    except ImportError:
        raise ImportError(
            "kokoro-onnx is not installed. Run: pip install kokoro-onnx soundfile"
        )
        
    print(f"[VoiceOver] Loading Kokoro ONNX model from {onnx_file}...")
    _kokoro_instance = Kokoro(onnx_file, voices_file)
    print(f"[VoiceOver] Kokoro loaded (sample rate: {_kokoro_sr})")
    return _kokoro_instance


def _cache_key(text: str, voice: str, speed: float, engine: str) -> str:
    """Generate a deterministic cache key from parameters."""
    voice_hash = ""
    if voice and os.path.isfile(voice):
        # Hash the voice file content for cloning consistency
        with open(voice, "rb") as f:
            voice_hash = hashlib.sha256(f.read()).hexdigest()[:12]
    elif voice:
        # String voice ID (e.g. "af_bella")
        voice_hash = voice
        
    payload = f"{engine}|{text}|{voice_hash}|{speed:.4f}"
    return hashlib.sha256(payload.encode()).hexdigest()


def _resample_scipy(samples: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """High-quality resampling using scipy — preserves duration exactly."""
    if orig_sr == target_sr:
        return samples
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(orig_sr, target_sr)
    up = target_sr // g
    down = orig_sr // g
    return resample_poly(samples, up, down).astype(np.float32)


class VoiceOver:
    """Generates synthetic speech using Kokoro ONNX (fast) or Chatterbox Turbo (HQ)."""

    @classmethod
    def generate(cls, text: str, voice: str = None, speed: float = 1.0,
                 cache: bool = True, engine: str = "kokoro") -> tuple:
        """Generate speech from text.

        Args:
            text: The text to speak.
            voice: Optional path to a ~10s reference .wav file for voice cloning
                   in Chatterbox, or a string like "af_bella" for Kokoro.
            speed: Speech speed multiplier (default 1.0).
            cache: If True (default), cache generated audio to disk.
            engine: "kokoro" (default) or "chatterbox".

        Returns:
            Tuple of (SoundFX, duration_in_seconds)
        """
        from pixelengine.sound import SoundFX, SAMPLE_RATE

        if engine not in ("kokoro", "chatterbox"):
            raise ValueError(f"Unknown voiceover engine: {engine}. Use 'kokoro' or 'chatterbox'.")

        # Resolve default voice
        if voice is None:
            if engine == "chatterbox":
                default_voice = os.path.join(os.path.dirname(__file__), "default_male.wav")
                if os.path.isfile(default_voice):
                    voice = default_voice
            else:
                voice = "af_bella"

        # ── Check disk cache ──
        key = _cache_key(text, voice, speed, engine)
        cache_path = os.path.join(_CACHE_DIR, f"{key}.npy")
        cache_meta_path = os.path.join(_CACHE_DIR, f"{key}.meta.npy")

        if cache and os.path.isfile(cache_path) and os.path.isfile(cache_meta_path):
            samples = np.load(cache_path)
            meta = np.load(cache_meta_path)
            cached_sr = int(meta[0])
            print(f"[VoiceOver] Cache hit ({engine}): '{text[:40]}...' (key={key[:8]})")

            # Resample from cached rate to current SAMPLE_RATE if needed
            if cached_sr != SAMPLE_RATE:
                samples = _resample_scipy(samples, cached_sr, SAMPLE_RATE)

            sfx = SoundFX(samples, name=f"voiceover_{engine}")
            return sfx, sfx.duration

        # ── Generate fresh audio ──
        t0 = time.time()
        
        if engine == "chatterbox":
            model = _get_chatterbox()
            if voice and os.path.isfile(voice):
                wav = model.generate(text, audio_prompt_path=voice)
            else:
                wav = model.generate(text)
            
            samples = wav.squeeze().cpu().numpy().astype(np.float32)
            model_sr = _chatterbox_sr or 24000
            
            # Apply speed adjustment via proper resampling for Chatterbox
            if speed != 1.0 and speed > 0:
                effective_sr = int(model_sr * speed)
                samples = _resample_scipy(samples, effective_sr, model_sr)
                
        else: # engine == "kokoro"
            model = _get_kokoro()
            # kokoro handles its own speed mapping
            samples, req_sr = model.create(text, voice=voice, speed=speed, lang="en-us")
            samples = samples.astype(np.float32)
            model_sr = _kokoro_sr

        elapsed = time.time() - t0
        print(f"[VoiceOver] Generated ({engine}): '{text[:40]}...' in {elapsed:.1f}s")

        # Normalize to [-1, 1] range
        peak = np.max(np.abs(samples))
        if peak > 0:
            samples = samples / peak

        # ── Cache to disk (at model's native rate, before final resample) ──
        if cache:
            os.makedirs(_CACHE_DIR, exist_ok=True)
            np.save(cache_path, samples)
            np.save(cache_meta_path, np.array([model_sr], dtype=np.int32))
            print(f"[VoiceOver] Cached: key={key[:8]}")

        # Resample from model's native rate to PixelEngine's SAMPLE_RATE
        if model_sr != SAMPLE_RATE:
            samples = _resample_scipy(samples, model_sr, SAMPLE_RATE)

        sfx = SoundFX(samples, name=f"voiceover_{engine}")
        return sfx, sfx.duration

    @classmethod
    def preload(cls, texts: list, voice: str = None, speed: float = 1.0,
                engine: str = "kokoro"):
        """Batch pre-generate voiceovers to populate cache.

        Call this before construct() to front-load all TTS work.
        Subsequent play_voiceover() calls will hit cache instantly.

        Args:
            texts: List of text strings to pre-generate.
            voice: Optional voice reference for all lines.
            speed: Speed multiplier for all lines.
            engine: "kokoro" or "chatterbox"
        """
        total = len(texts)
        print(f"[VoiceOver] Preloading {total} voiceover(s) using {engine}...")
        for i, text in enumerate(texts, 1):
            _, dur = cls.generate(text, voice=voice, speed=speed, engine=engine)
            print(f"  [{i}/{total}] '{text[:40]}...' → {dur:.2f}s")
        print("[VoiceOver] Preload complete.")

    @classmethod
    def clear_cache(cls):
        """Remove all cached TTS audio files."""
        import shutil
        if os.path.isdir(_CACHE_DIR):
            count = len([f for f in os.listdir(_CACHE_DIR) if f.endswith(".npy")])
            shutil.rmtree(_CACHE_DIR)
            print(f"[VoiceOver] Cleared {count} cached file(s).")
        else:
            print("[VoiceOver] Cache is already empty.")
