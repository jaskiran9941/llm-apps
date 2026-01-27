"""
Tab 2: Smart Chunking (Solution to Text Boundary Problems)
"""
import streamlit as st
import PyPDF2
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.baseline_rag.simple_chunker import SimpleChunker
from src.advanced_chunking.sentence_chunker import SentenceChunker
from src.advanced_chunking.semantic_chunker import SemanticChunker
from src.baseline_rag.vector_search import VectorSearch
from src.baseline_rag.generator import Generator


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def render():
    """Render Tab 2: Smart Chunking"""

    st.header("2️⃣ Smart Chunking")
    st.markdown("### Solution 1: Respect Text Boundaries")

    # Solution box
    st.markdown("""
    <div class="solution-box">
        <h4>✅ Solutions Demonstrated:</h4>
        <ul>
            <li><b>Sentence-Aware</b>: Split at sentence boundaries, not mid-sentence</li>
            <li><b>Semantic Chunking</b>: Split when topic changes (using embeddings)</li>
            <li><b>Better Retrieval</b>: Complete context = better answers</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'tab2_processed' not in st.session_state:
        st.session_state.tab2_processed = False
        st.session_state.tab2_results = {}

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF document",
        type=['pdf'],
        key="tab2_upload"
    )

    if uploaded_file:
        # Chunking strategy selector
        strategy = st.selectbox(
            "Select Chunking Strategy",
            ["Fixed-size (Baseline)", "Sentence-Aware", "Semantic"],
            key="tab2_strategy"
        )

        if st.button("Process Document", key="tab2_process"):
            with st.spinner(f"Processing with {strategy} chunking..."):
                # Extract text
                text = extract_text_from_pdf(uploaded_file)

                # Select chunker
                if strategy == "Fixed-size (Baseline)":
                    chunker = SimpleChunker(chunk_size=500, chunk_overlap=50)
                    collection_name = "tab2_fixed"
                elif strategy == "Sentence-Aware":
                    chunker = SentenceChunker(chunk_size=500, chunk_overlap=50)
                    collection_name = "tab2_sentence"
                else:  # Semantic
                    chunker = SemanticChunker(similarity_threshold=0.7, min_chunk_size=200)
                    collection_name = "tab2_semantic"

                # Chunk text
                chunks = chunker.chunk(text)
                stats = chunker.analyze_chunks(chunks)

                # Index chunks
                vector_search = VectorSearch(collection_name=collection_name)
                vector_search.clear()
                vector_search.add_chunks(chunks)

                # Store results
                st.session_state.tab2_results[strategy] = {
                    'chunks': chunks,
                    'stats': stats,
                    'collection_name': collection_name
                }

                st.session_state.tab2_processed = True
                st.success(f"✅ Processed with {strategy} chunking!")

        # Display statistics comparison
        if st.session_state.tab2_results:
            st.markdown("---")
            st.subheader("📊 Chunking Strategy Comparison")

            # Create comparison table
            comparison_data = []
            for strat, data in st.session_state.tab2_results.items():
                stats = data['stats']
                comparison_data.append({
                    "Strategy": strat,
                    "Total Chunks": stats.get('total_chunks', 0),
                    "Complete": stats.get('complete_chunks', 0),
                    "Incomplete": stats.get('incomplete_chunks', 0),
                    "Completeness": f"{stats.get('completeness_rate', 0) * 100:.0f}%",
                    "Avg Size": f"{stats.get('avg_chunk_size', 0):.0f} chars"
                })

            import pandas as pd
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)

            # Highlight winner
            best_strategy = max(
                st.session_state.tab2_results.items(),
                key=lambda x: x[1]['stats'].get('completeness_rate', 0)
            )[0]

            st.success(f"🏆 Best Strategy: **{best_strategy}** with highest completeness rate!")

    # Query interface
    if st.session_state.tab2_processed:
        st.markdown("---")
        st.subheader("🔍 Compare Retrieval Quality")

        query = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is the main conclusion?",
            key="tab2_query"
        )

        if query and st.button("Search All Strategies", key="tab2_search"):
            st.markdown("### 📊 Side-by-Side Comparison")

            # Create columns for each strategy
            cols = st.columns(len(st.session_state.tab2_results))

            for idx, (strat, data) in enumerate(st.session_state.tab2_results.items()):
                with cols[idx]:
                    st.markdown(f"#### {strat}")

                    # Search
                    vector_search = VectorSearch(collection_name=data['collection_name'])
                    results = vector_search.search(query, k=3)

                    # Generate answer
                    generator = Generator()
                    response = generator.generate(query, results)

                    # Display answer
                    st.info(response.answer)

                    # Show top chunk
                    if results:
                        with st.expander("Top Chunk"):
                            st.write(results[0].content[:300] + "...")
                            st.caption(f"Score: {results[0].score:.3f}")

                            # Show completeness
                            is_complete = results[0].metadata.get('is_complete', True)
                            if is_complete:
                                st.success("✅ Complete chunk")
                            else:
                                st.error("❌ Incomplete chunk")

                    # Metrics
                    avg_score = sum(r.score for r in results) / len(results) if results else 0
                    st.metric("Avg Score", f"{avg_score:.3f}")

            # Overall winner
            st.markdown("---")
            st.markdown("""
            <div class="info-box">
            <h4>💡 Key Insight:</h4>
            <p>Notice how <b>Semantic Chunking</b> and <b>Sentence-Aware</b> chunking
            provide more coherent chunks with complete thoughts, leading to better answers!</p>
            <p>This fixes the "broken sentences" problem from Tab 1.</p>
            </div>
            """, unsafe_allow_html=True)

    # Educational content
    with st.expander("📚 Learn: How Smart Chunking Works"):
        st.markdown("""
        ### Chunking Strategies Explained

        #### 1. Fixed-Size (The Problem)
        ```python
        # Splits at character 500, regardless of content
        chunk1 = text[0:500]  # "...uses REST APIs and"
        chunk2 = text[450:950]  # "and JWT tokens for auth..."
        # ❌ Breaks mid-sentence!
        ```

        #### 2. Sentence-Aware (Better)
        ```python
        sentences = split_into_sentences(text)
        # Accumulate until size limit, but keep sentences intact
        chunk = []
        for sentence in sentences:
            if len(chunk) + len(sentence) < 500:
                chunk.append(sentence)
            else:
                yield complete_chunk(chunk)  # ✅ Complete!
                chunk = [sentence]
        ```

        #### 3. Semantic (Best)
        ```python
        # Embed each sentence
        embeddings = embed(sentences)

        # Split when similarity drops (topic change)
        for i in range(1, len(sentences)):
            similarity = cosine_sim(embeddings[i-1], embeddings[i])
            if similarity < 0.7:  # Topic changed!
                yield chunk  # Start new chunk
        ```

        ### Why This Matters

        **Complete chunks → Better context → More accurate answers!**

        Estimated Accuracy Improvement: **60% → 85%** ⬆️
        """)
