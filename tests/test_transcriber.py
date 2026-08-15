from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from src.transcriber import transcribe


def test_empty_segments_filtered():
    """Test that empty segments are filtered out."""
    # Mock whisper result with empty segments
    mock_result = {
        "segments": [
            {"start": 0.0, "end": 1.0, "text": ""},
            {"start": 1.0, "end": 2.0, "text": "Hello world"},
            {"start": 2.0, "end": 3.0, "text": "   "},
            {"start": 3.0, "end": 4.0, "text": "Test"},
        ],
        "language": "en"
    }
    
    with patch("src.transcriber.whisper.load_model") as mock_load:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = mock_result
        mock_load.return_value = mock_model
        
        result = transcribe(Path("test.wav"), "base")
        
        # Should only have non-empty segments
        assert len(result) == 2
        assert result[0]["text"] == "Hello world"
        assert result[1]["text"] == "Test"


def test_segment_structure():
    """Test that output segments have required keys."""
    mock_result = {
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "Hello"},
        ],
        "language": "en"
    }
    
    with patch("src.transcriber.whisper.load_model") as mock_load:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = mock_result
        mock_load.return_value = mock_model
        
        result = transcribe(Path("test.wav"), "base")
        
        # Check structure
        assert "start" in result[0]
        assert "end" in result[0]
        assert "text" in result[0]
        assert "language" in result[0]
        assert result[0]["start"] == 0.0
        assert result[0]["end"] == 1.0
        assert result[0]["text"] == "Hello"
        assert result[0]["language"] == "en"