"""
Basic tests for RAG Evolution components
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.common.utils import generate_id, calculate_cosine_similarity, clean_text
from src.baseline_rag.simple_chunker import SimpleChunker
from src.advanced_chunking.sentence_chunker import SentenceChunker


class TestUtils:
    """Test utility functions"""

    def test_generate_id(self):
        """Test ID generation"""
        text = "This is a test"
        id1 = generate_id(text)
        id2 = generate_id(text)

        # Same text should generate same ID
        assert id1 == id2

        # Different text should generate different ID
        id3 = generate_id("Different text")
        assert id1 != id3

        # ID should be 16 characters
        assert len(id1) == 16

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        # Same vectors should have similarity 1.0
        sim1 = calculate_cosine_similarity(vec1, vec2)
        assert abs(sim1 - 1.0) < 0.01

        # Orthogonal vectors should have similarity 0.0
        sim2 = calculate_cosine_similarity(vec1, vec3)
        assert abs(sim2 - 0.0) < 0.01

    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "This   has\n\nexcessive    whitespace"
        cleaned = clean_text(dirty_text)

        assert "  " not in cleaned  # No double spaces
        assert cleaned == "This has excessive whitespace"


class TestSimpleChunker:
    """Test simple chunker"""

    def test_basic_chunking(self):
        """Test basic chunking"""
        text = "A" * 1000  # 1000 characters
        chunker = SimpleChunker(chunk_size=500, chunk_overlap=50)

        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert all(len(chunk.content) <= 550 for chunk in chunks)  # Allow some tolerance

    def test_chunk_metadata(self):
        """Test chunk metadata"""
        text = "This is a complete sentence."
        chunker = SimpleChunker(chunk_size=500)

        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0].metadata['chunking_strategy'] == 'fixed'
        assert 'is_complete' in chunks[0].metadata

    def test_analyze_chunks(self):
        """Test chunk analysis"""
        text = "First sentence. Second sentence. Third sentence."
        chunker = SimpleChunker(chunk_size=20)  # Small chunks

        chunks = chunker.chunk(text)
        stats = chunker.analyze_chunks(chunks)

        assert 'total_chunks' in stats
        assert stats['total_chunks'] == len(chunks)
        assert 'completeness_rate' in stats


class TestSentenceChunker:
    """Test sentence-aware chunker"""

    def test_sentence_boundaries(self):
        """Test that chunks respect sentence boundaries"""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunker = SentenceChunker(chunk_size=30)

        chunks = chunker.chunk(text)

        # All chunks should be complete sentences
        for chunk in chunks:
            assert chunk.metadata['is_complete'] is True

    def test_completeness_rate(self):
        """Test that sentence chunker has 100% completeness"""
        text = "A" * 500 + ". " + "B" * 500 + "."
        chunker = SentenceChunker(chunk_size=400)

        chunks = chunker.chunk(text)
        stats = chunker.analyze_chunks(chunks)

        assert stats['completeness_rate'] == 1.0
        assert stats['incomplete_chunks'] == 0


def test_imports():
    """Test that all modules can be imported"""
    # This will fail if there are import errors
    from src.baseline_rag import simple_chunker, text_embedder, vector_search, generator
    from src.advanced_chunking import sentence_chunker, semantic_chunker, preprocessors
    from src.hybrid_retrieval import bm25_searcher, hybrid_fusion, reranker, query_enhancer
    from src.vision_rag import (
        image_extractor,
        vision_embedder,
        multimodal_store,
        multimodal_retriever,
        vision_generator
    )
    from src.common import models, config, utils

    assert True  # If we get here, imports worked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
