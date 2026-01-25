"""
Core data models for the RAG system.

These Pydantic models define the data contracts between all components,
ensuring type safety and validation throughout the pipeline.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Document(BaseModel):
    """
    Represents a source document (e.g., a PDF file).

    This is the raw document before chunking. Each document has a unique ID
    and can contain metadata like filename, upload timestamp, etc.
    """
    doc_id: str = Field(..., description="Unique document identifier")
    text: str = Field(..., description="Full document text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (filename, upload_date, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "doc_123",
                "text": "This is the full document content...",
                "metadata": {"filename": "example.pdf", "pages": 10}
            }
        }


class Chunk(BaseModel):
    """
    Represents a chunk of text from a document.

    Documents are split into chunks for embedding. Each chunk maintains
    a reference to its source document and preserves metadata like page numbers
    for citation purposes.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Parent document ID")
    text: str = Field(..., description="Chunk text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk metadata (page_number, chunk_index, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_123_0",
                "doc_id": "doc_123",
                "text": "This is a chunk of text...",
                "metadata": {"page_number": 1, "chunk_index": 0}
            }
        }


class SearchResult(BaseModel):
    """
    Represents a single search result from the vector store.

    Contains the retrieved chunk and its similarity score. Scores are typically
    in the range [0, 1] for cosine similarity, with higher scores indicating
    better matches.
    """
    chunk: Chunk = Field(..., description="Retrieved chunk")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score (0-1, higher is better)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chunk": {
                    "chunk_id": "chunk_123_0",
                    "doc_id": "doc_123",
                    "text": "Relevant text...",
                    "metadata": {"page_number": 1}
                },
                "score": 0.85
            }
        }


class RetrievedChunk(BaseModel):
    """
    Enriched chunk information for displaying to users.

    Extends SearchResult with human-readable source information for citations.
    Used in the UI to show where information came from.
    """
    text: str = Field(..., description="Chunk text content")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    source_document: str = Field(..., description="Source document name")
    page_number: Optional[int] = Field(None, description="Page number in source")
    chunk_id: str = Field(..., description="Chunk identifier")
    doc_id: str = Field(..., description="Document identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Relevant chunk text...",
                "score": 0.85,
                "source_document": "example.pdf",
                "page_number": 5,
                "chunk_id": "chunk_123_4",
                "doc_id": "doc_123"
            }
        }


class QueryResult(BaseModel):
    """
    Complete result of a RAG query.

    Contains the generated answer, retrieved chunks used as context,
    and metadata about cost and performance. This is the primary output
    of the query pipeline.
    """
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer")
    retrieved_chunks: List[RetrievedChunk] = Field(
        default_factory=list,
        description="Chunks retrieved as context"
    )
    tokens_used: Dict[str, int] = Field(
        default_factory=dict,
        description="Token counts (input, output, total)"
    )
    cost: float = Field(0.0, description="Query cost in dollars")
    latency: float = Field(0.0, description="Query latency in seconds")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Query timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is RAG?",
                "answer": "RAG stands for Retrieval-Augmented Generation...",
                "retrieved_chunks": [],
                "tokens_used": {"input": 500, "output": 100, "total": 600},
                "cost": 0.02,
                "latency": 2.5,
                "metadata": {"model": "gpt-4"}
            }
        }


class IndexingResult(BaseModel):
    """
    Result of document indexing operation.

    Tracks statistics about the indexing process, including number of chunks
    created, embeddings generated, and costs incurred. Used to provide
    feedback to users after document upload.
    """
    doc_id: str = Field(..., description="Indexed document ID")
    success: bool = Field(..., description="Whether indexing succeeded")
    num_chunks: int = Field(0, description="Number of chunks created")
    num_embeddings: int = Field(0, description="Number of embeddings generated")
    cost: float = Field(0.0, description="Indexing cost in dollars")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (filename, chunk_size, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Indexing timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "doc_123",
                "success": True,
                "num_chunks": 42,
                "num_embeddings": 42,
                "cost": 0.004,
                "metadata": {
                    "filename": "example.pdf",
                    "chunk_size": 500,
                    "chunk_overlap": 50
                }
            }
        }
