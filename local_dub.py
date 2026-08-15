#!/usr/bin/env python3
"""
ReVoice — Local Video Dubbing System
Processes local video files with French speech to English
"""

import argparse
import sys
import subprocess
from pathlib import Path

from src.config import check_dependencies, FFMPEG_PATH
from src.transcriber import transcribe
from src.translator import Translator
from src.tts import generate_all_segments
from src.audio_processor import build_dubbed_audio, get_audio_duration
from src.video_processor import mux_video_audio, verify_output


def extract_audio(video_path: Path, output_dir: Path) -> Path:
    """Extract audio from video file using FFmpeg."""
    print(f"   Extracting audio from: {video_path.name}")
    
    # Convert to 16kHz mono WAV
    audio_path = output_dir / "audio.wav"
    ffmpeg_cmd = [
        FFMPEG_PATH,
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-y",
        str(audio_path)
    ]
    
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio extraction failed: {result.stderr}")
    
    return audio_path


def main():
    # Print banner
    print("=" * 60)
    print("ReVoice — Local Video Dubbing System")
    print("Translates French videos to English")
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
        description="ReVoice: Translate local French videos to English",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python local_dub.py "path/to/video.mkv" --language fr
  python local_dub.py "path/to/video.mp4" --model small --language fr
"""
    )
    
    parser.add_argument("input_file", help="Local video file to process")
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
        default="fr",
        help="Source language (default: fr for French)"
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary files after processing"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"Input file: {input_path}")
    print(f"Source language: {args.language}")
    print(f"Whisper model: {args.model}")
    print()
    
    try:
        # Extract audio from local video
        print("[1/6] Extracting audio from video...")
        audio_path = extract_audio(input_path, temp_dir)
        total_duration = get_audio_duration(audio_path)
        print(f"   Audio duration: {total_duration:.2f} seconds")
        
        # Step 2: Transcribe with French language
        print(f"[2/6] Transcribing speech... (model: {args.model}, language: {args.language})")
        segments = transcribe(audio_path, args.model, language=args.language)
        print(f"   Found {len(segments)} speech segments")
        
        # Step 3: Translate to English
        print("[3/6] Translating to English...")
        translator = Translator(args.language)
        segments = translator.translate(segments)
        print(f"   Translated {len(segments)} segments")
        
        # Step 4: Generate English TTS
        print("[4/6] Generating English audio...")
        segments = generate_all_segments(segments, temp_dir, args.voice)
        print(f"   Generated {len(segments)} TTS audio files")
        
        # Step 5: Build dubbed audio
        print("[5/6] Creating dubbed audio...")
        dubbed_wav = build_dubbed_audio(segments, total_duration, temp_dir)
        print(f"   Built dubbed audio: {dubbed_wav.name}")
        
        # Step 6: Mux video and new audio
        print("[6/6] Creating final dubbed video...")
        video_title = input_path.stem
        output_filename = f"{video_title}_dubbed_english.mp4"
        output_path = output_dir / output_filename
        
        # Copy input video to temp as video.mp4 for muxing
        video_path = temp_dir / "video.mp4"
        subprocess.run([
            FFMPEG_PATH,
            "-i", str(input_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-y",
            str(video_path)
        ], capture_output=True, shell=True)
        
        if not video_path.exists():
            raise RuntimeError("Failed to prepare video for muxing")
        
        mux_video_audio(video_path, dubbed_wav, output_path)
        
        if verify_output(output_path, total_duration):
            print("   Output verified successfully")
        
        print()
        print(f"[SUCCESS] Successfully created: {output_path}")
        print(f"Output video: {output_path}")
        print(f"Processing completed!")
        
        sys.exit(0)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
