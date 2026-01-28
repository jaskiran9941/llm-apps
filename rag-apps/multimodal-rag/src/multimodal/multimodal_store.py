"""
Unified vector store for multimodal RAG (text, images, tables, audio).
Uses simple in-memory store for Python 3.14 compatibility.
"""

from .simple_store import SimpleVectorStore as MultimodalStore

# Re-export for compatibility
__all__ = ['MultimodalStore']
