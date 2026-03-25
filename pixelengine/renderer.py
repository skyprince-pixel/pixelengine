"""PixelEngine renderer — encodes frames to video via ffmpeg."""
import subprocess
import shutil
from pathlib import Path
from PIL import Image
from pixelengine.config import PixelConfig


class Renderer:
    """Encodes a list of PIL Image frames to an MP4 video using ffmpeg."""

    def __init__(self, config: PixelConfig):
        self.config = config
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Verify ffmpeg is available on the system."""
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "ffmpeg not found! Install it:\n"
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

        output = Path(output_path)
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
            "-crf", "18",                           # quality (lower = better)
            str(output_path),
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        total = len(frames)
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

            # Progress indicator (every 5 seconds of video or last frame)
            if (i + 1) % (fps * 5) == 0 or i == total - 1:
                seconds = (i + 1) / fps
                pct = int((i + 1) / total * 100)
                print(f"  Encoding: {seconds:.1f}s — {pct}% ({i+1}/{total} frames)")

        process.stdin.close()
        process.wait()

        if process.returncode != 0:
            stderr = process.stderr.read().decode()
            raise RuntimeError(f"ffmpeg encoding failed:\n{stderr}")

        file_size = output.stat().st_size / 1024
        unit = "KB"
        if file_size > 1024:
            file_size /= 1024
            unit = "MB"
        print(f"  Output: {output_path} ({file_size:.1f} {unit})")
