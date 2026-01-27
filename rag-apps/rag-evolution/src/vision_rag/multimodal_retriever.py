"""
Unified retrieval for text and images
"""
from typing import List
from ..common.models import RetrievalResult


class MultimodalRetriever:
    """Retrieve and combine text and image results"""

    def __init__(self, multimodal_store):
        self.store = multimodal_store

    def retrieve(
        self,
        query: str,
        k: int = 5,
        include_images: bool = True,
        text_weight: float = 0.5
    ) -> dict:
        """
        Retrieve both text and images.

        Args:
            query: Search query
            k: Total number of results
            include_images: Whether to include images
            text_weight: Weight for text results (0-1)

        Returns:
            Dict with separate text and image results
        """
        if not include_images:
            # Text-only retrieval
            results = self.store.search(query, k=k, filter_type="text")
            return {
                "text_results": results,
                "image_results": [],
                "all_results": results
            }

        # Calculate how many of each type to retrieve
        k_text = int(k * text_weight)
        k_images = k - k_text

        # Retrieve text
        text_results = self.store.search(query, k=k_text * 2, filter_type="text")

        # Retrieve images
        image_results = self.store.search(query, k=k_images * 2, filter_type="image")

        # Take top k of each
        text_results = text_results[:k_text]
        image_results = image_results[:k_images]

        # Combine and sort by score
        all_results = text_results + image_results
        all_results.sort(key=lambda x: x.score, reverse=True)

        return {
            "text_results": text_results,
            "image_results": image_results,
            "all_results": all_results[:k]
        }

    def compare_with_text_only(
        self,
        query: str,
        k: int = 5
    ) -> dict:
        """
        Compare text-only vs multimodal retrieval.
        Used for demonstrating vision RAG benefits.
        """
        # Text-only
        text_only = self.retrieve(query, k=k, include_images=False)

        # Multimodal
        multimodal = self.retrieve(query, k=k, include_images=True)

        return {
            "text_only": text_only,
            "multimodal": multimodal,
            "improvement": {
                "added_images": len(multimodal["image_results"]),
                "avg_score_text_only": self._avg_score(text_only["all_results"]),
                "avg_score_multimodal": self._avg_score(multimodal["all_results"])
            }
        }

    def _avg_score(self, results: List[RetrievalResult]) -> float:
        """Calculate average score"""
        if not results:
            return 0.0
        return sum(r.score for r in results) / len(results)
