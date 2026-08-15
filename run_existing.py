#!/usr/bin/env python3
"""Run pipeline with existing temp files."""

from pathlib import Path
from src.pipeline import DubbingPipeline

# Use existing video in temp folder
temp_dir = Path("temp")
video_files = list(temp_dir.glob("*.mp4"))
audio_files = list(temp_dir.glob("*.wav"))

if not video_files:
    print("No video.mp4 found in temp/")
    exit(1)

if not audio_files:
    print("No audio.wav found in temp/")
    exit(1)

print(f"Using existing video: {video_files[0].name}")
print(f"Using existing audio: {audio_files[0].name}")

# Create a dummy URL that passes validation
dummy_url = "https://www.youtube.com/watch?v=EXISTING"

# Manually set up the existing files in temp
# The pipeline will use these when download_video is called
video_path = video_files[0]
audio_path = audio_files[0]

# Patch the download function to use existing files
import src.downloader as downloader_mod
original_download = downloader_mod.download_video

def patched_download(url, output_dir):
    print(f"[SKIP DOWNLOAD] Using existing files from {output_dir}")
    # Copy existing files to output_dir if needed
    import shutil
    if output_dir != temp_dir:
        shutil.copy(video_path, output_dir / "video.mp4")
        shutil.copy(audio_path, output_dir / "audio.wav")
    return (output_dir / "video.mp4", output_dir / "audio.wav")

downloader_mod.download_video = patched_download

# Run pipeline
try:
    pipeline = DubbingPipeline(
        url=dummy_url,
        output_dir=Path("output"),
        temp_dir=temp_dir,
        keep_temp=True
    )
    output_path = pipeline.run()
    print(f"\n✓ Successfully created: {output_path}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
