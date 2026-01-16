"""
Conversation Tone & Personality Analyzer
Upload audio/video files for analysis using Deepgram and Gemini.
"""

import os
import tempfile
import subprocess
from collections import deque
from dotenv import load_dotenv
import streamlit as st
import requests

from analyzer import ConversationAnalyzer

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Conversation Analyzer",
    page_icon="🎙️",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .speaker-card {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: #1a1a1a !important;
    }
    .speaker-card h3, .speaker-card p, .speaker-card strong, .speaker-card em {
        color: #1a1a1a !important;
    }
    .speaker-0 { background-color: #e3f2fd; border-left: 4px solid #2196f3; }
    .speaker-1 { background-color: #fce4ec; border-left: 4px solid #e91e63; }
    .speaker-2 { background-color: #e8f5e9; border-left: 4px solid #4caf50; }
    .speaker-3 { background-color: #fff3e0; border-left: 4px solid #ff9800; }
    .tone-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.25rem;
    }
    .tone-positive { background-color: #c8e6c9; color: #2e7d32 !important; }
    .tone-negative { background-color: #ffcdd2; color: #c62828 !important; }
    .tone-neutral { background-color: #fff9c4; color: #f57f17 !important; }
    .transcript-entry {
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        color: #1a1a1a !important;
    }
    .transcript-entry strong, .transcript-entry span {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)


def extract_audio_from_video(video_path: str, output_path: str) -> bool:
    """Extract audio from video file using ffmpeg."""
    try:
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return False


def transcribe_audio(audio_path: str, api_key: str) -> dict:
    """Transcribe audio using Deepgram API."""
    url = "https://api.deepgram.com/v1/listen"

    params = {
        "model": "nova-2",
        "language": "en",
        "punctuate": "true",
        "diarize": "true",
        "utterances": "true",
    }

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav",
    }

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    response = requests.post(url, params=params, headers=headers, data=audio_data)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Deepgram error: {response.status_code} - {response.text}")
        return None


def parse_transcription(result: dict) -> list:
    """Parse Deepgram transcription result into utterances."""
    utterances = []

    if not result:
        return utterances

    # Try to get utterances (with diarization)
    if "results" in result and "utterances" in result["results"]:
        for utt in result["results"]["utterances"]:
            utterances.append({
                "speaker": utt.get("speaker", 0),
                "text": utt.get("transcript", ""),
                "start": utt.get("start", 0),
                "end": utt.get("end", 0),
                "confidence": utt.get("confidence", 0),
            })
    # Fallback to channel alternatives
    elif "results" in result and "channels" in result["results"]:
        for channel in result["results"]["channels"]:
            for alt in channel.get("alternatives", []):
                if alt.get("transcript"):
                    # Try to get words with speaker info
                    words = alt.get("words", [])
                    if words:
                        # Group by speaker
                        current_speaker = words[0].get("speaker", 0)
                        current_text = []
                        current_start = words[0].get("start", 0)

                        for word in words:
                            speaker = word.get("speaker", 0)
                            if speaker != current_speaker:
                                # Save current utterance
                                if current_text:
                                    utterances.append({
                                        "speaker": current_speaker,
                                        "text": " ".join(current_text),
                                        "start": current_start,
                                        "end": word.get("start", 0),
                                        "confidence": 0.9,
                                    })
                                current_speaker = speaker
                                current_text = [word.get("punctuated_word", word.get("word", ""))]
                                current_start = word.get("start", 0)
                            else:
                                current_text.append(word.get("punctuated_word", word.get("word", "")))

                        # Save last utterance
                        if current_text:
                            utterances.append({
                                "speaker": current_speaker,
                                "text": " ".join(current_text),
                                "start": current_start,
                                "end": words[-1].get("end", 0),
                                "confidence": 0.9,
                            })
                    else:
                        # No word-level info, use whole transcript
                        utterances.append({
                            "speaker": 0,
                            "text": alt.get("transcript", ""),
                            "start": 0,
                            "end": 0,
                            "confidence": alt.get("confidence", 0),
                        })

    return utterances


def get_tone_class(tone: str) -> str:
    """Get CSS class based on tone."""
    positive_tones = ["calm", "warm", "enthusiastic", "supportive", "empathetic", "curious", "excited"]
    negative_tones = ["frustrated", "anxious", "defensive", "dismissive", "aggressive", "critical", "sarcastic"]

    if tone.lower() in positive_tones:
        return "tone-positive"
    elif tone.lower() in negative_tones:
        return "tone-negative"
    return "tone-neutral"


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "google_api_key" not in st.session_state:
        st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY", "")

    if "deepgram_key" not in st.session_state:
        st.session_state.deepgram_key = os.getenv("DEEPGRAM_API_KEY", "")

    if "analyzer" not in st.session_state:
        if st.session_state.google_api_key:
            st.session_state.analyzer = ConversationAnalyzer(st.session_state.google_api_key)
        else:
            st.session_state.analyzer = None

    if "transcripts" not in st.session_state:
        st.session_state.transcripts = []

    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False


def render_speaker_card(speaker_id: int, analysis):
    """Render a speaker analysis card."""
    speaker_label = f"Speaker {speaker_id + 1}"
    card_class = f"speaker-{speaker_id % 4}"

    tone = analysis.latest_tone
    personality = analysis.personality

    html = f'<div class="speaker-card {card_class}">'
    html += f'<h3>{speaker_label}</h3>'

    if tone:
        tone_class = get_tone_class(tone.primary_tone)
        html += f'<p><strong>Current Tone:</strong> <span class="tone-badge {tone_class}">{tone.primary_tone}</span>'
        if tone.secondary_tone:
            html += f' <span class="tone-badge tone-neutral">{tone.secondary_tone}</span>'
        html += '</p>'
        html += f'<p><strong>Emotional State:</strong> {tone.emotional_state}</p>'
        html += f'<p><strong>Style:</strong> {tone.communication_style}</p>'

    html += f'<p><em>Utterances: {analysis.utterance_count}</em></p>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)

    if personality:
        with st.expander("Personality Profile", expanded=False):
            st.write(f"**Communication:** {personality.communication_style}")
            st.write(f"**Emotional Expression:** {personality.emotional_expression}")
            st.write(f"**Conflict Approach:** {personality.conflict_approach}")
            st.write(f"**Listening Style:** {personality.listening_style}")
            if personality.key_traits:
                st.write(f"**Key Traits:** {', '.join(personality.key_traits)}")
            if personality.summary:
                st.info(personality.summary)


def render_transcript(transcripts: list):
    """Render the conversation transcript."""
    for entry in transcripts:
        speaker_class = f"speaker-{entry['speaker'] % 4}"
        tone = entry.get('tone', 'analyzing...')
        tone_class = get_tone_class(tone) if tone != 'analyzing...' else 'tone-neutral'

        html = f'''
        <div class="transcript-entry {speaker_class}">
            <strong>Speaker {entry['speaker'] + 1}:</strong> {entry['text']}
            <span class="tone-badge {tone_class}" style="font-size: 0.8em;">{tone}</span>
        </div>
        '''
        st.markdown(html, unsafe_allow_html=True)


def main():
    """Main application."""
    initialize_session_state()

    st.title("🎙️ Conversation Tone & Personality Analyzer")
    st.markdown("Upload audio or video files to analyze conversation dynamics, tone, and personality traits.")

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")

        # API Key inputs
        st.subheader("API Keys")

        google_key = st.text_input(
            "Google API Key (Gemini)",
            value=st.session_state.google_api_key,
            type="password",
            help="Required for tone/personality analysis"
        )
        if google_key and google_key != st.session_state.google_api_key:
            st.session_state.google_api_key = google_key
            st.session_state.analyzer = ConversationAnalyzer(google_key)
            st.rerun()

        deepgram_key = st.text_input(
            "Deepgram API Key",
            value=st.session_state.deepgram_key,
            type="password",
            help="Required for transcription"
        )
        if deepgram_key != st.session_state.deepgram_key:
            st.session_state.deepgram_key = deepgram_key
            st.rerun()

        st.divider()

        # Status
        st.subheader("Status")

        if st.session_state.google_api_key and st.session_state.analyzer:
            st.success("✓ Gemini: Ready")
        else:
            st.error("✗ Gemini: Key required")

        if st.session_state.deepgram_key:
            st.success("✓ Deepgram: Ready")
        else:
            st.warning("✗ Deepgram: Key required")

        st.divider()

        if st.button("🔄 Reset Analysis", use_container_width=True):
            if st.session_state.analyzer:
                st.session_state.analyzer.reset()
            st.session_state.transcripts = []
            st.session_state.analyzed = False
            st.rerun()

    # Check for required API keys
    if not st.session_state.analyzer:
        st.warning("⚠️ Please enter your Google API key in the sidebar to enable analysis.")
        return

    if not st.session_state.deepgram_key:
        st.warning("⚠️ Please enter your Deepgram API key in the sidebar to enable transcription.")
        return

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📁 Upload File")

        uploaded_file = st.file_uploader(
            "Upload audio or video file",
            type=["mp3", "wav", "m4a", "ogg", "flac", "mp4", "mov", "avi", "mkv", "webm"],
            help="Supported: MP3, WAV, M4A, OGG, FLAC, MP4, MOV, AVI, MKV, WEBM"
        )

        if uploaded_file:
            if uploaded_file.type.startswith("audio"):
                st.audio(uploaded_file)
            elif uploaded_file.type.startswith("video"):
                st.video(uploaded_file)

            if st.button("🎯 Analyze Conversation", use_container_width=True, type="primary"):
                with st.spinner("Processing..."):
                    # Save uploaded file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    # Extract audio if video
                    is_video = uploaded_file.type.startswith("video")
                    if is_video:
                        st.info("Extracting audio from video...")
                        audio_path = tmp_path.rsplit(".", 1)[0] + ".wav"
                        if not extract_audio_from_video(tmp_path, audio_path):
                            st.error("Failed to extract audio. Make sure ffmpeg is installed.")
                            os.unlink(tmp_path)
                            return
                    else:
                        # Convert to WAV if needed
                        if not uploaded_file.name.lower().endswith(".wav"):
                            st.info("Converting audio format...")
                            audio_path = tmp_path.rsplit(".", 1)[0] + ".wav"
                            cmd = ["ffmpeg", "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", audio_path]
                            subprocess.run(cmd, capture_output=True)
                        else:
                            audio_path = tmp_path

                    # Transcribe
                    st.info("Transcribing with Deepgram...")
                    result = transcribe_audio(audio_path, st.session_state.deepgram_key)

                    if result:
                        utterances = parse_transcription(result)

                        if utterances:
                            st.success(f"Found {len(utterances)} utterances from {len(set(u['speaker'] for u in utterances))} speaker(s)")

                            # Reset analyzer
                            st.session_state.analyzer.reset()
                            st.session_state.transcripts = []

                            # Analyze each utterance
                            st.info("Analyzing tone and personality...")
                            progress = st.progress(0)

                            for i, utt in enumerate(utterances):
                                if utt["text"].strip():
                                    tone = st.session_state.analyzer.analyze_tone(
                                        utt["text"].strip(),
                                        utt["speaker"]
                                    )

                                    st.session_state.transcripts.append({
                                        "speaker": utt["speaker"],
                                        "text": utt["text"].strip(),
                                        "tone": tone.primary_tone,
                                        "start": utt.get("start", 0),
                                    })

                                progress.progress((i + 1) / len(utterances))

                            # Analyze personalities
                            for speaker_id in st.session_state.analyzer.get_all_speakers():
                                st.session_state.analyzer.analyze_personality(speaker_id)

                            st.session_state.analyzed = True
                            progress.empty()
                            st.success("Analysis complete!")
                        else:
                            st.warning("No speech detected in the file.")

                    # Cleanup
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    if is_video and os.path.exists(audio_path):
                        os.unlink(audio_path)
                    elif audio_path != tmp_path and os.path.exists(audio_path):
                        os.unlink(audio_path)

                    st.rerun()

    with col2:
        st.subheader("📊 Analysis")

        speakers = st.session_state.analyzer.get_all_speakers()

        if speakers:
            for sid, analysis in speakers.items():
                render_speaker_card(sid, analysis)

            # Conversation dynamics
            if len(speakers) >= 2:
                st.divider()
                st.subheader("🔄 Conversation Dynamics")

                dynamics = st.session_state.analyzer.get_conversation_dynamics()
                if dynamics:
                    dcol1, dcol2 = st.columns(2)
                    with dcol1:
                        mood = dynamics.get("overall_mood", "N/A")
                        st.metric("Overall Mood", mood.capitalize() if isinstance(mood, str) else "N/A")
                        tension = dynamics.get("tension_level", "N/A")
                        st.metric("Tension Level", tension.capitalize() if isinstance(tension, str) else "N/A")
                    with dcol2:
                        connection = dynamics.get("connection_quality", "N/A")
                        st.metric("Connection", connection.capitalize() if isinstance(connection, str) else "N/A")
                        pattern = dynamics.get("interaction_pattern", "N/A")
                        st.metric("Pattern", pattern.capitalize() if isinstance(pattern, str) else "N/A")

                    if dynamics.get("advice"):
                        st.info(f"💡 **Tip:** {dynamics['advice']}")
        else:
            st.info("Upload a file and click 'Analyze' to see results.")

    # Transcript section
    if st.session_state.transcripts:
        st.divider()
        st.subheader("💬 Conversation Transcript")
        render_transcript(st.session_state.transcripts)


if __name__ == "__main__":
    main()
