"""
Production LLM Memory Application
Clean, functional chatbot with memory capabilities
"""

import streamlit as st
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import core components
from llm.claude_wrapper import ClaudeWrapper
from memory.episodic import EpisodicMemory
from memory.semantic_simple import SimpleSemanticMemory

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="LLM Memory Chat",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.episodic_with = EpisodicMemory()
    st.session_state.episodic_without = EpisodicMemory()
    st.session_state.semantic = SimpleSemanticMemory()
    st.session_state.chat_with = []
    st.session_state.chat_without = []
    st.session_state.kb_loaded = False
    st.session_state.initialized = True

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")

    # API Key check
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("sk-ant-demo"):
        st.error("⚠️ No valid API key found")
        api_key_input = st.text_input("Enter Anthropic API Key", type="password")
        if api_key_input:
            api_key = api_key_input
    else:
        st.success("✅ API Key loaded")

    st.markdown("---")

    # Knowledge Base
    st.subheader("📚 Knowledge Base")

    sample_docs_path = Path("knowledge_base/sample_docs")
    doc_files = list(sample_docs_path.glob("*.txt")) if sample_docs_path.exists() else []

    if not st.session_state.kb_loaded:
        if not doc_files:
            st.info("No documents found in knowledge_base/sample_docs/")
            st.caption("Add .txt files to enable document loading")
        else:
            if st.button("Load Documents", type="primary"):
                with st.spinner("Indexing documents..."):
                    try:
                        loaded = 0
                        for doc_file in doc_files:
                            with open(doc_file, 'r') as f:
                                content = f.read()
                                st.session_state.semantic.add_document(
                                    document_text=content,
                                    document_name=doc_file.stem,
                                    metadata={"source": str(doc_file)}
                                )
                                loaded += 1
                        st.session_state.kb_loaded = True
                        st.success(f"✅ Loaded {loaded} documents")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading documents: {str(e)}")
    else:
        docs = st.session_state.semantic.get_all_documents()
        st.success(f"✅ {len(docs)} documents indexed")

        if st.button("Clear Knowledge Base"):
            st.session_state.semantic.clear()
            st.session_state.kb_loaded = False
            st.rerun()

    st.markdown("---")

    # Settings
    st.subheader("🎛️ Settings")

    max_history = st.slider("Conversation history", 3, 20, 10)
    top_k = st.slider("Documents to retrieve", 1, 10, 3)
    similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.7, 0.05)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

    # Update memory settings
    st.session_state.episodic_with.max_history = max_history

    st.markdown("---")

    # Reset
    if st.button("🔄 Reset Conversations"):
        st.session_state.episodic_with.clear()
        st.session_state.episodic_without.clear()
        st.session_state.chat_with = []
        st.session_state.chat_without = []
        st.rerun()

    st.markdown("---")

    # Memory Viewer
    st.subheader("🔍 Memory Viewer")

    with st.expander("Episodic Memory (Conversation History)"):
        turns = st.session_state.episodic_with.get_turns()
        if turns:
            for i, turn in enumerate(turns):
                st.markdown(f"**Turn {i+1}** - {turn['timestamp'][:19]}")
                st.markdown(f"👤 {turn['user_message'][:100]}...")
                st.markdown(f"🤖 {turn['assistant_response'][:100]}...")
                st.caption(f"Tokens: {turn['tokens_used']}")
                st.markdown("---")
        else:
            st.caption("No conversation history yet")

    with st.expander("Semantic Memory (Knowledge Base)"):
        if st.session_state.kb_loaded:
            docs = st.session_state.semantic.get_all_documents()
            st.markdown(f"**{len(docs)} documents indexed**")
            for doc in docs:
                st.markdown(f"• **{doc['name']}** ({doc['chunks']} chunks)")

            st.markdown("---")
            st.markdown("**Stored Chunks:**")
            for i, (chunk, meta) in enumerate(zip(
                st.session_state.semantic.chunks[:10],
                st.session_state.semantic.metadata[:10]
            )):
                st.caption(f"[{meta['document_name']}] {chunk[:80]}...")
            if len(st.session_state.semantic.chunks) > 10:
                st.caption(f"... and {len(st.session_state.semantic.chunks) - 10} more chunks")
        else:
            st.caption("No documents loaded")

# Main content
st.title("🤖 LLM Memory Chat")

# Two columns for comparison
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧠 WITH Memory")
    st.caption("Uses conversation history + knowledge base")

with col2:
    st.markdown("### 💬 WITHOUT Memory")
    st.caption("Each message is independent")

