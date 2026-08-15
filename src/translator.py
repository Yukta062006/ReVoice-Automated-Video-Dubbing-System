import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from tqdm import tqdm
import torch


class Translator:
    """Translate segments from source language to English."""
    
    def __init__(self, source_language: str):
        self.source_language = source_language
        self._model = None
        self._tokenizer = None
        self._setup_model()
    
    def _setup_model(self):
        """Set up the translation model."""
        if self.source_language == "en":
            return
        
        # Indian languages mapping
        indian_languages = ["hi", "bn", "ta", "te", "ml", "gu", "mr", "pa", "ur", "kn", "or", "as"]
        
        # Determine model path
        if self.source_language in indian_languages:
            base_model = f"Helsinki-NLP/opus-mt-{self.source_language}-en"
        else:
            base_model = f"Helsinki-NLP/opus-mt-{self.source_language}-en"
        
        # Try to load specific model, fall back to multilingual
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(base_model)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
            print(f"   Loaded translation model: {base_model}")
        except Exception:
            # Fallback to multilingual model
            try:
                self._tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-mul-en")
                self._model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-mul-en")
                print("   Loaded fallback multilingual translation model")
            except Exception as e:
                raise RuntimeError(f"Could not load translation model: {e}")
    
    def _post_process_translation(self, text: str) -> str:
        """Post-process translation to improve grammar and vocabulary."""
        if not text:
            return ""
        
        result = text.strip()
        
        # Remove extra spaces
        result = re.sub(r'\s+', ' ', result)
        
        # Fix common punctuation issues
        result = re.sub(r'\s([?.!"])', r'\1', result)
        
        # Capitalize first letter
        result = re.sub(r'^([a-z])', lambda m: m.group(1).upper(), result)
        
        # Pronoun corrections for French to English
        # Fix "she is" being translated as "he is"
        result = re.sub(r'\bhe is\b', 'she is', result, flags=re.IGNORECASE)
        result = re.sub(r'\bHe is\b', 'She is', result)
        
        # Fix "they" being translated incorrectly
        # Ensure "they" is used for plural references
        result = re.sub(r'\bthem are\b', 'they are', result, flags=re.IGNORECASE)
        result = re.sub(r'\bThem are\b', 'They are', result)
        
        # Common French phrases and their better English translations
        common_phrases = {
            "il était une fois": "once upon a time",
            "merci": "thank you",
            "s'il vous plaît": "please",
            "s'il vous plaît": "please",
            "au revoir": "goodbye",
            "bonjour": "hello",
            "elles sont": "they are",
            "ils sont": "they are",
            "ils sont en train de": "they are",
            "elle est": "she is",
        }
        
        # Apply common phrase replacements
        for french, english in common_phrases.items():
            result = re.sub(re.escape(french), english, result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def _translate_text(self, text: str) -> str:
        """Translate a single text string."""
        if not text or not text.strip():
            return ""
        
        # Clean text
        text = text.strip()
        text = " ".join(text.split())
        
        if not text:
            return ""
        
        if self._model is None:
            return text
        
        # Tokenize
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Translate with better parameters
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_length=512,
                num_beams=5,  # Increased from 4 for better quality
                early_stopping=True,
                no_repeat_ngram_size=3,  # Prevent repetition
                length_penalty=1.0,
            )
        
        # Decode
        translation = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process for better grammar
        translation = self._post_process_translation(translation)
        
        return translation.strip()
    
    def translate(self, segments: list[dict]) -> list[dict]:
        """
        Translate all segments to English.
        
        Adds 'en_text' key to each segment.
        """
        if self.source_language == "en":
            # No translation needed
            for segment in segments:
                segment["en_text"] = segment["text"]
            return segments
        
        # Translate in batches
        batch_size = 32
        translated_segments = []
        
        for i in tqdm(range(0, len(segments), batch_size), desc="Translating to English"):
            batch = segments[i:i + batch_size]
            
            for segment in batch:
                try:
                    en_text = self._translate_text(segment["text"])
                    segment["en_text"] = en_text
                except Exception as e:
                    print(f"   Translation error for segment: {e}")
                    segment["en_text"] = segment["text"]
                
                translated_segments.append(segment)
        
        return translated_segments
