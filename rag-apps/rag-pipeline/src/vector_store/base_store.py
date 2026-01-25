"""
Abstract base class for vector stores.

Defines the interface for vector storage and retrieval, enabling
different vector DB implementations to be swapped (ChromaDB, Pinecone,
Weaviate, FAISS, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.models import Chunk, SearchResult


class BaseVectorStore(ABC):
    """
    Abstract base class for vector storage.

    Vector stores are specialized databases for similarity search:
    - Store embeddings (vectors) with metadata
    - Fast similarity search (find nearest neighbors)
    - Support filtering by metadata

    Popular implementations:
    - ChromaDB: Local, easy to use, good for development
    - Pinecone: Cloud-hosted, scalable, production-ready
    - Weaviate: Open-source, feature-rich
    - FAISS: Facebook's library, very fast but in-memory

    Educational Note:
    ----------------
    Vector databases are optimized for similarity search:
    1. Index vectors using approximate nearest neighbor (ANN) algorithms
    2. Much faster than brute-force comparison
    3. Trade-off: slight accuracy loss for huge speed gains

    Example: Finding 5 most similar items from 1M vectors:
    - Brute force: O(n) = 1M comparisons
    - ANN (e.g., HNSW): O(log n) = ~20 comparisons
    """

    @abstractmethod
    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Add documents (chunks) with their embeddings to the store.

        Args:
            chunks: List of Chunk objects
            embeddings: Corresponding embedding vectors
            metadata: Optional additional metadata for each chunk

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return
            filter_dict: Optional metadata filters (e.g., {"doc_id": "doc_123"})

        Returns:
            List of SearchResult objects (chunk + similarity score)
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document.

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the store.

        Returns:
            List of document metadata
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with stats (num_chunks, num_documents, etc.)
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all data from the store.

        WARNING: This deletes everything!

        Returns:
            True if successful
        """
        pass
