"""
Simple in-memory vector store (ChromaDB alternative for Python 3.14 compatibility).
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path
import pickle

from ..common.config import Config
from ..common.models import TextChunk, ImageInfo, TableInfo, AudioInfo, AudioSegment


class SimpleVectorStore:
    """Simple in-memory vector store with persistence."""

    def __init__(self, persist_directory: Path = None):
        """Initialize simple vector store."""
        if persist_directory is None:
            persist_directory = Config.CHROMA_DIR

        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.store_path = self.persist_directory / "simple_store.pkl"

        # In-memory storage
        self.ids: List[str] = []
        self.embeddings: List[List[float]] = []
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

        # Load if exists
        self._load()

    def add_text_chunks(self, chunks: List[Tuple[TextChunk, List[float], str]]):
        """Add text chunks."""
        for chunk, embedding, text in chunks:
            self._add_item(
                id=chunk.chunk_id,
                embedding=embedding,
                document=text,
                metadata={
                    "type": "text",
                    "page": chunk.page,
                    "chunk_index": chunk.chunk_index,
                    **chunk.metadata
                }
            )
        self._save()

    def add_images(self, images: List[Tuple[ImageInfo, List[float], str]]):
        """Add images."""
        for image_info, embedding, description in images:
            self._add_item(
                id=image_info.image_id,
                embedding=embedding,
                document=description,
                metadata={
                    "type": "image",
                    "page": image_info.page,
                    "image_path": image_info.image_path,
                    "width": image_info.width,
                    "height": image_info.height,
                    "format": image_info.format,
                    **image_info.metadata
                }
            )
        self._save()

    def add_tables(self, tables: List[Tuple[TableInfo, List[float], str]]):
        """Add tables."""
        for table_info, embedding, combined_text in tables:
            self._add_item(
                id=table_info.table_id,
                embedding=embedding,
                document=combined_text,
                metadata={
                    "type": "table",
                    "page": table_info.page,
                    "table_id": table_info.table_id,
                    "table_data": json.dumps(table_info.table_data),
                    "num_rows": table_info.num_rows,
                    "num_cols": table_info.num_cols,
                    "headers": json.dumps(table_info.headers),
                    "source_type": table_info.source_type,
                    "description": table_info.description or "",
                    "is_chunk": table_info.is_chunk,
                    **table_info.metadata
                }
            )
        self._save()

    def add_audio_segments(self, audio_segments: List[Tuple[AudioInfo, AudioSegment, List[float], str]]):
        """Add audio segments."""
        for audio_info, segment, embedding, enriched_text in audio_segments:
            self._add_item(
                id=segment.segment_id,
                embedding=embedding,
                document=enriched_text,
                metadata={
                    "type": "audio",
                    "audio_id": audio_info.audio_id,
                    "audio_path": audio_info.audio_path,
                    "segment_id": segment.segment_id,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "duration": segment.end_time - segment.start_time,
                    "language": audio_info.language,
                    "speaker": segment.speaker or "Unknown",
                    "topics": json.dumps(audio_info.topics or []),
                    **audio_info.metadata
                }
            )
        self._save()

    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
        filter_type: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query the store."""
        if not self.embeddings:
            return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}

        # Calculate cosine similarities
        query_emb = np.array(query_embedding)
        all_embeddings = np.array(self.embeddings)

        # Cosine similarity
        similarities = np.dot(all_embeddings, query_emb) / (
            np.linalg.norm(all_embeddings, axis=1) * np.linalg.norm(query_emb)
        )

        # Convert to distances (1 - similarity)
        distances = 1 - similarities

        # Apply filters
        valid_indices = []
        for i in range(len(self.ids)):
            metadata = self.metadatas[i]

            # Type filter
            if filter_type and metadata.get("type") != filter_type:
                continue

            # Metadata filters
            if filter_metadata:
                match = all(
                    metadata.get(key) == value
                    for key, value in filter_metadata.items()
                )
                if not match:
                    continue

            valid_indices.append(i)

        if not valid_indices:
            return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}

        # Get top k
        valid_distances = distances[valid_indices]
        sorted_idx = np.argsort(valid_distances)[:k]

        result_indices = [valid_indices[i] for i in sorted_idx]

        return {
            "ids": [[self.ids[i] for i in result_indices]],
            "distances": [[float(distances[i]) for i in result_indices]],
            "documents": [[self.documents[i] for i in result_indices]],
            "metadatas": [[self.metadatas[i] for i in result_indices]]
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        type_counts = {"text": 0, "image": 0, "table": 0, "audio": 0}

        for metadata in self.metadatas:
            type_name = metadata.get("type")
            if type_name in type_counts:
                type_counts[type_name] += 1

        return {
            "total_items": len(self.ids),
            "by_type": type_counts
        }

    def clear(self):
        """Clear all data."""
        self.ids = []
        self.embeddings = []
        self.documents = []
        self.metadatas = []
        self._save()

    def _add_item(self, id: str, embedding: List[float], document: str, metadata: Dict[str, Any]):
        """Add single item."""
        self.ids.append(id)
        self.embeddings.append(embedding)
        self.documents.append(document)
        self.metadatas.append(metadata)

    def _save(self):
        """Save to disk."""
        data = {
            "ids": self.ids,
            "embeddings": self.embeddings,
            "documents": self.documents,
            "metadatas": self.metadatas
        }
        with open(self.store_path, 'wb') as f:
            pickle.dump(data, f)

    def _load(self):
        """Load from disk."""
        if self.store_path.exists():
            with open(self.store_path, 'rb') as f:
                data = pickle.load(f)
                self.ids = data.get("ids", [])
                self.embeddings = data.get("embeddings", [])
                self.documents = data.get("documents", [])
                self.metadatas = data.get("metadatas", [])


# Alias for compatibility
MultimodalStore = SimpleVectorStore
