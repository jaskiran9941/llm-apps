"""
Memory-Based Chatbot Application
A personalized chatbot with persistent memory using OpenAI GPT-4o, Mem0, and Qdrant.
"""

import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
from config import get_config
from memory_manager import create_memory_manager


# Page configuration
st.set_page_config(
    page_title="Memory-Based Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = None
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = None


def setup_configuration():
    """Set up and validate configuration."""
    if st.session_state.config is None:
        st.session_state.config = get_config()

    config = st.session_state.config

    # API Key input in sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        api_key_input = st.text_input(
            "OpenAI API Key",
            value=config.openai_api_key if config.openai_api_key else "",
            type="password",
            help="Enter your OpenAI API key. It will be stored only for this session."
        )

        if api_key_input:
            config.update_api_key(api_key_input)

        # Validate configuration
        is_valid, error_msg = config.validate()

        if not is_valid:
            st.error(f"❌ {error_msg}")
            st.info("💡 Get your API key from: https://platform.openai.com/api-keys")
            return False

        st.success("✅ Configuration valid")

        # Model selection
        selected_model = st.selectbox(
            "Model",
            options=config.available_models,
            index=config.available_models.index(config.default_model),
            help="Select the OpenAI model to use"
        )
        config.update_model(selected_model)

        return True


def initialize_memory_manager():
    """Initialize the memory manager if not already initialized."""
    if st.session_state.memory_manager is None:
        try:
            config = st.session_state.config
            mem_config = {
                'qdrant_host': config.qdrant_host,
                'qdrant_port': config.qdrant_port,
                'collection_name': config.collection_name
            }
            st.session_state.memory_manager = create_memory_manager(mem_config)
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize memory system: {str(e)}")
            st.info("💡 Make sure Qdrant is running: `docker-compose up -d`")
            return False
    return True


def initialize_openai_client():
    """Initialize OpenAI client if not already initialized."""
    if st.session_state.openai_client is None:
        try:
            config = st.session_state.config
            st.session_state.openai_client = OpenAI(api_key=config.openai_api_key)
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
            return False
    return True


def get_user_id():
    """Get or set the user ID."""
    if st.session_state.user_id is None:
        with st.sidebar:
            st.divider()
            st.subheader("👤 User Identity")
            user_input = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Each user has separate memory storage"
            )

            if user_input:
                st.session_state.user_id = user_input.strip()
                st.success(f"✅ Logged in as: {st.session_state.user_id}")
                return True
            else:
                st.warning("⚠️ Please enter a username to continue")
                return False
    return True


def display_chat_interface():
    """Display the main chat interface."""
    st.title("🧠 Memory-Based Chatbot")
    st.markdown(
        "A personalized AI assistant that remembers your conversations and preferences."
    )

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show retrieved memories if available
            if message["role"] == "assistant" and "memories" in message:
                with st.expander("📚 Retrieved Memories", expanded=False):
                    if message["memories"]:
                        for idx, memory in enumerate(message["memories"], 1):
                            memory_text = memory.get('memory', 'N/A')
                            st.markdown(f"**{idx}.** {memory_text}")
                    else:
                        st.info("No relevant memories found")


