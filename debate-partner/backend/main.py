"""
Debate Partner API - FastAPI Backend
"""
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List

from services.stt import transcribe_audio
from services.debate import generate_counter_argument
from services.tts import text_to_speech

# Initialize FastAPI app
app = FastAPI(title="Debate Partner API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for audio files
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files for audio playback
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


class TextDebateRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = None


class DebateResponse(BaseModel):
    text: str
    audio_url: Optional[str] = None
    transcribed_input: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Debate Partner API", "status": "running"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/debate/text", response_model=DebateResponse)
async def debate_text(request: TextDebateRequest):
    """
    Process text-based debate input
    """
    try:
        # Generate counter-argument
        counter_arg = await generate_counter_argument(
            request.message,
            request.conversation_history
        )

        # Generate audio response
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        await text_to_speech(counter_arg, str(audio_path))

        return DebateResponse(
            text=counter_arg,
            audio_url=f"/outputs/{audio_filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/debate/audio", response_model=DebateResponse)
async def debate_audio(
    audio: UploadFile = File(...),
    conversation_history: Optional[str] = Form(None)
):
    """
    Process audio-based debate input
    """
    try:
        # Save uploaded audio
        audio_filename = f"{uuid.uuid4()}.{audio.filename.split('.')[-1]}"
        audio_path = UPLOAD_DIR / audio_filename

        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        # Transcribe audio to text
        transcribed_text = await transcribe_audio(str(audio_path))

        # Parse conversation history if provided
        history = []
        if conversation_history:
            import json
            history = json.loads(conversation_history)

        # Generate counter-argument
        counter_arg = await generate_counter_argument(transcribed_text, history)

        # Generate audio response
        output_filename = f"{uuid.uuid4()}.mp3"
        output_path = OUTPUT_DIR / output_filename
        await text_to_speech(counter_arg, str(output_path))

        # Clean up uploaded file
        os.remove(audio_path)

        return DebateResponse(
            text=counter_arg,
            audio_url=f"/outputs/{output_filename}",
            transcribed_input=transcribed_text
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
