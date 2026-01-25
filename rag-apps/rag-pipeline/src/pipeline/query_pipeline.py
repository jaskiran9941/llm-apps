"""
Query execution pipeline.

Orchestrates the full RAG query process:
Query → Embed → Retrieve → Generate → Return Answer

This pipeline is responsible for answering user questions using indexed documents.
"""

from typing import Optional, Dict, Any
from src.models import QueryResult
from src.retrieval.base_retriever import BaseRetriever
from src.generation.rag_generator import RAGGenerator
from src.utils.logger import EducationalLogger
from src.utils.validators import validate_query
import time

logger = EducationalLogger(__name__)


class QueryPipeline:
    """
    End-to-end query execution pipeline for RAG.

    This pipeline implements the full RAG workflow:

    1. Validate query
    2. Retrieve relevant chunks (retriever handles embedding)
    3. Generate answer using retrieved context
    4. Return structured result with metadata

    Educational Note:
    ----------------
    The query pipeline is run for each user question. It should be:
    - Fast: Users expect quick responses
    - Accurate: Retrieve the right chunks and generate good answers
    - Observable: Show what's happening (retrieved chunks, scores)
    - Cost-effective: Balance quality with token usage

    Design pattern: Strategy Pattern
    - Retriever is injected, can swap retrieval strategies
    - Generator is injected, can swap generation strategies
    - Easy to experiment with different approaches
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        generator: RAGGenerator
    ):
        """
        Initialize query pipeline.

        Args:
            retriever: Component for retrieving relevant chunks
            generator: Component for generating answers
        """
        self.retriever = retriever
        self.generator = generator

        logger.log_step(
            "PIPELINE_INIT",
            "Query pipeline initialized",
            "Ready to process questions using RAG"
        )

    def query(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        include_sources: bool = True
    ) -> QueryResult:
        """
        Execute RAG query.

        This is the main entry point for answering questions.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            filters: Optional metadata filters (e.g., specific document)
            include_sources: Include retrieved chunks in result

        Returns:
            QueryResult with answer and metadata
        """
        logger.info(f"{'='*60}")
        logger.info(f"Processing query: '{query}'")
        logger.info(f"{'='*60}")

        start_time = time.time()

        try:
            # Validate query
            validate_query(query)

            # Step 1: Retrieve relevant chunks
            logger.log_step(
                "STEP 1",
                f"Retrieving top {top_k} relevant chunks",
                "Finding most similar chunks using vector search"
            )

            retrieved_chunks = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                filters=filters
            )

            if not retrieved_chunks:
                logger.warning("No relevant chunks found!")
                logger.info(
                    "This could mean:\n"
                    "- No documents have been indexed\n"
                    "- Query is too different from any document content\n"
                    "- Similarity threshold is too high"
                )

            # Step 2: Generate answer using context
            logger.log_step(
                "STEP 2",
                "Generating answer",
                f"Using {len(retrieved_chunks)} chunks as context for LLM"
            )

            result = self.generator.generate_answer(
                query=query,
                retrieved_chunks=retrieved_chunks,
                include_sources=include_sources
            )

            # Log summary
            total_time = time.time() - start_time

            logger.info(f"{'='*60}")
            logger.info(f"✅ Query completed successfully!")
            logger.info(f"   - Chunks retrieved: {len(retrieved_chunks)}")
            logger.info(f"   - Answer length: {len(result.answer)} chars")
            logger.info(f"   - Cost: ${result.cost:.4f}")
            logger.info(f"   - Time: {total_time:.2f}s")
            logger.info(f"{'='*60}")

            return result

        except Exception as e:
            logger.error(f"❌ Query failed: {str(e)}")

            # Return error result
            return QueryResult(
                query=query,
                answer=f"Sorry, I encountered an error: {str(e)}",
                retrieved_chunks=[],
                tokens_used={"input": 0, "output": 0, "total": 0},
                cost=0.0,
                latency=time.time() - start_time,
                metadata={"error": str(e)}
            )

    def query_without_rag(self, query: str) -> QueryResult:
        """
        Execute query WITHOUT retrieval (for comparison).

        This demonstrates the difference between RAG and non-RAG:
        - RAG uses specific document context
        - Non-RAG uses only model's base knowledge

        Args:
            query: User's question

        Returns:
            QueryResult without retrieved chunks
        """
        logger.info(f"{'='*60}")
        logger.info(f"Processing NON-RAG query: '{query}'")
        logger.info(f"{'='*60}")

        try:
            validate_query(query)

            result = self.generator.generate_without_rag(query)

            logger.info(f"✅ Non-RAG query completed")
            logger.info(f"   - Answer length: {len(result.answer)} chars")
            logger.info(f"   - Cost: ${result.cost:.4f}")

            return result

        except Exception as e:
            logger.error(f"❌ Non-RAG query failed: {str(e)}")

            return QueryResult(
                query=query,
                answer=f"Sorry, I encountered an error: {str(e)}",
                retrieved_chunks=[],
                tokens_used={"input": 0, "output": 0, "total": 0},
                cost=0.0,
                latency=0.0,
                metadata={"error": str(e), "mode": "no_rag"}
            )

    def compare_rag_vs_no_rag(self, query: str, top_k: int = 5) -> Dict[str, QueryResult]:
        """
        Run same query with and without RAG for comparison.

        This is very educational for understanding RAG's value:
        - See how context improves answers
        - Compare costs (RAG is more expensive but more accurate)
        - Understand when RAG is necessary

        Args:
            query: User's question
            top_k: Number of chunks for RAG version

        Returns:
            Dictionary with 'rag' and 'no_rag' QueryResults
        """
        logger.info(f"Running RAG vs Non-RAG comparison for: '{query}'")

        # Run RAG version
        rag_result = self.query(query, top_k=top_k)

        # Run non-RAG version
        no_rag_result = self.query_without_rag(query)

        # Log comparison
        logger.info(f"\n{'='*60}")
        logger.info(f"RAG vs Non-RAG Comparison:")
        logger.info(f"{'='*60}")
        logger.info(f"RAG:")
        logger.info(f"   - Answer: {rag_result.answer[:100]}...")
        logger.info(f"   - Cost: ${rag_result.cost:.4f}")
        logger.info(f"   - Chunks used: {len(rag_result.retrieved_chunks)}")
        logger.info(f"\nNon-RAG:")
        logger.info(f"   - Answer: {no_rag_result.answer[:100]}...")
        logger.info(f"   - Cost: ${no_rag_result.cost:.4f}")
        logger.info(f"{'='*60}\n")

        return {
            "rag": rag_result,
            "no_rag": no_rag_result
        }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about pipeline configuration.

        Returns:
            Dictionary with pipeline details
        """
        return {
            "retriever": self.retriever.get_retriever_info(),
            "generator": {
                "model": self.generator.llm_manager.model,
                "temperature": self.generator.llm_manager.temperature,
                "max_tokens": self.generator.llm_manager.max_tokens
            }
        }
