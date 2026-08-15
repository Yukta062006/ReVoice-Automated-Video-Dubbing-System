import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.downloader import download_video


def test_invalid_url_raises():
    """Test that invalid URLs raise ValueError."""
    with pytest.raises(ValueError, match="Invalid YouTube URL"):
        download_video("not-a-url", Path("temp"))
    
    with pytest.raises(ValueError, match="Invalid YouTube URL"):
        download_video("ftp://example.com", Path("temp"))


def test_valid_url_format():
    """Test that valid YouTube URLs pass validation."""
    # These should not raise ValueError (they might fail later in the process)
    # due to mocking, we test that validation passes
    with patch("src.downloader.subprocess.run") as mock_run, \
         patch("pathlib.Path.glob") as mock_glob:
        
        # Setup mock to return a video file
        mock_glob.return_value = [Path("temp/video.mp4")]
        
        # Create a mock for the download subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Mock ffmpeg subprocess for audio extraction
        with patch("subprocess.run") as ffmpeg_mock:
            ffmpeg_result = MagicMock()
            ffmpeg_result.returncode = 0
            ffmpeg_mock.return_value = ffmpeg_result
            
            try:
                download_video("https://www.youtube.com/watch?v=test123", Path("temp"))
            except (RuntimeError, FileNotFoundError):
                # Expected to fail later (mocking), but not on URL validation
                pass
            
            try:
                download_video("https://youtu.be/test123", Path("temp"))
            except (RuntimeError, FileNotFoundError):
                # Expected to fail later (mocking), but not on URL validation
                pass