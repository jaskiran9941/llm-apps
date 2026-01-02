"""Streamlit testing interface for podcast summarizer."""
import streamlit as st
import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from podcast_fetcher import PodcastFetcher
from transcript_fetcher import TranscriptFetcher
from summarizer import PodcastSummarizer
from email_sender import EmailSender
import json
import feedparser
from datetime import datetime

st.set_page_config(
    page_title="Podcast Summarizer Tester",
    page_icon="🎧",
    layout="wide"
)

st.title("🎧 Podcast Summarizer - Testing Interface")
st.markdown("Test your podcast summarization workflow before deploying to GitHub Actions")

# Sidebar for API Keys
with st.sidebar:
    st.header("🔑 API Configuration")

    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Required for AI summarization"
    )

    sendgrid_key = st.text_input(
        "SendGrid API Key",
        type="password",
        value=os.getenv("SENDGRID_API_KEY", ""),
        help="Required for email delivery"
    )

    from_email = st.text_input(
        "From Email",
        value=os.getenv("FROM_EMAIL", ""),
        help="Verified sender email in SendGrid"
    )

    to_email = st.text_input(
        "To Email",
        value=os.getenv("TO_EMAIL", ""),
        help="Your email address"
    )

    # Set environment variables
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if sendgrid_key:
        os.environ["SENDGRID_API_KEY"] = sendgrid_key
    if from_email:
        os.environ["FROM_EMAIL"] = from_email
    if to_email:
        os.environ["TO_EMAIL"] = to_email

    st.divider()

    st.header("⚙️ Settings")
    summary_length = st.selectbox(
        "Summary Length",
        ["short", "medium", "long"],
        index=1
    )
    os.environ["SUMMARY_LENGTH"] = summary_length

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📡 Test RSS Feed",
    "🤖 Test Summarization",
    "📧 Test Email",
    "📋 Full Workflow"
])

