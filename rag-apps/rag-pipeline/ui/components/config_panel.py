"""
Configuration panel UI component.

Allows users to adjust RAG parameters and see their effects.
"""

import streamlit as st


def render_config_sidebar():
    """
    Render configuration panel in sidebar.

    Returns:
        Dictionary with configuration values
    """
    st.sidebar.header("⚙️ Configuration")

    # Chunking settings
    st.sidebar.subheader("📄 Chunking")

    chunk_size = st.sidebar.slider(
        "Chunk Size (characters)",
        min_value=200,
        max_value=2000,
        value=500,
        step=100,
        help="Larger chunks = more context but less precision"
    )

    chunk_overlap = st.sidebar.slider(
        "Chunk Overlap (characters)",
        min_value=0,
        max_value=min(500, chunk_size // 2),
        value=50,
        step=10,
        help="Overlap helps maintain context across boundaries"
    )

    # Show warning if overlap is large
    if chunk_overlap > chunk_size * 0.3:
        st.sidebar.warning(f"⚠️ Large overlap ({chunk_overlap/chunk_size*100:.0f}%) increases costs")

    st.sidebar.markdown("---")

    # Retrieval settings
    st.sidebar.subheader("🔍 Retrieval")

    top_k = st.sidebar.slider(
        "Top-K Chunks",
        min_value=1,
        max_value=20,
        value=5,
        help="Number of chunks to retrieve"
    )

    min_score = st.sidebar.slider(
        "Minimum Similarity Score",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Filter out chunks below this score"
    )

    st.sidebar.markdown("---")

    # Generation settings
    st.sidebar.subheader("🤖 Generation")

    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="0 = deterministic, 1 = creative"
    )

    max_tokens = st.sidebar.slider(
        "Max Output Tokens",
        min_value=100,
        max_value=2000,
        value=1000,
        step=100,
        help="Maximum length of generated response"
    )

    # Show parameter explanations
    with st.sidebar.expander("ℹ️ Parameter Guide"):
        st.markdown("""
        **Chunk Size:**
        - Small (200-300): Precise but less context
        - Medium (400-700): Balanced ✅
        - Large (800+): More context but less precise

        **Overlap:**
        - None (0): No redundancy
        - Small (50-100): Good continuity ✅
        - Large (200+): Expensive, diminishing returns

        **Top-K:**
        - Low (1-3): Fast, cheap, focused
        - Medium (4-7): Balanced ✅
        - High (10+): Comprehensive but expensive

        **Temperature:**
        - 0: Deterministic, factual ✅
        - 0.7: Balanced
        - 1+: Creative, varied
        """)

    return {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "top_k": top_k,
        "min_score": min_score,
        "temperature": temperature,
        "max_tokens": max_tokens
    }


def render_cost_calculator():
    """
    Render interactive cost calculator.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("💰 Cost Calculator")

    num_docs = st.sidebar.number_input(
        "Number of documents",
        min_value=1,
        max_value=1000,
        value=10,
        step=1
    )

    avg_pages = st.sidebar.number_input(
        "Avg pages per document",
        min_value=1,
        max_value=1000,
        value=20,
        step=5
    )

    queries_per_day = st.sidebar.number_input(
        "Queries per day",
        min_value=1,
        max_value=10000,
        value=50,
        step=10
    )

    # Estimate costs
    # Rough estimates:
    # - 1 page ≈ 500 tokens
    # - Embedding cost: $0.0001 per 1K tokens
    # - Query cost: ~$0.02 per query (varies with complexity)

    total_pages = num_docs * avg_pages
    total_tokens = total_pages * 500

    indexing_cost = (total_tokens / 1000) * 0.0001
    daily_query_cost = queries_per_day * 0.02
    monthly_cost = indexing_cost + (daily_query_cost * 30)

    st.sidebar.markdown(f"""
    **Estimated Costs:**
    - Indexing: ${indexing_cost:.2f} (one-time)
    - Daily queries: ${daily_query_cost:.2f}
    - Monthly total: ${monthly_cost:.2f}

    *Note: Rough estimates, actual costs vary*
    """)


def render_system_info(vector_store):
    """
    Render system information.

    Args:
        vector_store: Vector store to get stats from
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ System Info")

    stats = vector_store.get_stats()

    # Get indexed chunk settings from first chunk if available
    indexed_chunk_size = "N/A"
    indexed_chunk_overlap = "N/A"
    if vector_store.chunks:
        first_chunk = vector_store.chunks[0]
        indexed_chunk_size = first_chunk.metadata.get("chunk_size", "N/A")
        indexed_chunk_overlap = first_chunk.metadata.get("chunk_overlap", "N/A")

    st.sidebar.markdown(f"""
    - Collection: `{stats.get('collection_name', 'N/A')}`
    - Metric: `{stats.get('distance_function', 'N/A')}`
    - Total chunks: {stats.get('total_chunks', 0)}
    - Total docs: {stats.get('total_documents', 0)}
    - Indexed chunk size: {indexed_chunk_size}
    - Indexed chunk overlap: {indexed_chunk_overlap}
    """)

    # Clear database button
    if st.sidebar.button("🗑️ Clear All Data", help="Delete all indexed documents"):
        if st.sidebar.checkbox("Confirm deletion"):
            vector_store.clear()
            st.sidebar.success("Database cleared!")
            st.rerun()
