"""
Streamlit UI for Live Stream Analyzer.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import time

from stream_capture import StreamCapture
from agent import LiveStreamAgent
from analyzer import StreamAnalyzer

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Live Stream Analyzer",
    page_icon="📹",
    layout="wide"
)

# Title and description
st.title("📹 Live Stream Analyzer")
st.markdown("""
This tool analyzes live streams and generates intelligent summaries of the content.
Using Gemini AI, it identifies key moments, content shown, and provides insights about the stream activity.
""")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# API Key
api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Enter your Google Gemini API key"
)

st.sidebar.markdown("---")

# Main input section
st.header("📹 Stream Input")

col1, col2 = st.columns([2, 1])

with col1:
    stream_url = st.text_input(
        "Live Stream URL",
        placeholder="https://www.youtube.com/watch?v=... or other live stream URL",
        help="Enter the URL of the live stream you want to analyze"
    )

with col2:
    duration = st.number_input(
        "Duration (minutes)",
        min_value=0.5,
        max_value=30.0,
        value=2.0,
        step=0.5,
        help="How long to capture the stream (0.5 - 30 minutes)"
    )

# Advanced settings
with st.expander("🔧 Advanced Settings"):
    frame_interval = st.slider(
        "Frame Extraction Interval (seconds)",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
        help="How often to capture and analyze frames. Lower = more detailed but slower and more expensive."
    )

st.markdown("---")

# Analysis button
if st.button("🚀 Start Analysis", type="primary", use_container_width=True):

    # Validation
    if not stream_url:
        st.error("❌ Please enter a stream URL")
        st.stop()

    if not api_key:
        st.error("❌ Please enter your Gemini API key in the sidebar")
        st.stop()

    # Create progress container
    progress_container = st.container()

    with progress_container:
        st.info(f"🎬 Starting analysis of {duration} minute(s) of stream...")

        # Initialize components
        try:
            capturer = StreamCapture()
            agent = LiveStreamAgent(api_key)
            analyzer = StreamAnalyzer(api_key)

        except Exception as e:
            st.error(f"❌ Error initializing components: {str(e)}")
            st.stop()

        # Step 1: Capture stream
        st.subheader("1️⃣ Capturing Stream")
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text(f"Recording stream for {duration} minutes...")
            video_file = capturer.capture_stream(stream_url, duration)
            progress_bar.progress(33)
            st.success(f"✅ Stream captured: {Path(video_file).name}")

        except Exception as e:
            st.error(f"❌ Error capturing stream: {str(e)}")
            st.info("💡 Make sure yt-dlp and FFmpeg are installed and the URL is a valid live stream.")
            st.stop()

        # Step 2: Extract frames
        st.subheader("2️⃣ Extracting Frames")

        try:
            status_text.text(f"Extracting frames every {frame_interval} seconds...")
            frames = capturer.extract_frames(video_file, interval_seconds=frame_interval)
            progress_bar.progress(50)
            st.success(f"✅ Extracted {len(frames)} frames")

            # Show sample frames
            if len(frames) >= 3:
                st.write("Sample frames:")
                cols = st.columns(min(3, len(frames)))
                for i, col in enumerate(cols):
                    with col:
                        st.image(frames[i], caption=f"Frame {i+1}", use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error extracting frames: {str(e)}")
            st.stop()

        # Step 3: Analyze frames
        st.subheader("3️⃣ Analyzing Frames with AI")

        try:
            status_text.text(f"Analyzing {len(frames)} frames with Gemini...")

            # Create a progress placeholder
            analysis_progress = st.empty()

            observations = []
            for i, frame_path in enumerate(frames):
                timestamp = i * frame_interval
                analysis_progress.text(f"Analyzing frame {i+1}/{len(frames)} (at {timestamp}s)...")

                observation = agent.analyze_frame(frame_path, i+1, timestamp)
                observations.append(observation)

                # Update progress
                current_progress = 50 + int((i + 1) / len(frames) * 33)
                progress_bar.progress(current_progress)

            analysis_progress.empty()
            st.success(f"✅ Analyzed {len(observations)} frames")

        except Exception as e:
            st.error(f"❌ Error analyzing frames: {str(e)}")
            st.stop()

        # Step 4: Generate summary
        st.subheader("4️⃣ Generating Summary")

        try:
            status_text.text("Generating comprehensive summary...")
            summary = analyzer.generate_summary(observations)
            progress_bar.progress(100)
            st.success("✅ Summary generated")

            # Save reports
            summary_file = analyzer.save_summary(summary)
            full_report_file = analyzer.save_full_report(observations, summary)

        except Exception as e:
            st.error(f"❌ Error generating summary: {str(e)}")
            st.stop()

        status_text.empty()
        progress_bar.empty()

    # Display results
    st.markdown("---")
    st.header("📊 Analysis Results")

    # Summary
    st.markdown(summary['summary_text'])

    # Download options
    st.markdown("---")
    st.subheader("💾 Download Reports")

    col1, col2 = st.columns(2)

    with col1:
        with open(summary_file, 'r') as f:
            summary_content = f.read()

        st.download_button(
            label="📄 Download Summary (TXT)",
            data=summary_content,
            file_name=f"stream_summary_{int(time.time())}.txt",
            mime="text/plain"
        )

    with col2:
        with open(full_report_file, 'r') as f:
            report_content = f.read()

        st.download_button(
            label="📋 Download Full Report (JSON)",
            data=report_content,
            file_name=f"stream_report_{int(time.time())}.json",
            mime="application/json"
        )

    # Frame-by-frame details
    with st.expander("🔍 View Frame-by-Frame Analysis"):
        for obs in observations:
            if not obs.get('error', False):
                st.markdown(f"### Frame {obs['frame_number']} (at {obs['timestamp']}s)")
                st.markdown(obs['analysis'])
                st.markdown("---")

    st.success("🎉 Analysis complete!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    Built with Streamlit & Google Gemini 2.0 Flash | Live Stream Analyzer
</div>
""", unsafe_allow_html=True)
