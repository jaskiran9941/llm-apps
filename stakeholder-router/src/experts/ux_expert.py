"""UX domain expert."""
from src.experts.base_expert import BaseExpert
from src.utils.prompts import get_ux_expert_prompt


class UXExpert(BaseExpert):
    """Expert in UX design and user experience."""

    def __init__(self, llm_client=None):
        """Initialize UX Expert."""
        super().__init__(expert_name="UX Expert", llm_client=llm_client)

    def _get_system_prompt(self) -> str:
        """Get UX expert system prompt."""
        return get_ux_expert_prompt()
