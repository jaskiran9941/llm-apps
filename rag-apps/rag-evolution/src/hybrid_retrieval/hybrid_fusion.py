"""
Hybrid retrieval using Reciprocal Rank Fusion
"""
from typing import List, Dict
from ..common.models import RetrievalResult


class HybridFusion:
    """Combine multiple retrieval results using Reciprocal Rank Fusion"""

    def __init__(self, k: int = 60):
        """
        Initialize with RRF constant k.
        Default k=60 is commonly used in literature.
        """
        self.k = k

    def fuse(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        alpha: float = 0.5
    ) -> List[RetrievalResult]:
        """
        Fuse semantic and keyword results using RRF.

        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from BM25 search
            alpha: Weight for semantic results (1-alpha for keyword)

        Returns:
            Fused and reranked results
        """
        # Create score dictionaries
        scores: Dict[str, float] = {}
        results_map: Dict[str, RetrievalResult] = {}

        # Add semantic results
        for rank, result in enumerate(semantic_results):
            chunk_id = result.chunk_id
            rrf_score = alpha / (self.k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in results_map:
                results_map[chunk_id] = result

        # Add keyword results
        for rank, result in enumerate(keyword_results):
            chunk_id = result.chunk_id
            rrf_score = (1 - alpha) / (self.k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in results_map:
                results_map[chunk_id] = result

        # Sort by fused score
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Create fused results
        fused_results = []
        for chunk_id, score in sorted_ids:
            result = results_map[chunk_id]
            # Update score to fused score
            fused_result = RetrievalResult(
                content=result.content,
                score=score,
                chunk_id=result.chunk_id,
                page=result.page,
                result_type=result.result_type,
                metadata={
                    **result.metadata,
                    "retrieval_method": "hybrid_rrf",
                    "original_semantic_score": self._get_original_score(
                        result.chunk_id, semantic_results
                    ),
                    "original_keyword_score": self._get_original_score(
                        result.chunk_id, keyword_results
                    )
                }
            )
            fused_results.append(fused_result)

        return fused_results

    def _get_original_score(
        self,
        chunk_id: str,
        results: List[RetrievalResult]
    ) -> float:
        """Get original score from results"""
        for result in results:
            if result.chunk_id == chunk_id:
                return result.score
        return 0.0


class HybridRetriever:
    """Complete hybrid retrieval pipeline"""

    def __init__(self, vector_searcher, bm25_searcher, fusion: HybridFusion = None):
        self.vector_searcher = vector_searcher
        self.bm25_searcher = bm25_searcher
        self.fusion = fusion or HybridFusion()

    def search(
        self,
        query: str,
        k: int = 5,
        alpha: float = 0.5,
        retrieval_k: int = 20
    ) -> List[RetrievalResult]:
        """
        Perform hybrid search.

        Args:
            query: Search query
            k: Number of final results
            alpha: Weight for semantic vs keyword (0.5 = balanced)
            retrieval_k: Number of results to retrieve from each method before fusion

        Returns:
            Top k fused results
        """
        # Get results from both methods
        semantic_results = self.vector_searcher.search(query, k=retrieval_k)
        keyword_results = self.bm25_searcher.search(query, k=retrieval_k)

        # Fuse results
        fused_results = self.fusion.fuse(
            semantic_results,
            keyword_results,
            alpha=alpha
        )

        # Return top k
        return fused_results[:k]
