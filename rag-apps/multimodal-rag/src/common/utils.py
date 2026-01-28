"""
Utility functions for multimodal RAG system.
"""

import tiktoken
from typing import List, Dict, Any
from pathlib import Path
import hashlib
from datetime import datetime


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string.

    Args:
        text: Text to count tokens for
        model: Model name for tokenizer

    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def estimate_cost(
    embedding_tokens: int = 0,
    gpt4_input_tokens: int = 0,
    gpt4_output_tokens: int = 0,
    whisper_minutes: float = 0.0,
    num_images: int = 0
) -> float:
    """
    Estimate the cost of API calls.

    Args:
        embedding_tokens: Number of tokens for embeddings
        gpt4_input_tokens: Number of input tokens for GPT-4
        gpt4_output_tokens: Number of output tokens for GPT-4
        whisper_minutes: Minutes of audio to transcribe
        num_images: Number of images to process with GPT-4V

    Returns:
        Total estimated cost in USD
    """
    from .config import Config

    cost = 0.0

    # Embedding cost
    cost += (embedding_tokens / 1000) * Config.COST_EMBEDDING

    # GPT-4 cost
    cost += (gpt4_input_tokens / 1000) * Config.COST_GPT4_INPUT
    cost += (gpt4_output_tokens / 1000) * Config.COST_GPT4_OUTPUT

    # Whisper cost
    cost += whisper_minutes * Config.COST_WHISPER_PER_MINUTE

    # GPT-4V cost (approximately $0.02 per image)
    cost += num_images * 0.02

    return cost


def format_cost(cost: float) -> str:
    """
    Format cost for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1.0:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"


def format_time(seconds: float) -> str:
    """
    Format time duration for display.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp for audio playback.

    Args:
        seconds: Timestamp in seconds

    Returns:
        Formatted timestamp (MM:SS or HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def generate_id(content: str, prefix: str = "") -> str:
    """
    Generate a unique ID based on content.

    Args:
        content: Content to hash
        prefix: Prefix for the ID

    Returns:
        Unique ID string
    """
    hash_object = hashlib.md5(content.encode())
    hash_hex = hash_object.hexdigest()[:12]

    if prefix:
        return f"{prefix}_{hash_hex}"
    return hash_hex


def validate_file_size(file_path: Path, max_size_mb: float) -> bool:
    """
    Validate that a file is under the maximum size.

    Args:
        file_path: Path to file
        max_size_mb: Maximum size in megabytes

    Returns:
        True if file is valid size, False otherwise
    """
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    return file_size_mb <= max_size_mb


def get_file_extension(file_path: Path) -> str:
    """
    Get the file extension (lowercase, without dot).

    Args:
        file_path: Path to file

    Returns:
        File extension
    """
    return file_path.suffix.lower().lstrip('.')


def serialize_dataframe_to_markdown(df, max_rows: int = None) -> str:
    """
    Serialize a pandas DataFrame to markdown format.

    Args:
        df: Pandas DataFrame
        max_rows: Maximum number of rows to include

    Returns:
        Markdown formatted table
    """
    if max_rows:
        df = df.head(max_rows)

    return df.to_markdown(index=False)


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def merge_metadata(*metadata_dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple metadata dictionaries.

    Args:
        *metadata_dicts: Variable number of metadata dictionaries

    Returns:
        Merged metadata dictionary
    """
    merged = {}
    for metadata in metadata_dicts:
        if metadata:
            merged.update(metadata)
    return merged
