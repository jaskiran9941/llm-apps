import anthropic
from typing import List, Dict, Optional
from config.config import ANTHROPIC_API_KEY, DEFAULT_MODEL

class ClaudeWrapper:
    """Wrapper for Claude API with memory integration capabilities."""

    def __init__(self, api_key: str = ANTHROPIC_API_KEY, model: str = DEFAULT_MODEL):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate_response(
        self,
        user_message: str,
        system_prompt: str = "You are a helpful assistant.",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        retrieved_context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, any]:
        """
        Generate a response from Claude with optional memory context.

        Args:
            user_message: Current user question
            system_prompt: System instructions
            conversation_history: List of previous messages [{"role": "user", "content": "..."}]
            retrieved_context: Semantic memory context from RAG
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            Dict with 'response', 'tokens_used', 'context_included'
        """
        # Build the full system prompt with retrieved context
        full_system_prompt = system_prompt
        if retrieved_context:
            full_system_prompt += f"\n\n[RETRIEVED KNOWLEDGE]\n{retrieved_context}\n[END RETRIEVED KNOWLEDGE]\n\nUse the above knowledge to answer questions accurately."

        # Build message history
        messages = []

        # Add conversation history (episodic memory)
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=full_system_prompt,
            messages=messages
        )

        # Extract response text
        response_text = response.content[0].text

        # Calculate tokens used
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        return {
            "response": response_text,
            "tokens_used": tokens_used,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "context_included": {
                "retrieved_context": retrieved_context is not None,
                "conversation_history": len(conversation_history) if conversation_history else 0
            }
        }

    def generate_without_memory(
        self,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, any]:
        """Generate response without any memory context."""
        return self.generate_response(
            user_message=user_message,
            system_prompt="You are a helpful assistant.",
            conversation_history=None,
            retrieved_context=None,
            temperature=temperature,
            max_tokens=max_tokens
        )
