"""LLM client abstraction for Anthropic API."""
import json
from typing import Any, Dict, List, Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from src.config.settings import anthropic_settings

logger = structlog.get_logger()


class LLMClient:
    """Wrapper for Anthropic API with retry logic."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        self.api_key = api_key or anthropic_settings.api_key
        self.model = model or anthropic_settings.model
        self.max_tokens = max_tokens or anthropic_settings.max_tokens
        self.temperature = temperature or anthropic_settings.temperature
        self.client = anthropic.Anthropic(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def generate(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Generate a response from Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            max_tokens: Optional override for max tokens
            temperature: Optional override for temperature
            **kwargs: Additional arguments to pass to the API

        Returns:
            Generated text response
        """
        try:
            request_params = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "messages": messages,
                **kwargs,
            }

            if system:
                request_params["system"] = system

            logger.info(
                "llm_request",
                model=self.model,
                num_messages=len(messages),
                has_system=bool(system),
            )

            response = self.client.messages.create(**request_params)

            text_response = response.content[0].text
            logger.info(
                "llm_response",
                response_length=len(text_response),
                stop_reason=response.stop_reason,
            )

            return text_response

        except Exception as e:
            logger.error("llm_error", error=str(e), error_type=type(e).__name__)
            raise

    def generate_json(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a JSON response from Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt (should instruct JSON output)
            max_tokens: Optional override for max tokens
            temperature: Optional override for temperature
            **kwargs: Additional arguments to pass to the API

        Returns:
            Parsed JSON response as a dictionary
        """
        # Ensure system prompt requests JSON
        if system and "JSON" not in system:
            system = f"{system}\n\nYou must respond with valid JSON only. Do not include any other text."
        elif not system:
            system = "You must respond with valid JSON only. Do not include any other text."

        response_text = self.generate(
            messages=messages,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        # Parse JSON from response
        try:
            # Try to extract JSON if it's wrapped in code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()

            parsed_json = json.loads(json_str)
            logger.info("json_parsed_successfully", keys=list(parsed_json.keys()))
            return parsed_json

        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), response=response_text[:500])
            # Return a structured error response
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text,
                "parse_error": str(e),
            }
