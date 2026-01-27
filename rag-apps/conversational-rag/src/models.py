"""
Data models for Conversational RAG
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Chunk(BaseModel):
    """Represents a text chunk"""
    content: str
    page: int
    chunk_id: str
    metadata: dict = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """Represents a retrieval result"""
    content: str
    score: float
    chunk_id: str
    page: int
    result_type: Literal["text", "image"] = "text"
    image_path: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class RAGResponse(BaseModel):
    """Complete RAG response"""
    query: str
    answer: str
    retrieved_chunks: List[RetrievalResult]
    images: List[str] = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationMessage(BaseModel):
    """Single message in conversation"""
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    retrieved_chunks: List[RetrievalResult] = []
    metadata: dict = {}


class ConversationHistory(BaseModel):
    """Complete conversation history"""
    conversation_id: str
    messages: List[ConversationMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)

    def get_last_n_messages(self, n: int) -> List[ConversationMessage]:
        """Get last N messages"""
        return self.messages[-n:] if n > 0 else self.messages

    def format_for_llm(self, include_sources: bool = False) -> List[dict]:
        """Format history for OpenAI API"""
        messages = []
        for msg in self.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        return messages

    def get_last_user_query(self) -> Optional[str]:
        """Get the most recent user query"""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def get_last_assistant_response(self) -> Optional[str]:
        """Get the most recent assistant response"""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return None
