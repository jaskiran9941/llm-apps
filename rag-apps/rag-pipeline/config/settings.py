"""
Centralized configuration for the RAG system.

All configurable parameters are defined here, making it easy to adjust
system behavior without modifying code. Values can be overridden via
environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Configuration settings for the RAG system.

    This class centralizes all configuration parameters, with sensible defaults
    that can be overridden via environment variables. This makes the system
    flexible for different use cases and deployment environments.
    """

    # ==================== OpenAI Configuration ====================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small"
    )

    # ==================== Cost Constants (USD) ====================
    # These values may change - update based on OpenAI's current pricing
    GPT4_INPUT_COST_PER_1K: float = float(
        os.getenv("GPT4_INPUT_COST_PER_1K", "0.03")
    )
    GPT4_OUTPUT_COST_PER_1K: float = float(
        os.getenv("GPT4_OUTPUT_COST_PER_1K", "0.06")
    )
    EMBEDDING_COST_PER_1K: float = float(
        os.getenv("EMBEDDING_COST_PER_1K", "0.0001")
    )

    # ==================== Chunking Configuration ====================
    # Trade-off: Smaller chunks = more precise retrieval but more chunks to embed
    # Larger chunks = more context per chunk but less precise matching
    DEFAULT_CHUNK_SIZE: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "500"))

    # Overlap helps maintain context across chunk boundaries
    # Trade-off: More overlap = better context continuity but higher costs
    DEFAULT_CHUNK_OVERLAP: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "50"))

    # ==================== Retrieval Configuration ====================
    # Number of chunks to retrieve for context
    # Trade-off: More chunks = more context but higher cost and potential noise
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))

    # Minimum similarity score for retrieval (0-1)
    # Lower threshold = more results but potentially less relevant
    MIN_SIMILARITY_SCORE: float = 0.5

    # ==================== Generation Configuration ====================
    # Temperature controls randomness in LLM responses
    # 0 = deterministic, 1 = more creative/random
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))

    # Maximum tokens in LLM response
    MAX_OUTPUT_TOKENS: int = 1000

    # ==================== Storage Paths ====================
    # Base directory for all data
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    CHROMA_DB_DIR: Path = DATA_DIR / "chroma_db"
    CACHE_DIR: Path = DATA_DIR / "cache"

    # ==================== Vector Store Configuration ====================
    # ChromaDB collection name
    CHROMA_COLLECTION_NAME: str = "rag_documents"

    # Distance metric for similarity search
    # Options: "cosine" (default), "l2", "ip" (inner product)
    SIMILARITY_METRIC: str = "cosine"

    # ==================== Processing Limits ====================
    # Maximum file size for upload (in bytes)
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB

    # Allowed file extensions
    ALLOWED_EXTENSIONS: set = {".pdf"}

    # Batch size for embedding generation (to avoid rate limits)
    EMBEDDING_BATCH_SIZE: int = 100

    # ==================== Logging Configuration ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ==================== UI Configuration ====================
    # Streamlit page configuration
    PAGE_TITLE: str = "RAG Learning System"
    PAGE_ICON: str = "📚"
    LAYOUT: str = "wide"

    @classmethod
    def validate(cls) -> bool:
        """
        Validate critical configuration settings.

        Returns:
            bool: True if configuration is valid, raises ValueError otherwise
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not set. Please add it to your .env file."
            )

        if cls.DEFAULT_CHUNK_SIZE < 100:
            raise ValueError("CHUNK_SIZE must be at least 100 characters")

        if cls.DEFAULT_CHUNK_OVERLAP >= cls.DEFAULT_CHUNK_SIZE:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")

        if cls.DEFAULT_TOP_K < 1:
            raise ValueError("TOP_K must be at least 1")

        return True

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [
            cls.DATA_DIR,
            cls.UPLOADS_DIR,
            cls.CHROMA_DB_DIR,
            cls.CACHE_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Create a singleton instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()
