import shutil
import time
from pathlib import Path
from datetime import timedelta

from src.downloader import download_video
from src.transcriber import transcribe
from src.translator import Translator
from src.tts import generate_all_segments
from src.audio_processor import build_dubbed_audio, get_audio_duration
from src.video_processor import mux_video_audio, verify_output


class DubbingPipeline:
    """Main pipeline for dubbing videos."""
    
    def __init__(
        self,
        url: str,
        output_dir: Path,
        temp_dir: Path,
        whisper_model: str = "base",
        tts_voice: str = "en-US-GuyNeural",
        keep_temp: bool = False,
        language_override: str | None = None
    ):
        self.url = url
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.whisper_model = whisper_model
        self.tts_voice = tts_voice
        self.keep_temp = keep_temp
        self.language_override = language_override
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, name: str) -> str:
        """Sanitize filename for filesystem."""
        # Remove or replace invalid characters
        invalid = '<>:"/\\|?*'
        for char in invalid:
            name = name.replace(char, "_")
        return name
    
    def run(self) -> Path:
        """Run the complete dubbing pipeline."""
        start_time = time.time()
        
        try:
            # Step 1: Download video
            print("[1/6] Downloading video...")
            video_path, audio_path = download_video(self.url, self.temp_dir)
            print(f"   Downloaded: {video_path.name}")
            
            # Step 2: Get audio duration
            print("[2/6] Extracting and validating audio...")
            total_duration = get_audio_duration(audio_path)
            print(f"   Audio duration: {total_duration:.2f} seconds")
            
            # Step 3: Transcribe
            # Use language override if provided, otherwise auto-detect
            transcription_language = self.language_override
            print(f"[3/6] Transcribing speech... (model: {self.whisper_model})")
            if transcription_language:
                print(f"   Source language: {transcription_language}")
            segments = transcribe(audio_path, self.whisper_model, language=transcription_language)
            language = segments[0]["language"] if segments else "unknown"
            print(f"   Found {len(segments)} speech segments, language: {language}")
            
            # Step 4: Translate
            print("[4/6] Translating to English...")
            translator = Translator(self.language_override or language)
            segments = translator.translate(segments)
            print(f"   Translated {len(segments)} segments")
            
            # Step 5: Generate TTS
            print("[5/6] Generating English audio...")
            segments = generate_all_segments(segments, self.temp_dir, self.tts_voice)
            print(f"   Generated {len(segments)} TTS audio files")
            
            # Step 6: Build dubbed audio with debug info
            print("[6/6] Creating dubbed video...")
            
            # Calculate segment coverage
            if segments:
                first_start = min(s.get("start", 0) for s in segments if s.get("start"))
                last_end = max(s.get("end", 0) for s in segments if s.get("end"))
                coverage = last_end - first_start
                print(f"   Transcription coverage: {first_start:.2f}s to {last_end:.2f}s = {coverage:.2f}s")
                print(f"   Original video duration: {total_duration:.2f}s")
                print(f"   Number of transcription segments: {len(segments)}")
                print(f"   Number of translated segments: {len(segments)}")
                print(f"   Number of TTS segments: {len([s for s in segments if 'tts_path' in s])}")
            else:
                print(f"   Transcription coverage: N/A")
                print(f"   Original video duration: {total_duration:.2f}s")
            
            # Build dubbed audio
            dubbed_wav = build_dubbed_audio(segments, total_duration, self.temp_dir)
            print(f"   Built dubbed audio: {dubbed_wav.name}")
            
            # Step 6: Build dubbed audio
            print("[6/6] Creating dubbed video...")
            
            # Build dubbed audio
            dubbed_wav = build_dubbed_audio(segments, total_duration, self.temp_dir)
            print(f"   Built dubbed audio: {dubbed_wav.name}")
            
            # Get video title from URL (simplified)
            video_title = self._extract_video_title()
            output_filename = f"{self.sanitize_filename(video_title)}_dubbed.mp4"
            output_path = self.output_dir / output_filename
            
            # Mux video and audio
            print(f"   Muxing video and audio...")
            mux_video_audio(video_path, dubbed_wav, output_path)
            print(f"   Muxing completed")
            
            # Verify output
            if verify_output(output_path, total_duration):
                print("   Output verified successfully")
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            
            # Cleanup
            if not self.keep_temp:
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Print completion
            print("✓ Completed successfully.")
            print(f"Output: {output_path}")
            print(f"Processing time: {elapsed_str}")
            
            return output_path
            
        except Exception as e:
            # Cleanup on failure unless keep_temp
            if not self.keep_temp:
                try:
                    shutil.rmtree(self.temp_dir)
                except Exception:
                    pass
            
            raise e
    
    def _extract_video_title(self) -> str:
        """Extract video title from URL (simple implementation)."""
        # For now, return a simple title - could be enhanced with yt-dlp
        if "watch?v=" in self.url:
            return self.url.split("watch?v=")[-1][:11]
        elif "youtu.be/" in self.url:
            return self.url.split("youtu.be/")[-1][:11]
        return "video"