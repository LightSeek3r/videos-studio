# Video Remaster

Upscale videos to 1080p (or 4K) using [RealESRGAN](https://github.com/xinntao/Real-ESRGAN) with GPU acceleration.

## Quick Start

1. Place your video files in the **`input/`** folder
2. Double-click **`Restore.bat`**
3. Pick up your restored videos from the **`output/`** folder

That's it. The script auto-detects resolution, frame rate, and audio streams.

## Requirements

| Tool | Required | Install |
|------|----------|---------|
| **Python 3.7+** | Yes | [python.org](https://www.python.org/downloads/) — check "Add to PATH" |
| **FFmpeg** | Yes | `winget install Gyan.FFmpeg` or [ffmpeg.org](https://ffmpeg.org/download.html) |
| **GPU (Vulkan)** | Recommended | NVIDIA or AMD GPU with up-to-date drivers |

The `Restore.bat` script will check for missing dependencies and tell you exactly what to install.

## What it Does

1. Extracts frames from each video via FFmpeg
2. Upscales frames using RealESRGAN (neural network super-resolution)
3. Reconstructs the video with all original audio streams and subtitles preserved
4. Cleans up temporary files automatically

## Settings

Edit [`src/config.py`](src/config.py) to change:

- **`TARGET_HEIGHT`** — output resolution (default: `1080` for 1080p, set to `2160` for 4K)
- **`MODEL_NAME`** — RealESRGAN model (default: `realesr-animevideov3`)
- **`OUTPUT_SUFFIX`** — text appended to output filenames

## Project Structure

```
video-remaster/
├── Restore.bat          # Double-click to run
├── input/               # Place videos here
├── output/              # Restored videos appear here
├── src/                 # Application code
│   ├── main.py          # Entry point
│   ├── config.py        # Settings
│   ├── dependencies.py  # Auto-checks for ffmpeg, python, GPU
│   ├── video_processor.py  # Core upscaling pipeline
│   └── utils.py         # Helpers (ffprobe, file discovery)
├── vendor/              # RealESRGAN binaries & models
└── temp/                # Auto-cleaned working directory
```

## Notes

- **Disk space**: Frame extraction requires ~3-4x the original video size in temporary storage. Files are cleaned up after each video.
- **Processing time**: Depends on video length, resolution, and GPU. A 1080p target from 480p source on a mid-range GPU takes roughly real-time to 3x video duration.
- **Audio**: All audio streams from the original file are preserved automatically. No separate audio merging step needed.
