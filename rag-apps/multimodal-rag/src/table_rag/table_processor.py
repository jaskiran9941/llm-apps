"""
Table processing utilities: validation, chunking, and cleaning.
"""

import pandas as pd
from typing import List, Dict, Any
import logging

from ..common.models import TableInfo
from ..common.config import Config
from ..common.utils import generate_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableProcessor:
    """Process and clean tables."""

    def __init__(self):
        self.max_rows_per_chunk = Config.MAX_TABLE_ROWS_PER_CHUNK
        self.chunk_overlap = Config.TABLE_CHUNK_OVERLAP

    def chunk_large_table(self, table_info: TableInfo) -> List[TableInfo]:
        """
        Chunk large tables into smaller pieces.

        Args:
            table_info: TableInfo object

        Returns:
            List of chunked TableInfo objects
        """
        if table_info.num_rows <= self.max_rows_per_chunk:
            return [table_info]

        chunks = []
        df = pd.DataFrame(table_info.table_data)

        # Calculate number of chunks needed
        step_size = self.max_rows_per_chunk - self.chunk_overlap
        num_chunks = (len(df) - self.chunk_overlap) // step_size + 1

        for chunk_idx in range(num_chunks):
            start_idx = chunk_idx * step_size
            end_idx = min(start_idx + self.max_rows_per_chunk, len(df))

            chunk_df = df.iloc[start_idx:end_idx]

            # Create chunk TableInfo
            chunk_table_id = f"{table_info.table_id}_chunk_{chunk_idx}"

            chunk_metadata = table_info.metadata.copy()
            chunk_metadata.update({
                "is_chunk": True,
                "chunk_index": chunk_idx,
                "total_chunks": num_chunks,
                "chunk_rows": f"{start_idx}-{end_idx}",
            })

            chunk_info = TableInfo(
                table_id=chunk_table_id,
                page=table_info.page,
                table_data=chunk_df.to_dict(orient="list"),
                headers=table_info.headers,
                num_rows=len(chunk_df),
                num_cols=table_info.num_cols,
                source_type=table_info.source_type,
                is_chunk=True,
                chunk_index=chunk_idx,
                metadata=chunk_metadata
            )

            chunks.append(chunk_info)

        logger.info(f"Chunked table {table_info.table_id} into {len(chunks)} chunks")
        return chunks

    def validate_table(self, table_info: TableInfo) -> bool:
        """
        Validate table structure.

        Args:
            table_info: TableInfo object

        Returns:
            True if valid, False otherwise
        """
        # Check minimum dimensions
        if table_info.num_rows < 1 or table_info.num_cols < 2:
            logger.warning(f"Table {table_info.table_id} too small: {table_info.num_rows}x{table_info.num_cols}")
            return False

        # Check for data
        if not table_info.table_data:
            logger.warning(f"Table {table_info.table_id} has no data")
            return False

        # Check headers
        if not table_info.headers or len(table_info.headers) != table_info.num_cols:
            logger.warning(f"Table {table_info.table_id} has invalid headers")
            return False

        return True

    def clean_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean table data.

        Args:
            df: pandas DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')

        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]

        # Replace remaining NaN with empty string
        df = df.fillna("")

        return df

    def get_table_summary(self, table_info: TableInfo) -> Dict[str, Any]:
        """
        Generate summary statistics for a table.

        Args:
            table_info: TableInfo object

        Returns:
            Dictionary of summary statistics
        """
        df = pd.DataFrame(table_info.table_data)

        summary = {
            "shape": (table_info.num_rows, table_info.num_cols),
            "headers": table_info.headers,
            "dtypes": {},
            "sample_values": {},
        }

        # Get data types and sample values for each column
        for col in df.columns:
            # Infer type
            if pd.api.types.is_numeric_dtype(df[col]):
                col_type = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_type = "datetime"
            else:
                col_type = "text"

            summary["dtypes"][col] = col_type

            # Get sample values (first 3 non-empty)
            sample = df[col][df[col] != ""].head(3).tolist()
            summary["sample_values"][col] = sample

        return summary

    def serialize_to_markdown(self, table_info: TableInfo, max_rows: int = None) -> str:
        """
        Serialize table to markdown format.

        Args:
            table_info: TableInfo object
            max_rows: Maximum rows to include

        Returns:
            Markdown formatted string
        """
        df = pd.DataFrame(table_info.table_data)

        if max_rows and len(df) > max_rows:
            df_display = df.head(max_rows)
            remaining_rows = len(df) - max_rows
            markdown = df_display.to_markdown(index=False)
            markdown += f"\n\n... ({remaining_rows} more rows)"
        else:
            markdown = df.to_markdown(index=False)

        return markdown

    def export_to_csv(self, table_info: TableInfo, output_path: str) -> str:
        """
        Export table to CSV file.

        Args:
            table_info: TableInfo object
            output_path: Path to save CSV

        Returns:
            Path to saved file
        """
        df = pd.DataFrame(table_info.table_data)
        df.to_csv(output_path, index=False)
        logger.info(f"Exported table {table_info.table_id} to {output_path}")
        return output_path
