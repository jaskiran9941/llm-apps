"""Integration tests for end-to-end routing."""
import pytest
from unittest.mock import Mock, patch

from src.router.orchestrator import RoutingOrchestrator


class TestRoutingOrchestrator:
    """Integration tests for routing orchestrator."""

    @patch("src.router.orchestrator.LLMClient")
    def test_clear_pricing_query_routing(self, mock_llm_client_class):
        """Test end-to-end routing of clear pricing query."""
        mock_client = Mock()

        # Mock classification response
        mock_client.generate_json.return_value = {
            "category": "pricing",
            "confidence": 0.95,
            "reasoning": "Clear pricing question",
            "clarifying_questions": [],
        }

        # Mock expert response
        mock_client.generate.return_value = "Here's pricing advice..."

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=False,  # Skip OOD for simplicity
        )

        result = orchestrator.route_query("How should we price our product?")

        # Verify classification
        assert result.classification.category == "pricing"
        assert result.classification.confidence == 0.95

        # Verify routing
        assert len(result.expert_responses) == 1
        assert result.expert_responses[0].expert_name == "Pricing Expert"

        # Verify final response
        assert "Pricing Expert" in result.final_response
        assert result.metadata["routed_to"] == ["pricing"]

    @patch("src.router.orchestrator.LLMClient")
    def test_clear_ux_query_routing(self, mock_llm_client_class):
        """Test end-to-end routing of clear UX query."""
        mock_client = Mock()

        mock_client.generate_json.return_value = {
            "category": "ux",
            "confidence": 0.92,
            "reasoning": "Clear UX question",
            "clarifying_questions": [],
        }

        mock_client.generate.return_value = "Here's UX advice..."

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=False,
        )

        result = orchestrator.route_query("How can we improve the onboarding?")

        assert result.classification.category == "ux"
        assert len(result.expert_responses) == 1
        assert result.expert_responses[0].expert_name == "UX Expert"
        assert result.metadata["routed_to"] == ["ux"]

    @patch("src.router.orchestrator.LLMClient")
    def test_ambiguous_query_ask_clarifying(self, mock_llm_client_class):
        """Test ambiguous query with ask_clarifying strategy."""
        mock_client = Mock()

        mock_client.generate_json.return_value = {
            "category": "ambiguous",
            "confidence": 0.55,
            "reasoning": "Spans both domains",
            "clarifying_questions": ["Question 1?", "Question 2?"],
        }

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=False,
            ambiguity_strategy="ask_clarifying",
        )

        result = orchestrator.route_query("How do we design the pricing page?")

        assert result.classification.category == "ambiguous"
        assert result.ambiguity_resolution is not None
        assert result.ambiguity_resolution.strategy == "ask_clarifying"
        assert len(result.expert_responses) == 0  # No routing yet
        assert result.metadata.get("needs_clarification") is True
        assert "Question 1?" in result.final_response

    @patch("src.router.orchestrator.LLMClient")
    def test_ambiguous_query_route_both(self, mock_llm_client_class):
        """Test ambiguous query with route_both strategy."""
        mock_client = Mock()

        mock_client.generate_json.return_value = {
            "category": "ambiguous",
            "confidence": 0.55,
            "reasoning": "Spans both domains",
            "clarifying_questions": [],
        }

        mock_client.generate.return_value = "Expert response..."

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=False,
            ambiguity_strategy="route_both",
        )

        result = orchestrator.route_query("How do we optimize the checkout?")

        assert result.classification.category == "ambiguous"
        assert result.ambiguity_resolution.strategy == "route_both"
        assert len(result.expert_responses) == 2  # Both experts
        assert result.metadata["routed_to"] == ["pricing", "ux"]
        assert "Pricing Expert" in result.final_response
        assert "UX Expert" in result.final_response

    @patch("src.router.orchestrator.LLMClient")
    def test_ood_query_rejection(self, mock_llm_client_class):
        """Test OOD query is rejected."""
        mock_client = Mock()

        # OOD detection mock
        mock_client.generate_json.return_value = {
            "is_ood": True,
            "ood_category": "unrelated",
            "reasoning": "Completely unrelated",
        }

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=True,
        )

        result = orchestrator.route_query("What's the weather?")

        assert result.ood_result is not None
        assert result.ood_result.is_ood is True
        assert len(result.expert_responses) == 0  # Not routed
        assert result.metadata.get("rejected") is True
        assert "pricing and UX" in result.final_response

    @patch("src.router.orchestrator.LLMClient")
    def test_ood_from_classifier(self, mock_llm_client_class):
        """Test OOD detected by classifier."""
        mock_client = Mock()

        # Pass OOD detection
        mock_client.generate_json.side_effect = [
            {"is_ood": False, "ood_category": None, "reasoning": "OK"},
            {  # Classification
                "category": "ood",
                "confidence": 0.99,
                "reasoning": "Unrelated to product development",
                "clarifying_questions": [],
            },
        ]

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(llm_client=mock_client)

        result = orchestrator.route_query("Tell me a joke")

        assert result.classification.category == "ood"
        assert len(result.expert_responses) == 0
        assert result.metadata.get("rejected") is True

    @patch("src.router.orchestrator.LLMClient")
    def test_confidence_thresholds(self, mock_llm_client_class):
        """Test that confidence thresholds affect routing."""
        mock_client = Mock()

        mock_client.generate_json.return_value = {
            "category": "pricing",
            "confidence": 0.65,  # Medium confidence
            "reasoning": "Moderate certainty",
            "clarifying_questions": [],
        }

        mock_client.generate.return_value = "Response..."

        mock_llm_client_class.return_value = mock_client

        # With default thresholds, 0.65 should route normally
        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=False,
            confidence_threshold_high=0.8,
            confidence_threshold_low=0.5,
        )

        result = orchestrator.route_query("Pricing question")

        # Should route since confidence (0.65) is above low threshold (0.5)
        assert len(result.expert_responses) == 1
        assert result.expert_responses[0].expert_name == "Pricing Expert"

    @patch("src.router.orchestrator.LLMClient")
    def test_low_confidence_treated_as_ambiguous(self, mock_llm_client_class):
        """Test that low confidence triggers ambiguity handling."""
        mock_client = Mock()

        mock_client.generate_json.return_value = {
            "category": "pricing",
            "confidence": 0.3,  # Low confidence
            "reasoning": "Uncertain",
            "clarifying_questions": ["What do you mean?"],
        }

        mock_llm_client_class.return_value = mock_client

        orchestrator = RoutingOrchestrator(
            llm_client=mock_client,
            enable_ood_detection=False,
            ambiguity_strategy="ask_clarifying",
            confidence_threshold_low=0.5,
        )

        result = orchestrator.route_query("Unclear query")

        # Low confidence should trigger ambiguity handling
        assert result.ambiguity_resolution is not None
        assert result.metadata.get("needs_clarification") is True
