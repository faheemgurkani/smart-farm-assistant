def build_prompt(text, image_context, audio_context):
    parts = []
    if text:
        parts.append(f"Text: {text}")
    if image_context:
        parts.append(f"Image Analysis: {image_context}")
    if audio_context:
        parts.append(f"Voice Transcription: {audio_context}")
    return "\n".join(parts)
