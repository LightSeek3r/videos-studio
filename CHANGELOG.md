# Changelog

All notable changes to Video Studio are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the versions follow
[Semantic Versioning](https://semver.org) loosely while the project is 0.x.

## [0.1.0] - 2026-10-17

The first tagged version, published as open source under the MIT licence. It covers everything
since the repository started on 2026-03-10.

### Added

- **movie-concator**: finds the two parts of a video by their names, lets you pick pairs in a
  small tkinter window, and joins each pair into one MKV with `mkvmerge` (10 March).
- **movie-audio-merger**: finds two releases of the same film by title, year and name
  similarity, and builds one MKV with the first release plus the audio tracks of the second
  (10 March).
- **anime-restorer**: Real-ESRGAN upscaling to a target height through realesrgan-ncnn-vulkan,
  with a dependency check, batches of 1,000 frames to bound disk use, sample frame pairs for
  comparison, and every audio and subtitle track carried over; `Restore.bat` launcher and the
  Real-ESRGAN `.param` model files (26 May).
- **Open-source release** (17 October): MIT licence, NOTICE crediting Real-ESRGAN for the model
  files, `VERSION` file, this changelog, contributing guide, security policy, code of conduct,
  issue and pull request templates, and a README covering setup, usage, the third-party tools
  and their licences.

### Changed

- The README describes all three tools (26 May) and was rewritten for the public release
  (17 October).
- `.gitignore` keeps Python caches, virtual environments, video files and local notes out of the
  repository (17 October).

### Fixed

- The ASCII art banner of anime-restorer spells "Video Remaster" correctly (29 August).

[0.1.0]: https://github.com/LightSeek3r/videos-studio/releases/tag/v0.1.0
