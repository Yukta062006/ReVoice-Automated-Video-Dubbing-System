import shutil
import sys
from pathlib import Path

PROJECT_NAME = "ReVoice"
VERSION = "1.0.0"

TEMP_DIR = Path("temp")
OUTPUT_DIR = Path("output")
INPUT_DIR = Path("input")

WHISPER_MODEL = "base"
SUPPORTED_LANGUAGES = [
    "en", "hi", "bn", "ta", "te", "ml", "gu", "mr", "pa", "ur", "kn", "or", "as",
    "es", "fr", "de", "zh", "ja", "ko", "ru", "ar", "pt", "it", "nl", "pl", "tr",
    "th", "vi", "id", "uk", "el", "he", "fa", "ca", "cs", "ro", "hu", "sk", "sl",
    "hr", "sr", "bg", "lt", "lv", "et", "fi", "sv", "no", "da"
]
DEFAULT_TTS_VOICE = "en-US-GuyNeural"
MAX_SEGMENT_DURATION = 30.0
SPEED_ADJUSTMENT_THRESHOLD = 1.3

# FFmpeg path (set this if ffmpeg is not in PATH)
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-9.0-full_build\bin\ffmpeg.exe"


def check_dependencies():
    """Check if required dependencies are available."""
    # Check ffmpeg
    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd is None:
        # Try the hardcoded path
        if Path(FFMPEG_PATH).exists():
            import subprocess
            # Verify it works
            try:
                subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, check=True)
                # Add to PATH for this session
                import os
                os.environ["PATH"] = str(Path(FFMPEG_PATH).parent) + os.pathsep + os.environ.get("PATH", "")
                ffmpeg_cmd = FFMPEG_PATH
            except subprocess.SubprocessError:
                pass
    
    if ffmpeg_cmd is None:
        print("FFmpeg not found. Install it from https://ffmpeg.org/download.html")
        print("Windows: winget install ffmpeg")
        print("Mac: brew install ffmpeg")
        print("Linux: sudo apt install ffmpeg")
        sys.exit(1)