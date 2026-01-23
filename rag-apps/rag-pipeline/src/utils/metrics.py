"""
Metrics calculation for cost and performance tracking.

This module provides functions to calculate token counts, costs, and
other metrics for the RAG system. Understanding these metrics helps
optimize system performance and control expenses.
"""

import time
import tiktoken
from typing import Dict, Optional
from functools import wraps
from config.settings import settings


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text using tiktoken.

    Token counting is important because:
    1. OpenAI charges by token, not by character
    2. Models have token limits (e.g., GPT-4 has 8K/32K context limits)
    3. Helps estimate costs before making API calls

    Args:
        text: Text to count tokens in
        model: Model name for tokenizer selection

    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def calculate_embedding_cost(num_tokens: int) -> float:
    """
    Calculate cost for embedding generation.

    Args:
        num_tokens: Number of tokens to embed

    Returns:
        Cost in USD
    """
    return (num_tokens / 1000) * settings.EMBEDDING_COST_PER_1K


def calculate_llm_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4"
) -> float:
    """
    Calculate cost for LLM generation.

    Note: Input and output tokens have different prices. For GPT-4:
    - Input tokens are cheaper (reading context)
    - Output tokens are more expensive (generating response)

    Args:
        input_tokens: Number of input tokens (prompt + context)
        output_tokens: Number of output tokens (generated response)
        model: Model name

    Returns:
        Total cost in USD
    """
    input_cost = (input_tokens / 1000) * settings.GPT4_INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000) * settings.GPT4_OUTPUT_COST_PER_1K
    return input_cost + output_cost


def estimate_chunk_tokens(text: str, chunk_size: int) -> int:
    """
    Estimate number of chunks and total tokens.

    This helps predict costs before chunking. Rule of thumb:
    - 1 token ≈ 4 characters in English
    - But use tiktoken for accuracy

    Args:
        text: Full text to be chunked
        chunk_size: Target chunk size in characters

    Returns:
        Estimated total tokens
    """
    # Rough estimate: assume 75% of chunk_size due to sentence boundaries
    estimated_chunks = len(text) // int(chunk_size * 0.75)
    tokens_per_chunk = count_tokens(text[:chunk_size])
    return estimated_chunks * tokens_per_chunk


class Timer:
    """
    Context manager for timing operations.

    Example:
        with Timer() as timer:
            # do something
        print(f"Took {timer.elapsed:.2f} seconds")
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time


def measure_latency(func):
    """
    Decorator to measure function execution time.

    Example:
        @measure_latency
        def slow_function():
            time.sleep(2)

        # Function will log its execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Timer() as timer:
            result = func(*args, **kwargs)
        print(f"{func.__name__} took {timer.elapsed:.2f}s")
        return result
    return wrapper


class MetricsCollector:
    """
    Collect and aggregate metrics across operations.

    Useful for tracking costs and performance over multiple queries
    or document indexing operations.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all metrics to zero."""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_queries = 0
        self.total_documents = 0
        self.total_chunks = 0
        self.operation_times = []

    def record_embedding(self, num_tokens: int):
        """Record embedding generation."""
        self.total_tokens += num_tokens
        self.total_cost += calculate_embedding_cost(num_tokens)

    def record_llm_call(self, input_tokens: int, output_tokens: int):
        """Record LLM API call."""
        self.total_tokens += input_tokens + output_tokens
        self.total_cost += calculate_llm_cost(input_tokens, output_tokens)

    def record_query(self, latency: float):
        """Record query execution."""
        self.total_queries += 1
        self.operation_times.append(latency)

    def record_document(self, num_chunks: int):
        """Record document indexing."""
        self.total_documents += 1
        self.total_chunks += num_chunks

    def get_summary(self) -> Dict:
        """
        Get summary of collected metrics.

        Returns:
            Dictionary with aggregated metrics
        """
        avg_latency = (
            sum(self.operation_times) / len(self.operation_times)
            if self.operation_times else 0
        )

        return {
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "total_queries": self.total_queries,
            "total_documents": self.total_documents,
            "total_chunks": self.total_chunks,
            "average_latency": round(avg_latency, 2),
            "cost_per_query": (
                round(self.total_cost / self.total_queries, 4)
                if self.total_queries > 0 else 0
            )
        }


# Global metrics collector instance
global_metrics = MetricsCollector()
