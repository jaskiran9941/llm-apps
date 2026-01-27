"""Streamlit UI for side-by-side RAG comparison: Traditional vs Corrective vs Agentic."""

import streamlit as st
import time
from traditional_rag import TraditionalRAG
from corrective_rag import CorrectiveRAG
from agent import AgenticRAG


def initialize_systems():
    """Initialize all three RAG systems."""
    if 'systems_initialized' not in st.session_state:
        with st.spinner("Initializing RAG systems..."):
            st.session_state.traditional_rag = TraditionalRAG()
            st.session_state.corrective_rag = CorrectiveRAG()
            st.session_state.agentic_rag = AgenticRAG()

            # Initialize knowledge base (shared across all)
            result = st.session_state.traditional_rag.initialize_knowledge_base()

            if result["status"] in ["loaded", "success"]:
                st.session_state.systems_initialized = True
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"⚠️ {result['message']}")
                st.session_state.systems_initialized = False


def format_time(seconds):
    """Format time in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.2f}s"


def render_traditional_results(result, execution_time):
    """Render Traditional RAG results."""
    st.markdown("### 📘 Traditional RAG")
    st.markdown("*Simple retrieve-then-generate (1 retrieval, no evaluation)*")

    if result:
        # Answer
        st.markdown("#### Answer")
        st.success(result["answer"])

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("LLM Calls", result.get("llm_calls", 1))
        with col2:
            st.metric("Retrievals", result.get("retrieval_count", 1))
        with col3:
            st.metric("Time", format_time(execution_time))

        # Documents
        with st.expander(f"📄 Retrieved Documents ({len(result.get('documents', []))})"):
            for i, doc in enumerate(result.get("documents", []), 1):
                st.markdown(f"**Document {i}**")
                st.text(doc["content"][:300] + "...")
                st.caption(f"Source: {doc.get('metadata', {}).get('source', 'Unknown')}")
                st.divider()


def render_corrective_results(result, execution_time):
    """Render Corrective RAG results."""
    st.markdown("### 🔧 Corrective RAG")
    st.markdown("*Retrieve → Grade → Correct if needed → Generate*")

    if result:
        # Answer
        st.markdown("#### Answer")
        st.success(result["answer"])

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("LLM Calls", result.get("llm_calls", 0))
        with col2:
            grade = result.get("final_grade", {})
            relevance = grade.get("relevance", "N/A")
            if relevance == "relevant":
                st.metric("Grade", "✅ Relevant")
            elif relevance == "ambiguous":
                st.metric("Grade", "⚠️ Ambiguous")
            else:
                st.metric("Grade", "❌ Not Relevant")
        with col3:
            st.metric("Time", format_time(execution_time))

        # Correction History
        with st.expander("🔍 Correction Process", expanded=True):
            for step in result.get("correction_history", []):
                if step["step"] == "initial_retrieval":
                    st.markdown(f"**Step 1: {step['action']}**")
                    st.info(f"Query: `{step['query']}`")
                    st.caption(f"Found {step.get('documents_found', 0)} documents")

                elif step["step"] == "grading":
                    st.markdown(f"**Step 2: {step['action']}**")
                    grade_emoji = {
                        "relevant": "✅",
                        "ambiguous": "⚠️",
                        "not_relevant": "❌"
                    }.get(step.get("grade", ""), "")

                    st.info(f"{grade_emoji} Grade: **{step.get('grade', 'N/A')}** (confidence: {step.get('confidence', 0):.2f})")
                    st.caption(f"Reason: {step.get('reason', 'N/A')}")
                    st.caption(f"Recommended action: {step.get('recommended_action', 'N/A')}")

                elif step["step"] == "corrective_action":
                    st.markdown(f"**Step 3: {step['action']}** 🔧")
                    if "rewritten_query" in step:
                        st.warning(f"Original: `{step['original_query']}`")
                        st.success(f"Rewritten: `{step['rewritten_query']}`")
                        st.caption(f"Found {step.get('documents_found', 0)} documents with new query")
                    elif "documents_found" in step:
                        st.caption(f"Found {step.get('documents_found', 0)} documents from web")

                elif step["step"] == "generation":
                    st.markdown(f"**Step 4: {step['action']}**")
                    st.caption(f"Using {step.get('documents_used', 0)} documents")

                st.divider()

        # Documents
        with st.expander(f"📄 Final Documents ({len(result.get('documents', []))})"):
            for i, doc in enumerate(result.get("documents", []), 1):
                st.markdown(f"**Document {i}**")
                st.text(doc["content"][:300] + "...")
                source = doc.get('metadata', {}).get('source') or doc.get('url', 'Unknown')
                st.caption(f"Source: {source}")
                st.divider()


def render_agentic_results(result, execution_time):
    """Render Agentic RAG results."""
    st.markdown("### 🤖 Agentic RAG")
    st.markdown("*Multi-iteration ReAct loop with self-evaluation*")

    if result:
        # Answer
        st.markdown("#### Answer")
        st.success(result["answer"])

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Iterations", result.get("iterations", 0))
        with col2:
            # Estimate LLM calls: plan + evaluate + generate for each iteration, + final generate
            llm_calls_estimate = result.get("iterations", 0) * 2 + 1
            st.metric("~LLM Calls", llm_calls_estimate)
        with col3:
            status = "✅ Success" if result.get("success") else "⚠️ Max Iterations"
            st.metric("Status", status)
        with col4:
            st.metric("Time", format_time(execution_time))

        # Reasoning Trace
        with st.expander("🧠 Reasoning Trace", expanded=True):
            for trace in result.get("reasoning_trace", []):
                st.markdown(f"**Iteration {trace['iteration']}**")

                st.markdown("*Thought:*")
                st.info(trace.get("thought", "N/A"))

                st.markdown("*Action:*")
                st.code(f"Tool: {trace.get('tool', 'N/A')}\nQuery: {trace.get('query', 'N/A')}")

                st.markdown("*Observation:*")
                st.caption(trace.get("observation", "N/A"))

                st.markdown("*Reflection:*")
                score = trace.get("evaluation_score", 0)
                is_sufficient = trace.get("is_sufficient", False)

                if is_sufficient:
                    st.success(f"✅ Score: {score}/10 - {trace.get('reflection', 'N/A')}")
                else:
                    st.warning(f"⚠️ Score: {score}/10 - {trace.get('reflection', 'N/A')}")

                st.divider()

        # Documents
        with st.expander(f"📄 All Retrieved Documents ({len(result.get('documents_used', []))})"):
            for i, doc in enumerate(result.get("documents_used", []), 1):
                st.markdown(f"**Document {i}**")
                st.text(doc["content"][:300] + "...")
                source = doc.get('metadata', {}).get('source') or doc.get('url', 'Unknown')
                st.caption(f"Source: {source}")
                st.divider()


def main():
    st.set_page_config(
        page_title="RAG Comparison: Traditional vs Corrective vs Agentic",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 RAG Approaches Comparison")
    st.markdown("""
    Compare three different RAG approaches side-by-side:
    - **Traditional RAG**: Simple retrieve-then-generate
    - **Corrective RAG (CRAG)**: Adds relevance grading and corrective actions
    - **Agentic RAG**: Full autonomous reasoning with multi-iteration refinement
    """)

    # Initialize systems
    initialize_systems()

    if not st.session_state.get('systems_initialized', False):
        st.warning("⚠️ Please add documents to the ./documents directory and restart the app")
        return

    st.divider()

    # Query Input
    st.markdown("### 💬 Enter Your Question")
    question = st.text_input(
        "Ask a question:",
        placeholder="e.g., What is the capital of France? or What are the key features of our product?",
        label_visibility="collapsed"
    )

    col1, col2, col3, col4 = st.columns([2, 2, 2, 6])

    with col1:
        run_all = st.button("🚀 Run All", type="primary", use_container_width=True)
    with col2:
        run_traditional = st.button("📘 Traditional", use_container_width=True)
    with col3:
        run_corrective = st.button("🔧 Corrective", use_container_width=True)
    with col4:
        run_agentic = st.button("🤖 Agentic", use_container_width=True)

    st.divider()

    # Results Display
    if run_all or run_traditional or run_corrective or run_agentic:
        if not question:
            st.error("Please enter a question first!")
            return

        # Create three columns for results
        col_trad, col_corr, col_agent = st.columns(3)

        # Traditional RAG
        if run_all or run_traditional:
            with col_trad:
                with st.spinner("Running Traditional RAG..."):
                    start = time.time()
                    trad_result = st.session_state.traditional_rag.answer(question)
                    trad_time = time.time() - start
                    st.session_state.trad_result = trad_result
                    st.session_state.trad_time = trad_time

        # Corrective RAG
        if run_all or run_corrective:
            with col_corr:
                with st.spinner("Running Corrective RAG..."):
                    start = time.time()
                    corr_result = st.session_state.corrective_rag.answer(question)
                    corr_time = time.time() - start
                    st.session_state.corr_result = corr_result
                    st.session_state.corr_time = corr_time

        # Agentic RAG
        if run_all or run_agentic:
            with col_agent:
                with st.spinner("Running Agentic RAG..."):
                    start = time.time()
                    agent_result = st.session_state.agentic_rag.research(question)
                    agent_time = time.time() - start
                    st.session_state.agent_result = agent_result
                    st.session_state.agent_time = agent_time

    # Display results if they exist
    col_trad, col_corr, col_agent = st.columns(3)

    with col_trad:
        if 'trad_result' in st.session_state:
            render_traditional_results(
                st.session_state.trad_result,
                st.session_state.trad_time
            )

    with col_corr:
        if 'corr_result' in st.session_state:
            render_corrective_results(
                st.session_state.corr_result,
                st.session_state.corr_time
            )

    with col_agent:
        if 'agent_result' in st.session_state:
            render_agentic_results(
                st.session_state.agent_result,
                st.session_state.agent_time
            )

    # Add footer with comparison insights
    if all(key in st.session_state for key in ['trad_result', 'corr_result', 'agent_result']):
        st.divider()
        st.markdown("### 📊 Quick Comparison")

        comp_col1, comp_col2, comp_col3 = st.columns(3)

        with comp_col1:
            st.metric(
                "Traditional RAG",
                f"{st.session_state.trad_time:.2f}s",
                delta="Fastest" if st.session_state.trad_time < st.session_state.corr_time else None
            )

        with comp_col2:
            st.metric(
                "Corrective RAG",
                f"{st.session_state.corr_time:.2f}s",
                delta="Balanced" if st.session_state.corr_time < st.session_state.agent_time else None
            )

        with comp_col3:
            st.metric(
                "Agentic RAG",
                f"{st.session_state.agent_time:.2f}s",
                delta="Most Thorough"
            )


if __name__ == "__main__":
    main()
