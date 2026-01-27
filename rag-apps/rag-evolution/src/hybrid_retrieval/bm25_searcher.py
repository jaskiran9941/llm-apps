"""
BM25 keyword-based search
"""
from typing import List
from rank_bm25 import BM25Okapi
import nltk
from ..common.models import Chunk, RetrievalResult

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class BM25Searcher:
    """Keyword-based search using BM25 algorithm"""

    def __init__(self):
        self.bm25 = None
        self.chunks = []
        self.tokenized_corpus = []

    def index_chunks(self, chunks: List[Chunk]):
        """Index chunks for BM25 search"""
        self.chunks = chunks

        # Tokenize corpus
        self.tokenized_corpus = [
            self._tokenize(chunk.content) for chunk in chunks
        ]

        # Create BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        """Search using BM25"""
        if not self.bm25:
            return []

        # Tokenize query
        tokenized_query = self._tokenize(query)

        # Get scores
        scores = self.bm25.get_scores(tokenized_query)

        # Get top k indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        # Create results
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            result = RetrievalResult(
                content=chunk.content,
                score=float(scores[idx]),
                chunk_id=chunk.chunk_id,
                page=chunk.page,
                result_type="text",
                metadata={
                    **chunk.metadata,
                    "retrieval_method": "bm25"
                }
            )
            results.append(result)

        return results

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25"""
        # Simple word tokenization
        tokens = nltk.word_tokenize(text.lower())
        # Remove punctuation
        tokens = [t for t in tokens if t.isalnum()]
        return tokens

    def count(self) -> int:
        """Get number of indexed chunks"""
        return len(self.chunks)
