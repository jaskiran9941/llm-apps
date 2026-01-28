"""
Multimodal retriever with weighted 4-way search.
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging

from ..common.config import Config
from ..common.models import RetrievalResult
from ..table_rag.table_query_parser import TableQueryParser
from .multimodal_store import MultimodalStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimodalRetriever:
    """Retrieve from multiple modalities with weighted ranking."""

    def __init__(self, store: MultimodalStore):
        """
        Initialize multimodal retriever.

        Args:
            store: MultimodalStore instance
        """
        self.store = store
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.EMBEDDING_MODEL
        self.query_parser = TableQueryParser()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        return response.data[0].embedding

    def retrieve(
        self,
        query: str,
        k: int = None,
        text_weight: float = None,
        image_weight: float = None,
        table_weight: float = None,
        audio_weight: float = None,
        include_text: bool = True,
        include_images: bool = True,
        include_tables: bool = True,
        include_audio: bool = True,
        auto_adjust_weights: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve from multiple modalities.

        Args:
            query: Query string
            k: Total number of results
            text_weight: Weight for text results
            image_weight: Weight for image results
            table_weight: Weight for table results
            audio_weight: Weight for audio results
            include_text: Include text results
            include_images: Include image results
            include_tables: Include table results
            include_audio: Include audio results
            auto_adjust_weights: Automatically adjust weights based on query

        Returns:
            Dictionary with results and metadata
        """
        # Set defaults
        if k is None:
            k = Config.DEFAULT_K

        if text_weight is None:
            text_weight = Config.DEFAULT_TEXT_WEIGHT
        if image_weight is None:
            image_weight = Config.DEFAULT_IMAGE_WEIGHT
        if table_weight is None:
            table_weight = Config.DEFAULT_TABLE_WEIGHT
        if audio_weight is None:
            audio_weight = Config.DEFAULT_AUDIO_WEIGHT

        # Auto-adjust weights based on query
        if auto_adjust_weights:
            text_weight, image_weight, table_weight, audio_weight = self._adjust_weights(
                query, text_weight, image_weight, table_weight, audio_weight
            )

        # Embed query
        query_embedding = self.embed_query(query)

        # Calculate k per modality
        total_weight = (
            (text_weight if include_text else 0) +
            (image_weight if include_images else 0) +
            (table_weight if include_tables else 0) +
            (audio_weight if include_audio else 0)
        )

        k_text = int(k * text_weight / total_weight) if include_text else 0
        k_image = int(k * image_weight / total_weight) if include_images else 0
        k_table = int(k * table_weight / total_weight) if include_tables else 0
        k_audio = int(k * audio_weight / total_weight) if include_audio else 0

        # Ensure at least 1 result per enabled modality
        if include_text and k_text == 0:
            k_text = 1
        if include_images and k_image == 0:
            k_image = 1
        if include_tables and k_table == 0:
            k_table = 1
        if include_audio and k_audio == 0:
            k_audio = 1

        # Retrieve from each modality
        results = {
            "text": [] if include_text else None,
            "images": [] if include_images else None,
            "tables": [] if include_tables else None,
            "audio": [] if include_audio else None,
            "combined": [],
            "query": query,
            "weights": {
                "text": text_weight,
                "image": image_weight,
                "table": table_weight,
                "audio": audio_weight
            }
        }

        # Text results
        if include_text and k_text > 0:
            text_results = self.store.query(
                query_embedding=query_embedding,
                k=k_text,
                filter_type="text"
            )
            results["text"] = self._format_results(text_results, "text")
            results["combined"].extend(results["text"])

        # Image results
        if include_images and k_image > 0:
            image_results = self.store.query(
                query_embedding=query_embedding,
                k=k_image,
                filter_type="image"
            )
            results["images"] = self._format_results(image_results, "image")
            results["combined"].extend(results["images"])

        # Table results
        if include_tables and k_table > 0:
            table_results = self.store.query(
                query_embedding=query_embedding,
                k=k_table,
                filter_type="table"
            )
            results["tables"] = self._format_results(table_results, "table")
            results["combined"].extend(results["tables"])

        # Audio results
        if include_audio and k_audio > 0:
            audio_results = self.store.query(
                query_embedding=query_embedding,
                k=k_audio,
                filter_type="audio"
            )
            results["audio"] = self._format_results(audio_results, "audio")
            results["combined"].extend(results["audio"])

        # Sort combined results by score
        results["combined"].sort(key=lambda x: x.score, reverse=True)

        # Limit to top k
        results["combined"] = results["combined"][:k]

        logger.info(f"Retrieved {len(results['combined'])} results: "
                   f"text={len(results['text']) if results['text'] else 0}, "
                   f"images={len(results['images']) if results['images'] else 0}, "
                   f"tables={len(results['tables']) if results['tables'] else 0}, "
                   f"audio={len(results['audio']) if results['audio'] else 0}")

        return results

    def _adjust_weights(
        self,
        query: str,
        text_weight: float,
        image_weight: float,
        table_weight: float,
        audio_weight: float
    ) -> tuple:
        """
        Automatically adjust weights based on query content.

        Args:
            query: Query string
            text_weight: Default text weight
            image_weight: Default image weight
            table_weight: Default table weight
            audio_weight: Default audio weight

        Returns:
            Tuple of adjusted weights
        """
        query_lower = query.lower()

        # Boost table weight for table-related queries
        if self.query_parser.should_boost_table_weight(query):
            table_weight *= 1.5
            text_weight *= 0.8

        # Boost image weight for visual queries
        visual_keywords = ["image", "picture", "diagram", "chart", "graph", "visual", "show", "see"]
        if any(keyword in query_lower for keyword in visual_keywords):
            image_weight *= 1.5
            text_weight *= 0.8

        # Boost audio weight for audio-related queries
        audio_keywords = ["said", "mentioned", "discussed", "talked", "spoke", "audio", "recording", "transcript"]
        if any(keyword in query_lower for keyword in audio_keywords):
            audio_weight *= 1.5
            text_weight *= 0.8

        # Normalize weights to sum to 1.0
        total = text_weight + image_weight + table_weight + audio_weight
        return (text_weight / total, image_weight / total, table_weight / total, audio_weight / total)

    def _format_results(self, results: Dict[str, Any], result_type: str) -> List[RetrievalResult]:
        """
        Format ChromaDB results into RetrievalResult objects.

        Args:
            results: ChromaDB query results
            result_type: Type of results

        Returns:
            List of RetrievalResult objects
        """
        formatted = []

        if not results['ids'] or not results['ids'][0]:
            return formatted

        for i in range(len(results['ids'][0])):
            content = results['documents'][0][i]
            distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
            metadata = results['metadatas'][0][i]

            # Convert distance to similarity score (1 - normalized distance)
            score = 1.0 - min(distance, 1.0)

            # Create source info
            source_info = self._create_source_info(metadata, result_type)

            result = RetrievalResult(
                content=content,
                type=result_type,
                score=score,
                metadata=metadata,
                source_info=source_info
            )

            formatted.append(result)

        return formatted

    def _create_source_info(self, metadata: Dict[str, Any], result_type: str) -> str:
        """
        Create human-readable source information.

        Args:
            metadata: Result metadata
            result_type: Type of result

        Returns:
            Source info string
        """
        if result_type == "text":
            return f"Text from page {metadata.get('page', 'unknown')}"
        elif result_type == "image":
            return f"Image from page {metadata.get('page', 'unknown')}"
        elif result_type == "table":
            rows = metadata.get('num_rows', '?')
            cols = metadata.get('num_cols', '?')
            return f"Table ({rows}×{cols}) from page {metadata.get('page', 'unknown')}"
        elif result_type == "audio":
            start = metadata.get('start_time', 0)
            end = metadata.get('end_time', 0)
            from ..common.utils import format_timestamp
            return f"Audio segment [{format_timestamp(start)} - {format_timestamp(end)}]"
        else:
            return "Unknown source"
