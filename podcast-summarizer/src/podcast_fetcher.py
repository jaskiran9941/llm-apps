"""Fetch and parse podcast RSS feeds."""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import ssl
import feedparser

# macOS Python SSL certificate workaround
# Set globally for this process - this will affect feedparser but OpenAI SDK uses its own HTTP client
ssl._create_default_https_context = ssl._create_unverified_context


class PodcastFetcher:
    """Handles fetching and parsing podcast RSS feeds."""

    def __init__(self, config_path: str = "config/podcasts.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _load_config(self) -> Dict:
        """Load podcast configuration."""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _get_cache_path(self, podcast_name: str) -> Path:
        """Get cache file path for a podcast."""
        safe_name = "".join(c for c in podcast_name if c.isalnum() or c in (' ', '-', '_')).strip()
        return self.cache_dir / f"{safe_name}_processed.json"

    def _load_processed_episodes(self, podcast_name: str) -> set:
        """Load set of already processed episode URLs."""
        cache_path = self._get_cache_path(podcast_name)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                data = json.load(f)
                return set(data.get('processed_episodes', []))
        return set()

    def _save_processed_episode(self, podcast_name: str, episode_url: str):
        """Mark an episode as processed."""
        cache_path = self._get_cache_path(podcast_name)
        processed = self._load_processed_episodes(podcast_name)
        processed.add(episode_url)

        with open(cache_path, 'w') as f:
            json.dump({
                'processed_episodes': list(processed),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    def fetch_new_episodes(self, since_hours: int = 24) -> List[Dict]:
        """
        Fetch new podcast episodes published in the last N hours.

        Args:
            since_hours: Only fetch episodes published in the last N hours

        Returns:
            List of episode dictionaries with metadata
        """
        new_episodes = []
        cutoff_time = datetime.now() - timedelta(hours=since_hours)

        for podcast in self.config.get('podcasts', []):
            if not podcast.get('enabled', True):
                continue

            try:
                feed = feedparser.parse(podcast['rss_url'])
                processed_urls = self._load_processed_episodes(podcast['name'])

                max_episodes = self.config['settings'].get('max_episodes_per_podcast', 1)
                episodes_found = 0

                for entry in feed.entries:
                    if episodes_found >= max_episodes:
                        break

                    # Check if already processed
                    episode_url = entry.get('link', entry.get('id', ''))
                    if episode_url in processed_urls:
                        continue

                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])

                    # Skip old episodes
                    if pub_date and pub_date < cutoff_time:
                        continue

                    # Extract audio URL
                    audio_url = None
                    if hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if 'audio' in enclosure.get('type', ''):
                                audio_url = enclosure.get('href')
                                break

                    # Alternative: check links
                    if not audio_url and hasattr(entry, 'links'):
                        for link in entry.links:
                            if link.get('type', '').startswith('audio'):
                                audio_url = link.get('href')
                                break

                    episode_data = {
                        'podcast_name': podcast['name'],
                        'podcast_tags': podcast.get('tags', []),
                        'episode_title': entry.get('title', 'Untitled'),
                        'episode_url': episode_url,
                        'audio_url': audio_url,
                        'description': entry.get('summary', ''),
                        'published_date': pub_date.isoformat() if pub_date else None,
                        'duration': entry.get('itunes_duration', 'Unknown')
                    }

                    new_episodes.append(episode_data)
                    episodes_found += 1

            except Exception as e:
                print(f"Error fetching {podcast['name']}: {e}")
                continue

        return new_episodes

    def mark_episode_processed(self, episode: Dict):
        """Mark an episode as processed."""
        self._save_processed_episode(episode['podcast_name'], episode['episode_url'])

    def get_all_podcast_tags(self) -> set:
        """Get all unique tags from configured podcasts."""
        tags = set()
        for podcast in self.config.get('podcasts', []):
            tags.update(podcast.get('tags', []))
        return tags
