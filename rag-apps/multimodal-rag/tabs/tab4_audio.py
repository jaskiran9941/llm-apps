"""
Tab 4: Full Multimodal RAG - Text + Images + Tables + Audio
Complete implementation with audio upload, transcription, and querying.
"""

import streamlit as st
from pathlib import Path
import time

from src.audio_rag.audio_extractor import AudioExtractor
from src.audio_rag.audio_processor import AudioProcessor
from src.audio_rag.audio_embedder import AudioEmbedder
from src.multimodal.multimodal_store import MultimodalStore
from src.multimodal.multimodal_retriever import MultimodalRetriever
from src.multimodal.multimodal_generator import MultimodalGenerator
from src.common.config import Config
from src.common.utils import format_cost, format_time, format_timestamp


def render():
    """Render full multimodal RAG tab with audio support."""

    st.header("🎵 Full Multimodal: Text + Images + Tables + Audio")

    st.markdown("""
    **Full multimodal RAG** combines ALL modalities:
    - 📄 Text chunks
    - 🖼️ Image descriptions
    - 📊 Table data
    - 🎵 Audio transcripts with timestamps
    """)

    # Initialize components
    if 'audio_store' not in st.session_state:
        st.session_state.audio_store = MultimodalStore()
        st.session_state.audio_extractor = AudioExtractor()
        st.session_state.audio_processor = AudioProcessor()
        st.session_state.audio_embedder = AudioEmbedder()
        st.session_state.audio_retriever = MultimodalRetriever(st.session_state.audio_store)
        st.session_state.audio_generator = MultimodalGenerator()

    # Tabs for workflow
    workflow_tab1, workflow_tab2, workflow_tab3 = st.tabs([
        "1️⃣ Upload & Transcribe",
        "2️⃣ Preview & Enrich",
        "3️⃣ Query Audio"
    ])

    # === TAB 1: Upload & Transcribe ===
    with workflow_tab1:
        render_upload_tab()

    # === TAB 2: Preview & Enrich ===
    with workflow_tab2:
        render_preview_tab()

    # === TAB 3: Query Audio ===
    with workflow_tab3:
        render_query_tab()


def render_upload_tab():
    """Render upload and transcription tab."""
    st.subheader("Upload Audio Files")

    col1, col2 = st.columns([2, 1])

    with col1:
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload audio file",
            type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm'],
            help="Supported formats: MP3, WAV, M4A, FLAC, OGG, WebM",
            key="audio_file_uploader"
        )

        if uploaded_file:
            # Show file info
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"📁 **{uploaded_file.name}** ({file_size_mb:.2f} MB)")

            if file_size_mb > Config.MAX_AUDIO_FILE_SIZE_MB:
                st.warning(f"Large file detected (>{Config.MAX_AUDIO_FILE_SIZE_MB}MB). Will be split for processing.")

    with col2:
        st.markdown("**Supported Formats:**")
        st.markdown("- 🎵 MP3, WAV, M4A")
        st.markdown("- 🎵 FLAC, OGG, WebM")
        st.markdown("**Features:**")
        st.markdown("- Whisper API transcription")
        st.markdown("- Segment-level timestamps")
        st.markdown("- Auto file splitting")

    # Cost estimate
    if uploaded_file:
        # Estimate based on file size (rough approximation)
        estimated_duration_min = (uploaded_file.size / (1024 * 1024)) * 1.5  # ~1.5 min per MB for typical audio
        estimated_cost = estimated_duration_min * Config.COST_WHISPER_PER_MINUTE
        st.info(f"💰 Estimated transcription cost: {format_cost(estimated_cost)} (based on ~{estimated_duration_min:.1f} min)")

    # Transcribe button
    if st.button("🎤 Transcribe Audio", type="primary", disabled=uploaded_file is None, key="audio_transcribe_btn"):
        with st.spinner("Transcribing audio with Whisper API..."):
            try:
                # Save uploaded file
                file_path = Config.AUDIO_DIR / uploaded_file.name
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                start_time = time.time()

                # Transcribe
                audio_info = st.session_state.audio_extractor.transcribe(file_path)

                processing_time = time.time() - start_time

                # Store in session state
                st.session_state.current_audio = audio_info

                # Show success
                st.success(f"✅ Transcription complete!")

                # Show stats
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Duration", format_timestamp(audio_info.duration))
                col2.metric("Segments", len(audio_info.segments))
                col3.metric("Language", audio_info.language.upper())
                col4.metric("Processing", format_time(processing_time))

                # Show transcript preview
                with st.expander("📝 Transcript Preview", expanded=True):
                    st.text_area(
                        "Full Transcript",
                        audio_info.transcript[:2000] + ("..." if len(audio_info.transcript) > 2000 else ""),
                        height=200,
                        disabled=True
                    )

                # Save transcript
                transcript_path = st.session_state.audio_extractor.save_transcript(audio_info)
                st.info(f"📄 Transcript saved to: `{transcript_path.name}`")

            except Exception as e:
                st.error(f"Error transcribing audio: {e}")
                import traceback
                st.code(traceback.format_exc())


