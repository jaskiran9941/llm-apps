"""Reddit scout using Composio."""
import os
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from composio import ComposioToolSet, Action
from rich.console import Console

console = Console()


@dataclass
class RedditPost:
    """Represents a Reddit post."""
    title: str
    subreddit: str
    url: str
    score: int
    num_comments: int
    created_at: datetime
    selftext: str = ""

    def to_dict(self) -> dict:
        return {
            "source": "reddit",
            "title": self.title,
            "subreddit": self.subreddit,
            "url": self.url,
            "score": self.score,
            "num_comments": self.num_comments,
            "created_at": self.created_at.isoformat(),
            "content": self.selftext[:500] if self.selftext else "",
        }


class RedditScout:
    """Scout Reddit for trending topics using Composio."""

    def __init__(self):
        self.toolset = ComposioToolSet()
        self._authenticated = False

    def check_auth(self) -> bool:
        """Check if Reddit is authenticated with Composio."""
        try:
            connections = self.toolset.get_connected_accounts()
            for conn in connections:
                if conn.appName.lower() == "reddit":
                    self._authenticated = True
                    return True
            return False
        except Exception as e:
            console.print(f"[red]Error checking Reddit auth: {e}[/red]")
            return False

    def authenticate(self) -> str:
        """Initiate Reddit OAuth flow via Composio."""
        try:
            # This returns an auth URL for the user to visit
            connection_request = self.toolset.initiate_connection(
                app="reddit",
                redirect_url="https://backend.composio.dev/api/v1/auth-apps/add"
            )
            return connection_request.redirectUrl
        except Exception as e:
            console.print(f"[red]Error initiating Reddit auth: {e}[/red]")
            return ""

    async def search(
        self,
        query: str,
        subreddits: list[str],
        limit: int = 10,
        time_filter: str = "week"
    ) -> list[RedditPost]:
        """
        Search Reddit for posts matching query.

        Args:
            query: Search query
            subreddits: List of subreddits to search
            limit: Max results per subreddit
            time_filter: One of: hour, day, week, month, year, all
        """
        if not self._authenticated and not self.check_auth():
            console.print("[yellow]Reddit not authenticated. Run setup first.[/yellow]")
            return []

        posts = []

        for subreddit in subreddits:
            try:
                # Use Composio's Reddit search action
                result = self.toolset.execute_action(
                    action=Action.REDDIT_SEARCH,
                    params={
                        "q": query,
                        "subreddit": subreddit,
                        "limit": limit,
                        "t": time_filter,
                        "sort": "relevance",
                    }
                )

                if result.get("successful") and result.get("data"):
                    for item in result["data"].get("children", []):
                        data = item.get("data", {})
                        post = RedditPost(
                            title=data.get("title", ""),
                            subreddit=data.get("subreddit", subreddit),
                            url=f"https://reddit.com{data.get('permalink', '')}",
                            score=data.get("score", 0),
                            num_comments=data.get("num_comments", 0),
                            created_at=datetime.fromtimestamp(data.get("created_utc", 0)),
                            selftext=data.get("selftext", ""),
                        )
                        posts.append(post)

            except Exception as e:
                console.print(f"[red]Error searching r/{subreddit}: {e}[/red]")
                continue

        # Sort by score (engagement)
        posts.sort(key=lambda p: p.score, reverse=True)
        return posts[:limit]

    async def get_hot_posts(
        self,
        subreddits: list[str],
        limit: int = 10
    ) -> list[RedditPost]:
        """Get hot posts from subreddits."""
        if not self._authenticated and not self.check_auth():
            return []

        posts = []

        for subreddit in subreddits:
            try:
                result = self.toolset.execute_action(
                    action=Action.REDDIT_GET_SUBREDDIT_HOT_POSTS,
                    params={
                        "subreddit": subreddit,
                        "limit": limit,
                    }
                )

                if result.get("successful") and result.get("data"):
                    for item in result["data"].get("children", []):
                        data = item.get("data", {})
                        post = RedditPost(
                            title=data.get("title", ""),
                            subreddit=data.get("subreddit", subreddit),
                            url=f"https://reddit.com{data.get('permalink', '')}",
                            score=data.get("score", 0),
                            num_comments=data.get("num_comments", 0),
                            created_at=datetime.fromtimestamp(data.get("created_utc", 0)),
                            selftext=data.get("selftext", ""),
                        )
                        posts.append(post)

            except Exception as e:
                console.print(f"[red]Error getting hot from r/{subreddit}: {e}[/red]")
                continue

        posts.sort(key=lambda p: p.score, reverse=True)
        return posts[:limit]
