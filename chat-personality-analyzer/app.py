"""Chat Personality Analyzer - Streamlit App."""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import UPLOADS_DIR, GOOGLE_API_KEY
from src.services.personality_analyzer import PersonalityAnalyzer

# Page config
st.set_page_config(
    page_title="Chat Personality Analyzer",
    page_icon="🧠",
    layout="wide"
)


def init_session_state():
    """Initialize session state variables."""
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "api_key_configured" not in st.session_state:
        st.session_state.api_key_configured = False
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "uploaded_paths" not in st.session_state:
        st.session_state.uploaded_paths = []


def display_personality_card(name: str, personality: dict):
    """Display a personality analysis card for one person."""
    with st.expander(f"**{name}**", expanded=True):
        if "error" in personality:
            st.error(personality.get("raw_text", "Failed to analyze"))
            return

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Communication Style**")
            style = personality.get("communication_style", {})
            if isinstance(style, dict):
                for key, value in style.items():
                    st.write(f"- {key.replace('_', ' ').title()}: {value}")
            else:
                st.write(style)

            st.markdown("**Personality Traits**")
            traits = personality.get("personality_traits", [])
            if traits:
                st.write(", ".join(traits))

        with col2:
            st.markdown("**Values & Interests**")
            values = personality.get("values_interests", [])
            if values:
                for v in values:
                    st.write(f"- {v}")

            st.markdown("**Emotional Tendency**")
            st.write(personality.get("emotional_tendency", "Unknown"))

            st.markdown("**Conversation Role**")
            st.write(personality.get("conversation_role", "Unknown"))


def display_advice_card(name: str, advice: dict):
    """Display approach advice for one person."""
    with st.expander(f"**How to Approach {name}**", expanded=True):
        if "error" in advice:
            st.error(advice.get("raw_text", "Failed to generate advice"))
            return

        # Key insight at the top
        key_insight = advice.get("key_insight", "")
        if key_insight:
            st.info(f"**Key Insight:** {key_insight}")

        st.markdown("**Best Communication Approach**")
        st.write(advice.get("communication_approach", "Not available"))

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Topics to Focus On**")
            topics = advice.get("topics_to_focus_on", [])
            for topic in topics:
                st.write(f"✓ {topic}")

        with col2:
            st.markdown("**Things to Avoid**")
            avoid = advice.get("things_to_avoid", [])
            for item in avoid:
                st.write(f"✗ {item}")

        st.markdown("**Building Rapport**")
        st.write(advice.get("building_rapport", "Not available"))


def main():
    """Main app function."""
    init_session_state()

    # Header
    st.title("🧠 Chat Personality Analyzer")
    st.markdown("Upload conversation screenshots to analyze participant personalities and get approach advice.")

    # Sidebar: API Configuration
    with st.sidebar:
        st.header("Configuration")

        # API key input with env fallback
        api_key = st.text_input(
            "Google Gemini API Key",
            value=GOOGLE_API_KEY,
            type="password",
            help="Get your API key from https://makersuite.google.com/app/apikey"
        )

        if not api_key:
            st.warning("Please enter your Gemini API key to continue.")
            st.stop()

        # Initialize analyzer if key changed or not configured
        if not st.session_state.api_key_configured or st.session_state.analyzer is None:
            try:
                st.session_state.analyzer = PersonalityAnalyzer(api_key)
                st.session_state.api_key_configured = True
                st.success("API key configured!")
            except Exception as e:
                st.error(f"Failed to configure API: {e}")
                st.stop()

        st.divider()
        st.markdown("**How to use:**")
        st.markdown("""
        1. Upload screenshot(s) of a conversation
        2. Click "Analyze Conversation"
        3. View personality insights and approach advice
        """)

    # Main content
    uploaded_files = st.file_uploader(
        "Upload conversation screenshots",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="Upload one or more screenshots of the conversation"
    )

    if uploaded_files:
        # Display uploaded images
        st.subheader("Uploaded Screenshots")
        cols = st.columns(min(len(uploaded_files), 3))

        # Save uploaded files and display previews
        image_paths = []
        for idx, uploaded_file in enumerate(uploaded_files):
            # Save to uploads directory
            file_path = UPLOADS_DIR / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            image_paths.append(str(file_path))

            # Display preview
            col_idx = idx % 3
            with cols[col_idx]:
                st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

        st.session_state.uploaded_paths = image_paths

        # Analyze button
        if st.button("🔍 Analyze Conversation", type="primary", use_container_width=True):
            with st.spinner("Analyzing conversation... This may take a moment."):
                try:
                    results = st.session_state.analyzer.analyze_screenshots(image_paths)
                    st.session_state.analysis_results = results
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.session_state.analysis_results = None

    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        st.divider()

        # Extracted conversation
        with st.expander("📝 Extracted Conversation", expanded=False):
            st.text(results.get("extracted_text", "No text extracted"))

        # Personality Analysis
        st.subheader("👤 Personality Analysis")
        personalities = results.get("personalities", {})

        if "error" in personalities:
            st.error(f"Failed to analyze personalities: {personalities.get('raw_text', 'Unknown error')}")
        else:
            for name, personality in personalities.items():
                display_personality_card(name, personality)

        # Approach Advice
        st.subheader("💡 How to Approach Each Person")
        advice = results.get("advice", {})

        if "error" in advice:
            st.error(f"Failed to generate advice: {advice.get('raw_text', 'Unknown error')}")
        else:
            for name, person_advice in advice.items():
                display_advice_card(name, person_advice)


if __name__ == "__main__":
    main()
