# 🚀 Quick Setup Instructions

## 1. Add API Keys

Edit the `.env` file in this directory and add your API keys:

```bash
# Open .env file
open .env
# Or use: nano .env
```

Replace these values:
```env
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY
ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY
ELEVENLABS_API_KEY=YOUR_ACTUAL_KEY
```

### Where to Get API Keys:
- **OpenAI**: https://platform.openai.com/api-keys (for Whisper STT)
- **Anthropic**: https://console.anthropic.com/ (for Claude debate)
- **ElevenLabs**: https://elevenlabs.io/ → Profile → API Key (for TTS voice)

## 2. Start Backend Server

```bash
cd backend
source venv/bin/activate
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

## 3. Start Frontend (New Terminal)

Open a NEW terminal window:

```bash
cd debate-partner/frontend
npm run dev
```

You should see:
```
VITE ready in XXX ms
➜  Local:   http://localhost:5173/
```

## 4. Test the App

1. Open browser to: **http://localhost:5173**
2. Try text input first: "I think cats are better than dogs"
3. Click Send
4. Wait for response (should take 5-10 seconds)
5. Click "Play Response" to hear the audio

## 5. Test Voice Input

1. Click "🎤 Record Voice"
2. Allow microphone permission
3. Say something like: "Social media is harmful"
4. Click "Stop Recording"
5. Wait for transcription + debate response
6. Play the audio response

## Troubleshooting

### Backend won't start
- Check that `.env` file exists and has all 3 API keys
- Make sure virtual environment is activated: `source venv/bin/activate`

### Frontend won't start
- Make sure you're in the `frontend` directory
- Check that `npm install` completed successfully in frontend folder

### API errors
- **401 Unauthorized**: API key is invalid or missing
- **429 Rate Limit**: You've hit API rate limits
- **Insufficient credits**: Check your API account has credits

### Microphone not working
- Grant browser permission when prompted
- Chrome/Firefox work best
- Safari may have issues with MediaRecorder API

### No audio playback
- Check backend terminal - should show file being created
- Look for files in `backend/outputs/` directory
- Check browser console for CORS errors

## Cost Per Test

Each debate costs approximately:
- Whisper (voice input): ~$0.006
- Claude (debate): ~$0.01-0.03
- ElevenLabs (voice output): ~$0.02-0.04

**Total: ~$0.04-0.08 per debate**

So you can do ~12-25 test debates for $1.

## Next Steps

Once it works:
1. Try different debate topics
2. Experiment with the prompts in `backend/services/debate.py`
3. Try different TTS voices in `backend/services/tts.py`
4. Ready to push to GitHub when you're happy!
