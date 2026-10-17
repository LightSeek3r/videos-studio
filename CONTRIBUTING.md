# Contributing to Video Studio

Thanks for taking an interest. Video Studio is a small, one-person project, so the process is light.

## Reporting a problem

- **A bug or an idea:** open an [issue](https://github.com/LightSeek3r/videos-studio/issues/new/choose)
  and pick the matching template. Say which tool, your Windows and Python versions, the versions
  of FFmpeg or MKVToolNix, and paste the console output.
- **A security problem:** do not use an issue. See [SECURITY.md](SECURITY.md).

Please never attach video files or frames from them: describe the file instead (container,
resolution, frame rate, audio and subtitle tracks, as `ffprobe` or `mkvmerge -i` reports them).

## Running the tools

See the [README](README.md). The scripts need Python 3.7 or newer and nothing from pip; each tool
needs its external programs (FFmpeg and realesrgan-ncnn-vulkan for anime-restorer, MKVToolNix for
the other two).

## Sending a pull request

1. Open an issue first for anything larger than a fix, so we agree on the direction.
2. Branch from `main`, keep the change small and focused.
3. Check it:

   ```bash
   python -m compileall -q anime-restorer/src movie-audio-merger movie-concator
   ```

   must exit with code 0. Then run the tool you changed on a short clip of your own:
   - **anime-restorer:** a clip of a few seconds in `input/`; check the output plays, keeps every
     audio and subtitle track, and seeks correctly. With `TARGET_HEIGHT` changed if you touched the
     scaling logic.
   - **movie-audio-merger / movie-concator:** a pair of small MKV files; check the pair is found,
     the output has the expected tracks (`mkvmerge -i <output>`), and nothing is left in `C:\Temp`.
   - Also run the tool in a folder with no matching files: it should say so and exit cleanly.
4. Put the reason in the PR description, and what you tested on.

### House rules

- **Standard library only.** A new pip dependency needs a good reason, discussed in an issue first.
- **Settings in `config.py`** for anime-restorer, not scattered constants.
- **New code passes arguments as a list** to `subprocess.run`, as anime-restorer does, rather than a
  shell string built from file names.
- **Comments say why, not what.**
- **No media in the repository**: no videos, frames or screenshots from films or series.

By contributing you agree that your contribution is released under the [MIT licence](LICENSE).
This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
