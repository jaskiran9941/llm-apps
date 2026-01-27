"""
OpenAI text embeddings
"""
from typing import List
import openai
from ..utils.config import Config


class TextEmbedder:
    """Generate embeddings using OpenAI's text-embedding-3-small"""

    def __init__(self, model: str = None):
        self.model = model or Config.EMBEDDING_MODEL
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding text: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error embedding batch: {e}")
            return []

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension for the model"""
        return 1536
