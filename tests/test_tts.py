from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from src.tts import generate_all_segments


def test_skips_empty_text():
    """Test that segments with empty en_text are skipped."""
    segments = [
        {"start": 0.0, "end": 1.0, "en_text": "Hello"},
        {"start": 1.0, "end": 2.0, "en_text": ""},
        {"start": 2.0, "end": 3.0, "en_text": "   "},
        {"start": 3.0, "end": 4.0, "en_text": "World"},
    ]
    
    with patch("src.tts.generate_tts") as mock_generate, \
         patch("src.tts.AudioSegment"):
        
        result = generate_all_segments(segments, Path("temp"), "en-US-GuyNeural")
        
        # Only 2 segments should have tts_path (non-empty text)
        count = sum(1 for s in result if "tts_path" in s)
        assert count == 2


def test_tts_output_path_naming():
    """Test that segment files are named correctly."""
    segments = [
        {"start": 0.0, "end": 1.0, "en_text": "First"},
        {"start": 1.0, "end": 2.0, "en_text": "Second"},
        {"start": 2.0, "end": 3.0, "en_text": "Third"},
    ]
    
    with patch("src.tts.generate_tts") as mock_generate, \
         patch("src.tts.AudioSegment"):
        
        result = generate_all_segments(segments, Path("temp"), "en-US-GuyNeural")
        
        # Check file naming pattern
        assert result[0]["tts_path"].name == "seg_0000.wav"
        assert result[1]["tts_path"].name == "seg_0001.wav"
        assert result[2]["tts_path"].name == "seg_0002.wav"