#!/usr/bin/env python3
"""Test transcription with French language."""

from pathlib import Path
from src.transcriber import transcribe

print("=" * 60)
print("Testing French Transcription")
print("=" * 60)
print()

# Check if audio file exists
audio_path = Path("temp/audio.wav")
if not audio_path.exists():
    print(f"Audio file not found: {audio_path}")
    print("Please run the full pipeline first to download and extract audio.")
else:
    print(f"Using audio file: {audio_path}")
    print(f"Audio duration: {(audio_path.stat().st_size / (16000 * 2 * 60)):.2f} minutes (estimated)")
    print()

    # Transcribe with French language
    print("Transcribing with language='fr'...")
    segments = transcribe(audio_path, model_name="small", language="fr")
    
    print()
    print(f"Found {len(segments)} segments")
    print()
    print("Transcription:")
    print("-" * 60)
    for i, seg in enumerate(segments):
        print(f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}")
        print()
    print("-" * 60)
    print()
    print(f"Detected language: {segments[0]['language'] if segments else 'N/A'}")