def render_preview_tab():
    """Render preview and enrichment tab."""
    st.subheader("Preview and Enrich Audio")

    if 'current_audio' not in st.session_state:
        st.info("👈 Please transcribe an audio file first in the Upload tab")
        return

    audio_info = st.session_state.current_audio

    # Audio info display
    st.markdown("### Audio Information")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("File", Path(audio_info.audio_path).name)
    col2.metric("Duration", format_timestamp(audio_info.duration))
    col3.metric("Segments", len(audio_info.segments))
    col4.metric("Language", audio_info.language.upper())

    # Segment browser
    st.markdown("### Segment Browser")
    st.markdown("Browse transcript segments with timestamps:")

    # Create segment dataframe for display
    segment_data = []
    for seg in audio_info.segments:
        segment_data.append({
            "Start": format_timestamp(seg.start_time),
            "End": format_timestamp(seg.end_time),
            "Text": seg.text[:100] + ("..." if len(seg.text) > 100 else ""),
            "Speaker": seg.speaker or "—"
        })

    if segment_data:
        st.dataframe(segment_data, use_container_width=True, height=300)

    # Enrichment section
    st.markdown("---")
    st.markdown("### Enrich with AI Analysis")

    col1, col2 = st.columns(2)

    with col1:
        enrich_topics = st.checkbox("Extract Topics", value=True, help="Detect key topics discussed", key="audio_enrich_topics")
        enrich_summary = st.checkbox("Generate Summary", value=True, help="Create executive summary", key="audio_enrich_summary")

    with col2:
        enrich_entities = st.checkbox("Extract Entities", value=True, help="Find people, companies, dates", key="audio_enrich_entities")
        rechunk_segments = st.checkbox("Re-chunk Segments", value=False, help="Combine short segments", key="audio_rechunk")

    # Estimate cost
    num_analyses = sum([enrich_topics, enrich_summary, enrich_entities])
    estimated_cost = num_analyses * 0.01  # ~$0.01 per GPT-4 call
    st.info(f"💰 Estimated enrichment cost: {format_cost(estimated_cost)}")

    if st.button("🧠 Enrich Audio", type="primary", key="audio_enrich_btn"):
        with st.spinner("Enriching audio with AI analysis..."):
            try:
                progress_bar = st.progress(0)

                # Topics
                if enrich_topics and not audio_info.topics:
                    audio_info.topics = st.session_state.audio_processor.detect_topics(audio_info.transcript)
                    progress_bar.progress(33)

                # Summary
                if enrich_summary and not audio_info.summary:
                    audio_info.summary = st.session_state.audio_processor.summarize_transcript(audio_info)
                    progress_bar.progress(66)

                # Entities
                if enrich_entities and not audio_info.entities:
                    audio_info.entities = st.session_state.audio_processor.extract_entities(audio_info.transcript)
                    progress_bar.progress(100)

                # Re-chunk if requested
                if rechunk_segments:
                    audio_info.segments = st.session_state.audio_processor.chunk_segments(audio_info)

                st.session_state.current_audio = audio_info
                st.success("✅ Enrichment complete!")

            except Exception as e:
                st.error(f"Error enriching audio: {e}")
                import traceback
                st.code(traceback.format_exc())

    # Display enrichment results
    if audio_info.topics or audio_info.summary or audio_info.entities:
        st.markdown("---")
        st.markdown("### Enrichment Results")

        if audio_info.topics:
            st.markdown("**🏷️ Topics:**")
            st.markdown(", ".join([f"`{topic}`" for topic in audio_info.topics]))

        if audio_info.summary:
            st.markdown("**📋 Summary:**")
            st.info(audio_info.summary)

        if audio_info.entities:
            st.markdown("**👥 Entities:**")
            for entity_type, entities in audio_info.entities.items():
                if entities:
                    st.markdown(f"- **{entity_type.title()}:** {', '.join(entities)}")

    # Embed and store
    st.markdown("---")
    st.markdown("### Store in Vector Database")

    # Cost estimate for embedding
    cost_info = st.session_state.audio_embedder.estimate_cost([audio_info])
    st.info(f"💰 Embedding cost: {format_cost(cost_info['embedding_cost'])} ({cost_info['num_segments']} segments)")

    if st.button("🚀 Embed & Store Audio", type="primary", key="audio_embed_btn"):
        with st.spinner("Embedding audio segments..."):
            try:
                progress_bar = st.progress(0)

                # Embed all segments
                embedded_segments = st.session_state.audio_embedder.embed_audio(audio_info)
                progress_bar.progress(50)

                # Format for storage: (AudioInfo, AudioSegment, embedding, enriched_text)
                store_data = [
                    (audio_info, segment, embedding, enriched_text)
                    for segment, embedding, enriched_text in embedded_segments
                ]

                # Store in vector DB
                st.session_state.audio_store.add_audio_segments(store_data)
                progress_bar.progress(100)

                st.success(f"✅ Stored {len(embedded_segments)} audio segments in vector database")

                # Show sample
                if embedded_segments:
                    with st.expander("📝 Sample Embedded Text"):
                        _, _, sample_text = embedded_segments[0]
                        st.code(sample_text[:500] + "..." if len(sample_text) > 500 else sample_text)

            except Exception as e:
                st.error(f"Error storing audio: {e}")
                import traceback
                st.code(traceback.format_exc())


