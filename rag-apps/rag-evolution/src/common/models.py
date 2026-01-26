"""
Pydantic models for the RAG Evolution Showcase
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


class ImageInfo(BaseModel):
    """Represents an extracted image"""
    image_path: str
    page: int
    description: Optional[str] = None
    image_id: str
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


class ChunkingStrategy(BaseModel):
    """Configuration for chunking strategy"""
    strategy_type: Literal["fixed", "sentence", "semantic"]
    chunk_size: int = 500
    chunk_overlap: int = 50
    semantic_threshold: float = 0.7


class RetrievalStrategy(BaseModel):
    """Configuration for retrieval strategy"""
    strategy_type: Literal["semantic", "keyword", "hybrid", "hybrid_rerank"]
    k: int = 5
    rerank: bool = False


class DocumentStats(BaseModel):
    """Statistics about a processed document"""
    total_pages: int
    total_chunks: int
    total_images: int
    avg_chunk_size: float
    processing_time: float
