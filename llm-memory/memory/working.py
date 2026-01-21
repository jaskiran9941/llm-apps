from typing import List, Dict

class WorkingMemory:
    """
    Manages working memory - intermediate reasoning steps.

    This is different from episodic/semantic:
    - Episodic: What happened in conversation
    - Semantic: Long-term knowledge
    - Working: How LLM thinks through problems (chain-of-thought)

    Less critical for basic demo, but shows another memory dimension.
    """

    def __init__(self):
        self.reasoning_steps = []

    def add_reasoning_step(self, step: str, step_type: str = "thought"):
        """
        Add a reasoning step.

        Args:
            step: The reasoning content
            step_type: Type of step (thought, calculation, conclusion)
        """
        self.reasoning_steps.append({
            "step": step,
            "type": step_type
        })

    def get_reasoning_trace(self) -> List[Dict]:
        """Get all reasoning steps."""
        return self.reasoning_steps

    def get_formatted_trace(self) -> str:
        """Get reasoning trace as formatted string."""
        if not self.reasoning_steps:
            return "No reasoning steps recorded."

        trace = "Chain of Thought:\n"
        for i, step in enumerate(self.reasoning_steps, 1):
            trace += f"{i}. [{step['type']}] {step['step']}\n"

        return trace

    def clear(self):
        """Clear working memory."""
        self.reasoning_steps = []

    def create_cot_prompt(self, base_prompt: str) -> str:
        """
        Create a chain-of-thought prompt.

        Adds instructions for step-by-step reasoning.
        """
        cot_instruction = """
Before answering, think through the problem step by step:
1. What is being asked?
2. What information do I have?
3. What's my reasoning process?
4. What's the final answer?

Show your reasoning, then provide the final answer.
"""
        return cot_instruction + "\n\n" + base_prompt
