"""
Text chunking strategies for RAG.

This module implements the Strategy pattern for chunking, making it easy
to add new chunking methods in future projects (semantic chunking,
recursive chunking, etc.).

Educational Note:
----------------
Chunking is one of the most important decisions in RAG. The trade-offs:

- Small chunks (100-300 tokens):
  ✅ Precise retrieval (get exactly what you need)
  ❌ Less context (may miss related info)
  ❌ More chunks = more embeddings = higher cost

- Large chunks (700-1500 tokens):
  ✅ More context per chunk
  ❌ Less precise (may include irrelevant text)
  ❌ Larger context window = higher LLM costs

- Overlap:
  Overlap between chunks helps maintain context across boundaries.
  Typical: 10-20% of chunk size
"""

import re
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models import Document, Chunk
from src.utils.logger import EducationalLogger
from config.settings import settings

logger = EducationalLogger(__name__)


class BaseChunker(ABC):
    """
    Abstract base class for chunking strategies.

    This enables the Strategy pattern: different chunking algorithms
    can be swapped in/out without changing other code.

    Future implementations might include:
    - SemanticChunker: Use embeddings to find natural break points
    - RecursiveChunker: Split by paragraphs, then sentences, then words
    - StructureAwareChunker: Respect document structure (headers, lists)
    """

    @abstractmethod
    def chunk(self, document: Document, **kwargs) -> List[Chunk]:
        """
        Split document into chunks.

        Args:
            document: Document to chunk
            **kwargs: Chunker-specific parameters

        Returns:
            List of Chunk objects
        """
        pass

    def _extract_page_number(self, text: str, position: int) -> int:
        """
        Determine page number for text at given position.

        Looks for nearest [PAGE X] marker before the position.

        Args:
            text: Full document text
            position: Character position in text

        Returns:
            Page number (1-indexed)
        """
        # Find all page markers before this position
        page_pattern = r'\[PAGE (\d+)\]'
        matches = list(re.finditer(page_pattern, text[:position]))

        if matches:
            # Return the last page marker before this position
            last_match = matches[-1]
            return int(last_match.group(1))

        # Default to page 1 if no marker found
        return 1


class FixedSizeChunker(BaseChunker):
    """
    Split text into fixed-size chunks with overlap.

    This is the simplest chunking strategy:
    1. Split text into chunks of approximately chunk_size characters
    2. Add overlap between chunks for context continuity
    3. Try to break at sentence boundaries when possible

    This implementation is used in Project 1. In Projects 2-4, you'll
    add more sophisticated chunking strategies.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separator: str = " "
    ):
        """
        Initialize fixed-size chunker.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            separator: Character to split on (default: space)
        """
        self.chunk_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP
        self.separator = separator

        logger.log_step(
            "CHUNKER_INIT",
            f"Fixed-size chunker: {self.chunk_size} chars, {self.chunk_overlap} overlap",
            f"Each chunk will be ~{self.chunk_size} characters with {self.chunk_overlap} character overlap for context continuity"
        )

    def chunk(self, document: Document, **kwargs) -> List[Chunk]:
        """
        Chunk document into fixed-size pieces.

        Algorithm:
        1. Clean page markers from text (but remember positions for metadata)
        2. Split into sentences
        3. Group sentences until reaching chunk_size
        4. Add overlap by including last N characters from previous chunk

        Args:
            document: Document to chunk

        Returns:
            List of Chunk objects with preserved metadata
        """
        text = document.text
        doc_id = document.doc_id

        logger.log_step(
            "CHUNKING",
            f"Document {doc_id}: {len(text)} chars",
            "Splitting into chunks at sentence boundaries"
        )

        # Store original text with page markers for page number extraction
        original_text = text

        # Remove page markers for cleaner chunks
        # But keep track of where they were for page number metadata
        text_clean = re.sub(r'\[PAGE \d+\]\s*', '', text)

        # Split into sentences (simple sentence boundary detection)
        sentences = self._split_into_sentences(text_clean)

        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # Check if adding this sentence exceeds chunk_size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = ' '.join(current_chunk)

                # Find position in original text to determine page number
                position = original_text.find(current_chunk[0])
                page_number = self._extract_page_number(original_text, position)

                # Create Chunk object
                chunk = Chunk(
                    chunk_id=f"{doc_id}_chunk_{chunk_index}",
                    doc_id=doc_id,
                    text=chunk_text,
                    metadata={
                        "chunk_index": chunk_index,
                        "page_number": page_number,
                        "char_count": len(chunk_text),
                        "filename": document.metadata.get("filename", "unknown")
                    }
                )
                chunks.append(chunk)
                chunk_index += 1

                # Start new chunk with overlap
                # Include last few sentences for context
                overlap_text = chunk_text[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                if overlap_text:
                    # Find sentences that fit in overlap
                    overlap_sentences = []
                    overlap_length = 0
                    for s in reversed(current_chunk):
                        if overlap_length + len(s) <= self.chunk_overlap:
                            overlap_sentences.insert(0, s)
                            overlap_length += len(s)
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_length = overlap_length
                else:
                    current_chunk = []
                    current_length = 0

            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 for space

        # Add final chunk if there's remaining text
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            position = original_text.find(current_chunk[0])
            page_number = self._extract_page_number(original_text, position)

            chunk = Chunk(
                chunk_id=f"{doc_id}_chunk_{chunk_index}",
                doc_id=doc_id,
                text=chunk_text,
                metadata={
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "char_count": len(chunk_text),
                    "filename": document.metadata.get("filename", "unknown")
                }
            )
            chunks.append(chunk)

        logger.log_metric(
            "Chunks created",
            len(chunks),
            f"Average size: {sum(len(c.text) for c in chunks) // len(chunks) if chunks else 0} chars"
        )

        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        This is a simple sentence splitter. More sophisticated versions
        could use NLP libraries like spaCy or NLTK.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple regex-based sentence splitting
        # Looks for periods, exclamation marks, question marks followed by space and capital letter
        sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
        sentences = sentence_endings.split(text)

        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences


class CharacterChunker(BaseChunker):
    """
    Simple character-based chunking (no sentence awareness).

    This is the most basic chunking strategy: just split every N characters.
    Generally worse than FixedSizeChunker because it can split mid-sentence.

    Included for educational purposes and as a baseline for comparison.
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP

    def chunk(self, document: Document, **kwargs) -> List[Chunk]:
        """
        Chunk document by character count.

        Args:
            document: Document to chunk

        Returns:
            List of Chunk objects
        """
        text = document.text
        doc_id = document.doc_id
        original_text = text

        # Remove page markers for cleaner chunks
        text_clean = re.sub(r'\[PAGE \d+\]\s*', '', text)

        chunks = []
        chunk_index = 0
        start = 0

        while start < len(text_clean):
            # Calculate end position
            end = start + self.chunk_size

            # Extract chunk
            chunk_text = text_clean[start:end]

            # Find page number
            page_number = self._extract_page_number(original_text, start)

            # Create Chunk object
            chunk = Chunk(
                chunk_id=f"{doc_id}_chunk_{chunk_index}",
                doc_id=doc_id,
                text=chunk_text,
                metadata={
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "char_count": len(chunk_text),
                    "filename": document.metadata.get("filename", "unknown")
                }
            )
            chunks.append(chunk)
            chunk_index += 1

            # Move start position (accounting for overlap)
            start = end - self.chunk_overlap

        return chunks
