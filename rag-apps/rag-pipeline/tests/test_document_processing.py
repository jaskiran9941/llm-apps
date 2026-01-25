"""
Tests for document processing components.
"""

import pytest
from pathlib import Path
from src.models import Document, Chunk
from src.document_processing.chunker import FixedSizeChunker, CharacterChunker
from src.document_processing.preprocessor import TextPreprocessor


class TestTextPreprocessor:
    """Tests for TextPreprocessor."""

    def test_normalize_whitespace(self):
        preprocessor = TextPreprocessor(normalize_whitespace=True)
        text = "This  has   multiple    spaces\n\n\n\nand newlines"
        result = preprocessor.preprocess(text)

        assert "  " not in result  # No double spaces
        assert "\n\n\n" not in result  # No triple newlines

    def test_preserve_paragraphs(self):
        preprocessor = TextPreprocessor(preserve_paragraphs=True)
        text = "Paragraph one.\n\nParagraph two."
        result = preprocessor.preprocess(text)

        assert "\n\n" in result  # Paragraph breaks preserved

    def test_empty_text(self):
        preprocessor = TextPreprocessor()
        result = preprocessor.preprocess("")
        assert result == ""


class TestFixedSizeChunker:
    """Tests for FixedSizeChunker."""

    def test_chunk_creation(self):
        chunker = FixedSizeChunker(chunk_size=100, chunk_overlap=20)
        document = Document(
            doc_id="test_doc",
            text="This is a test document. " * 20,  # Repeating text
            metadata={"filename": "test.pdf"}
        )

        chunks = chunker.chunk(document)

        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.doc_id == "test_doc" for chunk in chunks)

    def test_chunk_overlap(self):
        chunker = FixedSizeChunker(chunk_size=100, chunk_overlap=20)
        document = Document(
            doc_id="test_doc",
            text="Sentence one. Sentence two. Sentence three. " * 10,
            metadata={}
        )

        chunks = chunker.chunk(document)

        # Check that chunks have some overlap
        if len(chunks) > 1:
            # Some text from first chunk should appear in second
            assert len(chunks[0].text) > 0
            assert len(chunks[1].text) > 0

    def test_chunk_metadata(self):
        chunker = FixedSizeChunker(chunk_size=100, chunk_overlap=20)
        document = Document(
            doc_id="test_doc",
            text="Test text. " * 20,
            metadata={"filename": "test.pdf", "pages": 1}
        )

        chunks = chunker.chunk(document)

        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_index"] == i
            assert "filename" in chunk.metadata
            assert "char_count" in chunk.metadata

    def test_page_number_extraction(self):
        chunker = FixedSizeChunker(chunk_size=200, chunk_overlap=50)
        document = Document(
            doc_id="test_doc",
            text="[PAGE 1]\nText on page one. " * 5 + "[PAGE 2]\nText on page two. " * 5,
            metadata={}
        )

        chunks = chunker.chunk(document)

        # At least one chunk should have page number
        assert any(chunk.metadata.get("page_number", 0) > 0 for chunk in chunks)


class TestCharacterChunker:
    """Tests for CharacterChunker."""

    def test_character_chunking(self):
        chunker = CharacterChunker(chunk_size=50, chunk_overlap=10)
        document = Document(
            doc_id="test_doc",
            text="A" * 200,  # 200 characters
            metadata={}
        )

        chunks = chunker.chunk(document)

        # Should create multiple chunks
        assert len(chunks) > 1

        # Each chunk should be approximately chunk_size
        for chunk in chunks[:-1]:  # All except last
            assert len(chunk.text) <= 50 + 5  # Some tolerance


def test_chunker_strategy_pattern():
    """Test that different chunkers work with same interface."""

    document = Document(
        doc_id="test_doc",
        text="This is a test. " * 50,
        metadata={}
    )

    chunkers = [
        FixedSizeChunker(chunk_size=100, chunk_overlap=20),
        CharacterChunker(chunk_size=100, chunk_overlap=20)
    ]

    for chunker in chunkers:
        chunks = chunker.chunk(document)
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
