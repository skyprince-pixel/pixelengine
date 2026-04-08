"""PixelEngine parallel renderer — multi-core frame rendering.

Splits the frame range across CPU cores for significant speedup on
multi-core machines. Each worker re-runs construct() to rebuild scene
state, then renders only its assigned frame range to a temporary file.
The main process concatenates the chunks via ffmpeg.

Usage::

    scene = MyScene()
    scene.render(parallel=True)            # auto-detect cores
    scene.render(parallel=True, workers=4) # explicit worker count

Architecture:
    1. Main process runs construct() once to determine total frame count
    2. Frame range is split into N chunks (one per worker)
    3. Each worker subprocess re-runs construct() but only captures
       frames in its assigned range (skipping others)
    4. Workers write raw RGB frames to temporary files
    5. Main process concatenates chunks and pipes to ffmpeg
"""
import os
import sys
import time
import tempfile
import struct
import multiprocessing
from PIL import Image

from pixelengine.config import PixelConfig
from pixelengine.renderer import Renderer, get_codec_info


def _count_frames(scene_cls, config):
    """Run construct() in counting mode to determine total frames."""
    scene = scene_cls(config=config)
    scene._counting_mode = True
    scene._frame_count = 0

    # Patch _capture_frame to just count
    original_capture = scene._capture_frame

    def counting_capture():
        scene._frame_count += 1
        scene._current_time += 1.0 / config.fps

    scene._capture_frame = counting_capture

    try:
        scene.construct()
    except Exception:
        pass

    return scene._frame_count


def _render_chunk(args):
    """Worker function: render a range of frames to a temp file.

    Args:
        args: Tuple of (scene_cls_name, scene_module, config_dict,
              chunk_start, chunk_end, output_path, worker_id)
    """
    scene_cls_name, scene_module_name, config_dict, chunk_start, chunk_end, output_path, worker_id = args

    # Reconstruct config
    config = PixelConfig(**config_dict)

    # Import the scene class
    import importlib
    module = importlib.import_module(scene_module_name)
    scene_cls = getattr(module, scene_cls_name)

    # Build scene
    scene = scene_cls(config=config)
    scene.auto_sound = False  # No audio in workers
    scene._frame_count = 0
    scene._current_time = 0
    scene._renderer = None

    # Collect frames in our range
    frames_data = []
    global_frame = [0]

    original_capture = scene.__class__._capture_frame

    def selective_capture(self_inner):
        frame_idx = global_frame[0]
        global_frame[0] += 1

        # Always advance time
        dt = 1.0 / config.fps
        self_inner._current_time += dt
        self_inner.camera.update(dt)

        # Run updaters
        for obj in list(self_inner._objects):
            if hasattr(obj, '_fps'):
                obj._fps = config.fps
            if hasattr(obj, '_updaters') and obj._updaters:
                for updater in list(obj._updaters):
                    try:
                        updater(obj, dt)
                    except Exception:
                        pass

        if frame_idx < chunk_start or frame_idx >= chunk_end:
            self_inner._frame_count += 1
            return

        # Render this frame
        self_inner.canvas.clear()
        sorted_objects = sorted(self_inner._objects, key=lambda o: o.z_index)

        for obj in sorted_objects:
            if not obj.visible:
                continue
            self_inner._render_object(obj)

        # Lighting
        if self_inner._lights:
            self_inner._lighting_engine.apply(self_inner.canvas, self_inner._lights, sorted_objects)

        frame = self_inner.canvas.get_frame(config.upscale)

        # Camera FX
        if self_inner._camera_fx.count > 0:
            frame = self_inner._camera_fx.apply(frame)

        frames_data.append(frame)
        self_inner._frame_count += 1

    # Monkey-patch _capture_frame
    scene._capture_frame = lambda: selective_capture(scene)

    try:
        scene.construct()
    except Exception:
        pass

    # Write frames to temp file as raw RGB
    with open(output_path, 'wb') as f:
        for frame_img in frames_data:
            if frame_img.mode == "RGBA":
                rgb = Image.new("RGB", frame_img.size, (0, 0, 0))
                rgb.paste(frame_img, mask=frame_img.split()[3])
                frame_img = rgb
            elif frame_img.mode != "RGB":
                frame_img = frame_img.convert("RGB")
            f.write(frame_img.tobytes())

    return len(frames_data)


