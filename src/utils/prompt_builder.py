def build_prompt(text, image_context, audio_context, context=None, language_info=None):
    """
    Build a prompt for the LLM, optionally injecting session context fields and language information.
    
    Args:
        text: Input text
        image_context: Image analysis context
        audio_context: Audio transcription context
        context: Session context dictionary
        language_info: Language detection information dictionary
    """
    parts = []
    
    # Add language instruction if language is detected
    if language_info and language_info.get('language_code') != 'en':
        language_name = language_info.get('language_name', 'the detected language')
        parts.append(f"IMPORTANT: Please respond in {language_name}. The user is speaking in {language_name}.")
    
    # Add context block if present
    if context:
        ctx_block = "\n".join(f"{k}: {v}" for k, v in context.items())
        if ctx_block:
            parts.append(f"Context:\n{ctx_block}")
    
    if text:
        parts.append(f"Text: {text}")
    if image_context:
        parts.append(f"Image Analysis: {image_context}")
    if audio_context:
        parts.append(f"Voice Transcription: {audio_context}")
    
    return "\n".join(parts)
