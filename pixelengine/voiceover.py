"""PixelEngine VoiceOver — AI Text-to-Speech using Chatterbox Turbo.

This module provides high-quality TTS using Resemble AI's Chatterbox Turbo model.
Models are auto-downloaded from HuggingFace on first use (~1.5 GB).

Usage::

    # Generate speech (default voice)
    audio, duration = VoiceOver.generate("Welcome to PixelEngine!")

    # Generate speech with voice cloning (provide a ~10s reference .wav)
    audio, duration = VoiceOver.generate("Welcome!", voice="ref_clip.wav")

    # In a Scene
    self.play_voiceover("Welcome to PixelEngine!")
"""
import os
import numpy as np
import torch

# Lazy-load model to avoid slow imports if unused
_model_instance = None
_model_sr = None  # Sample rate from the model


def _get_device() -> str:
    """Auto-detect best available device: mps (Apple Silicon) > cpu."""
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _get_chatterbox():
    """Get or initialize the Chatterbox Turbo model."""
    global _model_instance, _model_sr
    if _model_instance is not None:
        return _model_instance

    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS, REPO_ID
        from huggingface_hub import snapshot_download
    except ImportError:
        raise ImportError(
            "chatterbox-tts is not installed. Run: pip install chatterbox-tts"
        )

    device = _get_device()
    print(f"[VoiceOver] Downloading/Loading Chatterbox Turbo on device: {device}")
    
    # ChatterboxTurboTTS.from_pretrained hardcodes token=True, which requires an HF login.
    # The repo is public, so we download it directly without a token.
    local_path = snapshot_download(
        repo_id=REPO_ID,
        token=False,  # Bypass HF login requirement
        allow_patterns=["*.safetensors", "*.json", "*.txt", "*.pt", "*.model"]
    )
    
    _model_instance = ChatterboxTurboTTS.from_local(local_path, device=device)
    _model_sr = _model_instance.sr
    print(f"[VoiceOver] Model loaded (sample rate: {_model_sr})")
    return _model_instance


class VoiceOver:
    """Generates synthetic speech using Chatterbox Turbo."""

    @classmethod
    def generate(cls, text: str, voice: str = None, speed: float = 1.0) -> tuple:
        """Generate speech from text.

        Args:
            text: The text to speak. Supports paralinguistic tags:
                  [laugh], [chuckle], [cough] for natural realism.
            voice: Optional path to a ~10s reference .wav file for voice
                   cloning. If None, uses the model's default voice.
            speed: Speech speed multiplier (default 1.0). Values < 1.0 are
                   slower, > 1.0 are faster.

        Returns:
            Tuple of (SoundFX, duration_in_seconds)
        """
        model = _get_chatterbox()

        # Generate audio — returns a torch tensor [1, num_samples]
        if voice is None:
            default_voice = os.path.join(os.path.dirname(__file__), "default_male.wav")
            if os.path.isfile(default_voice):
                voice = default_voice

        if voice and os.path.isfile(voice):
            wav = model.generate(text, audio_prompt_path=voice)
        else:
            wav = model.generate(text)

        # Convert torch tensor to numpy float32
        samples = wav.squeeze().cpu().numpy().astype(np.float32)

        # Normalize to [-1, 1] range
        peak = np.max(np.abs(samples))
        if peak > 0:
            samples = samples / peak

        # Apply speed adjustment via resampling
        if speed != 1.0 and speed > 0:
            original_len = len(samples)
            target_len = int(original_len / speed)
            if target_len > 0:
                indices = np.linspace(0, original_len - 1, target_len).astype(int)
                samples = samples[indices]

        from pixelengine.sound import SoundFX, SAMPLE_RATE

        # Resample from model's native rate to PixelEngine's SAMPLE_RATE (22050)
        model_sr = _model_sr or 24000
        if model_sr != SAMPLE_RATE:
            duration = len(samples) / model_sr
            target_len = int(duration * SAMPLE_RATE)
            if target_len > 0:
                indices = np.linspace(0, len(samples) - 1, target_len).astype(int)
                samples = samples[indices]

        sfx = SoundFX(samples, name="voiceover_chatterbox")
        return sfx, sfx.duration
