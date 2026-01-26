"""Streamlit UI for the Agentic RAG Research Assistant."""

import streamlit as st
from agent import AgenticRAG
import config
import os

# Page config
st.set_page_config(
    page_title="Agentic RAG Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = AgenticRAG()
    st.session_state.initialized = False
    st.session_state.chat_history = []

# Header
st.title("🤖 Truly Agentic RAG Research Assistant")
st.markdown("*An autonomous agent with self-evaluation and dynamic replanning*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    st.markdown(f"""
    **Model**: {config.LLM_MODEL}
    **Max Iterations**: {config.MAX_ITERATIONS}
    **Eval Threshold**: {config.EVALUATION_THRESHOLD}/10
    """)

    st.divider()

    st.header("📚 Knowledge Base")

    # Check if documents exist
    docs_exist = os.path.exists(config.DOCUMENTS_DIR) and \
                 len([f for f in os.listdir(config.DOCUMENTS_DIR) if not f.startswith('.')]) > 0

    if docs_exist:
        st.success(f"✓ Documents found in `{config.DOCUMENTS_DIR}`")
        doc_count = len([f for f in os.listdir(config.DOCUMENTS_DIR) if not f.startswith('.')])
        st.info(f"📄 {doc_count} file(s) available")
    else:
        st.warning(f"⚠️ No documents in `{config.DOCUMENTS_DIR}`")
        st.info("Add PDFs, .txt, or .md files to enable local search")

    if st.button("🔄 Initialize Knowledge Base", use_container_width=True):
        with st.spinner("Initializing..."):
            result = st.session_state.agent.initialize_knowledge_base()
            if result["status"] in ["success", "loaded"]:
                st.session_state.initialized = True
                st.success(result["message"])
            else:
                st.error(result["message"])

    if st.session_state.initialized:
        st.success("✓ Knowledge base ready")

    st.divider()

    st.header("ℹ️ About")
    st.markdown("""
    This agent autonomously:
    - 🧠 **Reasons** about information needs
    - 🔍 **Searches** local docs and web
    - ⚖️ **Evaluates** result quality
    - 🔄 **Adapts** strategy if needed
    - 📊 **Shows** its thinking process
    """)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
st.header("💬 Research Chat")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and "metadata" in message:
            # Show reasoning trace in expander
            with st.expander("🔍 View Agent's Reasoning Process"):
                metadata = message["metadata"]

                st.markdown(f"""
                **Iterations**: {metadata['iterations']}
                **Success**: {'✅ Yes' if metadata['success'] else '⚠️ Partial'}
                **Documents Retrieved**: {len(metadata['documents_used'])}
                """)

                st.divider()

                for trace in metadata['reasoning_trace']:
                    st.markdown(f"### 🔄 Iteration {trace['iteration']}")

                    st.markdown(f"**💭 Thought**")
                    st.info(trace['thought'])

                    st.markdown(f"**🎯 Action**")
                    st.code(f"Tool: {trace['tool']}\nQuery: {trace['query']}", language="text")

                    st.markdown(f"**👀 Observation**")
                    st.success(trace['observation'])

                    st.markdown(f"**🤔 Reflection**")
                    reflection_text = trace['reflection']
                    if 'evaluation_score' in trace:
                        reflection_text += f"\n\n**Score**: {trace['evaluation_score']}/10"
                        if trace.get('is_sufficient'):
                            reflection_text += " ✅ Sufficient!"
                        else:
                            reflection_text += " ❌ Need more information"
                    st.warning(reflection_text)

                    st.divider()

                # Show sources
                if metadata['documents_used']:
                    st.markdown("### 📄 Sources Used")
                    for i, doc in enumerate(metadata['documents_used'][:5], 1):
                        source = doc.get('metadata', {}).get('source', 'Unknown')
                        st.markdown(f"{i}. `{source}`")
                        with st.expander(f"View content"):
                            st.text(doc['content'][:500] + "...")

# Chat input
if prompt := st.chat_input("Ask a research question..."):
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent is researching..."):
            result = st.session_state.agent.research(prompt)

            st.markdown(result["answer"])

            # Store response with metadata
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["answer"],
                "metadata": result
            })

            # Auto-expand reasoning on first message
            if len(st.session_state.chat_history) <= 2:
                st.info("💡 Click 'View Agent's Reasoning Process' above to see how I found this answer!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
Made with ❤️ | Uses OpenAI GPT-4, ChromaDB, DuckDuckGo |
<a href='https://github.com' target='_blank'>View Code</a>
</div>
""", unsafe_allow_html=True)
