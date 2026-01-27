"""
Table embedding using hybrid approach: caption + serialization.
"""

import pandas as pd
from openai import OpenAI
from typing import List, Tuple
import logging

from ..common.models import TableInfo
from ..common.config import Config
from ..common.utils import count_tokens
from .table_processor import TableProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableEmbedder:
    """Generate embeddings for tables using hybrid approach."""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.EMBEDDING_MODEL
        self.chat_model = Config.CHAT_MODEL
        self.processor = TableProcessor()
        self.preview_rows = Config.TABLE_PREVIEW_ROWS

    def generate_caption(self, table_info: TableInfo) -> str:
        """
        Generate a descriptive caption for the table using GPT-4.

        Args:
            table_info: TableInfo object

        Returns:
            Generated caption
        """
        df = pd.DataFrame(table_info.table_data)

        # Create table preview (first N rows + summary)
        preview = self.processor.serialize_to_markdown(table_info, max_rows=self.preview_rows)
        summary = self.processor.get_table_summary(table_info)

        # Build prompt
        prompt = f"""Analyze this table and provide a concise description (2-3 sentences) covering:
1. What the table represents
2. Key columns and their meanings
3. Data types and patterns
4. Potential use cases

Table Preview:
{preview}

Summary Statistics:
- Shape: {summary['shape'][0]} rows × {summary['shape'][1]} columns
- Columns: {', '.join(summary['headers'])}
- Data Types: {summary['dtypes']}

Provide only the description, no additional commentary."""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a data analyst describing tables concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )

            caption = response.choices[0].message.content.strip()
            logger.info(f"Generated caption for table {table_info.table_id}: {len(caption)} chars")
            return caption

        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            # Fallback caption
            return f"Table with {table_info.num_rows} rows and {table_info.num_cols} columns: {', '.join(table_info.headers)}"

    def serialize_table(self, table_info: TableInfo) -> str:
        """
        Serialize table to markdown format with context.

        Args:
            table_info: TableInfo object

        Returns:
            Markdown formatted string with headers
        """
        markdown = self.processor.serialize_to_markdown(table_info)

        # Add header context
        context = f"""Table Information:
- Location: Page {table_info.page}
- Dimensions: {table_info.num_rows} rows × {table_info.num_cols} columns
- Source: {table_info.source_type.upper()}

Table Data:
{markdown}"""

        return context

    def embed_table(self, table_info: TableInfo, generate_caption: bool = True) -> Tuple[List[float], str]:
        """
        Generate embedding for table using hybrid approach.

        Args:
            table_info: TableInfo object
            generate_caption: Whether to generate GPT-4 caption

        Returns:
            Tuple of (embedding vector, combined text)
        """
        # Generate caption
        if generate_caption and not table_info.description:
            caption = self.generate_caption(table_info)
            table_info.description = caption
        else:
            caption = table_info.description or ""

        # Serialize table
        if not table_info.serialized_text:
            serialized = self.serialize_table(table_info)
            table_info.serialized_text = serialized
        else:
            serialized = table_info.serialized_text

        # Combine caption and serialization
        combined_text = f"{caption}\n\n{serialized}"

        # Generate embedding
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=combined_text
            )

            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for table {table_info.table_id}")
            return embedding, combined_text

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_tables(self, tables: List[TableInfo], generate_captions: bool = True) -> List[Tuple[TableInfo, List[float], str]]:
        """
        Generate embeddings for multiple tables.

        Args:
            tables: List of TableInfo objects
            generate_captions: Whether to generate GPT-4 captions

        Returns:
            List of tuples (TableInfo, embedding, combined_text)
        """
        results = []

        for table_info in tables:
            try:
                embedding, combined_text = self.embed_table(table_info, generate_caption=generate_captions)
                results.append((table_info, embedding, combined_text))
            except Exception as e:
                logger.error(f"Failed to embed table {table_info.table_id}: {e}")
                continue

        logger.info(f"Successfully embedded {len(results)}/{len(tables)} tables")
        return results

    def estimate_cost(self, tables: List[TableInfo], generate_captions: bool = True) -> dict:
        """
        Estimate the cost of embedding tables.

        Args:
            tables: List of TableInfo objects
            generate_captions: Whether captions will be generated

        Returns:
            Dictionary with cost breakdown
        """
        total_caption_tokens = 0
        total_embedding_tokens = 0

        for table in tables:
            # Estimate caption generation cost
            if generate_captions:
                preview = self.processor.serialize_to_markdown(table, max_rows=self.preview_rows)
                prompt_tokens = count_tokens(preview) + 200  # Base prompt
                total_caption_tokens += prompt_tokens

            # Estimate embedding cost
            caption = table.description or "Default caption placeholder"
            serialized = table.serialized_text or self.serialize_table(table)
            combined_text = f"{caption}\n\n{serialized}"
            total_embedding_tokens += count_tokens(combined_text)

        # Calculate costs
        caption_cost = (total_caption_tokens / 1000) * Config.COST_GPT4_INPUT + (400 * len(tables) / 1000) * Config.COST_GPT4_OUTPUT
        embedding_cost = (total_embedding_tokens / 1000) * Config.COST_EMBEDDING

        return {
            "caption_tokens": total_caption_tokens,
            "embedding_tokens": total_embedding_tokens,
            "caption_cost": caption_cost if generate_captions else 0,
            "embedding_cost": embedding_cost,
            "total_cost": caption_cost + embedding_cost if generate_captions else embedding_cost,
            "num_tables": len(tables)
        }
