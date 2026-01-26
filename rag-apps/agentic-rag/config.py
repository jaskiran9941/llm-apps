"""Configuration for the Agentic RAG system."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", None)

# Agent Configuration
MAX_ITERATIONS = 3  # Maximum retrieval attempts before giving up
EVALUATION_THRESHOLD = 7  # Out of 10 - minimum score to accept results
MAX_DOCS_PER_RETRIEVAL = 5  # Number of documents to retrieve per search

# Model Configuration
LLM_MODEL = "gpt-4o-mini"  # Reasoning model
EMBEDDING_MODEL = "text-embedding-3-small"  # Embedding model
TEMPERATURE = 0.7  # Higher = more creative, lower = more focused

# Vector Database
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "research_documents"

# Document Processing
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# Paths
DOCUMENTS_DIR = "./documents"