def render_query_tab():
    """Render query tab for audio search."""
    st.subheader("Query Audio Content")

    # Check if audio is stored
    stats = st.session_state.audio_store.get_stats()
    if stats['by_type']['audio'] == 0:
        st.info("👈 Please transcribe and store audio first")
        return

    st.success(f"🎵 {stats['by_type']['audio']} audio segment(s) in vector store")

    # Also show other modalities
    other_modalities = []
    if stats['by_type']['text'] > 0:
        other_modalities.append(f"📄 {stats['by_type']['text']} text")
    if stats['by_type']['table'] > 0:
        other_modalities.append(f"📊 {stats['by_type']['table']} tables")
    if stats['by_type']['image'] > 0:
        other_modalities.append(f"🖼️ {stats['by_type']['image']} images")

    if other_modalities:
        st.info(f"Also available: {', '.join(other_modalities)}")

    # Query examples
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Audio-Specific Queries:**
        - "What was discussed about marketing?"
        - "What did they say about revenue?"
        - "List all action items mentioned"
        - "What topics were covered?"

        **Timestamp Queries:**
        - "What was mentioned at the beginning?"
        - "Summarize the main discussion"

        **Cross-Modal Queries (if other modalities loaded):**
        - "Compare what was said with the table data"
        - "Explain the chart mentioned in the audio"
        """)

    # Query input
    query = st.text_input(
        "Enter your question:",
        placeholder="e.g., What did they discuss about revenue growth?",
        help="Ask questions about the audio content",
        key="audio_query_input"
    )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            k_results = st.slider("Number of results", 1, 20, 5, key="audio_k_results")
            audio_weight = st.slider("Audio weight", 0.0, 1.0, 0.7, key="audio_weight")
        with col2:
            include_sources = st.checkbox("Show source segments", value=True, key="audio_include_sources")
            include_other = st.checkbox("Include other modalities", value=True, key="audio_include_other")

    # Query button
    if st.button("🔍 Search", type="primary", disabled=not query, key="audio_search_btn"):
        with st.spinner("Searching audio content..."):
            start_time = time.time()

            try:
                # Retrieve
                retrieval_results = st.session_state.audio_retriever.retrieve(
                    query=query,
                    k=k_results,
                    audio_weight=audio_weight,
                    include_audio=True,
                    include_text=include_other and stats['by_type']['text'] > 0,
                    include_tables=include_other and stats['by_type']['table'] > 0,
                    include_images=include_other and stats['by_type']['image'] > 0,
                    auto_adjust_weights=True
                )

                # Generate answer
                result = st.session_state.audio_generator.generate_answer(
                    query=query,
                    retrieval_results=retrieval_results['combined'],
                    include_sources=include_sources
                )

                processing_time = time.time() - start_time

                # Display answer
                st.markdown("### 💡 Answer")
                st.markdown(result.answer)

                # Show metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Processing Time", format_time(processing_time))
                col2.metric("Cost", format_cost(result.cost_estimate))
                col3.metric("Sources Used", len(result.sources))

                # Show sources with timestamps
                if include_sources and result.sources:
                    st.markdown("---")
                    st.markdown("### 📚 Source Segments")

                    for i, source in enumerate(result.sources, 1):
                        with st.expander(f"**{i}. {source.source_info}** (score: {source.score:.3f})"):
                            # Show type badge
                            if source.type == "audio":
                                st.markdown("🎵 **Audio Segment**")

                                # Show timestamp info
                                start = source.metadata.get('start_time', 0)
                                end = source.metadata.get('end_time', 0)
                                st.markdown(f"⏱️ **Timestamp:** {format_timestamp(start)} - {format_timestamp(end)}")

                                # Show speaker if available
                                speaker = source.metadata.get('speaker')
                                if speaker and speaker != "Unknown":
                                    st.markdown(f"🗣️ **Speaker:** {speaker}")

                                # Show topics if available
                                import json
                                topics_json = source.metadata.get('topics', '[]')
                                topics = json.loads(topics_json) if topics_json else []
                                if topics:
                                    st.markdown(f"🏷️ **Topics:** {', '.join(topics)}")

                            elif source.type == "table":
                                st.markdown("📊 **Table Data**")
                            elif source.type == "text":
                                st.markdown("📄 **Text Content**")
                            elif source.type == "image":
                                st.markdown("🖼️ **Image Description**")

                            # Show content
                            st.markdown("**Content:**")
                            st.text(source.content[:500] + "..." if len(source.content) > 500 else source.content)

            except Exception as e:
                st.error(f"Error during search: {e}")
                import traceback
                st.code(traceback.format_exc())
