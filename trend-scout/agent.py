"""Main Trend Scout agent using LangGraph."""
import os
import asyncio
from typing import TypedDict
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.table import Table

from config import TOPICS, SUBREDDIT_MAP, MAX_RESULTS_PER_SOURCE
from scouts import RedditScout, WebScout

console = Console()


class ScoutState(TypedDict):
    """State for the scout workflow."""
    topics: list[str]
    reddit_results: list[dict]
    web_results: list[dict]
    analysis: str
    digest_html: str
    sent: bool


class TrendScoutAgent:
    """
    Autonomous agent that scouts multiple sources for trending topics
    and generates a daily digest.
    """

    def __init__(self):
        self.reddit = RedditScout()
        self.web = WebScout()

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
        )

        # Build the workflow
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(ScoutState)

        # Add nodes
        workflow.add_node("scout_reddit", self._scout_reddit)
        workflow.add_node("scout_web", self._scout_web)
        workflow.add_node("analyze", self._analyze)
        workflow.add_node("generate_digest", self._generate_digest)

        # Define edges
        workflow.set_entry_point("scout_reddit")
        workflow.add_edge("scout_reddit", "scout_web")
        workflow.add_edge("scout_web", "analyze")
        workflow.add_edge("analyze", "generate_digest")
        workflow.add_edge("generate_digest", END)

        return workflow.compile()

    async def _scout_reddit(self, state: ScoutState) -> dict:
        """Scout Reddit for all topics."""
        console.print("[bold blue]Scouting Reddit...[/bold blue]")
        all_results = []

        for topic in state["topics"]:
            subreddits = SUBREDDIT_MAP.get(topic, ["all"])
            posts = await self.reddit.search(
                query=topic,
                subreddits=subreddits,
                limit=MAX_RESULTS_PER_SOURCE,
                time_filter="week"
            )
            for post in posts:
                result = post.to_dict()
                result["topic"] = topic
                all_results.append(result)

        console.print(f"  Found [green]{len(all_results)}[/green] Reddit posts")
        return {"reddit_results": all_results}

    async def _scout_web(self, state: ScoutState) -> dict:
        """Scout web (Twitter, HN, news) for all topics."""
        console.print("[bold blue]Scouting Web (Twitter, HN, News)...[/bold blue]")
        all_results = []

        for topic in state["topics"]:
            results = await self.web.search_all(
                query=topic,
                limit=MAX_RESULTS_PER_SOURCE,
            )
            for r in results:
                result = r.to_dict()
                result["topic"] = topic
                all_results.append(result)

        console.print(f"  Found [green]{len(all_results)}[/green] web results")
        return {"web_results": all_results}

    async def _analyze(self, state: ScoutState) -> dict:
        """Analyze all results with Gemini."""
        console.print("[bold blue]Analyzing with Gemini...[/bold blue]")

        # Combine all results
        all_results = state["reddit_results"] + state["web_results"]

        if not all_results:
            return {"analysis": "No results found for the specified topics."}

        # Build context for LLM
        results_text = ""
        for r in all_results[:50]:  # Limit to avoid token limits
            results_text += f"""
---
Source: {r.get('source', 'unknown')}
Topic: {r.get('topic', 'unknown')}
Title: {r.get('title', 'N/A')}
Content: {r.get('content', r.get('description', 'N/A'))[:300]}
URL: {r.get('url', 'N/A')}
"""

        prompt = f"""You are a tech trend analyst. Analyze these search results and identify:

1. **Top 5 Most Important Trends** - What themes appear across multiple sources?
2. **Hot Takes** - Any controversial or surprising findings?
3. **Action Items** - What should someone interested in these topics pay attention to?
4. **Notable Finds** - Specific posts or articles worth checking out.

For each trend, explain WHY it matters and cite specific sources.

Topics being tracked: {', '.join(state['topics'])}

Search Results:
{results_text}

Provide a clear, concise analysis. Be specific and cite sources."""

        response = await self.llm.ainvoke([
            SystemMessage(content="You are a sharp tech analyst who cuts through noise to find signal."),
            HumanMessage(content=prompt),
        ])

        console.print("  Analysis complete")
        return {"analysis": response.content}

    async def _generate_digest(self, state: ScoutState) -> dict:
        """Generate HTML email digest."""
        console.print("[bold blue]Generating digest...[/bold blue]")

        # Count results by source
        reddit_count = len(state["reddit_results"])
        web_count = len(state["web_results"])

        # Get top items from each source
        top_reddit = sorted(
            state["reddit_results"],
            key=lambda x: x.get("score", 0),
            reverse=True
        )[:5]

        top_web = state["web_results"][:5]

        date_str = datetime.now().strftime("%B %d, %Y")

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #007bff; margin-top: 30px; }}
        h3 {{ color: #555; }}
        .item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #007bff; }}
        .item a {{ color: #007bff; text-decoration: none; font-weight: 600; }}
        .item a:hover {{ text-decoration: underline; }}
        .meta {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .analysis {{ background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: #e9ecef; padding: 15px 25px; border-radius: 8px; text-align: center; }}
        .stat-num {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Trend Scout Digest</h1>
    <p><strong>{date_str}</strong> | Topics: {', '.join(state['topics'])}</p>

    <div class="stats">
        <div class="stat">
            <div class="stat-num">{reddit_count}</div>
            <div class="stat-label">Reddit Posts</div>
        </div>
        <div class="stat">
            <div class="stat-num">{web_count}</div>
            <div class="stat-label">Web/Twitter</div>
        </div>
    </div>

    <h2>Analysis</h2>
    <div class="analysis">
        {state['analysis'].replace(chr(10), '<br>')}
    </div>

    <h2>Top Reddit Discussions</h2>
"""

        for item in top_reddit:
            html += f"""
    <div class="item">
        <a href="{item.get('url', '#')}">{item.get('title', 'Untitled')}</a>
        <div class="meta">r/{item.get('subreddit', '?')} | Score: {item.get('score', 0)} | {item.get('num_comments', 0)} comments</div>
    </div>
"""

        html += "<h2>From the Web & Twitter</h2>"
        for item in top_web:
            html += f"""
    <div class="item">
        <a href="{item.get('url', '#')}">{item.get('title', 'Untitled')}</a>
        <div class="meta">Source: {item.get('source', 'web')}</div>
    </div>
"""

        html += """
    <div class="footer">
        <p>Generated by Trend Scout | Powered by Composio + Gemini</p>
    </div>
</body>
</html>
"""

        console.print("  Digest ready")
        return {"digest_html": html, "sent": False}

    async def run(self, topics: list[str] = None) -> ScoutState:
        """Run the full scout workflow."""
        if topics is None:
            topics = TOPICS

        console.print(f"\n[bold]Starting Trend Scout[/bold]")
        console.print(f"Topics: {', '.join(topics)}\n")

        initial_state: ScoutState = {
            "topics": topics,
            "reddit_results": [],
            "web_results": [],
            "analysis": "",
            "digest_html": "",
            "sent": False,
        }

        # Run the workflow
        final_state = await self.workflow.ainvoke(initial_state)

        return final_state

    def print_summary(self, state: ScoutState):
        """Print a summary table of results."""
        table = Table(title="Scout Results Summary")
        table.add_column("Source", style="cyan")
        table.add_column("Count", justify="right", style="green")

        table.add_row("Reddit", str(len(state["reddit_results"])))
        table.add_row("Web/Twitter", str(len(state["web_results"])))
        table.add_row("Total", str(
            len(state["reddit_results"]) + len(state["web_results"])
        ), style="bold")

        console.print(table)


# For testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    agent = TrendScoutAgent()
    state = asyncio.run(agent.run())
    agent.print_summary(state)

    # Save digest to file for preview
    with open("digest_preview.html", "w") as f:
        f.write(state["digest_html"])
    console.print("\n[green]Digest saved to digest_preview.html[/green]")
