# Chat Personality Analyzer

## Overview
Streamlit app that analyzes conversation screenshots using Gemini Vision to identify participant personalities and provide communication advice.

## Quick Start
```bash
cd chat-personality-analyzer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY
streamlit run app.py  # Port 8501
```

## Environment
- `GOOGLE_API_KEY`: Gemini API key (get from https://makersuite.google.com/app/apikey)

## Architecture
```
app.py                              # Streamlit UI
src/
  services/personality_analyzer.py  # Core analysis (Gemini Vision)
  utils/config.py                   # Configuration
```

### Analysis Pipeline
1. **Extract Conversation**: Gemini Vision OCRs screenshots → structured text
2. **Analyze Personalities**: Identifies each speaker's traits, style, values
3. **Generate Advice**: Provides approach tips per person

### Key Patterns
- Single Gemini client configured once in `PersonalityAnalyzer.__init__`
- PIL Image objects passed to `generate_content()` (not file paths)
- JSON output parsing with fallback for malformed responses
- Session state for analyzer instance persistence

## Tech Stack
- **UI**: Streamlit
- **AI**: Gemini 1.5 Pro (vision + text)
- **Image Processing**: Pillow
