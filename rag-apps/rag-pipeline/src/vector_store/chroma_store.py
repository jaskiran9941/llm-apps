"""
ChromaDB vector store implementation.

ChromaDB is an excellent choice for learning RAG:
- Runs locally (no API keys needed for the DB itself)
- Persistent storage
- Good performance for moderate datasets
- Easy to use
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.vector_store.base_store import BaseVectorStore
from src.models import Chunk, SearchResult
from src.utils.logger import EducationalLogger
from config.settings import settings

logger = EducationalLogger(__name__)


class ChromaVectorStore(BaseVectorStore):
    """
    Vector store using ChromaDB.

    ChromaDB features:
    - Persistent storage (survives restarts)
    - Supports cosine similarity, L2, and inner product
    - Built-in metadata filtering
    - Good for datasets up to ~millions of vectors

    Educational Note:
    ----------------
    Similarity metrics:
    - Cosine similarity: Measures angle between vectors (ignores magnitude)
      Best for: Text embeddings (direction matters more than magnitude)
    - L2 (Euclidean): Measures straight-line distance
      Best for: When magnitude matters
    - Inner Product (IP): Dot product of vectors
      Best for: When vectors are normalized
    """

    def __init__(
        self,
        collection_name: str = None,
        persist_directory: Path = None,
        similarity_metric: str = None
    ):
        """
        Initialize ChromaDB vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistent storage
            similarity_metric: Distance metric ("cosine", "l2", "ip")
        """
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.persist_directory = persist_directory or settings.CHROMA_DB_DIR
        self.similarity_metric = similarity_metric or settings.SIMILARITY_METRIC

        # Map similarity metric to ChromaDB distance function
        # Note: ChromaDB uses distance, not similarity
        # For cosine: distance = 1 - similarity
        metric_map = {
            "cosine": "cosine",
            "l2": "l2",
            "ip": "ip"
        }
        self.distance_function = metric_map.get(
            self.similarity_metric,
            "cosine"
        )

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_function}
            )
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_function}
            )
            logger.info(f"Created new collection: {self.collection_name}")

        logger.log_step(
            "VECTOR_STORE_INIT",
            f"ChromaDB at {self.persist_directory}",
            f"Using {self.distance_function} distance for similarity search"
        )

    def add_documents(
        self,
        chunks: List[Chunk],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Add chunks with embeddings to ChromaDB.

        Args:
            chunks: List of Chunk objects
            embeddings: Corresponding embeddings
            metadata: Optional additional metadata

        Returns:
            True if successful
        """
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
            "Storing embeddings and metadata for similarity search"
        )

        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]

        # Combine chunk metadata with additional metadata
        metadatas = []
        for i, chunk in enumerate(chunks):
            meta = {
                "doc_id": chunk.doc_id,
                "chunk_index": chunk.metadata.get("chunk_index", i),
                "page_number": chunk.metadata.get("page_number", 0),
                "filename": chunk.metadata.get("filename", "unknown"),
                "char_count": chunk.metadata.get("char_count", len(chunk.text))
            }

            # Add additional metadata if provided
            if metadata and i < len(metadata):
                meta.update(metadata[i])

            metadatas.append(meta)

        try:
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )

            logger.log_metric(
                "Chunks stored",
                len(chunks),
                f"in collection '{self.collection_name}'"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            return False

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar chunks.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of SearchResult objects
        """
        logger.log_step(
            "VECTOR_SEARCH",
            f"Searching for top {top_k} similar chunks",
            "Finding chunks with highest semantic similarity to query"
        )

        try:
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_dict,  # Metadata filtering
                include=["documents", "metadatas", "distances"]
            )

            # Convert to SearchResult objects
            search_results = []

            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    chunk_id = results['ids'][0][i]
                    document = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]

                    # Convert distance to similarity score
                    # For cosine distance: similarity = 1 - distance
                    # This gives us a score in [0, 1] where 1 is most similar
                    if self.distance_function == "cosine":
                        score = 1 - distance
                    elif self.distance_function == "l2":
                        # For L2, convert to similarity (inverse relationship)
                        # Smaller distance = higher similarity
                        score = 1 / (1 + distance)
                    else:  # ip (inner product)
                        # Higher inner product = higher similarity
                        score = distance

                    # Ensure score is in [0, 1]
                    score = max(0.0, min(1.0, score))

                    # Create Chunk object
                    chunk = Chunk(
                        chunk_id=chunk_id,
                        doc_id=metadata.get("doc_id", "unknown"),
                        text=document,
                        metadata=metadata
                    )

                    # Create SearchResult
                    search_result = SearchResult(
                        chunk=chunk,
                        score=score
                    )

                    search_results.append(search_result)

            logger.log_metric(
                "Results found",
                len(search_results),
                f"Scores range: {min(r.score for r in search_results):.2f} - {max(r.score for r in search_results):.2f}" if search_results else "No results"
            )

            return search_results

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document.

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        logger.log_step(
            "DELETE_DOCUMENT",
            f"Deleting document {doc_id}",
            "Removing all chunks for this document"
        )

        try:
            # Delete all chunks with this doc_id
            self.collection.delete(
                where={"doc_id": doc_id}
            )

            logger.info(f"Deleted document: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {str(e)}")
            return False

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all unique documents in the store.

        Returns:
            List of document info (doc_id, filename, num_chunks)
        """
        try:
            # Get all items
            results = self.collection.get(
                include=["metadatas"]
            )

            # Group by doc_id
            docs = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('doc_id')
                if doc_id and doc_id not in docs:
                    docs[doc_id] = {
                        'doc_id': doc_id,
                        'filename': metadata.get('filename', 'unknown'),
                        'num_chunks': 0
                    }
                if doc_id:
                    docs[doc_id]['num_chunks'] += 1

            return list(docs.values())

        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with stats
        """
        try:
            count = self.collection.count()
            documents = self.list_documents()

            return {
                "total_chunks": count,
                "total_documents": len(documents),
                "collection_name": self.collection_name,
                "distance_function": self.distance_function,
                "persist_directory": str(self.persist_directory)
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {}

    def clear(self) -> bool:
        """
        Delete all data from the collection.

        WARNING: This is irreversible!

        Returns:
            True if successful
        """
        logger.warning(f"Clearing all data from collection '{self.collection_name}'")

        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)

            # Recreate empty collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": self.distance_function}
            )

            logger.info("Collection cleared and recreated")
            return True

        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            return False
