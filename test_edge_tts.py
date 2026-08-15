#!/usr/bin/env python3
"""Test Edge TTS directly."""

import asyncio
from pathlib import Path
import edge_tts

async def test_tts():
    text = "Ceci est un test en francais."
    voice = "en-US-GuyNeural"
    output_path = Path("test_edge_tts_output.wav")
    
    print(f"Testing TTS with: {text}")
    print(f"Voice: {voice}")
    
    communicate = edge_tts.Communicate(text, voice)
    
    try:
        await communicate.save(str(output_path))
        size = output_path.stat().st_size
        print(f"TTS file created: {size} bytes")
        
        if size > 100:
            print("SUCCESS: TTS is working!")
        else:
            print("FAILURE: TTS file too small")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_tts())
