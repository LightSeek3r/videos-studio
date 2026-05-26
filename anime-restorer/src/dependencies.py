"""
Dependency checker — verifies that required tools are available
and guides the user through installation if they're missing.
"""
import shutil
import subprocess
import sys
import os

from config import REALESRGAN_EXE


def check_python() -> bool:
    """Python is running if we got here, but verify version >= 3.7."""
    return sys.version_info >= (3, 7)


def check_ffmpeg() -> bool:
    """Check if ffmpeg and ffprobe are on PATH."""
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def check_realesrgan() -> bool:
    """Check if the RealESRGAN executable exists in the vendor directory."""
    return os.path.isfile(REALESRGAN_EXE)


def check_gpu() -> bool:
    """
    Best-effort check for Vulkan-capable GPU.
    RealESRGAN NCNN uses Vulkan — if no GPU is detected, it will fall back to CPU (very slow).
    """
    try:
        result = subprocess.run(
            [REALESRGAN_EXE, "-i", ".", "-o", ".", "-n", "realesr-animevideov3", "-s", "2"],
            capture_output=True, text=True, timeout=10
        )
        # If it mentions "no vulkan device" in stderr, GPU isn't available
        if "no vulkan device" in result.stderr.lower():
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return True  # Assume GPU is present if we can't determine otherwise


def verify_all() -> bool:
    """
    Run all dependency checks. Print status and installation instructions
    for anything missing. Returns True if all critical deps are met.
    """
    all_ok = True

    # Python version
    if not check_python():
        print(f"[X] Python 3.7+ required (found {sys.version})")
        print("    Download from: https://www.python.org/downloads/")
        all_ok = False
    else:
        print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # FFmpeg
    if not check_ffmpeg():
        print("[X] FFmpeg not found on PATH")
        print("    Install options:")
        print("      1. winget install Gyan.FFmpeg")
        print("      2. choco install ffmpeg")
        print("      3. Download from https://ffmpeg.org/download.html")
        print("    After installing, make sure 'ffmpeg' is accessible from the command line.")
        all_ok = False
    else:
        # Get version string
        try:
            ver = subprocess.check_output(["ffmpeg", "-version"], text=True).split("\n")[0]
            print(f"[OK] {ver.strip()}")
        except Exception:
            print("[OK] FFmpeg found")

    # RealESRGAN binary
    if not check_realesrgan():
        print("[X] RealESRGAN executable not found")
        print(f"    Expected at: {REALESRGAN_EXE}")
        print("    Download from: https://github.com/xinntao/Real-ESRGAN/releases")
        print("    Place realesrgan-ncnn-vulkan.exe in the vendor/ folder.")
        all_ok = False
    else:
        print("[OK] RealESRGAN binary found")

    # GPU (non-blocking warning)
    if all_ok and check_realesrgan():
        if not check_gpu():
            print("[!!] No Vulkan GPU detected — processing will be VERY slow on CPU")
            print("     A dedicated GPU (NVIDIA/AMD) is strongly recommended.")

    return all_ok
