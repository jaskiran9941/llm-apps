"""
Semantic chunking based on topic similarity
"""
from typing import List
import nltk
from ..common.models import Chunk
from ..common.utils import generate_id, calculate_cosine_similarity
from ..baseline_rag.text_embedder import TextEmbedder

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class SemanticChunker:
    """
    Chunks text based on semantic similarity.
    Starts new chunk when topic changes.
    """

    def __init__(self, similarity_threshold: float = 0.7, min_chunk_size: int = 200):
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.embedder = TextEmbedder()

    def chunk(self, text: str, page: int = 0) -> List[Chunk]:
        """Split text based on semantic similarity"""
        # Split into sentences
        sentences = nltk.sent_tokenize(text)

        if len(sentences) <= 1:
            return [self._create_chunk(text, page, topic_changes=0)]

        # Embed all sentences
        embeddings = self.embedder.embed_batch(sentences)

        chunks = []
        current_chunk = [sentences[0]]
        current_embedding = embeddings[0]
        topic_changes = 0

        for i in range(1, len(sentences)):
            # Calculate similarity with current chunk
            similarity = calculate_cosine_similarity(current_embedding, embeddings[i])

            # Check if we should start a new chunk
            chunk_text = " ".join(current_chunk)
            if (similarity < self.similarity_threshold and
                len(chunk_text) >= self.min_chunk_size):
                # Topic changed - create new chunk
                chunks.append(self._create_chunk(chunk_text, page, topic_changes))
                current_chunk = [sentences[i]]
                current_embedding = embeddings[i]
                topic_changes += 1
            else:
                # Continue current chunk
                current_chunk.append(sentences[i])
                # Update embedding to be average of chunk
                current_embedding = self._average_embeddings(
                    embeddings[i - len(current_chunk) + 1:i + 1]
                )

        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(self._create_chunk(chunk_text, page, topic_changes))

        return chunks

    def _create_chunk(self, text: str, page: int, topic_changes: int) -> Chunk:
        """Create a chunk object"""
        return Chunk(
            content=text,
            page=page,
            chunk_id=generate_id(text),
            metadata={
                "chunking_strategy": "semantic",
                "is_complete": True,
                "num_sentences": len(nltk.sent_tokenize(text)),
                "topic_changes": topic_changes
            }
        )

    def _average_embeddings(self, embeddings: List[List[float]]) -> List[float]:
        """Calculate average of embeddings"""
        if not embeddings:
            return []

        import numpy as np
        return np.mean(embeddings, axis=0).tolist()

    def analyze_chunks(self, chunks: List[Chunk]) -> dict:
        """Analyze chunk quality"""
        if not chunks:
            return {}

        total_topic_changes = sum(
            c.metadata.get("topic_changes", 0) for c in chunks
        )

        return {
            "total_chunks": len(chunks),
            "complete_chunks": len(chunks),
            "incomplete_chunks": 0,
            "completeness_rate": 1.0,
            "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks),
            "total_topic_changes": total_topic_changes,
            "avg_sentences_per_chunk": sum(
                c.metadata.get("num_sentences", 0) for c in chunks
            ) / len(chunks)
        }
