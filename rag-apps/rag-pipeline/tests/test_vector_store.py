"""
Tests for vector store components.
"""

import pytest
import tempfile
from pathlib import Path
from src.vector_store.chroma_store import ChromaVectorStore
from src.models import Chunk


@pytest.fixture
def temp_chroma_dir():
    """Create temporary directory for ChromaDB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestChromaVectorStore:
    """Tests for ChromaDB vector store."""

    def test_initialization(self, temp_chroma_dir):
        """Test vector store initialization."""
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )

        assert store.collection_name == "test_collection"
        assert store.collection is not None

    def test_add_and_search(self, temp_chroma_dir):
        """Test adding documents and searching."""
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )

        # Create test chunks
        chunks = [
            Chunk(
                chunk_id="chunk_1",
                doc_id="doc_1",
                text="Python is a programming language",
                metadata={"page_number": 1, "filename": "test.pdf"}
            ),
            Chunk(
                chunk_id="chunk_2",
                doc_id="doc_1",
                text="Machine learning is a subset of AI",
                metadata={"page_number": 2, "filename": "test.pdf"}
            )
        ]

        # Create dummy embeddings
        embeddings = [
            [0.1] * 1536,
            [0.2] * 1536
        ]

        # Add documents
        success = store.add_documents(chunks, embeddings)
        assert success

        # Search
        query_embedding = [0.15] * 1536  # Between the two
        results = store.search(query_embedding, top_k=2)

        assert len(results) <= 2
        assert all(hasattr(r, 'chunk') for r in results)
        assert all(hasattr(r, 'score') for r in results)

    def test_delete_document(self, temp_chroma_dir):
        """Test deleting documents."""
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )

        # Add a chunk
        chunks = [
            Chunk(
                chunk_id="chunk_1",
                doc_id="doc_1",
                text="Test text",
                metadata={}
            )
        ]
        embeddings = [[0.1] * 1536]

        store.add_documents(chunks, embeddings)

        # Delete
        success = store.delete_document("doc_1")
        assert success

        # Verify deletion
        docs = store.list_documents()
        assert len(docs) == 0

    def test_list_documents(self, temp_chroma_dir):
        """Test listing documents."""
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )

        # Add chunks from different documents
        chunks = [
            Chunk(chunk_id="c1", doc_id="doc_1", text="Text 1", metadata={"filename": "file1.pdf"}),
            Chunk(chunk_id="c2", doc_id="doc_1", text="Text 2", metadata={"filename": "file1.pdf"}),
            Chunk(chunk_id="c3", doc_id="doc_2", text="Text 3", metadata={"filename": "file2.pdf"})
        ]
        embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]

        store.add_documents(chunks, embeddings)

        # List documents
        docs = store.list_documents()

        assert len(docs) == 2
        assert any(d['doc_id'] == 'doc_1' for d in docs)
        assert any(d['doc_id'] == 'doc_2' for d in docs)

    def test_get_stats(self, temp_chroma_dir):
        """Test getting statistics."""
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )

        # Add some chunks
        chunks = [
            Chunk(chunk_id=f"c{i}", doc_id="doc_1", text=f"Text {i}", metadata={})
            for i in range(5)
        ]
        embeddings = [[0.1] * 1536] * 5

        store.add_documents(chunks, embeddings)

        # Get stats
        stats = store.get_stats()

        assert stats["total_chunks"] == 5
        assert stats["total_documents"] >= 1
        assert "collection_name" in stats
        assert "distance_function" in stats

    def test_clear(self, temp_chroma_dir):
        """Test clearing all data."""
        store = ChromaVectorStore(
            collection_name="test_collection",
            persist_directory=temp_chroma_dir
        )

        # Add chunks
        chunks = [
            Chunk(chunk_id="c1", doc_id="doc_1", text="Text", metadata={})
        ]
        embeddings = [[0.1] * 1536]

        store.add_documents(chunks, embeddings)

        # Clear
        success = store.clear()
        assert success

        # Verify
        stats = store.get_stats()
        assert stats["total_chunks"] == 0
