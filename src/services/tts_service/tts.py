import os
import tempfile
import io
import wave
import numpy as np
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from TTS.api import TTS
    from TTS.utils.manage import ModelManager
    COQUI_AVAILABLE = True
except ImportError:
    logger.warning("Coqui TTS not available, falling back to pyttsx3")
    COQUI_AVAILABLE = False
    import pyttsx3

class EnhancedTTS:
    """Enhanced TTS service using Coqui TTS with fallback to pyttsx3"""
    
    def __init__(self):
        self.tts_model = None
        self.fallback_engine = None
        self.current_language = 'en'
        
        # Language to model mappings for Coqui TTS
        self.language_models = {
            'en': 'tts_models/en/ljspeech/fast_pitch',
            'es': 'tts_models/es/css10/vits',
            'fr': 'tts_models/fr/css10/vits',
            'de': 'tts_models/de/css10/vits',
            'it': 'tts_models/it/css10/vits',
            'pt': 'tts_models/pt/css10/vits',
            'ru': 'tts_models/ru/css10/vits',
            'zh': 'tts_models/zh-CN/baker/tacotron2-DDC',
            'ja': 'tts_models/ja/css10/vits',
            'ko': 'tts_models/ko/css10/vits',
            'ar': 'tts_models/ar/css10/vits',
            'hi': 'tts_models/hi/css10/vits',
            'ur': 'tts_models/ur/css10/vits',
            'bn': 'tts_models/bn/css10/vits',
            'pa': 'tts_models/pa/css10/vits'
        }
        
        self.initialize_tts()
    
    def initialize_tts(self):
        """Initialize the TTS model"""
        if COQUI_AVAILABLE:
            try:
                # Use a smaller, faster model for quicker startup
                self.tts_model = TTS(model_name=self.language_models['en'], 
                                    progress_bar=False)
                logger.info("Coqui TTS initialized successfully with English model")
            except Exception as e:
                logger.error(f"Failed to initialize Coqui TTS: {e}")
                self.tts_model = None
        else:
            # Fallback to pyttsx3
            try:
                self.fallback_engine = pyttsx3.init()
                # Configure pyttsx3 for better quality
                self.fallback_engine.setProperty('rate', 150)  # Speed of speech
                self.fallback_engine.setProperty('volume', 0.9)  # Volume level
                logger.info("pyttsx3 fallback initialized")
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the language for TTS output
        
        Args:
            language_code: ISO language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            True if language was set successfully, False otherwise
        """
        if not COQUI_AVAILABLE or not self.tts_model:
            logger.warning("Cannot set language: Coqui TTS not available")
            return False
        
        # Check if language is supported
        if language_code not in self.language_models:
            logger.warning(f"Language {language_code} not supported, using English")
            language_code = 'en'
        
        # Only change model if language is different
        if language_code != self.current_language:
            try:
                model_name = self.language_models[language_code]
                self.tts_model = TTS(model_name=model_name, progress_bar=False)
                self.current_language = language_code
                logger.info(f"TTS language changed to {language_code} using model: {model_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to change TTS language to {language_code}: {e}")
                # Fallback to English
                try:
                    self.tts_model = TTS(model_name=self.language_models['en'], progress_bar=False)
                    self.current_language = 'en'
                    logger.info("Fell back to English TTS model")
                    return False
                except Exception as fallback_e:
                    logger.error(f"Failed to fallback to English TTS: {fallback_e}")
                    return False
        
        return True
    
    def speak(self, text: str, output_format: str = "wav", language_code: str = None) -> bytes:
        """
        Convert text to speech and return audio bytes
        
        Args:
            text: Text to convert to speech
            output_format: Output format ('wav' or 'mp3')
            language_code: ISO language code for TTS (e.g., 'en', 'es', 'fr')
            
        Returns:
            Audio bytes in the specified format
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return b""
        
        # Set language if specified
        if language_code:
            self.set_language(language_code)
        
        # Preprocess text to handle very short inputs
        processed_text = self._preprocess_text(text)
        
        try:
            if COQUI_AVAILABLE and self.tts_model:
                return self._speak_with_coqui(processed_text, output_format)
            elif self.fallback_engine:
                return self._speak_with_pyttsx3(processed_text, output_format)
            else:
                logger.error("No TTS engine available")
                return b""
        except Exception as e:
            logger.error(f"TTS conversion failed: {e}")
            return b""
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text to handle TTS model requirements"""
        # Remove any problematic characters that might cause TTS issues
        import re
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Ensure minimum length for TTS models
        if len(text.strip()) < 10:
            # Add padding for very short texts
            text = f"Here is the response: {text}"
        
        # Limit maximum length to prevent memory issues and large audio files
        if len(text) > 1000:  # Reduced from 2000 to prevent large audio files
            text = text[:1000] + "..."
        
        return text.strip()
    
    def _speak_with_coqui(self, text: str, output_format: str) -> bytes:
        """Convert text to speech using Coqui TTS"""
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as temp_file:
                temp_path = temp_file.name
            
            # Generate speech using Coqui TTS
            self.tts_model.tts_to_file(text=text, file_path=temp_path)
            
            # Read the generated audio file
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Check audio size and warn if too large
            audio_size_mb = len(audio_bytes) / (1024 * 1024)
            if audio_size_mb > 5:  # Warn if larger than 5MB
                logger.warning(f"Generated audio is {audio_size_mb:.2f}MB - this may cause gRPC issues")
            
            logger.info(f"Coqui TTS generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}")
            # Try with fallback text if kernel size error
            if "kernel size" in str(e).lower() or "input size" in str(e).lower():
                logger.info("Attempting fallback with longer text for kernel size error")
                fallback_text = f"Here is the detailed response: {text}. This should provide sufficient length for the TTS model."
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as temp_file:
                        temp_path = temp_file.name
                    
                    self.tts_model.tts_to_file(text=fallback_text, file_path=temp_path)
                    
                    with open(temp_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    os.unlink(temp_path)
                    logger.info(f"Coqui TTS fallback generated {len(audio_bytes)} bytes of audio")
                    return audio_bytes
                except Exception as fallback_e:
                    logger.error(f"Coqui TTS fallback also failed: {fallback_e}")
            
            # Fallback to pyttsx3 if available
            if self.fallback_engine:
                logger.info("Falling back to pyttsx3")
                return self._speak_with_pyttsx3(text, output_format)
            return b""
    
    def _speak_with_pyttsx3(self, text: str, output_format: str) -> bytes:
        """Convert text to speech using pyttsx3 fallback"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as temp_file:
                temp_path = temp_file.name
            
            # Generate speech using pyttsx3
            self.fallback_engine.save_to_file(text, temp_path)
            self.fallback_engine.runAndWait()
            
            # Read the generated audio file
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            # Check audio size and warn if too large
            audio_size_mb = len(audio_bytes) / (1024 * 1024)
            if audio_size_mb > 5:  # Warn if larger than 5MB
                logger.warning(f"Generated audio is {audio_size_mb:.2f}MB - this may cause gRPC issues")
            
            logger.info(f"pyttsx3 generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"pyttsx3 failed: {e}")
            return b""
    
    def get_available_models(self) -> list:
        """Get list of available TTS models"""
        if COQUI_AVAILABLE:
            try:
                manager = ModelManager()
                return manager.list_models()
            except Exception as e:
                logger.error(f"Failed to get available models: {e}")
                return []
        return []
    
    def change_model(self, model_name: str) -> bool:
        """Change the TTS model"""
        if COQUI_AVAILABLE:
            try:
                self.tts_model = TTS(model_name=model_name, progress_bar=False)
                logger.info(f"Changed TTS model to: {model_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to change model to {model_name}: {e}")
                return False
        return False

# Initialize the enhanced TTS service
enhanced_tts = EnhancedTTS()

def speak(text: str, output_format: str = "wav", language_code: str = None) -> bytes:
    """
    Main function to convert text to speech
    
    Args:
        text: Text to convert to speech
        output_format: Output format ('wav' or 'mp3')
        language_code: ISO language code for TTS (e.g., 'en', 'es', 'fr')
        
    Returns:
        Audio bytes in the specified format
    """
    return enhanced_tts.speak(text, output_format, language_code)

def get_tts_status() -> dict:
    """Get TTS service status and information"""
    return {
        "coqui_available": COQUI_AVAILABLE,
        "model_loaded": enhanced_tts.tts_model is not None,
        "fallback_available": enhanced_tts.fallback_engine is not None,
        "available_models": enhanced_tts.get_available_models() if COQUI_AVAILABLE else []
    }
