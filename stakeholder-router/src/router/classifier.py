"""JSON-based request classifier."""
from dataclasses import dataclass
from typing import List, Optional

import structlog

from src.utils.llm_client import LLMClient
from src.utils.prompts import get_classifier_prompt

logger = structlog.get_logger()


@dataclass
class ClassificationResult:
    """Result of query classification."""

    category: str  # "pricing", "ux", "ambiguous", "ood"
    confidence: float  # 0.0-1.0
    reasoning: str
    clarifying_questions: List[str]
    raw_response: Optional[dict] = None

    @property
    def is_pricing(self) -> bool:
        """Check if classified as pricing."""
        return self.category == "pricing"

    @property
    def is_ux(self) -> bool:
        """Check if classified as UX."""
        return self.category == "ux"

    @property
    def is_ambiguous(self) -> bool:
        """Check if classified as ambiguous."""
        return self.category == "ambiguous"

    @property
    def is_ood(self) -> bool:
        """Check if classified as out-of-distribution."""
        return self.category == "ood"

    @property
    def has_high_confidence(self) -> bool:
        """Check if confidence is high (>0.8)."""
        return self.confidence > 0.8

    @property
    def has_medium_confidence(self) -> bool:
        """Check if confidence is medium (0.5-0.8)."""
        return 0.5 <= self.confidence <= 0.8

    @property
    def has_low_confidence(self) -> bool:
        """Check if confidence is low (<0.5)."""
        return self.confidence < 0.5


class RequestClassifier:
    """Classifies user queries using Claude with JSON output."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize classifier.

        Args:
            llm_client: Optional LLM client (creates default if not provided)
        """
        self.llm_client = llm_client or LLMClient()
        self.system_prompt = get_classifier_prompt()

    def classify(self, query: str) -> ClassificationResult:
        """Classify a user query.

        Args:
            query: User's question or request

        Returns:
            ClassificationResult with category, confidence, and reasoning
        """
        logger.info("classifying_query", query=query[:100])

        messages = [{"role": "user", "content": query}]

        try:
            response_json = self.llm_client.generate_json(
                messages=messages,
                system=self.system_prompt,
                temperature=0.3,  # Lower temperature for more consistent classification
            )

            # Handle parsing errors
            if "error" in response_json:
                logger.error(
                    "classification_json_error",
                    error=response_json.get("error"),
                    raw_response=response_json.get("raw_response", "")[:200],
                )
                # Fallback to ambiguous with low confidence
                return ClassificationResult(
                    category="ambiguous",
                    confidence=0.3,
                    reasoning=f"Failed to parse classification: {response_json.get('error')}",
                    clarifying_questions=[
                        "Could you rephrase your question?",
                        "What specific aspect are you most interested in?",
                    ],
                    raw_response=response_json,
                )

            # Extract fields with validation
            category = response_json.get("category", "ambiguous")
            confidence = float(response_json.get("confidence", 0.5))
            reasoning = response_json.get("reasoning", "No reasoning provided")
            clarifying_questions = response_json.get("clarifying_questions", [])

            # Validate category
            valid_categories = ["pricing", "ux", "ambiguous", "ood"]
            if category not in valid_categories:
                logger.warning(
                    "invalid_category",
                    category=category,
                    valid_categories=valid_categories,
                )
                category = "ambiguous"

            # Validate confidence
            confidence = max(0.0, min(1.0, confidence))

            result = ClassificationResult(
                category=category,
                confidence=confidence,
                reasoning=reasoning,
                clarifying_questions=clarifying_questions,
                raw_response=response_json,
            )

            logger.info(
                "classification_complete",
                category=category,
                confidence=confidence,
                has_questions=len(clarifying_questions) > 0,
            )

            return result

        except Exception as e:
            logger.error("classification_error", error=str(e), error_type=type(e).__name__)
            # Return safe fallback
            return ClassificationResult(
                category="ambiguous",
                confidence=0.3,
                reasoning=f"Classification failed: {str(e)}",
                clarifying_questions=[
                    "Could you rephrase your question?",
                    "What specific aspect would you like help with?",
                ],
                raw_response={"error": str(e)},
            )
