#!/usr/bin/env python3
"""
ReVoice — Automated Video Dubbing System
Translates any YouTube video into English
"""

import argparse
import sys
from pathlib import Path

from src.config import check_dependencies, PROJECT_NAME, VERSION
from src.pipeline import DubbingPipeline


def main():
    # Print banner
    print("=" * 60)
    print("ReVoice — Automated Video Dubbing System")
    print("Translates any YouTube video into English")
    print("=" * 60)
    print()
    
    # Check dependencies
    check_dependencies()
    
    # Create directories
    output_dir = Path("output")
    temp_dir = Path("temp")
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="ReVoice: Translate YouTube videos to English",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python main.py "https://www.youtube.com/watch?v=XXXXX"
  python main.py "https://youtu.be/XXXXX" --model small --voice en-GB-RyanNeural
"""
    )
    
    parser.add_argument("url", help="YouTube URL to process")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model: tiny/base/small/medium/large (default: base)"
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default="en-US-GuyNeural",
        help="TTS voice name (default: en-US-GuyNeural)"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        default=None,
        help="Override source language (default: auto-detect)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files after processing"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Alias for --keep-temp"
    )
    
    args = parser.parse_args()
    
    # Handle keep_temp flag
    keep_temp = args.keep_temp or args.no_cleanup
    
    try:
        # Create and run pipeline
        pipeline = DubbingPipeline(
            url=args.url,
            output_dir=Path(args.output),
            temp_dir=temp_dir,
            whisper_model=args.model,
            tts_voice=args.voice,
            keep_temp=keep_temp,
            language_override=args.language
        )
        
        output_path = pipeline.run()
        print()
        print(f"✓ Successfully created: {output_path}")
        sys.exit(0)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()