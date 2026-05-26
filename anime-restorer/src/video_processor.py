"""
Video processing pipeline — extract frames, upscale with RealESRGAN, reconstruct video.

Frames are processed in batches of BATCH_SIZE to keep peak disk usage low:
  1. Extract ALL frames to TEMP_FRAMES_IN (one ffmpeg pass).
  2. For each batch: move frames to TEMP_BATCH_IN, run ESRGAN → TEMP_FRAMES_OUT,
     build a video segment, delete the batch frames, repeat.
  3. Concatenate all segments and mux in the original audio streams.
"""
import math
import os
import shutil
import subprocess
import threading
import time

from config import (
    BATCH_SIZE,
    ESRGAN_OUTPUT_FORMAT,
    MODEL_NAME,
    OUTPUT_DIR,
    OUTPUT_SUFFIX,
    PIXEL_FORMAT,
    REALESRGAN_EXE,
    SAMPLE_INTERVAL,
    SAMPLES_DIR,
    TARGET_HEIGHT,
    TEMP_BATCH_IN,
    TEMP_FRAMES_IN,
    TEMP_FRAMES_OUT,
    TEMP_SEGMENTS,
    VIDEO_CODEC,
)
from utils import (
    calculate_scale_factor,
    clear_directory,
    ensure_directories,
    format_duration,
    get_audio_stream_count,
    get_fps,
    get_resolution,
)


def _loader_animation(stop_event: threading.Event, prefix: str = "Processing") -> None:
    """Spinning loader shown while RealESRGAN runs."""
    chars = ["|", "/", "-", "\\"]
    idx = 0
    while not stop_event.is_set():
        print(f"\r  {prefix} {chars[idx % len(chars)]}", end="", flush=True)
        time.sleep(0.3)
        idx += 1
    print(f"\r  {prefix} done." + " " * 10)


