"""
Speech-to-Text service using OpenAI Whisper API
"""
import os
from openai import OpenAI


async def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file to text using Whisper API

    Args:
        audio_file_path: Path to the audio file

    Returns:
        Transcribed text
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    except Exception as e:
        raise Exception(f"STT Error: {str(e)}")
