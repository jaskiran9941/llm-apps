"""
Tab 1: Baseline RAG (Demonstrating Problems)
"""
import streamlit as st
import PyPDF2
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.baseline_rag.simple_chunker import SimpleChunker
from src.baseline_rag.text_embedder import TextEmbedder
from src.baseline_rag.vector_search import VectorSearch
from src.baseline_rag.generator import Generator
from src.vision_rag.image_extractor import ImageExtractor


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def render():
    """Render Tab 1: Baseline RAG"""

    st.header("1️⃣ Baseline Text-Only RAG")
    st.markdown("### The Starting Point: See the Problems")

    # Problem box
    st.markdown("""
    <div class="problem-box">
        <h4>⚠️ Problems We'll Discover:</h4>
        <ul>
            <li><b>Bad Chunking</b>: Text split mid-sentence, losing context</li>
            <li><b>Semantic-Only Search</b>: Misses exact matches (product codes, SKUs)</li>
            <li><b>Image Blindness</b>: Cannot see charts, diagrams, tables</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'tab1_processed' not in st.session_state:
        st.session_state.tab1_processed = False
        st.session_state.tab1_chunks = []
        st.session_state.tab1_stats = {}
        st.session_state.tab1_images_count = 0

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF document",
        type=['pdf'],
        key="tab1_upload"
    )

    if uploaded_file:
        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("Process Document", key="tab1_process"):
                with st.spinner("Processing document..."):
                    # Save uploaded file temporarily
                    temp_path = Path(f"/tmp/{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Extract text
                    text = extract_text_from_pdf(uploaded_file)

                    # Count images (to show what we're missing)
                    extractor = ImageExtractor()
                    images = extractor.extract_images(str(temp_path))
                    st.session_state.tab1_images_count = len(images)

                    # Chunk text with simple chunker
                    chunker = SimpleChunker(chunk_size=500, chunk_overlap=50)
                    chunks = chunker.chunk(text)
                    st.session_state.tab1_chunks = chunks

                    # Analyze chunks
                    st.session_state.tab1_stats = chunker.analyze_chunks(chunks)

                    # Index chunks
                    vector_search = VectorSearch(collection_name="tab1_baseline")
                    vector_search.clear()
                    vector_search.add_chunks(chunks)

                    st.session_state.tab1_processed = True
                    st.success("✅ Document processed!")

        with col2:
            if st.session_state.tab1_processed:
                # Show statistics
                st.markdown("### 📊 Document Stats")
                stats = st.session_state.tab1_stats

                st.metric("Total Chunks", stats.get('total_chunks', 0))
                st.metric(
                    "Incomplete Chunks",
                    stats.get('incomplete_chunks', 0),
                    delta=f"{stats.get('completeness_rate', 0) * 100:.0f}% complete",
                    delta_color="inverse"
                )

                # Warning about images
                if st.session_state.tab1_images_count > 0:
                    st.warning(f"⚠️ {st.session_state.tab1_images_count} images detected but IGNORED!")

    # Query interface
    if st.session_state.tab1_processed:
        st.markdown("---")
        st.subheader("🔍 Ask Questions")

        query = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is the main topic of this document?",
            key="tab1_query"
        )

        if query and st.button("Search", key="tab1_search"):
            with st.spinner("Searching..."):
                # Search
                vector_search = VectorSearch(collection_name="tab1_baseline")
                results = vector_search.search(query, k=5)

                # Generate answer
                generator = Generator()
                response = generator.generate(query, results)

                # Display answer
                st.markdown("### 💬 Answer")
                st.info(response.answer)

                # Display retrieved chunks
                st.markdown("### 📄 Retrieved Chunks")

                for i, result in enumerate(results, 1):
                    is_complete = result.metadata.get('is_complete', True)

                    with st.expander(
                        f"Chunk {i} - Page {result.page} "
                        f"{'✅' if is_complete else '❌ INCOMPLETE'}",
                        expanded=(not is_complete)
                    ):
                        # Highlight incomplete chunks
                        if not is_complete:
                            st.markdown("""
                            <div class="problem-box">
                            <b>⚠️ Problem: Chunk cut mid-sentence!</b>
                            </div>
                            """, unsafe_allow_html=True)

                        st.write(result.content)
                        st.caption(f"Score: {result.score:.3f}")

                # Metrics
                st.markdown("### 📈 Metrics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Chunks Retrieved", len(results))

                with col2:
                    avg_score = sum(r.score for r in results) / len(results) if results else 0
                    st.metric("Avg Similarity", f"{avg_score:.2f}")

                with col3:
                    # Estimate accuracy based on completeness
                    complete_chunks = sum(
                        1 for r in results
                        if r.metadata.get('is_complete', True)
                    )
                    accuracy = (complete_chunks / len(results) * 100) if results else 0
                    st.metric("Estimated Accuracy", f"{accuracy:.0f}%")

                # Show problems
                if st.session_state.tab1_images_count > 0:
                    st.markdown("""
                    <div class="problem-box">
                    <h4>🚨 Problems Detected:</h4>
                    <ul>
                        <li>Document has images/charts that were completely ignored</li>
                        <li>Some chunks are incomplete (cut mid-sentence)</li>
                        <li>Pure semantic search may miss exact matches</li>
                    </ul>
                    <p><b>💡 Solution: Continue to the next tabs to see how we fix these!</b></p>
                    </div>
                    """, unsafe_allow_html=True)

    # Educational content
    with st.expander("📚 Learn: How Baseline RAG Works"):
        st.markdown("""
        ### Baseline RAG Pipeline

        1. **Chunking**: Split document into fixed-size pieces (500 chars)
           - ❌ Problem: Breaks mid-sentence
           - Example: "The system uses microservices. Each|" ← Cuts here!

        2. **Embedding**: Convert text to vectors using OpenAI
           - Model: `text-embedding-3-small` (1536 dimensions)
           - Cost: ~$0.02 per 1M tokens

        3. **Storage**: Store in ChromaDB vector database
           - Uses cosine similarity for search

        4. **Retrieval**: Find similar chunks to query
           - ❌ Problem: Semantic-only, misses exact matches

        5. **Generation**: GPT-4 generates answer from chunks
           - ❌ Problem: Can't use information from images!

        **This is why we need the improvements in the next tabs!**
        """)
