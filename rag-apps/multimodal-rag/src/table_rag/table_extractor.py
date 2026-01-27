"""
Table extraction from PDFs, Excel, and CSV files.
"""

import pdfplumber
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging

from ..common.models import TableInfo
from ..common.utils import generate_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableExtractor:
    """Extract tables from various file formats."""

    def extract_from_pdf(self, pdf_path: Path) -> List[TableInfo]:
        """
        Extract tables from PDF using pdfplumber.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of TableInfo objects
        """
        tables = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract tables using both lattice and stream strategies
                    page_tables = page.extract_tables()

                    for table_index, table_data in enumerate(page_tables):
                        if not table_data or len(table_data) < 2:
                            continue

                        # Convert to DataFrame
                        try:
                            df = self._table_to_dataframe(table_data)

                            if df.empty or len(df.columns) < 2:
                                continue

                            # Create TableInfo
                            table_info = self._create_table_info(
                                df=df,
                                page=page_num,
                                table_index=table_index,
                                source_type="pdf"
                            )

                            tables.append(table_info)
                            logger.info(f"Extracted table from page {page_num}: {df.shape}")

                        except Exception as e:
                            logger.warning(f"Failed to parse table on page {page_num}: {e}")
                            continue

        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")

        return tables

    def extract_from_excel(self, excel_path: Path) -> List[TableInfo]:
        """
        Extract tables from Excel file.

        Args:
            excel_path: Path to Excel file

        Returns:
            List of TableInfo objects (one per sheet)
        """
        tables = []

        try:
            # Read all sheets
            excel_file = pd.ExcelFile(excel_path)

            for sheet_index, sheet_name in enumerate(excel_file.sheet_names):
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)

                    if df.empty or len(df.columns) < 2:
                        continue

                    # Create TableInfo
                    table_info = self._create_table_info(
                        df=df,
                        page=sheet_index,
                        table_index=0,
                        source_type="excel",
                        metadata={"sheet_name": sheet_name}
                    )

                    tables.append(table_info)
                    logger.info(f"Extracted table from sheet '{sheet_name}': {df.shape}")

                except Exception as e:
                    logger.warning(f"Failed to parse sheet '{sheet_name}': {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting tables from Excel: {e}")

        return tables

    def extract_from_csv(self, csv_path: Path) -> List[TableInfo]:
        """
        Extract table from CSV file.

        Args:
            csv_path: Path to CSV file

        Returns:
            List containing single TableInfo object
        """
        tables = []

        try:
            # Try to read CSV with automatic delimiter detection
            df = pd.read_csv(csv_path)

            if not df.empty and len(df.columns) >= 2:
                # Create TableInfo
                table_info = self._create_table_info(
                    df=df,
                    page=0,
                    table_index=0,
                    source_type="csv"
                )

                tables.append(table_info)
                logger.info(f"Extracted table from CSV: {df.shape}")

        except Exception as e:
            logger.error(f"Error extracting table from CSV: {e}")

        return tables

    def _table_to_dataframe(self, table_data: List[List[Any]]) -> pd.DataFrame:
        """
        Convert raw table data to DataFrame.

        Args:
            table_data: Raw table data (list of lists)

        Returns:
            pandas DataFrame
        """
        if not table_data or len(table_data) < 2:
            return pd.DataFrame()

        # First row as headers
        headers = table_data[0]
        data = table_data[1:]

        # Clean headers
        headers = [str(h).strip() if h else f"Column_{i}" for i, h in enumerate(headers)]

        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Clean data: remove None and empty strings
        df = df.fillna("")

        # Remove completely empty rows
        df = df[df.astype(str).ne("").any(axis=1)]

        return df

    def _create_table_info(
        self,
        df: pd.DataFrame,
        page: int,
        table_index: int,
        source_type: str,
        metadata: Dict[str, Any] = None
    ) -> TableInfo:
        """
        Create TableInfo object from DataFrame.

        Args:
            df: pandas DataFrame
            page: Page number or sheet index
            table_index: Index of table on page
            source_type: Source type (pdf, excel, csv)
            metadata: Additional metadata

        Returns:
            TableInfo object
        """
        # Generate unique ID
        table_id = generate_id(
            f"{source_type}_{page}_{table_index}_{df.shape}",
            prefix="table"
        )

        # Serialize DataFrame
        table_data = df.to_dict(orient="records")

        # Get headers
        headers = df.columns.tolist()

        # Create metadata
        table_metadata = metadata or {}
        table_metadata.update({
            "source_type": source_type,
            "shape": str(df.shape),
        })

        return TableInfo(
            table_id=table_id,
            page=page,
            table_data=table_data,
            headers=headers,
            num_rows=len(df),
            num_cols=len(df.columns),
            source_type=source_type,
            metadata=table_metadata
        )
