"""
Document management UI component.

Handles:
- Document upload
- Document listing
- Document deletion
"""

import streamlit as st
from pathlib import Path
from typing import List, Dict
from src.pipeline.indexing_pipeline import IndexingPipeline


def render_upload_section(indexing_pipeline: IndexingPipeline, upload_dir: Path):
    """
    Render document upload interface.

    Args:
        indexing_pipeline: Pipeline for indexing documents
        upload_dir: Directory to save uploaded files
    """
    st.header("📤 Upload Documents")

    st.markdown("""
    Upload PDF documents to add them to the knowledge base.
    The system will:
    1. Extract text from the PDF
    2. Split into chunks
    3. Generate embeddings
    4. Store in vector database
    """)

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF files to index"
    )

    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s)")

        # Upload button
        if st.button("🚀 Upload and Index", type="primary"):
            with st.spinner("Processing documents..."):
                results = []

                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, uploaded_file in enumerate(uploaded_files):
                    # Save file
                    file_path = upload_dir / uploaded_file.name
                    file_path.write_bytes(uploaded_file.read())

                    # Update progress
                    status_text.text(f"Processing {uploaded_file.name}...")

                    # Index document
                    result = indexing_pipeline.index_document(file_path)
                    results.append(result)

                    # Update progress
                    progress_bar.progress((i + 1) / len(uploaded_files))

                progress_bar.empty()
                status_text.empty()

                # Show results
                st.subheader("Indexing Results")

                for result in results:
                    if result.success:
                        st.success(f"✅ {result.metadata['filename']}")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Chunks", result.num_chunks)
                        with col2:
                            st.metric("Cost", f"${result.cost:.4f}")
                        with col3:
                            st.metric("Time", f"{result.metadata.get('processing_time', 0):.1f}s")
                    else:
                        st.error(f"❌ {result.metadata['filename']}: {result.error_message}")

                # Summary
                successful = sum(1 for r in results if r.success)
                total_cost = sum(r.cost for r in results)
                total_chunks = sum(r.num_chunks for r in results)

                st.markdown("---")
                st.markdown(f"""
                **Summary:**
                - Successful: {successful}/{len(results)}
                - Total chunks: {total_chunks}
                - Total cost: ${total_cost:.4f}
                """)


def render_document_list(vector_store):
    """
    Render list of indexed documents with delete option.

    Args:
        vector_store: Vector store to query documents
    """
    st.header("📚 Indexed Documents")

    # Get documents
    documents = vector_store.list_documents()

    if not documents:
        st.info("No documents indexed yet. Upload some PDFs to get started!")
        return

    # Display documents
    st.write(f"Total documents: {len(documents)}")

    for doc in documents:
        with st.expander(f"📄 {doc['filename']}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Document ID:** {doc['doc_id']}")
                st.write(f"**Chunks:** {doc['num_chunks']}")

            with col2:
                if st.button("🗑️ Delete", key=f"delete_{doc['doc_id']}"):
                    # Confirm deletion
                    if st.session_state.get(f"confirm_delete_{doc['doc_id']}", False):
                        vector_store.delete_document(doc['doc_id'])
                        st.success(f"Deleted {doc['filename']}")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{doc['doc_id']}"] = True
                        st.warning("Click again to confirm deletion")


def render_storage_stats(vector_store):
    """
    Render storage statistics.

    Args:
        vector_store: Vector store to get stats from
    """
    stats = vector_store.get_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Chunks",
            stats.get("total_chunks", 0),
            help="Number of text chunks stored"
        )

    with col2:
        st.metric(
            "Total Documents",
            stats.get("total_documents", 0),
            help="Number of indexed documents"
        )

    with col3:
        avg_chunks = (
            stats.get("total_chunks", 0) / max(1, stats.get("total_documents", 1))
        )
        st.metric(
            "Avg Chunks/Doc",
            f"{avg_chunks:.0f}",
            help="Average chunks per document"
        )
