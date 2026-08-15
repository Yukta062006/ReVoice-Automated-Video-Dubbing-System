import subprocess
from src.config import FFMPEG_PATH

# Patch pydub for Python 3.13+ compatibility before imports
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
import time
import edge_tts
from pydub import AudioSegment
from pathlib import Path
from tqdm import tqdm
import re


# Edge TTS voices for gender-specific pronunciation
VOICE_MALE = "en-US-GuyNeural"
VOICE_FEMALE = "en-US-AvaNeural"
VOICE_NEUTRAL = "en-US-GuyNeural"

# Gender detection keywords - but we'll use male voice for all
FEMALE_KEYWORDS = ["her", "she", "woman", "lady", "girl", "她们", "她"]
MALE_KEYWORDS = ["he", "him", "his", "man", "boy", "they", "them", "their", "they're", "他们", "他"]


def detect_gender(text: str) -> str:
    """Detect gender from text to select appropriate voice."""
    text_lower = text.lower()
    
    # Check for female keywords
    for keyword in FEMALE_KEYWORDS:
        if keyword.lower() in text_lower:
            return "female"
    
    # Check for male keywords
    for keyword in MALE_KEYWORDS:
        if keyword.lower() in text_lower:
            return "male"
    
    # Default to neutral/male for general content
    return "neutral"


def get_voice_for_gender(gender: str) -> str:
    """Get appropriate Edge TTS voice for gender."""
    # Always use male voice for all segments
    return "en-US-GuyNeural"


def improve_pronunciation(text: str) -> str:
    """Apply text improvements for better TTS pronunciation."""
    if not text:
        return text
    
    result = text
    
    # Remove extra spaces
    result = re.sub(r'\s+', ' ', result)
    
    # Add commas for better pauses
    result = re.sub(r',(\w)', r', \1', result)
    result = re.sub(r'\.(\w)', r'. \1', result)
    
    # Ensure proper punctuation
    if not result.endswith('.'):
        result = result + '.'
    
    return result.strip()


async def generate_tts_async(text: str, voice: str, output_path: Path, max_retries: int = 3) -> None:
    """Generate TTS audio asynchronously using Edge TTS with improved settings."""
    retry_count = 0
    last_error = None
    
    # Clean text - remove empty or invalid text
    if not text or not text.strip():
        raise RuntimeError("Empty text provided for TTS")
    
    text = text.strip()
    
    # Improve pronunciation with text formatting
    text = improve_pronunciation(text)
    
    while retry_count < max_retries:
        try:
            # Use improved voice settings for better pronunciation
            # Rate: -10% to -30% for clearer speech
            # Pitch: varies by gender
            communicate = edge_tts.Communicate(
                text, 
                voice,
                rate="-15%",
                pitch="+0Hz"
            )
            temp_path = output_path.with_suffix(".mp3")
            
            await communicate.save(str(temp_path))
            
            # Check if MP3 file has content
            if not temp_path.exists() or temp_path.stat().st_size < 100:
                raise RuntimeError("TTS returned empty audio file")
            
            # Use FFmpeg to convert MP3 to WAV with proper parameters
            # This avoids the pydub fake audioop issue
            cmd = [
                FFMPEG_PATH,
                "-i", str(temp_path),
                "-ar", "16000",
                "-ac", "1",
                "-sample_fmt", "s16",
                "-y",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            # Delete temporary MP3
            if temp_path.exists():
                temp_path.unlink()
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
            
            # Verify output WAV has content
            if not output_path.exists() or output_path.stat().st_size < 100:
                raise RuntimeError("Output WAV file is empty or too small")
            
            return
            
        except Exception as e:
            retry_count += 1
            last_error = str(e)
            if retry_count < max_retries:
                print(f"   TTS retry {retry_count}/{max_retries} for segment...")
                time.sleep(1)
                continue
            raise RuntimeError(f"TTS generation failed after {max_retries} retries: {last_error}")


def generate_tts(text: str, voice: str, output_path: Path) -> None:
    """Synchronous wrapper for generate_tts_async."""
    asyncio.run(generate_tts_async(text, voice, output_path))


def generate_all_segments(segments: list[dict], temp_dir: Path, voice: str) -> list[dict]:
    """Generate TTS audio for all segments with gender-aware voice selection."""
    # Filter segments with non-empty en_text
    segments_to_process = []
    for seg in segments:
        if seg.get("en_text", "").strip():
            segments_to_process.append(seg)
    
    print(f"   Processing {len(segments_to_process)} segments with TTS...")
    
    # Generate TTS for each segment
    for i, segment in enumerate(segments_to_process):
        # Detect gender and select appropriate voice
        text = segment.get("en_text", "")
        gender = detect_gender(text)
        selected_voice = get_voice_for_gender(gender)
        
        print(f"   Segment {i+1}/{len(segments_to_process)}: gender={gender}, voice={selected_voice}")
        
        output_file = temp_dir / f"seg_{i:04d}.wav"
        try:
            generate_tts(text, selected_voice, output_file)
            segment["tts_path"] = output_file
        except Exception as e:
            print(f"   WARNING: TTS failed for segment {i+1}: {e}")
            # Create a silent audio file for empty segments
            print(f"   Creating silent audio for segment {i+1}...")
            subprocess.run([
                FFMPEG_PATH,
                "-f", "lavfi",
                "-i", "anullsrc=channel_layout=mono:sample_rate=16000",
                "-t", "0.1",  # 100ms silence
                "-c:a", "pcm_s16le",
                "-y",
                str(output_file)
            ], capture_output=True, shell=True)
            segment["tts_path"] = output_file
    
    # Count successful TTS generation
    successful = len([s for s in segments if "tts_path" in s])
    print(f"   Successfully generated TTS for {successful}/{len(segments_to_process)} segments")
    
    return segments
