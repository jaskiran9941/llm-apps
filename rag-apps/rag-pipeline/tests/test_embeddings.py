"""
Tests for embedding components.

Note: These tests mock OpenAI API calls to avoid costs.
"""

import pytest
from unittest.mock import Mock, patch
from src.embeddings.openai_embeddings import OpenAIEmbeddingManager
from src.models import Chunk


class TestOpenAIEmbeddingManager:
    """Tests for OpenAI embedding manager."""

    @patch('src.embeddings.openai_embeddings.OpenAI')
    def test_embed_text(self, mock_openai):
        """Test embedding a single text."""

        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create manager
        manager = OpenAIEmbeddingManager(api_key="test_key")

        # Test embedding
        text = "Test text for embedding"
        embedding = manager.embed_text(text)

        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

    @patch('src.embeddings.openai_embeddings.OpenAI')
    def test_embed_batch(self, mock_openai):
        """Test embedding multiple texts."""

        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536),
            Mock(embedding=[0.3] * 1536)
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create manager
        manager = OpenAIEmbeddingManager(api_key="test_key")

        # Test batch embedding
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = manager.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 1536 for emb in embeddings)

    @patch('src.embeddings.openai_embeddings.OpenAI')
    def test_caching(self, mock_openai):
        """Test that embeddings are cached."""

        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create manager
        manager = OpenAIEmbeddingManager(api_key="test_key")

        # Embed same text twice
        text = "Test text"
        emb1 = manager.embed_text(text)
        emb2 = manager.embed_text(text)

        # Should be same (cached)
        assert emb1 == emb2

        # API should only be called once
        assert mock_client.embeddings.create.call_count == 1

    def test_get_embedding_dimension(self):
        """Test getting embedding dimension."""

        manager = OpenAIEmbeddingManager(
            api_key="test_key",
            model="text-embedding-3-small"
        )

        assert manager.get_embedding_dimension() == 1536

    @patch('src.embeddings.openai_embeddings.OpenAI')
    def test_embed_chunks(self, mock_openai):
        """Test embedding chunk objects."""

        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536)
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Create manager
        manager = OpenAIEmbeddingManager(api_key="test_key")

        # Create chunks
        chunks = [
            Chunk(chunk_id="c1", doc_id="d1", text="Text 1", metadata={}),
            Chunk(chunk_id="c2", doc_id="d1", text="Text 2", metadata={})
        ]

        # Embed chunks
        embeddings = manager.embed_chunks(chunks)

        assert len(embeddings) == 2
        assert all(len(emb) == 1536 for emb in embeddings)
