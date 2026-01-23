"""
PDF document loader.

Extracts text from PDF files while preserving page numbers for citation.
Supports multiple PDF libraries with fallback mechanisms.
"""

import PyPDF2
import pdfplumber
from pathlib import Path
from typing import List, Optional
from src.models import Document
from src.utils.logger import EducationalLogger
from src.utils.validators import validate_file_upload

logger = EducationalLogger(__name__)


class PDFLoader:
    """
    Load and extract text from PDF files.

    This class tries multiple extraction methods:
    1. pdfplumber - Better for complex PDFs with tables
    2. PyPDF2 - Faster, good for simple text PDFs

    Page numbers are preserved in metadata for citation purposes.
    """

    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize PDF loader.

        Args:
            use_pdfplumber: If True, prefer pdfplumber over PyPDF2
        """
        self.use_pdfplumber = use_pdfplumber

    def load(self, file_path: Path, doc_id: Optional[str] = None) -> Document:
        """
        Load a PDF file and extract text.

        Args:
            file_path: Path to PDF file
            doc_id: Optional document ID (defaults to filename)

        Returns:
            Document object with extracted text and metadata

        Raises:
            ValueError: If file validation fails
            Exception: If PDF extraction fails
        """
        # Validate file
        validate_file_upload(file_path)

        # Generate doc_id if not provided
        if doc_id is None:
            doc_id = file_path.stem  # Filename without extension

        logger.log_step(
            "PDF_LOAD",
            f"Loading {file_path.name}",
            "Extracting text while preserving page numbers for citations"
        )

        try:
            # Try extraction method
            if self.use_pdfplumber:
                text, pages = self._extract_with_pdfplumber(file_path)
            else:
                text, pages = self._extract_with_pypdf2(file_path)

            # Create metadata
            metadata = {
                "filename": file_path.name,
                "source_path": str(file_path),
                "num_pages": pages,
                "extraction_method": "pdfplumber" if self.use_pdfplumber else "PyPDF2"
            }

            logger.log_metric(
                "Pages extracted",
                pages,
                f"from {file_path.name}"
            )

            return Document(
                doc_id=doc_id,
                text=text,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Failed to load PDF {file_path.name}: {str(e)}")
            # Try fallback method
            if self.use_pdfplumber:
                logger.info("Trying fallback to PyPDF2...")
                text, pages = self._extract_with_pypdf2(file_path)
            else:
                logger.info("Trying fallback to pdfplumber...")
                text, pages = self._extract_with_pdfplumber(file_path)

            metadata = {
                "filename": file_path.name,
                "source_path": str(file_path),
                "num_pages": pages,
                "extraction_method": "fallback"
            }

            return Document(
                doc_id=doc_id,
                text=text,
                metadata=metadata
            )

    def _extract_with_pdfplumber(self, file_path: Path) -> tuple[str, int]:
        """
        Extract text using pdfplumber.

        pdfplumber is better at:
        - Extracting text from complex layouts
        - Handling tables and columns
        - Preserving text order

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (extracted_text, num_pages)
        """
        text_parts = []
        num_pages = 0

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from page
                page_text = page.extract_text()

                if page_text:
                    # Add page marker for later reference
                    # This helps during chunking to maintain page numbers
                    page_marker = f"\n[PAGE {page_num}]\n"
                    text_parts.append(page_marker + page_text)

                num_pages += 1

        full_text = "\n".join(text_parts)
        return full_text, num_pages

    def _extract_with_pypdf2(self, file_path: Path) -> tuple[str, int]:
        """
        Extract text using PyPDF2.

        PyPDF2 is:
        - Faster than pdfplumber
        - Good for simple text PDFs
        - Less accurate for complex layouts

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (extracted_text, num_pages)
        """
        text_parts = []
        num_pages = 0

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            for page_num, page in enumerate(pdf_reader.pages, start=1):
                # Extract text from page
                page_text = page.extract_text()

                if page_text:
                    # Add page marker
                    page_marker = f"\n[PAGE {page_num}]\n"
                    text_parts.append(page_marker + page_text)

        full_text = "\n".join(text_parts)
        return full_text, num_pages

    def load_multiple(self, file_paths: List[Path]) -> List[Document]:
        """
        Load multiple PDF files.

        Args:
            file_paths: List of paths to PDF files

        Returns:
            List of Document objects
        """
        documents = []

        for file_path in file_paths:
            try:
                doc = self.load(file_path)
                documents.append(doc)
            except Exception as e:
                logger.error(
                    f"Skipping {file_path.name} due to error: {str(e)}"
                )
                continue

        logger.info(
            f"Loaded {len(documents)}/{len(file_paths)} documents successfully"
        )

        return documents
