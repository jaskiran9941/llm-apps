"""
Multimodal RAG Application - Main Entry Point

This Streamlit app demonstrates progressive multimodal RAG capabilities:
- Tab 1: Text-only RAG (baseline)
- Tab 2: Text + Images (vision RAG)
- Tab 3: Text + Images + Tables ✅ FULLY FUNCTIONAL
- Tab 4: Text + Images + Tables + Audio (full multimodal)
- Tab 5: Side-by-side comparison
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import tab modules
from tabs import tab1_baseline, tab2_vision, tab3_tables, tab4_audio, tab5_comparison

# Page config
st.set_page_config(
    page_title="Multimodal RAG",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .modality-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .badge-text { background-color: #e3f2fd; color: #1976d2; }
    .badge-image { background-color: #f3e5f5; color: #7b1fa2; }
    .badge-table { background-color: #e8f5e9; color: #388e3c; }
    .badge-audio { background-color: #fff3e0; color: #f57c00; }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with info and stats."""

    with st.sidebar:
        st.header("ℹ️ About")

        st.markdown("""
        This application demonstrates **progressive multimodal RAG** capabilities:

        **Supported Modalities:**
        - 📄 **Text**: Document chunks
        - 🖼️ **Images**: Visual content (pending)
        - 📊 **Tables**: Structured data ✅
        - 🎵 **Audio**: Transcripts (pending)

        **Status:**
        - ✅ Table RAG fully functional
        - ✅ Backend 100% complete
        - 🚧 Vision & Audio UI pending
        """)

        st.markdown("---")

        st.header("🔧 Configuration")

        # API Key status
        from src.common.config import Config
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "your_openai_api_key_here":
            st.success("✅ API Key configured")
        else:
            st.error("❌ API Key not set")
            st.info("Add to `.env` file")

        # Stats
        st.markdown("---")
        st.header("📊 Vector Store")

        try:
            from src.multimodal.multimodal_store import MultimodalStore
            store = MultimodalStore()
            stats = store.get_stats()

            st.metric("Total Items", stats["total_items"])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Text", stats["by_type"]["text"])
                st.metric("Images", stats["by_type"]["image"])
            with col2:
                st.metric("Tables", stats["by_type"]["table"])
                st.metric("Audio", stats["by_type"]["audio"])

        except Exception as e:
            st.info("Empty store")

        # Clear button
        if st.button("🗑️ Clear Store", help="Remove all data"):
            try:
                from src.multimodal.multimodal_store import MultimodalStore
                store = MultimodalStore()
                store.clear()
                st.success("Store cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def main():
    """Main application."""

    # Header
    st.markdown('<div class="main-header">🎯 Multimodal RAG Beyond Vision</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Tables + Audio Support for Comprehensive Document Understanding</div>', unsafe_allow_html=True)

    # Modality badges
    st.markdown("""
    <div>
        <span class="modality-badge badge-text">📄 Text</span>
        <span class="modality-badge badge-image">🖼️ Images</span>
        <span class="modality-badge badge-table">📊 Tables ✅</span>
        <span class="modality-badge badge-audio">🎵 Audio</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Render sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Text-Only RAG",
        "🖼️ Vision RAG",
        "📊 Table RAG ✅",
        "🎵 Full Multimodal",
        "⚖️ Comparison"
    ])

    with tab1:
        tab1_baseline.render()

    with tab2:
        tab2_vision.render()

    with tab3:
        tab3_tables.render()

    with tab4:
        tab4_audio.render()

    with tab5:
        tab5_comparison.render()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        Built with ❤️ using Streamlit, OpenAI GPT-4, Whisper, and ChromaDB<br>
        <small>Multimodal RAG Beyond Vision: Tables + Audio Support</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
