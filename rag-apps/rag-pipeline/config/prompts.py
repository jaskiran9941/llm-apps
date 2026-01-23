"""
Prompt templates for RAG system.

This module contains all prompt templates used for LLM generation.
Having prompts in one place makes them easy to iterate on and improve.
"""

from typing import List
from src.models import RetrievedChunk


# ==================== System Prompts ====================

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on provided context.

Your responsibilities:
1. Answer questions accurately using ONLY the information in the provided context
2. If the context doesn't contain enough information, clearly state this
3. Always cite the source document and page number when referencing information
4. Be concise but comprehensive
5. If multiple chunks provide relevant information, synthesize them into a coherent answer

Important rules:
- DO NOT make up information not present in the context
- DO NOT use your general knowledge unless explicitly asked
- Always indicate source citations in your response
- If uncertain, acknowledge the limitations of the available context
"""


# ==================== RAG Prompt Templates ====================

RAG_PROMPT_TEMPLATE = """Based on the following context from the knowledge base, please answer the user's question.

Context:
{context}

Question: {query}

Instructions:
- Answer based ONLY on the context provided above
- Cite sources using the format: [Source: filename, Page: X]
- If the context doesn't contain the answer, say "I don't have enough information in the provided documents to answer this question."
- Be specific and use direct quotes when appropriate

Answer:"""


NO_RAG_PROMPT_TEMPLATE = """Please answer the following question using your general knowledge:

Question: {query}

Answer:"""


# ==================== Context Formatting ====================

def format_context(retrieved_chunks: List[RetrievedChunk]) -> str:
    """
    Format retrieved chunks into a context string for the LLM.

    This function converts the list of retrieved chunks into a single
    formatted string that provides clear separation between different
    sources and includes relevant metadata.

    Args:
        retrieved_chunks: List of retrieved chunks with metadata

    Returns:
        Formatted context string

    Example output:
        ---
        [Document: example.pdf, Page: 3, Relevance: 0.89]
        This is the content of the first chunk...

        ---
        [Document: example.pdf, Page: 5, Relevance: 0.85]
        This is the content of the second chunk...
    """
    if not retrieved_chunks:
        return "No relevant context found."

    context_parts = []

    for i, chunk in enumerate(retrieved_chunks, 1):
        # Create header with source information
        page_info = f"Page: {chunk.page_number}" if chunk.page_number else "Page: Unknown"
        header = f"[Document: {chunk.source_document}, {page_info}, Relevance: {chunk.score:.2f}]"

        # Format the chunk
        chunk_text = f"---\n{header}\n{chunk.text}\n"
        context_parts.append(chunk_text)

    return "\n".join(context_parts)


def construct_rag_prompt(query: str, retrieved_chunks: List[RetrievedChunk]) -> str:
    """
    Construct the complete RAG prompt with context.

    Args:
        query: User's question
        retrieved_chunks: Retrieved chunks to use as context

    Returns:
        Complete prompt string ready for the LLM
    """
    context = format_context(retrieved_chunks)
    return RAG_PROMPT_TEMPLATE.format(context=context, query=query)


def construct_no_rag_prompt(query: str) -> str:
    """
    Construct a prompt without RAG context (for comparison).

    Args:
        query: User's question

    Returns:
        Prompt string without context
    """
    return NO_RAG_PROMPT_TEMPLATE.format(query=query)


# ==================== Educational Prompts ====================

EXPLAIN_RAG_SYSTEM_PROMPT = """You are an educational AI assistant explaining how RAG systems work.
Use simple language and concrete examples. Break down complex concepts into understandable parts."""


CHUNK_SIZE_EXPLANATION = """
Chunk size is a critical parameter in RAG systems:

**Small chunks (100-300 tokens):**
- ✅ Pros: More precise retrieval, exactly relevant text
- ❌ Cons: Less context, may miss related information, more chunks = higher cost

**Medium chunks (300-700 tokens):**
- ✅ Pros: Good balance of precision and context
- ❌ Cons: May include some irrelevant text
- 💡 Recommended for most use cases

**Large chunks (700-1500 tokens):**
- ✅ Pros: Maximum context, captures full ideas
- ❌ Cons: Less precise retrieval, may include noise, higher cost

**Overlap:**
Overlap between chunks helps maintain context across boundaries. Typical values are 10-20% of chunk size.
"""


SIMILARITY_SCORE_EXPLANATION = """
Similarity scores indicate how well a chunk matches your query:

**Score ranges (cosine similarity):**
- 0.9-1.0: Excellent match - highly relevant
- 0.8-0.9: Good match - relevant content
- 0.7-0.8: Moderate match - somewhat relevant
- 0.6-0.7: Weak match - marginally relevant
- <0.6: Poor match - likely not relevant

The retrieval threshold determines the minimum score required to include a chunk.
Lower thresholds give more results but may include noise.
"""
