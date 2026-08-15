#!/usr/bin/env python3
"""Verify the ReVoice system is working."""

import sys
from pathlib import Path

print("=" * 60)
print("ReVoice System Verification")
print("=" * 60)
print()

# Check if required modules can be imported
print("[1/5] Checking imports...")
try:
    from src.pipeline import DubbingPipeline
    from src.config import check_dependencies
    print("   ✓ All imports successful")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Check if directories exist
print("[2/5] Checking directories...")
for dir_name in ["output", "temp"]:
    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ {dir_name}/ directory exists")

# Check dependencies
print("[3/5] Checking dependencies...")
try:
    check_dependencies()
    print("   ✓ Dependencies satisfied")
except RuntimeError as e:
    print(f"   ✗ Dependency check failed: {e}")
    sys.exit(1)

# Test pipeline initialization
print("[4/5] Testing pipeline initialization...")
try:
    pipeline = DubbingPipeline(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        output_dir=Path("output"),
        temp_dir=Path("temp"),
        whisper_model="tiny",
        tts_voice="en-US-GuyNeural",
        keep_temp=True
    )
    print("   ✓ Pipeline initialized successfully")
except Exception as e:
    print(f"   ✗ Pipeline initialization failed: {e}")
    sys.exit(1)

# Test config module
print("[5/5] Testing config module...")
try:
    from src.config import FFMPEG_PATH
    from pathlib import Path
    ffmpeg_path = Path(FFMPEG_PATH)
    if ffmpeg_path.exists():
        print(f"   ✓ FFmpeg found at: {FFMPEG_PATH}")
    else:
        print(f"   ✗ FFmpeg not found at: {FFMPEG_PATH}")
except Exception as e:
    print(f"   ✗ Config test failed: {e}")

print()
print("=" * 60)
print("Verification Complete!")
print("=" * 60)
print()
print("To test the full pipeline, run:")
print('  python main.py "https://www.youtube.com/watch?v=VIDEO_ID"')
print()
print("For help:")
print('  python main.py --help')
