import streamlit as st
from typing import Dict

class UIComponents:
    """Reusable Streamlit UI components for education."""

    @staticmethod
    def show_concept_explanation(concept: str):
        """Show explanation for a memory concept."""
        concepts = {
            "episodic": {
                "title": "📖 Episodic Memory",
                "definition": "Memory of past conversations - what was said and when.",
                "how_it_works": """
                - Stores conversation history (user messages + assistant responses)
                - Maintains temporal sequence (what happened first, second, etc.)
                - Limited by context window (can't store infinite history)
                - Uses sliding window: keeps recent turns, drops old ones
                """,
                "why_it_matters": """
                Without episodic memory:
                - LLM can't remember previous messages
                - Each question is treated independently
                - No continuity in conversation

                With episodic memory:
                - LLM understands context from earlier in conversation
                - Can reference previous topics
                - Natural, flowing dialogue
                """,
                "example": """
                **Without Episodic:**
                User: "I'm planning a party for 20 people"
                Bot: "That's nice!"
                User: "What's a good budget?"
                Bot: "Budget for what?" ❌

                **With Episodic:**
                User: "I'm planning a party for 20 people"
                Bot: "That's nice!"
                User: "What's a good budget?"
                Bot: "For a party of 20, budget $50-100 per person" ✅
                """
            },
            "semantic": {
                "title": "📚 Semantic Memory",
                "definition": "Long-term knowledge storage - facts and information independent of personal experience.",
                "how_it_works": """
                **RAG Process (Retrieval Augmented Generation):**

                1. **Storage Phase:**
                   - Documents are split into chunks (500 tokens each)
                   - Each chunk is embedded (converted to 384-dimensional vector)
                   - Vectors stored in database (ChromaDB)

                2. **Retrieval Phase:**
                   - User asks a question
                   - Question is embedded to vector
                   - Similarity search finds relevant chunks (cosine similarity)
                   - Top-k most similar chunks retrieved

                3. **Augmentation Phase:**
                   - Retrieved chunks added to LLM prompt
                   - LLM uses this context to answer accurately
                """,
                "why_it_matters": """
                Without semantic memory:
                - LLM limited to training data knowledge
                - Can't access company-specific information
                - May hallucinate or give generic answers

                With semantic memory:
                - Access to specific documents and policies
                - Accurate, grounded responses
                - Can cite sources
                """,
                "example": """
                **Without Semantic:**
                User: "How many vacation days do TechCorp employees get?"
                Bot: "Most companies offer 10-15 days" ❌ (generic)

                **With Semantic:**
                User: "How many vacation days do TechCorp employees get?"
                [Retrieves: "TechCorp offers 15 vacation days per year"]
                Bot: "TechCorp employees get 15 vacation days per year" ✅
                """
            },
            "working": {
                "title": "🧠 Working Memory",
                "definition": "Temporary storage for intermediate reasoning steps - the LLM's 'scratch pad'.",
                "how_it_works": """
                - LLM breaks down complex problems into steps
                - Each step is processed sequentially
                - Previous steps inform next steps
                - Similar to human "thinking aloud"
                """,
                "why_it_matters": """
                Without working memory:
                - Direct question → answer (may miss nuances)
                - Less reliable for multi-step reasoning

                With working memory (Chain-of-Thought):
                - Question → reasoning steps → answer
                - More accurate for complex problems
                - Transparent reasoning process
                """,
                "example": """
                **Direct:**
                User: "If I take 3 vacation days and 2 sick days, how many do I have left?"
                Bot: "12 vacation days" (may be wrong)

                **Chain-of-Thought:**
                Reasoning:
                1. Standard vacation: 15 days
                2. Taking 3 days: 15 - 3 = 12 left
                3. Sick days are separate
                Answer: "12 vacation days left (sick days don't reduce vacation)"
                """
            }
        }

        if concept.lower() not in concepts:
            st.error(f"Unknown concept: {concept}")
            return

        info = concepts[concept.lower()]

        st.markdown(f"### {info['title']}")

        with st.expander("Definition", expanded=True):
            st.markdown(info['definition'])

        with st.expander("How It Works"):
            st.markdown(info['how_it_works'])

        with st.expander("Why It Matters"):
            st.markdown(info['why_it_matters'])

        with st.expander("Example"):
            st.code(info['example'])

    @staticmethod
    def show_settings_panel():
        """Display settings panel for memory configuration."""
        st.sidebar.markdown("## ⚙️ Settings")

        # Episodic Memory Settings
        st.sidebar.markdown("### 💬 Episodic Memory")
        max_history = st.sidebar.slider(
            "Max conversation turns to keep",
            min_value=3,
            max_value=20,
            value=10,
            help="Number of previous conversation turns to remember"
        )

        # Semantic Memory Settings
        st.sidebar.markdown("### 📚 Semantic Memory")
        top_k = st.sidebar.slider(
            "Top-K retrieval",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of most relevant chunks to retrieve"
        )

        similarity_threshold = st.sidebar.slider(
            "Similarity threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Minimum similarity score for retrieval (0.0 to 1.0)"
        )

        # LLM Settings
        st.sidebar.markdown("### 🤖 LLM Settings")
        model_choice = st.sidebar.selectbox(
            "Model",
            options=["haiku", "sonnet", "opus"],
            index=0,
            help="Haiku is fastest and cheapest, Opus is most capable"
        )

        temperature = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher = more creative, Lower = more focused"
        )

        return {
            "max_history": max_history,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "model": model_choice,
            "temperature": temperature
        }

    @staticmethod
    def show_memory_stats(
        episodic_turns: int,
        episodic_tokens: int,
        semantic_chunks: int,
        total_retrievals: int
    ):
        """Display memory statistics dashboard."""
        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📊 Memory Stats")

        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("💬 Conv Turns", episodic_turns)
            st.metric("🔍 Retrievals", total_retrievals)

        with col2:
            st.metric("📚 Doc Chunks", semantic_chunks)
            st.metric("🎯 Tokens Used", f"{episodic_tokens:,}")

    @staticmethod
    def show_welcome_screen():
        """Display welcome screen with learning path options."""
        st.markdown("""
        # 🧠 LLM Memory Learning Platform

        Welcome! This interactive platform teaches you **how LLM memory actually works**.

        ## What You'll Learn

        1. **Types of Memory**
           - 💬 Episodic (conversation history)
           - 📚 Semantic (knowledge retrieval)
           - 🧠 Working (reasoning)

        2. **How Memory Works**
           - Vector embeddings
           - Similarity search
           - Context assembly

        3. **Why Memory Matters**
           - See WITH vs WITHOUT side-by-side
           - Understand trade-offs (accuracy vs cost)

        ## Choose Your Path

        - 📖 **Tabs at the top** - Explore different aspects
        - 🎮 **Try the comparison** - See memory in action
        - 🔬 **Deep dives** - Understand internals
        - 🛝 **Playground** - Experiment yourself

        ## Quick Start

        1. Try the **Side-by-Side Comparison** tab
        2. Ask: "How many vacation days do I get?"
        3. Compare the responses!

        ---
        """)

        st.info("💡 **Tip:** Hover over elements for explanations. Check the sidebar for settings.")
