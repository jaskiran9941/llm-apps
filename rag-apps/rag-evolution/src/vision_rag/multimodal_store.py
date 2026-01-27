"""
Multimodal vector store (text + images)
"""
from typing import List, Union
import chromadb
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

        # Initialize ChromaDB with new API (v0.4+)
        self.client = chromadb.PersistentClient(path=str(Config.CHROMA_DIR))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
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

    def add_images(self, images: List[ImageInfo]):
        """Add images to the store one at a time for robustness"""
        if not images:
            return

        # Process and add each image individually
        # This ensures partial progress is saved even if some images fail
        for image in images:
            try:
                # Generate description if needed
                if not image.description:
                    image.description = self.vision_embedder.describe_image(image.image_path)

                # Skip failed descriptions
                if image.description and image.description.startswith("[DESCRIPTION_FAILED]"):
                    continue

                # Generate embedding
                embedding = self.text_embedder.embed_text(image.description)

                # Build metadata - spread first, then override type to ensure it's 'image'
                meta = {**image.metadata}
                meta["type"] = "image"  # Override any type from extraction
                meta["page"] = image.page
                meta["image_path"] = image.image_path

                # Add to collection immediately
                self.collection.add(
                    ids=[f"image_{image.image_id}"],
                    embeddings=[embedding],
                    documents=[image.description],
                    metadatas=[meta]
                )
            except Exception as e:
                print(f"Error processing image {image.image_path}: {e}")
                continue

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
            metadata={"hnsw:space": "cosine"}
        )
