"""
Multimodal vector store (text + images)
"""
from typing import List, Union
import chromadb
from chromadb.config import Settings
from ..common.models import Chunk, ImageInfo, RetrievalResult
from ..common.config import Config
from .vision_embedder import VisionEmbedder
from ..baseline_rag.text_embedder import TextEmbedder


class MultimodalVectorStore:
    """Store and search both text and images"""

    def __init__(self, collection_name: str = "multimodal_rag"):
        self.collection_name = collection_name
        self.text_embedder = TextEmbedder()
        self.vision_embedder = VisionEmbedder()

        # Initialize ChromaDB (compatible with 0.3.x)
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(Config.CHROMA_DIR),
                anonymized_telemetry=False
            )
        )

        # Create or get collection
        # embedding_function=None tells ChromaDB we're handling embeddings ourselves
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=None
        )

    def add_text_chunks(self, chunks: List[Chunk]):
        """Add text chunks to the store"""
        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]
        ids = [f"text_{chunk.chunk_id}" for chunk in chunks]
        metadatas = [
            {
                "type": "text",
                "page": chunk.page,
                **chunk.metadata
            }
            for chunk in chunks
        ]

        # Generate embeddings
        embeddings = self.text_embedder.embed_batch(texts)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        self.client.persist()

    def add_images(self, images: List[ImageInfo]):
        """Add images to the store"""
        if not images:
            return

        # Generate descriptions and embeddings
        for image in images:
            if not image.description:
                image.description = self.vision_embedder.describe_image(image.image_path)

        descriptions = [img.description for img in images]
        ids = [f"image_{img.image_id}" for img in images]
        metadatas = [
            {
                "type": "image",
                "page": img.page,
                "image_path": img.image_path,
                **img.metadata
            }
            for img in images
        ]

        # Generate embeddings from descriptions
        embeddings = self.text_embedder.embed_batch(descriptions)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=descriptions,
            metadatas=metadatas
        )
        self.client.persist()

    def search(
        self,
        query: str,
        k: int = 10,
        filter_type: str = None
    ) -> List[RetrievalResult]:
        """
        Search for both text and images.

        Args:
            query: Search query
            k: Number of results
            filter_type: 'text', 'image', or None for both

        Returns:
            Mixed results (text and images)
        """
        # Embed query
        query_embedding = self.text_embedder.embed_text(query)

        # Build filter
        where_filter = None
        if filter_type:
            where_filter = {"type": filter_type}

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter
        )

        # Parse results
        retrieved = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                result_type = metadata.get('type', 'text')

                result = RetrievalResult(
                    content=results['documents'][0][i],
                    score=1 - results['distances'][0][i],
                    chunk_id=results['ids'][0][i],
                    page=metadata.get('page', 0),
                    result_type=result_type,
                    image_path=metadata.get('image_path') if result_type == 'image' else None,
                    metadata=metadata
                )
                retrieved.append(result)

        return retrieved

    def get_statistics(self) -> dict:
        """Get store statistics"""
        all_items = self.collection.get()

        text_count = sum(
            1 for m in all_items['metadatas'] if m.get('type') == 'text'
        )
        image_count = sum(
            1 for m in all_items['metadatas'] if m.get('type') == 'image'
        )

        return {
            "total_items": len(all_items['ids']),
            "text_chunks": text_count,
            "images": image_count
        }

    def clear(self):
        """Clear the collection"""
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=None
        )
        self.client.persist()
