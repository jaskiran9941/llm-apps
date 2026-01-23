import streamlit as st
import os
from pathlib import Path

# Import our modules
from config.config import PAGE_TITLE, PAGE_ICON, AVAILABLE_MODELS
from llm.claude_wrapper import ClaudeWrapper
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.working import WorkingMemory
from visualizers.embedding_viz import EmbeddingVisualizer
from visualizers.retrieval_viz import RetrievalVisualizer
from visualizers.token_viz import TokenVisualizer
from utils.ui_components import UIComponents
from utils.demo_scenarios import DemoScenarios

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables."""
    if 'initialized' not in st.session_state:
        # Memory systems
        st.session_state.episodic_with = EpisodicMemory()
        st.session_state.episodic_without = EpisodicMemory()
        st.session_state.semantic = SemanticMemory()
        st.session_state.working = WorkingMemory()

        # Chat history (for display)
        st.session_state.chat_with = []
        st.session_state.chat_without = []

        # Statistics
        st.session_state.total_retrievals = 0
        st.session_state.tokens_with = 0
        st.session_state.tokens_without = 0

        # Knowledge base loaded flag
        st.session_state.kb_loaded = False

        st.session_state.initialized = True

init_session_state()

# Sidebar
st.sidebar.title("🧠 LLM Memory Platform")

# Settings
settings = UIComponents.show_settings_panel()

# Load knowledge base button
if not st.session_state.kb_loaded:
    if st.sidebar.button("📚 Load Sample Knowledge Base", type="primary"):
        with st.spinner("Loading documents..."):
            # Load all sample documents
            sample_docs_path = Path("knowledge_base/sample_docs")
            loaded_count = 0

            for doc_file in sample_docs_path.glob("*.txt"):
                with open(doc_file, 'r') as f:
                    content = f.read()
                    st.session_state.semantic.add_document(
                        document_text=content,
                        document_name=doc_file.stem,
                        metadata={"source": str(doc_file)}
                    )
                    loaded_count += 1

            st.session_state.kb_loaded = True
            st.sidebar.success(f"✅ Loaded {loaded_count} documents!")
            st.rerun()
else:
    st.sidebar.success("✅ Knowledge Base Loaded")

    # Option to clear KB
    if st.sidebar.button("🗑️ Clear Knowledge Base"):
        st.session_state.semantic.clear()
        st.session_state.kb_loaded = False
        st.rerun()

# Demo scenarios
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎮 Demo Scenarios")
scenario_names = ["Select a scenario..."] + list(DemoScenarios.get_all_scenarios().keys())
selected_scenario = st.sidebar.selectbox(
    "Try a pre-built scenario",
    options=scenario_names,
    format_func=lambda x: DemoScenarios.get_all_scenarios().get(x, {}).get('name', x) if x != "Select a scenario..." else x
)

if selected_scenario != "Select a scenario...":
    scenario = DemoScenarios.get_scenario_by_key(selected_scenario)
    st.sidebar.markdown(f"**{scenario['name']}**")
    st.sidebar.markdown(f"_{scenario['description']}_")

    for i, msg in enumerate(scenario['messages']):
        if st.sidebar.button(f"▶️ Send: {msg[:30]}...", key=f"scenario_{i}"):
            # This will be handled in the comparison tab
            st.session_state.scenario_message = msg

# Quick questions
st.sidebar.markdown("---")
st.sidebar.markdown("### ❓ Quick Questions")
quick_questions = DemoScenarios.get_quick_questions()
for i, question in enumerate(quick_questions[:5]):
    if st.sidebar.button(f"💬 {question}", key=f"quick_{i}"):
        st.session_state.scenario_message = question

# Memory statistics
semantic_stats = st.session_state.semantic.get_embedding_stats()
UIComponents.show_memory_stats(
    episodic_turns=len(st.session_state.episodic_with),
    episodic_tokens=st.session_state.tokens_with,
    semantic_chunks=semantic_stats['total_chunks'],
    total_retrievals=st.session_state.total_retrievals
)

# Reset button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset All Conversations"):
    st.session_state.episodic_with.clear()
    st.session_state.episodic_without.clear()
    st.session_state.chat_with = []
    st.session_state.chat_without = []
    st.session_state.tokens_with = 0
    st.session_state.tokens_without = 0
    st.rerun()

# Main content - Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Side-by-Side Comparison",
    "📚 Memory Deep Dives",
    "⚙️ Memory Internals",
    "🛝 Playground"
])

# TAB 1: Side-by-Side Comparison
with tab1:
    st.title("🔍 WITH Memory vs WITHOUT Memory")
    st.markdown("Ask the same question to both chatbots and see the difference!")

    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("⚠️ ANTHROPIC_API_KEY not found in environment variables. Please set it in a .env file.")
        st.stop()

    # Initialize Claude wrapper
    claude = ClaudeWrapper(model=AVAILABLE_MODELS[settings['model']])

    # Create two columns for comparison
    col_with, col_without = st.columns(2)

    with col_with:
        st.markdown("### 🧠 WITH Memory")
        st.markdown("Uses episodic + semantic memory")

    with col_without:
        st.markdown("### 🤖 WITHOUT Memory")
        st.markdown("No context, no knowledge base")

    # Display chat history
    with col_with:
        st.markdown("#### Chat History")
        for msg in st.session_state.chat_with:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

    with col_without:
        st.markdown("#### Chat History")
        for msg in st.session_state.chat_without:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])

    # Input area
    user_question = st.text_input(
        "Your question:",
        placeholder="Try: 'How many vacation days do I get?' or 'Can I work remotely?'",
        key="comparison_input"
    )

    # Check if scenario message is set
    if 'scenario_message' in st.session_state:
        user_question = st.session_state.scenario_message
        del st.session_state.scenario_message

    if st.button("Send to Both", type="primary") and user_question:
        # Add user message to both chats
        st.session_state.chat_with.append({"role": "user", "content": user_question})
        st.session_state.chat_without.append({"role": "user", "content": user_question})

        # WITH MEMORY
        with col_with:
            with st.spinner("Thinking with memory..."):
                # Get conversation history
                history = st.session_state.episodic_with.get_conversation_history()

                # Retrieve relevant context
                retrieved_context, retrieval_details = st.session_state.semantic.retrieve(
                    query=user_question,
                    top_k=settings['top_k'],
                    similarity_threshold=settings['similarity_threshold']
                )

                if retrieved_context:
                    st.session_state.total_retrievals += 1

                # Generate response
                response_with = claude.generate_response(
                    user_message=user_question,
                    conversation_history=history,
                    retrieved_context=retrieved_context,
                    temperature=settings['temperature']
                )

                # Display response
                with st.chat_message("assistant"):
                    st.markdown(response_with['response'])

                # Show what memory was used
                with st.expander("🔍 Memory Used"):
                    st.markdown("**Retrieved Context:**")
                    if retrieval_details:
                        for detail in retrieval_details:
                            st.markdown(f"- {detail['metadata']['document_name']} (similarity: {detail['similarity']:.3f})")
                    else:
                        st.info("No relevant documents retrieved")

                    st.markdown(f"**Conversation History:** {len(history)//2} turns")

                # Update memory and chat
                st.session_state.episodic_with.add_turn(
                    user_question,
                    response_with['response'],
                    response_with['tokens_used']
                )
                st.session_state.chat_with.append({
                    "role": "assistant",
                    "content": response_with['response']
                })
                st.session_state.tokens_with += response_with['tokens_used']

        # WITHOUT MEMORY
        with col_without:
            with st.spinner("Thinking without memory..."):
                response_without = claude.generate_without_memory(
                    user_message=user_question,
                    temperature=settings['temperature']
                )

                # Display response
                with st.chat_message("assistant"):
                    st.markdown(response_without['response'])

                # Update memory and chat
                st.session_state.episodic_without.add_turn(
                    user_question,
                    response_without['response'],
                    response_without['tokens_used']
                )
                st.session_state.chat_without.append({
                    "role": "assistant",
                    "content": response_without['response']
                })
                st.session_state.tokens_without += response_without['tokens_used']

        st.rerun()

    # Token comparison at bottom
    if st.session_state.tokens_with > 0:
        st.markdown("---")
        TokenVisualizer.show_token_comparison(
            st.session_state.tokens_with,
            st.session_state.tokens_without
        )

# TAB 2: Memory Deep Dives
with tab2:
    st.title("📚 Memory Type Deep Dives")

    memory_type = st.selectbox(
        "Choose memory type to explore:",
        ["Episodic Memory", "Semantic Memory", "Working Memory"]
    )

    if memory_type == "Episodic Memory":
        st.markdown("## 💬 Episodic Memory Explorer")
        UIComponents.show_concept_explanation("episodic")

        st.markdown("---")
        st.markdown("### Current Conversation (WITH Memory)")

        turns = st.session_state.episodic_with.get_turns()
        if turns:
            # Show conversation timeline
            for i, turn in enumerate(turns, 1):
                with st.expander(f"Turn {i} - {turn['timestamp'][:19]}"):
                    st.markdown(f"**User:** {turn['user_message']}")
                    st.markdown(f"**Assistant:** {turn['assistant_response']}")
                    st.markdown(f"**Tokens:** {turn['tokens_used']}")

            # Token visualization
            st.markdown("---")
            TokenVisualizer.show_context_window(turns)

            # Sliding window demo
            st.markdown("---")
            TokenVisualizer.show_sliding_window_demo(turns, settings['max_history'])
        else:
            st.info("No conversation yet. Try the Side-by-Side Comparison tab!")

    elif memory_type == "Semantic Memory":
        st.markdown("## 📚 Semantic Memory Explorer")
        UIComponents.show_concept_explanation("semantic")

        if not st.session_state.kb_loaded:
            st.warning("⚠️ Knowledge base not loaded. Click 'Load Sample Knowledge Base' in the sidebar.")
        else:
            st.markdown("---")
            st.markdown("### Knowledge Base Contents")

            # Show indexed documents
            docs = st.session_state.semantic.get_all_documents()
            st.markdown(f"**Total Documents:** {len(docs)}")

            for doc in docs:
                with st.expander(f"📄 {doc['name']} ({doc['chunks']} chunks)"):
                    st.json(doc['metadata'])

            # Interactive retrieval test
            st.markdown("---")
            st.markdown("### 🔍 Test Retrieval")

            test_query = st.text_input(
                "Enter a test query:",
                placeholder="e.g., 'How many vacation days?'"
            )

            if test_query:
                retrieved_context, retrieval_details = st.session_state.semantic.retrieve(
                    query=test_query,
                    top_k=settings['top_k'],
                    similarity_threshold=settings['similarity_threshold']
                )

                RetrievalVisualizer.show_retrieval_process(retrieval_details)

                # Show embedding visualization
                if retrieval_details:
                    st.markdown("---")
                    st.markdown("### 📊 Embedding Space Visualization")

                    # Get all chunk embeddings
                    all_results = st.session_state.semantic.collection.get(include=['embeddings', 'documents', 'metadatas'])

                    if all_results['embeddings']:
                        chunk_embeddings = all_results['embeddings']
                        chunk_labels = [meta['document_name'] for meta in all_results['metadatas']]
                        chunk_contents = all_results['documents']

                        # Get query embedding
                        query_embedding = st.session_state.semantic.embedding_model.encode(test_query).tolist()

                        # Get indices of retrieved chunks
                        retrieved_ids = [d['chunk_id'] for d in retrieval_details]
                        retrieval_indices = [all_results['ids'].index(rid) for rid in retrieved_ids if rid in all_results['ids']]
                        similarities = [d['similarity'] for d in retrieval_details]

                        # Create visualization
                        fig = EmbeddingVisualizer.create_2d_plot(
                            chunk_embeddings=chunk_embeddings,
                            chunk_labels=chunk_labels,
                            chunk_contents=chunk_contents,
                            query_embedding=query_embedding,
                            query_text=test_query,
                            retrieval_indices=retrieval_indices,
                            similarities=similarities,
                            method="pca"
                        )

                        st.plotly_chart(fig, use_container_width=True)

    elif memory_type == "Working Memory":
        st.markdown("## 🧠 Working Memory Explorer")
        UIComponents.show_concept_explanation("working")

        st.markdown("---")
        st.info("Working memory (chain-of-thought) is demonstrated through the reasoning process of the LLM. Try asking complex questions in the comparison tab to see multi-step reasoning.")

# TAB 3: Memory Internals
with tab3:
    st.title("⚙️ How Memory Works: Step-by-Step")

    st.markdown("""
    This section breaks down the RAG (Retrieval Augmented Generation) process into digestible steps.
    """)

    # Step selector
    step = st.slider("Select Step", min_value=1, max_value=5, value=1, step=1)

    RetrievalVisualizer.show_step_by_step_animation(step)

    st.markdown("---")

    # Show prompt assembly if we have a recent query
    if st.session_state.chat_with:
        st.markdown("### 🎯 Example: Complete Prompt Assembly")

        last_user_msg = None
        for msg in reversed(st.session_state.chat_with):
            if msg['role'] == 'user':
                last_user_msg = msg['content']
                break

        if last_user_msg:
            # Get what would be retrieved
            retrieved_context, retrieval_details = st.session_state.semantic.retrieve(
                query=last_user_msg,
                top_k=settings['top_k'],
                similarity_threshold=settings['similarity_threshold']
            )

            # Get conversation history
            history = st.session_state.episodic_with.get_conversation_history()

            # Show prompt assembly
            RetrievalVisualizer.show_prompt_assembly(
                system_prompt="You are a helpful assistant.",
                retrieved_context=retrieved_context,
                conversation_history=history[:-2] if len(history) >= 2 else [],  # Exclude the last turn
                current_question=last_user_msg
            )

# TAB 4: Playground
with tab4:
    st.title("🛝 Memory Playground")
    st.markdown("Experiment with memory settings and see their impact!")

    st.markdown("### 🎛️ Experiment Controls")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Memory Toggles:**")
        use_episodic = st.checkbox("Use Episodic Memory", value=True)
        use_semantic = st.checkbox("Use Semantic Memory", value=True)

    with col2:
        st.markdown("**Retrieval Parameters:**")
        playground_top_k = st.slider("Top-K", 1, 10, 3, key="playground_topk")
        playground_threshold = st.slider("Threshold", 0.0, 1.0, 0.7, 0.05, key="playground_threshold")

    st.markdown("---")

    # Query input
    playground_query = st.text_area(
        "Test Query:",
        placeholder="Ask a question to see how different settings affect the response..."
    )

    if st.button("🚀 Test Query", type="primary") and playground_query:
        if not os.getenv("ANTHROPIC_API_KEY"):
            st.error("⚠️ ANTHROPIC_API_KEY not set")
        else:
            claude_playground = ClaudeWrapper(model=AVAILABLE_MODELS[settings['model']])

            # Configure memory based on toggles
            history = st.session_state.episodic_with.get_conversation_history() if use_episodic else None
            retrieved_context = None

            if use_semantic and st.session_state.kb_loaded:
                retrieved_context, retrieval_details = st.session_state.semantic.retrieve(
                    query=playground_query,
                    top_k=playground_top_k,
                    similarity_threshold=playground_threshold
                )

            # Generate response
            with st.spinner("Generating..."):
                response = claude_playground.generate_response(
                    user_message=playground_query,
                    conversation_history=history,
                    retrieved_context=retrieved_context,
                    temperature=settings['temperature']
                )

            # Display results
            st.markdown("### 💬 Response")
            st.markdown(response['response'])

            # Show what was used
            st.markdown("### 📊 Memory Usage")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Episodic Memory",
                    f"{len(history)//2 if history else 0} turns",
                    delta="Active" if use_episodic else "Disabled"
                )

            with col2:
                chunks_retrieved = len(retrieval_details) if use_semantic and 'retrieval_details' in locals() else 0
                st.metric(
                    "Semantic Memory",
                    f"{chunks_retrieved} chunks",
                    delta="Active" if use_semantic else "Disabled"
                )

            with col3:
                st.metric("Tokens Used", f"{response['tokens_used']:,}")

            # Show retrieval details if semantic memory was used
            if use_semantic and 'retrieval_details' in locals() and retrieval_details:
                st.markdown("### 🔍 Retrieved Chunks")
                RetrievalVisualizer.show_retrieval_process(retrieval_details)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🧠 LLM Memory Learning Platform | Built with Streamlit & Claude |
    <a href='https://github.com/anthropics/claude-code'>Learn More</a></p>
</div>
""", unsafe_allow_html=True)
