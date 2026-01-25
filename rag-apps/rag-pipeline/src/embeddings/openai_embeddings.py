"""
OpenAI embeddings implementation.

Uses OpenAI's text-embedding-3-small model for generating embeddings.
Includes batching, retry logic, and cost tracking.
"""

import time
from typing import List
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from src.embeddings.embedding_manager import BaseEmbeddingManager
from src.utils.logger import EducationalLogger
from src.utils.metrics import count_tokens, calculate_embedding_cost
from config.settings import settings

logger = EducationalLogger(__name__)


class OpenAIEmbeddingManager(BaseEmbeddingManager):
    """
    Generate embeddings using OpenAI's API.

    Features:
    - Automatic batching for efficiency
    - Retry logic for rate limits
    - Cost tracking
    - Optional caching

    Educational Note:
    ----------------
    text-embedding-3-small is chosen because:
    - Good quality for most RAG use cases
    - Low cost ($0.0001 per 1K tokens)
    - 1536 dimensions (good balance)
    - Fast inference

    For higher quality (at higher cost), you could use text-embedding-3-large.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        batch_size: int = None
    ):
        """
        Initialize OpenAI embedding manager.

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Embedding model name (defaults to settings)
            batch_size: Maximum texts per batch (defaults to settings)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        self.batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Cache for embeddings (optional - to avoid re-embedding same text)
        self.cache = {}

        # Track costs
        self.total_tokens = 0
        self.total_cost = 0.0

        logger.log_step(
            "EMBEDDING_INIT",
            f"Model: {self.model}, Batch size: {self.batch_size}",
            "Using OpenAI embeddings for semantic search"
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Uses caching to avoid re-embedding identical texts.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache
        if text in self.cache:
            logger.debug(f"Cache hit for text: {text[:50]}...")
            return self.cache[text]

        # Generate embedding
        embedding = self._generate_embedding(text)

        # Cache result
        self.cache[text] = embedding

        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Processes in batches to respect API limits and improve efficiency.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        logger.log_step(
            "BATCH_EMBEDDING",
            f"Embedding {len(texts)} texts",
            f"Processing in batches of {self.batch_size} for efficiency"
        )

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = self._generate_embeddings_batch(batch)
            all_embeddings.extend(batch_embeddings)

            # Log progress
            logger.debug(
                f"Processed {min(i + self.batch_size, len(texts))}/{len(texts)} texts"
            )

        logger.log_metric(
            "Embeddings generated",
            len(all_embeddings),
            f"Total cost: ${self.total_cost:.4f}"
        )

        return all_embeddings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding with retry logic.

        The @retry decorator automatically retries on failure:
        - Up to 3 attempts
        - Exponential backoff (wait 2s, 4s, 8s)
        - Handles rate limits gracefully

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )

            embedding = response.data[0].embedding

            # Track costs
            tokens = count_tokens(text, model=self.model)
            cost = calculate_embedding_cost(tokens)
            self.total_tokens += tokens
            self.total_cost += cost

            return embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch with retry logic.

        Args:
            texts: Batch of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )

            embeddings = [item.embedding for item in response.data]

            # Track costs
            total_tokens = sum(count_tokens(text, model=self.model) for text in texts)
            cost = calculate_embedding_cost(total_tokens)
            self.total_tokens += total_tokens
            self.total_cost += cost

            logger.debug(
                f"Batch: {len(texts)} texts, {total_tokens} tokens, ${cost:.4f}"
            )

            return embeddings

        except Exception as e:
            logger.error(f"Batch embedding generation failed: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension for the current model.

        Returns:
            Embedding dimension (1536 for text-embedding-3-small)
        """
        # text-embedding-3-small has 1536 dimensions
        # text-embedding-3-large has 3072 dimensions
        if "large" in self.model:
            return 3072
        else:
            return 1536

    def get_cost_summary(self) -> dict:
        """
        Get summary of embedding costs.

        Returns:
            Dictionary with cost metrics
        """
        return {
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "model": self.model,
            "cache_size": len(self.cache)
        }

    def clear_cache(self):
        """Clear embedding cache."""
        self.cache.clear()
        logger.info("Embedding cache cleared")
