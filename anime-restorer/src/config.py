"""
Configuration for the video remaster pipeline.
All paths, constants, and user-tunable settings live here.
"""
import os

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(ROOT_DIR, "input")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
TEMP_DIR = os.path.join(ROOT_DIR, "temp")
TEMP_FRAMES_IN = os.path.join(TEMP_DIR, "frames_in")
TEMP_FRAMES_OUT = os.path.join(TEMP_DIR, "frames_out")
TEMP_BATCH_IN = os.path.join(TEMP_DIR, "batch_in")
TEMP_SEGMENTS = os.path.join(TEMP_DIR, "segments")
SAMPLES_DIR = os.path.join(ROOT_DIR, "samples")
VENDOR_DIR = os.path.join(ROOT_DIR, "vendor")
REALESRGAN_EXE = os.path.join(VENDOR_DIR, "realesrgan-ncnn-vulkan.exe")
MODELS_DIR = os.path.join(VENDOR_DIR, "models")

# ── Video Settings ───────────────────────────────────────────────────────────
TARGET_HEIGHT = 1080          # Target output height in pixels (1080 = 1080p, 2160 = 4K)
FPS_FALLBACK = 23.976         # Fallback FPS when detection fails
MODEL_NAME = "realesr-animevideov3"  # RealESRGAN model to use
VIDEO_CODEC = "libx264"       # Output video codec
PIXEL_FORMAT = "yuv420p"      # Output pixel format
OUTPUT_SUFFIX = "Restored"    # Appended to output filename

# ── Supported Formats ────────────────────────────────────────────────────────
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".m4v", ".mpg", ".mpeg", ".ts", ".vob",
}

# ── RealESRGAN ───────────────────────────────────────────────────────────────
ESRGAN_SCALE_FACTORS = [2, 3, 4]  # Available upscale factors for the model
ESRGAN_OUTPUT_FORMAT = "jpg"       # Frame output format (jpg is faster, png is lossless)

# ── Batching & Samples ───────────────────────────────────────────────────────
BATCH_SIZE = 1000        # Frames extracted+upscaled per batch (limits peak disk usage)
SAMPLE_INTERVAL = 1000   # Save one comparison sample every N frames (e.g. frame 1000, 2000, ...)
