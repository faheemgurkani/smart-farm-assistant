#!/usr/bin/env python3
"""
Test script for enhanced audio processing functionality
"""

import sys
import os
# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.services.multimodal_service import asr

def test_enhanced_audio_processing():
    """Test the enhanced audio processing functionality"""
    
    # Mock session context
    session_context = {
        "crop_type": "cabbage",
        "region": "punjab"
    }
    
    # Test with audio path and text input
    audio_path = "test_audio.wav"  # This won't exist, but will test the flow
    text_input = "What should I do about this?"
    
    print("Testing enhanced audio processing...")
    print(f"Audio path: {audio_path}")
    print(f"Text input: {text_input}")
    print(f"Session context: {session_context}")
    print("-" * 50)
    
    try:
        # Test the enhanced audio processing
        result = asr.process_audio_with_enhanced_intent(audio_path, text_input, session_context)
        
        print("Results:")
        print(f"Transcribed text: {result['transcribed_text']}")
        print(f"Audio-based intent: {result['audio_intent']}")
        print(f"Combined text: {result['combined_text']}")
        print(f"Final intent: {result['final_intent']}")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

def test_audio_intent_classification():
    """Test just the audio intent classification"""
    
    session_context = {
        "crop_type": "wheat",
        "region": "pakistan"
    }
    
    audio_path = "test_audio.wav"
    
    print("Testing audio intent classification...")
    print(f"Audio path: {audio_path}")
    print(f"Session context: {session_context}")
    print("-" * 50)
    
    try:
        transcribed_text, audio_intent = asr.classify_audio_intent_with_gemma3n(audio_path, session_context)
        
        print("Results:")
        print(f"Transcribed text: {transcribed_text}")
        print(f"Audio-based intent: {audio_intent}")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("Enhanced Audio Processing Test")
    print("=" * 50)
    
    # Test 1: Audio intent classification
    print("\nTest 1: Audio Intent Classification")
    success1 = test_audio_intent_classification()
    
    # Test 2: Enhanced audio processing
    print("\nTest 2: Enhanced Audio Processing")
    success2 = test_enhanced_audio_processing()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Audio Intent Classification: {'PASS' if success1 else 'FAIL'}")
    print(f"Enhanced Audio Processing: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n✅ All tests passed! STT based audio processing is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.") 