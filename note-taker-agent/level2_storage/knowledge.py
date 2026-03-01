"""
knowledge.py — Level 2: ChromaDB semantic search

What this solves from Level 1's wall:
  Before: finding notes required exact title match
  After:  ask "find notes about strategy" → finds relevant notes by MEANING

How it works:
  1. When you save a note → its text is converted to a vector (embedding)
     A vector is just a list of ~384 numbers that represents the meaning of the text
  2. When you search → your query is also converted to a vector
  3. ChromaDB compares vectors mathematically → returns closest matches

This is the core of RAG (Retrieval Augmented Generation):
  - Retrieval: ChromaDB finds relevant notes
  - Augmented: those notes get added to Claude's context
  - Generation: Claude answers using that context

Why this matters: keyword search finds "product strategy" if you typed those words.
Semantic search finds it even if the note says "go-to-market plan" or "competitive positioning".
"""

import chromadb
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

# Lazy-initialized — only created when first used
_client = None
_collection = None


def get_collection():
    """Get or create the ChromaDB collection."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=DB_PATH)
        _collection = _client.get_or_create_collection(
            name="notes",
            metadata={"hnsw:space": "cosine"}  # cosine similarity = compare directions of vectors
        )
    return _collection


def add_note(title: str, content: str, tags: list = None):
    """
    Embed a note and store it in ChromaDB.

    ChromaDB uses its built-in embedding model (all-MiniLM-L6-v2) to
    convert text → vector automatically. You don't call any embedding API.

    upsert = insert or update. Re-saving a note with the same title
    overwrites the old vector, keeping the index clean.
    """
    collection = get_collection()

    # Stable ID: title-based so re-saves overwrite cleanly
    doc_id = title.lower().replace(" ", "_").replace("/", "-")

    # The full text (title + content) is what gets embedded
    full_text = f"{title}\n\n{content}"

    collection.upsert(
        ids=[doc_id],
        documents=[full_text],
        metadatas=[{
            "title": title,
            "tags": ", ".join(tags or []),
            "created_at": datetime.now().isoformat()
        }]
    )


def search_notes(query: str, n_results: int = 3) -> str:
    """
    Find notes semantically similar to the query.

    The difference from keyword search:
    - "product strategy" → also finds "go-to-market", "competitive moat", "roadmap"
    - "meeting notes" → also finds "standup", "sync", "discussion"
    - "AI ideas" → also finds "machine learning", "LLM thoughts", "automation"
    """
    collection = get_collection()

    count = collection.count()
    if count == 0:
        return "No notes indexed yet. Save some notes first."

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, count)
    )

    if not results["documents"][0]:
        return "No relevant notes found."

    output = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        # Cosine distance: 0 = identical, 2 = opposite
        # Convert to a 0-100% relevance score
        relevance = round((1 - distance) * 100)
        title = meta.get("title", "Untitled")
        preview = doc[:200].replace("\n", " ")
        output.append(f"[{relevance}% match] **{title}**\n{preview}...")

    return f"Found {len(output)} semantically relevant note(s):\n\n" + "\n\n".join(output)


def remove_note(title: str):
    """Remove a note from the index when it's deleted from disk."""
    collection = get_collection()
    doc_id = title.lower().replace(" ", "_").replace("/", "-")
    try:
        collection.delete(ids=[doc_id])
    except Exception:
        pass  # Fine if it wasn't indexed
