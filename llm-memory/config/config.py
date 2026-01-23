import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Configuration
DEFAULT_MODEL = "claude-3-5-haiku-20241022"  # Fast and cost-effective for learning
AVAILABLE_MODELS = {
    "haiku": "claude-3-5-haiku-20241022",
    "sonnet": "claude-3-5-sonnet-20241022",
    "opus": "claude-opus-4-5-20251101"
}

# Memory Configuration
MAX_CONVERSATION_HISTORY = 10
CHUNK_SIZE = 500
TOP_K_RETRIEVAL = 3
SIMILARITY_THRESHOLD = 0.7

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
CHROMA_COLLECTION_NAME = "knowledge_base"

# UI Configuration
PAGE_TITLE = "LLM Memory Learning Platform"
PAGE_ICON = "🧠"
