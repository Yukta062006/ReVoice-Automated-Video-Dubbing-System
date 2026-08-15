#!/usr/bin/env python3
"""Simple test of the audio overlay approach."""

import subprocess
from pathlib import Path
from src.config import FFMPEG_PATH

ffprobe = Path(FFMPEG_PATH).parent / "ffprobe.exe"

# Create a simple test with known segments
# Simulate: segment at 0-5s, silence 5-9s, segment at 9-15s

# Create 3 TTS files
cmd1 = [FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=5", "-ar", "16000", "-ac", "1", "test_seg1.wav"]
cmd2 = [FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=6", "-ar", "16000", "-ac", "1", "test_seg2.wav"]
subprocess.run(cmd1, capture_output=True, shell=True)
subprocess.run(cmd2, capture_output=True, shell=True)

print("Test segments created")

# Now test the overlay approach
base_audio = "test_base.wav"
cmd_base = [FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=16000:duration=15", "-ar", "16000", "-ac", "1", base_audio]
subprocess.run(cmd_base, capture_output=True, shell=True)

# Overlay seg1 at 0s, seg2 at 9s
cmd = [
    FFMPEG_PATH, "-y",
    "-i", base_audio,
    "-i", "test_seg1.wav",
    "-i", "test_seg2.wav",
    "-filter_complex", 
    "[1:a]adelay=0|0[tts0];[2:a]adelay=9000|9000[tts1];[0:a][tts0]amix=inputs=2:duration=first:dropout_transition=0[ov0];[ov0][tts1]amix=inputs=2:duration=first:dropout_transition=0[out]",
    "-map", "[out]",
    "-c:a", "pcm_s16le",
    "-ar", "16000",
    "-ac", "1",
    "test_output.wav"
]
result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
print(f"Return: {result.returncode}")
print(f"Stderr: {result.stderr[-500:] if result.stderr else 'None'}")

# Check output duration
cmd_dur = [str(ffprobe), "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", "test_output.wav"]
proc = subprocess.run(cmd_dur, capture_output=True, text=True, shell=True)
print(f"Output duration: {proc.stdout.strip()}s")
