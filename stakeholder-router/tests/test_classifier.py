"""Tests for request classifier."""
import pytest
from unittest.mock import Mock, patch

from src.router.classifier import RequestClassifier, ClassificationResult


class TestRequestClassifier:
    """Test cases for RequestClassifier."""

    def test_classification_result_properties(self):
        """Test ClassificationResult property methods."""
        # Pricing
        result = ClassificationResult(
            category="pricing",
            confidence=0.9,
            reasoning="Test",
            clarifying_questions=[],
        )
        assert result.is_pricing
        assert not result.is_ux
        assert not result.is_ambiguous
        assert not result.is_ood
        assert result.has_high_confidence
        assert not result.has_medium_confidence
        assert not result.has_low_confidence

        # UX
        result = ClassificationResult(
            category="ux",
            confidence=0.7,
            reasoning="Test",
            clarifying_questions=[],
        )
        assert result.is_ux
        assert not result.is_pricing
        assert result.has_medium_confidence

        # Ambiguous
        result = ClassificationResult(
            category="ambiguous",
            confidence=0.4,
            reasoning="Test",
            clarifying_questions=["Q1", "Q2"],
        )
        assert result.is_ambiguous
        assert result.has_low_confidence

        # OOD
        result = ClassificationResult(
            category="ood", confidence=0.95, reasoning="Test", clarifying_questions=[]
        )
        assert result.is_ood

    @patch("src.router.classifier.LLMClient")
    def test_classify_pricing_query(self, mock_llm_client_class):
        """Test classifying a clear pricing query."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "category": "pricing",
            "confidence": 0.95,
            "reasoning": "Clear pricing strategy question",
            "clarifying_questions": [],
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("How should we price our SaaS product?")

        assert result.category == "pricing"
        assert result.confidence == 0.95
        assert result.is_pricing
        assert result.has_high_confidence

    @patch("src.router.classifier.LLMClient")
    def test_classify_ux_query(self, mock_llm_client_class):
        """Test classifying a clear UX query."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "category": "ux",
            "confidence": 0.92,
            "reasoning": "Clear UX design question",
            "clarifying_questions": [],
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("How can we improve the onboarding flow?")

        assert result.category == "ux"
        assert result.is_ux
        assert result.has_high_confidence

    @patch("src.router.classifier.LLMClient")
    def test_classify_ambiguous_query(self, mock_llm_client_class):
        """Test classifying an ambiguous query."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "category": "ambiguous",
            "confidence": 0.55,
            "reasoning": "Spans both UX and pricing",
            "clarifying_questions": [
                "Are you asking about visual design?",
                "Or pricing tier structure?",
            ],
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("How do we design the pricing page?")

        assert result.category == "ambiguous"
        assert result.is_ambiguous
        assert len(result.clarifying_questions) == 2
        assert result.has_medium_confidence

    @patch("src.router.classifier.LLMClient")
    def test_classify_ood_query(self, mock_llm_client_class):
        """Test classifying an OOD query."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "category": "ood",
            "confidence": 0.99,
            "reasoning": "Completely unrelated to product development",
            "clarifying_questions": [],
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("What's the weather today?")

        assert result.category == "ood"
        assert result.is_ood
        assert result.has_high_confidence

    @patch("src.router.classifier.LLMClient")
    def test_classify_handles_json_error(self, mock_llm_client_class):
        """Test that classifier handles JSON parsing errors gracefully."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "error": "Failed to parse JSON",
            "raw_response": "This is not JSON",
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("Test query")

        # Should fallback to ambiguous with low confidence
        assert result.category == "ambiguous"
        assert result.confidence == 0.3
        assert len(result.clarifying_questions) > 0

    @patch("src.router.classifier.LLMClient")
    def test_classify_validates_category(self, mock_llm_client_class):
        """Test that invalid categories are corrected."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "category": "invalid_category",
            "confidence": 0.8,
            "reasoning": "Test",
            "clarifying_questions": [],
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("Test query")

        # Should correct to ambiguous
        assert result.category == "ambiguous"

    @patch("src.router.classifier.LLMClient")
    def test_classify_clamps_confidence(self, mock_llm_client_class):
        """Test that confidence is clamped to valid range."""
        mock_client = Mock()
        mock_client.generate_json.return_value = {
            "category": "pricing",
            "confidence": 1.5,  # Invalid: > 1.0
            "reasoning": "Test",
            "clarifying_questions": [],
        }
        mock_llm_client_class.return_value = mock_client

        classifier = RequestClassifier(llm_client=mock_client)
        result = classifier.classify("Test query")

        # Should clamp to 1.0
        assert result.confidence == 1.0
