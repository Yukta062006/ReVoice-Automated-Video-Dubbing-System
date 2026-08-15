#!/usr/bin/env python3
"""Test TTS with FFmpeg conversion."""

import asyncio
import subprocess
from pathlib import Path
import edge_tts
from src.config import FFMPEG_PATH

async def test_conversion():
    text = "Hello world test"
    voice = "en-US-GuyNeural"
    mp3_path = Path("test_output.mp3")
    wav_path = Path("test_output.wav")
    
    # Generate TTS
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(mp3_path))
    print(f"MP3 size: {mp3_path.stat().st_size} bytes")
    
    # Convert with FFmpeg
    cmd = [
        FFMPEG_PATH,
        "-i", str(mp3_path),
        "-ar", "16000",
        "-ac", "1",
        "-sample_fmt", "s16",
        "-y",
        str(wav_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
    else:
        print(f"WAV size: {wav_path.stat().st_size} bytes")
        
        # Clean up
        mp3_path.unlink()
        wav_path.unlink()

if __name__ == "__main__":
    asyncio.run(test_conversion())
