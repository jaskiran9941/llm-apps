"""
RAG-specific answer generation.

This module orchestrates the generation phase of RAG:
1. Format retrieved chunks into context
2. Construct prompt with context
3. Generate answer using LLM
4. Return structured result with citations
"""

from typing import List, Optional
from src.generation.llm_manager import LLMManager
from src.models import RetrievedChunk, QueryResult
from src.utils.logger import EducationalLogger
from config.prompts import (
    SYSTEM_PROMPT,
    construct_rag_prompt,
    construct_no_rag_prompt,
    format_context
)
import time

logger = EducationalLogger(__name__)


class RAGGenerator:
    """
    Generate answers using Retrieval-Augmented Generation.

    The RAG process:
    1. Retrieve relevant chunks (done by retriever)
    2. Format chunks into context
    3. Construct prompt: system + context + query
    4. Generate answer using LLM
    5. Return answer with metadata (sources, cost, etc.)

    Educational Note:
    ----------------
    Why RAG works:
    - Gives LLM specific, relevant information
    - Reduces hallucination (model has facts to work with)
    - Enables citations (model can reference sources)
    - Allows up-to-date information (just update documents)

    Trade-offs:
    - More tokens = higher cost (context + query + answer)
    - Quality depends on retrieval (bad retrieval = bad answer)
    - Longer prompts = slower responses
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        system_prompt: str = None
    ):
        """
        Initialize RAG generator.

        Args:
            llm_manager: LLM manager for text generation
            system_prompt: System prompt (defaults to RAG system prompt)
        """
        self.llm_manager = llm_manager
        self.system_prompt = system_prompt or SYSTEM_PROMPT

        logger.log_step(
            "GENERATOR_INIT",
            "RAG generator initialized",
            "Ready to generate answers using retrieved context"
        )

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[RetrievedChunk],
        include_sources: bool = True
    ) -> QueryResult:
        """
        Generate answer using RAG.

        Args:
            query: User's question
            retrieved_chunks: Chunks retrieved by retriever
            include_sources: Include source citations in metadata

        Returns:
            QueryResult with answer and metadata
        """
        logger.log_step(
            "RAG_GENERATION",
            f"Generating answer for: '{query[:50]}...'",
            f"Using {len(retrieved_chunks)} retrieved chunks as context"
        )

        # Start timing
        start_time = time.time()

        # Construct RAG prompt with context
        prompt = construct_rag_prompt(query, retrieved_chunks)

        # Log prompt size for educational purposes
        prompt_tokens = self.llm_manager.count_prompt_tokens(
            prompt,
            self.system_prompt
        )
        logger.log_metric(
            "Prompt size",
            f"{prompt_tokens} tokens",
            "Larger context = more tokens = higher cost but better answers"
        )

        # Generate answer
        result = self.llm_manager.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        # Calculate total latency
        total_latency = time.time() - start_time

        # Create QueryResult
        query_result = QueryResult(
            query=query,
            answer=result["answer"],
            retrieved_chunks=retrieved_chunks if include_sources else [],
            tokens_used=result["tokens"],
            cost=result["cost"],
            latency=total_latency,
            metadata={
                "model": result["model"],
                "temperature": result["temperature"],
                "num_chunks_used": len(retrieved_chunks),
                "prompt_tokens": prompt_tokens
            }
        )

        logger.log_metric(
            "Answer generated",
            f"{len(result['answer'])} chars",
            f"Cost: ${result['cost']:.4f}, Time: {total_latency:.2f}s"
        )

        return query_result

    def generate_without_rag(
        self,
        query: str
    ) -> QueryResult:
        """
        Generate answer WITHOUT retrieval (for comparison).

        This is useful for demonstrating the value of RAG:
        - Compare RAG answer vs non-RAG answer
        - See how context improves accuracy
        - Understand when RAG is necessary vs when base knowledge suffices

        Args:
            query: User's question

        Returns:
            QueryResult without retrieved chunks
        """
        logger.log_step(
            "NO_RAG_GENERATION",
            "Generating answer WITHOUT retrieval",
            "Using only the model's base knowledge (no document context)"
        )

        # Start timing
        start_time = time.time()

        # Construct prompt without context
        prompt = construct_no_rag_prompt(query)

        # Generate answer
        result = self.llm_manager.generate(
            prompt=prompt,
            system_prompt=None  # No system prompt for non-RAG
        )

        # Calculate total latency
        total_latency = time.time() - start_time

        # Create QueryResult
        query_result = QueryResult(
            query=query,
            answer=result["answer"],
            retrieved_chunks=[],  # No chunks used
            tokens_used=result["tokens"],
            cost=result["cost"],
            latency=total_latency,
            metadata={
                "model": result["model"],
                "temperature": result["temperature"],
                "mode": "no_rag"
            }
        )

        logger.log_metric(
            "Non-RAG answer generated",
            f"{len(result['answer'])} chars",
            f"Cost: ${result['cost']:.4f}, Time: {total_latency:.2f}s"
        )

        return query_result

    def explain_answer_quality(self, query_result: QueryResult) -> str:
        """
        Generate educational explanation of answer quality.

        Args:
            query_result: Result from generation

        Returns:
            Human-readable explanation
        """
        explanation = "Answer Quality Analysis:\n\n"

        # Check if RAG was used
        if query_result.retrieved_chunks:
            explanation += "✅ RAG Mode: Answer based on retrieved context\n"
            explanation += f"   - {len(query_result.retrieved_chunks)} chunks used\n"

            # Analyze chunk quality
            avg_score = sum(c.score for c in query_result.retrieved_chunks) / len(query_result.retrieved_chunks)
            explanation += f"   - Average relevance: {avg_score:.3f}\n"

            if avg_score >= 0.8:
                explanation += "   - High relevance: Answer should be accurate\n"
            elif avg_score >= 0.6:
                explanation += "   - Moderate relevance: Answer may be partially accurate\n"
            else:
                explanation += "   - Low relevance: Answer may not be reliable\n"

            # Check for diverse sources
            sources = set(c.source_document for c in query_result.retrieved_chunks)
            explanation += f"   - Sources used: {', '.join(sources)}\n"

        else:
            explanation += "❌ Non-RAG Mode: Answer based on model's base knowledge\n"
            explanation += "   - No document context used\n"
            explanation += "   - May not reflect your specific documents\n"

        # Cost analysis
        explanation += f"\nCost: ${query_result.cost:.4f}\n"
        explanation += f"Tokens: {query_result.tokens_used['total']} total "
        explanation += f"({query_result.tokens_used['input']} input, "
        explanation += f"{query_result.tokens_used['output']} output)\n"

        # Performance
        explanation += f"Latency: {query_result.latency:.2f}s\n"

        return explanation
