"""
Tab 4: Vision RAG (Ultimate Solution - Multimodal)
"""
import streamlit as st
import PyPDF2
from pathlib import Path
import sys
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.advanced_chunking.semantic_chunker import SemanticChunker
from src.vision_rag.image_extractor import ImageExtractor
from src.vision_rag.multimodal_store import MultimodalVectorStore
from src.vision_rag.multimodal_retriever import MultimodalRetriever
from src.vision_rag.vision_generator import VisionGenerator


def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def render():
    """Render Tab 4: Vision RAG"""

    st.header("4️⃣ Vision-Based Multimodal RAG")
    st.markdown("### Ultimate Solution: Text + Images Together")

    # Solution box
    st.markdown("""
    <div class="solution-box">
        <h4>🎯 Complete Solution:</h4>
        <ul>
            <li><b>Image Extraction</b>: Extract charts, diagrams, photos from PDFs</li>
            <li><b>GPT-4 Vision</b>: Describe images in detail (including data from charts)</li>
            <li><b>Unified Search</b>: Search across both text AND images</li>
            <li><b>Visual Answers</b>: Show retrieved images alongside answers</li>
        </ul>
        <p><b>This solves the fundamental limitation of text-only RAG!</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'tab4_processed' not in st.session_state:
        st.session_state.tab4_processed = False
        st.session_state.tab4_text_chunks = []
        st.session_state.tab4_images = []
        st.session_state.tab4_store = None

    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF document (works best with charts, diagrams, or images)",
        type=['pdf'],
        key="tab4_upload"
    )

    if uploaded_file:
        col1, col2 = st.columns([3, 1])

        with col1:
            process_images = st.checkbox(
                "Enable Vision RAG (extract and process images)",
                value=True,
                key="tab4_enable_vision"
            )

        with col2:
            if st.button("Process Document", key="tab4_process"):
                with st.spinner("Processing document (this may take a minute)..."):
                    # Save uploaded file temporarily
                    temp_path = Path(f"/tmp/{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Extract text
                    text = extract_text_from_pdf(uploaded_file)

                    # Chunk text
                    chunker = SemanticChunker(similarity_threshold=0.7)
                    chunks = chunker.chunk(text)
                    st.session_state.tab4_text_chunks = chunks

                    # Initialize multimodal store
                    store = MultimodalVectorStore(collection_name="tab4_vision")
                    store.clear()

                    # Add text chunks
                    store.add_text_chunks(chunks)

                    # Extract and process images if enabled
                    images = []
                    if process_images:
                        progress = st.progress(0)
                        status = st.empty()

                        # Extract images
                        status.text("Extracting images from PDF...")
                        extractor = ImageExtractor()
                        extractor.clear_images()
                        images = extractor.extract_images(str(temp_path))

                        # Process images with GPT-4 Vision
                        if images:
                            from src.vision_rag.vision_embedder import VisionEmbedder
                            vision_embedder = VisionEmbedder()

                            failed_count = 0
                            for i, image_info in enumerate(images):
                                status.text(
                                    f"Describing image {i+1}/{len(images)} with GPT-4 Vision..."
                                )
                                # Actually describe the image here
                                try:
                                    image_info.description = vision_embedder.describe_image(
                                        image_info.image_path
                                    )
                                    if image_info.description.startswith("[DESCRIPTION_FAILED]"):
                                        failed_count += 1
                                except Exception as e:
                                    image_info.description = f"[DESCRIPTION_FAILED] {e}"
                                    failed_count += 1

                                progress.progress((i + 1) / len(images))

                            # Add images to store (descriptions already generated)
                            store.add_images(images)

                            if failed_count > 0:
                                st.warning(
                                    f"⚠️ {failed_count}/{len(images)} image descriptions failed. "
                                    f"This may affect retrieval quality. Check that your "
                                    f"VISION_MODEL is set to a valid model (e.g., gpt-4o)."
                                )

                        progress.empty()
                        status.empty()

                    st.session_state.tab4_images = images
                    st.session_state.tab4_store = store
                    st.session_state.tab4_processed = True

                    st.success(
                        f"✅ Processed {len(chunks)} text chunks and "
                        f"{len(images)} images!"
                    )

    # Show statistics
    if st.session_state.tab4_processed:
        st.markdown("---")
        st.subheader("📊 Document Statistics")

        col1, col2, col3, col4 = st.columns(4)

        stats = st.session_state.tab4_store.get_statistics()

        with col1:
            st.metric("Text Chunks", stats['text_chunks'])

        with col2:
            st.metric("Images", stats['images'])

        with col3:
            st.metric("Total Items", stats['total_items'])

        with col4:
            multimodal = stats['images'] > 0
            st.metric("Mode", "Multimodal" if multimodal else "Text-only")

        # Show sample images
        if st.session_state.tab4_images:
            with st.expander(f"📸 View Extracted Images ({len(st.session_state.tab4_images)})"):
                cols = st.columns(3)
                for i, img_info in enumerate(st.session_state.tab4_images[:6]):
                    with cols[i % 3]:
                        try:
                            image = Image.open(img_info.image_path)
                            st.image(image, caption=f"Page {img_info.page}", use_container_width=True)
                            if img_info.description:
                                st.caption(f"Description: {img_info.description[:100]}...")
                        except:
                            st.error(f"Error loading image {i+1}")

    # Query interface
    if st.session_state.tab4_processed:
        st.markdown("---")
        st.subheader("🔍 Query with Vision RAG")

        # Mode selector
        mode = st.radio(
            "Comparison Mode:",
            ["Text-only RAG", "Vision RAG (Text + Images)", "Side-by-Side Comparison"],
            key="tab4_mode"
        )

        query = st.text_input(
            "Enter your question:",
            placeholder="e.g., What was the Q3 revenue growth? or Describe the architecture diagram",
            key="tab4_query"
        )

        if query and st.button("Search", key="tab4_search"):
            retriever = MultimodalRetriever(st.session_state.tab4_store)
            generator = VisionGenerator()

            if mode == "Side-by-Side Comparison":
                st.markdown("### 📊 Text-only vs Vision RAG")

                col1, col2 = st.columns(2)

                # Text-only
                with col1:
                    st.markdown("#### 📄 Text-only RAG")
                    with st.spinner("Searching (text-only)..."):
                        results = retriever.retrieve(query, k=5, include_images=False)

                        response = generator.generate(
                            query,
                            results['text_results'],
                            []
                        )

                        st.info(response.answer)

                        # Metrics
                        st.metric("Sources Used", len(results['text_results']))
                        st.metric("Images Used", 0)

                        # Show limitations
                        if st.session_state.tab4_images:
                            st.warning(
                                f"⚠️ {len(st.session_state.tab4_images)} images "
                                f"in document were IGNORED"
                            )

                # Vision RAG
                with col2:
                    st.markdown("#### 👁️ Vision RAG")
                    with st.spinner("Searching (text + images)..."):
                        results = retriever.retrieve(query, k=5, include_images=True)

                        response = generator.generate(
                            query,
                            results['text_results'],
                            results['image_results']
                        )

                        st.success(response.answer)

                        # Metrics
                        st.metric("Sources Used", len(results['all_results']))
                        st.metric("Images Used", len(results['image_results']))

                        # Show images
                        if response.images:
                            st.markdown("**Retrieved Images:**")
                            for img_path in response.images:
                                try:
                                    image = Image.open(img_path)
                                    st.image(image, use_container_width=True)
                                except:
                                    st.error("Error loading image")

                # Comparison summary
                st.markdown("---")
                st.markdown("""
                <div class="info-box">
                <h4>💡 Key Differences:</h4>
                <ul>
                    <li><b>Text-only</b>: Can only use text descriptions, misses visual information</li>
                    <li><b>Vision RAG</b>: Uses charts, diagrams, and images for precise answers</li>
                    <li><b>Result</b>: Vision RAG provides specific numbers and details from images!</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

            else:
                # Single mode
                include_images = (mode == "Vision RAG (Text + Images)")

                with st.spinner(f"Searching with {mode}..."):
                    results = retriever.retrieve(
                        query,
                        k=5,
                        include_images=include_images
                    )

                    response = generator.generate(
                        query,
                        results['text_results'],
                        results['image_results'] if include_images else []
                    )

                    # Display answer
                    st.markdown("### 💬 Answer")
                    if include_images:
                        st.success(response.answer)
                    else:
                        st.info(response.answer)

                    # Display retrieved images
                    if include_images and response.images:
                        st.markdown("### 🖼️ Retrieved Images")
                        cols = st.columns(2)
                        for i, img_path in enumerate(response.images):
                            with cols[i % 2]:
                                try:
                                    image = Image.open(img_path)
                                    st.image(image, use_container_width=True)

                                    # Show description
                                    img_result = next(
                                        (r for r in results['image_results']
                                         if r.image_path == img_path),
                                        None
                                    )
                                    if img_result:
                                        with st.expander("View Description"):
                                            st.write(img_result.content)
                                except:
                                    st.error(f"Error loading image {i+1}")

                    # Display text results
                    st.markdown("### 📄 Retrieved Text Chunks")
                    for i, result in enumerate(results['text_results'], 1):
                        with st.expander(f"Chunk {i} - Page {result.page} (Score: {result.score:.3f})"):
                            st.write(result.content)

                    # Metrics
                    st.markdown("### 📈 Metrics")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Results", len(results['all_results']))

                    with col2:
                        st.metric("Text Chunks", len(results['text_results']))

                    with col3:
                        st.metric("Images", len(results['image_results']))

                    with col4:
                        avg_score = (
                            sum(r.score for r in results['all_results']) /
                            len(results['all_results'])
                            if results['all_results'] else 0
                        )
                        st.metric("Avg Score", f"{avg_score:.3f}")

    # Educational content
    with st.expander("📚 Learn: How Vision RAG Works"):
        st.markdown("""
        ### Vision RAG Pipeline

        #### Step 1: Extract Images from PDF
        ```python
        # Use PyMuPDF to extract images
        doc = fitz.open("document.pdf")
        images = []
        for page in doc:
            for img in page.get_images():
                image_data = doc.extract_image(img)
                images.append(image_data)
        ```

        #### Step 2: Describe Images with GPT-4 Vision
        ```python
        # Send each image to GPT-4o (vision-capable)
        description = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail..."},
                    {"type": "image_url", "image_url": {"url": image_base64}}
                ]
            }]
        )

        # GPT-4V returns detailed description:
        # "Bar chart showing Q3 revenue of $12.3M, up 45% from
        #  Q3 2023 ($8.5M). Chart has blue bars with labels..."
        ```

        #### Step 3: Embed Image Descriptions
        ```python
        # Embed the description (not the image itself)
        description_embedding = embed(description)

        # Store with metadata
        vector_db.add(
            embedding=description_embedding,
            metadata={"type": "image", "path": image_path}
        )
        ```

        #### Step 4: Unified Retrieval
        ```python
        # Search returns both text AND images
        results = vector_db.search(query_embedding)

        # Results might include:
        # - Text chunk: "Q3 showed strong growth..."
        # - Image: Bar chart with exact numbers
        # - Text chunk: "Revenue targets exceeded..."
        ```

        #### Step 5: Generate with Visual Context
        ```python
        context = format_context(text_chunks, image_descriptions)

        answer = gpt4.generate(query, context)
        # Answer: "Q3 revenue was $12.3M, a 45% increase from $8.5M"
        # (precise numbers from the chart!)
        ```

        ### Why This Is Revolutionary

        **Before (Text-only):**
        - Q: "What was Q3 revenue growth?"
        - A: "The report mentions strong growth" ❌ (vague)

        **After (Vision RAG):**
        - Q: "What was Q3 revenue growth?"
        - A: "45% growth, from $8.5M to $12.3M" ✅ (precise!)
        - [Shows chart image as proof]

        ### Performance Improvement

        - Text-only accuracy: ~85%
        - Vision RAG accuracy: ~95-98% ⬆️⬆️

        ### Cost Considerations

        - GPT-4 Vision: ~$0.01-0.03 per image
        - Worth it for documents with critical visual information!
        - For 10 images: ~$0.30 processing cost
        """)

    # Use cases
    with st.expander("🎯 Perfect Use Cases for Vision RAG"):
        st.markdown("""
        ### When to Use Vision RAG

        ✅ **Ideal For:**
        1. **Financial Reports** - Charts with revenue, growth, metrics
        2. **Technical Documentation** - Architecture diagrams, flowcharts
        3. **Product Manuals** - Assembly instructions with photos
        4. **Scientific Papers** - Graphs, data visualizations
        5. **Medical Records** - Scans, diagrams, charts
        6. **Real Estate** - Floor plans, property photos
        7. **Analytics Dashboards** - Performance charts

        ❌ **Not Needed For:**
        1. Plain text documents (novels, articles)
        2. Simple Q&A without visuals
        3. Code repositories (text-based)

        ### eBay Use Case Example

        **Seller Help Documentation:**
        - Upload PDF: "Seller Performance Guide"
        - Contains: Performance charts, fee tables, category images

        **Query:** "What's the fee structure for electronics?"

        **Vision RAG Response:**
        - Retrieves fee table image
        - Extracts exact percentages from table
        - Shows relevant category image
        - Provides precise answer with visual proof!

        **Impact:** Sellers get accurate fee info instead of vague answers
        """)
