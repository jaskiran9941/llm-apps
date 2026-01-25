"""
Input validation utilities.

Validates user inputs, file uploads, and configuration parameters
to ensure system stability and security.
"""

import os
from pathlib import Path
from typing import Optional, List
from config.settings import settings


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_file_upload(file_path: Path) -> bool:
    """
    Validate uploaded file.

    Checks:
    1. File exists
    2. File extension is allowed
    3. File size is within limits

    Args:
        file_path: Path to uploaded file

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    # Check existence
    if not file_path.exists():
        raise ValidationError(f"File not found: {file_path}")

    # Check extension
    if file_path.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Check file size
    file_size = file_path.stat().st_size
    if file_size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        file_mb = file_size / (1024 * 1024)
        raise ValidationError(
            f"File too large: {file_mb:.1f}MB (max: {max_mb:.1f}MB)"
        )

    # Check file is readable
    if not os.access(file_path, os.R_OK):
        raise ValidationError(f"File not readable: {file_path}")

    return True


def validate_chunk_config(chunk_size: int, chunk_overlap: int) -> bool:
    """
    Validate chunking configuration.

    Args:
        chunk_size: Chunk size in characters
        chunk_overlap: Overlap between chunks in characters

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if chunk_size < 100:
        raise ValidationError(
            "Chunk size too small. Minimum 100 characters required."
        )

    if chunk_size > 5000:
        raise ValidationError(
            "Chunk size too large. Maximum 5000 characters recommended."
        )

    if chunk_overlap < 0:
        raise ValidationError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValidationError(
            "Chunk overlap must be less than chunk size."
        )

    # Warn if overlap is too large (>50% of chunk size)
    if chunk_overlap > chunk_size * 0.5:
        # This is a warning, not an error
        print(
            f"Warning: Large overlap ({chunk_overlap} chars, "
            f"{chunk_overlap/chunk_size*100:.0f}% of chunk size) "
            f"may increase costs significantly."
        )

    return True


def validate_retrieval_config(top_k: int) -> bool:
    """
    Validate retrieval configuration.

    Args:
        top_k: Number of chunks to retrieve

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if top_k < 1:
        raise ValidationError("top_k must be at least 1")

    if top_k > 50:
        raise ValidationError(
            "top_k too large. Maximum 50 chunks recommended. "
            "Large values increase cost and may add noise."
        )

    return True


def validate_query(query: str) -> bool:
    """
    Validate user query.

    Args:
        query: User's question

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if not query or not query.strip():
        raise ValidationError("Query cannot be empty")

    if len(query) > 1000:
        raise ValidationError(
            "Query too long. Please keep queries under 1000 characters."
        )

    return True


def validate_temperature(temperature: float) -> bool:
    """
    Validate LLM temperature parameter.

    Args:
        temperature: Temperature value (0-2)

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if temperature < 0 or temperature > 2:
        raise ValidationError(
            "Temperature must be between 0 and 2. "
            "0 = deterministic, 1 = balanced, 2 = very creative"
        )

    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem operations
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove or replace dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Ensure filename isn't empty after sanitization
    if not filename or filename == '_':
        filename = 'unnamed_file'

    return filename


def validate_document_id(doc_id: str) -> bool:
    """
    Validate document ID format.

    Args:
        doc_id: Document identifier

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if not doc_id or not doc_id.strip():
        raise ValidationError("Document ID cannot be empty")

    # Check for dangerous characters
    if any(char in doc_id for char in ['/', '\\', '\x00', '..']):
        raise ValidationError("Document ID contains invalid characters")

    return True
