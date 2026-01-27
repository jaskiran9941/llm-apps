"""
Hybrid retrieval using Reciprocal Rank Fusion
"""
from typing import List, Dict
from ..models import RetrievalResult


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
            fused_result = RetrievalResult(
                content=result.content,
                score=score,
                chunk_id=result.chunk_id,
                page=result.page,
                result_type=result.result_type,
                metadata={
                    **result.metadata,
                    "retrieval_method": "hybrid_rrf"
                }
            )
            fused_results.append(fused_result)

        return fused_results
