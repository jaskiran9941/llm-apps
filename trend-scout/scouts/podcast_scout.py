"""Podcast scout using Composio Listen Notes integration."""
import os
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from composio import ComposioToolSet, Action
from rich.console import Console

console = Console()


@dataclass
class PodcastEpisode:
    """Represents a podcast episode."""
    title: str
    podcast_name: str
    description: str
    url: str
    audio_url: str
    published_at: datetime
    duration_minutes: int

    def to_dict(self) -> dict:
        return {
            "source": "podcast",
            "title": self.title,
            "podcast_name": self.podcast_name,
            "description": self.description[:500],
            "url": self.url,
            "audio_url": self.audio_url,
            "published_at": self.published_at.isoformat(),
            "duration_minutes": self.duration_minutes,
        }


class PodcastScout:
    """Scout podcasts for relevant episodes using Listen Notes via Composio."""

    def __init__(self):
        self.toolset = ComposioToolSet()
        self._authenticated = False

    def check_auth(self) -> bool:
        """Check if Listen Notes is authenticated with Composio."""
        try:
            connections = self.toolset.get_connected_accounts()
            for conn in connections:
                if conn.appName.lower() == "listennotes":
                    self._authenticated = True
                    return True
            return False
        except Exception as e:
            console.print(f"[red]Error checking Listen Notes auth: {e}[/red]")
            return False

    def authenticate(self) -> str:
        """Initiate Listen Notes auth via Composio."""
        try:
            connection_request = self.toolset.initiate_connection(
                app="listennotes",
                redirect_url="https://backend.composio.dev/api/v1/auth-apps/add"
            )
            return connection_request.redirectUrl
        except Exception as e:
            console.print(f"[red]Error initiating Listen Notes auth: {e}[/red]")
            return ""

    async def search(
        self,
        query: str,
        limit: int = 10,
        published_after: Optional[datetime] = None,
        sort_by: str = "recent"  # recent, relevance
    ) -> list[PodcastEpisode]:
        """
        Search for podcast episodes matching query.

        Args:
            query: Search query
            limit: Max results
            published_after: Only episodes after this date
            sort_by: 'recent' or 'relevance'
        """
        if not self._authenticated and not self.check_auth():
            console.print("[yellow]Listen Notes not authenticated. Run setup first.[/yellow]")
            return []

        episodes = []

        try:
            params = {
                "q": query,
                "type": "episode",
                "sort_by_date": 1 if sort_by == "recent" else 0,
                "len_min": 5,  # Minimum 5 minutes
                "len_max": 120,  # Max 2 hours
            }

            if published_after:
                params["published_after"] = int(published_after.timestamp() * 1000)

            result = self.toolset.execute_action(
                action=Action.LISTENNOTES_SEARCH,
                params=params
            )

            if result.get("successful") and result.get("data"):
                for item in result["data"].get("results", [])[:limit]:
                    episode = PodcastEpisode(
                        title=item.get("title_original", ""),
                        podcast_name=item.get("podcast", {}).get("title_original", ""),
                        description=item.get("description_original", ""),
                        url=item.get("listennotes_url", ""),
                        audio_url=item.get("audio", ""),
                        published_at=datetime.fromtimestamp(
                            item.get("pub_date_ms", 0) / 1000
                        ),
                        duration_minutes=item.get("audio_length_sec", 0) // 60,
                    )
                    episodes.append(episode)

        except Exception as e:
            console.print(f"[red]Error searching podcasts: {e}[/red]")

        return episodes

    async def get_trending(
        self,
        genre_ids: Optional[list[int]] = None,
        limit: int = 10
    ) -> list[PodcastEpisode]:
        """
        Get trending/best podcast episodes.

        Genre IDs for tech:
        - 127: Technology
        - 131: Tech News
        - 140: Entrepreneurship
        - 173: AI & Data Science
        """
        if not self._authenticated and not self.check_auth():
            return []

        episodes = []

        # Default to tech-related genres
        if genre_ids is None:
            genre_ids = [127, 131, 140]

        try:
            result = self.toolset.execute_action(
                action=Action.LISTENNOTES_GET_BEST_PODCASTS,
                params={
                    "genre_id": genre_ids[0] if genre_ids else 127,
                    "page": 1,
                }
            )

            if result.get("successful") and result.get("data"):
                for podcast in result["data"].get("podcasts", [])[:limit]:
                    # Get latest episode from each trending podcast
                    latest = podcast.get("latest_episode_id")
                    if latest:
                        episode = PodcastEpisode(
                            title=podcast.get("title", ""),
                            podcast_name=podcast.get("title", ""),
                            description=podcast.get("description", ""),
                            url=podcast.get("listennotes_url", ""),
                            audio_url="",
                            published_at=datetime.now(),
                            duration_minutes=0,
                        )
                        episodes.append(episode)

        except Exception as e:
            console.print(f"[red]Error getting trending podcasts: {e}[/red]")

        return episodes
