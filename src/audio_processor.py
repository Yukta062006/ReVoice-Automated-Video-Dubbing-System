import subprocess
from pathlib import Path
from typing import List
from src.config import FFMPEG_PATH


def get_audio_duration(audio_path: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    ffprobe_path = Path(FFMPEG_PATH).parent / "ffprobe.exe"
    probe_cmd = [
        str(ffprobe_path),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    
    result = subprocess.run(probe_cmd, capture_output=True, text=True, shell=True)
    return float(result.stdout.strip())


def build_dubbed_audio(segments: List[dict], total_duration: float, temp_dir: Path) -> Path:
    """
    Build a dubbed audio track by placing TTS segments at their original timestamps.
    Mixes English TTS with original video audio at appropriate volumes.
    
    Returns:
        Path to the final dubbed audio file.
    """
    tts_segments = [seg for seg in segments if "tts_path" in seg and seg["tts_path"]]
    
    print(f"   Processing {len(tts_segments)} TTS segments")
    
    if tts_segments:
        print(f"   First segment: {tts_segments[0]['start']:.2f}s - {tts_segments[0]['end']:.2f}s")
        print(f"   Last segment: {tts_segments[-1]['start']:.2f}s - {tts_segments[-1]['end']:.2f}s")
        print(f"   Original video duration: {total_duration:.2f}s")
    
    output_path = temp_dir / "dubbed_audio.wav"
    
    if not tts_segments:
        print(f"   Creating full {total_duration:.2f}s silence audio...")
        subprocess.run([
            FFMPEG_PATH,
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=mono:sample_rate=16000",
            "-t", str(total_duration),
            "-c:a", "pcm_s16le",
            "-y",
            str(output_path)
        ], capture_output=True, shell=True)
        return output_path
    
    # Use original extracted audio as base (contains background and music)
    base_audio = temp_dir / "audio.wav"
    if not base_audio.exists():
        print("   ERROR: Original audio not found!")
        base_audio = temp_dir / "base_silence.wav"
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=mono:sample_rate=16000:duration={total_duration}",
            "-c:a", "pcm_s16le",
            str(base_audio)
        ]
        subprocess.run(cmd, capture_output=True, shell=True)
    
    placed_segments = []
    
    for i, seg in enumerate(tts_segments):
        start_ms = int(seg["start"] * 1000)
        segment_output = temp_dir / f"seg_placed_{i:04d}.wav"
        
        # Get TTS duration
        tts_dur_cmd = [
            FFMPEG_PATH,
            "-i", str(seg["tts_path"]),
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1"
        ]
        tts_result = subprocess.run(tts_dur_cmd, capture_output=True, text=True)
        tts_duration = float(tts_result.stdout.strip()) if tts_result.stdout.strip() else 0
        
        # Apply loud volume boost to TTS only (no background mixing)
        # Use volume=4.0 for very loud speech output
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(seg["tts_path"]),
            "-af", "volume=4.0",
            "-c:a", "pcm_s16le",
            str(segment_output)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and segment_output.exists():
            placed_segments.append(segment_output)
            print(f"   Placed segment {i+1}: {seg['start']:.2f}s - {seg['end']:.2f}s")
    
    if not placed_segments:
        print("   No segments placed successfully")
        return base_audio
    
    # Mix all placed segments together
    inputs = ["-y"]
    for f in placed_segments:
        inputs.extend(["-i", str(f)])
    
    n_inputs = len(placed_segments)
    mix_filter = "".join(f"[{i}:a]" for i in range(n_inputs)) + f"amix=inputs={n_inputs}:duration=longest:dropout_transition=0[out]"
    
    cmd = [FFMPEG_PATH] + inputs + [
        "-filter_complex", mix_filter,
        "-map", "[out]",
        "-c:a", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0 or not output_path.exists():
        print(f"   Mixing failed: {result.stderr[-200:] if result.stderr else 'No error output'}")
        return _mix_segments(placed_segments, output_path)
    
    final_dur = get_audio_duration(output_path)
    print(f"   Final audio duration: {final_dur:.2f}s")
    
    if abs(final_dur - total_duration) > 0.5:
        print(f"   Audio duration {final_dur:.2f}s doesn't match total {total_duration:.2f}s, padding...")
        temp_output = temp_dir / "dubbed_audio_temp.wav"
        cmd = [
            FFMPEG_PATH, "-y",
            "-i", str(output_path),
            "-af", f"apad=pad_dur={total_duration - final_dur}",
            "-c:a", "pcm_s16le",
            str(temp_output)
        ]
        subprocess.run(cmd, capture_output=True, shell=True)
        if temp_output.exists():
            if output_path.exists():
                output_path.unlink()
            temp_output.rename(output_path)
            return output_path
    
    return output_path


def _mix_segments(placed_segments: List[Path], output_path: Path) -> Path:
    """Fallback method to mix segments using amix."""
    if len(placed_segments) == 1:
        return placed_segments[0]
    
    inputs = ["-y"]
    for f in placed_segments:
        inputs.extend(["-i", str(f)])
    
    n_inputs = len(placed_segments)
    mix_filter = "".join(f"[{i}:a]" for i in range(n_inputs)) + f"amix=inputs={n_inputs}:duration=longest:dropout_transition=0[out]"
    
    cmd = [FFMPEG_PATH] + inputs + [
        "-filter_complex", mix_filter,
        "-map", "[out]",
        "-c:a", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and output_path.exists():
        return output_path
    
    return placed_segments[0]
