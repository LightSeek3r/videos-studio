"""
Video Remaster — Main orchestrator.
Discovers videos in input/, processes them, outputs to output/.
"""
import os
import sys
import time

# Ensure src/ is on the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import INPUT_DIR, OUTPUT_DIR, TARGET_HEIGHT
from dependencies import verify_all
from utils import discover_videos, ensure_directories, format_duration
from video_processor import process_video

BANNER = r"""
 __      ___     _              ____                          _            
 \ \    / (_)   | |            |  _ \                        | |           
  \ \  / / _  __| | ___  ___   | |_) | ___ _ __ ___   __ _ ___| |_ ___ _ __ 
   \ \/ / | |/ _` |/ _ \/ _ \  |   <  / _ \ '_ ` _ \ / _` / __| __/ _ \ '__|
    \  /  | | (_| |  __/ (_) | | |\ \ | __/ | | | | | (_| \__ \ ||  __/ |   
     \/   |_|\__,_|\___|\___/  |_| \_\\___|_| |_| |_|\__,_|___/\__\___|_|  
"""


def main():
    print(BANNER)
    print(f"  Target: {TARGET_HEIGHT}p upscale via RealESRGAN")
    print(f"  Input:  input/")
    print(f"  Output: output/")
    print()

    # ── Dependency check ─────────────────────────────────────────
    print("Checking dependencies...\n")
    if not verify_all():
        print("\n[!] Missing dependencies. Please install them and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    print()

    # ── Ensure directories ───────────────────────────────────────
    ensure_directories(INPUT_DIR, OUTPUT_DIR)

    # ── Discover videos ──────────────────────────────────────────
    videos = discover_videos()

    if not videos:
        print("No video files found in input/ folder.")
        print("Place your video files there and run again.")
        input("\nPress Enter to exit...")
        sys.exit(0)

    print(f"Found {len(videos)} video(s) to process:\n")
    for i, v in enumerate(videos, 1):
        print(f"  {i}. {os.path.basename(v)}")

    # ── Confirm ──────────────────────────────────────────────────
    print()
    reply = input("Proceed with processing all videos? [Y/n] > ").strip().lower()
    if reply and reply not in ("y", "yes"):
        print("Aborted.")
        input("\nPress Enter to exit...")
        sys.exit(0)

    # ── Process ──────────────────────────────────────────────────
    total_start = time.time()
    results = []

    for i, video_path in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}]", end="")
        try:
            output_path = process_video(video_path)
            results.append((os.path.basename(video_path), "OK", output_path))
        except Exception as e:
            print(f"\n  ERROR: {e}")
            results.append((os.path.basename(video_path), "FAILED", str(e)))

    # ── Summary ──────────────────────────────────────────────────
    total_elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"  All done — {format_duration(total_elapsed)} total")
    print(f"{'='*60}\n")

    for name, status, detail in results:
        icon = "OK" if status == "OK" else "FAIL"
        print(f"  [{icon}] {name}")
        if status == "OK":
            print(f"        -> {os.path.basename(detail)}")
        else:
            print(f"        -> {detail}")

    print(f"\nRestored videos are in: output/")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
