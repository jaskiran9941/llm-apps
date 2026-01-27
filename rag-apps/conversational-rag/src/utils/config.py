"""
Configuration management
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4")

    # Chunking
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Retrieval
    TOP_K = int(os.getenv("TOP_K", "5"))

    # Vector DB
    CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "../../data/chroma_conversational")

    # Documents
    DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "../../data/documents")

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        return True