# Tab 1: Test RSS Feed
with tab1:
    st.header("Test Podcast RSS Feed")
    st.markdown("Enter a podcast RSS URL to see what episodes are available")

    rss_url = st.text_input(
        "Podcast RSS URL",
        placeholder="https://example.com/podcast/feed.xml",
        help="Find this on the podcast's website or in podcast directories"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔍 Fetch Episodes", type="primary"):
            if rss_url:
                with st.spinner("Fetching podcast feed..."):
                    try:
                        # Parse feed with SSL verification disabled for self-signed certs
                        import ssl
                        if hasattr(ssl, '_create_unverified_context'):
                            ssl_context = ssl._create_unverified_context()
                        else:
                            ssl_context = None
                        feed = feedparser.parse(rss_url)

                        if feed.bozo:
                            st.error(f"Error parsing feed: {feed.bozo_exception}")
                        else:
                            st.success(f"Found: **{feed.feed.get('title', 'Unknown Podcast')}**")

                            st.subheader(f"Latest Episodes ({len(feed.entries)} total)")

                            for i, entry in enumerate(feed.entries[:5]):
                                with st.expander(f"Episode {i+1}: {entry.get('title', 'Untitled')}"):
                                    st.write(f"**Published:** {entry.get('published', 'Unknown')}")
                                    st.write(f"**Duration:** {entry.get('itunes_duration', 'Unknown')}")

                                    # Audio URL
                                    audio_url = None
                                    if hasattr(entry, 'enclosures') and entry.enclosures:
                                        for enc in entry.enclosures:
                                            if 'audio' in enc.get('type', ''):
                                                audio_url = enc.get('href')
                                                break

                                    if audio_url:
                                        st.write(f"**Audio URL:** ✅ Available")
                                        st.code(audio_url, language=None)
                                    else:
                                        st.write("**Audio URL:** ❌ Not found")

                                    # Description
                                    desc = entry.get('summary', '')
                                    if desc:
                                        st.write(f"**Description Length:** {len(desc)} characters")
                                        with st.expander("View Description"):
                                            st.write(desc[:500] + "..." if len(desc) > 500 else desc)

                                    # Link
                                    if entry.get('link'):
                                        st.write(f"**Episode URL:** {entry.get('link')}")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter an RSS URL")

# Tab 2: Test Summarization
with tab2:
    st.header("Test AI Summarization")
    st.markdown("Test the summarization with a sample podcast episode")

    test_rss = st.text_input(
        "Podcast RSS URL",
        key="summarize_rss",
        placeholder="https://example.com/podcast/feed.xml"
    )

    if st.button("🤖 Fetch & Summarize Latest Episode", type="primary"):
        if not openai_key:
            st.error("❌ OpenAI API Key is required!")
        elif test_rss:
            with st.spinner("Processing episode..."):
                try:
                    # Fetch feed
                    feed = feedparser.parse(test_rss)
                    if not feed.entries:
                        st.error("No episodes found in feed")
                    else:
                        entry = feed.entries[0]

                        # Build episode dict
                        audio_url = None
                        if hasattr(entry, 'enclosures') and entry.enclosures:
                            for enc in entry.enclosures:
                                if 'audio' in enc.get('type', ''):
                                    audio_url = enc.get('href')
                                    break

                        episode = {
                            'podcast_name': feed.feed.get('title', 'Unknown Podcast'),
                            'episode_title': entry.get('title', 'Untitled'),
                            'episode_url': entry.get('link', ''),
                            'audio_url': audio_url,
                            'description': entry.get('summary', ''),
                            'published_date': entry.get('published', None),
                            'duration': entry.get('itunes_duration', 'Unknown'),
                            'podcast_tags': []
                        }

                        st.info(f"**Episode:** {episode['episode_title']}")

                        # Get transcript
                        st.write("**Step 1:** Fetching transcript...")
                        transcript_fetcher = TranscriptFetcher()
                        transcript = transcript_fetcher.get_transcript(episode)

                        if not transcript:
                            st.warning("No transcript found, using description as fallback")
                            transcript = transcript_fetcher.get_transcript_from_description(episode)

                        if transcript and len(transcript) > 100:
                            st.success(f"✅ Got {len(transcript)} characters of text")

                            with st.expander("View Transcript/Content"):
                                st.text(transcript[:2000] + "..." if len(transcript) > 2000 else transcript)

                            # Summarize
                            st.write("**Step 2:** Generating AI summary...")
                            summarizer = PodcastSummarizer()
                            summary = summarizer.summarize_episode(episode, transcript)

                            st.success("✅ Summary generated!")

                            # Display summary
                            st.markdown("---")
                            st.markdown(summary['summary_text'])

                        else:
                            st.error("❌ Insufficient content to summarize")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    with st.expander("View Error Details"):
                        st.code(traceback.format_exc())
        else:
            st.warning("Please enter an RSS URL")

# Tab 3: Test Email
with tab3:
    st.header("Test Email Delivery")
    st.markdown("Send a test email to verify SendGrid configuration")

    st.info(f"**From:** {from_email or 'Not set'}")
    st.info(f"**To:** {to_email or 'Not set'}")

    if st.button("📧 Send Test Email", type="primary"):
        if not sendgrid_key or not from_email or not to_email:
            st.error("❌ SendGrid API Key, From Email, and To Email are all required!")
        else:
            with st.spinner("Sending test email..."):
                try:
                    email_sender = EmailSender()
                    success = email_sender.send_test_email()

                    if success:
                        st.success("✅ Test email sent! Check your inbox.")
                        st.balloons()
                    else:
                        st.error("❌ Failed to send email. Check the console for details.")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    with st.expander("View Error Details"):
                        st.code(traceback.format_exc())

# Tab 4: Full Workflow
with tab4:
    st.header("Full Workflow Test")
    st.markdown("Run the complete workflow with your configured podcasts")

    # Show current config
    config_path = Path(__file__).parent / "config" / "podcasts.json"

    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

        st.subheader("Current Podcast Configuration")

        enabled_podcasts = [p for p in config['podcasts'] if p.get('enabled', True)]

        if enabled_podcasts:
            for podcast in enabled_podcasts:
                st.write(f"✅ **{podcast['name']}**")
                st.write(f"   Tags: {', '.join(podcast.get('tags', []))}")
        else:
            st.warning("No enabled podcasts in configuration")

        st.divider()

        hours_back = st.slider(
            "Check for episodes published in the last N hours",
            min_value=1,
            max_value=2160,
            value=168
        )

        if st.button("🚀 Run Full Workflow", type="primary"):
            if not openai_key:
                st.error("❌ OpenAI API Key is required!")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # Fetch episodes
                    status_text.text("📥 Fetching new episodes...")
                    progress_bar.progress(10)

                    fetcher = PodcastFetcher()
                    new_episodes = fetcher.fetch_new_episodes(since_hours=hours_back)

                    if not new_episodes:
                        st.info("No new episodes found")
                        progress_bar.progress(100)
                    else:
                        st.success(f"Found {len(new_episodes)} new episode(s)")
                        progress_bar.progress(30)

                        # Process episodes
                        transcript_fetcher = TranscriptFetcher()
                        summarizer = PodcastSummarizer()
                        summaries = []

                        for i, episode in enumerate(new_episodes):
                            status_text.text(f"Processing {i+1}/{len(new_episodes)}: {episode['episode_title'][:50]}...")
                            progress_bar.progress(30 + int(40 * (i / len(new_episodes))))

                            # Get transcript
                            transcript = transcript_fetcher.get_transcript(episode)
                            if not transcript:
                                transcript = transcript_fetcher.get_transcript_from_description(episode)

                            if transcript and len(transcript) > 100:
                                summary = summarizer.summarize_episode(episode, transcript)
                                summaries.append(summary)
                                fetcher.mark_episode_processed(episode)

                        if summaries:
                            # Generate digest
                            status_text.text("📧 Generating digest...")
                            progress_bar.progress(80)

                            digest_content = summarizer.summarize_multiple_episodes(summaries)

                            # Generate recommendations
                            podcast_names = list(set(s['podcast_name'] for s in summaries))
                            all_tags = list(fetcher.get_all_podcast_tags())
                            recommendations = summarizer.generate_recommendations(podcast_names, all_tags)

                            # Display results
                            st.markdown("---")
                            st.markdown("### Preview of Email Content")
                            st.markdown(digest_content)
                            st.markdown("---")
                            st.markdown(recommendations['recommendations_text'])

                            # Automatically send email
                            if sendgrid_key and from_email and to_email:
                                status_text.text("📧 Sending email...")
                                progress_bar.progress(90)

                                try:
                                    email_sender = EmailSender()
                                    success = email_sender.send_digest(digest_content, recommendations)

                                    if success:
                                        st.success("✅ Email sent successfully to " + to_email)
                                        st.balloons()
                                    else:
                                        st.error("❌ Failed to send email. Check the error details below.")
                                except Exception as email_error:
                                    st.error(f"❌ Error sending email: {str(email_error)}")
                                    import traceback
                                    with st.expander("View Email Error Details"):
                                        st.code(traceback.format_exc())
                            else:
                                st.warning("⚠️ Email not sent - SendGrid credentials not configured")

                            progress_bar.progress(100)
                            status_text.text("✅ Complete!")
                        else:
                            st.warning("No episodes could be summarized")
                            progress_bar.progress(100)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    with st.expander("View Error Details"):
                        st.code(traceback.format_exc())
    else:
        st.error(f"Configuration file not found: {config_path}")

# Footer
st.divider()
st.markdown("### 💡 Tips")
st.markdown("""
- **Test RSS Feed first** to verify your podcast URLs are correct
- **Test Summarization** to ensure API keys work and content is good
- **Test Email** to verify SendGrid configuration
- **Run Full Workflow** to test everything together before deploying to GitHub Actions
""")
