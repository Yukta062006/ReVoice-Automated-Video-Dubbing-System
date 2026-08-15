#!/usr/bin/env python3
"""Check segment timestamps."""

from pathlib import Path
from src.transcriber import transcribe
from src.translator import Translator

# Transcribe
print("Transcribing...")
segments = transcribe(Path("temp/audio.wav"), model_name="small", language="fr")
total_duration = 150.58  # From the pipeline

print(f"Total video duration: {total_duration:.2f} seconds")
print(f"Number of segments: {len(segments)}")
print()

# Show first 10 segments
print("First 10 segments:")
for i, seg in enumerate(segments[:10]):
    duration = seg["end"] - seg["start"]
    print(f"  [{i}] {seg['start']:.1f}-{seg['end']:.1f}s ({duration:.1f}s): {seg['text'][:50]}")

# Check coverage
if segments:
    first_start = segments[0]["start"]
    last_end = segments[-1]["end"]
    coverage = last_end - first_start
    print()
    print(f"Coverage: {first_start:.1f}s to {last_end:.1f}s = {coverage:.1f}s")
    print(f"Total video: {total_duration:.1f}s")
    print(f"Missing from start: {first_start:.1f}s")
    print(f"Missing from end: {total_duration - last_end:.1f}s")

# Translate
print()
print("Translating...")
translator = Translator("fr")
translated = translator.translate(segments)

# Check if all segments have en_text
missing = [i for i, s in enumerate(translated) if not s.get("en_text", "").strip()]
print(f"Segments without English translation: {len(missing)}")

# Generate TTS
print()
print("Generating TTS...")
from src.tts import generate_all_segments
result = generate_all_segments(translated, Path("temp"), "en-US-GuyNeural")

# Check TTS files
tts_files = [s.get("tts_path") for s in result if s.get("tts_path")]
print(f"TTS files generated: {len(tts_files)}")

# Check actual audio duration from TTS files
total_tts_duration = 0
for seg in result:
    if "tts_path" in seg and seg["tts_path"]:
        path = seg["tts_path"]
        if Path(path).exists():
            # Get duration using ffprobe
            import subprocess
            from src.config import FFMPEG_PATH
            ffprobe = Path(FFMPEG_PATH).parent / "ffprobe.exe"
            cmd = [str(ffprobe), "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
            proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            dur = float(proc.stdout.strip()) if proc.stdout.strip() else 0
            total_tts_duration += dur

print(f"Total TTS audio duration: {total_tts_duration:.1f} seconds")
