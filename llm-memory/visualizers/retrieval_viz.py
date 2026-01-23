import streamlit as st
from typing import List, Dict

class RetrievalVisualizer:
    """Visualize the RAG retrieval process step-by-step."""

    @staticmethod
    def show_retrieval_process(retrieval_details: List[Dict]):
        """
        Display retrieved chunks with similarity scores.

        Args:
            retrieval_details: List of dicts with chunk info and similarity scores
        """
        if not retrieval_details:
            st.info("No relevant documents retrieved (similarity below threshold)")
            return

        st.markdown("### 📚 Retrieved Knowledge")
        st.markdown(f"Found **{len(retrieval_details)}** relevant chunks:")

        for i, detail in enumerate(retrieval_details, 1):
            similarity = detail['similarity']
            content = detail['content']
            metadata = detail['metadata']
            doc_name = metadata.get('document_name', 'Unknown')

            # Color code by similarity
            if similarity >= 0.85:
                badge_color = "🟢"
                badge_text = "Highly Relevant"
            elif similarity >= 0.70:
                badge_color = "🟡"
                badge_text = "Relevant"
            else:
                badge_color = "🟠"
                badge_text = "Moderately Relevant"

            with st.expander(f"{badge_color} **Chunk {i}** from *{doc_name}* - Similarity: **{similarity:.3f}** ({badge_text})"):
                st.markdown(f"**Content:**")
                st.markdown(f"> {content}")
                st.markdown(f"**Metadata:**")
                st.json(metadata)

    @staticmethod
    def show_step_by_step_animation(step: int):
        """
        Show step-by-step breakdown of RAG process.

        Args:
            step: Current step (1-5)
        """
        steps = {
            1: {
                "title": "📝 Step 1: Document Upload",
                "description": "A document is uploaded to the system.",
                "visual": """
                ```
                Document: "TechCorp Vacation Policy"
                └─> Raw text content
                ```
                """
            },
            2: {
                "title": "✂️ Step 2: Text Chunking",
                "description": "Document is split into smaller chunks (typically 500 tokens each).",
                "visual": """
                ```
                Document
                ├─> Chunk 1: "All employees get 15 vacation days..."
                ├─> Chunk 2: "Vacation requests must be submitted..."
                └─> Chunk 3: "Sick leave is separate from vacation..."
                ```
                """
            },
            3: {
                "title": "🧮 Step 3: Embedding",
                "description": "Each chunk is converted to a 384-dimensional vector using a neural network.",
                "visual": """
                ```
                Chunk 1 → [0.23, 0.87, -0.45, 0.12, ..., 0.67]
                                  (384 numbers)

                Similar meanings = Similar vectors
                ```
                """
            },
            4: {
                "title": "💾 Step 4: Storage",
                "description": "Vectors are stored in ChromaDB for fast similarity search.",
                "visual": """
                ```
                ChromaDB
                ├─ chunk_1: [0.23, 0.87, ...] + metadata
                ├─ chunk_2: [0.19, 0.82, ...] + metadata
                └─ chunk_3: [-0.05, 0.34, ...] + metadata
                ```
                """
            },
            5: {
                "title": "🔍 Step 5: Retrieval (when you ask a question)",
                "description": "Your question is embedded and compared to stored chunks using cosine similarity.",
                "visual": """
                ```
                Query: "How many vacation days?"
                    ↓ (embed)
                Query Vector: [0.22, 0.85, -0.43, ...]
                    ↓ (similarity search)
                Top matches:
                ✓ Chunk 1: similarity = 0.89
                ✓ Chunk 2: similarity = 0.73
                ✗ Chunk 3: similarity = 0.42 (below threshold)
                    ↓
                Retrieved chunks added to LLM prompt
                ```
                """
            }
        }

        if step in steps:
            st.markdown(f"## {steps[step]['title']}")
            st.markdown(steps[step]['description'])
            st.markdown(steps[step]['visual'])

    @staticmethod
    def show_prompt_assembly(
        system_prompt: str,
        retrieved_context: str,
        conversation_history: List[Dict],
        current_question: str
    ):
        """
        Show how the final prompt is assembled from different memory components.

        This makes it clear what the LLM actually sees.
        """
        st.markdown("### 🎯 Final Prompt Assembly")
        st.markdown("This is what the LLM receives (with all memory context):")

        # System Prompt
        with st.expander("🤖 System Prompt", expanded=False):
            st.code(system_prompt, language="text")

        # Retrieved Context (Semantic Memory)
        if retrieved_context:
            with st.expander("📚 Retrieved Context (Semantic Memory)", expanded=True):
                st.markdown(retrieved_context)
                st.info(f"📊 Length: ~{len(retrieved_context.split())} words")
        else:
            st.warning("No semantic memory context retrieved")

        # Conversation History (Episodic Memory)
        if conversation_history:
            with st.expander(f"💬 Conversation History (Episodic Memory) - {len(conversation_history)} messages", expanded=True):
                for msg in conversation_history:
                    role = msg['role'].capitalize()
                    content = msg['content']
                    st.markdown(f"**{role}:** {content}")
        else:
            st.warning("No conversation history")

        # Current Question
        with st.expander("❓ Current Question", expanded=True):
            st.markdown(f"**User:** {current_question}")

        st.success("✅ LLM processes all of the above to generate a contextual, accurate response!")
