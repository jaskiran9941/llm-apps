"""
Logging configuration for the RAG system.

Provides structured logging with educational context to help users
understand what's happening at each step of the pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from config.settings import settings


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level
    log_level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class EducationalLogger:
    """
    Enhanced logger with educational context.

    This logger adds helpful explanations alongside technical log messages
    to help users understand the RAG pipeline.
    """

    def __init__(self, name: str):
        self.logger = setup_logger(name)
        self.educational_mode = True

    def log_step(self, step: str, details: str, explanation: str = ""):
        """
        Log a pipeline step with explanation.

        Args:
            step: Short step name (e.g., "CHUNKING")
            details: Technical details
            explanation: Educational explanation of what's happening
        """
        msg = f"[{step}] {details}"
        if self.educational_mode and explanation:
            msg += f" | Why: {explanation}"
        self.logger.info(msg)

    def log_metric(self, metric_name: str, value: any, context: str = ""):
        """
        Log a metric with context.

        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context about the metric
        """
        msg = f"[METRIC] {metric_name}: {value}"
        if context:
            msg += f" | {context}"
        self.logger.info(msg)

    def info(self, msg: str):
        """Standard info logging."""
        self.logger.info(msg)

    def warning(self, msg: str):
        """Standard warning logging."""
        self.logger.warning(msg)

    def error(self, msg: str):
        """Standard error logging."""
        self.logger.error(msg)

    def debug(self, msg: str):
        """Standard debug logging."""
        self.logger.debug(msg)
