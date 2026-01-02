"""AI-powered podcast summarization using OpenAI GPT."""
import os
from typing import Dict, List, Optional
from openai import OpenAI
import httpx


class PodcastSummarizer:
    """Generates summaries and insights from podcast transcripts."""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Create HTTP client that bypasses SSL verification for corporate proxies
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(api_key=api_key, http_client=http_client)
        self.summary_length = os.getenv('SUMMARY_LENGTH', 'medium')

    def _get_summary_instructions(self) -> str:
        """Get summary length instructions based on settings."""
        length_map = {
            'short': '2-3 concise bullet points',
            'medium': '5-7 detailed bullet points',
            'long': '10-15 comprehensive bullet points with sub-points'
        }
        return length_map.get(self.summary_length, length_map['medium'])

    def summarize_episode(self, episode: Dict, transcript: str) -> Dict:
        """
        Generate a comprehensive summary of a podcast episode.

        Args:
            episode: Episode metadata
            transcript: Full transcript or description text

        Returns:
            Dictionary with summary, key points, and action items
        """
        prompt = f"""You are analyzing a podcast episode. Please provide a structured summary.

Podcast: {episode['podcast_name']}
Episode: {episode['episode_title']}
Published: {episode.get('published_date', 'Unknown')}

Transcript/Content:
{transcript[:50000]}  # Limit to avoid token limits

Please provide:
1. A brief overview (2-3 sentences)
2. Key points and insights ({self._get_summary_instructions()})
3. Notable quotes or highlights (if any)
4. Action items or takeaways (if applicable)
5. Main topics covered (as tags)

Format your response as follows:
## Overview
[Your overview here]

## Key Points
- [Point 1]
- [Point 2]
...

## Highlights
- [Quote or highlight 1]
- [Quote or highlight 2]

## Takeaways
- [Actionable item 1]
- [Actionable item 2]

## Topics
[comma-separated list of topics]
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )

            summary_text = response.choices[0].message.content

            # Parse the structured response
            return {
                'summary_text': summary_text,
                'podcast_name': episode['podcast_name'],
                'episode_title': episode['episode_title'],
                'episode_url': episode['episode_url'],
                'published_date': episode.get('published_date'),
                'duration': episode.get('duration')
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error generating summary: {e}")
            print(error_details)
            return {
                'summary_text': f"Error generating summary: {str(e)}\n\nDetails: {error_details[:500]}",
                'podcast_name': episode['podcast_name'],
                'episode_title': episode['episode_title'],
                'episode_url': episode['episode_url'],
                'published_date': episode.get('published_date'),
                'duration': episode.get('duration')
            }

    def generate_recommendations(self, current_podcasts: List[str], tags: List[str]) -> List[Dict]:
        """
        Generate podcast recommendations based on current subscriptions and interests.

        Args:
            current_podcasts: List of currently subscribed podcast names
            tags: List of interest tags

        Returns:
            List of recommended podcasts with descriptions
        """
        prompt = f"""Based on someone who listens to these podcasts:
{', '.join(current_podcasts)}

And is interested in these topics:
{', '.join(tags)}

Please recommend 5 similar podcasts they might enjoy. For each recommendation, provide:
1. Podcast name
2. Brief description (1-2 sentences)
3. Why it's a good fit
4. Key topics covered

Format each recommendation as:
### [Podcast Name]
**Description:** [Brief description]
**Why you'll like it:** [Reasoning]
**Topics:** [Comma-separated topics]
**RSS Feed:** [If you know it, otherwise say "Search for it"]

---
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )

            recommendations_text = response.choices[0].message.content

            return {
                'recommendations_text': recommendations_text,
                'count': 5
            }

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return {
                'recommendations_text': f"Error generating recommendations: {str(e)}",
                'count': 0
            }

    def summarize_multiple_episodes(self, summaries: List[Dict]) -> str:
        """
        Create a unified daily digest from multiple episode summaries.

        Args:
            summaries: List of episode summary dictionaries

        Returns:
            Formatted daily digest text
        """
        if not summaries:
            return "No new podcast episodes today."

        digest_parts = [
            "# 🎧 Your Daily Podcast Digest\n",
            f"*{len(summaries)} new episode{'s' if len(summaries) > 1 else ''} today*\n\n"
        ]

        for i, summary in enumerate(summaries, 1):
            digest_parts.append(f"## {i}. {summary['podcast_name']}: {summary['episode_title']}\n")

            if summary.get('published_date'):
                digest_parts.append(f"📅 {summary['published_date']} | ⏱️ {summary.get('duration', 'Unknown duration')}\n")

            if summary.get('episode_url'):
                digest_parts.append(f"🔗 [Listen here]({summary['episode_url']})\n\n")

            digest_parts.append(f"{summary['summary_text']}\n\n")
            digest_parts.append("---\n\n")

        return ''.join(digest_parts)
