"""
Utility functions — ffprobe helpers, file discovery, directory management.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Optional, Tuple

from config import (
    FPS_FALLBACK,
    INPUT_DIR,
    VIDEO_EXTENSIONS,
)


def get_fps(video_path: str) -> float:
    """Extract the frame rate from a video file using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=r_frame_rate",
                "-of", "json",
                video_path,
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        fps_str = data["streams"][0]["r_frame_rate"]
        num, den = map(int, fps_str.split("/"))
        fps = num / den
        print(f"  Detected FPS: {fps:.3f}")
        return fps
    except Exception as e:
        print(f"  FPS detection failed ({e}), using fallback: {FPS_FALLBACK}")
        return FPS_FALLBACK


def get_resolution(video_path: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract width and height from a video file using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                video_path,
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        stream = data["streams"][0]
        return stream["width"], stream["height"]
    except Exception as e:
        print(f"  Resolution detection failed: {e}")
        return None, None


def get_audio_stream_count(video_path: str) -> int:
    """Count how many audio streams exist in a video file."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "a",
                "-show_entries", "stream=index",
                "-of", "json",
                video_path,
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        return len(data.get("streams", []))
    except Exception:
        return 0


def calculate_scale_factor(current_height: int, target_height: int) -> Tuple[int, float]:
    """
    Find the best ESRGAN scale factor to reach (or exceed) the target height,
    then compute the ffmpeg resize ratio to hit the target exactly.

    Strategy: pick the smallest ESRGAN factor that reaches or exceeds target.
    If no factor reaches target, use the largest available.

    Returns (esrgan_factor, ffmpeg_resize_ratio).
    ratio < 1.0 means pre-downscale before ESRGAN (source overflows).
    ratio == 1.0 means perfect fit.
    ratio > 1.0 should not happen — we always overshoot or match.
    """
    from config import ESRGAN_SCALE_FACTORS

    # Find smallest factor where current_height * factor >= target
    viable = [f for f in sorted(ESRGAN_SCALE_FACTORS) if current_height * f >= target_height]

    if viable:
        best_esrgan = viable[0]  # smallest that reaches target
    else:
        best_esrgan = max(ESRGAN_SCALE_FACTORS)  # can't reach target, use max

    upscaled_height = current_height * best_esrgan
    ffmpeg_ratio = target_height / upscaled_height
    return best_esrgan, ffmpeg_ratio


def discover_videos(directory: str = None) -> list[str]:
    """Find all video files in the given directory (non-recursive)."""
    directory = directory or INPUT_DIR
    if not os.path.isdir(directory):
        return []
    videos = []
    for fname in sorted(os.listdir(directory)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            videos.append(os.path.join(directory, fname))
    return videos


def clear_directory(directory: str) -> None:
    """Remove all files in a directory (but keep the directory itself)."""
    if not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
        return
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)
        elif os.path.isdir(fpath):
            shutil.rmtree(fpath)


def ensure_directories(*dirs: str) -> None:
    """Create directories if they don't exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs}s"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours}h {mins}m {secs}s"
