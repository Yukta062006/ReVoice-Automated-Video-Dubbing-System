# ReVoice — Automated Video Dubbing System

> ReVoice turns any YouTube video into a natural English-dubbed version.

## What It Does

ReVoice is a CLI tool that automatically translates YouTube videos into English:

1. **Downloads** any YouTube video (or short) using yt-dlp
2. **Extracts** the audio and transcribes speech using Whisper AI
3. **Translates** non-English speech to English using Helsinki-NLP models
4. **Generates** natural English TTS audio using Edge TTS
5. **Muxes** the dubbed audio back into the original video without re-encoding

The result is a fully dubbed video that preserves the original visuals while replacing speech with clear English audio.

## Features

- Support for all YouTube video URLs (full videos and shorts)
- Multiple Whisper model sizes for speed/quality tradeoff
- Natural-sounding Edge TTS voices
- Automatic timing adjustment to match original speech rhythm
- No re-encoding of original video stream
- Cross-platform (Windows, macOS, Linux)

## Requirements

- **Python 3.8+**
- **FFmpeg** installed and in PATH
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Installation

```bash
# Clone or download the project
cd ReVoice

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (if not already installed)
# Windows: winget install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

## Usage

```bash
# Basic usage (auto-detects language)
python main.py "https://www.youtube.com/watch?v=XXXXX"

# With custom model and voice
python main.py "https://youtu.be/XXXXX" --model small --voice en-GB-RyanNeural

# Specify output directory
python main.py "YOUTUBE_URL" -o ./my-dubbed-videos

# Keep temporary files for debugging
python main.py "YOUTUBE_URL" --keep-temp
```

### Command Line Options

```
positional arguments:
  url                   YouTube URL to process

optional arguments:
  -h, --help            show this help message and exit
  --output, -o          Output directory (default: output)
  --model, -m           Whisper model: tiny/base/small/medium/large (default: base)
  --voice, -v           TTS voice name (default: en-US-GuyNeural)
  --language, -l        Override source language (default: auto-detect)
  --keep-temp           Keep temporary files after processing
  --no-cleanup          Alias for --keep-temp
```

### Available TTS Voices

Some popular Edge TTS voices:
- `en-US-GuyNeural` (default) - American male
- `en-US-JennyNeural` - American female
- `en-GB-RyanNeural` - British male
- `en-AU-NatashaNeural` - Australian female

## Architecture

```
YouTube URL
    |
    v
[Downloader] --> yt-dlp downloads video
    |
    v
[Audio Extractor] --> ffmpeg extracts audio
    |
    v
[Transcriber] --> Whisper transcribes speech
    |
    v
[Translator] --> Helsinki-NLP translates to English
    |
    v
[TTS Generator] --> Edge TTS generates English audio
    |
    v
[Audio Processor] --> Aligns TTS with original timing
    |
    v
[Video Mixer] --> ffmpeg muxes audio into video
    |
    v
Final Dubbed Video
```

## Supported Languages

Whisper auto-detects and supports all languages. Translation works for:
- English, Spanish, French, German, Chinese, Japanese, Korean, Russian, Arabic, Portuguese, Italian
- Indian languages: Hindi, Bengali, Tamil, Telugu, Malayalam, Gujarati, Marathi, Punjabi, Urdu, Kannada, Odia, Assamese
- Plus many more via Helsinki-NLP multilingual models

## Troubleshooting

**"FFmpeg not found"**
- Install FFmpeg and add it to your PATH

**"Video unavailable or private"**
- The video may be private, removed, or region-locked

**Slow processing**
- Use smaller Whisper models (`--model tiny` or `--model base`)
- Shorter videos process faster

**Poor translation quality**
- Some language pairs may have limited model support
- Try different Whisper models for better transcription

## License

This project is provided as-is for educational and personal use.

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloading
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- [Helsinki-NLP](https://github.com/Helsinki-NLP) - Translation models
- [Edge TTS](https://github.com/rany2/edge-tts) - Text-to-speech
- [pydub](https://github.com/jiaaro/pydub) - Audio processing