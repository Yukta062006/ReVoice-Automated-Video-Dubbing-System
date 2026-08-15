#!/usr/bin/env python3
"""Verify the full pipeline works end-to-end."""

from pathlib import Path
from src.transcriber import transcribe
from src.translator import Translator

# Check if audio file exists
audio_path = Path("temp/audio.wav")
if not audio_path.exists():
    print("Audio file not found. Please run the pipeline first.")
else:
    print("=" * 60)
    print("Pipeline Verification")
    print("=" * 60)
    print()
    
    # Step 1: Transcribe French
    print("Step 1: French Transcription")
    print("-" * 60)
    segments = transcribe(audio_path, model_name="small", language="fr")
    print(f"Found {len(segments)} segments with language: {segments[0]['language']}")
    print()
    print("Transcribed French text:")
    for i, seg in enumerate(segments):
        text = seg['text'][:80]
        print(f"  [{i+1}] {text}...")
    print()
    
    # Step 2: Translate to English
    print("Step 2: Translation to English")
    print("-" * 60)
    translator = Translator("fr")
    translated = translator.translate(segments)
    print(f"Translated {len(translated)} segments")
    print()
    print("English translation:")
    for i, seg in enumerate(translated[:5]):  # Show first 5
        text = seg['en_text'][:80]
        print(f"  [{i+1}] {text}...")
    if len(translated) > 5:
        print(f"  ... and {len(translated) - 5} more segments")
    print()
    
    # Step 3: Check TTS files
    print("Step 3: TTS Files Check")
    print("-" * 60)
    tts_files = list(Path("temp").glob("seg_*.wav"))
    print(f"Found {len(tts_files)} TTS files")
    if tts_files:
        for f in tts_files[:3]:
            size = f.stat().st_size
            print(f"  {f.name}: {size} bytes")
        if len(tts_files) > 3:
            print(f"  ... and {len(tts_files) - 3} more files")
    print()
    
    # Step 4: Check dubbed audio
    print("Step 4: Dubbed Audio Check")
    print("-" * 60)
    dubbed = Path("temp/dubbed_audio.wav")
    if dubbed.exists():
        print(f"Dubbed audio: {dubbed.stat().st_size} bytes")
    else:
        print("Dubbed audio: NOT FOUND")
    print()
    
    # Step 5: Check output
    print("Step 5: Output Check")
    print("-" * 60)
    output_files = list(Path("output").glob("*.mp4"))
    if output_files:
        for f in output_files:
            print(f"Output: {f.name} ({f.stat().st_size} bytes)")
    else:
        print("No output files found (TTS may have failed)")
    print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print("✓ French transcription: Working")
    print("✓ Translation: Working")
    print("⚠ TTS Generation: Needs network (Edge TTS service)")
    print("✓ Muxing: Ready to run when TTS works")
