"""Fetch or generate podcast transcripts."""
import requests
import os
import tempfile
from typing import Optional, Dict
from pathlib import Path
from openai import OpenAI


class TranscriptFetcher:
    """Handles fetching existing transcripts or generating new ones."""

    def __init__(self):
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _try_fetch_existing_transcript(self, episode: Dict) -> Optional[str]:
        """
        Attempt to fetch existing transcript from common sources.

        This checks:
        1. Episode description for transcript links
        2. Common transcript hosting services
        """
        # Check episode description for transcript URLs
        description = episode.get('description', '')

        # Look for common transcript indicators
        transcript_keywords = ['transcript', 'show notes', 'full text']

        # Simple heuristic: if description is very long, it might be the transcript
        if len(description) > 2000:
            # Strip HTML tags
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(description, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)

            if len(text) > 2000:
                return text

        # TODO: Could add more sophisticated transcript discovery:
        # - Check podcast website
        # - Use podcast-specific APIs (e.g., Spotify, Apple Podcasts)
        # - Check transcript services like Otter.ai, Rev.com

        return None

    def _transcribe_with_whisper(self, audio_url: str) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API."""
        if not self.openai_client:
            print("OpenAI API key not configured, skipping transcription")
            return None

        try:
            print(f"Downloading audio from {audio_url}...")

            # Download audio file
            response = requests.get(audio_url, stream=True, timeout=300)
            response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            try:
                print("Transcribing audio with Whisper...")
                with open(tmp_path, 'rb') as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                return transcript
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    def get_transcript(self, episode: Dict) -> Optional[str]:
        """
        Get transcript for an episode, trying existing sources first.

        Args:
            episode: Episode metadata dictionary

        Returns:
            Transcript text or None if unavailable
        """
        # Try to fetch existing transcript first
        print(f"Looking for existing transcript for: {episode['episode_title']}")
        transcript = self._try_fetch_existing_transcript(episode)

        if transcript:
            print("Found existing transcript!")
            return transcript

        # Fall back to Whisper transcription if audio URL available
        if episode.get('audio_url'):
            print("No existing transcript found, transcribing with Whisper...")
            return self._transcribe_with_whisper(episode['audio_url'])
        else:
            print("No audio URL available for transcription")
            return None

    def get_transcript_from_description(self, episode: Dict) -> str:
        """
        Extract usable content from episode description.
        Used as fallback when no full transcript is available.
        """
        description = episode.get('description', '')
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(description, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