class ParallelRenderer:
    """Multi-core parallel frame renderer.

    Splits rendering across worker processes for significant speedup.

    Usage::

        renderer = ParallelRenderer(MyScene, config=PixelConfig.landscape())
        renderer.render("output.mp4", workers=4)
    """

    def __init__(self, scene_cls, config: PixelConfig = None):
        self.scene_cls = scene_cls
        self.config = config or PixelConfig()

    def render(self, output_path: str, workers: int = None,
               on_progress=None):
        """Render the scene using parallel workers.

        Args:
            output_path: Output video file path.
            workers: Number of worker processes (None = auto-detect).
            on_progress: Optional callback(stage, detail).
        """
        if workers is None:
            workers = max(1, multiprocessing.cpu_count() - 1)
        workers = max(1, workers)

        start_time = time.time()

        # Step 1: Count total frames
        if on_progress:
            on_progress("counting", "Counting total frames...")
        print(f"[PixelEngine] Parallel render: counting frames...")

        total_frames = _count_frames(self.scene_cls, self.config)
        if total_frames == 0:
            print("[PixelEngine] Warning: No frames to render!")
            return

        print(f"[PixelEngine] Total frames: {total_frames}, workers: {workers}")

        # Step 2: Split into chunks
        chunk_size = max(1, total_frames // workers)
        chunks = []
        for i in range(workers):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, total_frames)
            if i == workers - 1:
                end = total_frames  # Last worker gets remainder
            if start < end:
                chunks.append((start, end))

        # Step 3: Prepare worker args
        scene_module = self.scene_cls.__module__
        scene_name = self.scene_cls.__name__
        config_dict = {
            'canvas_width': self.config.canvas_width,
            'canvas_height': self.config.canvas_height,
            'upscale': self.config.upscale,
            'fps': self.config.fps,
            'output_format': self.config.output_format,
            'codec': self.config.codec,
            'background_color': self.config.background_color,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            worker_args = []
            chunk_files = []
            for i, (start, end) in enumerate(chunks):
                chunk_path = os.path.join(tmpdir, f"chunk_{i:04d}.raw")
                chunk_files.append(chunk_path)
                worker_args.append((
                    scene_name, scene_module, config_dict,
                    start, end, chunk_path, i,
                ))

            # Step 4: Run workers
            if on_progress:
                on_progress("rendering", f"Rendering {len(chunks)} chunks across {workers} workers...")
            print(f"[PixelEngine] Rendering {len(chunks)} chunks...")

            with multiprocessing.Pool(workers) as pool:
                results = pool.map(_render_chunk, worker_args)

            rendered = sum(results)
            print(f"[PixelEngine] All chunks complete: {rendered} frames rendered")

            # Step 5: Concatenate and encode
            if on_progress:
                on_progress("encoding", "Encoding video...")
            print(f"[PixelEngine] Encoding video...")

            width = self.config.output_width
            height = self.config.output_height
            frame_bytes = width * height * 3

            renderer = Renderer(self.config)
            renderer.open(output_path, width, height)

            for chunk_path in chunk_files:
                if not os.path.exists(chunk_path):
                    continue
                with open(chunk_path, 'rb') as f:
                    while True:
                        data = f.read(frame_bytes)
                        if len(data) < frame_bytes:
                            break
                        img = Image.frombytes("RGB", (width, height), data)
                        renderer.add_frame(img)

            renderer.close()

        elapsed = time.time() - start_time
        size_kb = os.path.getsize(output_path) / 1024
        print(
            f"[PixelEngine] Parallel render complete: {output_path} "
            f"({size_kb:.1f} KB, {elapsed:.1f}s, {rendered/elapsed:.1f} fps)"
        )
