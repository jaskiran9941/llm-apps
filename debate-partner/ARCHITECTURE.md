# Architecture Deep Dive

## System Design

### High-Level Overview

The Debate Partner is built as a three-tier application with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │   UI     │  │  State   │  │  Audio Handling      │  │
│  │Components│  │Management│  │  (Record/Playback)   │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON + FormData
┌────────────────────▼────────────────────────────────────┐
│                    API Gateway Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │ FastAPI  │  │  CORS    │  │  File Upload         │  │
│  │ Routes   │  │Middleware│  │  Handler             │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Service Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │   STT    │  │  Debate  │  │       TTS            │  │
│  │ Service  │  │  Engine  │  │     Service          │  │
│  └────┬─────┘  └────┬─────┘  └──────┬───────────────┘  │
└───────┼─────────────┼────────────────┼──────────────────┘
        │             │                │
┌───────▼─────┐ ┌────▼─────┐  ┌───────▼────────┐
│   Whisper   │ │  Claude  │  │   ElevenLabs   │
│     API     │ │   API    │  │      API       │
└─────────────┘ └──────────┘  └────────────────┘
```

## Data Flow

### Text Input Flow
```
User types position
    ↓
Frontend validates input
    ↓
POST /api/debate/text
    {
      message: "string",
      conversation_history: [{role, content}]
    }
    ↓
debate.py: generate_counter_argument()
    ↓
Claude API call (~3-5s)
    ↓
tts.py: text_to_speech()
    ↓
ElevenLabs API call (~5-10s)
    ↓
