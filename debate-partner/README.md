# 🎙️ AI Debate Partner

An AI-powered debate system that argues the opposite side of any position you take. Features full audio capabilities with speech-to-text input and text-to-speech output, helping you think critically and explore different perspectives.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green) ![React](https://img.shields.io/badge/React-18-61dafb) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 What Makes This Interesting

- **🎤 Full Audio Pipeline**: Speech-to-Text → LLM Processing → Text-to-Speech
- **🔄 Multi-API Orchestration**: Chains OpenAI Whisper, Claude, and ElevenLabs seamlessly
- **💬 Context-Aware Debates**: Maintains conversation history across multiple turns
- **🎭 Adversarial Prompting**: System designed specifically to challenge your viewpoints

## 🚀 Key Learning Outcomes

This project demonstrates:

1. **Audio AI Integration**
   - OpenAI Whisper for speech transcription
   - ElevenLabs for natural voice synthesis
   - Browser MediaRecorder API for audio capture

2. **Multi-API Orchestration**
   - Sequential API chaining with error handling
   - Cost optimization strategies (~$0.04-0.08 per debate)
   - Latency management across 3 external services

3. **Production Patterns**
   - FastAPI async/await patterns
   - File upload and static file serving
   - Environment variable management
   - CORS configuration for development

4. **Prompt Engineering**
   - System prompts for consistent adversarial behavior
   - Context preservation across turns
   - Output optimization for audio playback

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
│  (React UI) │
└──────┬──────┘
       │
       ├─── Text Input ──────────┐
       │                         │
       └─── Audio Input ─────┐   │
                             │   │
                    ┌────────▼───▼────────┐
                    │   FastAPI Backend   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
            ┌───────▼──┐  ┌────▼────┐  ┌─▼─────────┐
            │ Whisper  │  │ Claude  │  │ ElevenLabs│
            │   STT    │  │  Debate │  │    TTS    │
            └──────────┘  └─────────┘  └───────────┘
```

**Flow:**
1. User speaks/types position
2. Whisper API transcribes (if audio)
3. Claude generates counter-argument
4. ElevenLabs converts to speech
5. Frontend displays text + plays audio

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- API Keys:
  - [OpenAI](https://platform.openai.com/api-keys) - for Whisper STT
  - [Anthropic](https://console.anthropic.com/) - for Claude
  - [ElevenLabs](https://elevenlabs.io/) - for TTS

## ⚡ Quick Start

### 1. Clone and Navigate
```bash
git clone <your-repo>
cd debate-partner
```

### 2. Configure API Keys
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
```

### 3. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Setup Frontend
```bash
cd ../frontend
npm install
```

### 5. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### 6. Start Debating!
Open http://localhost:5173 in your browser

## 🎮 Usage

### Text-Based Debate
1. Type your position: *"Remote work is better than office work"*
2. Click **Send**
3. Wait ~15-20 seconds
4. Read the counter-argument
5. Click **▶️ Play Response** to hear it

### Voice-Based Debate
1. Click **🎤 Record Voice**
2. Allow microphone permission
3. Speak your position
4. Click **Stop Recording**
5. Wait ~25-30 seconds (includes transcription time)
6. See transcribed input + counter-argument
7. Listen to audio response

## 📁 Project Structure

```
debate-partner/
├── backend/
│   ├── services/
│   │   ├── stt.py              # OpenAI Whisper integration
│   │   ├── debate.py           # Claude debate logic
│   │   └── tts.py              # ElevenLabs voice synthesis
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── uploads/                # Temporary audio uploads
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.jsx    # Voice input
│   │   │   ├── AudioPlayer.jsx      # Voice playback
│   │   │   └── DebateChat.jsx       # Conversation UI
│   │   ├── App.jsx             # Main application
│   │   └── main.jsx            # Entry point
│   └── package.json            # Node dependencies
│
├── .env.example                # Environment template
├── .gitignore
└── README.md                   # This file
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with async support
- **OpenAI Whisper API** - State-of-the-art speech recognition
- **Anthropic Claude** - Advanced LLM for debate generation
- **ElevenLabs** - High-quality text-to-speech synthesis

### Frontend
- **React 18** - UI framework with hooks
- **Vite** - Fast build tool and dev server
- **MediaRecorder API** - Browser audio capture
- **Fetch API** - HTTP requests to backend

## 💰 Cost Analysis

Per debate session (assuming ~1 minute audio):

| Service | Cost | Usage |
|---------|------|-------|
| Whisper API | ~$0.006 | 1 min transcription |
| Claude API | ~$0.01-0.03 | ~200-400 tokens |
| ElevenLabs | ~$0.02-0.04 | 1 min audio generation |
| **Total** | **~$0.04-0.08** | Per complete debate |

**Budget estimates:**
- 100 debates: ~$4-8
- 1000 debates: ~$40-80

## 🎨 Customization

### Change Debate Style

Edit `backend/services/debate.py`:

```python
SYSTEM_PROMPT = """You are an expert debate partner...
[Modify this to change behavior]
"""
```

### Change Voice

Edit `backend/services/tts.py`:

```python
# Available voices: Sarah, Charlie, George, Liam, etc.
audio = generate(
    text=text,
    voice="VOICE_ID_HERE",
    model="eleven_multilingual_v2"
)
```

Get voice IDs from your ElevenLabs account.

### Adjust Response Length

Edit `backend/services/debate.py`:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,  # Increase for longer responses
    ...
)
```

## 🐛 Troubleshooting

### Backend Issues

**"API key not found"**
- Verify `.env` file exists in project root
- Check all three keys are set correctly
- Restart backend after changing `.env`

**"Port 8000 already in use"**
```bash
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**"Failed to get debate response"**
- Check backend is running on port 8000
- Open browser console for detailed errors
- Verify CORS is configured correctly

**Microphone not working**
- Grant browser microphone permission
- Use Chrome or Firefox (Safari has issues)
- Check browser console for errors

**Audio won't play**
- Verify audio files in `backend/outputs/`
- Check browser console for 404 errors
- Ensure backend static file serving is working

## 🚀 Future Enhancements

### Planned Features
- [ ] Multiple debate modes (Socratic, Devil's Advocate, Steel Man)
- [ ] Voice selection UI (choose from 20+ voices)
- [ ] Export debates as PDF/audio files
- [ ] Debate history and persistence
- [ ] Multi-language support
- [ ] Real-time streaming responses

### Advanced Ideas
- [ ] Research-backed arguments with web search
- [ ] Fact-checking with citations
- [ ] Multi-agent debates (3+ perspectives)
- [ ] Argument strength scoring
- [ ] Visual argument mapping
- [ ] Community debate tournaments

## 📚 Learning Resources

### Understanding the Stack
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [OpenAI Whisper Docs](https://platform.openai.com/docs/guides/speech-to-text)
- [Claude API Guide](https://docs.anthropic.com/claude/docs)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)

### Related Projects
- [Shubham Saboo's AI Projects](https://github.com/shubhamsaboo) - Inspiration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM frameworks
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - Autonomous agents

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Add more debate modes and styles
- Implement streaming for faster UX
- Add comprehensive error handling
- Create unit and integration tests
- Improve audio quality and compression
- Add user authentication and sessions

## 📄 License

MIT License - feel free to use for learning or commercial projects.

## 🙏 Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Inspired by [Shubham Saboo's](https://github.com/shubhamsaboo) practical AI projects
- Uses cutting-edge AI APIs from OpenAI, Anthropic, and ElevenLabs

---

**Made with ❤️ for critical thinking and AI exploration**

*Star ⭐ this repo if you find it useful!*
