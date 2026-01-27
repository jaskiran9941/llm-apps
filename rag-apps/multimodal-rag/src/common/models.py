"""
Pydantic models for multimodal RAG system.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TextChunk(BaseModel):
    """Model for text chunks."""
    chunk_id: str
    text: str
    page: int
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ImageInfo(BaseModel):
    """Model for extracted images."""
    image_id: str
    page: int
    image_path: str
    description: Optional[str] = None
    width: int
    height: int
    format: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TableInfo(BaseModel):
    """Model for extracted tables."""
    table_id: str
    page: int  # For PDFs, sheet index for Excel
    table_data: Dict[str, Any]  # Serialized DataFrame
    headers: List[str]
    num_rows: int
    num_cols: int
    description: Optional[str] = None  # GPT-4 generated
    serialized_text: Optional[str] = None  # Markdown format
    source_type: Literal["pdf", "excel", "csv"] = "pdf"
    is_chunk: bool = False
    chunk_index: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AudioSegment(BaseModel):
    """Model for audio transcript segments."""
    segment_id: str
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    speaker: Optional[str] = None


class AudioInfo(BaseModel):
    """Model for audio files."""
    audio_id: str
    audio_path: str
    duration: float  # Seconds
    transcript: str  # Full transcript
    segments: List[AudioSegment]
    language: str
    topics: Optional[List[str]] = None
    summary: Optional[str] = None
    entities: Optional[Dict[str, List[str]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """Model for retrieval results."""
    content: str
    type: Literal["text", "image", "table", "audio"]
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_info: Optional[str] = None


class QueryResult(BaseModel):
    """Model for query results."""
    query: str
    answer: str
    sources: List[RetrievalResult]
    processing_time: float
    cost_estimate: float
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentStats(BaseModel):
    """Statistics for processed documents."""
    num_text_chunks: int = 0
    num_images: int = 0
    num_tables: int = 0
    num_audio_segments: int = 0
    total_tokens: int = 0
    processing_cost: float = 0.0
    processing_time: float = 0.0
