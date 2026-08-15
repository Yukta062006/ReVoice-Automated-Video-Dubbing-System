#!/usr/bin/env python3
"""Debug TTS generation."""

from pathlib import Path
from src.transcriber import transcribe
from src.translator import Translator
from src.tts import generate_all_segments

# Transcribe
print("Transcribing...")
segments = transcribe(Path("temp/audio.wav"), model_name="small", language="fr")
print(f"Transcribed {len(segments)} segments")
print()

# Translate
print("Translating...")
translator = Translator("fr")
segments = translator.translate(segments)
print(f"Translated {len(segments)} segments")
print()

# Check if en_text exists
print("Checking segments for en_text:")
for i, seg in enumerate(segments[:5]):
    has_text = "en_text" in seg
    text = seg.get("en_text", "")[:50] if has_text else "MISSING"
    print(f"  [{i}] has_en_text={has_text}: {text}")

print()

# Generate TTS
print("Generating TTS...")
segments = generate_all_segments(segments, Path("temp"), "en-US-GuyNeural")

# Check results
print("\nTTS file sizes:")
for seg in segments[:5]:
    path = seg.get("tts_path")
    if path and Path(path).exists():
        size = Path(path).stat().st_size
        print(f"  {path.name}: {size} bytes")
    else:
        print(f"  MISSING: {seg.get('en_text', '')[:30]}")
