"""Web scout using Tavily for X/Twitter and general web search."""
import os
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from tavily import TavilyClient
from rich.console import Console

console = Console()


@dataclass
class WebResult:
    """Represents a web search result."""
    title: str
    url: str
    content: str
    source: str  # twitter, blog, news, etc.
    published_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "content": self.content[:500],
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }


class WebScout:
    """
    Scout the web using Tavily.

    This is the fallback for X/Twitter (avoids expensive API)
    and can search blogs, news, etc.
    """

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not set")
        self.client = TavilyClient(api_key=api_key)

    async def search_twitter(
        self,
        query: str,
        limit: int = 10
    ) -> list[WebResult]:
        """
        Search X/Twitter content via Tavily web search.
        Avoids expensive X API by searching indexed tweets.
        """
        results = []

        try:
            # Search specifically on twitter.com/x.com
            response = self.client.search(
                query=f"{query} site:twitter.com OR site:x.com",
                search_depth="advanced",
                max_results=limit,
                include_domains=["twitter.com", "x.com"],
            )

            for item in response.get("results", []):
                result = WebResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    source="twitter",
                )
                results.append(result)

        except Exception as e:
            console.print(f"[red]Error searching Twitter: {e}[/red]")

        return results

    async def search_tech_news(
        self,
        query: str,
        limit: int = 10
    ) -> list[WebResult]:
        """Search tech news and blogs."""
        results = []

        # Tech news domains
        domains = [
            "techcrunch.com",
            "theverge.com",
            "arstechnica.com",
            "wired.com",
            "hackernews.com",
            "producthunt.com",
        ]

        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=limit,
                include_domains=domains,
            )

            for item in response.get("results", []):
                result = WebResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    source="news",
                )
                results.append(result)

        except Exception as e:
            console.print(f"[red]Error searching tech news: {e}[/red]")

        return results

    async def search_hacker_news(
        self,
        query: str,
        limit: int = 10
    ) -> list[WebResult]:
        """Search Hacker News discussions."""
        results = []

        try:
            response = self.client.search(
                query=f"{query} site:news.ycombinator.com",
                search_depth="advanced",
                max_results=limit,
            )

            for item in response.get("results", []):
                result = WebResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    source="hackernews",
                )
                results.append(result)

        except Exception as e:
            console.print(f"[red]Error searching HN: {e}[/red]")

        return results

    async def search_all(
        self,
        query: str,
        limit: int = 10
    ) -> list[WebResult]:
        """Search across Twitter, news, and HN."""
        all_results = []

        # Run all searches
        twitter = await self.search_twitter(query, limit=limit//3)
        news = await self.search_tech_news(query, limit=limit//3)
        hn = await self.search_hacker_news(query, limit=limit//3)

        all_results.extend(twitter)
        all_results.extend(news)
        all_results.extend(hn)

        return all_results[:limit]
