"""
Audio processing utilities: topic detection, summarization, entity extraction.
"""

from openai import OpenAI
from typing import List, Dict, Any
import logging

from ..common.models import AudioInfo, AudioSegment
from ..common.config import Config
from ..common.utils import count_tokens

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Process audio transcripts for enhanced search."""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.chat_model = Config.CHAT_MODEL

    def detect_topics(self, transcript: str, max_topics: int = 5) -> List[str]:
        """
        Extract key topics from transcript using GPT-4.

        Args:
            transcript: Full transcript text
            max_topics: Maximum number of topics to extract

        Returns:
            List of topic strings
        """
        prompt = f"""Analyze this audio transcript and extract the {max_topics} most important topics discussed.
Return ONLY a comma-separated list of topics (e.g., "revenue growth, Q3 results, market expansion").

Transcript:
{transcript[:3000]}  # Limit to first 3000 chars

Topics:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You extract key topics from transcripts concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )

            topics_str = response.choices[0].message.content.strip()
            topics = [t.strip() for t in topics_str.split(',')]
            logger.info(f"Detected {len(topics)} topics")
            return topics[:max_topics]

        except Exception as e:
            logger.error(f"Error detecting topics: {e}")
            return []

    def summarize_transcript(self, audio_info: AudioInfo) -> str:
        """
        Generate executive summary of audio content.

        Args:
            audio_info: AudioInfo object

        Returns:
            Summary text
        """
        prompt = f"""Provide a concise executive summary (3-4 sentences) of this audio transcript.
Focus on key points, decisions, and action items.

Transcript ({audio_info.duration:.0f} seconds, {audio_info.language}):
{audio_info.transcript[:4000]}  # Limit context

Summary:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You summarize audio transcripts concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary: {len(summary)} chars")
            return summary

        except Exception as e:
            logger.error(f"Error summarizing transcript: {e}")
            return ""

    def extract_entities(self, transcript: str) -> Dict[str, List[str]]:
        """
        Extract named entities from transcript.

        Args:
            transcript: Transcript text

        Returns:
            Dictionary of entity types to entity lists
        """
        prompt = f"""Extract key entities from this transcript in these categories:
- People: Names of people mentioned
- Companies: Organizations or company names
- Products: Product or service names
- Locations: Places, cities, countries
- Dates: Specific dates or time periods mentioned

Return as JSON format with keys: people, companies, products, locations, dates
Each value should be a list of strings.

Transcript:
{transcript[:3000]}

JSON:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You extract entities from text and return JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            import json
            entities = json.loads(response.choices[0].message.content)
            logger.info(f"Extracted entities: {sum(len(v) for v in entities.values())} total")
            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                "people": [],
                "companies": [],
                "products": [],
                "locations": [],
                "dates": []
            }

    def enrich_audio_info(self, audio_info: AudioInfo) -> AudioInfo:
        """
        Enrich AudioInfo with topics, summary, and entities.

        Args:
            audio_info: AudioInfo object

        Returns:
            Enriched AudioInfo object
        """
        logger.info(f"Enriching audio {audio_info.audio_id}...")

        # Detect topics
        if not audio_info.topics:
            audio_info.topics = self.detect_topics(audio_info.transcript)

        # Generate summary
        if not audio_info.summary:
            audio_info.summary = self.summarize_transcript(audio_info)

        # Extract entities
        if not audio_info.entities:
            audio_info.entities = self.extract_entities(audio_info.transcript)

        logger.info(f"Enrichment complete for {audio_info.audio_id}")
        return audio_info

    def chunk_segments(
        self,
        audio_info: AudioInfo,
        target_duration: float = None
    ) -> List[AudioSegment]:
        """
        Combine or split segments to target duration.

        Args:
            audio_info: AudioInfo object
            target_duration: Target duration per chunk in seconds

        Returns:
            List of re-chunked segments
        """
        if target_duration is None:
            target_duration = Config.AUDIO_SEGMENT_DURATION_SECONDS

        if not audio_info.segments:
            return []

        chunked_segments = []
        current_chunk_text = []
        current_start = audio_info.segments[0].start_time
        current_duration = 0.0

        for segment in audio_info.segments:
            segment_duration = segment.end_time - segment.start_time
            current_duration += segment_duration
            current_chunk_text.append(segment.text)

            # Check if we've reached target duration
            if current_duration >= target_duration:
                # Create combined segment
                combined_segment = AudioSegment(
                    segment_id=generate_id(f"{audio_info.audio_id}_{len(chunked_segments)}", prefix="seg"),
                    start_time=current_start,
                    end_time=segment.end_time,
                    text=" ".join(current_chunk_text).strip(),
                    confidence=None
                )
                chunked_segments.append(combined_segment)

                # Reset for next chunk
                current_chunk_text = []
                current_start = segment.end_time
                current_duration = 0.0

        # Add remaining text as final segment
        if current_chunk_text:
            combined_segment = AudioSegment(
                segment_id=generate_id(f"{audio_info.audio_id}_{len(chunked_segments)}", prefix="seg"),
                start_time=current_start,
                end_time=audio_info.segments[-1].end_time,
                text=" ".join(current_chunk_text).strip(),
                confidence=None
            )
            chunked_segments.append(combined_segment)

        logger.info(f"Re-chunked {len(audio_info.segments)} segments into {len(chunked_segments)} chunks")
        return chunked_segments


# Import at end to avoid circular import
from ..common.utils import generate_id
