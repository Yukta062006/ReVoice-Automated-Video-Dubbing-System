from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from src.translator import Translator


def test_english_passthrough():
    """Test that English text is passed through unchanged."""
    translator = Translator("en")
    
    segments = [
        {"start": 0.0, "end": 1.0, "text": "Hello world"},
        {"start": 1.0, "end": 2.0, "text": "This is English"},
    ]
    
    result = translator.translate(segments)
    
    assert len(result) == 2
    assert result[0]["en_text"] == "Hello world"
    assert result[1]["en_text"] == "This is English"


def test_translation_adds_en_text():
    """Test that translation adds en_text key to segments."""
    # Mock the model
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    
    def mock_generate(*args, **kwargs):
        return [[1, 2, 3, 4]]  # Mock output IDs
    
    mock_model.generate = mock_generate
    
    def mock_decode(ids, *args, **kwargs):
        return "Hello world"
    
    mock_tokenizer.decode = mock_decode
    mock_tokenizer.return_value = {"input_ids": [[1, 2, 3]]}
    
    with patch("src.translator.AutoTokenizer.from_pretrained") as mock_tok, \
         patch("src.translator.AutoModelForSeq2SeqLM.from_pretrained") as mock_model_load:
        
        mock_tok.return_value = mock_tokenizer
        mock_model_load.return_value = mock_model
        
        translator = Translator("hi")
        
        segments = [
            {"start": 0.0, "end": 1.0, "text": "Namaste"},
        ]
        
        result = translator.translate(segments)
        
        assert len(result) == 1
        assert "en_text" in result[0]