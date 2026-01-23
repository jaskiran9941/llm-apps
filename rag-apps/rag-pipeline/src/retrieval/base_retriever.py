"""
Abstract base class for retrievers.

Retrieval is a critical component of RAG. This module defines the interface
for different retrieval strategies that can be added in future projects.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.models import RetrievedChunk


class BaseRetriever(ABC):
    """
    Abstract base class for retrieval strategies.

    Retrievers take a query and return relevant chunks. Different
    retrieval strategies have different strengths:

    - Semantic Retrieval (Project 1):
      Pure vector similarity. Fast and simple.

    - Hybrid Retrieval (Project 3):
      Combines vector search with keyword search (BM25).
      Better for queries with specific terms.

    - Reranking Retrieval (Project 3):
      Two-stage: retrieve many candidates, then rerank.
      Higher quality but slower.

    - Context-Enhanced Retrieval (Project 4):
      Returns parent chunks or surrounding context.
      More context per result.

    Educational Note:
    ----------------
    The retrieval stage is often the bottleneck in RAG quality:
    - If you don't retrieve the right chunks, the LLM can't answer correctly
    - "Garbage in, garbage out" applies here
    - Worth experimenting with different strategies

    Trade-offs:
    - Precision vs Recall: Get exactly what you need vs get everything relevant
    - Speed vs Quality: Fast approximate search vs slower exact search
    - Cost vs Performance: More retrieved chunks = higher LLM costs
    """

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User's question or search query
            top_k: Number of chunks to retrieve
            filters: Optional metadata filters (e.g., {"doc_id": "specific_doc"})

        Returns:
            List of RetrievedChunk objects, sorted by relevance
        """
        pass

    @abstractmethod
    def get_retriever_info(self) -> Dict[str, Any]:
        """
        Get information about this retriever.

        Returns:
            Dictionary with retriever type, configuration, etc.
        """
        pass
