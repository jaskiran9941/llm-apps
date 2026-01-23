"""
Abstract base class for embedding generation.

This module defines the interface for embedding managers, enabling
different embedding providers to be swapped in (OpenAI, Cohere,
local models like sentence-transformers, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Union
from src.models import Chunk


class BaseEmbeddingManager(ABC):
    """
    Abstract base class for embedding generation.

    Embeddings are vector representations of text that capture semantic meaning.
    Similar texts have similar embeddings (measured by cosine similarity).

    Why abstract class:
    - Enables swapping embedding providers (OpenAI, Cohere, local models)
    - Consistent interface across different implementations
    - Easy to add new embedding strategies in future projects

    Educational Note:
    ----------------
    Embeddings are the foundation of semantic search:
    1. Convert text to numbers (vectors)
    2. Similar meaning = similar vectors
    3. Find similar vectors = find similar meaning

    Different embedding models have different characteristics:
    - OpenAI text-embedding-3-small: Good quality, low cost, 1536 dimensions
    - OpenAI text-embedding-3-large: Higher quality, higher cost, 3072 dimensions
    - Local models (sentence-transformers): Free but need hosting
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Batch processing is more efficient than individual calls:
        - Reduces API round trips
        - Often cheaper (some providers charge per request)
        - Faster overall processing

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.

        Different models produce different sized vectors:
        - text-embedding-3-small: 1536 dimensions
        - text-embedding-3-large: 3072 dimensions
        - sentence-transformers (e.g., all-MiniLM-L6-v2): 384 dimensions

        Returns:
            Embedding dimension
        """
        pass

    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        """
        Generate embeddings for a list of chunks.

        This is a convenience method that extracts text from chunks
        and calls embed_batch.

        Args:
            chunks: List of Chunk objects

        Returns:
            List of embedding vectors (same order as chunks)
        """
        texts = [chunk.text for chunk in chunks]
        return self.embed_batch(texts)
