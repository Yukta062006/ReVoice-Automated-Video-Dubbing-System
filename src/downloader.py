import subprocess
import re
import time
from pathlib import Path

from src.config import FFMPEG_PATH


def download_video(source: str, output_dir: Path) -> tuple[Path, Path]:
    """
    Download a YouTube video or copy a local file and extract its audio.
    
    Args:
        source: Either a YouTube URL or a path to a local video file
        
    Returns:
        tuple: (video_path, audio_path)
    """
    source_path = Path(source)
    
    # Check if source is a local file
    if source_path.exists() and source_path.is_file():
        print(f"   Using local file: {source_path.name}")
        
        # Copy to temp as video.mp4
        video_path = output_dir / "video.mp4"
        subprocess.run([
            FFMPEG_PATH,
            "-i", str(source_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-y",
            str(video_path)
        ], capture_output=True, shell=True)
        
        if not video_path.exists():
            raise RuntimeError("Failed to copy local video file")
        
        # Extract audio
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
        
        return (video_path, audio_path)
    
    # Otherwise, treat as YouTube URL
    if not (source.startswith("http") or "youtube.com" in source or "youtu.be" in source):
        raise ValueError("Invalid YouTube URL or file path")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download video using yt-dlp
    output_pattern = str(output_dir / "video.%(ext)s")
    cmd = [
        "python", "-m", "yt_dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", output_pattern,
        "--no-playlist",
        "--retries", "3",
        "--fragment-retries", "3",
        "--retry-sleep", "2",
        source
    ]
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                stderr = result.stderr.lower()
                if "video unavailable" in stderr or "private video" in stderr:
                    raise RuntimeError("Video is unavailable or private")
                if "timed out" in stderr or "connection" in stderr:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"   Download failed, retrying ({retry_count}/{max_retries})...")
                        time.sleep(2)
                        continue
                    raise RuntimeError(f"Download failed after {max_retries} retries: {result.stderr}")
                raise RuntimeError(f"Download failed: {result.stderr}")
            else:
                break
        except subprocess.CalledProcessError as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"   Download failed, retrying ({retry_count}/{max_retries})...")
                time.sleep(2)
                continue
            raise RuntimeError(f"Download failed: {str(e)}")
    
    # Find the downloaded video file
    video_files = list(output_dir.glob("video*.mp4"))
    if not video_files:
        # Try to find any mp4 file
        video_files = list(output_dir.glob("*.mp4"))
    
    if not video_files:
        raise RuntimeError("No video file found after download")
    
    video_path = video_files[0]
    
    # Extract audio using ffmpeg
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
    
    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            raise RuntimeError(f"Audio extraction failed: {result.stderr}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio extraction failed: {str(e)}")
    
    return (video_path, audio_path)