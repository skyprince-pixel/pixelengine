"""PixelEngine renderer — encodes frames to video via PyAV or ffmpeg.

Uses PyAV (Python bindings for FFmpeg's C libraries) when available for
fast in-memory encoding. Falls back to ffmpeg subprocess if PyAV is not
installed.
"""
import subprocess
import sys
import time
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from pixelengine.config import PixelConfig

# Try importing PyAV
try:
    import av
    HAS_PYAV = True
except ImportError:
    HAS_PYAV = False


def _progress_bar(current: int, total: int, phase: str, start_time: float,
                  bar_width: int = 30):
    """Print an inline CLI progress bar with ETA."""
    pct = current / total if total > 0 else 1.0
    filled = int(bar_width * pct)
    bar = "█" * filled + "░" * (bar_width - filled)

    elapsed = time.time() - start_time
    if current > 0:
        eta = (elapsed / current) * (total - current)
        fps = current / elapsed if elapsed > 0 else 0
    else:
        eta = 0
        fps = 0

    eta_str = f"{eta:.0f}s" if eta < 120 else f"{eta/60:.1f}m"

    sys.stdout.write(
        f"\r  {phase}: [{bar}] {pct*100:5.1f}% | "
        f"{current}/{total} | "
        f"{fps:.1f} fps | "
        f"ETA: {eta_str}  "
    )
    sys.stdout.flush()

    if current >= total:
        elapsed_str = f"{elapsed:.1f}s" if elapsed < 120 else f"{elapsed/60:.1f}m"
        sys.stdout.write(
            f"\r  {phase}: [{bar}] 100.0% | "
            f"{total}/{total} | "
            f"done in {elapsed_str}       \n"
        )
        sys.stdout.flush()


class Renderer:
    """Encodes a list of PIL Image frames to an MP4 video.

    Uses PyAV when available for 2-3x faster encoding.
    Falls back to ffmpeg subprocess pipe otherwise.
    """

    def __init__(self, config: PixelConfig):
        self.config = config
        if not HAS_PYAV:
            self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Verify ffmpeg is available on the system."""
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "ffmpeg not found! Install PyAV (`pip install av`) or ffmpeg:\n"
                "  macOS:   brew install ffmpeg\n"
                "  Linux:   sudo apt install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )

    def encode(self, frames: list, output_path: str):
        """Encode a list of PIL Image frames to MP4.

        Args:
            frames: List of PIL Images (already upscaled to output resolution).
            output_path: Path for the output video file.
        """
        if not frames:
            raise ValueError("No frames to encode")

        if HAS_PYAV:
            self._encode_pyav(frames, output_path)
        else:
            self._encode_ffmpeg(frames, output_path)

    def _encode_pyav(self, frames: list, output_path: str):
        """Encode using PyAV (in-memory FFmpeg bindings)."""
        width = frames[0].width
        height = frames[0].height
        fps = self.config.fps

        container = av.open(str(output_path), mode='w')
        stream = container.add_stream('libx264', rate=fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'
        stream.options = {'crf': '15', 'preset': 'fast'}

        total = len(frames)
        start_time = time.time()

        for i, frame in enumerate(frames):
            # Convert RGBA → RGB
            if frame.mode == "RGBA":
                rgb_frame = Image.new("RGB", frame.size, (0, 0, 0))
                rgb_frame.paste(frame, mask=frame.split()[3])
                frame = rgb_frame
            elif frame.mode != "RGB":
                frame = frame.convert("RGB")

            # Convert to numpy array and create PyAV frame
            arr = np.array(frame)
            video_frame = av.VideoFrame.from_ndarray(arr, format='rgb24')
            video_frame.pts = i

            for packet in stream.encode(video_frame):
                container.mux(packet)

            _progress_bar(i + 1, total, "Encoding [PyAV]", start_time)

        # Flush encoder
        for packet in stream.encode():
            container.mux(packet)

        container.close()

        output = Path(output_path)
        file_size = output.stat().st_size / 1024
        unit = "KB"
        if file_size > 1024:
            file_size /= 1024
            unit = "MB"
        print(f"  Output: {output_path} ({file_size:.1f} {unit})")

    def _encode_ffmpeg(self, frames: list, output_path: str):
        """Encode using ffmpeg subprocess (fallback)."""
        width = frames[0].width
        height = frames[0].height
        fps = self.config.fps

        cmd = [
            "ffmpeg", "-y",                        # overwrite output
            "-f", "rawvideo",                       # raw input format
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",              # frame dimensions
            "-pix_fmt", "rgb24",                    # input pixel format
            "-r", str(fps),                         # frame rate
            "-i", "-",                              # read from stdin
            "-c:v", "libx264",                      # H.264 codec
            "-pix_fmt", "yuv420p",                  # output pixel format
            "-preset", "fast",                      # encoding speed
            "-crf", "15",                           # quality (lower = better)
            str(output_path),
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        total = len(frames)
        start_time = time.time()

        for i, frame in enumerate(frames):
            # Convert RGBA → RGB (flatten onto black background)
            if frame.mode == "RGBA":
                rgb_frame = Image.new("RGB", frame.size, (0, 0, 0))
                rgb_frame.paste(frame, mask=frame.split()[3])
                frame = rgb_frame
            elif frame.mode != "RGB":
                frame = frame.convert("RGB")

            # Write raw pixel bytes to ffmpeg stdin
            process.stdin.write(frame.tobytes())

            # Update progress bar every frame
            _progress_bar(i + 1, total, "Encoding [ffmpeg]", start_time)

        process.stdin.close()
        process.wait()

        if process.returncode != 0:
            stderr = process.stderr.read().decode()
            raise RuntimeError(f"ffmpeg encoding failed:\n{stderr}")

        output = Path(output_path)
        file_size = output.stat().st_size / 1024
        unit = "KB"
        if file_size > 1024:
            file_size /= 1024
            unit = "MB"
        print(f"  Output: {output_path} ({file_size:.1f} {unit})")
