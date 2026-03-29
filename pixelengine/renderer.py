"""PixelEngine renderer — encodes frames to video via PyAV or ffmpeg.

Uses PyAV (Python bindings for FFmpeg's C libraries) when available for
fast in-memory encoding. Falls back to ffmpeg subprocess if PyAV is not
installed.
"""
import subprocess
import shutil
from PIL import Image
import numpy as np
from pixelengine.config import PixelConfig

# Try importing PyAV
try:
    import av
    # Disabled by default on macOS due to QuickTime moov atom / H264 profile issues
    # The ffmpeg subprocess is more reliable for valid .mp4 files
    HAS_PYAV = False
except ImportError:
    HAS_PYAV = False



class Renderer:
    """Streams PIL Image frames into an MP4 video.

    Uses PyAV when available for 2-3x faster encoding.
    Falls back to ffmpeg subprocess pipe otherwise.
    """

    def __init__(self, config: PixelConfig):
        self.config = config
        self._container = None
        self._stream = None
        self._process = None
        self._width = 0
        self._height = 0
        self._output_path = None
        self._frame_count = 0
        
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

    def open(self, output_path: str, width: int, height: int):
        """Open the video encoder stream."""
        self._output_path = output_path
        self._width = width
        self._height = height
        self._frame_count = 0
        
        if HAS_PYAV:
            self._open_pyav()
        else:
            self._open_ffmpeg()

    def add_frame(self, frame: Image.Image):
        """Add a single frame to the video stream."""
        if HAS_PYAV:
            self._add_frame_pyav(frame)
        else:
            self._add_frame_ffmpeg(frame)
        self._frame_count += 1

    def close(self):
        """Close the encoder and finalize the video file."""
        if HAS_PYAV:
            self._close_pyav()
        else:
            self._close_ffmpeg()

    def _open_pyav(self):
        """Initialize PyAV (in-memory FFmpeg bindings)."""
        self._container = av.open(str(self._output_path), mode='w')
        self._stream = self._container.add_stream('libx264', rate=self.config.fps)
        self._stream.width = self._width
        self._stream.height = self._height
        self._stream.pix_fmt = 'yuv420p'
        self._stream.options = {'crf': '15', 'preset': 'fast'}

    def _add_frame_pyav(self, frame: Image.Image):
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
        video_frame.pts = self._frame_count

        for packet in self._stream.encode(video_frame):
            self._container.mux(packet)

    def _close_pyav(self):
        # Flush encoder
        for packet in self._stream.encode():
            self._container.mux(packet)
        self._container.close()

    def _open_ffmpeg(self):
        """Initialize ffmpeg subprocess (fallback)."""
        cmd = [
            "ffmpeg", "-y",                        # overwrite output
            "-f", "rawvideo",                       # raw input format
            "-vcodec", "rawvideo",
            "-s", f"{self._width}x{self._height}",  # frame dimensions
            "-pix_fmt", "rgb24",                    # input pixel format
            "-r", str(self.config.fps),             # frame rate
            "-i", "-",                              # read from stdin
            "-c:v", "libx264",                      # H.264 codec
            "-pix_fmt", "yuv420p",                  # output pixel format
            "-preset", "fast",                      # encoding speed
            "-crf", "15",                           # quality
            str(self._output_path),
        ]

        self._process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def _add_frame_ffmpeg(self, frame: Image.Image):
        # Convert RGBA → RGB (flatten onto black background)
        if frame.mode == "RGBA":
            rgb_frame = Image.new("RGB", frame.size, (0, 0, 0))
            rgb_frame.paste(frame, mask=frame.split()[3])
            frame = rgb_frame
        elif frame.mode != "RGB":
            frame = frame.convert("RGB")

        # Write raw pixel bytes to ffmpeg stdin
        self._process.stdin.write(frame.tobytes())

    def _close_ffmpeg(self):
        self._process.stdin.close()
        self._process.wait()

        if self._process.returncode != 0:
            stderr = self._process.stderr.read().decode()
            raise RuntimeError(f"ffmpeg encoding failed:\n{stderr}")
