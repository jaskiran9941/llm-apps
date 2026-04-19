from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.utils import get_response

app = FastAPI(title="TaskFlow Support Chatbot")

STATIC_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message] = Field(...)


class ChatResponse(BaseModel):
    messages: List[Message]


@app.get("/", response_class=HTMLResponse)
async def root():
    return (STATIC_DIR / "index.html").read_text()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    raw = [m.model_dump() for m in request.messages]
    updated = get_response(raw)
    return ChatResponse(messages=[Message(**m) for m in updated])
