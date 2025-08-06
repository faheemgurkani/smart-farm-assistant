import os
import logging
from typing import Optional, Dict, List
from langdetect import detect, DetectorFactory
import whisper

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageDetectionService:
    """
    Language detection service for both text and audio inputs.
    Provides fallback mechanisms and language validation.
    """
    
    def __init__(self):
        # Supported languages with their ISO codes
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'ur': 'Urdu',
            'bn': 'Bengali',
            'pa': 'Punjabi'
        }
        
        # Fallback language (English)
        self.fallback_language = 'en'
        
        # Initialize Whisper model for audio language detection
        self.whisper_model = None
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model for audio language detection"""
        try:
            logger.info("Loading Whisper model for audio language detection...")
            self.whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def detect_text_language(self, text: str) -> Dict[str, str]:
        """
        Detect language from text input.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with 'language_code', 'language_name', and 'confidence'
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for language detection")
                return self._get_fallback_result()
            
            # Detect language
            detected_lang = detect(text.strip())
            
            # Validate if detected language is supported
            if detected_lang in self.supported_languages:
                language_name = self.supported_languages[detected_lang]
                logger.info(f"Detected language: {language_name} ({detected_lang})")
                return {
                    'language_code': detected_lang,
                    'language_name': language_name,
                    'confidence': 'high',
                    'method': 'text_detection'
                }
            else:
                logger.warning(f"Detected language '{detected_lang}' not in supported list, using fallback")
                return self._get_fallback_result()
                
        except Exception as e:
            logger.error(f"Text language detection failed: {e}")
            return self._get_fallback_result()
    
    def detect_audio_language(self, audio_path: str) -> Dict[str, str]:
        """
        Detect language from audio input using Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dict with 'language_code', 'language_name', and 'confidence'
        """
        try:
            if not audio_path or not os.path.exists(audio_path):
                logger.warning(f"Audio file not found: {audio_path}")
                return self._get_fallback_result()
            
            if self.whisper_model is None:
                logger.warning("Whisper model not available, using fallback")
                return self._get_fallback_result()
            
            # Use Whisper to detect language
            result = self.whisper_model.detect_language(audio_path)
            detected_lang = result['language']
            
            # Validate if detected language is supported
            if detected_lang in self.supported_languages:
                language_name = self.supported_languages[detected_lang]
                logger.info(f"Audio language detected: {language_name} ({detected_lang})")
                return {
                    'language_code': detected_lang,
                    'language_name': language_name,
                    'confidence': 'high',
                    'method': 'audio_detection'
                }
            else:
                logger.warning(f"Detected audio language '{detected_lang}' not in supported list, using fallback")
                return self._get_fallback_result()
                
        except Exception as e:
            logger.error(f"Audio language detection failed: {e}")
            return self._get_fallback_result()
    
    def _get_fallback_result(self) -> Dict[str, str]:
        """Get fallback language result (English)"""
        return {
            'language_code': self.fallback_language,
            'language_name': self.supported_languages[self.fallback_language],
            'confidence': 'low',
            'method': 'fallback'
        }
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language code is supported"""
        return language_code in self.supported_languages
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        return self.supported_languages.copy()
    
    def get_language_name(self, language_code: str) -> Optional[str]:
        """Get language name from language code"""
        return self.supported_languages.get(language_code)

# Global instance
language_detector = LanguageDetectionService() 