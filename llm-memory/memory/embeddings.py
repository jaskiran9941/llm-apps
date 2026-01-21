"""
Multi-provider embedding support
Supports: HuggingFace, OpenAI, Cohere, Voyage, FastEmbed
"""

import numpy as np
from typing import List, Union
import os


class EmbeddingProvider:
    """Abstract base for embedding providers."""

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Embed text(s) and return numpy array."""
        raise NotImplementedError


class HuggingFaceEmbeddings(EmbeddingProvider):
    """HuggingFace sentence-transformers embeddings (Local, Free)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.dimension = 384

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts)


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embeddings (API, Paid)."""

    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.dimension = 1536 if "large" in model else 512

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)


class CohereEmbeddings(EmbeddingProvider):
    """Cohere embeddings (API, Paid)."""

    def __init__(self, api_key: str = None, model: str = "embed-english-v3.0"):
        import cohere
        self.client = cohere.Client(api_key=api_key or os.getenv("COHERE_API_KEY"))
        self.model = model
        self.dimension = 1024

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"
        )

        return np.array(response.embeddings)


class VoyageEmbeddings(EmbeddingProvider):
    """Voyage AI embeddings (API, Paid - Best for RAG)."""

    def __init__(self, api_key: str = None, model: str = "voyage-2"):
        import voyageai
        self.client = voyageai.Client(api_key=api_key or os.getenv("VOYAGE_API_KEY"))
        self.model = model
        self.dimension = 1024

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        result = self.client.embed(
            texts=texts,
            model=self.model
        )

        return np.array(result.embeddings)


class FastEmbeddings(EmbeddingProvider):
    """FastEmbed embeddings (Local, Free, Fast)."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding
        self.model = TextEmbedding(model_name=model_name)
        self.dimension = 384

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        embeddings = list(self.model.embed(texts))
        return np.array(embeddings)


class OllamaEmbeddings(EmbeddingProvider):
    """Ollama embeddings (Local, Free)."""

    def __init__(self, model: str = "nomic-embed-text"):
        import ollama
        self.client = ollama
        self.model = model
        self.dimension = 768

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        embeddings = []
        for text in texts:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            embeddings.append(response['embedding'])

        return np.array(embeddings)


# Factory function
def get_embedding_provider(provider: str = "huggingface", **kwargs) -> EmbeddingProvider:
    """
    Get an embedding provider.

    Args:
        provider: One of ["huggingface", "openai", "cohere", "voyage", "fastembed", "ollama"]
        **kwargs: Provider-specific arguments (api_key, model, etc.)

    Returns:
        EmbeddingProvider instance
    """
    providers = {
        "huggingface": HuggingFaceEmbeddings,
        "openai": OpenAIEmbeddings,
        "cohere": CohereEmbeddings,
        "voyage": VoyageEmbeddings,
        "fastembed": FastEmbeddings,
        "ollama": OllamaEmbeddings
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from {list(providers.keys())}")

    return providers[provider](**kwargs)


# Comparison info
PROVIDER_INFO = {
    "huggingface": {
        "name": "HuggingFace (sentence-transformers)",
        "type": "Local",
        "cost": "Free",
        "speed": "Medium",
        "quality": "Good",
        "requires": "pip install sentence-transformers",
        "pros": ["Free", "Local", "No API needed", "Private"],
        "cons": ["Slower than FastEmbed", "Larger memory usage"]
    },
    "openai": {
        "name": "OpenAI Embeddings",
        "type": "API",
        "cost": "$0.02/1M tokens",
        "speed": "Fast",
        "quality": "Excellent",
        "requires": "pip install openai",
        "pros": ["High quality", "Well-optimized", "Good docs"],
        "cons": ["Costs money", "API dependency", "Data sent to OpenAI"]
    },
    "cohere": {
        "name": "Cohere Embeddings",
        "type": "API",
        "cost": "$0.10/1M tokens",
        "speed": "Fast",
        "quality": "Excellent",
        "requires": "pip install cohere",
        "pros": ["Great for search", "Multilingual", "Good support"],
        "cons": ["Costs money", "API dependency"]
    },
    "voyage": {
        "name": "Voyage AI",
        "type": "API",
        "cost": "$0.13/1M tokens",
        "speed": "Fast",
        "quality": "Best for RAG",
        "requires": "pip install voyageai",
        "pros": ["Optimized for RAG", "Best retrieval quality"],
        "cons": ["Most expensive", "Newer service"]
    },
    "fastembed": {
        "name": "FastEmbed",
        "type": "Local",
        "cost": "Free",
        "speed": "Very Fast",
        "quality": "Good",
        "requires": "pip install fastembed",
        "pros": ["Fastest local option", "Low memory", "Free"],
        "cons": ["Slightly lower quality than HuggingFace"]
    },
    "ollama": {
        "name": "Ollama",
        "type": "Local",
        "cost": "Free",
        "speed": "Fast",
        "quality": "Very Good",
        "requires": "ollama installed + ollama pull nomic-embed-text",
        "pros": ["Completely local", "Free", "Good quality"],
        "cons": ["Requires Ollama setup", "Larger disk usage"]
    }
}
