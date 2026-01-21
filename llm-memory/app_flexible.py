"""
Production LLM Memory App with Flexible Embedding Providers
Choose between: HuggingFace, OpenAI, Cohere, Voyage, FastEmbed, Ollama
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

from llm.claude_wrapper import ClaudeWrapper
from memory.episodic import EpisodicMemory
from memory.embeddings import get_embedding_provider, PROVIDER_INFO
import numpy as np

load_dotenv()

st.set_page_config(
    page_title="LLM Memory Chat - Flexible",
    page_icon="🎛️",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.episodic_with = EpisodicMemory()
    st.session_state.episodic_without = EpisodicMemory()
    st.session_state.chat_with = []
    st.session_state.chat_without = []
    st.session_state.kb_loaded = False
    st.session_state.initialized = True

# Custom semantic memory with pluggable embeddings
class FlexibleSemanticMemory:
    """Semantic memory with configurable embedding provider."""

    def __init__(self, embedding_provider):
        self.embedding_provider = embedding_provider
        self.chunks = []
        self.embeddings = []
        self.metadata = []

    def chunk_text(self, text: str, chunk_size: int = 500):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def add_document(self, document_text: str, document_name: str, metadata: dict = None):
        chunks = self.chunk_text(document_text)

        for i, chunk in enumerate(chunks):
            embedding = self.embedding_provider.embed(chunk)[0]
            self.chunks.append(chunk)
            self.embeddings.append(embedding)

            chunk_meta = {
                "document_name": document_name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                chunk_meta.update(metadata)
            self.metadata.append(chunk_meta)

        return len(chunks)

    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def retrieve(self, query: str, top_k: int = 3, similarity_threshold: float = 0.7):
        if not self.chunks:
            return "", []

        query_embedding = self.embedding_provider.embed(query)[0]

        similarities = []
        for i, chunk_embedding in enumerate(self.embeddings):
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            similarities.append((i, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)

        retrieval_details = []
        context_chunks = []

        for idx, similarity in similarities[:top_k]:
            if similarity >= similarity_threshold:
                retrieval_details.append({
                    "similarity": float(similarity),
                    "content": self.chunks[idx],
                    "metadata": self.metadata[idx]
                })
                context_chunks.append(self.chunks[idx])

        formatted_context = "\n\n---\n\n".join(context_chunks)
        return formatted_context, retrieval_details

    def get_all_documents(self):
        documents = {}
        for meta in self.metadata:
            doc_name = meta['document_name']
            if doc_name not in documents:
                documents[doc_name] = {"name": doc_name, "chunks": 0}
            documents[doc_name]['chunks'] += 1
        return list(documents.values())

    def clear(self):
        self.chunks = []
        self.embeddings = []
        self.metadata = []

# Sidebar
with st.sidebar:
    st.title("🎛️ Configuration")

    # Embedding Provider Selection
    st.subheader("🔧 Embedding Provider")

    provider_choice = st.selectbox(
        "Choose provider",
        ["huggingface", "openai", "cohere", "voyage", "fastembed", "ollama"],
        index=0,
        help="Different providers offer different trade-offs"
    )

    # Show provider info
    with st.expander(f"ℹ️ About {PROVIDER_INFO[provider_choice]['name']}"):
        info = PROVIDER_INFO[provider_choice]
        st.markdown(f"**Type:** {info['type']}")
        st.markdown(f"**Cost:** {info['cost']}")
        st.markdown(f"**Speed:** {info['speed']}")
        st.markdown(f"**Quality:** {info['quality']}")
        st.markdown(f"**Install:** `{info['requires']}`")

        st.markdown("**Pros:**")
        for pro in info['pros']:
            st.markdown(f"- ✅ {pro}")

        st.markdown("**Cons:**")
        for con in info['cons']:
            st.markdown(f"- ⚠️ {con}")

    # API Keys
    st.markdown("---")
    st.subheader("🔑 API Keys")

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key or anthropic_key.startswith("sk-ant-demo"):
        anthropic_key = st.text_input("Anthropic API Key", type="password")

    # Provider-specific API keys
    provider_key = None
    if provider_choice == "openai":
        provider_key = os.getenv("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password")
    elif provider_choice == "cohere":
        provider_key = os.getenv("COHERE_API_KEY") or st.text_input("Cohere API Key", type="password")
    elif provider_choice == "voyage":
        provider_key = os.getenv("VOYAGE_API_KEY") or st.text_input("Voyage API Key", type="password")

    # Initialize embedding provider
    if 'embedding_provider' not in st.session_state or st.session_state.get('current_provider') != provider_choice:
        try:
            with st.spinner(f"Loading {provider_choice}..."):
                if provider_key:
                    st.session_state.embedding_provider = get_embedding_provider(provider_choice, api_key=provider_key)
                else:
                    st.session_state.embedding_provider = get_embedding_provider(provider_choice)

                st.session_state.current_provider = provider_choice
                st.session_state.semantic = FlexibleSemanticMemory(st.session_state.embedding_provider)
                st.session_state.kb_loaded = False  # Reset KB when provider changes
                st.success(f"✅ {PROVIDER_INFO[provider_choice]['name']} loaded")
        except Exception as e:
            st.error(f"Error loading {provider_choice}: {str(e)}")
            st.info("Make sure the required package is installed")

    st.markdown("---")

    # Knowledge Base
    st.subheader("📚 Knowledge Base")

    if not st.session_state.kb_loaded:
        if st.button("Load Documents", type="primary"):
            if 'semantic' in st.session_state:
                with st.spinner("Indexing documents..."):
                    try:
                        sample_docs_path = Path("knowledge_base/sample_docs")
                        loaded = 0
                        for doc_file in sample_docs_path.glob("*.txt"):
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
                        st.error(f"Error: {str(e)}")
            else:
                st.error("Embedding provider not loaded")
    else:
        docs = st.session_state.semantic.get_all_documents()
        st.success(f"✅ {len(docs)} documents indexed")
        st.caption(f"Using: {PROVIDER_INFO[provider_choice]['name']}")

        if st.button("Clear Knowledge Base"):
            st.session_state.semantic.clear()
            st.session_state.kb_loaded = False
            st.rerun()

    st.markdown("---")

    # Settings
    st.subheader("🎛️ Settings")
    top_k = st.slider("Documents to retrieve", 1, 10, 3)
    similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.7, 0.05)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    if st.button("🔄 Reset Conversations"):
        st.session_state.episodic_with.clear()
        st.session_state.episodic_without.clear()
        st.session_state.chat_with = []
        st.session_state.chat_without = []
        st.rerun()

# Main content
st.title("🎛️ LLM Memory Chat - Flexible Embeddings")
st.caption(f"Currently using: **{PROVIDER_INFO.get(provider_choice, {}).get('name', 'Unknown')}**")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧠 WITH Memory")
    for msg in st.session_state.chat_with:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            if msg['role'] == 'assistant' and msg.get('metadata'):
                with st.expander("📎 Sources"):
                    for doc in msg['metadata'].get('retrieved_docs', []):
                        st.caption(f"• {doc['metadata']['document_name']} ({doc['similarity']:.2f})")

with col2:
    st.markdown("### 💬 WITHOUT Memory")
    for msg in st.session_state.chat_without:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

# Input
user_input = st.chat_input("Ask a question...")

if user_input and anthropic_key:
    st.session_state.chat_with.append({"role": "user", "content": user_input})
    st.session_state.chat_without.append({"role": "user", "content": user_input})

    claude = ClaudeWrapper(api_key=anthropic_key)

    # WITH MEMORY
    with col1:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = st.session_state.episodic_with.get_conversation_history()

                retrieved_context = ""
                retrieval_details = []

                if st.session_state.kb_loaded and 'semantic' in st.session_state:
                    retrieved_context, retrieval_details = st.session_state.semantic.retrieve(
                        query=user_input,
                        top_k=top_k,
                        similarity_threshold=similarity_threshold
                    )

                try:
                    response = claude.generate_response(
                        user_message=user_input,
                        conversation_history=history,
                        retrieved_context=retrieved_context,
                        temperature=temperature
                    )

                    st.markdown(response['response'])

                    if retrieval_details:
                        with st.expander("📎 Sources"):
                            for doc in retrieval_details:
                                st.caption(f"• {doc['metadata']['document_name']} ({doc['similarity']:.2f})")

                    st.session_state.episodic_with.add_turn(
                        user_input,
                        response['response'],
                        response['tokens_used']
                    )

                    st.session_state.chat_with.append({
                        "role": "assistant",
                        "content": response['response'],
                        "metadata": {"retrieved_docs": retrieval_details}
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # WITHOUT MEMORY
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

                    st.session_state.episodic_without.add_turn(
                        user_input,
                        response['response'],
                        response['tokens_used']
                    )

                    st.session_state.chat_without.append({
                        "role": "assistant",
                        "content": response['response']
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.rerun()

elif user_input and not anthropic_key:
    st.error("⚠️ Please enter your Anthropic API key in the sidebar")