def process_user_message(user_message: str):
    """
    Process user message: retrieve memories, generate response, store new memory.

    Args:
        user_message: The user's input message
    """
    memory_manager = st.session_state.memory_manager
    user_id = st.session_state.user_id
    config = st.session_state.config
    openai_client = st.session_state.openai_client

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_message})

    with st.chat_message("user"):
        st.markdown(user_message)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Step 1: Search for relevant memories
            relevant_memories = memory_manager.search_memories(
                query=user_message,
                user_id=user_id,
                limit=config.default_top_k
            )

            # Step 2: Build context from memories
            context = ""
            if relevant_memories:
                context = "Relevant information from previous conversations:\n"
                for memory in relevant_memories:
                    memory_text = memory.get('memory', '')
                    if memory_text:
                        context += f"- {memory_text}\n"
                context += "\n"

            # Step 3: Create system prompt
            system_prompt = f"""You are a helpful AI assistant with memory of previous conversations.
You have access to the user's conversation history and preferences.

{context}

Use this context to provide personalized and contextual responses.
If the context is relevant, reference it naturally in your response.
If the user asks about previous conversations, use the context to answer accurately."""

            # Step 4: Generate response using OpenAI
            try:
                response = openai_client.chat.completions.create(
                    model=config.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                assistant_message = response.choices[0].message.content

                # Display the response
                st.markdown(assistant_message)

                # Show retrieved memories in an expander
                with st.expander("📚 Retrieved Memories", expanded=False):
                    if relevant_memories:
                        for idx, memory in enumerate(relevant_memories, 1):
                            memory_text = memory.get('memory', 'N/A')
                            st.markdown(f"**{idx}.** {memory_text}")
                    else:
                        st.info("No relevant memories found")

                # Step 5: Store the conversation in memory
                conversation_text = f"User: {user_message}\nAssistant: {assistant_message}"
                memory_manager.add_memory(
                    text=conversation_text,
                    user_id=user_id,
                    metadata={
                        'model': config.default_model,
                        'type': 'conversation'
                    }
                )

                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "memories": relevant_memories
                })

            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")


def display_sidebar():
    """Display sidebar with memory statistics and controls."""
    memory_manager = st.session_state.memory_manager
    user_id = st.session_state.user_id

    if not user_id or not memory_manager:
        return

    with st.sidebar:
        st.divider()

        # Memory Statistics
        st.subheader("📊 Memory Statistics")
        stats = memory_manager.get_memory_stats(user_id)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Memories", stats.get('total_count', 0))
        with col2:
            last_updated = stats.get('last_updated')
            if last_updated:
                try:
                    dt = datetime.fromisoformat(last_updated)
                    st.metric("Last Updated", dt.strftime("%m/%d %H:%M"))
                except:
                    st.metric("Last Updated", "N/A")
            else:
                st.metric("Last Updated", "Never")

        st.divider()

        # View All Memories
        if st.button("📖 View All Memories", use_container_width=True):
            memories = memory_manager.get_all_memories(user_id)
            if memories:
                st.subheader("All Memories")
                for idx, memory in enumerate(memories, 1):
                    memory_text = memory.get('memory', 'N/A')
                    with st.expander(f"Memory {idx}", expanded=False):
                        st.write(memory_text)
                        if 'metadata' in memory:
                            st.caption(f"Metadata: {memory['metadata']}")
            else:
                st.info("No memories found")

        # Export Memories
        if st.button("💾 Export Memories", use_container_width=True):
            export_data = memory_manager.export_memories(user_id)
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"memories_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

        # Clear Memory
        if st.button("🗑️ Clear All Memories", use_container_width=True, type="secondary"):
            if st.button("⚠️ Confirm Clear", use_container_width=True, type="primary"):
                if memory_manager.clear_memories(user_id):
                    st.success("✅ Memories cleared successfully!")
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("❌ Failed to clear memories")

        # Clear Conversation
        st.divider()
        if st.button("🔄 Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def main():
    """Main application logic."""
    initialize_session_state()

    # Step 1: Configuration setup
    if not setup_configuration():
        st.stop()

    # Step 2: User identification
    if not get_user_id():
        st.info("👈 Please enter your username in the sidebar to begin")
        st.stop()

    # Step 3: Initialize memory manager
    if not initialize_memory_manager():
        st.stop()

    # Step 4: Initialize OpenAI client
    if not initialize_openai_client():
        st.stop()

    # Step 5: Display sidebar
    display_sidebar()

    # Step 6: Display chat interface
    display_chat_interface()

    # Step 7: Chat input
    if prompt := st.chat_input("Type your message here..."):
        process_user_message(prompt)


if __name__ == "__main__":
    main()
