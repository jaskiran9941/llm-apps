"""
Semantic retrieval using vector similarity.

This is the foundation retrieval strategy for RAG. It works by:
1. Embedding the query
2. Finding chunks with similar embeddings
3. Returning top-k most similar chunks

Simple, fast, and effective for most queries.
"""

from typing import List, Optional, Dict, Any
from src.retrieval.base_retriever import BaseRetriever
from src.embeddings.embedding_manager import BaseEmbeddingManager
from src.vector_store.base_store import BaseVectorStore
from src.models import RetrievedChunk
from src.utils.logger import EducationalLogger
from config.settings import settings

logger = EducationalLogger(__name__)


class SemanticRetriever(BaseRetriever):
    """
    Retrieve chunks using semantic similarity.

    How it works:
    1. Query → Embedding (using same model as documents)
    2. Vector similarity search in vector store
    3. Return top-k most similar chunks

    Why it works:
    - Similar meaning = similar embeddings
    - No keyword matching required
    - Works across different phrasings of the same concept

    Example:
    - Query: "How do I reset my password?"
    - Will match: "Password reset instructions"
    - Will also match: "Changing your account credentials"
    - Won't require exact keywords

    Educational Note:
    ----------------
    Semantic search is powerful but has limitations:
    ✅ Handles synonyms and paraphrasing
    ✅ Understands context and meaning
    ❌ May miss exact keyword matches
    ❌ Can be confused by ambiguous queries

    For production, often combine with keyword search (hybrid retrieval).
    """

    def __init__(
        self,
        embedding_manager: BaseEmbeddingManager,
        vector_store: BaseVectorStore,
        min_score: float = None
    ):
        """
        Initialize semantic retriever.

        Args:
            embedding_manager: Embedding generator
            vector_store: Vector database
            min_score: Minimum similarity score threshold (0-1)
        """
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store
        self.min_score = min_score or settings.MIN_SIMILARITY_SCORE

        logger.log_step(
            "RETRIEVER_INIT",
            "Semantic retriever initialized",
            f"Using vector similarity with minimum score {self.min_score}"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve semantically similar chunks.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            filters: Optional metadata filters

        Returns:
            List of RetrievedChunk objects
        """
        logger.log_step(
            "RETRIEVAL",
            f"Query: '{query[:50]}...'",
            f"Finding {top_k} most semantically similar chunks"
        )

        # Step 1: Embed the query
        # CRITICAL: Must use same embedding model as documents!
        query_embedding = self.embedding_manager.embed_text(query)

        logger.debug(
            f"Query embedded: {len(query_embedding)} dimensions"
        )

        # Step 2: Search vector store
        search_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filters
        )

        # Step 3: Filter by minimum score and convert to RetrievedChunk
        retrieved_chunks = []

        for result in search_results:
            # Apply score threshold
            if result.score < self.min_score:
                logger.debug(
                    f"Chunk {result.chunk.chunk_id} filtered out: "
                    f"score {result.score:.3f} < {self.min_score}"
                )
                continue

            # Convert to RetrievedChunk with source information
            retrieved_chunk = RetrievedChunk(
                text=result.chunk.text,
                score=result.score,
                source_document=result.chunk.metadata.get("filename", "unknown"),
                page_number=result.chunk.metadata.get("page_number"),
                chunk_id=result.chunk.chunk_id,
                doc_id=result.chunk.doc_id
            )

            retrieved_chunks.append(retrieved_chunk)

        # Sort by score (highest first)
        retrieved_chunks.sort(key=lambda x: x.score, reverse=True)

        logger.log_metric(
            "Chunks retrieved",
            len(retrieved_chunks),
            f"Score range: {min(c.score for c in retrieved_chunks):.3f} - {max(c.score for c in retrieved_chunks):.3f}" if retrieved_chunks else "No results above threshold"
        )

        # Educational logging
        if retrieved_chunks:
            logger.info(f"Top result: score={retrieved_chunks[0].score:.3f}, "
                       f"source={retrieved_chunks[0].source_document}, "
                       f"page={retrieved_chunks[0].page_number}")
        else:
            logger.warning(
                f"No chunks found above threshold {self.min_score}. "
                f"Consider lowering threshold or rephrasing query."
            )

        return retrieved_chunks

    def get_retriever_info(self) -> Dict[str, Any]:
        """
        Get information about this retriever.

        Returns:
            Dictionary with configuration
        """
        return {
            "type": "semantic",
            "embedding_model": self.embedding_manager.model,
            "embedding_dimension": self.embedding_manager.get_embedding_dimension(),
            "vector_store": type(self.vector_store).__name__,
            "min_score": self.min_score,
            "description": "Pure semantic similarity using vector embeddings"
        }

    def explain_scores(self, retrieved_chunks: List[RetrievedChunk]) -> str:
        """
        Generate educational explanation of retrieval scores.

        Args:
            retrieved_chunks: Retrieved chunks with scores

        Returns:
            Human-readable explanation
        """
        if not retrieved_chunks:
            return "No chunks were retrieved. This might mean:\n" \
                   "- No documents have been indexed yet\n" \
                   "- The query is too different from any document content\n" \
                   "- The similarity threshold is too high"

        explanation = "Retrieval Score Explanation:\n\n"

        for i, chunk in enumerate(retrieved_chunks, 1):
            score = chunk.score

            # Interpret score
            if score >= 0.9:
                quality = "Excellent match"
            elif score >= 0.8:
                quality = "Good match"
            elif score >= 0.7:
                quality = "Moderate match"
            elif score >= 0.6:
                quality = "Weak match"
            else:
                quality = "Poor match"

            explanation += f"{i}. {quality} (score: {score:.3f})\n"
            explanation += f"   Source: {chunk.source_document}, Page: {chunk.page_number}\n"
            explanation += f"   Preview: {chunk.text[:100]}...\n\n"

        return explanation
