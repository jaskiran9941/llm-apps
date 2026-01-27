"""
Utility functions for RAG Evolution
"""
import hashlib
import time
from typing import List, Any
from functools import wraps
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def generate_id(content: str) -> str:
    """Generate unique ID from content"""
    return hashlib.md5(content.encode()).hexdigest()[:16]


def time_it(func):
    """Decorator to measure execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1).reshape(1, -1)
    vec2 = np.array(vec2).reshape(1, -1)
    return float(cosine_similarity(vec1, vec2)[0][0])


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_context(chunks: List[str], max_chunks: int = 5) -> str:
    """Format retrieved chunks into context for generation"""
    context_parts = []
    for i, chunk in enumerate(chunks[:max_chunks], 1):
        context_parts.append(f"[Context {i}]\n{chunk}\n")
    return "\n".join(context_parts)


def calculate_metrics(
    query: str,
    retrieved_chunks: List[Any],
    expected_chunks: List[str] = None
) -> dict:
    """Calculate retrieval metrics"""
    metrics = {
        "num_retrieved": len(retrieved_chunks),
        "avg_score": 0.0,
        "has_images": False
    }

    if retrieved_chunks:
        scores = [chunk.score for chunk in retrieved_chunks if hasattr(chunk, 'score')]
        if scores:
            metrics["avg_score"] = sum(scores) / len(scores)

        # Check for images
        metrics["has_images"] = any(
            getattr(chunk, 'result_type', 'text') == 'image'
            for chunk in retrieved_chunks
        )

    # Calculate accuracy if expected chunks provided
    if expected_chunks:
        retrieved_content = {chunk.content for chunk in retrieved_chunks}
        expected_set = set(expected_chunks)
        matches = retrieved_content.intersection(expected_set)
        metrics["accuracy"] = len(matches) / len(expected_set) if expected_set else 0.0

    return metrics


def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove excessive whitespace
    text = " ".join(text.split())

    # Remove common PDF artifacts
    text = text.replace("\x00", "")
    text = text.replace("\ufffd", "")

    return text.strip()


def estimate_cost(
    num_embeddings: int = 0,
    num_tokens_generated: int = 0,
    num_vision_calls: int = 0
) -> float:
    """Estimate OpenAI API cost"""
    # Approximate costs (as of 2024)
    EMBEDDING_COST_PER_1K = 0.00002  # text-embedding-3-small
    GPT4_COST_PER_1K = 0.03  # gpt-4 output
    VISION_COST_PER_IMAGE = 0.02  # gpt-4-vision-preview

    embedding_cost = (num_embeddings / 1000) * EMBEDDING_COST_PER_1K
    generation_cost = (num_tokens_generated / 1000) * GPT4_COST_PER_1K
    vision_cost = num_vision_calls * VISION_COST_PER_IMAGE

    return embedding_cost + generation_cost + vision_cost
