# anime-restorer

Upscales videos to 1080p (or any height you set) with [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
on the GPU, and rebuilds each one with all of its audio and subtitle tracks.

## Quick start

1. Install FFmpeg and put `realesrgan-ncnn-vulkan.exe` (with its `.dll` files) in `vendor/` and the
   model `.bin` files in `vendor/models/`. The [main README](../README.md#anime-restorer) has the
   download links.
2. Place your videos in **`input/`**.
3. Double-click **`Restore.bat`** (or run `python src/main.py`).
4. Pick up the restored videos in **`output/`**, and compare sample frames in `samples/`.

The script checks its dependencies first and says exactly what is missing.

## Settings

Edit [`src/config.py`](src/config.py): `TARGET_HEIGHT` (`1080`, or `2160` for 4K), `MODEL_NAME`
(`realesr-animevideov3`), `OUTPUT_SUFFIX`, `BATCH_SIZE` and the rest are described in the
[main README](../README.md#settings).

## Layout

```
anime-restorer/
  Restore.bat           double-click launcher
  input/                place videos here
  output/               restored videos appear here
  samples/              original/upscaled frame pairs, one every 1,000 frames
  src/
    main.py               entry point
    config.py             settings
    dependencies.py       checks Python, FFmpeg, ffprobe, Real-ESRGAN and the GPU
    video_processor.py    extract, upscale in batches, assemble
    utils.py              ffprobe helpers, file discovery
  vendor/               realesrgan-ncnn-vulkan and its models
  temp/                 working directory, emptied as the work progresses
```

Frames are extracted as PNG files before upscaling, so keep plenty of free disk space.
