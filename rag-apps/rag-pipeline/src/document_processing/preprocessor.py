"""
Text preprocessing utilities.

Cleans and normalizes text before chunking and embedding.
Goal: Improve embedding quality by removing noise while preserving meaning.
"""

import re
from typing import Optional
from src.utils.logger import EducationalLogger

logger = EducationalLogger(__name__)


class TextPreprocessor:
    """
    Preprocess text for better RAG performance.

    Preprocessing improves embedding quality by:
    1. Normalizing whitespace (consistent spacing)
    2. Removing special characters that don't add meaning
    3. Optionally removing headers/footers
    4. Preserving paragraph structure (important for context)
    """

    def __init__(
        self,
        normalize_whitespace: bool = True,
        remove_special_chars: bool = False,
        preserve_paragraphs: bool = True
    ):
        """
        Initialize preprocessor.

        Args:
            normalize_whitespace: Replace multiple spaces/newlines with single ones
            remove_special_chars: Remove non-alphanumeric characters (be careful!)
            preserve_paragraphs: Keep paragraph breaks (recommended for RAG)
        """
        self.normalize_whitespace = normalize_whitespace
        self.remove_special_chars = remove_special_chars
        self.preserve_paragraphs = preserve_paragraphs

    def preprocess(self, text: str) -> str:
        """
        Apply all preprocessing steps.

        Args:
            text: Raw text from document

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        # Store original length for logging
        original_length = len(text)

        # Apply preprocessing steps
        text = self._extract_page_markers(text)
        text = self._normalize_whitespace(text)

        if self.remove_special_chars:
            text = self._remove_special_characters(text)

        if self.preserve_paragraphs:
            text = self._preserve_paragraph_structure(text)

        # Log preprocessing impact
        logger.log_metric(
            "Text preprocessed",
            f"{original_length} → {len(text)} chars",
            f"Reduced by {original_length - len(text)} characters"
        )

        return text.strip()

    def _extract_page_markers(self, text: str) -> str:
        """
        Extract and preserve page markers for later use.

        Page markers like [PAGE 1] are added during PDF extraction
        and help maintain page references during chunking.

        Args:
            text: Text with page markers

        Returns:
            Text with normalized page markers
        """
        # Normalize page marker format
        text = re.sub(r'\[PAGE\s+(\d+)\]', r'[PAGE \1]', text)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace while preserving paragraph breaks.

        Why: Inconsistent whitespace can affect token counting and
        embedding quality. But we want to keep paragraph structure.

        Args:
            text: Text with irregular whitespace

        Returns:
            Text with normalized whitespace
        """
        if not self.normalize_whitespace:
            return text

        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text

    def _remove_special_characters(self, text: str) -> str:
        """
        Remove special characters that don't add semantic meaning.

        WARNING: Be careful with this! Some special characters matter:
        - Hyphens in compound words
        - Apostrophes in contractions
        - Periods in abbreviations

        Only enable if you know your documents have problematic characters.

        Args:
            text: Text with special characters

        Returns:
            Text with special characters removed
        """
        # Keep: letters, numbers, basic punctuation, whitespace
        # Remove: emoji, symbols, control characters
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()\[\]]', ' ', text)
        return text

    def _preserve_paragraph_structure(self, text: str) -> str:
        """
        Ensure paragraph breaks are preserved.

        Why: Paragraph breaks indicate semantic boundaries. Breaking chunks
        at paragraph boundaries often gives better results than mid-sentence.

        Args:
            text: Text potentially missing clear paragraph breaks

        Returns:
            Text with clear paragraph structure
        """
        # Ensure double newline after sentence-ending punctuation
        # followed by capital letter (indicates new paragraph)
        text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', text)

        return text

    def remove_headers_footers(
        self,
        text: str,
        header_pattern: Optional[str] = None,
        footer_pattern: Optional[str] = None
    ) -> str:
        """
        Remove repeated headers and footers from paginated documents.

        Many PDFs have page numbers, copyright notices, etc. repeated
        on every page. These don't add semantic value and can confuse
        the embedding model.

        Args:
            text: Text with headers/footers
            header_pattern: Regex pattern for headers
            footer_pattern: Regex pattern for footers

        Returns:
            Text with headers/footers removed
        """
        if header_pattern:
            text = re.sub(header_pattern, '', text, flags=re.MULTILINE)

        if footer_pattern:
            text = re.sub(footer_pattern, '', text, flags=re.MULTILINE)

        return text

    def clean_page_numbers(self, text: str) -> str:
        """
        Remove standalone page numbers but preserve [PAGE X] markers.

        Args:
            text: Text with page numbers

        Returns:
            Text with standalone page numbers removed
        """
        # Remove lines that are just numbers (page numbers)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

        return text
