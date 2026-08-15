#!/usr/bin/env python3
"""Test audio conversion from MP3 to WAV."""

import sys
import types

# Create a fake audioop module to inject
fake_audioop = types.ModuleType("audioop")
fake_audioop.__dict__.update({
    'mul': lambda *args: b'',
    'max': lambda *args: 0,
    'min': lambda *args: 0,
    'avg': lambda *args: 0,
    'reverse': lambda x: x,
    'negate': lambda x: x,
    'lin2lin': lambda *args: (b'', None),
    'adpcm2lin': lambda *args: (b'', None),
    'lin2adpcm': lambda *args: (b'', None),
    'stereo2mono': lambda *args: b'',
    'mono2stereo': lambda *args: b'',
    'pan': lambda *args: b'',
    'fade': lambda *args: b'',
    'ratecv': lambda *args, state=None: (b'', state),
    'dither': lambda *args: b'',
    'add': lambda *args: b'',
})

# Inject the fake module before any pydub imports
sys.modules['audioop'] = fake_audioop
sys.modules['pyaudioop'] = fake_audioop

import asyncio
from pathlib import Path
import edge_tts
from pydub import AudioSegment

async def test_conversion():
    text = "Hello world"
    voice = "en-US-GuyNeural"
    mp3_path = Path("test_output.mp3")
    wav_path = Path("test_output.wav")
    
    # Generate TTS
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(mp3_path))
    print(f"MP3 size: {mp3_path.stat().st_size} bytes")
    
    # Convert with pydub
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        print(f"Loaded audio: {len(audio)}ms duration")
        
        # Set parameters
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        print(f"Converted audio: {len(audio)}ms duration")
        
        # Export
        audio.export(str(wav_path), format="wav")
        print(f"WAV size: {wav_path.stat().st_size} bytes")
        
        # Clean up
        mp3_path.unlink()
        wav_path.unlink()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_conversion())
