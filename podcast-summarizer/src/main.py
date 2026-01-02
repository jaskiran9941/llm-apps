#!/usr/bin/env python3
"""Main workflow orchestrator for podcast summarization."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from podcast_fetcher import PodcastFetcher
from transcript_fetcher import TranscriptFetcher
from summarizer import PodcastSummarizer
from email_sender import EmailSender


def main():
    """Run the podcast summarization workflow."""
    # Load environment variables
    load_dotenv()

    print("🎧 Starting Podcast Summarization Workflow\n")

    # Initialize components
    try:
        fetcher = PodcastFetcher()
        transcript_fetcher = TranscriptFetcher()
        summarizer = PodcastSummarizer()
        email_sender = EmailSender()
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        sys.exit(1)

    # Fetch new episodes (last 24 hours)
    print("📥 Fetching new podcast episodes...")
    new_episodes = fetcher.fetch_new_episodes(since_hours=24)

    if not new_episodes:
        print("✅ No new episodes found in the last 24 hours.")

        # Optionally send a "no new episodes" email
        # Uncomment if you want notifications even with no content:
        # email_sender.send_digest("No new episodes today.", {"recommendations_text": ""})

        return

    print(f"📝 Found {len(new_episodes)} new episode(s)\n")

    # Process each episode
    summaries = []

    for i, episode in enumerate(new_episodes, 1):
        print(f"\n--- Processing {i}/{len(new_episodes)}: {episode['episode_title']} ---")

        # Get transcript
        transcript = transcript_fetcher.get_transcript(episode)

        if not transcript:
            print("⚠️  No transcript available, using description as fallback")
            transcript = transcript_fetcher.get_transcript_from_description(episode)

        if not transcript or len(transcript) < 100:
            print("⚠️  Insufficient content, skipping this episode")
            continue

        # Generate summary
        print("🤖 Generating AI summary...")
        summary = summarizer.summarize_episode(episode, transcript)
        summaries.append(summary)

        # Mark as processed
        fetcher.mark_episode_processed(episode)
        print("✅ Episode processed")

    if not summaries:
        print("\n❌ No episodes could be summarized")
        return

    # Generate unified digest
    print("\n📧 Generating email digest...")
    digest_content = summarizer.summarize_multiple_episodes(summaries)

    # Generate recommendations
    print("💡 Generating podcast recommendations...")
    podcast_names = list(set(s['podcast_name'] for s in summaries))
    all_tags = list(fetcher.get_all_podcast_tags())

    recommendations = summarizer.generate_recommendations(podcast_names, all_tags)

    # Send email
    print("📨 Sending digest email...")
    success = email_sender.send_digest(digest_content, recommendations)

    if success:
        print("\n✅ Workflow completed successfully!")
    else:
        print("\n❌ Workflow completed with errors (email failed)")
        sys.exit(1)


def test_email():
    """Test email configuration."""
    load_dotenv()

    try:
        email_sender = EmailSender()
        success = email_sender.send_test_email()

        if success:
            print("\n✅ Test email sent! Check your inbox.")
        else:
            print("\n❌ Failed to send test email.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test-email":
        test_email()
    else:
        main()
