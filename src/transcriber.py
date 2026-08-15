import whisper
from pathlib import Path


def transcribe(audio_path: Path, model_name: str = "base", language: str | None = None) -> list[dict]:
    """
    Transcribe audio using Whisper.
    
    Args:
        audio_path: Path to audio file
        model_name: Whisper model size (tiny, base, small, medium, large)
        language: Source language code (e.g., "fr" for French). If None, auto-detect.
    
    Returns:
        list[dict]: List of segments with start, end, text, language keys
    """
    print("Transcribing audio... (this may take several minutes for long videos)")
    
    # Load Whisper model
    model = whisper.load_model(model_name)
    
    # Prepare transcribe arguments
    transcribe_args = {
        "verbose": False,
        "fp16": False,  # Use FP32 for CPU (more reliable)
        "word_timestamps": True,  # Word-level timestamps for better alignment
    }
    
    # Explicitly set language if provided (critical for accurate French transcription)
    if language:
        transcribe_args["language"] = language
        print(f"   Using specified language: {language}")
    else:
        print("   Auto-detecting language...")
    
    # Additional quality settings for better transcription
    # Use beam search for more accurate results (default is 1, we use 5)
    transcribe_args["beam_size"] = 5
    
    # Temperature settings - use low temperature for deterministic results
    transcribe_args["temperature"] = 0.0
    
    # Compression ratio threshold for detecting repetition
    transcribe_args["compression_ratio_threshold"] = 2.4
    
    # Logprob threshold for filtering low-probability tokens
    transcribe_args["logprob_threshold"] = -1.0
    
    # Transcribe the audio
    result = model.transcribe(str(audio_path), **transcribe_args)
    
    # Extract word-level timestamps and group into segments
    # This ensures full video coverage
    word_segments = []
    if result.get("words"):
        current_segment = None
        for word in result["words"]:
            word_text = word["word"].strip()
            if word_text:
                if current_segment is None:
                    current_segment = {
                        "start": word["start"],
                        "end": word["end"],
                        "text": word_text
                    }
                elif word["start"] - current_segment["end"] < 1.0:  # Merge words close together
                    current_segment["end"] = word["end"]
                    current_segment["text"] += word_text
                else:
                    word_segments.append(current_segment)
                    current_segment = {
                        "start": word["start"],
                        "end": word["end"],
                        "text": word_text
                    }
        if current_segment:
            word_segments.append(current_segment)
    
    # If no words detected, fall back to sentence segments
    if not word_segments:
        word_segments = result.get("segments", [])
    
    # Get language (from forced language or auto-detected)
    detected_language = language or result.get("language", "en")
    
    # Add language to each segment and filter empty segments
    filtered_segments = []
    for seg in word_segments:
        text = seg.get("text", "").strip()
        if text:
            filtered_segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": text,
                "language": detected_language
            })
    
    return filtered_segments