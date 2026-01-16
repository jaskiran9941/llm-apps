# Conversation Tone & Personality Analyzer

Analyze conversations from audio or video files to understand tone, personality traits, and conversation dynamics using AI.

## Features

- **Upload audio files**: MP3, WAV, M4A, OGG, FLAC
- **Upload video files**: MP4, MOV, AVI, MKV, WEBM (audio extracted automatically)
- **Speaker diarization**: Automatically detects and separates multiple speakers
- **Tone analysis**: Identifies emotional tone for each utterance (calm, frustrated, defensive, etc.)
- **Personality profiling**: Builds personality profiles based on communication patterns
- **Conversation dynamics**: Analyzes overall mood, tension levels, and interaction patterns

## Tech Stack

- **Streamlit** - Web UI
- **Deepgram** - Speech-to-text transcription with speaker diarization
- **Google Gemini** - Tone and personality analysis
- **FFmpeg** - Audio extraction from video files

## Setup

### Prerequisites

- Python 3.9+
- FFmpeg installed (`brew install ffmpeg` on macOS)
- Deepgram API key ([console.deepgram.com](https://console.deepgram.com))
- Google API key ([aistudio.google.com](https://aistudio.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/jaskiran9941/llm-apps.git
cd llm-apps/conversation-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add your DEEPGRAM_API_KEY and GOOGLE_API_KEY
```

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Sample Audio/Video Files

Download sample audio and video files for testing from Kaggle:

**[Video and Audio Samples Dataset](https://www.kaggle.com/datasets/csanskriti/video-and-audio-samples)**

## Usage

1. Enter your API keys in the sidebar (or set them in `.env`)
2. Upload an audio or video file containing a conversation
3. Click "Analyze Conversation"
4. View:
   - **Transcript** with speaker labels and tone tags
   - **Speaker cards** showing tone and personality analysis
   - **Conversation dynamics** (for multi-speaker conversations)

## How It Works

1. **Upload**: Audio/video file is uploaded to the app
2. **Extract**: If video, audio is extracted using FFmpeg
3. **Transcribe**: Deepgram transcribes audio with speaker diarization
4. **Analyze**: Gemini analyzes each utterance for tone
5. **Profile**: Personality profiles are built from conversation patterns
6. **Display**: Results shown in an interactive UI

## License

MIT
