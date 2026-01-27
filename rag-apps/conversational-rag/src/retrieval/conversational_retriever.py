"""
Conversational retrieval with query enhancement
"""
from typing import List
from ..models import ConversationHistory, RetrievalResult
from .vector_search import VectorSearch
from .bm25_search import BM25Searcher
from .hybrid_fusion import HybridFusion


class ConversationalQueryEnhancer:
    """Enhance queries using conversation context"""

    def enhance(self, query: str, history: ConversationHistory) -> str:
        """
        Enhance query with context from history

        Examples:
        - "tell me more" -> "tell me more about [previous topic]"
        - "what else?" -> "what else about [previous context]?"
        - "clarify that" -> uses last assistant message as context
        """
        if not self._is_followup_query(query):
            return query

        # Get recent context
        recent_messages = history.get_last_n_messages(3)

        if not recent_messages:
            return query

        # Build enhanced query using simple rule-based approach
        enhanced = self._build_enhanced_query(query, recent_messages)
        return enhanced

    def _is_followup_query(self, query: str) -> bool:
        """Check if query is a follow-up"""
        followup_patterns = [
            "tell me more", "what else", "clarify", "explain that",
            "what about", "and?", "continue", "more details",
            "what do you mean", "elaborate", "expand on",
            "go on", "keep going", "anything else", "what's that",
            "how so", "why is that", "how does that work"
        ]
        query_lower = query.lower().strip()

        # Check for exact matches or partial matches
        for pattern in followup_patterns:
            if pattern in query_lower:
                return True

        # Check for very short queries (likely follow-ups)
        if len(query.split()) <= 3 and any(
            word in query_lower for word in ["more", "else", "that", "what", "how", "why"]
        ):
            return True

        return False

    def _build_enhanced_query(
        self,
        query: str,
        recent_messages: List
    ) -> str:
        """Build enhanced query with context"""
        # Get the last user query and assistant response
        last_user_query = None
        last_assistant_response = None

        for msg in reversed(recent_messages):
            if msg.role == "user" and last_user_query is None:
                last_user_query = msg.content
            elif msg.role == "assistant" and last_assistant_response is None:
                last_assistant_response = msg.content

            if last_user_query and last_assistant_response:
                break

        # Build enhanced query
        context_parts = []

        if last_user_query:
            context_parts.append(f"Previous question: {last_user_query}")

        # Combine with current query
        if context_parts:
            enhanced = f"{' '.join(context_parts)}. Current question: {query}"
            return enhanced

        return query


class ConversationalRetriever:
    """Retrieve chunks with conversation context"""

    def __init__(
        self,
        vector_search: VectorSearch,
        bm25_search: BM25Searcher,
        fusion: HybridFusion = None
    ):
        self.vector_search = vector_search
        self.bm25_search = bm25_search
        self.fusion = fusion or HybridFusion()
        self.query_enhancer = ConversationalQueryEnhancer()

    def retrieve(
        self,
        query: str,
        conversation_history: ConversationHistory,
        k: int = 5,
        alpha: float = 0.5
    ) -> List[RetrievalResult]:
        """
        Retrieve with conversation context

        Steps:
        1. Enhance query using conversation history
        2. Perform hybrid retrieval (semantic + keyword)
        3. Fuse and return top-k results
        """
        # Enhance query if needed
        enhanced_query = self.query_enhancer.enhance(query, conversation_history)

        # Hybrid retrieval - get more results for better fusion
        retrieval_k = k * 2

        semantic_results = self.vector_search.search(enhanced_query, k=retrieval_k)
        keyword_results = self.bm25_search.search(enhanced_query, k=retrieval_k)

        # Reciprocal Rank Fusion
        fused_results = self.fusion.fuse(
            semantic_results,
            keyword_results,
            alpha=alpha
        )

        return fused_results[:k]
