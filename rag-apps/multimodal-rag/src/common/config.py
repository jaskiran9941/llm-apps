"""
Configuration settings for multimodal RAG system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings."""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    UPLOADS_DIR = DATA_DIR / "uploads"
    IMAGES_DIR = DATA_DIR / "images"
    TABLES_DIR = DATA_DIR / "tables"
    AUDIO_DIR = DATA_DIR / "audio"
    TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
    CHROMA_DIR = DATA_DIR / "chroma_multimodal"
    SAMPLE_DOCS_DIR = PROJECT_ROOT / "sample_docs"

    # Model Settings
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-4o"
    VISION_MODEL = "gpt-4o"
    WHISPER_MODEL = "whisper-1"

    # Embedding Settings
    EMBEDDING_DIMENSION = 1536

    # Text Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Table Processing
    MAX_TABLE_ROWS_PER_CHUNK = 50
    TABLE_CHUNK_OVERLAP = 5
    TABLE_PREVIEW_ROWS = 5

    # Audio Processing
    MAX_AUDIO_FILE_SIZE_MB = 25
    AUDIO_CHUNK_DURATION_SECONDS = 600  # 10 minutes
    AUDIO_SEGMENT_DURATION_SECONDS = 60  # 1 minute for embedding

    # Retrieval Settings
    DEFAULT_K = 10
    DEFAULT_TEXT_WEIGHT = 0.3
    DEFAULT_IMAGE_WEIGHT = 0.2
    DEFAULT_TABLE_WEIGHT = 0.3
    DEFAULT_AUDIO_WEIGHT = 0.2

    # Cost Settings (per 1K tokens)
    COST_EMBEDDING = 0.00002
    COST_GPT4_INPUT = 0.0025  # gpt-4o
    COST_GPT4_OUTPUT = 0.01   # gpt-4o
    COST_WHISPER_PER_MINUTE = 0.006

    # ChromaDB Settings
    COLLECTION_NAME = "multimodal_rag"

    # UI Settings
    MAX_DISPLAY_RESULTS = 5

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        for dir_path in [
            cls.DATA_DIR,
            cls.UPLOADS_DIR,
            cls.IMAGES_DIR,
            cls.TABLES_DIR,
            cls.AUDIO_DIR,
            cls.TRANSCRIPTS_DIR,
            cls.CHROMA_DIR,
            cls.SAMPLE_DOCS_DIR,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Ensure directories exist on import
Config.ensure_directories()
