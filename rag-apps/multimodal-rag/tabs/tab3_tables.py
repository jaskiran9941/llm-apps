"""
Tab 3: Table RAG - Text + Images + Tables
Demonstrates table extraction, embedding, and querying.
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import time

from src.table_rag.table_extractor import TableExtractor
from src.table_rag.table_processor import TableProcessor
from src.table_rag.table_embedder import TableEmbedder
from src.table_rag.table_query_parser import TableQueryParser
from src.multimodal.multimodal_store import MultimodalStore
from src.multimodal.multimodal_retriever import MultimodalRetriever
from src.multimodal.multimodal_generator import MultimodalGenerator
from src.common.config import Config
from src.common.utils import format_cost, format_time


def render():
    """Render Table RAG tab."""

    st.header("📊 Table RAG: Structured Data + Semantic Search")

    st.markdown("""
    This tab demonstrates **table extraction and hybrid querying**:
    - Extract tables from PDFs, Excel, CSV files
    - Generate semantic captions with GPT-4
    - Support both semantic and structured queries
    - Interactive table preview and export
    """)

    # Initialize components
    if 'table_store' not in st.session_state:
        st.session_state.table_store = MultimodalStore()
        st.session_state.table_extractor = TableExtractor()
        st.session_state.table_processor = TableProcessor()
        st.session_state.table_embedder = TableEmbedder()
        st.session_state.query_parser = TableQueryParser()
        st.session_state.retriever = MultimodalRetriever(st.session_state.table_store)
        st.session_state.generator = MultimodalGenerator()

    # Tabs for workflow
    workflow_tab1, workflow_tab2, workflow_tab3 = st.tabs([
        "1️⃣ Upload & Extract",
        "2️⃣ Preview & Process",
        "3️⃣ Query Tables"
    ])

    # === TAB 1: Upload & Extract ===
    with workflow_tab1:
        st.subheader("Upload Documents with Tables")

        col1, col2 = st.columns([2, 1])

        with col1:
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload file (PDF, Excel, CSV)",
                type=['pdf', 'xlsx', 'xls', 'csv'],
                help="Upload a document containing tables"
            )

            # Or use sample
            use_sample = st.checkbox("Use sample CSV data", value=True)

            if use_sample:
                sample_path = Config.SAMPLE_DOCS_DIR / "sample_data.csv"
                if sample_path.exists():
                    st.info(f"📁 Using sample file: `{sample_path.name}`")
                    uploaded_file = sample_path

        with col2:
            st.markdown("**Table Extraction:**")
            st.markdown("- PDF: `pdfplumber`")
            st.markdown("- Excel: `pandas`")
            st.markdown("- CSV: Auto-detect")
            st.markdown("**Features:**")
            st.markdown("- Multi-sheet support")
            st.markdown("- Auto-chunking")
            st.markdown("- Data validation")

        # Extract button
        if st.button("🔍 Extract Tables", type="primary", disabled=uploaded_file is None):
            with st.spinner("Extracting tables..."):
                try:
                    # Save uploaded file if needed
                    if isinstance(uploaded_file, Path):
                        file_path = uploaded_file
                    else:
                        file_path = Config.UPLOADS_DIR / uploaded_file.name
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())

                    # Extract based on file type
                    file_ext = file_path.suffix.lower()

                    if file_ext == '.csv':
                        tables = st.session_state.table_extractor.extract_from_csv(file_path)
                    elif file_ext in ['.xlsx', '.xls']:
                        tables = st.session_state.table_extractor.extract_from_excel(file_path)
                    elif file_ext == '.pdf':
                        tables = st.session_state.table_extractor.extract_from_pdf(file_path)
                    else:
                        st.error("Unsupported file type")
                        return

                    # Store in session state
                    st.session_state.extracted_tables = tables

                    st.success(f"✅ Extracted {len(tables)} table(s)")

                    # Show summary
                    for i, table in enumerate(tables):
                        st.write(f"**Table {i+1}:** {table.num_rows} rows × {table.num_cols} columns")

                except Exception as e:
                    st.error(f"Error extracting tables: {e}")

    # === TAB 2: Preview & Process ===
    with workflow_tab2:
        st.subheader("Preview and Process Tables")

        if 'extracted_tables' not in st.session_state:
            st.info("👈 Please extract tables first in the Upload tab")
            return

        tables = st.session_state.extracted_tables

        if not tables:
            st.warning("No tables extracted")
            return

        # Table selector
        table_idx = st.selectbox(
            "Select table to preview",
            range(len(tables)),
            format_func=lambda i: f"Table {i+1} ({tables[i].num_rows}×{tables[i].num_cols})"
        )

        selected_table = tables[table_idx]

        # Display table info
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", selected_table.num_rows)
        col2.metric("Columns", selected_table.num_cols)
        col3.metric("Source", selected_table.source_type.upper())
        col4.metric("Page/Sheet", selected_table.page)

        # Show table data
        st.markdown("**Table Preview:**")
        df = pd.DataFrame(selected_table.table_data)
        st.dataframe(df, use_container_width=True)

        # Export option
        if st.button("📥 Export to CSV"):
            csv_path = Config.TABLES_DIR / f"{selected_table.table_id}.csv"
            st.session_state.table_processor.export_to_csv(selected_table, str(csv_path))
            st.success(f"Exported to `{csv_path}`")

        # Process & embed
        st.markdown("---")
        st.subheader("Process and Embed Tables")

        col1, col2 = st.columns(2)

        with col1:
            generate_captions = st.checkbox(
                "Generate GPT-4 captions",
                value=True,
                help="Generate semantic descriptions (costs ~$0.012 per table)"
            )

        with col2:
            # Show cost estimate
            cost_info = st.session_state.table_embedder.estimate_cost(tables, generate_captions)
            st.info(f"💰 Estimated cost: {format_cost(cost_info['total_cost'])}")

        if st.button("🚀 Process & Store Tables", type="primary"):
            with st.spinner("Processing tables..."):
                progress_bar = st.progress(0)

                try:
                    # Process tables
                    all_embedded = []

                    for i, table in enumerate(tables):
                        # Validate
                        if not st.session_state.table_processor.validate_table(table):
                            st.warning(f"Skipping invalid table {i+1}")
                            continue

                        # Chunk if needed
                        chunks = st.session_state.table_processor.chunk_large_table(table)

                        # Embed
                        embedded = st.session_state.table_embedder.embed_tables(chunks, generate_captions)
                        all_embedded.extend(embedded)

                        progress_bar.progress((i + 1) / len(tables))

                    # Store in vector DB
                    st.session_state.table_store.add_tables(all_embedded)

                    st.success(f"✅ Processed and stored {len(all_embedded)} table chunks")

                    # Show sample caption
                    if generate_captions and all_embedded:
                        sample_table, _, _ = all_embedded[0]
                        if sample_table.description:
                            with st.expander("📝 Sample Generated Caption"):
                                st.write(sample_table.description)

                except Exception as e:
                    st.error(f"Error processing tables: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    # === TAB 3: Query Tables ===
    with workflow_tab3:
        st.subheader("Query Tables")

        # Check if tables are stored
        stats = st.session_state.table_store.get_stats()
        if stats['by_type']['table'] == 0:
            st.info("👈 Please process and store tables first")
            return

        st.success(f"📊 {stats['by_type']['table']} table(s) in vector store")

        # Query examples
        with st.expander("💡 Example Queries"):
            st.markdown("""
            **Semantic Queries:**
            - "What was Q3 revenue?"
            - "Show the pricing structure"
            - "Which products are in the Electronics category?"

            **Structured Queries:**
            - "Products with price greater than 100"
            - "Revenue between 100000 and 200000"
            - "Items in Q2 2024"

            **Hybrid Queries:**
            - "Average Q3 revenue"
            - "Total revenue from Q1 to Q3"
            - "Maximum price in Electronics category"
            """)

        # Query input
        query = st.text_input(
            "Enter your question:",
            placeholder="e.g., What was Q3 revenue for Widget A?",
            help="Ask semantic or structured questions about the tables"
        )

        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                k_results = st.slider("Number of results", 1, 20, 5)
                table_weight = st.slider("Table weight", 0.0, 1.0, 0.7)
            with col2:
                include_sources = st.checkbox("Include source citations", value=True)
                auto_adjust = st.checkbox("Auto-adjust weights", value=True)

        # Query button
        if st.button("🔍 Search", type="primary", disabled=not query):
            with st.spinner("Searching..."):
                start_time = time.time()

                try:
                    # Parse query
                    query_info = st.session_state.query_parser.parse_query(query)

                    # Show query analysis
                    with st.expander("📊 Query Analysis"):
                        st.json(query_info)

                    # Retrieve
                    retrieval_results = st.session_state.retriever.retrieve(
                        query=query,
                        k=k_results,
                        table_weight=table_weight,
                        include_tables=True,
                        include_text=False,
                        include_images=False,
                        include_audio=False,
                        auto_adjust_weights=auto_adjust
                    )

                    # Generate answer
                    result = st.session_state.generator.generate_answer(
                        query=query,
                        retrieval_results=retrieval_results['combined'],
                        include_sources=include_sources
                    )

                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(result.answer)

                    # Show metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Processing Time", format_time(result.processing_time))
                    col2.metric("Cost", format_cost(result.cost_estimate))
                    col3.metric("Sources Used", len(result.sources))

                    # Show sources
                    if result.sources:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(result.sources, 1):
                                st.markdown(f"**{i}. {source.source_info}** (score: {source.score:.3f})")

                                # Show table data if available
                                if source.type == "table" and "table_data" in source.metadata:
                                    import json
                                    table_data = json.loads(source.metadata["table_data"])
                                    df = pd.DataFrame(table_data)
                                    st.dataframe(df.head(10), use_container_width=True)
                                else:
                                    st.text(source.content[:300] + "..." if len(source.content) > 300 else source.content)

                                st.markdown("---")

                except Exception as e:
                    st.error(f"Error during search: {e}")
                    import traceback
                    st.code(traceback.format_exc())
