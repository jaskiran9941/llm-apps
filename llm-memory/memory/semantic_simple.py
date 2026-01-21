"""
Simple semantic memory using sentence transformers and numpy
No ChromaDB dependency - pure Python implementation
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple
from config.config import EMBEDDING_MODEL, CHUNK_SIZE, TOP_K_RETRIEVAL, SIMILARITY_THRESHOLD


class SimpleSemanticMemory:
    """Lightweight semantic memory using in-memory vector storage."""

    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.chunks = []  # List of text chunks
        self.embeddings = []  # List of embedding vectors
        self.metadata = []  # List of metadata dicts

    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def add_document(self, document_text: str, document_name: str, metadata: Dict = None):
        """Add a document to semantic memory."""
        # Chunk the document
        chunks = self.chunk_text(document_text)

        # Embed and store each chunk
        for i, chunk in enumerate(chunks):
            # Embed
            embedding = self.embedding_model.encode(chunk)

            # Store
            self.chunks.append(chunk)
            self.embeddings.append(embedding)

            chunk_meta = {
                "document_name": document_name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                chunk_meta.update(metadata)
            self.metadata.append(chunk_meta)

        return len(chunks)

    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        similarity_threshold: float = SIMILARITY_THRESHOLD
    ) -> Tuple[str, List[Dict]]:
        """Retrieve relevant context for a query."""
        if not self.chunks:
            return "", []

        # Embed the query
        query_embedding = self.embedding_model.encode(query)

        # Calculate similarities
        similarities = []
        for i, chunk_embedding in enumerate(self.embeddings):
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            similarities.append((i, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top-k above threshold
        retrieval_details = []
        context_chunks = []

        for idx, similarity in similarities[:top_k]:
            if similarity >= similarity_threshold:
                retrieval_details.append({
                    "chunk_id": f"chunk_{idx}",
                    "similarity": float(similarity),
                    "content": self.chunks[idx],
                    "metadata": self.metadata[idx]
                })
                context_chunks.append(self.chunks[idx])

        # Format context
        formatted_context = "\n\n---\n\n".join(context_chunks)

        return formatted_context, retrieval_details

    def get_all_documents(self) -> List[Dict]:
        """Get list of all indexed documents."""
        documents = {}
        for meta in self.metadata:
            doc_name = meta['document_name']
            if doc_name not in documents:
                documents[doc_name] = {
                    "name": doc_name,
                    "chunks": 0,
                    "metadata": meta
                }
            documents[doc_name]['chunks'] += 1

        return list(documents.values())

    def get_embedding_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        return {
            "total_chunks": len(self.chunks),
            "embedding_dimension": 384,
            "model": EMBEDDING_MODEL
        }

    def clear(self):
        """Clear all documents from semantic memory."""
        self.chunks = []
        self.embeddings = []
        self.metadata = []
