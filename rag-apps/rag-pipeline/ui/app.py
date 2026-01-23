"""
Main Streamlit application for RAG Learning System.

This app provides an interactive interface for:
- Uploading and indexing documents
- Asking questions with RAG
- Comparing RAG vs non-RAG
- Experimenting with parameters
- Learning about RAG concepts
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.document_processing.pdf_loader import PDFLoader
from src.document_processing.preprocessor import TextPreprocessor
from src.document_processing.chunker import FixedSizeChunker
from src.embeddings.openai_embeddings import OpenAIEmbeddingManager
from src.vector_store.simple_store import SimpleVectorStore
from src.retrieval.semantic_retriever import SemanticRetriever
from src.generation.llm_manager import LLMManager
from src.generation.rag_generator import RAGGenerator
from src.pipeline.indexing_pipeline import IndexingPipeline
from src.pipeline.query_pipeline import QueryPipeline

from ui.components.config_panel import (
    render_config_sidebar,
    render_cost_calculator,
    render_system_info
)
from ui.components.document_manager import (
    render_upload_section,
    render_document_list,
    render_storage_stats
)
from ui.components.query_interface import (
    render_query_input,
    render_query_buttons,
    render_query_result,
    render_comparison,
    render_query_history
)


# Page configuration
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_components(config):
    """
    Initialize RAG components (cached for performance).

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (indexing_pipeline, query_pipeline, vector_store)
    """
    # Initialize components
    pdf_loader = PDFLoader(use_pdfplumber=True)

    preprocessor = TextPreprocessor(
        normalize_whitespace=True,
        remove_special_chars=False,
        preserve_paragraphs=True
    )

    chunker = FixedSizeChunker(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"]
    )

    embedding_manager = OpenAIEmbeddingManager()

    vector_store = SimpleVectorStore()

    retriever = SemanticRetriever(
        embedding_manager=embedding_manager,
        vector_store=vector_store,
        min_score=config["min_score"]
    )

    llm_manager = LLMManager(
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )

    rag_generator = RAGGenerator(llm_manager=llm_manager)

    # Create pipelines
    indexing_pipeline = IndexingPipeline(
        pdf_loader=pdf_loader,
        preprocessor=preprocessor,
        chunker=chunker,
        embedding_manager=embedding_manager,
        vector_store=vector_store
    )

    query_pipeline = QueryPipeline(
        retriever=retriever,
        generator=rag_generator
    )

    return indexing_pipeline, query_pipeline, vector_store


def main():
    """Main application function."""

    # Title
    st.title("📚 RAG Learning System")
    st.markdown("""
    **Retrieval-Augmented Generation** - Upload documents, ask questions, and learn how RAG works!
    """)

    # Sidebar configuration
    config = render_config_sidebar()
    render_cost_calculator()

    # Initialize components
    try:
        # Validate API key
        settings.validate()

        indexing_pipeline, query_pipeline, vector_store = initialize_components(config)

        render_system_info(vector_store)

    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {str(e)}")
        st.info("Please set your OPENAI_API_KEY in the .env file")
        st.stop()

    # Initialize session state
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload Documents",
        "🔍 Query Interface",
        "🧪 Experiments",
        "📖 Documentation"
    ])

    # TAB 1: Upload Documents
    with tab1:
        render_upload_section(indexing_pipeline, settings.UPLOADS_DIR)

        st.markdown("---")

        # Document list
        render_document_list(vector_store)

        st.markdown("---")

        # Storage stats
        st.subheader("📊 Storage Statistics")
        render_storage_stats(vector_store)

    # TAB 2: Query Interface
    with tab2:
        # Check if documents are indexed
        stats = vector_store.get_stats()
        if stats.get("total_chunks", 0) == 0:
            st.warning("⚠️ No documents indexed yet! Go to 'Upload Documents' tab to add some.")
            st.stop()

        # Query input
        query, top_k, show_comparison = render_query_input()

        # Query buttons
        ask_rag, ask_no_rag, ask_compare = render_query_buttons()

        # Handle query execution
        if query:
            if ask_rag:
                with st.spinner("Generating answer with RAG..."):
                    result = query_pipeline.query(query, top_k=top_k)
                    st.session_state.query_history.append((query, result))

                st.markdown("---")
                render_query_result(result, show_chunks=True)

            elif ask_no_rag:
                with st.spinner("Generating answer without RAG..."):
                    result = query_pipeline.query_without_rag(query)
                    st.session_state.query_history.append((query, result))

                st.markdown("---")
                render_query_result(result, show_chunks=False)

            elif ask_compare:
                with st.spinner("Comparing RAG vs non-RAG..."):
                    results = query_pipeline.compare_rag_vs_no_rag(query, top_k=top_k)

                st.markdown("---")
                render_comparison(results["rag"], results["no_rag"])

        else:
            st.info("👆 Enter a question above and click a button to get started!")

        # Query history
        if st.session_state.query_history:
            render_query_history(st.session_state.query_history)

    # TAB 3: Experiments
    with tab3:
        st.header("🧪 Experiments")

        st.markdown("""
        Explore how different parameters affect RAG performance.
        """)

        exp_tab1, exp_tab2 = st.tabs([
            "Chunk Size Impact",
            "RAG vs Non-RAG"
        ])

        with exp_tab1:
            st.subheader("📏 How Chunk Size Affects Retrieval")

            st.markdown("""
            Experiment with different chunk sizes to see their impact on:
            - Number of chunks created
            - Retrieval precision
            - Cost

            **Exercise:**
            1. Index the same document with different chunk sizes
            2. Ask the same question
            3. Compare the retrieved chunks and answer quality
            """)

            st.info("""
            **Key Insights:**
            - Smaller chunks: More precise but may miss context
            - Larger chunks: More context but less precise
            - Overlap: Helps maintain continuity across boundaries
            """)

        with exp_tab2:
            st.subheader("⚖️ RAG vs Non-RAG Comparison")

            st.markdown("""
            See the difference between:
            - **With RAG**: Answers based on your specific documents
            - **Without RAG**: Answers based on model's general knowledge

            Try asking questions that:
            1. Are specific to your documents (RAG should excel)
            2. Are general knowledge (both should work)
            3. Require combining information from multiple sources
            """)

            example_query = st.text_input(
                "Try a comparison query:",
                placeholder="e.g., What are the key findings in the research paper?"
            )

            if example_query and st.button("🔄 Run Comparison"):
                with st.spinner("Running comparison..."):
                    results = query_pipeline.compare_rag_vs_no_rag(example_query, top_k=config["top_k"])
                    render_comparison(results["rag"], results["no_rag"])

    # TAB 4: Documentation
    with tab4:
        st.header("📖 How RAG Works")

        st.markdown("""
        ## What is RAG?

        **Retrieval-Augmented Generation (RAG)** combines information retrieval with text generation:

        1. **Retrieval**: Find relevant information from a knowledge base
        2. **Augmentation**: Add that information to the prompt as context
        3. **Generation**: LLM generates an answer using the context

        ## Why Use RAG?

        ✅ **Accuracy**: Answers based on specific documents, not just training data
        ✅ **Citations**: Can reference exact sources
        ✅ **Up-to-date**: Update documents without retraining model
        ✅ **Cost-effective**: Cheaper than fine-tuning large models
        ✅ **Transparency**: See which chunks influenced the answer

        ## How This System Works

        ### 1. Indexing Pipeline
        ```
        PDF → Extract Text → Preprocess → Chunk → Embed → Store
        ```

        - **Extract**: Get text from PDF, preserve page numbers
        - **Preprocess**: Clean and normalize text
        - **Chunk**: Split into ~500 character pieces with overlap
        - **Embed**: Convert to 1536-dimension vectors (OpenAI)
        - **Store**: Save in ChromaDB for fast retrieval

        ### 2. Query Pipeline
        ```
        Question → Embed → Retrieve → Format Context → Generate → Answer
        ```

        - **Embed**: Convert question to same vector space as documents
        - **Retrieve**: Find most similar chunks (cosine similarity)
        - **Context**: Format retrieved chunks into prompt
        - **Generate**: LLM creates answer using context
        - **Return**: Answer with sources and metadata

        ## Key Parameters

        ### Chunk Size
        - **Small (200-300)**: Precise retrieval, less context per chunk
        - **Medium (400-700)**: Balanced - good for most use cases ✅
        - **Large (800-1500)**: More context, less precise retrieval

        ### Chunk Overlap
        - Maintains context across chunk boundaries
        - Typical: 10-20% of chunk size
        - Trade-off: Better continuity vs higher costs

        ### Top-K (Retrieval)
        - Number of chunks to retrieve
        - More chunks = more context but higher cost
        - Typical: 3-7 chunks ✅

        ### Temperature
        - Controls randomness in LLM response
        - 0 = deterministic, factual ✅
        - 1 = creative, varied
        - 2 = very creative (may hallucinate)

        ## Cost Breakdown

        **Indexing (one-time per document):**
        - Embedding: $0.0001 per 1K tokens
        - Example: 100-page document ≈ 50K tokens ≈ $0.005

        **Querying (per question):**
        - Embedding query: ~$0.0001
        - LLM generation: ~$0.01-0.03 (depends on context size)
        - Example: Question with 5 chunks ≈ $0.02

        ## Best Practices

        1. **Start Simple**: Use default parameters, then optimize
        2. **Monitor Costs**: Track token usage and costs
        3. **Experiment**: Try different chunk sizes and top-k values
        4. **Evaluate**: Compare RAG vs non-RAG for your use case
        5. **Iterate**: Refine based on answer quality and cost

        ## Future Enhancements

        This is Project 1 - a foundation for learning RAG. Future projects will add:

        - **Project 2**: Advanced chunking (semantic, recursive)
        - **Project 3**: Hybrid retrieval (BM25 + semantic) and reranking
        - **Project 4**: Context enhancement (parent-child chunks, query rewriting)

        ## Resources

        - [Anthropic's RAG Guide](https://www.anthropic.com/index/contextual-retrieval)
        - [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
        - [ChromaDB Documentation](https://docs.trychroma.com/)
        """)


if __name__ == "__main__":
    main()
