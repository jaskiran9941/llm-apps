"""Simplified Streamlit UI for Agentic RAG (without ChromaDB dependency)."""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Agentic RAG Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# Check for API key
api_key = os.getenv("OPENAI_API_KEY")

# Header
st.title("🤖 Truly Agentic RAG Research Assistant")
st.markdown("*An autonomous agent with self-evaluation and dynamic replanning*")

# Check API key
if not api_key or api_key == "your-openai-api-key-here":
    st.error("⚠️ OpenAI API key not configured!")
    st.markdown("""
    **To get started:**

    1. Open the `.env` file in this directory
    2. Replace `your-openai-api-key-here` with your actual OpenAI API key
    3. Restart this app

    Get your API key from: https://platform.openai.com/api-keys
    """)
    st.code("""
# In .env file:
OPENAI_API_KEY=sk-your-actual-key-here
    """, language="bash")
    st.stop()

# Import agent only after API key check
try:
    from agent_simple import AgenticRAG
    agent = AgenticRAG()
except ImportError:
    st.error("Missing dependencies. Installing basic packages...")
    st.stop()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    st.markdown("""
    **Model**: GPT-4o-mini
    **Max Iterations**: 3
    **Eval Threshold**: 7/10
    """)

    st.divider()

    st.header("ℹ️ About")
    st.markdown("""
    This agent autonomously:
    - 🧠 **Reasons** about information needs
    - 🔍 **Searches** the web intelligently
    - ⚖️ **Evaluates** result quality
    - 🔄 **Adapts** strategy if needed
    - 📊 **Shows** its thinking process

    **Note**: This simplified version uses web search only.
    For full features with local document search, install:
    ```
    pip install chromadb langchain langchain-openai
    ```
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
                        source = doc.get('url', 'Unknown')
                        title = doc.get('metadata', {}).get('title', 'Untitled')
                        st.markdown(f"{i}. [{title}]({source})")

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
            result = agent.research(prompt)

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
Made with ❤️ | Uses OpenAI GPT-4o-mini, DuckDuckGo | Truly Agentic RAG Demo
</div>
""", unsafe_allow_html=True)
