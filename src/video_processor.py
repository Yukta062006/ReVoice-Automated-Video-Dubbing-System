import subprocess
from pathlib import Path

from src.config import FFMPEG_PATH


def mux_video_audio(video_path: Path, audio_path: Path, output_path: Path) -> None:
    """
    Mux video and audio together without re-encoding.
    
    Args:
        video_path: Path to original video
        audio_path: Path to dubbed audio (WAV)
        output_path: Path for output video
    """
    cmd = [
        FFMPEG_PATH,
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg muxing failed: {result.stderr}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg muxing failed: {str(e)}")
    
    # Verify output exists and has content
    if not output_path.exists():
        raise RuntimeError("FFmpeg muxing failed: output file not created")
    
    if output_path.stat().st_size == 0:
        raise RuntimeError("FFmpeg muxing failed: output file is empty")


def verify_output(output_path: Path, original_duration: float) -> bool:
    """
    Verify the output video duration is within tolerance.
    
    Returns True if duration is within 5% of original.
    """
    # Use ffmpeg's ffprobe (same directory as ffmpeg)
    ffprobe_path = Path(FFMPEG_PATH).parent / "ffprobe.exe"
    probe_cmd = [
        str(ffprobe_path),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            return False
        
        output_duration = float(result.stdout.strip())
        
        # Check within 5% tolerance
        tolerance = original_duration * 0.05
        return abs(output_duration - original_duration) <= tolerance
    
    except Exception:
        return False