<h1 align="center">Video Studio</h1>

<p align="center"><strong>Small Python tools for video post-processing: upscale, merge audio, join parts.</strong></p>

<p align="center">
  <a href="LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/licence-MIT-1f6feb"></a>
  <a href="CHANGELOG.md"><img alt="Version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-1f6feb"></a>
  <img alt="Python 3.7+" src="https://img.shields.io/badge/python-3.7%2B-1f6feb">
  <img alt="No pip dependencies" src="https://img.shields.io/badge/pip%20dependencies-none-1f6feb">
</p>

<p align="center">
  <a href="https://www.unit42.fr/projects">Projects on unit42.fr</a> ·
  <a href="CHANGELOG.md">Changelog</a> ·
  <a href="https://github.com/LightSeek3r/videos-studio/issues">Report an issue</a>
</p>

Video Studio is a set of three command-line tools for working on your own video files. One
upscales animation with the Real-ESRGAN neural network and rebuilds the video with every audio
and subtitle track; the other two drive MKVToolNix to merge the audio tracks of two releases of
the same film, or to join a film that comes in two parts. Each tool is a plain Python script
that uses only the standard library and calls well-known open-source programs to do the heavy
lifting.

**Part of [Unit42](https://www.unit42.fr).** Video Studio is built and maintained by
[LightSeek3r](https://github.com/LightSeek3r) and listed on the
[Unit42 projects page](https://www.unit42.fr/projects). This README is for people who want to
run, read or contribute to the code.

- [The tools](#the-tools)
- [Requirements](#requirements) · [anime-restorer](#anime-restorer) · [movie-audio-merger](#movie-audio-merger) · [movie-concator](#movie-concator)
- [Third-party tools and models](#third-party-tools-and-models) · [Responsible use](#responsible-use)
- [Project structure](#project-structure)
- [Contributing](#contributing) · [Security](#security) · [Versions](#versions) · [Licence](#licence)

## The tools

| Tool | What it does | Calls |
|---|---|---|
| [anime-restorer](anime-restorer/) | Upscales every video in `input/` to 1080p (or any height you set) with Real-ESRGAN, frame by frame on the GPU, and writes the result to `output/` with all audio and subtitle tracks | FFmpeg, ffprobe, realesrgan-ncnn-vulkan |
| [movie-audio-merger](movie-audio-merger/) | Finds two MKV releases of the same film in a folder and builds one file with the first release plus the audio tracks of the second (for example a DDP track and a DTS track) | mkvmerge |
| [movie-concator](movie-concator/) | Finds files that are two parts of one video (`Part1` / `Part2`), lets you tick them in a small window, and joins each pair into one MKV | mkvmerge |

## Requirements

- **Python 3.7 or newer**, nothing to `pip install`: the scripts import only the standard library
  (`tkinter` included, used by movie-concator). The code has been compiled and smoke-run with
  Python 3.13.
- **Windows.** The scripts are written for it: anime-restorer calls
  `vendor/realesrgan-ncnn-vulkan.exe`, and the two MKV tools stage their work in `C:\Temp`.
- The external programs each tool calls, listed below with where to get them.

## anime-restorer

### Setup

1. Install **FFmpeg** so that `ffmpeg` and `ffprobe` are on your `PATH`, for example
   `winget install Gyan.FFmpeg` or a build from [ffmpeg.org](https://ffmpeg.org/download.html).
2. Download `realesrgan-ncnn-vulkan-20220424-windows.zip` from
   [Real-ESRGAN release v0.2.5.0](https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.2.5.0) and
   copy into `anime-restorer/vendor/`:
   - `realesrgan-ncnn-vulkan.exe` and the `.dll` files next to it,
   - the `.bin` weight files from its `models/` folder into `anime-restorer/vendor/models/`
     (the matching `.param` files are already in this repository).
3. A GPU with an up-to-date Vulkan driver (NVIDIA, AMD or Intel). Real-ESRGAN also runs without
   one, much more slowly.

### Run

Put your videos in `anime-restorer/input/`, then double-click `anime-restorer/Restore.bat`, or:

```bash
python anime-restorer/src/main.py
```

The script first checks its dependencies and says exactly what is missing, lists the videos it
found (`.mp4 .mkv .avi .mov .wmv .flv .webm .m4v .mpg .mpeg .ts .vob`), and asks for
confirmation. Restored files land in `anime-restorer/output/` as
`<name>.Restored.1080p.<ext>`; a video whose output already exists is skipped.

### How it works

1. **Probe.** ffprobe reads the resolution, frame rate and number of audio tracks.
2. **Pick a scale.** The smallest Real-ESRGAN factor (2x, 3x or 4x) that reaches the target
   height is used; when it overshoots, FFmpeg scales the result down to the exact height.
3. **Extract.** FFmpeg writes every frame as a PNG into `anime-restorer/temp/`.
4. **Upscale in batches** of 1,000 frames: Real-ESRGAN upscales the batch, FFmpeg encodes it as
   an H.264 segment, and the batch's frames are deleted before the next one.
5. **Samples.** Every 1,000th frame is kept as an original/upscaled pair in
   `anime-restorer/samples/<video name>/`, so you can compare the result.
6. **Assemble.** The segments are joined, then muxed with every audio track of the original
   (re-encoded to AAC 192 kb/s so it stays in sync with the new video) and its subtitle tracks
   (copied as they are).

Plan for plenty of free disk space: step 3 holds every frame of the video as a PNG at once.
`temp/` is emptied as the work progresses.

### Settings

Everything lives in [`anime-restorer/src/config.py`](anime-restorer/src/config.py):

| Setting | Default | What it controls |
|---|---|---|
| `TARGET_HEIGHT` | `1080` | Output height in pixels (`2160` for 4K) |
| `MODEL_NAME` | `realesr-animevideov3` | Real-ESRGAN model, a name from `vendor/models/` |
| `ESRGAN_SCALE_FACTORS` | `[2, 3, 4]` | Factors the model offers. `realesr-animevideov3` comes in x2, x3 and x4; the `realesrgan-x4plus` models only in x4, so use `[4]` with them |
| `ESRGAN_OUTPUT_FORMAT` | `jpg` | Format of the upscaled frames (`png` is lossless and slower) |
| `VIDEO_CODEC` / `PIXEL_FORMAT` | `libx264` / `yuv420p` | Output video encoding |
| `OUTPUT_SUFFIX` | `Restored` | Text added to output file names |
| `BATCH_SIZE` | `1000` | Frames upscaled per batch |
| `SAMPLE_INTERVAL` | `1000` | One sample pair every N frames |
| `FPS_FALLBACK` | `23.976` | Frame rate used when ffprobe cannot read one |

## movie-audio-merger

Needs [MKVToolNix](https://mkvtoolnix.download/) with `mkvmerge` on your `PATH`, and an existing
`C:\Temp` folder.

Open a terminal in the folder that holds the two releases and run the script from there (or
copy it into that folder and double-click it):

```bash
python path/to/movie-audio-merger/MovieAudioMerger.py
```

- **Pairing.** Two files form a pair when the text before the first four-digit number (the year)
  and the year itself are identical, and the rest of their names is at least 90 % similar.
  Subtitle and text files (`.ass .srt .ssa .txt`) and unfinished downloads (`.!ut .!bt`) are left
  out.
- **Choosing.** Each pair is shown in turn: press Enter to process it, or type `n` to skip it.
- **Merging.** Both files are copied to `C:\Temp`, and `mkvmerge` writes a file with everything
  from the first one plus the audio tracks of the second (`--no-video --no-subtitles`). The
  result is named after the common parts of the two names with `DDPxDTS` in between, copied back
  next to the originals, and the copies in `C:\Temp` are deleted.

## movie-concator

Needs [MKVToolNix](https://mkvtoolnix.download/) with `mkvmerge` on your `PATH`, and an existing
`C:\Temp` folder.

Open a terminal in the folder that holds the parts and run:

```bash
python path/to/movie-concator/MovieConcator.py
```

- **Pairing.** Two files form a pair when their names have the same length and the first
  character that differs is a digit in both, as in `Film.Part1.mkv` and `Film.Part2.mkv`. The
  same subtitle, text and download extensions as above are left out.
- **Choosing.** A small window lists the pairs with a checkbox each; tick the ones to join and
  click **Confirm Selection**.
- **Joining.** As above, the work happens in `C:\Temp`: `mkvmerge` appends the second file to the
  first (`file1 + file2`), and the result, named with `Assembled` in place of the differing part,
  is copied back next to the originals.

## Third-party tools and models

Video Studio drives these programs and includes none of them, apart from the Real-ESRGAN
`.param` model files described in [NOTICE](NOTICE). Each keeps its own licence.

| Component | Used by | Licence | Source |
|---|---|---|---|
| FFmpeg and ffprobe | anime-restorer | LGPL 2.1 or later; some builds GPL | [ffmpeg.org/legal](https://ffmpeg.org/legal.html) |
| realesrgan-ncnn-vulkan | anime-restorer | MIT | [xinntao/Real-ESRGAN-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) |
| Real-ESRGAN models (`.param` here, `.bin` from the release) | anime-restorer | BSD 3-Clause | [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) |
| MKVToolNix (`mkvmerge`) | movie-audio-merger, movie-concator | GPL 2.0 | [mkvtoolnix.download](https://mkvtoolnix.download/) |
| Python and its standard library (`tkinter`) | all | PSF licence | [python.org](https://www.python.org/downloads/) |

## Responsible use

Process only media you own or have the rights to work with. Upscaling, merging or joining a
file creates a new copy of the work: keep it for your own use unless its licence allows
more. This repository holds code, documentation and model descriptions only, and its
`.gitignore` keeps video files out of it.

## Project structure

```
anime-restorer/
  Restore.bat           double-click launcher (runs src/main.py)
  src/
    main.py               finds the videos, asks for confirmation, prints a summary
    config.py             paths and every setting
    dependencies.py       checks Python, FFmpeg, ffprobe, the Real-ESRGAN binary and the GPU
    utils.py              ffprobe helpers, scale factor choice, file discovery
    video_processor.py    extract, upscale in batches, encode segments, assemble
  input/  output/       your videos in and out (git-ignored apart from .gitkeep)
  vendor/models/        Real-ESRGAN .param files and their LICENSE; the .exe, .dll and .bin go in vendor/
movie-audio-merger/
  MovieAudioMerger.py   pair detection and mkvmerge audio merge
movie-concator/
  MovieConcator.py      pair detection, tkinter picker and mkvmerge append
VERSION                 the current version
```

## Contributing

Bug reports, ideas and small pull requests are welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) first: it says how to run the tools and what to check before
sending a change. Questions can go in an
[issue](https://github.com/LightSeek3r/videos-studio/issues) too.

## Security

Please do not open a public issue for a vulnerability. [SECURITY.md](SECURITY.md) says how to
report one privately. The repository holds no secrets and the tools make no network requests.

## Versions

The version in [`VERSION`](VERSION) and the `vX.Y.Z` git tags follow
[Semantic Versioning](https://semver.org) loosely while the project is 0.x. Notable changes are
listed in [CHANGELOG.md](CHANGELOG.md) and each tag has a
[GitHub release](https://github.com/LightSeek3r/videos-studio/releases).

## Licence

The source code is released under the [MIT licence](LICENSE). It covers the code written for
Video Studio only. FFmpeg, Real-ESRGAN and its models, realesrgan-ncnn-vulkan and MKVToolNix
keep their own licences (see [Third-party tools and models](#third-party-tools-and-models) and
[NOTICE](NOTICE)), and the videos you process keep theirs.
