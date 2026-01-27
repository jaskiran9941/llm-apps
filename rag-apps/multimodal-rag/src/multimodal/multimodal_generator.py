"""
Answer generation using cross-modal context.
"""

from openai import OpenAI
from typing import List, Dict, Any
import logging
import json
from pathlib import Path

from ..common.config import Config
from ..common.models import RetrievalResult, QueryResult
from ..common.utils import count_tokens, format_cost
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimodalGenerator:
    """Generate answers using multimodal context."""

    def __init__(self):
        """Initialize multimodal generator."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.chat_model = Config.CHAT_MODEL

    def generate_answer(
        self,
        query: str,
        retrieval_results: List[RetrievalResult],
        include_sources: bool = True
    ) -> QueryResult:
        """
        Generate answer from multimodal retrieval results.

        Args:
            query: User query
            retrieval_results: List of RetrievalResult objects
            include_sources: Whether to include source citations

        Returns:
            QueryResult object
        """
        start_time = time.time()

        # Build context from results
        context = self._build_context(retrieval_results)

        # Generate answer
        answer = self._call_gpt4(query, context, include_sources)

        # Calculate metrics
        processing_time = time.time() - start_time
        cost_estimate = self._estimate_cost(query, context, answer)

        result = QueryResult(
            query=query,
            answer=answer,
            sources=retrieval_results,
            processing_time=processing_time,
            cost_estimate=cost_estimate,
            metadata={
                "num_sources": len(retrieval_results),
                "source_types": self._count_source_types(retrieval_results)
            }
        )

        logger.info(f"Generated answer in {processing_time:.2f}s, cost: {format_cost(cost_estimate)}")
        return result

    def _build_context(self, results: List[RetrievalResult]) -> str:
        """
        Build context string from multimodal results.

        Args:
            results: List of RetrievalResult objects

        Returns:
            Context string
        """
        context_parts = []

        # Group by type
        by_type = {
            "text": [],
            "image": [],
            "table": [],
            "audio": []
        }

        for result in results:
            by_type[result.type].append(result)

        # Add text context
        if by_type["text"]:
            context_parts.append("=== TEXT CONTENT ===")
            for i, result in enumerate(by_type["text"], 1):
                context_parts.append(f"\n[Text {i}] {result.source_info}")
                context_parts.append(result.content)

        # Add image context
        if by_type["image"]:
            context_parts.append("\n=== IMAGES ===")
            for i, result in enumerate(by_type["image"], 1):
                context_parts.append(f"\n[Image {i}] {result.source_info}")
                context_parts.append(result.content)

        # Add table context
        if by_type["table"]:
            context_parts.append("\n=== TABLES ===")
            for i, result in enumerate(by_type["table"], 1):
                context_parts.append(f"\n[Table {i}] {result.source_info}")
                context_parts.append(result.content)

        # Add audio context
        if by_type["audio"]:
            context_parts.append("\n=== AUDIO TRANSCRIPTS ===")
            for i, result in enumerate(by_type["audio"], 1):
                context_parts.append(f"\n[Audio {i}] {result.source_info}")
                context_parts.append(result.content)

        return "\n".join(context_parts)

    def _call_gpt4(self, query: str, context: str, include_sources: bool) -> str:
        """
        Call GPT-4 to generate answer.

        Args:
            query: User query
            context: Context string
            include_sources: Whether to cite sources

        Returns:
            Generated answer
        """
        system_prompt = """You are a helpful AI assistant that answers questions using multimodal context including text, images, tables, and audio transcripts.

Guidelines:
- Answer the question accurately using the provided context
- Synthesize information across different modalities when relevant
- When referencing tables, mention specific data points
- When referencing images, describe what they show
- When referencing audio, mention timestamps if relevant
- Be concise but complete
- If the context doesn't contain enough information, say so
"""

        if include_sources:
            system_prompt += "\n- Cite your sources using [Text 1], [Table 2], [Image 1], [Audio 1] format"

        user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

    def _estimate_cost(self, query: str, context: str, answer: str) -> float:
        """
        Estimate the cost of generation.

        Args:
            query: User query
            context: Context string
            answer: Generated answer

        Returns:
            Estimated cost in USD
        """
        # Count tokens
        input_tokens = count_tokens(context + query) + 200  # +200 for system prompt
        output_tokens = count_tokens(answer)

        # Calculate cost
        input_cost = (input_tokens / 1000) * Config.COST_GPT4_INPUT
        output_cost = (output_tokens / 1000) * Config.COST_GPT4_OUTPUT

        return input_cost + output_cost

    def _count_source_types(self, results: List[RetrievalResult]) -> Dict[str, int]:
        """
        Count sources by type.

        Args:
            results: List of RetrievalResult objects

        Returns:
            Dictionary of counts by type
        """
        counts = {"text": 0, "image": 0, "table": 0, "audio": 0}

        for result in results:
            if result.type in counts:
                counts[result.type] += 1

        return counts

    def generate_summary(self, results: List[QueryResult]) -> str:
        """
        Generate a summary of multiple query results.

        Args:
            results: List of QueryResult objects

        Returns:
            Summary text
        """
        if not results:
            return "No query results to summarize."

        summary_parts = [
            f"Processed {len(results)} queries:",
            f"- Total processing time: {sum(r.processing_time for r in results):.2f}s",
            f"- Total cost: {format_cost(sum(r.cost_estimate for r in results))}",
            f"- Average sources per query: {sum(len(r.sources) for r in results) / len(results):.1f}",
        ]

        return "\n".join(summary_parts)
