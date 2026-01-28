"""
Audio embedding using segment-level approach.
"""

from openai import OpenAI
from typing import List, Tuple
import logging

from ..common.models import AudioInfo, AudioSegment
from ..common.config import Config
from ..common.utils import count_tokens, format_timestamp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioEmbedder:
    """Generate embeddings for audio segments."""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.EMBEDDING_MODEL

    def enrich_segment_context(
        self,
        segment: AudioSegment,
        audio_info: AudioInfo
    ) -> str:
        """
        Enrich segment text with metadata context.

        Args:
            segment: AudioSegment object
            audio_info: Parent AudioInfo object

        Returns:
            Enriched text for embedding
        """
        timestamp_start = format_timestamp(segment.start_time)
        timestamp_end = format_timestamp(segment.end_time)

        enriched_text = f"""[Audio Transcript - {timestamp_start} to {timestamp_end}]
Source: {Path(audio_info.audio_path).name}
Language: {audio_info.language}
"""

        # Add speaker if available
        if segment.speaker:
            enriched_text += f"Speaker: {segment.speaker}\n"

        # Add topics if available
        if audio_info.topics:
            enriched_text += f"Topics: {', '.join(audio_info.topics)}\n"

        enriched_text += f"\n{segment.text}"

        return enriched_text

    def embed_segment(
        self,
        segment: AudioSegment,
        audio_info: AudioInfo
    ) -> Tuple[List[float], str]:
        """
        Generate embedding for a single audio segment.

        Args:
            segment: AudioSegment object
            audio_info: Parent AudioInfo object

        Returns:
            Tuple of (embedding vector, enriched text)
        """
        # Enrich with context
        enriched_text = self.enrich_segment_context(segment, audio_info)

        # Generate embedding
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=enriched_text
            )

            embedding = response.data[0].embedding
            return embedding, enriched_text

        except Exception as e:
            logger.error(f"Error generating embedding for segment {segment.segment_id}: {e}")
            raise

    def embed_audio(
        self,
        audio_info: AudioInfo
    ) -> List[Tuple[AudioSegment, List[float], str]]:
        """
        Generate embeddings for all segments in audio.

        Args:
            audio_info: AudioInfo object

        Returns:
            List of tuples (AudioSegment, embedding, enriched_text)
        """
        results = []

        for segment in audio_info.segments:
            try:
                embedding, enriched_text = self.embed_segment(segment, audio_info)
                results.append((segment, embedding, enriched_text))
            except Exception as e:
                logger.error(f"Failed to embed segment {segment.segment_id}: {e}")
                continue

        logger.info(f"Successfully embedded {len(results)}/{len(audio_info.segments)} segments")
        return results

    def embed_multiple_audio(
        self,
        audio_infos: List[AudioInfo]
    ) -> List[Tuple[AudioInfo, AudioSegment, List[float], str]]:
        """
        Generate embeddings for multiple audio files.

        Args:
            audio_infos: List of AudioInfo objects

        Returns:
            List of tuples (AudioInfo, AudioSegment, embedding, enriched_text)
        """
        all_results = []

        for audio_info in audio_infos:
            segment_results = self.embed_audio(audio_info)
            for segment, embedding, enriched_text in segment_results:
                all_results.append((audio_info, segment, embedding, enriched_text))

        logger.info(f"Successfully embedded {len(all_results)} total segments from {len(audio_infos)} audio files")
        return all_results

    def estimate_cost(self, audio_infos: List[AudioInfo]) -> dict:
        """
        Estimate the cost of embedding audio.

        Args:
            audio_infos: List of AudioInfo objects

        Returns:
            Dictionary with cost breakdown
        """
        total_transcription_minutes = 0.0
        total_embedding_tokens = 0
        total_segments = 0

        for audio_info in audio_infos:
            # Transcription cost
            total_transcription_minutes += audio_info.duration / 60.0

            # Embedding cost
            for segment in audio_info.segments:
                enriched_text = self.enrich_segment_context(segment, audio_info)
                total_embedding_tokens += count_tokens(enriched_text)
                total_segments += 1

        # Calculate costs
        transcription_cost = total_transcription_minutes * Config.COST_WHISPER_PER_MINUTE
        embedding_cost = (total_embedding_tokens / 1000) * Config.COST_EMBEDDING

        return {
            "transcription_minutes": total_transcription_minutes,
            "embedding_tokens": total_embedding_tokens,
            "transcription_cost": transcription_cost,
            "embedding_cost": embedding_cost,
            "total_cost": transcription_cost + embedding_cost,
            "num_audio_files": len(audio_infos),
            "num_segments": total_segments
        }


# Import at end to avoid circular import
from pathlib import Path
