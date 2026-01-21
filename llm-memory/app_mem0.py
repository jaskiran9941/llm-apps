"""
Production LLM Application with Mem0
Using Mem0 for managed memory layer
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Note: Install with: pip install mem0ai anthropic

try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False

from anthropic import Anthropic

load_dotenv()

# Page config
st.set_page_config(
    page_title="LLM Chat with Mem0",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.messages = []
    st.session_state.user_id = "user_1"  # In production, this would be actual user ID
    st.session_state.initialized = True

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")

    # API Keys
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("sk-ant-demo"):
        st.error("⚠️ No valid API key")
        api_key = st.text_input("Anthropic API Key", type="password")
    else:
        st.success("✅ API Key loaded")

    st.markdown("---")

    # Mem0 status
    st.subheader("🧠 Mem0 Memory")

    if MEM0_AVAILABLE:
        st.success("✅ Mem0 installed")

        # Initialize Mem0
        if 'memory' not in st.session_state and api_key:
            try:
                config = {
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "collection_name": "mem0_chat",
                            "path": "./chroma_mem0"
                        }
                    }
                }
                st.session_state.memory = Memory.from_config(config)
                st.info("Mem0 initialized")
            except Exception as e:
                st.error(f"Mem0 init error: {str(e)}")

        # Memory management
        if st.button("View Memories"):
            if 'memory' in st.session_state:
                try:
                    memories = st.session_state.memory.get_all(user_id=st.session_state.user_id)
                    if memories:
                        st.json(memories)
                    else:
                        st.info("No memories stored yet")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if st.button("Clear Memories"):
            if 'memory' in st.session_state:
                try:
                    st.session_state.memory.delete_all(user_id=st.session_state.user_id)
                    st.success("Memories cleared")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠️ Mem0 not installed")
        st.code("pip install mem0ai", language="bash")

    st.markdown("---")

    # Settings
    st.subheader("🎛️ Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max tokens", 256, 2048, 1024, 256)

    st.markdown("---")

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("🧠 LLM Chat with Mem0 Memory")

if not MEM0_AVAILABLE:
    st.error("❌ Mem0 is not installed. Install with: `pip install mem0ai`")
    st.stop()

if not api_key:
    st.warning("⚠️ Please enter your Anthropic API key in the sidebar")
    st.stop()

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
        if msg.get('memories'):
            with st.expander("🧠 Memories used"):
                for memory in msg['memories']:
                    st.caption(f"• {memory}")

# Chat input
user_input = st.chat_input("Ask anything...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Initialize clients
                client = Anthropic(api_key=api_key)
                memory = st.session_state.memory

                # Search relevant memories
                relevant_memories = memory.search(
                    query=user_input,
                    user_id=st.session_state.user_id
                )

                # Build context from memories
                memory_context = ""
                memory_list = []
                if relevant_memories:
                    memory_context = "\n\nRelevant context from previous conversations:\n"
                    for mem in relevant_memories:
                        memory_text = mem.get('memory', '')
                        memory_context += f"- {memory_text}\n"
                        memory_list.append(memory_text)

                # Create prompt with memory context
                system_prompt = f"""You are a helpful assistant with access to conversation history.
{memory_context}

Use the above context when relevant to provide personalized, contextual responses."""

                # Call Claude
                response = client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_input}]
                )

                assistant_response = response.content[0].text
                st.markdown(assistant_response)

                # Store this interaction in Mem0
                memory.add(
                    messages=[
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": assistant_response}
                    ],
                    user_id=st.session_state.user_id
                )

                # Show which memories were used
                if memory_list:
                    with st.expander("🧠 Memories used"):
                        for mem in memory_list:
                            st.caption(f"• {mem}")

                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "memories": memory_list
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

    st.rerun()

# Info panel
with st.expander("ℹ️ About Mem0"):
    st.markdown("""
    **Mem0** is a memory layer for LLMs that:

    - **Automatically extracts** key information from conversations
    - **Stores memories** in a vector database
    - **Retrieves relevant context** when needed
    - **Manages memory lifecycle** (update, delete, expire)

    **Key Features:**
    - Persistent memory across sessions
    - Semantic search for relevant context
    - User-specific memory isolation
    - Automatic memory categorization

    **Comparison:**
    - **Custom RAG**: Full control, manual document management
    - **Mem0**: Automated, conversation-focused, managed memory
    """)
