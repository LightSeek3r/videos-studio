# videos-studio

A collection of Python utilities for video post-processing — upscaling, audio merging, and concatenation.

## Tools

| Tool | What it does |
|------|-------------|
| [anime-restorer](anime-restorer/) | Upscales anime videos to 1080p or 4K using RealESRGAN neural-network super-resolution |
| [movie-audio-merger](movie-audio-merger/) | Merges audio tracks from two MKV releases of the same film into one file (e.g. DDP + DTS) |
| [movie-concator](movie-concator/) | Concatenates two MKV files that belong together (e.g. a movie split across two parts) |

---

## anime-restorer

Upscales videos to 1080p (or 4K) using [RealESRGAN](https://github.com/xinntao/Real-ESRGAN) with GPU acceleration via Vulkan.

### Quick start

1. Place video files in `anime-restorer/input/`
2. Double-click `anime-restorer/Restore.bat`
3. Collect restored videos from `anime-restorer/output/`

The script auto-detects resolution, frame rate, and audio streams. All original audio tracks and subtitles are preserved.

### Requirements

| Tool | Install |
|------|---------|
| Python 3.7+ | [python.org](https://www.python.org/downloads/) — check "Add to PATH" |
| FFmpeg | `winget install Gyan.FFmpeg` |
| GPU with Vulkan | NVIDIA or AMD with up-to-date drivers (CPU fallback is very slow) |

`Restore.bat` checks for missing dependencies and reports exactly what is needed.

### How it works

1. Extracts frames from each video with FFmpeg
2. Upscales frames in batches using RealESRGAN
3. Reconstructs the video and muxes back all original audio/subtitle streams
4. Cleans up temporary files automatically

### Configuration

Edit [`anime-restorer/src/config.py`](anime-restorer/src/config.py):

| Setting | Default | Description |
|---------|---------|-------------|
| `TARGET_HEIGHT` | `1080` | Output height in pixels (`2160` for 4K) |
| `MODEL_NAME` | `realesr-animevideov3` | RealESRGAN model |
| `OUTPUT_SUFFIX` | `Restored` | Text appended to output filenames |
| `BATCH_SIZE` | `1000` | Frames processed per batch (controls peak disk usage) |

### Notes

- Frame extraction needs roughly 3–4× the source video size in temporary disk space.
- Processing speed depends on video length, source resolution, and GPU. A 480p-to-1080p upscale on a mid-range GPU runs at approximately real-time to 3× video duration.

---

## movie-audio-merger

Merges the audio tracks of two MKV files that share the same video — useful when one release has DDP audio and another has DTS (or any other combination).

### Quick start

1. Copy `MovieAudioMerger.py` into the folder that contains the two MKV files
2. Run it (double-click or `python MovieAudioMerger.py`)
3. The script auto-detects matching file pairs by comparing name prefixes and release year, presents them for confirmation, then calls `mkvmerge` to produce a merged `.mkv`

### Requirements

- Python 3.7+
- [MKVToolNix](https://mkvtoolnix.download/) (`mkvmerge` must be on PATH)

### Pair detection logic

Two files are considered a pair when they share the same title prefix and year, and their suffixes are at least 90 % similar (measured by sequence matching). The output filename is auto-generated from the common parts of the two input names (`…DDPxDTS….mkv`).

---

## movie-concator

Concatenates two MKV files in sequence — useful when a film or episode was split into two separate parts.

### Quick start

1. Copy `MovieConcator.py` into the folder that contains the two MKV files
2. Run it (double-click or `python MovieConcator.py`)
3. A small GUI lists detected file pairs; select the ones to merge and click **Confirm Selection**
4. `mkvmerge` produces a single `.mkv` with the suffix `Assembled`

### Requirements

- Python 3.7+
- [MKVToolNix](https://mkvtoolnix.download/) (`mkvmerge` must be on PATH)

### Pair detection logic

Two files are considered a pair when they have identical lengths and differ by exactly one digit character in their name (e.g. `MovieTitle.Part1.mkv` / `MovieTitle.Part2.mkv`).

---

## Dependencies at a glance

| Dependency | Used by | Install |
|------------|---------|---------|
| Python 3.7+ | All tools | [python.org](https://www.python.org/downloads/) |
| FFmpeg | anime-restorer | `winget install Gyan.FFmpeg` |
| MKVToolNix | movie-audio-merger, movie-concator | [mkvtoolnix.download](https://mkvtoolnix.download/) |
| GPU (Vulkan) | anime-restorer | NVIDIA / AMD drivers |
