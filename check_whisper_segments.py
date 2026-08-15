#!/usr/bin/env python3
"""Check Whisper segment detection."""

import whisper
from pathlib import Path

# Load audio
audio_path = Path("temp/audio.wav")

# Load model
model = whisper.load_model("small")

# Transcribe with different settings
result = model.transcribe(str(audio_path), language="fr", verbose=False, word_timestamps=True)

print(f"Total segments: {len(result['segments'])}")
print(f"Detected language: {result.get('language', 'unknown')}")

if result['segments']:
    first_start = result['segments'][0]['start']
    last_end = result['segments'][-1]['end']
    print(f"First segment start: {first_start:.2f}")
    print(f"Last segment end: {last_end:.2f}")
    print(f"Coverage: {last_end - first_start:.2f} seconds")
    print(f"Total video duration: 150.58 seconds")
    print(f"Missing from start: {first_start:.2f} seconds")
    print(f"Missing from end: {150.58 - last_end:.2f} seconds")

print("\nAll segments:")
for i, seg in enumerate(result['segments'][:25]):
    duration = seg['end'] - seg['start']
    print(f"  [{i}] {seg['start']:.1f}-{seg['end']:.1f}s ({duration:.1f}s)")
