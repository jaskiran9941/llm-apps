import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import os
from config.config import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    TOP_K_RETRIEVAL,
    SIMILARITY_THRESHOLD
)

class SemanticMemory:
    """
    Manages semantic memory using RAG (Retrieval Augmented Generation).

    Key concepts:
    - Documents are split into chunks
    - Each chunk is embedded into a vector (384 dimensions)
    - Vectors are stored in ChromaDB
    - When user asks a question, we:
      1. Embed the question
      2. Find similar document chunks (cosine similarity)
      3. Return top-k most relevant chunks
      4. Add them to LLM prompt as context
    """

    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIRECTORY):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"description": "Knowledge base for LLM memory demo"}
        )

    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """
        Split text into chunks for embedding.

        Why chunking?
        - Embeddings work best on focused content
        - Smaller chunks = more precise retrieval
        - Typical size: 500 tokens (~2000 characters)
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    def add_document(self, document_text: str, document_name: str, metadata: Dict = None):
        """
        Add a document to semantic memory.

        Process:
        1. Split document into chunks
        2. Embed each chunk to vector
        3. Store in ChromaDB with metadata

        Args:
            document_text: Full document content
            document_name: Name/identifier for the document
            metadata: Additional metadata (source, date, etc.)
        """
        # Chunk the document
        chunks = self.chunk_text(document_text)

        # Prepare data for ChromaDB
        chunk_ids = []
        chunk_texts = []
        chunk_metadata = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_name}_chunk_{i}"
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk)

            chunk_meta = {
                "document_name": document_name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                chunk_meta.update(metadata)
            chunk_metadata.append(chunk_meta)

        # Embed chunks
        embeddings = self.embedding_model.encode(chunk_texts).tolist()

        # Add to ChromaDB
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=chunk_metadata
        )

        return len(chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RETRIEVAL,
        similarity_threshold: float = SIMILARITY_THRESHOLD
    ) -> Tuple[str, List[Dict]]:
        """
        Retrieve relevant context for a query.

        Process:
        1. Embed the query to vector
        2. Find similar vectors in ChromaDB (cosine similarity)
        3. Filter by similarity threshold
        4. Return top-k most relevant chunks

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            Tuple of (formatted_context_string, retrieval_details)
        """
        # Embed the query
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Parse results
        retrieval_details = []
        context_chunks = []

        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                # Calculate similarity score (ChromaDB returns distance, we want similarity)
                # For cosine distance: similarity = 1 - distance
                distance = results['distances'][0][i]
                similarity = 1 - distance

                # Filter by threshold
                if similarity >= similarity_threshold:
                    chunk_text = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]

                    retrieval_details.append({
                        "chunk_id": results['ids'][0][i],
                        "similarity": round(similarity, 3),
                        "content": chunk_text,
                        "metadata": metadata
                    })

                    context_chunks.append(chunk_text)

        # Format context for LLM prompt
        formatted_context = "\n\n---\n\n".join(context_chunks)

        return formatted_context, retrieval_details

    def get_all_documents(self) -> List[Dict]:
        """Get list of all indexed documents."""
        results = self.collection.get()

        documents = {}
        if results['ids']:
            for i, chunk_id in enumerate(results['ids']):
                doc_name = results['metadatas'][i]['document_name']
                if doc_name not in documents:
                    documents[doc_name] = {
                        "name": doc_name,
                        "chunks": 0,
                        "metadata": results['metadatas'][i]
                    }
                documents[doc_name]['chunks'] += 1

        return list(documents.values())

    def get_embedding_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        results = self.collection.get()
        return {
            "total_chunks": len(results['ids']) if results['ids'] else 0,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "model": EMBEDDING_MODEL
        }

    def clear(self):
        """Clear all documents from semantic memory."""
        self.client.delete_collection(CHROMA_COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"description": "Knowledge base for LLM memory demo"}
        )

    def delete_document(self, document_name: str):
        """Delete all chunks of a specific document."""
        # Get all chunk IDs for this document
        results = self.collection.get()
        chunk_ids_to_delete = []

        if results['ids']:
            for i, chunk_id in enumerate(results['ids']):
                if results['metadatas'][i]['document_name'] == document_name:
                    chunk_ids_to_delete.append(chunk_id)

        if chunk_ids_to_delete:
            self.collection.delete(ids=chunk_ids_to_delete)

        return len(chunk_ids_to_delete)
