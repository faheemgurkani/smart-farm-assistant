#!/usr/bin/env python3
"""
Test script for language detection functionality
"""

import sys
import os
# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the language detection service
from src.services.language_detection import language_detector

def test_text_language_detection():
    """Test text language detection"""
    print("=== Testing Text Language Detection ===")
    
    test_cases = [
        ("Hello, how are you?", "English"),
        ("Hola, ¿cómo estás?", "Spanish"),
        ("Bonjour, comment allez-vous?", "French"),
        ("Guten Tag, wie geht es Ihnen?", "German"),
        ("Ciao, come stai?", "Italian"),
        ("Olá, como você está?", "Portuguese"),
        ("Привет, как дела?", "Russian"),
        ("你好，你好吗？", "Chinese"),
        ("こんにちは、お元気ですか？", "Japanese"),
        ("안녕하세요, 어떻게 지내세요?", "Korean"),
        ("مرحبا، كيف حالك؟", "Arabic"),
        ("नमस्ते, आप कैसे हैं?", "Hindi"),
        ("ہیلو، آپ کیسے ہیں؟", "Urdu"),
        ("হ্যালো, আপনি কেমন আছেন?", "Bengali"),
        ("ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?", "Punjabi")
    ]
    
    for text, expected_language in test_cases:
        result = language_detector.detect_text_language(text)
        detected_language = result.get('language_name', 'Unknown')
        confidence = result.get('confidence', 'Unknown')
        method = result.get('method', 'Unknown')
        
        print(f"Text: '{text[:30]}...'")
        print(f"  Expected: {expected_language}")
        print(f"  Detected: {detected_language}")
        print(f"  Confidence: {confidence}")
        print(f"  Method: {method}")
        print()

def test_supported_languages():
    """Test supported languages list"""
    print("=== Testing Supported Languages ===")
    
    supported = language_detector.get_supported_languages()
    print(f"Total supported languages: {len(supported)}")
    
    for code, name in supported.items():
        print(f"  {code}: {name}")
    print()

def test_language_validation():
    """Test language validation"""
    print("=== Testing Language Validation ===")
    
    test_languages = ['en', 'es', 'fr', 'de', 'xx', 'yy']
    
    for lang in test_languages:
        is_supported = language_detector.is_language_supported(lang)
        language_name = language_detector.get_language_name(lang)
        print(f"  {lang}: {'✓' if is_supported else '✗'} ({language_name or 'Not found'})")
    print()

def test_audio_language_detection():
    """Test audio language detection"""
    print("=== Testing Audio Language Detection ===")
    
    # Test with sample audio files (if available)
    test_audio_files = [
        # You can add actual audio file paths here for testing
        # "tests/audio_samples/english_sample.wav",
        # "tests/audio_samples/spanish_sample.wav",
        # "tests/audio_samples/french_sample.wav",
    ]
    
    if test_audio_files:
        for audio_file in test_audio_files:
            if os.path.exists(audio_file):
                result = language_detector.detect_audio_language(audio_file)
                detected_language = result.get('language_name', 'Unknown')
                confidence = result.get('confidence', 'Unknown')
                method = result.get('method', 'Unknown')
                
                print(f"Audio file: {audio_file}")
                print(f"  Detected: {detected_language}")
                print(f"  Confidence: {confidence}")
                print(f"  Method: {method}")
                print()
            else:
                print(f"Audio file not found: {audio_file}")
    else:
        print("  No audio files provided for testing")
        print("  To test audio detection, add audio file paths to test_audio_files list")
        print("  Example: 'tests/audio_samples/english_sample.wav'")
        print()
    
    # Test with non-existent file (should fallback to English)
    print("Testing with non-existent audio file (should fallback to English):")
    result = language_detector.detect_audio_language("non_existent_file.wav")
    detected_language = result.get('language_name', 'Unknown')
    confidence = result.get('confidence', 'Unknown')
    method = result.get('method', 'Unknown')
    
    print(f"  Detected: {detected_language}")
    print(f"  Confidence: {confidence}")
    print(f"  Method: {method}")
    print()

def test_whisper_model_availability():
    """Test if Whisper model is available for audio detection"""
    print("=== Testing Whisper Model Availability ===")
    
    if language_detector.whisper_model is not None:
        print("  ✓ Whisper model is loaded and available for audio detection")
    else:
        print("  ✗ Whisper model is not available")
        print("  This means audio language detection will fallback to English")
    print()

if __name__ == "__main__":
    print("Language Detection Test Suite")
    print("=" * 40)
    print()
    
    test_supported_languages()
    test_language_validation()
    test_text_language_detection()
    test_whisper_model_availability()
    test_audio_language_detection()
    
    print("Test completed!") 