"""
Tab 3: Hybrid Retrieval (Solution to Exact Match Problems)
"""
import streamlit as st
import PyPDF2
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.baseline_rag.simple_chunker import SimpleChunker
from src.advanced_chunking.semantic_chunker import SemanticChunker
from src.baseline_rag.vector_search import VectorSearch
from src.baseline_rag.generator import Generator
from src.hybrid_retrieval.bm25_searcher import BM25Searcher
from src.hybrid_retrieval.hybrid_fusion import HybridRetriever, HybridFusion
from src.hybrid_retrieval.reranker import OpenAIReranker
from src.hybrid_retrieval.query_enhancer import QueryEnhancer


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def render():
    """Render Tab 3: Hybrid Retrieval"""

    st.header("3️⃣ Hybrid Retrieval")
    st.markdown("### Solution 2: Combine Semantic + Keyword Search")

    # Solution box
    st.markdown("""
    <div class="solution-box">
        <h4>✅ Solutions Demonstrated:</h4>
        <ul>
            <li><b>BM25 Keyword Search</b>: Find exact matches (SKUs, codes, names)</li>
            <li><b>Hybrid Fusion</b>: Combine semantic + keyword for best of both</li>
            <li><b>AI Reranking</b>: Use GPT-4 to reorder results by relevance</li>
            <li><b>Query Enhancement</b>: Rewrite, expand, and improve queries</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'tab3_processed' not in st.session_state:
        st.session_state.tab3_processed = False
        st.session_state.tab3_chunks = []
        st.session_state.tab3_vector_search = None
        st.session_state.tab3_bm25_search = None

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF document (ideally with product codes, SKUs, or specific terms)",
        type=['pdf'],
        key="tab3_upload"
    )

    if uploaded_file:
        if st.button("Process Document", key="tab3_process"):
            with st.spinner("Processing document..."):
                # Extract text
                text = extract_text_from_pdf(uploaded_file)

                # Chunk text (using semantic chunking from Tab 2)
                chunker = SemanticChunker(similarity_threshold=0.7)
                chunks = chunker.chunk(text)
                st.session_state.tab3_chunks = chunks

                # Index with vector search
                vector_search = VectorSearch(collection_name="tab3_hybrid")
                vector_search.clear()
                vector_search.add_chunks(chunks)
                st.session_state.tab3_vector_search = vector_search

                # Index with BM25
                bm25_search = BM25Searcher()
                bm25_search.index_chunks(chunks)
                st.session_state.tab3_bm25_search = bm25_search

                st.session_state.tab3_processed = True
                st.success(f"✅ Indexed {len(chunks)} chunks with both semantic and keyword search!")

    # Query interface
    if st.session_state.tab3_processed:
        st.markdown("---")
        st.subheader("🔍 Compare Retrieval Strategies")

        # Query enhancement options
        col1, col2 = st.columns([3, 1])

        with col1:
            query = st.text_input(
                "Enter your question:",
                placeholder="e.g., What is product SKU-12345? or How does authentication work?",
                key="tab3_query"
            )

        with col2:
            enhance_query = st.checkbox("Enhance Query", value=False, key="tab3_enhance")

        # Display enhanced query
        enhanced_query = query
        if enhance_query and query:
            enhancer = QueryEnhancer()
            with st.spinner("Enhancing query..."):
                enhanced_query = enhancer.rewrite_query(query)
                if enhanced_query != query:
                    st.info(f"**Enhanced Query:** {enhanced_query}")

        # Retrieval strategy selector
        strategies = st.multiselect(
            "Select strategies to compare:",
            ["Semantic Only", "Keyword Only (BM25)", "Hybrid", "Hybrid + Reranking"],
            default=["Semantic Only", "Hybrid"],
            key="tab3_strategies"
        )

        if query and st.button("Search", key="tab3_search"):
            st.markdown("### 📊 Strategy Comparison")

            # Create columns based on selected strategies
            if strategies:
                cols = st.columns(len(strategies))

                results_dict = {}

                for idx, strategy in enumerate(strategies):
                    with cols[idx]:
                        st.markdown(f"#### {strategy}")

                        with st.spinner(f"Searching with {strategy}..."):
                            # Perform search based on strategy
                            if strategy == "Semantic Only":
                                results = st.session_state.tab3_vector_search.search(
                                    enhanced_query, k=5
                                )

                            elif strategy == "Keyword Only (BM25)":
                                results = st.session_state.tab3_bm25_search.search(
                                    enhanced_query, k=5
                                )

                            elif strategy == "Hybrid":
                                fusion = HybridFusion()
                                retriever = HybridRetriever(
                                    st.session_state.tab3_vector_search,
                                    st.session_state.tab3_bm25_search,
                                    fusion
                                )
                                results = retriever.search(enhanced_query, k=5)

                            else:  # Hybrid + Reranking
                                fusion = HybridFusion()
                                retriever = HybridRetriever(
                                    st.session_state.tab3_vector_search,
                                    st.session_state.tab3_bm25_search,
                                    fusion
                                )
                                hybrid_results = retriever.search(enhanced_query, k=10)

                                # Rerank
                                reranker = OpenAIReranker()
                                results = reranker.rerank(enhanced_query, hybrid_results, top_k=5)

                            results_dict[strategy] = results

                            # Generate answer
                            generator = Generator()
                            response = generator.generate(enhanced_query, results)

                            # Display answer
                            st.markdown("**Answer:**")
                            st.info(response.answer)

                            # Show top chunk
                            if results:
                                with st.expander("Top Result"):
                                    st.write(results[0].content[:300] + "...")
                                    st.caption(f"Score: {results[0].score:.3f}")
                                    if 'retrieval_method' in results[0].metadata:
                                        st.caption(
                                            f"Method: {results[0].metadata['retrieval_method']}"
                                        )

                            # Metrics
                            avg_score = (
                                sum(r.score for r in results) / len(results)
                                if results else 0
                            )
                            st.metric("Avg Score", f"{avg_score:.3f}")

                            # Color code based on performance
                            if avg_score > 0.8:
                                st.success("🟢 High quality")
                            elif avg_score > 0.6:
                                st.warning("🟡 Medium quality")
                            else:
                                st.error("🔴 Low quality")

                # Summary comparison
                st.markdown("---")
                st.markdown("### 📈 Performance Summary")

                summary_data = []
                for strategy, results in results_dict.items():
                    avg_score = (
                        sum(r.score for r in results) / len(results)
                        if results else 0
                    )
                    summary_data.append({
                        "Strategy": strategy,
                        "Avg Score": f"{avg_score:.3f}",
                        "Top Result Score": f"{results[0].score:.3f}" if results else "0.000",
                        "Results": len(results)
                    })

                import pandas as pd
                df = pd.DataFrame(summary_data)
                st.dataframe(df, use_container_width=True)

                # Winner
                best = max(summary_data, key=lambda x: float(x["Avg Score"]))
                st.success(f"🏆 Best Strategy: **{best['Strategy']}** "
                          f"(Avg Score: {best['Avg Score']})")

                # Insight
                st.markdown("""
                <div class="info-box">
                <h4>💡 Key Insights:</h4>
                <ul>
                    <li><b>Semantic</b>: Great for conceptual queries, may miss exact terms</li>
                    <li><b>Keyword (BM25)</b>: Perfect for exact matches, weaker on concepts</li>
                    <li><b>Hybrid</b>: Best of both worlds! Combines strengths</li>
                    <li><b>Hybrid + Rerank</b>: Highest quality but more expensive</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

    # Educational content
    with st.expander("📚 Learn: How Hybrid Retrieval Works"):
        st.markdown("""
        ### Hybrid Retrieval Pipeline

        #### 1. Semantic Search (Vector Similarity)
        ```python
        # Embed query
        query_vec = embed("What is product SKU-12345?")

        # Find similar vectors
        results = vector_db.search(query_vec)
        # Good for: concepts, paraphrases, synonyms
        # Weak for: exact codes, numbers
        ```

        #### 2. Keyword Search (BM25)
        ```python
        # Tokenize and match terms
        results = bm25.search("SKU-12345")
        # Good for: exact matches, product codes
        # Weak for: synonyms, paraphrases
        ```

        #### 3. Reciprocal Rank Fusion (RRF)
        ```python
        # Combine rankings from both methods
        for rank, result in enumerate(semantic_results):
            score[result.id] += 1 / (60 + rank + 1)

        for rank, result in enumerate(keyword_results):
            score[result.id] += 1 / (60 + rank + 1)

        # Sort by combined score
        final_results = sort_by_score(score)
        # ✅ Gets best of both!
        ```

        #### 4. Optional: AI Reranking
        ```python
        # Use GPT-4 to assess relevance
        for result in hybrid_results:
            relevance_score = gpt4_rate_relevance(query, result)

        # Reorder by GPT-4 scores
        # ✅ Most accurate, but costs more
        ```

        ### Performance Gains

        - Semantic Only: ~75% accuracy
        - Hybrid: ~90% accuracy ⬆️
        - Hybrid + Rerank: ~95% accuracy ⬆️⬆️

        **Cost vs Quality Trade-off:** Reranking adds ~$0.01 per query
        """)