def _extract_frames(video_path: str) -> None:
    """Use ffmpeg to extract video frames as PNGs at original resolution."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-qscale:v", "1",
        "-qmin", "1",
        "-qmax", "1",
        "-vsync", "cfr",
        os.path.join(TEMP_FRAMES_IN, "frame%08d.png"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg frame extraction failed:\n{result.stderr[-500:]}")


def _upscale_frames(input_dir: str, output_dir: str, esrgan_factor: int) -> int:
    """Run RealESRGAN on input_dir → output_dir. Returns number of frames produced."""
    cmd = [
        REALESRGAN_EXE,
        "-i", input_dir,
        "-o", output_dir,
        "-n", MODEL_NAME,
        "-s", str(esrgan_factor),
        "-f", ESRGAN_OUTPUT_FORMAT,
    ]

    stop_event = threading.Event()
    loader = threading.Thread(
        target=_loader_animation,
        args=(stop_event, f"RealESRGAN {esrgan_factor}x upscale"),
        daemon=True,
    )
    loader.start()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"RealESRGAN failed (exit code {result.returncode}):\n{result.stderr[-500:]}"
            )
    finally:
        stop_event.set()
        loader.join()

    frame_count = len([f for f in os.listdir(output_dir) if f.startswith("frame")])
    if frame_count == 0:
        raise RuntimeError("RealESRGAN produced 0 output frames. Check GPU/Vulkan drivers.")
    return frame_count


def _save_samples(
    batch_in_dir: str,
    batch_out_dir: str,
    batch_start: int,
    batch_size: int,
    sample_interval: int,
    samples_dir: str,
) -> None:
    """
    Copy original + upscaled frames at every sample_interval milestone into samples_dir.
    E.g. with sample_interval=1000: saves frame 1000, 2000, 3000, ...
    """
    first = batch_start
    last = batch_start + batch_size - 1
    first_milestone = math.ceil(first / sample_interval) * sample_interval
    milestones = range(first_milestone, last + 1, sample_interval)

    for milestone in milestones:
        frame_stem = f"frame{milestone:08d}"
        src_orig = os.path.join(batch_in_dir, frame_stem + ".png")
        src_up = os.path.join(batch_out_dir, frame_stem + "." + ESRGAN_OUTPUT_FORMAT)

        if not os.path.isfile(src_orig) or not os.path.isfile(src_up):
            continue

        os.makedirs(samples_dir, exist_ok=True)
        shutil.copy2(src_orig, os.path.join(samples_dir, f"frame_{milestone:08d}_original.png"))
        shutil.copy2(src_up, os.path.join(samples_dir, f"frame_{milestone:08d}_upscaled.{ESRGAN_OUTPUT_FORMAT}"))
        print(f"    Saved sample: frame {milestone:,}")


def _make_segment(
    frame_dir: str,
    start_number: int,
    frame_count: int,
    fps: float,
    segment_path: str,
    target_height: int = 0,
) -> None:
    """Create a video-only segment from the upscaled frames in frame_dir."""
    frame_pattern = os.path.join(frame_dir, f"frame%08d.{ESRGAN_OUTPUT_FORMAT}")
    cmd = [
        "ffmpeg", "-y",
        "-r", str(fps),
        "-start_number", str(start_number),
        "-i", frame_pattern,
        "-frames:v", str(frame_count),
    ]
    if target_height > 0:
        cmd.extend(["-vf", f"scale=-2:{target_height}"])
    cmd.extend([
        "-c:v", VIDEO_CODEC,
        "-bf", "0",       # no B-frames → DTS == PTS, no edit-list offset in MP4
        "-pix_fmt", PIXEL_FORMAT,
        "-r", str(fps),   # enforce CFR on output side as well
        segment_path,
    ])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg segment creation failed:\n{result.stderr[-500:]}")


def _concatenate_segments(
    segment_info: list,
    fps: float,
    original_video: str,
    output_path: str,
    audio_streams: int,
) -> None:
    """
    Two-step assembly to guarantee correct seeking after fast-forward.

    Step 1 — Concat all video-only segments into a single clean intermediate.
             A single-file intermediate (instead of feeding the concat demuxer
             directly into a two-input mux) means ffmpeg in step 2 works from
             a normal seekable file and can properly interleave audio+video.

    Step 2 — Mux the intermediate video with the original audio/subtitles.
             Audio is re-encoded so its timestamps are generated fresh against
             the clean video timeline (stream-copying audio from a different
             source produces PTS that diverge from the video after a seek).
    """
    seg_dir = os.path.dirname(segment_info[0][0])
    concat_list = os.path.join(seg_dir, "concat_list.txt")
    intermediate = os.path.join(seg_dir, "_concat_video_only.mp4")

    # ── ffconcat list with explicit durations ─────────────────────
    with open(concat_list, "w", encoding="utf-8") as fh:
        fh.write("ffconcat version 1.0\n")
        for i, (seg, frame_count) in enumerate(segment_info):
            fh.write(f"file '{seg.replace(os.sep, '/')}'\n")
            if i < len(segment_info) - 1:
                fh.write(f"duration {frame_count / fps:.9f}\n")

    # ── Step 1: concat segments → clean video-only intermediate ───
    step1 = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c:v", "copy",
        "-an",
        intermediate,
    ]
    r1 = subprocess.run(step1, capture_output=True, text=True)
    os.remove(concat_list)
    if r1.returncode != 0:
        raise RuntimeError(f"ffmpeg concat (step 1) failed:\n{r1.stderr[-500:]}")

    # ── Step 2: mux intermediate video + original audio ───────────
    step2 = [
        "ffmpeg", "-y",
        "-i", intermediate,
        "-i", original_video,
        "-map", "0:v:0",
    ]
    for i in range(audio_streams):
        step2.extend(["-map", f"1:a:{i}"])
    step2.extend(["-map", "1:s?"])
    step2.extend([
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-c:s", "copy",
    ])
    output_ext = os.path.splitext(output_path)[1].lower()
    if output_ext in (".mp4", ".m4v"):
        step2.extend(["-movflags", "+faststart"])
    step2.append(output_path)

    r2 = subprocess.run(step2, capture_output=True, text=True)
    os.remove(intermediate)
    if r2.returncode != 0:
        raise RuntimeError(f"ffmpeg mux (step 2) failed:\n{r2.stderr[-500:]}")


def _build_output_path(original_path: str) -> str:
    """Generate the output file path from the original file name."""
    basename = os.path.basename(original_path)
    name, ext = os.path.splitext(basename)
    output_name = f"{name}.{OUTPUT_SUFFIX}.{TARGET_HEIGHT}p{ext}"
    return os.path.join(OUTPUT_DIR, output_name)


def process_video(video_path: str) -> str:
    """
    Full pipeline for a single video file.
    Returns the path to the restored video.
    """
    basename = os.path.basename(video_path)
    output_path = _build_output_path(video_path)

    if os.path.isfile(output_path):
        print(f"\n  Output already exists, skipping: {os.path.basename(output_path)}")
        return output_path

    print(f"\n{'='*60}")
    print(f"  Processing: {basename}")
    print(f"{'='*60}")
    start_time = time.time()

    # ── Probe video info ─────────────────────────────────────────
    width, height = get_resolution(video_path)
    if width is None or height is None:
        raise RuntimeError(f"Cannot read resolution of {basename}")

    fps = get_fps(video_path)
    audio_streams = get_audio_stream_count(video_path)
    print(f"  Original: {width}x{height}, {fps:.3f} fps, {audio_streams} audio stream(s)")

    # ── Calculate scaling strategy ───────────────────────────────
    esrgan_factor, ffmpeg_ratio = calculate_scale_factor(height, TARGET_HEIGHT)
    upscaled_h = height * esrgan_factor

    needs_post_scale = abs(ffmpeg_ratio - 1.0) > 0.01
    if needs_post_scale:
        print(f"  Strategy: ESRGAN {esrgan_factor}x ({width}x{height} -> {width*esrgan_factor}x{upscaled_h}) -> scale to {TARGET_HEIGHT}p")
    else:
        print(f"  Strategy: ESRGAN {esrgan_factor}x (perfect fit to {TARGET_HEIGHT}p)")

    # ── Prepare directories ──────────────────────────────────────
    ensure_directories(TEMP_FRAMES_IN, TEMP_FRAMES_OUT, TEMP_BATCH_IN, TEMP_SEGMENTS, OUTPUT_DIR)
    clear_directory(TEMP_FRAMES_IN)
    clear_directory(TEMP_FRAMES_OUT)
    clear_directory(TEMP_BATCH_IN)
    clear_directory(TEMP_SEGMENTS)

    # Samples sub-directory named after the video (no extension)
    video_base = os.path.splitext(basename)[0]
    video_samples_dir = os.path.join(SAMPLES_DIR, video_base)

    # ── Step 1: Extract ALL frames ───────────────────────────────
    print("  Extracting frames...")
    _extract_frames(video_path)
    all_frames = sorted(f for f in os.listdir(TEMP_FRAMES_IN) if f.startswith("frame"))
    total_frames = len(all_frames)
    print(f"  Extracted {total_frames:,} frames")

    if total_frames == 0:
        raise RuntimeError("Frame extraction produced 0 frames")

    # ── Steps 2–4: Batch upscale + segment ───────────────────────
    num_batches = math.ceil(total_frames / BATCH_SIZE)
    segment_paths: list[tuple[str, int]] = []  # (path, frame_count)

    for batch_idx in range(num_batches):
        batch_files = all_frames[batch_idx * BATCH_SIZE : (batch_idx + 1) * BATCH_SIZE]
        batch_actual = len(batch_files)

        # Parse 1-based frame number from filename: "frame00001000.png" → 1000
        start_frame_num = int(os.path.splitext(batch_files[0])[0][5:])

        print(f"\n  Batch {batch_idx + 1}/{num_batches}  "
              f"(frames {start_frame_num:,} – {start_frame_num + batch_actual - 1:,})")

        # Move this batch out of frames_in so ESRGAN only sees current batch
        for fname in batch_files:
            shutil.move(os.path.join(TEMP_FRAMES_IN, fname), os.path.join(TEMP_BATCH_IN, fname))

        # Upscale
        frame_count = _upscale_frames(TEMP_BATCH_IN, TEMP_FRAMES_OUT, esrgan_factor)
        print(f"    Upscaled {frame_count} frames")

        # Save comparison samples for milestone frames in this batch
        _save_samples(
            batch_in_dir=TEMP_BATCH_IN,
            batch_out_dir=TEMP_FRAMES_OUT,
            batch_start=start_frame_num,
            batch_size=batch_actual,
            sample_interval=SAMPLE_INTERVAL,
            samples_dir=video_samples_dir,
        )

        # Build video-only segment
        segment_path = os.path.join(TEMP_SEGMENTS, f"segment_{batch_idx:04d}.mp4")
        print(f"    Building segment {batch_idx + 1}/{num_batches}...")
        _make_segment(
            frame_dir=TEMP_FRAMES_OUT,
            start_number=start_frame_num,
            frame_count=batch_actual,
            fps=fps,
            segment_path=segment_path,
            target_height=TARGET_HEIGHT if needs_post_scale else 0,
        )
        segment_paths.append((segment_path, batch_actual))

        # Free disk space: delete batch frames immediately
        clear_directory(TEMP_BATCH_IN)
        clear_directory(TEMP_FRAMES_OUT)

    # ── Step 5: Concatenate segments + mux audio ─────────────────
    print("\n  Assembling final video...")
    _concatenate_segments(segment_paths, fps, video_path, output_path, audio_streams)

    # ── Cleanup segments ─────────────────────────────────────────
    clear_directory(TEMP_SEGMENTS)

    elapsed = time.time() - start_time
    print(f"  Completed in {format_duration(elapsed)}")
    print(f"  Output: {os.path.basename(output_path)}")

    return output_path
