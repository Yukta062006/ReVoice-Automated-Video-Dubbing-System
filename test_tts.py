#!/usr/bin/env python3
import asyncio
import edge_tts

async def test_tts():
    communicate = edge_tts.Communicate('Hello world', 'en-US-GuyNeural')
    try:
        await communicate.save('test_output.wav')
        print('Saved test file')
        # Check file size
        import os
        size = os.path.getsize('test_output.wav')
        print(f'File size: {size} bytes')
        if size < 1000:
            print('WARNING: File is too small - may be empty!')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test_tts())
