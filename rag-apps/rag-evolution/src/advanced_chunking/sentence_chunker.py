"""
Sentence-aware chunking that respects sentence boundaries
"""
from typing import List
import nltk
from ..common.models import Chunk
from ..common.utils import generate_id

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class SentenceChunker:
    """
    Chunks text by sentences, respecting natural boundaries.
    Improvement over fixed-size chunking.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, page: int = 0) -> List[Chunk]:
        """Split text into sentence-aware chunks"""
        # Split into sentences
        sentences = nltk.sent_tokenize(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk)
                chunks.append(self._create_chunk(chunk_text, page))

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk,
                    self.chunk_overlap
                )
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, page))

        return chunks

    def _create_chunk(self, text: str, page: int) -> Chunk:
        """Create a chunk object"""
        return Chunk(
            content=text,
            page=page,
            chunk_id=generate_id(text),
            metadata={
                "chunking_strategy": "sentence",
                "is_complete": True,  # Always complete sentences
                "num_sentences": len(nltk.sent_tokenize(text))
            }
        )

    def _get_overlap_sentences(self, sentences: List[str], overlap_size: int) -> List[str]:
        """Get sentences for overlap"""
        overlap_sentences = []
        overlap_length = 0

        # Take sentences from the end until we reach overlap size
        for sentence in reversed(sentences):
            if overlap_length + len(sentence) > overlap_size:
                break
            overlap_sentences.insert(0, sentence)
            overlap_length += len(sentence)

        return overlap_sentences

    def analyze_chunks(self, chunks: List[Chunk]) -> dict:
        """Analyze chunk quality"""
        if not chunks:
            return {}

        return {
            "total_chunks": len(chunks),
            "complete_chunks": len(chunks),  # All are complete
            "incomplete_chunks": 0,
            "completeness_rate": 1.0,
            "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks),
            "avg_sentences_per_chunk": sum(
                c.metadata.get("num_sentences", 0) for c in chunks
            ) / len(chunks)
        }
