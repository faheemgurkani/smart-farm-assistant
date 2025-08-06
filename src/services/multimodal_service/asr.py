import os
import base64
import requests
from typing import Tuple, Dict, Any

def transcribe(audio_path):
    """Transcribe audio to text using a speech recognition service"""
    # TODO: Implement real STT (Whisper, Google Speech, etc.)
    # For now, return a more realistic placeholder
    if not audio_path or not os.path.exists(audio_path):
        return "No audio file provided."
    
    # Placeholder implementation - in production, use actual STT service
    return "There are holes in the leaves of my cabbage plants."

def classify_audio_intent_with_gemma3n(audio_path: str, session_context: Dict[str, Any]) -> Tuple[str, str]:
    """
    Use Gemma 3n to classify intent directly from audio input.
    
    Args:
        audio_path: Path to the audio file
        session_context: Current session context
        
    Returns:
        Tuple of (transcribed_text, classified_intent)
    """
    # First, transcribe the audio
    transcribed_text = transcribe(audio_path)
    
    # Create a prompt for intent classification from audio
    intent_classification_prompt = f"""You are an agricultural intent classifier. Analyze the user's audio input and classify their intent.

AUDIO TRANSCRIPTION: {transcribed_text}
CURRENT SESSION CONTEXT: {session_context}

INTENT CATEGORIES:
- crop_advice: Questions about planting, growing, crop selection, timing, crop problems, pests affecting crops
- fertilizer: Questions about fertilizers, nutrients, feeding plants, NPK, organic fertilizers
- soil_health: Questions about soil quality, soil problems, soil improvement, soil drying, soil becoming dead
- faq: General questions, how-to, what-is, why questions, general agricultural knowledge

CLASSIFICATION RULES:
- If the user mentions 'soil', 'drying', 'dead soil', 'soil quality' → soil_health
- If the user mentions 'fertilizer', 'nutrients', 'feeding' → fertilizer
- If the user mentions specific crops, planting, growing, pests → crop_advice
- Otherwise → faq

Respond with ONLY the intent label: crop_advice, fertilizer, soil_health, or faq."""
    
    # Call Gemma 3n for intent classification
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3n:e4b",
                "prompt": intent_classification_prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            classified_intent = response.json().get("response", "").strip().lower().split()[0]
            valid_intents = ["crop_advice", "fertilizer", "faq", "soil_health"]
            final_intent = classified_intent if classified_intent in valid_intents else "faq"
            return transcribed_text, final_intent
        else:
            print(f"Error from Ollama: {response.status_code}, {response.text}")
            return transcribed_text, "faq"  # fallback
            
    except Exception as e:
        print(f"Exception while calling Ollama for audio intent classification: {e}")
        return transcribed_text, "faq"  # fallback

def process_audio_with_enhanced_intent(audio_path: str, text_input: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced audio processing that combines audio-based intent classification with text input.
    
    Args:
        audio_path: Path to the audio file
        text_input: Additional text input from user
        session_context: Current session context
        
    Returns:
        Dictionary containing transcribed text, audio-based intent, combined text, and final intent
    """
    print(f"[AUDIO PROCESSING] Starting enhanced audio processing...")
    
    # Step 1: Get audio-based intent classification
    transcribed_text, audio_intent = classify_audio_intent_with_gemma3n(audio_path, session_context)
    print(f"[AUDIO PROCESSING] Audio transcription: '{transcribed_text}'")
    print(f"[AUDIO PROCESSING] Audio-based intent: {audio_intent}")
    
    # Step 2: Combine transcribed text with user text input
    combined_text = transcribed_text
    if text_input and text_input.strip():
        combined_text = f"{transcribed_text} {text_input}".strip()
    print(f"[AUDIO PROCESSING] Combined text: '{combined_text}'")
    
    # Step 3: Get final intent classification from combined text
    final_intent_prompt = f"""You are an agricultural intent classifier. Analyze the combined user input and classify their intent.

COMBINED USER INPUT: {combined_text}
CURRENT SESSION CONTEXT: {session_context}

INTENT CATEGORIES:
- crop_advice: Questions about planting, growing, crop selection, timing, crop problems, pests affecting crops
- fertilizer: Questions about fertilizers, nutrients, feeding plants, NPK, organic fertilizers
- soil_health: Questions about soil quality, soil problems, soil improvement, soil drying, soil becoming dead
- faq: General questions, how-to, what-is, why questions, general agricultural knowledge

CLASSIFICATION RULES:
- If the user mentions 'soil', 'drying', 'dead soil', 'soil quality' → soil_health
- If the user mentions 'fertilizer', 'nutrients', 'feeding' → fertilizer
- If the user mentions specific crops, planting, growing, pests → crop_advice
- Otherwise → faq

Respond with ONLY the intent label: crop_advice, fertilizer, soil_health, or faq."""
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3n:e4b",
                "prompt": final_intent_prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            final_intent = response.json().get("response", "").strip().lower().split()[0]
            valid_intents = ["crop_advice", "fertilizer", "faq", "soil_health"]
            final_intent = final_intent if final_intent in valid_intents else "faq"
        else:
            print(f"Error from Ollama: {response.status_code}, {response.text}")
            final_intent = "faq"  # fallback
            
    except Exception as e:
        print(f"Exception while calling Ollama for final intent classification: {e}")
        final_intent = "faq"  # fallback
    
    print(f"[AUDIO PROCESSING] Final intent: {final_intent}")
    
    return {
        "transcribed_text": transcribed_text,
        "audio_intent": audio_intent,
        "combined_text": combined_text,
        "final_intent": final_intent
    }