# Display chats
with col1:
    for msg in st.session_state.chat_with:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            if msg['role'] == 'assistant' and msg.get('metadata'):
                if msg['metadata'].get('retrieved_docs'):
                    with st.expander("📎 Sources"):
                        for doc in msg['metadata'].get('retrieved_docs', []):
                            st.caption(f"• {doc['metadata']['document_name']} (similarity: {doc['similarity']:.2f})")

                # Debug: Show what was sent to LLM
                with st.expander("🔬 Debug: What was sent to Claude"):
                    st.markdown("**Conversation History (Episodic Memory):**")
                    debug_history = msg['metadata'].get('history', [])
                    if debug_history:
                        for h_msg in debug_history:
                            role_icon = "👤" if h_msg['role'] == 'user' else "🤖"
                            content = h_msg['content']
                            st.markdown(f"{role_icon} **{h_msg['role']}**: {content[:200]}{'...' if len(content) > 200 else ''}")
                    else:
                        st.caption("No conversation history")

                    st.markdown("---")
                    st.markdown("**Retrieved Context (Semantic Memory):**")
                    debug_context = msg['metadata'].get('retrieved_context', '')
                    if debug_context:
                        st.text(debug_context[:500] + "..." if len(debug_context) > 500 else debug_context)
                    else:
                        st.caption("No context retrieved")

with col2:
    for msg in st.session_state.chat_without:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

# Input
user_input = st.chat_input("Ask a question...")

if user_input and api_key:
    # Add user message to both
    st.session_state.chat_with.append({"role": "user", "content": user_input})
    st.session_state.chat_without.append({"role": "user", "content": user_input})

    # Initialize Claude
    claude = ClaudeWrapper(api_key=api_key)

    # WITH MEMORY - Left side
    with col1:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get conversation history
                history = st.session_state.episodic_with.get_conversation_history()

                # Retrieve from knowledge base
                retrieved_context = ""
                retrieval_details = []

                if st.session_state.kb_loaded:
                    retrieved_context, retrieval_details = st.session_state.semantic.retrieve(
                        query=user_input,
                        top_k=top_k,
                        similarity_threshold=similarity_threshold
                    )

                # Generate response
                try:
                    response = claude.generate_response(
                        user_message=user_input,
                        conversation_history=history,
                        retrieved_context=retrieved_context,
                        temperature=temperature
                    )

                    st.markdown(response['response'])

                    # Show sources
                    if retrieval_details:
                        with st.expander("📎 Sources"):
                            for doc in retrieval_details:
                                st.caption(f"• {doc['metadata']['document_name']} (similarity: {doc['similarity']:.2f})")

                    # Debug: Show what was sent to LLM
                    with st.expander("🔬 Debug: What was sent to Claude"):
                        st.markdown("**Conversation History (Episodic Memory):**")
                        if history:
                            for i, msg in enumerate(history):
                                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                                st.markdown(f"{role_icon} **{msg['role']}**: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
                        else:
                            st.caption("No conversation history")

                        st.markdown("---")
                        st.markdown("**Retrieved Context (Semantic Memory):**")
                        if retrieved_context:
                            st.text(retrieved_context[:500] + "..." if len(retrieved_context) > 500 else retrieved_context)
                        else:
                            st.caption("No context retrieved")

                    # Update memory
                    st.session_state.episodic_with.add_turn(
                        user_input,
                        response['response'],
                        response['tokens_used']
                    )

                    # Add to chat
                    st.session_state.chat_with.append({
                        "role": "assistant",
                        "content": response['response'],
                        "metadata": {
                            "retrieved_docs": retrieval_details,
                            "tokens": response['tokens_used'],
                            "history": history,
                            "retrieved_context": retrieved_context
                        }
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # WITHOUT MEMORY - Right side
    with col2:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = claude.generate_without_memory(
                        user_message=user_input,
                        temperature=temperature
                    )

                    st.markdown(response['response'])

                    # Update memory (for display only)
                    st.session_state.episodic_without.add_turn(
                        user_input,
                        response['response'],
                        response['tokens_used']
                    )

                    # Add to chat
                    st.session_state.chat_without.append({
                        "role": "assistant",
                        "content": response['response']
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.rerun()

elif user_input and not api_key:
    st.error("⚠️ Please enter your Anthropic API key in the sidebar")

# Stats at bottom
if st.session_state.chat_with:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_turns = len(st.session_state.episodic_with)
        st.metric("Conversation Turns", total_turns)

    with col2:
        total_tokens = st.session_state.episodic_with.get_total_tokens()
        st.metric("Total Tokens (WITH)", f"{total_tokens:,}")

    with col3:
        if st.session_state.kb_loaded:
            stats = st.session_state.semantic.get_embedding_stats()
            st.metric("Indexed Chunks", stats['total_chunks'])
