"""
Audio transcription using OpenAI Whisper API.
"""

from openai import OpenAI
from pathlib import Path
from typing import List, Dict, Any
import logging
from pydub import AudioSegment
import tempfile
import os

from ..common.models import AudioInfo, AudioSegment as AudioSegmentModel
from ..common.config import Config
from ..common.utils import generate_id, validate_file_size, format_timestamp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extract transcripts from audio files using Whisper API."""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.WHISPER_MODEL
        self.max_file_size_mb = Config.MAX_AUDIO_FILE_SIZE_MB
        self.chunk_duration = Config.AUDIO_CHUNK_DURATION_SECONDS

    def transcribe(self, audio_path: Path) -> AudioInfo:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioInfo object with transcript and segments
        """
        # Validate file size
        if not validate_file_size(audio_path, self.max_file_size_mb):
            logger.info(f"Audio file exceeds {self.max_file_size_mb}MB, splitting...")
            return self._transcribe_large_file(audio_path)
        else:
            return self._transcribe_file(audio_path)

    def _transcribe_file(self, audio_path: Path) -> AudioInfo:
        """
        Transcribe a single audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioInfo object
        """
        try:
            with open(audio_path, "rb") as audio_file:
                # Call Whisper API with verbose response
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )

            # Extract information
            full_transcript = response.text
            language = response.language
            duration = response.duration if hasattr(response, 'duration') else 0.0

            # Process segments
            segments = []
            if hasattr(response, 'segments') and response.segments:
                for idx, segment in enumerate(response.segments):
                    # Handle both dict and object responses from OpenAI API
                    if isinstance(segment, dict):
                        start = segment.get('start', 0.0)
                        end = segment.get('end', 0.0)
                        text = segment.get('text', '').strip()
                        confidence = segment.get('avg_logprob', None)
                    else:
                        # Object with attributes
                        start = getattr(segment, 'start', 0.0)
                        end = getattr(segment, 'end', 0.0)
                        text = getattr(segment, 'text', '').strip()
                        confidence = getattr(segment, 'avg_logprob', None)

                    segment_model = AudioSegmentModel(
                        segment_id=generate_id(f"{audio_path.name}_{idx}", prefix="seg"),
                        start_time=start,
                        end_time=end,
                        text=text,
                        confidence=confidence
                    )
                    segments.append(segment_model)
            else:
                # Fallback: create single segment
                segments.append(AudioSegmentModel(
                    segment_id=generate_id(f"{audio_path.name}_0", prefix="seg"),
                    start_time=0.0,
                    end_time=duration,
                    text=full_transcript,
                    confidence=None
                ))

            # Create AudioInfo
            audio_info = AudioInfo(
                audio_id=generate_id(audio_path.name, prefix="audio"),
                audio_path=str(audio_path),
                duration=duration,
                transcript=full_transcript,
                segments=segments,
                language=language,
                metadata={
                    "filename": audio_path.name,
                    "file_size_mb": audio_path.stat().st_size / (1024 * 1024)
                }
            )

            logger.info(f"Transcribed {audio_path.name}: {duration:.1f}s, {len(segments)} segments")
            return audio_info

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    def _transcribe_large_file(self, audio_path: Path) -> AudioInfo:
        """
        Transcribe large audio file by splitting into chunks.

        Args:
            audio_path: Path to large audio file

        Returns:
            AudioInfo object with combined transcripts
        """
        # Split audio into chunks
        chunk_paths = self.split_large_audio(audio_path)

        all_segments = []
        full_transcript_parts = []
        total_duration = 0.0
        detected_language = "en"

        try:
            # Transcribe each chunk
            for chunk_idx, chunk_path in enumerate(chunk_paths):
                chunk_info = self._transcribe_file(chunk_path)

                # Adjust segment timestamps
                time_offset = chunk_idx * self.chunk_duration
                for segment in chunk_info.segments:
                    segment.start_time += time_offset
                    segment.end_time += time_offset
                    all_segments.append(segment)

                full_transcript_parts.append(chunk_info.transcript)
                total_duration += chunk_info.duration
                detected_language = chunk_info.language

            # Combine results
            audio_info = AudioInfo(
                audio_id=generate_id(audio_path.name, prefix="audio"),
                audio_path=str(audio_path),
                duration=total_duration,
                transcript=" ".join(full_transcript_parts),
                segments=all_segments,
                language=detected_language,
                metadata={
                    "filename": audio_path.name,
                    "file_size_mb": audio_path.stat().st_size / (1024 * 1024),
                    "was_chunked": True,
                    "num_chunks": len(chunk_paths)
                }
            )

            logger.info(f"Transcribed large file {audio_path.name}: {total_duration:.1f}s, {len(all_segments)} segments")
            return audio_info

        finally:
            # Cleanup temporary chunk files
            for chunk_path in chunk_paths:
                try:
                    chunk_path.unlink()
                except:
                    pass

    def split_large_audio(self, audio_path: Path) -> List[Path]:
        """
        Split large audio file into chunks.

        Args:
            audio_path: Path to audio file

        Returns:
            List of paths to temporary chunk files
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            chunk_duration_ms = self.chunk_duration * 1000

            chunk_paths = []
            num_chunks = len(audio) // chunk_duration_ms + 1

            for i in range(num_chunks):
                start_ms = i * chunk_duration_ms
                end_ms = min((i + 1) * chunk_duration_ms, len(audio))

                chunk = audio[start_ms:end_ms]

                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=audio_path.suffix,
                    dir=Config.AUDIO_DIR
                )
                chunk.export(temp_file.name, format=audio_path.suffix.lstrip('.'))
                chunk_paths.append(Path(temp_file.name))

            logger.info(f"Split audio into {len(chunk_paths)} chunks of {self.chunk_duration}s each")
            return chunk_paths

        except Exception as e:
            logger.error(f"Error splitting audio: {e}")
            raise

    def save_transcript(self, audio_info: AudioInfo, output_path: Path = None) -> Path:
        """
        Save transcript to text file.

        Args:
            audio_info: AudioInfo object
            output_path: Optional output path

        Returns:
            Path to saved transcript
        """
        if output_path is None:
            output_path = Config.TRANSCRIPTS_DIR / f"{audio_info.audio_id}_transcript.txt"

        # Format transcript with timestamps
        lines = [f"Transcript: {Path(audio_info.audio_path).name}"]
        lines.append(f"Duration: {format_timestamp(audio_info.duration)}")
        lines.append(f"Language: {audio_info.language}")
        lines.append("-" * 80)
        lines.append("")

        for segment in audio_info.segments:
            timestamp = format_timestamp(segment.start_time)
            lines.append(f"[{timestamp}] {segment.text}")

        output_path.write_text("\n".join(lines))
        logger.info(f"Saved transcript to {output_path}")
        return output_path
