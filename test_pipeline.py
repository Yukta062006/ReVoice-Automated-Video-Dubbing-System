#!/usr/bin/env python3
"""Debug script to test the pipeline."""

import traceback
from pathlib import Path
from src.pipeline import DubbingPipeline

try:
    pipeline = DubbingPipeline(
        url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        output_dir=Path('output'),
        temp_dir=Path('temp'),
        whisper_model='tiny',
        tts_voice='en-US-GuyNeural',
        keep_temp=True
    )
    output_path = pipeline.run()
    print(f"Success: {output_path}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
