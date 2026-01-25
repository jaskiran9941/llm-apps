"""
LLM API wrapper for text generation.

Handles interaction with OpenAI's API, including:
- Token counting and cost calculation
- Retry logic for reliability
- Error handling
"""

import time
from typing import Dict, Optional, List
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from src.utils.logger import EducationalLogger
from src.utils.metrics import count_tokens, calculate_llm_cost
from config.settings import settings

logger = EducationalLogger(__name__)


class LLMManager:
    """
    Manage interactions with Large Language Models.

    This wrapper provides:
    - Consistent interface for LLM calls
    - Automatic retry on failures
    - Token counting and cost tracking
    - Support for different models and parameters

    Educational Note:
    ----------------
    LLM Parameters:
    - Temperature (0-2): Controls randomness
      * 0 = deterministic, same answer every time
      * 0.7 = balanced (default)
      * 1+ = creative, more varied responses

    - Max tokens: Limits response length
      * Set based on your use case
      * Longer responses = higher cost

    - Top-p: Alternative to temperature (nucleus sampling)
      * Usually use either temperature OR top-p, not both
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        """
        Initialize LLM manager.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum response length
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.temperature = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens or settings.MAX_OUTPUT_TOKENS

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Track usage
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

        logger.log_step(
            "LLM_INIT",
            f"Model: {self.model}, Temperature: {self.temperature}",
            f"Using {self.model} for answer generation"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt (sets behavior)
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Dictionary with response text, tokens, cost, etc.
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Build messages
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        logger.log_step(
            "LLM_GENERATE",
            f"Generating response (temp={temp})",
            "Sending prompt to LLM for answer generation"
        )

        try:
            # Start timing
            start_time = time.time()

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )

            # Calculate latency
            latency = time.time() - start_time

            # Extract response
            answer = response.choices[0].message.content

            # Get token usage from response
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            # Calculate cost
            cost = calculate_llm_cost(input_tokens, output_tokens, self.model)

            # Track usage
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost

            logger.log_metric(
                "LLM Response",
                f"{output_tokens} tokens",
                f"Cost: ${cost:.4f}, Latency: {latency:.2f}s"
            )

            return {
                "answer": answer,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "cost": cost,
                "latency": latency,
                "model": self.model,
                "temperature": temp
            }

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise

    def count_prompt_tokens(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> int:
        """
        Count tokens in a prompt before sending.

        Useful for:
        - Estimating costs
        - Checking if prompt fits in context window
        - Optimizing prompt length

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Token count
        """
        text = prompt
        if system_prompt:
            text = system_prompt + "\n\n" + prompt

        return count_tokens(text, model=self.model)

    def estimate_cost(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        expected_output_tokens: int = 500
    ) -> float:
        """
        Estimate cost of a generation.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            expected_output_tokens: Estimated response length

        Returns:
            Estimated cost in USD
        """
        input_tokens = self.count_prompt_tokens(prompt, system_prompt)
        return calculate_llm_cost(input_tokens, expected_output_tokens, self.model)

    def get_usage_summary(self) -> Dict:
        """
        Get summary of LLM usage and costs.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "model": self.model,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
            "average_cost_per_request": (
                round(self.total_cost / max(1, self.total_input_tokens // 1000), 4)
            )
        }

    def reset_usage(self):
        """Reset usage tracking."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        logger.info("LLM usage statistics reset")
