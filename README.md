# ReVoice

## Automated AI Video Dubbing System

ReVoice is a Python-based automated video dubbing system that converts speech from a foreign-language YouTube video into English audio while preserving the original video.

The system automates the complete workflow:

**YouTube URL → Download → Audio Extraction → Transcription → Translation → English TTS → Timestamp Synchronization → Final Dubbed Video**

---

## Overview

ReVoice is designed to simplify the video dubbing process by combining speech recognition, translation, text-to-speech, and audio/video processing into a single pipeline.

The system accepts a YouTube URL as input, downloads the video, extracts its audio, transcribes the speech using Whisper, translates the transcript into English, generates English speech, synchronizes the generated audio with the original timestamps, and produces a final English-dubbed video.

The original video visuals are preserved while the original speech audio is replaced with synchronized English audio.

---

## Features

- YouTube video downloading using yt-dlp
- Multilingual speech transcription using Whisper
- Timestamped transcription
- Source-language to English translation
- Natural English text-to-speech generation
- Timestamp-based audio synchronization
- Original video preservation
- FFmpeg-based audio and video processing
- Local video processing
- Terminal progress reporting
- Support for longer-duration videos

---

## Architecture

```text
                    YouTube URL
                         |
                         v
                  +--------------+
                  |    yt-dlp    |
                  | Video Download|
                  +------+-------+
                         |
                         v
                  +--------------+
                  |    FFmpeg    |
                  | Audio Extract|
                  +------+-------+
                         |
                         v
                  +--------------+
                  |   Whisper    |
                  | Transcription|
                  | + Timestamps |
                  +------+-------+
                         |
                         v
                  +--------------+
                  | Translation  |
                  | Source → Eng |
                  +------+-------+
                         |
                         v
                  +--------------+
                  |     TTS      |
                  | English Voice|
                  +------+-------+
                         |
                         v
                  +--------------+
                  | Synchronizer |
                  |  Timestamps  |
                  +------+-------+
                         |
                         v
                  +--------------+
                  |    FFmpeg    |
                  | Audio + Video|
                  +------+-------+
                         |
                         v
                English-Dubbed Video

                ## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application and pipeline |
| yt-dlp | YouTube video downloading |
| Whisper | Multilingual speech transcription |
| Translation | Source-language to English translation |
| Text-to-Speech | English speech generation |
| FFmpeg | Audio extraction and video processing |

---

## Workflow

### 1. YouTube Video Download

The system accepts a YouTube URL and downloads the source video using `yt-dlp`.

```text
YouTube URL
     |
     v
   yt-dlp
     |
     v
Source Video
