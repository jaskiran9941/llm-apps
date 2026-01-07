"""
Text-to-Speech service using ElevenLabs API
"""
import os
from elevenlabs import generate, set_api_key


async def text_to_speech(text: str, output_path: str) -> str:
    """
    Convert text to speech using ElevenLabs API

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file

    Returns:
        Path to the generated audio file
    """
    try:
        # Set API key
        set_api_key(os.getenv("ELEVENLABS_API_KEY"))

        # Generate audio using ElevenLabs
        # Using Adam voice - you can change to any voice from your account
        audio = generate(
            text=text,
            voice="pNInz6obpgDQGcFmaJgB",  # Adam - Dominant, Firm
            model="eleven_multilingual_v2"
        )

        # Save audio to file
        with open(output_path, "wb") as f:
            f.write(audio)

        return output_path

    except Exception as e:
        raise Exception(f"TTS Error: {str(e)}")
