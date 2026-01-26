"""
Text preprocessing utilities
"""
import re
from typing import Dict, List


class TextPreprocessor:
    """Preprocess text before chunking"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove null bytes and replacement characters
        text = text.replace("\x00", "")
        text = text.replace("\ufffd", "")

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page numbers (common pattern)
        text = re.sub(r'Page \d+', '', text)

        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def detect_tables(text: str) -> List[Dict]:
        """Detect table-like structures in text"""
        tables = []
        lines = text.split('\n')

        table_lines = []
        in_table = False

        for line in lines:
            # Simple heuristic: lines with multiple tabs or pipes
            if '\t' in line or '|' in line:
                table_lines.append(line)
                in_table = True
            elif in_table and table_lines:
                # End of table
                tables.append({
                    'content': '\n'.join(table_lines),
                    'num_rows': len(table_lines)
                })
                table_lines = []
                in_table = False

        # Add last table if exists
        if table_lines:
            tables.append({
                'content': '\n'.join(table_lines),
                'num_rows': len(table_lines)
            })

        return tables

    @staticmethod
    def preserve_code_blocks(text: str) -> str:
        """Preserve code block formatting"""
        # Detect code blocks (indented or fenced)
        code_block_pattern = r'```[\s\S]*?```|`[^`]+`'

        # Replace with placeholder to prevent chunking in middle
        code_blocks = re.findall(code_block_pattern, text)

        for i, block in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            text = text.replace(block, placeholder)

        return text

    @staticmethod
    def extract_headers(text: str) -> List[str]:
        """Extract section headers"""
        headers = []

        # Pattern for common header formats
        patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Za-z\s]+):$',  # Title case with colon
            r'^\d+\.\s+([A-Z][A-Za-z\s]+)$',  # Numbered sections
        ]

        for line in text.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    headers.append(match.group(1) if match.groups() else line.strip())
                    break

        return headers


class DocumentStructureAnalyzer:
    """Analyze document structure"""

    @staticmethod
    def analyze(text: str) -> Dict:
        """Analyze document structure"""
        preprocessor = TextPreprocessor()

        return {
            'total_chars': len(text),
            'total_lines': len(text.split('\n')),
            'tables': preprocessor.detect_tables(text),
            'headers': preprocessor.extract_headers(text),
            'has_code_blocks': bool(re.search(r'```[\s\S]*?```', text)),
            'avg_line_length': sum(len(line) for line in text.split('\n')) / max(len(text.split('\n')), 1)
        }
