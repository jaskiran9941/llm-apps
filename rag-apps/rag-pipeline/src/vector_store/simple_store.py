"""
Simple in-memory vector store (ChromaDB alternative for Python 3.14).

This is a lightweight implementation that works without ChromaDB.
Uses numpy for cosine similarity calculations.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import pickle
from src.vector_store.base_store import BaseVectorStore
from src.models import Chunk, SearchResult
from src.utils.logger import EducationalLogger

logger = EducationalLogger(__name__)


class SimpleVectorStore(BaseVectorStore):
    """
    Simple in-memory vector store using numpy.

    This is a lightweight alternative to ChromaDB that works with Python 3.14.
    Perfect for learning and development, though not optimized for production.
    """

    def __init__(
        self,
        collection_name: str = "rag_documents",
        persist_directory: Path = None,
        similarity_metric: str = "cosine"
    ):
        """Initialize simple vector store."""
        self.collection_name = collection_name
        self.persist_directory = persist_directory or Path("./data/simple_db")
        self.similarity_metric = similarity_metric

        # In-memory storage
        self.chunks: List[Chunk] = []
        self.embeddings: List[np.ndarray] = []
        self.chunk_ids: List[str] = []

        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Try to load existing data
        self._load()

        logger.log_step(
            "VECTOR_STORE_INIT",
            f"Simple vector store at {self.persist_directory}",
            f"Using {self.similarity_metric} similarity (in-memory storage)"
        )

    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Add chunks with embeddings."""
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to add")
            return False

        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings"
            )

        logger.log_step(
            "ADDING_TO_STORE",
            f"Adding {len(chunks)} chunks",
            "Storing in memory"
        )

        for chunk, embedding in zip(chunks, embeddings):
            self.chunks.append(chunk)
            self.embeddings.append(np.array(embedding))
            self.chunk_ids.append(chunk.chunk_id)

        # Persist to disk
        self._save()

        logger.log_metric(
            "Chunks stored",
            len(chunks),
            f"Total chunks: {len(self.chunks)}"
        )

        return True

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar chunks."""
        if not self.embeddings:
            logger.warning("No documents in store")
            return []

        logger.log_step(
            "VECTOR_SEARCH",
            f"Searching for top {top_k} similar chunks",
            f"Comparing against {len(self.embeddings)} stored embeddings"
        )

        query_vec = np.array(query_embedding)

        # Calculate similarities
        similarities = []
        for i, emb in enumerate(self.embeddings):
            chunk = self.chunks[i]

            # Apply filters if provided
            if filter_dict:
                match = all(
                    chunk.metadata.get(k) == v or chunk.doc_id == v
                    for k, v in filter_dict.items()
                )
                if not match:
                    continue

            # Calculate similarity
            if self.similarity_metric == "cosine":
                similarity = self._cosine_similarity(query_vec, emb)
            elif self.similarity_metric == "l2":
                distance = np.linalg.norm(query_vec - emb)
                similarity = 1 / (1 + distance)
            else:  # inner product
                similarity = np.dot(query_vec, emb)

            similarities.append((i, similarity))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top-k
        results = []
        for idx, score in similarities[:top_k]:
            chunk = self.chunks[idx]
            results.append(SearchResult(chunk=chunk, score=float(score)))

        logger.log_metric(
            "Results found",
            len(results),
            f"Scores range: {min(r.score for r in results):.2f} - {max(r.score for r in results):.2f}" if results else "No results"
        )

        return results

    def delete_document(self, doc_id: str) -> bool:
        """Delete all chunks for a document."""
        logger.log_step(
            "DELETE_DOCUMENT",
            f"Deleting document {doc_id}",
            "Removing from memory"
        )

        # Find indices to remove
        indices_to_remove = [
            i for i, chunk in enumerate(self.chunks)
            if chunk.doc_id == doc_id
        ]

        # Remove in reverse order to maintain indices
        for idx in reversed(indices_to_remove):
            del self.chunks[idx]
            del self.embeddings[idx]
            del self.chunk_ids[idx]

        # Persist
        self._save()

        logger.info(f"Deleted {len(indices_to_remove)} chunks for document: {doc_id}")
        return True

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all unique documents."""
        docs = {}
        for chunk in self.chunks:
            doc_id = chunk.doc_id
            if doc_id not in docs:
                docs[doc_id] = {
                    'doc_id': doc_id,
                    'filename': chunk.metadata.get('filename', 'unknown'),
                    'num_chunks': 0
                }
            docs[doc_id]['num_chunks'] += 1

        return list(docs.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        documents = self.list_documents()

        return {
            "total_chunks": len(self.chunks),
            "total_documents": len(documents),
            "collection_name": self.collection_name,
            "distance_function": self.similarity_metric,
            "persist_directory": str(self.persist_directory)
        }

    def clear(self) -> bool:
        """Clear all data."""
        logger.warning(f"Clearing all data from collection '{self.collection_name}'")

        self.chunks = []
        self.embeddings = []
        self.chunk_ids = []

        # Remove persisted files
        db_file = self.persist_directory / f"{self.collection_name}.pkl"
        if db_file.exists():
            db_file.unlink()

        logger.info("Collection cleared")
        return True

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def _save(self):
        """Save to disk."""
        try:
            db_file = self.persist_directory / f"{self.collection_name}.pkl"

            data = {
                'chunks': self.chunks,
                'embeddings': [emb.tolist() for emb in self.embeddings],
                'chunk_ids': self.chunk_ids
            }

            with open(db_file, 'wb') as f:
                pickle.dump(data, f)

            logger.debug(f"Saved {len(self.chunks)} chunks to {db_file}")
        except Exception as e:
            logger.error(f"Failed to save: {str(e)}")

    def _load(self):
        """Load from disk."""
        try:
            db_file = self.persist_directory / f"{self.collection_name}.pkl"

            if not db_file.exists():
                logger.debug("No existing data to load")
                return

            with open(db_file, 'rb') as f:
                data = pickle.load(f)

            self.chunks = data['chunks']
            self.embeddings = [np.array(emb) for emb in data['embeddings']]
            self.chunk_ids = data['chunk_ids']

            logger.info(f"Loaded {len(self.chunks)} chunks from {db_file}")
        except Exception as e:
            logger.warning(f"Could not load existing data: {str(e)}")
