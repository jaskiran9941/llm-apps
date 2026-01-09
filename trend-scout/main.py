"""Main entry point for Trend Scout."""
import os
import asyncio
import argparse
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from rich.console import Console
from dotenv import load_dotenv

from config import TOPICS, DIGEST_EMAIL, DIGEST_TIME
from agent import TrendScoutAgent
from email_sender import EmailSender

load_dotenv()
console = Console()


async def run_scout_and_send(topics: list[str] = None, send_email: bool = True):
    """Run the scout workflow and optionally send email."""
    if topics is None:
        topics = TOPICS

    agent = TrendScoutAgent()
    sender = EmailSender()

    console.print(f"\n[bold cyan]{'='*50}[/bold cyan]")
    console.print(f"[bold]Trend Scout - {datetime.now().strftime('%Y-%m-%d %H:%M')}[/bold]")
    console.print(f"[bold cyan]{'='*50}[/bold cyan]\n")

    # Run the agent
    state = await agent.run(topics)

    # Print summary
    agent.print_summary(state)

    # Save digest locally
    digest_path = f"digests/digest_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
    os.makedirs("digests", exist_ok=True)
    with open(digest_path, "w") as f:
        f.write(state["digest_html"])
    console.print(f"\n[green]Digest saved to {digest_path}[/green]")

    # Send email if configured
    if send_email and DIGEST_EMAIL:
        console.print(f"\n[bold]Sending digest to {DIGEST_EMAIL}...[/bold]")
        success = await sender.send_trend_digest(
            to_email=DIGEST_EMAIL,
            digest_html=state["digest_html"],
            topics=topics,
        )
        if success:
            console.print("[green]Email sent successfully![/green]")
        else:
            console.print("[red]Failed to send email. Check Gmail auth.[/red]")
    elif not DIGEST_EMAIL:
        console.print("[yellow]No DIGEST_EMAIL set. Skipping email.[/yellow]")

    return state


async def run_scheduler():
    """Run the scout on a schedule."""
    # Parse time from config
    hour, minute = DIGEST_TIME.split(":")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scout_and_send,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="trend_scout_daily",
        name="Daily Trend Scout",
    )

    console.print(f"[bold green]Scheduler started![/bold green]")
    console.print(f"Will run daily at {DIGEST_TIME}")
    console.print("Press Ctrl+C to stop.\n")

    scheduler.start()

    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        console.print("\n[yellow]Scheduler stopped.[/yellow]")
        scheduler.shutdown()


async def setup_auth():
    """Interactive setup for Composio authentication."""
    from scouts import RedditScout, PodcastScout
    from email_sender import EmailSender

    console.print("\n[bold]Trend Scout Setup[/bold]\n")

    # Check each service
    services = [
        ("Reddit", RedditScout()),
        ("Gmail", EmailSender()),
        ("Listen Notes (Podcasts)", PodcastScout()),
    ]

    for name, service in services:
        if service.check_auth():
            console.print(f"[green]{name}: Connected[/green]")
        else:
            console.print(f"[yellow]{name}: Not connected[/yellow]")
            auth_url = service.authenticate()
            if auth_url:
                console.print(f"  Visit this URL to connect {name}:")
                console.print(f"  [blue]{auth_url}[/blue]\n")
                input("  Press Enter after authenticating...")

    console.print("\n[green]Setup complete![/green]")


def main():
    parser = argparse.ArgumentParser(description="Trend Scout - Your daily tech trend digest")
    parser.add_argument(
        "command",
        choices=["run", "schedule", "setup", "preview"],
        help="Command to run"
    )
    parser.add_argument(
        "--topics",
        nargs="+",
        help="Override default topics",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Skip sending email",
    )

    args = parser.parse_args()

    if args.command == "setup":
        asyncio.run(setup_auth())

    elif args.command == "run":
        topics = args.topics if args.topics else TOPICS
        asyncio.run(run_scout_and_send(topics, send_email=not args.no_email))

    elif args.command == "schedule":
        asyncio.run(run_scheduler())

    elif args.command == "preview":
        # Run without email, just preview
        topics = args.topics if args.topics else TOPICS
        asyncio.run(run_scout_and_send(topics, send_email=False))
        console.print("\n[cyan]Open digests/ folder to view the HTML digest[/cyan]")


if __name__ == "__main__":
    main()
