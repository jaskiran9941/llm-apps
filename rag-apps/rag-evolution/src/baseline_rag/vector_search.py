"""
Vector search using ChromaDB
"""
from typing import List
import chromadb
from chromadb.config import Settings
from ..common.models import Chunk, RetrievalResult
from ..common.config import Config
from .text_embedder import TextEmbedder


class VectorSearch:
    """Simple vector similarity search"""

    def __init__(self, collection_name: str = "baseline_rag"):
        self.collection_name = collection_name
        self.embedder = TextEmbedder()

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

    def add_chunks(self, chunks: List[Chunk]):
        """Add chunks to vector database"""
        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [
            {
                "page": chunk.page,
                **chunk.metadata
            }
            for chunk in chunks
        ]

        # Generate embeddings
        embeddings = self.embedder.embed_batch(texts)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        self.client.persist()

    def search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        """Search for similar chunks"""
        # Embed query
        query_embedding = self.embedder.embed_text(query)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        # Parse results
        retrieved = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                result = RetrievalResult(
                    content=results['documents'][0][i],
                    score=1 - results['distances'][0][i],  # Convert distance to similarity
                    chunk_id=results['ids'][0][i],
                    page=results['metadatas'][0][i].get('page', 0),
                    result_type="text",
                    metadata=results['metadatas'][0][i]
                )
                retrieved.append(result)

        return retrieved

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

    def count(self) -> int:
        """Get number of chunks in collection"""
        return self.collection.count()
