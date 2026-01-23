"""Pricing domain expert."""
from src.experts.base_expert import BaseExpert
from src.utils.prompts import get_pricing_expert_prompt


class PricingExpert(BaseExpert):
    """Expert in pricing strategy and monetization."""

    def __init__(self, llm_client=None):
        """Initialize Pricing Expert."""
        super().__init__(expert_name="Pricing Expert", llm_client=llm_client)

    def _get_system_prompt(self) -> str:
        """Get pricing expert system prompt."""
        return get_pricing_expert_prompt()