Save audio to /outputs/*.mp3
    ↓
Return JSON response
    {
      text: "counter-argument",
      audio_url: "/outputs/uuid.mp3"
    }
    ↓
Frontend displays + plays audio
```

### Audio Input Flow
```
User clicks record
    ↓
MediaRecorder captures audio
    ↓
Blob created on stop
    ↓
POST /api/debate/audio (FormData)
    {
      audio: File,
      conversation_history: JSON string
    }
    ↓
Save to /uploads/*.webm (~50-500KB)
    ↓
stt.py: transcribe_audio()
    ↓
Whisper API call (~2-3s)
    ↓
Delete uploaded file
    ↓
debate.py: generate_counter_argument()
    ↓
Claude API call (~3-5s)
    ↓
tts.py: text_to_speech()
    ↓
ElevenLabs API call (~5-10s)
    ↓
Return JSON response
    {
      text: "counter-argument",
      audio_url: "/outputs/uuid.mp3",
      transcribed_input: "user's spoken text"
    }
    ↓
Frontend shows transcription + response + audio
```

## Component Details

### Backend Services

#### 1. STT Service (`services/stt.py`)

**Purpose**: Convert audio to text using OpenAI Whisper

**Key Functions**:
- `transcribe_audio(audio_file_path)` - Async transcription

**Design Decisions**:
- Uses Whisper-1 model (multilingual, robust)
- Returns raw text (no timestamps needed)
- Client initialized per-request to avoid stale connections
- Errors wrapped with context for debugging

**Performance**:
- Latency: ~2-3 seconds for 1 minute audio
- Accuracy: 95%+ for clear speech
- Cost: $0.006 per minute

#### 2. Debate Service (`services/debate.py`)

**Purpose**: Generate adversarial counter-arguments using Claude

**Key Functions**:
- `generate_counter_argument(user_message, conversation_history)`

**Design Decisions**:
- System prompt emphasizes **opposite stance**
- Max tokens: 1024 (optimal for TTS, ~2-3 paragraphs)
- Uses Claude Sonnet 4 (best balance of quality/speed/cost)
- Conversation history maintained client-side, passed on each request
- API key validation before client creation

**Prompt Engineering**:
```python
SYSTEM_PROMPT = """
1. Always take OPPOSITE stance
2. Identify position first, then argue against it
3. Use logical reasoning + examples
4. Be respectful but firm
5. Keep concise (2-3 paragraphs for audio)
"""
```

**Performance**:
- Latency: ~3-5 seconds
- Quality: High coherence, stays on-topic
- Cost: $0.01-0.03 per response

#### 3. TTS Service (`services/tts.py`)

**Purpose**: Convert text responses to natural speech

**Key Functions**:
- `text_to_speech(text, output_path)`

**Design Decisions**:
- Uses ElevenLabs v2 multilingual model
- Voice ID: Adam (authoritative, firm - good for debates)
- Output format: MP3 (browser-compatible)
- Files saved with UUID names to avoid collisions

**Voice Selection Rationale**:
- Adam: Dominant, firm tone suits adversarial debates
- Alternative voices available: Sarah (reassuring), Charlie (energetic)

**Performance**:
- Latency: ~5-10 seconds for 200 words
- Quality: Near-human naturalness
- Cost: ~$0.02-0.04 per minute

### Frontend Components

#### 1. App.jsx (Main Orchestrator)

**Responsibilities**:
- Manage conversation state
- Handle both text and audio submissions
- Build conversation history for API
- Error handling and loading states

**State Management**:
```javascript
messages: [
  {
    role: 'user' | 'assistant',
    content: string,
    audioUrl?: string,
    isAudio?: boolean,
    timestamp: ISO string
  }
]
```

#### 2. AudioRecorder.jsx

**Responsibilities**:
- Request microphone permission
- Record audio using MediaRecorder API
- Display recording timer
- Convert to Blob on stop

**Technical Details**:
- Format: WebM (browser standard)
- Encoding: Opus codec (efficient)
- Chunk size: Default (auto-determined)
- Stop mechanism: Manual user click

**Error Handling**:
- Permission denied → Alert user
- No microphone → Alert user
- Recording failure → Graceful fallback

#### 3. AudioPlayer.jsx

**Responsibilities**:
- Play generated audio responses
- Show play/pause state
- Handle playback completion

**Technical Details**:
- Uses HTML5 `<audio>` element
- Preload: none (lazy loading)
- Format: MP3 (universally supported)

#### 4. DebateChat.jsx

**Responsibilities**:
- Display conversation history
- Auto-scroll to latest message
- Show loading states
- Clear chat functionality

**UI Features**:
- User messages: Purple gradient
- Assistant messages: Gray background
- Audio badge: Indicates voice input
- Typing indicator: Three animated dots

## API Endpoints

### POST /api/debate/text

**Purpose**: Process text-based debate input

**Request**:
```json
{
  "message": "string",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Response**:
```json
{
  "text": "counter-argument string",
  "audio_url": "/outputs/uuid.mp3",
  "transcribed_input": null
}
```

**Error Responses**:
- 500: "Debate generation error: ..." (Claude API failure)
- 500: "TTS Error: ..." (ElevenLabs failure)

### POST /api/debate/audio

**Purpose**: Process audio-based debate input

**Request**: FormData
- `audio`: File (WebM blob)
- `conversation_history`: JSON string (optional)

**Response**:
```json
{
  "text": "counter-argument string",
  "audio_url": "/outputs/uuid.mp3",
  "transcribed_input": "user's spoken text"
}
```

**Error Responses**:
- 500: "STT Error: ..." (Whisper API failure)
- 500: "Debate generation error: ..." (Claude failure)
- 500: "TTS Error: ..." (ElevenLabs failure)

## Environment Configuration

### Required Variables

```bash
# OpenAI API Key (for Whisper STT)
OPENAI_API_KEY=sk-proj-...

# Anthropic API Key (for Claude debate)
ANTHROPIC_API_KEY=sk-ant-...

# ElevenLabs API Key (for TTS)
ELEVENLABS_API_KEY=sk_...
```

### Loading Strategy

**Problem**: Python `load_dotenv()` doesn't override existing env vars by default

**Solution**: Use `override=True` flag
```python
load_dotenv(dotenv_path=env_path, override=True)
```

**Why**: Prevents conflicts with shell environment variables

### Security Considerations

1. **.env in .gitignore**: Never commit API keys
2. **Server-side validation**: All keys validated before use
3. **CORS**: Restricted to localhost in development
4. **File cleanup**: Uploaded audio deleted after transcription
5. **UUID filenames**: Prevents path traversal attacks

## Performance Optimization

### Latency Breakdown

**Text input total**: ~8-15 seconds
- Claude: 3-5s
- ElevenLabs: 5-10s

**Audio input total**: ~10-18 seconds
- Whisper: 2-3s
- Claude: 3-5s
- ElevenLabs: 5-10s

### Optimization Strategies

1. **Async/Await**: All API calls are async
2. **Connection pooling**: HTTP clients reused
3. **Minimal token usage**: 1024 max tokens for responses
4. **File cleanup**: Uploads deleted immediately after use
5. **No unnecessary processing**: Direct passthrough where possible

### Future Optimizations

- [ ] Response streaming (Claude + ElevenLabs both support)
- [ ] Audio caching (dedupe similar responses)
- [ ] Parallel processing (transcribe while generating response)
- [ ] WebSocket connection (reduce HTTP overhead)
- [ ] CDN for static audio files

## Error Handling Strategy

### Three-Layer Defense

1. **Service Layer**: Catch API errors, wrap with context
2. **API Gateway**: HTTP exception handling
3. **Frontend**: User-friendly error messages

### Error Flow Example

```python
# Service layer
try:
    client = Anthropic(...)
    response = client.messages.create(...)
except Exception as e:
    raise Exception(f"Debate generation error: {str(e)}")
    # ↓
# API gateway
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
    # ↓
# Frontend
.catch(error => {
    alert('Failed to get response. Check console.')
})
```

## Scalability Considerations

### Current Limitations

- **Stateless**: No session persistence
- **Single server**: No load balancing
- **File system storage**: Outputs saved to disk
- **Synchronous processing**: One request at a time per endpoint

### Scaling Path

#### Phase 1: Basic Production (1-100 users)
- Add Redis for session storage
- Database for conversation history
- S3/Cloud Storage for audio files
- Docker containerization

#### Phase 2: Medium Scale (100-1000 users)
- Kubernetes for auto-scaling
- CDN for audio delivery
- Queue system (Celery/Redis) for async processing
- Rate limiting per user

#### Phase 3: Large Scale (1000+ users)
- Multi-region deployment
- Caching layer for common debates
- WebSocket for real-time streaming
- Analytics and monitoring

## Testing Strategy

### Unit Tests (To Be Implemented)

```python
# Test STT service
def test_transcribe_audio():
    # Mock Whisper API response
    # Verify transcription accuracy

# Test debate service
def test_generate_counter_argument():
    # Mock Claude API response
    # Verify prompt structure
    # Test conversation history

# Test TTS service
def test_text_to_speech():
    # Mock ElevenLabs API
    # Verify audio file creation
```

### Integration Tests

```python
# Test full flow
async def test_text_debate_flow():
    # Submit text → verify all steps → check output

async def test_audio_debate_flow():
    # Upload audio → verify transcription → check debate → verify TTS
```

### E2E Tests

```javascript
// Playwright/Cypress
describe('Debate Partner', () => {
  it('should complete text debate', () => {
    // Type message → submit → verify response
  })

  it('should record and process audio', () => {
    // Record → stop → verify transcription + response
  })
})
```

## Deployment

### Development
```bash
# Backend
python main.py  # Port 8000

# Frontend
npm run dev     # Port 5173
```

### Production

#### Option 1: Traditional Server
```bash
# Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend (build + serve)
npm run build
serve -s dist -p 5173
```

#### Option 2: Docker
```dockerfile
# Backend Dockerfile
FROM python:3.9
COPY backend/ /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# Frontend Dockerfile
FROM node:18
COPY frontend/ /app
RUN npm install && npm run build
CMD ["npx", "serve", "-s", "dist"]
```

#### Option 3: Cloud Platform
- **Backend**: Railway, Render, Fly.io
- **Frontend**: Vercel, Netlify
- **Storage**: AWS S3, Cloudflare R2

## Monitoring & Observability

### Key Metrics to Track

1. **Performance**
   - API latency (p50, p95, p99)
   - Error rates per service
   - Audio file sizes

2. **Usage**
   - Debates per day
   - Text vs audio ratio
   - Avg conversation length

3. **Costs**
   - API spend per service
   - Cost per debate
   - Monthly burn rate

### Logging Strategy

```python
import logging

logger = logging.getLogger(__name__)

# Log all API calls
logger.info(f"Claude API call: {len(messages)} messages")
logger.info(f"Audio generated: {len(audio)} bytes")

# Log errors with context
logger.error(f"TTS failed: {error}", extra={"text_length": len(text)})
```

## Security Checklist

- [x] API keys in environment variables
- [x] `.env` in `.gitignore`
- [x] CORS configured for specific origins
- [x] File upload size limits (implicit in FastAPI)
- [ ] Rate limiting (to be added)
- [ ] Input sanitization (to be added)
- [ ] HTTPS in production (deployment concern)
- [ ] API key rotation strategy (operational)

## Contributing Guidelines

1. **Code Style**: Follow existing patterns
2. **Type Hints**: Use Python type hints for functions
3. **Error Messages**: Be descriptive and actionable
4. **Comments**: Explain *why*, not *what*
5. **Testing**: Add tests for new features
6. **Documentation**: Update this file for architectural changes

---

**Last Updated**: January 2026
**Maintainer**: Your Name
**Version**: 1.0.0
