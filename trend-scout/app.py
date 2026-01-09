"""Streamlit dashboard for Trend Scout."""
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load existing .env if present
load_dotenv()

# Config file for UI-entered settings
CONFIG_FILE = Path(__file__).parent / "config.json"

st.set_page_config(
    page_title="Trend Scout",
    page_icon="🔍",
    layout="wide",
)


def load_config() -> dict:
    """Load config from JSON file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save config to JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key(key_name: str) -> str:
    """Get API key from config or environment."""
    config = load_config()
    return config.get(key_name, "") or os.getenv(key_name, "")


def set_api_key(key_name: str, value: str):
    """Save API key to config."""
    config = load_config()
    config[key_name] = value
    save_config(config)
    os.environ[key_name] = value


def check_connections():
    """Check which services are connected."""
    composio_key = get_api_key("COMPOSIO_API_KEY")
    if not composio_key:
        return {"Reddit": False, "Gmail": False}

    os.environ["COMPOSIO_API_KEY"] = composio_key

    status = {}
    try:
        from scouts import RedditScout
        from email_sender import EmailSender

        reddit = RedditScout()
        status["Reddit"] = reddit.check_auth()

        email = EmailSender()
        status["Gmail"] = email.check_auth()
    except Exception as e:
        status = {"Reddit": False, "Gmail": False}

    return status


def get_saved_digests():
    """Get list of saved digest files."""
    digest_dir = Path(__file__).parent / "digests"
    if not digest_dir.exists():
        return []

    files = list(digest_dir.glob("digest_*.html"))
    files.sort(reverse=True, key=lambda x: x.stat().st_mtime)
    return files


def sidebar():
    """Sidebar with API keys and settings."""
    with st.sidebar:
        st.header("🔑 API Keys")

        # Composio
        st.markdown("[Get Composio key](https://app.composio.dev/settings)")
        composio_key = st.text_input(
            "Composio",
            value=get_api_key("COMPOSIO_API_KEY"),
            type="password",
            key="composio_input",
            placeholder="Enter Composio API key"
        )

        # Google
        st.markdown("[Get Google AI key](https://aistudio.google.com/apikey)")
        google_key = st.text_input(
            "Google AI",
            value=get_api_key("GOOGLE_API_KEY"),
            type="password",
            key="google_input",
            placeholder="Enter Google API key"
        )

        # Tavily
        st.markdown("[Get Tavily key](https://tavily.com)")
        tavily_key = st.text_input(
            "Tavily",
            value=get_api_key("TAVILY_API_KEY"),
            type="password",
            key="tavily_input",
            placeholder="Enter Tavily API key"
        )

        # Email
        digest_email = st.text_input(
            "Digest Email",
            value=get_api_key("DIGEST_EMAIL"),
            key="email_input",
            placeholder="your@email.com"
        )

        if st.button("💾 Save Keys", use_container_width=True):
            set_api_key("COMPOSIO_API_KEY", composio_key)
            set_api_key("GOOGLE_API_KEY", google_key)
            set_api_key("TAVILY_API_KEY", tavily_key)
            set_api_key("DIGEST_EMAIL", digest_email)
            st.success("Saved!")
            st.rerun()

        st.divider()

        # Connection status
        st.header("🔗 Connections")

        if not get_api_key("COMPOSIO_API_KEY"):
            st.caption("Add Composio key first")
        else:
            os.environ["COMPOSIO_API_KEY"] = get_api_key("COMPOSIO_API_KEY")
            status = check_connections()

            for service, connected in status.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    if connected:
                        st.success(service, icon="✅")
                    else:
                        st.warning(service, icon="⚠️")
                with col2:
                    if not connected:
                        if st.button("Connect", key=f"connect_{service}"):
                            try:
                                if service == "Reddit":
                                    from scouts import RedditScout
                                    scout = RedditScout()
                                    auth_url = scout.authenticate()
                                elif service == "Gmail":
                                    from email_sender import EmailSender
                                    sender = EmailSender()
                                    auth_url = sender.authenticate()
                                else:
                                    auth_url = None

                                if auth_url:
                                    st.markdown(f"[🔗 Click to connect]({auth_url})")
                            except Exception as e:
                                st.error(str(e)[:50])

        st.divider()

        # Topics
        st.header("📋 Topics")
        config = load_config()
        current_topics = config.get("topics", [
            "AI agents",
            "LLM applications",
            "developer tools",
            "startups funding",
        ])

        topics_text = st.text_area(
            "One per line",
            value="\n".join(current_topics),
            height=120,
            label_visibility="collapsed"
        )

        if st.button("Save Topics", use_container_width=True):
            new_topics = [t.strip() for t in topics_text.split("\n") if t.strip()]
            config = load_config()
            config["topics"] = new_topics
            save_config(config)
            st.success(f"Saved {len(new_topics)} topics!")


def run_scout_page():
    """Main scout runner page."""
    st.header("Run Scout")

    # Check for required keys
    missing_keys = []
    if not get_api_key("COMPOSIO_API_KEY"):
        missing_keys.append("Composio")
    if not get_api_key("GOOGLE_API_KEY"):
        missing_keys.append("Google AI")
    if not get_api_key("TAVILY_API_KEY"):
        missing_keys.append("Tavily")

    if missing_keys:
        st.warning(f"⚠️ Missing API keys: {', '.join(missing_keys)}")
        st.info("👈 Add your API keys in the sidebar")
        return

    # Set environment variables
    os.environ["COMPOSIO_API_KEY"] = get_api_key("COMPOSIO_API_KEY")
    os.environ["GOOGLE_API_KEY"] = get_api_key("GOOGLE_API_KEY")
    os.environ["TAVILY_API_KEY"] = get_api_key("TAVILY_API_KEY")

    # Load topics
    config = load_config()
    topics = config.get("topics", [
        "AI agents",
        "LLM applications",
        "developer tools",
        "startups funding",
    ])

    # Connection status
    status = check_connections()
    cols = st.columns(2)
    for i, (service, connected) in enumerate(status.items()):
        with cols[i]:
            if connected:
                st.success(f"✅ {service}")
            else:
                st.warning(f"⚠️ {service}")

    st.divider()

    # Topic selection
    selected_topics = st.multiselect(
        "Select topics to scout",
        options=topics,
        default=topics[:2] if len(topics) >= 2 else topics
    )

    # Email option
    digest_email = get_api_key("DIGEST_EMAIL")
    send_email = st.checkbox(
        f"📧 Send digest to {digest_email}" if digest_email else "📧 Send email",
        value=bool(digest_email) and status.get("Gmail", False),
        disabled=not digest_email or not status.get("Gmail", False)
    )

    st.divider()

    # Run button
    if st.button("🚀 Run Scout Now", type="primary", use_container_width=True):
        if not selected_topics:
            st.error("Please select at least one topic")
            return

        from agent import TrendScoutAgent
        from email_sender import EmailSender
        import config as cfg
        cfg.TOPICS = selected_topics

        with st.spinner("Scouting..."):
            progress = st.progress(0, text="Initializing...")

            async def run_scout():
                agent = TrendScoutAgent()

                progress.progress(10, text="🔍 Scouting Reddit...")
                state = await agent.run(selected_topics)

                progress.progress(80, text="📝 Generating digest...")

                # Save digest
                digest_dir = Path(__file__).parent / "digests"
                digest_dir.mkdir(exist_ok=True)
                digest_path = digest_dir / f"digest_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
                digest_path.write_text(state["digest_html"])

                progress.progress(90, text="✨ Finalizing...")

                if send_email and digest_email:
                    progress.progress(95, text="📧 Sending email...")
                    sender = EmailSender()
                    await sender.send_trend_digest(
                        to_email=digest_email,
                        digest_html=state["digest_html"],
                        topics=selected_topics,
                    )

                progress.progress(100, text="✅ Done!")
                return state, str(digest_path)

            state, digest_path = asyncio.run(run_scout())

        st.success("Scout complete!")

        # Stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Reddit", len(state["reddit_results"]))
        col2.metric("Web/X", len(state["web_results"]))
        total = len(state["reddit_results"]) + len(state["web_results"])
        col3.metric("Total", total)

        # Analysis
        with st.expander("📊 Analysis", expanded=True):
            st.markdown(state["analysis"])

        # Digest preview
        with st.expander("📄 Digest Preview"):
            st.components.v1.html(state["digest_html"], height=600, scrolling=True)


def digests_page():
    """View saved digests."""
    st.header("Saved Digests")

    digests = get_saved_digests()

    if not digests:
        st.info("No digests yet. Run a scout to generate one.")
        return

    selected = st.selectbox(
        "Select digest",
        options=digests,
        format_func=lambda x: x.stem.replace("digest_", "").replace("_", " @ "),
    )

    if selected:
        html_content = selected.read_text()

        col1, col2 = st.columns([3, 1])
        with col2:
            st.download_button(
                label="⬇️ Download",
                data=html_content,
                file_name=selected.name,
                mime="text/html",
            )

        st.components.v1.html(html_content, height=800, scrolling=True)


def main():
    # Sidebar with API keys
    sidebar()

    # Main content
    st.title("🔍 Trend Scout")
    st.caption("Autonomous tech trend digest powered by Composio + Gemini")

    tab1, tab2 = st.tabs(["Run Scout", "Digests"])

    with tab1:
        run_scout_page()

    with tab2:
        digests_page()


if __name__ == "__main__":
    main()
