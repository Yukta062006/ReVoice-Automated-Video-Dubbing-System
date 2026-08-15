#!/usr/bin/env python3
"""Check segment coverage."""

from pathlib import Path
from src.transcriber import transcribe

segments = transcribe(Path("temp/audio.wav"), model_name="small", language="fr")

print(f"Total segments: {len(segments)}")
if segments:
    print(f"First segment start: {segments[0]['start']:.2f}")
    print(f"Last segment end: {segments[-1]['end']:.2f}")
    print(f"Coverage: {segments[-1]['end'] - segments[0]['start']:.2f} seconds")
    
    # Show all segments
    print("\nAll segments:")
    for i, seg in enumerate(segments):
        duration = seg['end'] - seg['start']
        print(f"  [{i}] {seg['start']:.1f}-{seg['end']:.1f}s ({duration:.1f}s)")
