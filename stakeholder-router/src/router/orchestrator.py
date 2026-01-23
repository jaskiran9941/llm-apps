"""Main routing orchestrator coordinating classification, guardrails, and experts."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

import structlog

from src.config.settings import router_settings
from src.router.classifier import RequestClassifier, ClassificationResult
from src.router.guardrails import OODDetector, AmbiguityHandler, AmbiguityResolution, OODResult
from src.experts.pricing_expert import PricingExpert
from src.experts.ux_expert import UXExpert
from src.experts.base_expert import ExpertResponse
from src.utils.llm_client import LLMClient

logger = structlog.get_logger()


@dataclass
class RoutingResult:
    """Result of routing a query through the system."""

    query: str
    classification: ClassificationResult
    ood_result: Optional[OODResult] = None
    ambiguity_resolution: Optional[AmbiguityResolution] = None
    expert_responses: List[ExpertResponse] = field(default_factory=list)
    final_response: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query": self.query,
            "classification": {
                "category": self.classification.category,
                "confidence": self.classification.confidence,
                "reasoning": self.classification.reasoning,
                "clarifying_questions": self.classification.clarifying_questions,
            },
            "ood_result": {
                "is_ood": self.ood_result.is_ood,
                "ood_category": self.ood_result.ood_category,
                "reasoning": self.ood_result.reasoning,
            } if self.ood_result else None,
            "ambiguity_resolution": {
                "strategy": self.ambiguity_resolution.strategy,
                "target_experts": self.ambiguity_resolution.target_experts,
                "clarifying_questions": self.ambiguity_resolution.clarifying_questions,
                "reasoning": self.ambiguity_resolution.reasoning,
            } if self.ambiguity_resolution else None,
            "expert_responses": [resp.to_dict() for resp in self.expert_responses],
            "final_response": self.final_response,
            "metadata": self.metadata,
        }


class RoutingOrchestrator:
    """Main orchestrator coordinating all routing components."""

    def __init__(
        self,
        enable_ood_detection: Optional[bool] = None,
        ambiguity_strategy: Optional[str] = None,
        confidence_threshold_high: Optional[float] = None,
        confidence_threshold_low: Optional[float] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        """Initialize orchestrator.

        Args:
            enable_ood_detection: Whether to enable OOD detection
            ambiguity_strategy: Strategy for handling ambiguous queries
            confidence_threshold_high: High confidence threshold
            confidence_threshold_low: Low confidence threshold
            llm_client: Optional shared LLM client
        """
        self.llm_client = llm_client or LLMClient()

        # Configuration
        self.enable_ood_detection = (
            enable_ood_detection
            if enable_ood_detection is not None
            else router_settings.enable_ood_detection
        )
        self.confidence_threshold_high = (
            confidence_threshold_high or router_settings.confidence_threshold_high
        )
        self.confidence_threshold_low = (
            confidence_threshold_low or router_settings.confidence_threshold_low
        )

        # Components
        self.classifier = RequestClassifier(llm_client=self.llm_client)
        self.ood_detector = OODDetector(llm_client=self.llm_client)
        self.ambiguity_handler = AmbiguityHandler(
            default_strategy=ambiguity_strategy or router_settings.default_strategy
        )

        # Experts
        self.pricing_expert = PricingExpert(llm_client=self.llm_client)
        self.ux_expert = UXExpert(llm_client=self.llm_client)

        logger.info(
            "orchestrator_initialized",
            ood_detection=self.enable_ood_detection,
            ambiguity_strategy=self.ambiguity_handler.default_strategy,
            threshold_high=self.confidence_threshold_high,
            threshold_low=self.confidence_threshold_low,
        )

    def route_query(
        self,
        query: str,
        ambiguity_strategy_override: Optional[str] = None,
    ) -> RoutingResult:
        """Route a query through the complete system.

        Args:
            query: User's question or request
            ambiguity_strategy_override: Optional override for ambiguity handling

        Returns:
            RoutingResult with all routing decisions and responses
        """
        logger.info("routing_query", query=query[:100])

        result = RoutingResult(query=query, classification=None)

        # Step 1: OOD Detection (pre-routing guardrail)
        if self.enable_ood_detection:
            ood_result = self.ood_detector.detect_ood(query)
            result.ood_result = ood_result

            if ood_result.is_ood:
                logger.info("query_rejected_ood", category=ood_result.ood_category)
                result.final_response = ood_result.suggested_response or "I can only help with pricing and UX questions."
                result.metadata["rejected"] = True
                result.metadata["rejection_reason"] = "ood"
                return result

        # Step 2: Classification
        classification = self.classifier.classify(query)
        result.classification = classification

        logger.info(
            "classification_result",
            category=classification.category,
            confidence=classification.confidence,
        )

        # Step 3: Handle OOD from classifier
        if classification.is_ood:
            logger.info("query_classified_as_ood")
            result.final_response = "I'm designed to help with product pricing and UX design questions. Your query seems outside my area of expertise. Could you ask about pricing strategy or user experience instead?"
            result.metadata["rejected"] = True
            result.metadata["rejection_reason"] = "ood_classification"
            return result

        # Step 4: Handle ambiguous queries
        if classification.is_ambiguous or classification.has_low_confidence:
            logger.info("handling_ambiguous_query", confidence=classification.confidence)

            ambiguity_resolution = self.ambiguity_handler.handle_ambiguous(
                query=query,
                classification=classification,
                strategy=ambiguity_strategy_override,
            )
            result.ambiguity_resolution = ambiguity_resolution

            # Strategy: Ask clarifying questions
            if ambiguity_resolution.strategy == "ask_clarifying":
                questions = "\n".join(
                    f"{i+1}. {q}"
                    for i, q in enumerate(ambiguity_resolution.clarifying_questions)
                )
                result.final_response = (
                    f"I need some clarification to route your query appropriately:\n\n{questions}\n\n"
                    f"Please let me know which aspect you're most interested in."
                )
                result.metadata["needs_clarification"] = True
                return result

            # Strategy: Route to both or pick primary
            target_experts = ambiguity_resolution.target_experts

        else:
            # Clear classification - route to single expert
            if classification.is_pricing:
                target_experts = ["pricing"]
            elif classification.is_ux:
                target_experts = ["ux"]
            else:
                # Fallback
                target_experts = ["pricing"]

        # Step 5: Execute expert routing
        expert_responses = self._route_to_experts(
            query=query,
            target_experts=target_experts,
        )
        result.expert_responses = expert_responses

        # Step 6: Aggregate responses
        final_response = self._aggregate_responses(
            expert_responses=expert_responses,
            target_experts=target_experts,
        )
        result.final_response = final_response

        result.metadata["routed_to"] = target_experts
        result.metadata["num_experts"] = len(target_experts)

        logger.info(
            "routing_complete",
            num_experts=len(target_experts),
            experts=target_experts,
        )

        return result

    def _route_to_experts(
        self,
        query: str,
        target_experts: List[str],
    ) -> List[ExpertResponse]:
        """Route query to specified experts.

        Args:
            query: User's question
            target_experts: List of expert names to route to

        Returns:
            List of expert responses
        """
        responses = []

        for expert_name in target_experts:
            logger.info("routing_to_expert", expert=expert_name)

            if expert_name == "pricing":
                response = self.pricing_expert.process_query(query)
            elif expert_name == "ux":
                response = self.ux_expert.process_query(query)
            else:
                logger.warning("unknown_expert", expert=expert_name)
                continue

            responses.append(response)

        return responses

    def _aggregate_responses(
        self,
        expert_responses: List[ExpertResponse],
        target_experts: List[str],
    ) -> str:
        """Aggregate expert responses into final response.

        Args:
            expert_responses: List of expert responses
            target_experts: List of expert names

        Returns:
            Aggregated final response
        """
        if not expert_responses:
            return "No expert responses available."

        # Single expert response
        if len(expert_responses) == 1:
            response = expert_responses[0]
            return f"**{response.expert_name}:**\n\n{response.response}"

        # Multiple expert responses
        parts = []
        for response in expert_responses:
            parts.append(f"**{response.expert_name}:**\n\n{response.response}")

        aggregated = "\n\n---\n\n".join(parts)

        # Add synthesis note
        synthesis_note = (
            "\n\n---\n\n**Note:** This query spans multiple domains. "
            "Above are perspectives from both our Pricing and UX experts."
        )

        return aggregated + synthesis_note
