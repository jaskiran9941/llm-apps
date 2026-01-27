"""
Conversational RAG - Chat with your documents
"""
import streamlit as st
import uuid
import os
from pathlib import Path

from src.models import ConversationHistory, ConversationMessage
from src.document_processor import DocumentProcessor
from src.retrieval.vector_search import VectorSearch
from src.retrieval.bm25_search import BM25Searcher
from src.retrieval.hybrid_fusion import HybridFusion
from src.retrieval.conversational_retriever import ConversationalRetriever
from src.generation.conversational_generator import ConversationalGenerator
from src.utils.config import Config

# Page config
st.set_page_config(
    page_title="Conversational RAG",
    page_icon="🗣️",
    layout="wide"
)

# Title
st.title("🗣️ Conversational RAG")
st.markdown("*Chat with your documents using natural follow-up questions*")


def initialize_session_state():
    """Initialize session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = ConversationHistory(
            conversation_id=str(uuid.uuid4())
        )

    if 'processed' not in st.session_state:
        st.session_state.processed = False

    if 'vector_search' not in st.session_state:
        st.session_state.vector_search = None

    if 'bm25_search' not in st.session_state:
        st.session_state.bm25_search = None

    if 'chunks' not in st.session_state:
        st.session_state.chunks = []

    if 'document_name' not in st.session_state:
        st.session_state.document_name = None


def validate_config():
    """Validate API configuration"""
    try:
        Config.validate()
        return True
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {str(e)}")
        st.info("Please set your OPENAI_API_KEY in a .env file")
        return False


def process_document(uploaded_file, chunk_size, chunk_overlap):
    """Process uploaded PDF document"""
    with st.spinner("Processing document..."):
        # Create processor
        processor = DocumentProcessor(chunk_size=chunk_size, overlap=chunk_overlap)

        # Process PDF
        chunks = processor.process_pdf(uploaded_file)

        if not chunks:
            st.error("No text could be extracted from the PDF")
            return False

        # Initialize search components
        vector_search = VectorSearch(collection_name="conversational_rag")
        bm25_search = BM25Searcher()

        # Clear existing data
        vector_search.clear()

        # Index chunks
        with st.spinner("Indexing chunks..."):
            vector_search.add_chunks(chunks)
            bm25_search.index_chunks(chunks)

        # Store in session state
        st.session_state.chunks = chunks
        st.session_state.vector_search = vector_search
        st.session_state.bm25_search = bm25_search
        st.session_state.processed = True
        st.session_state.document_name = uploaded_file.name

        st.success(f"✅ Processed {len(chunks)} chunks from {uploaded_file.name}")
        return True


def clear_conversation():
    """Clear conversation history"""
    st.session_state.conversation_history = ConversationHistory(
        conversation_id=str(uuid.uuid4())
    )


def main():
    """Main application"""
    # Initialize
    initialize_session_state()

    # Validate config
    if not validate_config():
        return

    # Sidebar
    with st.sidebar:
        st.header("📄 Document Upload")

        # File uploader
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=['pdf'],
            help="Upload a PDF document to chat with"
        )

        # Processing settings
        st.subheader("⚙️ Processing Settings")
        chunk_size = st.slider(
            "Chunk Size",
            min_value=256,
            max_value=1024,
            value=512,
            step=128,
            help="Size of text chunks for retrieval"
        )

        chunk_overlap = st.slider(
            "Chunk Overlap",
            min_value=0,
            max_value=200,
            value=50,
            step=25,
            help="Overlap between chunks"
        )

        # Process button
        if uploaded_file:
            if st.button("Process Document", type="primary"):
                process_document(uploaded_file, chunk_size, chunk_overlap)

        # Retrieval settings
        st.subheader("🔍 Retrieval Settings")
        top_k = st.slider(
            "Number of chunks (k)",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of relevant chunks to retrieve"
        )

        alpha = st.slider(
            "Semantic vs Keyword balance",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="0=keyword only, 1=semantic only, 0.5=balanced"
        )

        # Chat settings
        st.subheader("💬 Chat Settings")
        model = st.selectbox(
            "Chat Model",
            options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
            help="OpenAI model for answer generation"
        )

        # Clear conversation
        st.divider()
        if st.button("🗑️ Clear Conversation"):
            clear_conversation()
            st.rerun()

        # Statistics
        if st.session_state.processed:
            st.divider()
            st.subheader("📊 Statistics")
            st.metric("Document", st.session_state.document_name or "N/A")
            st.metric("Total Chunks", len(st.session_state.chunks))
            st.metric("Messages", len(st.session_state.conversation_history.messages))

    # Main chat area
    if not st.session_state.processed:
        st.info("👈 Upload and process a PDF document to start chatting")
        return

    # Display conversation history
    for msg in st.session_state.conversation_history.messages:
        with st.chat_message(msg.role):
            st.write(msg.content)

            # Show sources for assistant messages
            if msg.role == "assistant" and msg.retrieved_chunks:
                with st.expander(f"📚 Sources ({len(msg.retrieved_chunks)})"):
                    for i, chunk in enumerate(msg.retrieved_chunks, 1):
                        st.caption(
                            f"**Source {i}** - Page {chunk.page} (Score: {chunk.score:.3f})"
                        )
                        st.text(chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content)
                        st.divider()

    # Chat input
    if prompt := st.chat_input("Ask a question about the document"):
        # Add user message to history
        user_msg = ConversationMessage(role="user", content=prompt)
        st.session_state.conversation_history.messages.append(user_msg)

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Initialize retriever
                fusion = HybridFusion()
                retriever = ConversationalRetriever(
                    st.session_state.vector_search,
                    st.session_state.bm25_search,
                    fusion
                )

                # Retrieve relevant chunks
                chunks = retriever.retrieve(
                    prompt,
                    st.session_state.conversation_history,
                    k=top_k,
                    alpha=alpha
                )

                # Generate answer
                generator = ConversationalGenerator(model=model)
                response = generator.generate(
                    prompt,
                    chunks,
                    st.session_state.conversation_history
                )

                # Display answer
                st.write(response.answer)

                # Display sources
                if chunks:
                    with st.expander(f"📚 Sources ({len(chunks)})"):
                        for i, chunk in enumerate(chunks, 1):
                            st.caption(
                                f"**Source {i}** - Page {chunk.page} (Score: {chunk.score:.3f})"
                            )
                            st.text(chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content)
                            st.divider()

                # Add assistant message to history
                assistant_msg = ConversationMessage(
                    role="assistant",
                    content=response.answer,
                    retrieved_chunks=chunks
                )
                st.session_state.conversation_history.messages.append(assistant_msg)


if __name__ == "__main__":
    main()
