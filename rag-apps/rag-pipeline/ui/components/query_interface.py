"""
Query interface UI component.

Handles:
- Query input
- RAG vs non-RAG comparison
- Results display with retrieved chunks
"""

import streamlit as st
from src.pipeline.query_pipeline import QueryPipeline
from src.models import QueryResult


def render_query_input():
    """
    Render query input interface.

    Returns:
        Tuple of (query text, top_k value)
    """
    st.header("🔍 Ask Questions")

    # Query input
    query = st.text_area(
        "Your question:",
        placeholder="e.g., What are the main features of the product?",
        height=100,
        help="Ask a question about your uploaded documents"
    )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        top_k = st.slider(
            "Number of chunks to retrieve",
            min_value=1,
            max_value=20,
            value=5,
            help="More chunks = more context but higher cost"
        )

        show_comparison = st.checkbox(
            "Compare RAG vs Non-RAG",
            value=False,
            help="See how RAG improves answers compared to base model"
        )

    return query, top_k, show_comparison


def render_query_buttons():
    """
    Render query execution buttons.

    Returns:
        Tuple of (ask_rag, ask_no_rag, ask_compare)
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        ask_rag = st.button(
            "🎯 Ask with RAG",
            type="primary",
            use_container_width=True,
            help="Answer using retrieved document context"
        )

    with col2:
        ask_no_rag = st.button(
            "💭 Ask without RAG",
            use_container_width=True,
            help="Answer using only model's base knowledge"
        )

    with col3:
        ask_compare = st.button(
            "⚖️ Compare Both",
            use_container_width=True,
            help="Compare RAG vs non-RAG answers side-by-side"
        )

    return ask_rag, ask_no_rag, ask_compare


def render_query_result(result: QueryResult, show_chunks: bool = True):
    """
    Render query result with answer and metadata.

    Args:
        result: QueryResult object
        show_chunks: Whether to show retrieved chunks
    """
    # Answer
    st.markdown("### 💬 Answer")
    st.markdown(result.answer)

    # Metadata
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Tokens",
            result.tokens_used.get('total', 0),
            help="Total tokens used (input + output)"
        )

    with col2:
        st.metric(
            "Cost",
            f"${result.cost:.4f}",
            help="Cost of this query"
        )

    with col3:
        st.metric(
            "Latency",
            f"{result.latency:.2f}s",
            help="Time to generate answer"
        )

    with col4:
        st.metric(
            "Chunks Used",
            len(result.retrieved_chunks),
            help="Number of retrieved chunks"
        )

    # Show retrieved chunks
    if show_chunks and result.retrieved_chunks:
        st.markdown("---")
        st.markdown("### 📑 Retrieved Context")

        for i, chunk in enumerate(result.retrieved_chunks, 1):
            with st.expander(
                f"Chunk {i}: {chunk.source_document} (Page {chunk.page_number}) - "
                f"Score: {chunk.score:.3f}"
            ):
                # Score indicator
                score_color = (
                    "🟢" if chunk.score >= 0.8
                    else "🟡" if chunk.score >= 0.6
                    else "🔴"
                )
                st.markdown(f"{score_color} **Relevance:** {chunk.score:.3f}")

                # Progress bar for score
                st.progress(chunk.score)

                # Chunk text
                st.markdown("**Text:**")
                st.text_area(
                    "Chunk content",
                    chunk.text,
                    height=150,
                    key=f"chunk_{chunk.chunk_id}",
                    label_visibility="collapsed"
                )


def render_comparison(rag_result: QueryResult, no_rag_result: QueryResult):
    """
    Render side-by-side comparison of RAG vs non-RAG results.

    Args:
        rag_result: RAG query result
        no_rag_result: Non-RAG query result
    """
    st.markdown("## ⚖️ RAG vs Non-RAG Comparison")

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 With RAG (Context-Based)")
        st.markdown("**Answer:**")
        st.info(rag_result.answer)

        st.markdown("**Metrics:**")
        st.write(f"- Tokens: {rag_result.tokens_used.get('total', 0)}")
        st.write(f"- Cost: ${rag_result.cost:.4f}")
        st.write(f"- Chunks: {len(rag_result.retrieved_chunks)}")
        st.write(f"- Latency: {rag_result.latency:.2f}s")

        if rag_result.retrieved_chunks:
            st.markdown("**Sources:**")
            sources = set(
                f"{c.source_document} (p.{c.page_number})"
                for c in rag_result.retrieved_chunks
            )
            for source in sources:
                st.write(f"- {source}")

    with col2:
        st.markdown("### 💭 Without RAG (Base Knowledge)")
        st.markdown("**Answer:**")
        st.info(no_rag_result.answer)

        st.markdown("**Metrics:**")
        st.write(f"- Tokens: {no_rag_result.tokens_used.get('total', 0)}")
        st.write(f"- Cost: ${no_rag_result.cost:.4f}")
        st.write(f"- Chunks: 0 (no retrieval)")
        st.write(f"- Latency: {no_rag_result.latency:.2f}s")

        st.markdown("**Note:**")
        st.write("No document context used - relies only on model's training data")

    # Analysis
    st.markdown("---")
    st.markdown("### 📊 Analysis")

    cost_diff = rag_result.cost - no_rag_result.cost
    time_diff = rag_result.latency - no_rag_result.latency

    st.markdown(f"""
    **RAG vs Non-RAG:**
    - RAG cost: **${rag_result.cost:.4f}** ({'+' if cost_diff >= 0 else ''}{cost_diff:.4f} vs non-RAG)
    - RAG time: **{rag_result.latency:.2f}s** ({'+' if time_diff >= 0 else ''}{time_diff:.2f}s vs non-RAG)
    - RAG uses **{len(rag_result.retrieved_chunks)} chunks** from your documents
    - Non-RAG uses **no context**, only the model's base knowledge

    **Key Takeaway:**
    RAG is more expensive and slower, but provides answers based on YOUR specific documents
    with verifiable sources. Non-RAG is cheaper and faster, but may not reflect your data.
    """)


def render_query_history(history: list):
    """
    Render query history.

    Args:
        history: List of (query, result) tuples
    """
    if not history:
        return

    st.markdown("---")
    st.markdown("### 📜 Query History")

    for i, (query, result) in enumerate(reversed(history[-5:]), 1):
        with st.expander(f"{i}. {query[:50]}..."):
            st.markdown(f"**Q:** {query}")
            st.markdown(f"**A:** {result.answer[:200]}...")
            st.write(f"Cost: ${result.cost:.4f}, Chunks: {len(result.retrieved_chunks)}")
