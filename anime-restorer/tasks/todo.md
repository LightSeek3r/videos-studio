# Video Remaster — Rearchitecture Plan

## Problem Analysis

### Current Issues
1. **Nested structure**: Everything lives inside `realesrgan-ncnn-vulkan-20220424-windows/` — a vendor folder name that shouldn't be the project root
2. **Two separate workflows**: Video restoration (.bat → Python) and audio merging (.bat → PowerShell) are disconnected
3. **No dependency management**: Assumes ffmpeg, Python, MKVToolNix are already installed, no checks
4. **Massive disk footprint**: Extracts ALL frames as PNGs before processing — a 2hr video at 24fps = ~172,800 PNG files
5. **Hardcoded paths**: MKVToolNix path hardcoded, model names hardcoded
6. **No cleanup**: Temp frames left on disk after processing
7. **Fragile code**: No error handling on subprocess calls, no validation, calculate_factors always returns first factor
8. **Audio merger is MKV-only**: PowerShell GUI-based, won't work in batch mode
9. **Leftover frame artifacts** in root directory

### Architecture Goals
- **Single entry point**: Drop files in `input/`, double-click `Restore.bat`, get results in `output/`
- **Unified pipeline**: Video upscaling + audio preservation in one pass
- **Dependency auto-detection**: Check for ffmpeg, Python; prompt for install if missing
- **Disk-efficient**: Process in chunks, clean up temp files progressively
- **Robust**: Proper error handling, progress reporting, resume capability
- **Clean structure**: Vendor binaries separated from application code

## New Directory Structure

```
video-remaster/
├── Restore.bat                 # Single entry point — double-click this
├── README.md                   # Clear user instructions
├── CLAUDE.md                   # AI workflow instructions (keep)
├── input/                      # User drops videos here
├── output/                     # Restored videos appear here
├── src/                        # Application code
│   ├── main.py                 # Orchestrator
│   ├── config.py               # All settings & constants
│   ├── dependencies.py         # Dependency checker & installer prompts
│   ├── video_processor.py      # Frame extraction, upscaling, reconstruction
│   └── utils.py                # Shared utilities (fps detection, resolution, etc.)
├── vendor/                     # Third-party binaries (RealESRGAN)
│   ├── realesrgan-ncnn-vulkan.exe
│   ├── vcomp140.dll
│   ├── vcomp140d.dll
│   └── models/                 # ESRGAN model files
│       ├── *.param
│       └── *.bin
├── temp/                       # Transient (auto-cleaned)
│   ├── frames_in/
│   └── frames_out/
└── tasks/                      # Project management
```

## Implementation Steps

- [x] Write architecture plan
- [ ] Create directory structure & move vendor binaries
- [ ] Implement `src/config.py` — settings, paths, constants
- [ ] Implement `src/dependencies.py` — check ffmpeg, python, warn about GPU
- [ ] Implement `src/utils.py` — ffprobe helpers, file discovery
- [ ] Implement `src/video_processor.py` — core pipeline (extract → upscale → merge)
- [ ] Implement `src/main.py` — orchestrator with progress & error handling
- [ ] Create `Restore.bat` — dependency check + launch
- [ ] Write `README.md`
- [ ] Verify end-to-end
- [ ] Clean up old structure

## Key Design Decisions

1. **Audio handling**: ffmpeg already copies audio in the merge step (-map 1:a). For multi-audio MKV files, we'll map ALL audio streams, not just the first. This eliminates the need for a separate audio merger step for most cases.
2. **Disk space**: We keep the frame-based approach (RealESRGAN requires it), but clean temp frames after each video.
3. **Scale calculation fix**: Current `calculate_factors` always returns the first factor (2x). Need to find the optimal factor that gets closest to target resolution.
4. **Model selection**: Default to `realesr-animevideov3` but allow user to pick from available models via config.
5. **No chunked processing for now**: RealESRGAN processes frame-by-frame internally. The bottleneck is disk space for extracted frames. We'll add progress tracking and cleanup.
