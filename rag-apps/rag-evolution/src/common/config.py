"""
Configuration management for RAG Evolution
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4")
    VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o")

    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        "./data/chroma_multimodal"
    )

    # Chunking Configuration
    MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "5"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    SEMANTIC_THRESHOLD = float(os.getenv("SEMANTIC_THRESHOLD", "0.7"))

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
    IMAGES_DIR = DATA_DIR / "images"
    CHROMA_DIR = DATA_DIR / "chroma_multimodal"

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment variables")

        # Create directories if they don't exist
        for dir_path in [cls.DATA_DIR, cls.SAMPLE_DOCS_DIR, cls.IMAGES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

        return True


# Validate on import
Config.validate()
