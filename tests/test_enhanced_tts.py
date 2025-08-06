#!/usr/bin/env python3
"""
Test script for enhanced TTS functionality with Coqui TTS
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.services.tts_service import tts

def test_tts_status():
    """Test TTS service status"""
    print("Testing TTS service status...")
    print("-" * 50)
    
    try:
        status = tts.get_tts_status()
        
        print("TTS Status:")
        print(f"  Coqui TTS Available: {status['coqui_available']}")
        print(f"  Model Loaded: {status['model_loaded']}")
        print(f"  Fallback Available: {status['fallback_available']}")
        print(f"  Available Models: {status['available_models']}")
        
        return True
        
    except Exception as e:
        print(f"Error getting TTS status: {e}")
        return False

def test_tts_conversion():
    """Test text-to-speech conversion"""
    print("\nTesting TTS conversion...")
    print("-" * 50)
    
    test_text = "Hello, this is a test of the enhanced TTS system with Coqui TTS."
    
    try:
        print(f"Converting text: '{test_text}'")
        
        # Test WAV format
        print("Testing WAV format...")
        audio_wav = tts.speak(test_text, "wav")
        print(f"WAV audio generated: {len(audio_wav)} bytes")
        
        # Test MP3 format
        print("Testing MP3 format...")
        audio_mp3 = tts.speak(test_text, "mp3")
        print(f"MP3 audio generated: {len(audio_mp3)} bytes")
        
        if audio_wav and audio_mp3:
            print("✅ TTS conversion successful!")
            return True
        else:
            print("❌ TTS conversion failed!")
            return False
            
    except Exception as e:
        print(f"Error during TTS conversion: {e}")
        return False

def test_agricultural_tts():
    """Test TTS with agricultural content"""
    print("\nTesting agricultural TTS...")
    print("-" * 50)
    
    agricultural_text = """
    Based on your description of holes in cabbage leaves, this appears to be 
    cabbage white butterfly damage. The larvae feed on the leaves, creating 
    irregular holes. I recommend using row covers to prevent egg laying and 
    applying Bacillus thuringiensis for organic control.
    """
    
    try:
        print("Converting agricultural advice to speech...")
        audio = tts.speak(agricultural_text, "wav")
        
        if audio:
            print(f"✅ Agricultural TTS successful: {len(audio)} bytes")
            return True
        else:
            print("❌ Agricultural TTS failed!")
            return False
            
    except Exception as e:
        print(f"Error during agricultural TTS: {e}")
        return False

def test_empty_text():
    """Test TTS with empty text"""
    print("\nTesting empty text handling...")
    print("-" * 50)
    
    try:
        audio = tts.speak("", "wav")
        
        if not audio:
            print("✅ Empty text handled correctly (no audio generated)")
            return True
        else:
            print("❌ Empty text should not generate audio")
            return False
            
    except Exception as e:
        print(f"Error handling empty text: {e}")
        return False

if __name__ == "__main__":
    print("Enhanced TTS Test Suite")
    print("=" * 50)
    
    # Test 1: TTS Status
    print("\nTest 1: TTS Service Status")
    status_success = test_tts_status()
    
    # Test 2: Basic TTS Conversion
    print("\nTest 2: Basic TTS Conversion")
    conversion_success = test_tts_conversion()
    
    # Test 3: Agricultural TTS
    print("\nTest 3: Agricultural TTS")
    agricultural_success = test_agricultural_tts()
    
    # Test 4: Empty Text Handling
    print("\nTest 4: Empty Text Handling")
    empty_success = test_empty_text()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"TTS Status: {'PASS' if status_success else 'FAIL'}")
    print(f"Basic Conversion: {'PASS' if conversion_success else 'FAIL'}")
    print(f"Agricultural TTS: {'PASS' if agricultural_success else 'FAIL'}")
    print(f"Empty Text Handling: {'PASS' if empty_success else 'FAIL'}")
    
    all_passed = status_success and conversion_success and agricultural_success and empty_success
    
    if all_passed:
        print("\n✅ All tests passed! Enhanced TTS is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\nNote: If Coqui TTS is not available, the system will fall back to pyttsx3.") 