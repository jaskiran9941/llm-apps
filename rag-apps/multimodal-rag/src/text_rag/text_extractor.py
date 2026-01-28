"""
Simple fixed-size chunker (demonstrates the problem)
"""
from typing import List
from ..common.models import Chunk
from ..common.utils import generate_id


class SimpleChunker:
    """
    Fixed-size chunker that breaks text at arbitrary positions.
    This is intentionally naive to demonstrate chunking problems.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, page: int = 0) -> List[Chunk]:
        """
        Split text into fixed-size chunks (character-based).
        PROBLEM: This breaks in the middle of sentences!
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunk = Chunk(
                    content=chunk_text,
                    page=page,
                    chunk_id=generate_id(chunk_text),
                    metadata={
                        "start_char": start,
                        "end_char": end,
                        "chunking_strategy": "fixed",
                        "is_complete": self._is_complete_chunk(chunk_text)
                    }
                )
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def _is_complete_chunk(self, text: str) -> bool:
        """
        Check if chunk ends with sentence boundary.
        Used to highlight problematic chunks in UI.
        """
        sentence_endings = ['.', '!', '?', '\n']
        return any(text.rstrip().endswith(ending) for ending in sentence_endings)

    def analyze_chunks(self, chunks: List[Chunk]) -> dict:
        """Analyze chunk quality for UI feedback"""
        if not chunks:
            return {}

        complete_chunks = sum(1 for c in chunks if c.metadata.get("is_complete", False))
        incomplete_chunks = len(chunks) - complete_chunks

        return {
            "total_chunks": len(chunks),
            "complete_chunks": complete_chunks,
            "incomplete_chunks": incomplete_chunks,
            "completeness_rate": complete_chunks / len(chunks) if chunks else 0,
            "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks)
        }
