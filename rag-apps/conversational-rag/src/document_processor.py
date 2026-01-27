"""
Document processing with PDF extraction and semantic chunking
"""
from typing import List
import PyPDF2
import uuid
from .models import Chunk


class SemanticChunker:
    """Simple semantic-inspired chunker using sentence boundaries"""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, page: int = 1) -> List[Chunk]:
        """Chunk text into semantic chunks"""
        # Split by sentences (simple approach)
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk_size, save current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(Chunk(
                    content=chunk_text,
                    page=page,
                    chunk_id=str(uuid.uuid4()),
                    metadata={"chunk_size": len(chunk_text)}
                ))

                # Keep overlap sentences
                overlap_text = " ".join(current_chunk)
                while len(overlap_text) > self.overlap and current_chunk:
                    current_chunk.pop(0)
                    overlap_text = " ".join(current_chunk)

                current_length = len(overlap_text)

            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 for space

        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(Chunk(
                content=chunk_text,
                page=page,
                chunk_id=str(uuid.uuid4()),
                metadata={"chunk_size": len(chunk_text)}
            ))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]


class DocumentProcessor:
    """Process PDFs into searchable chunks"""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunker = SemanticChunker(chunk_size=chunk_size, overlap=overlap)

    def process_pdf(self, pdf_file) -> List[Chunk]:
        """
        Extract text from PDF and chunk it

        Args:
            pdf_file: File-like object or path to PDF

        Returns:
            List of chunks
        """
        # Extract text from PDF
        text_by_page = self._extract_text(pdf_file)

        # Chunk each page
        all_chunks = []
        for page_num, text in text_by_page.items():
            if text.strip():
                chunks = self.chunker.chunk(text, page=page_num)
                all_chunks.extend(chunks)

        return all_chunks

    def _extract_text(self, pdf_file) -> dict:
        """
        Extract text from PDF file

        Returns:
            Dictionary mapping page number to text
        """
        text_by_page = {}

        try:
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_by_page[page_num + 1] = text  # 1-indexed pages

        except Exception as e:
            print(f"Error extracting text from PDF: {e}")

        return text_by_page
