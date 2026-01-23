"""Guardrails for OOD detection and ambiguity handling."""
from dataclasses import dataclass
from typing import List, Optional, Tuple

import structlog

from src.router.classifier import ClassificationResult
from src.utils.llm_client import LLMClient
from src.utils.prompts import get_ood_detection_prompt

logger = structlog.get_logger()


@dataclass
class OODResult:
    """Result of OOD detection."""

    is_ood: bool
    ood_category: Optional[str]  # "unrelated", "jailbreak", "inappropriate"
    reasoning: str
    suggested_response: Optional[str] = None


@dataclass
class AmbiguityResolution:
    """Resolution strategy for ambiguous queries."""

    strategy: str  # "ask_clarifying", "route_both", "pick_primary"
    target_experts: List[str]  # ["pricing"], ["ux"], or ["pricing", "ux"]
    clarifying_questions: List[str]
    reasoning: str


class OODDetector:
    """Detects out-of-distribution queries."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize OOD detector.

        Args:
            llm_client: Optional LLM client (creates default if not provided)
        """
        self.llm_client = llm_client or LLMClient()

    def detect_ood(self, query: str) -> OODResult:
        """Detect if query is out-of-distribution.

        Args:
            query: User's question or request

        Returns:
            OODResult indicating if query is OOD and why
        """
        logger.info("detecting_ood", query=query[:100])

        # Quick keyword-based pre-filter for obvious OOD cases
        ood_keywords = [
            "weather",
            "sports",
            "recipe",
            "joke",
            "ignore previous",
            "ignore all",
            "system prompt",
            "you are now",
        ]

        query_lower = query.lower()
        for keyword in ood_keywords:
            if keyword in query_lower:
                logger.info("ood_detected_by_keyword", keyword=keyword)
                return OODResult(
                    is_ood=True,
                    ood_category="unrelated" if keyword not in ["ignore", "system"] else "jailbreak",
                    reasoning=f"Query contains unrelated keyword: '{keyword}'",
                    suggested_response="I'm designed to help with product pricing and UX design questions. Could you ask about pricing strategy or user experience instead?",
                )

        # Use LLM for more nuanced detection
        try:
            prompt = get_ood_detection_prompt(query)
            messages = [{"role": "user", "content": prompt}]

            response_json = self.llm_client.generate_json(
                messages=messages,
                temperature=0.2,
            )

            is_ood = response_json.get("is_ood", False)
            ood_category = response_json.get("ood_category")
            reasoning = response_json.get("reasoning", "No reasoning provided")

            if is_ood:
                suggested_response = self._get_ood_response(ood_category)
            else:
                suggested_response = None

            logger.info("ood_detection_complete", is_ood=is_ood, category=ood_category)

            return OODResult(
                is_ood=is_ood,
                ood_category=ood_category,
                reasoning=reasoning,
                suggested_response=suggested_response,
            )

        except Exception as e:
            logger.error("ood_detection_error", error=str(e))
            # Fail open - don't block legitimate queries due to detection errors
            return OODResult(
                is_ood=False,
                ood_category=None,
                reasoning=f"OOD detection failed: {str(e)}",
            )

    def _get_ood_response(self, ood_category: Optional[str]) -> str:
        """Get appropriate response for OOD category."""
        responses = {
            "unrelated": "I'm designed to help with product pricing and UX design questions. Your query seems unrelated to these topics. Could you ask about pricing strategy or user experience instead?",
            "jailbreak": "I'm designed to help with product pricing and UX design questions. I can't help with that type of request.",
            "inappropriate": "I'm designed to help with product pricing and UX design questions. I can't assist with that request.",
        }
        return responses.get(ood_category or "unrelated", responses["unrelated"])


class AmbiguityHandler:
    """Handles ambiguous queries with different strategies."""

    STRATEGIES = ["ask_clarifying", "route_both", "pick_primary"]

    def __init__(self, default_strategy: str = "ask_clarifying"):
        """Initialize ambiguity handler.

        Args:
            default_strategy: Default strategy to use
        """
        if default_strategy not in self.STRATEGIES:
            raise ValueError(f"Invalid strategy. Must be one of: {self.STRATEGIES}")
        self.default_strategy = default_strategy

    def handle_ambiguous(
        self,
        query: str,
        classification: ClassificationResult,
        strategy: Optional[str] = None,
    ) -> AmbiguityResolution:
        """Handle an ambiguous query.

        Args:
            query: User's question
            classification: Classification result
            strategy: Optional strategy override

        Returns:
            AmbiguityResolution with routing decision
        """
        strategy = strategy or self.default_strategy

        if strategy not in self.STRATEGIES:
            logger.warning("invalid_strategy", strategy=strategy, using_default=self.default_strategy)
            strategy = self.default_strategy

        logger.info("handling_ambiguity", strategy=strategy, confidence=classification.confidence)

        if strategy == "ask_clarifying":
            return self._ask_clarifying(query, classification)
        elif strategy == "route_both":
            return self._route_both(query, classification)
        elif strategy == "pick_primary":
            return self._pick_primary(query, classification)
        else:
            # Fallback
            return self._ask_clarifying(query, classification)

    def _ask_clarifying(
        self,
        query: str,
        classification: ClassificationResult,
    ) -> AmbiguityResolution:
        """Strategy: Ask clarifying questions."""
        questions = classification.clarifying_questions or [
            "Are you asking about pricing strategy and monetization?",
            "Or are you asking about user experience and interface design?",
        ]

        return AmbiguityResolution(
            strategy="ask_clarifying",
            target_experts=[],
            clarifying_questions=questions,
            reasoning="Query is ambiguous - requesting clarification before routing",
        )

    def _route_both(
        self,
        query: str,
        classification: ClassificationResult,
    ) -> AmbiguityResolution:
        """Strategy: Route to both experts and compare."""
        return AmbiguityResolution(
            strategy="route_both",
            target_experts=["pricing", "ux"],
            clarifying_questions=[],
            reasoning="Query spans both domains - routing to both experts for comprehensive answer",
        )

    def _pick_primary(
        self,
        query: str,
        classification: ClassificationResult,
    ) -> AmbiguityResolution:
        """Strategy: Pick most likely expert based on keywords."""
        # Simple keyword-based heuristic
        pricing_keywords = ["price", "pricing", "cost", "tier", "plan", "revenue", "monetize"]
        ux_keywords = ["design", "ux", "ui", "interface", "user", "usability", "flow"]

        query_lower = query.lower()
        pricing_score = sum(1 for kw in pricing_keywords if kw in query_lower)
        ux_score = sum(1 for kw in ux_keywords if kw in query_lower)

        if pricing_score > ux_score:
            primary_expert = "pricing"
            reasoning = f"Keyword analysis suggests pricing focus (score: {pricing_score} vs {ux_score})"
        elif ux_score > pricing_score:
            primary_expert = "ux"
            reasoning = f"Keyword analysis suggests UX focus (score: {ux_score} vs {pricing_score})"
        else:
            # Tie - default to pricing
            primary_expert = "pricing"
            reasoning = "Keyword analysis inconclusive - defaulting to pricing expert"

        logger.info(
            "picked_primary_expert",
            expert=primary_expert,
            pricing_score=pricing_score,
            ux_score=ux_score,
        )

        return AmbiguityResolution(
            strategy="pick_primary",
            target_experts=[primary_expert],
            clarifying_questions=[],
            reasoning=reasoning,
        )
