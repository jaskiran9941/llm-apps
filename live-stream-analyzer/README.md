# 📹 Live Stream Analyzer

A **multimodal AI application** that analyzes live streams using Google Gemini 2.0 Vision. Captures stream frames, analyzes each with AI, and generates comprehensive summaries of the content.

## Features

- 👁️ **Multimodal Analysis** - Uses Gemini Vision to analyze each frame
- 🎥 **Multi-Platform** - Works with YouTube, Twitch, eBay Live, and other platforms
- 🧠 **AI Summarization** - Gemini aggregates all frame observations into comprehensive summaries
- 🔍 **Priority Scoring** - Each frame gets a priority score (1-5) based on content importance
- 🖥️ **Simple UI** - Easy-to-use Streamlit web interface
- 💾 **Detailed Reports** - Exports frame-by-frame analysis and summaries

## Quick Start

### Prerequisites

1. **Install FFmpeg:**
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

2. **Get Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a free API key

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add: GEMINI_API_KEY=your_key_here
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## How It Works

### 1. Stream Capture
- Captures live stream video using yt-dlp and FFmpeg
- Extracts frames at configurable intervals (default: every 10 seconds)

### 2. Frame-by-Frame Analysis
- Each frame is analyzed independently by Gemini Vision
- Extracts: content visible, status indicators, activity level, notable moments
- Assigns priority score (1-5) based on content importance

### 3. Summary Generation
- All frame observations are sent to Gemini
- AI synthesizes observations into a comprehensive summary:
  - Executive summary of main highlights
  - Key events detected (with timestamps)
  - Content presented throughout stream
  - Notable moments and insights
  - Stream activity assessment

**Usage:**
```bash
streamlit run app.py
# Enter stream URL → Set duration → Click "Start Analysis"
```

## Project Structure

```
├── app.py                 # Streamlit web interface
├── agent.py              # Gemini AI agent for frame analysis
├── analyzer.py           # Summary generation
├── stream_capture.py     # Stream capture & frame extraction
├── requirements.txt      # Python dependencies
└── outputs/             # Generated videos, frames, and reports
```

## Example Output

The analyzer generates:

**Summary (TXT)** - Human-readable summary including:
- Executive summary
- Key events detected
- Content presented
- Notable moments
- Stream activity insights

**Full Report (JSON)** - Detailed data with:
- Frame-by-frame analysis
- Timestamps
- Complete metadata

## Architecture

```
Stream URL → Capture → Frame Extraction → Frame Analysis → Summary Generation
                                              ↓
                                    Gemini Vision analyzes each frame
                                    Observations stored in memory
                                    Priority scores assigned
```

**Key Components:**
- **LiveStreamAgent** (`agent.py`) - Analyzes individual frames with Gemini Vision
- **StreamAnalyzer** (`analyzer.py`) - Sends all observations to Gemini for summary
- **StreamCapture** (`stream_capture.py`) - Handles video capture and frame extraction

**Technologies:**
- **Google Gemini 2.0 Flash** - Multimodal vision AI
- **Streamlit** - Web interface
- **yt-dlp** - Stream URL extraction
- **FFmpeg** - Video capture
- **OpenCV** - Frame extraction

## Cost

- Uses Gemini 2.0 Flash free tier (generous limits)
- Typical 2-minute stream ≈ 13 API calls (essentially free)

## License

MIT License
