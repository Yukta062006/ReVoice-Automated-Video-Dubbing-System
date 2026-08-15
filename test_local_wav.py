#!/usr/bin/env python3
"""Test transcription on local WAV file."""

from pathlib import Path
from src.transcriber import transcribe

# Test with existing WAV file
audio_path = Path("output/test_output.wav")
if audio_path.exists():
    print(f"Testing transcription on: {audio_path}")
    print(f"File size: {audio_path.stat().st_size} bytes")
    
    # Transcribe with English language (since we don't have French audio)
    segments = transcribe(audio_path, model_name="tiny", language="en")
    
    print(f"\nFound {len(segments)} segments:")
    for seg in segments:
        print(f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text'][:50]}")
else:
    print("No test WAV file found. Downloading a video first...")
