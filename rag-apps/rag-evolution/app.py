"""
RAG Evolution Showcase - Main Streamlit App
Demonstrates the evolution of RAG from limitations to vision-based solutions
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import components for each tab
from tabs import tab1_baseline, tab2_chunking, tab3_hybrid, tab4_vision

# Page configuration
st.set_page_config(
    page_title="RAG Evolution Showcase",
    page_icon="🚀",
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
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .problem-box {
        background-color: #ffe6e6;
        border-left: 5px solid #ff4444;
        padding: 1rem;
        margin: 1rem 0;
    }
    .solution-box {
        background-color: #e6ffe6;
        border-left: 5px solid #44ff44;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e6f3ff;
        border-left: 5px solid #4444ff;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">🚀 RAG Evolution Showcase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">From Limitations to Vision-based Solutions</div>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("About This App")
    st.info("""
    This app demonstrates the evolution of RAG systems through 4 progressive stages:

    1. **Baseline RAG**: See the problems
    2. **Smart Chunking**: Fix text boundaries
    3. **Hybrid Retrieval**: Fix exact match issues
    4. **Vision RAG**: Fix image blindness

    Each tab shows problems and solutions in action!
    """)

    st.header("Learning Goals")
    st.success("""
    - Understand RAG fundamentals
    - See limitations firsthand
    - Learn progressive solutions
    - Master vision-based RAG
    """)

    st.header("Tech Stack")
    st.code("""
    - OpenAI (embeddings, GPT-4, GPT-4V)
    - ChromaDB (vector storage)
    - BM25 (keyword search)
    - PyMuPDF (image extraction)
    """)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Baseline RAG (Problems)",
    "2️⃣ Smart Chunking (Solution 1)",
    "3️⃣ Hybrid Retrieval (Solution 2)",
    "4️⃣ Vision RAG (Ultimate)"
])

# Tab 1: Baseline RAG
with tab1:
    tab1_baseline.render()

# Tab 2: Smart Chunking
with tab2:
    tab2_chunking.render()

# Tab 3: Hybrid Retrieval
with tab3:
    tab3_hybrid.render()

# Tab 4: Vision RAG
with tab4:
    tab4_vision.render()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with OpenAI, ChromaDB, and Streamlit | Educational Project</p>
    <p>Estimated Cost per Session: $0.10 - $0.50</p>
</div>
""", unsafe_allow_html=True)
