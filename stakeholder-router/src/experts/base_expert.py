"""Base class for domain experts."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from src.utils.llm_client import LLMClient

logger = structlog.get_logger()


@dataclass
class ExpertResponse:
    """Standardized response from a domain expert."""

    expert_name: str
    response: str
    confidence: float
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "expert_name": self.expert_name,
            "response": self.response,
            "confidence": self.confidence,
            "sources": self.sources,
            "metadata": self.metadata,
        }


class BaseExpert(ABC):
    """Base class for domain experts."""

    def __init__(
        self,
        expert_name: str,
        llm_client: Optional[LLMClient] = None,
    ):
        """Initialize expert.

        Args:
            expert_name: Name of the expert (e.g., "Pricing Expert")
            llm_client: Optional LLM client (creates default if not provided)
        """
        self.expert_name = expert_name
        self.llm_client = llm_client or LLMClient()

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the expert's system prompt.

        Returns:
            System prompt defining expert's knowledge and behavior
        """
        pass

    def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExpertResponse:
        """Process a user query.

        Args:
            query: User's question or request
            context: Optional additional context

        Returns:
            ExpertResponse with answer and metadata
        """
        logger.info(
            "expert_processing_query",
            expert=self.expert_name,
            query=query[:100],
            has_context=bool(context),
        )

        # Build messages
        messages = [{"role": "user", "content": query}]

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            messages[0]["content"] = f"Context: {context_str}\n\nQuery: {query}"

        try:
            # Generate response
            response_text = self.llm_client.generate(
                messages=messages,
                system=self._get_system_prompt(),
                temperature=0.7,
            )

            # Calculate confidence based on response characteristics
            confidence = self._estimate_confidence(response_text)

            # Extract sources if mentioned
            sources = self._extract_sources(response_text)

            expert_response = ExpertResponse(
                expert_name=self.expert_name,
                response=response_text,
                confidence=confidence,
                sources=sources,
                metadata={
                    "query": query,
                    "context": context,
                    "response_length": len(response_text),
                },
            )

            logger.info(
                "expert_response_complete",
                expert=self.expert_name,
                response_length=len(response_text),
                confidence=confidence,
            )

            return expert_response

        except Exception as e:
            logger.error(
                "expert_processing_error",
                expert=self.expert_name,
                error=str(e),
                error_type=type(e).__name__,
            )

            # Return error response
            return ExpertResponse(
                expert_name=self.expert_name,
                response=f"I encountered an error processing your query: {str(e)}",
                confidence=0.0,
                sources=[],
                metadata={"error": str(e), "query": query},
            )

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into readable string."""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _estimate_confidence(self, response: str) -> float:
        """Estimate confidence based on response characteristics.

        This is a simple heuristic - in production you might want more sophisticated methods.
        """
        # Indicators of high confidence
        high_confidence_phrases = [
            "research shows",
            "industry standard",
            "best practice",
            "proven approach",
            "commonly used",
        ]

        # Indicators of low confidence
        low_confidence_phrases = [
            "might",
            "could",
            "perhaps",
            "it depends",
            "not sure",
            "unclear",
        ]

        response_lower = response.lower()

        high_count = sum(1 for phrase in high_confidence_phrases if phrase in response_lower)
        low_count = sum(1 for phrase in low_confidence_phrases if phrase in response_lower)

        # Base confidence
        confidence = 0.7

        # Adjust based on indicators
        confidence += high_count * 0.05
        confidence -= low_count * 0.1

        # Clamp to valid range
        return max(0.3, min(0.95, confidence))

    def _extract_sources(self, response: str) -> List[str]:
        """Extract mentioned sources from response.

        This is a simple heuristic - looks for company names or specific references.
        """
        sources = []

        # Common SaaS companies often referenced
        companies = [
            "Stripe",
            "Slack",
            "Notion",
            "Figma",
            "Atlassian",
            "Dropbox",
            "Zoom",
            "Salesforce",
        ]

        for company in companies:
            if company in response:
                sources.append(company)

        return sources
