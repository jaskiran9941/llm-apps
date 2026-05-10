"""
retriever.py

BM25 retrieval over the chunked eBay Live knowledge base.

BM25 (Best Match 25) is the industry-standard first-pass retrieval algorithm.
It extends TF-IDF with:
  - Term frequency saturation (k1): repeated terms add diminishing returns
  - Length normalization (b): short documents are not penalised for not repeating terms

Formula:
  BM25(q, d) = Σ_{t in q}  IDF(t) * tf(t,d) * (k1 + 1)
                                     ─────────────────────────────────────────────
                                     tf(t,d) + k1 * (1 - b + b * |d| / avgdl)

  IDF(t) = log((N - df_t + 0.5) / (df_t + 0.5) + 1)

Where:
  tf(t,d)  = count of term t in document d
  df_t     = number of documents containing term t
  N        = total number of documents
  |d|      = length of document d (in tokens)
  avgdl    = average document length across all documents
  k1       = term frequency saturation (default 1.5)
  b        = length normalization (default 0.75)

Usage:
  from retriever import BM25Retriever
  r = BM25Retriever.from_file("data/chunks.json")
  results = r.retrieve("How does bidding work?", k=5)
  for rank, (chunk, score) in enumerate(results, 1):
      print(rank, chunk["section_name"], score)
"""

import json
import math
import os
import re
import sys
from collections import Counter
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CHUNKS_PATH = os.path.join(SCRIPT_DIR, "data", "chunks.json")


# ---------------------------------------------------------------------------
# Text preprocessing
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    """
    Lowercase and split text into word tokens.

    We use a simple regex that keeps alphanumeric characters and strips
    punctuation. We also strip common stopwords so BM25 focuses on
    content-bearing terms.

    In production you would use a proper tokenizer (e.g., NLTK) and
    a more comprehensive stopword list.
    """
    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "it", "its", "are",
        "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "may",
        "can", "that", "this", "these", "those", "i", "you", "we", "they",
        "he", "she", "not", "if", "as", "so", "what", "how", "when",
        "which", "who", "your", "my", "their", "our", "about",
    }
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


# ---------------------------------------------------------------------------
# BM25 implementation
# ---------------------------------------------------------------------------

def bm25_score(
    query_terms: list[str],
    doc_terms: list[str],
    doc_lengths: list[int],
    avg_doc_len: float,
    df: dict[str, int],
    n_docs: int,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """
    Compute the BM25 score for a single (query, document) pair.

    Parameters
    ----------
    query_terms   : tokenized query
    doc_terms     : tokenized document
    doc_lengths   : list of all document lengths (used for avg_doc_len check)
    avg_doc_len   : average document length in the corpus
    df            : document frequency dict — df[term] = count of docs containing term
    n_docs        : total number of documents in the corpus
    k1            : term frequency saturation parameter (default 1.5)
    b             : length normalization parameter (default 0.75)

    Returns
    -------
    float: BM25 relevance score (higher = more relevant)
    """
    score = 0.0
    doc_len = len(doc_terms)
    term_freq = Counter(doc_terms)

    for term in set(query_terms):  # de-duplicate query terms
        if term not in term_freq:
            continue

        tf = term_freq[term]
        df_t = df.get(term, 0)

        # Robertson-Sparck Jones IDF (smooth variant)
        idf = math.log((n_docs - df_t + 0.5) / (df_t + 0.5) + 1)

        # BM25 TF component with length normalization
        tf_component = (tf * (k1 + 1)) / (
            tf + k1 * (1 - b + b * doc_len / avg_doc_len)
        )

        score += idf * tf_component

    return score


class BM25Retriever:
    """
    BM25 retriever for a fixed collection of text chunks.

    Attributes
    ----------
    chunks      : list of chunk dicts (id, section_name, content, ...)
    doc_tokens  : tokenized version of each chunk's content
    df          : document frequency table
    avg_doc_len : average document length across chunks
    """

    def __init__(self, chunks: list[dict], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b

        # Tokenize all chunks
        self.doc_tokens: list[list[str]] = [
            tokenize(c["content"]) for c in chunks
        ]

        # Document lengths
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_len = (
            sum(self.doc_lengths) / len(self.doc_lengths)
            if self.doc_lengths
            else 1.0
        )

        # Document frequency table
        self.df: dict[str, int] = {}
        for tokens in self.doc_tokens:
            for term in set(tokens):
                self.df[term] = self.df.get(term, 0) + 1

        self.n_docs = len(chunks)

    @classmethod
    def from_file(cls, path: str = DEFAULT_CHUNKS_PATH, **kwargs) -> "BM25Retriever":
        """Load chunks from a JSON file and create a BM25Retriever."""
        path = os.path.normpath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"chunks.json not found at:\n  {path}\n"
                "Run chunk_knowledge_base.py first."
            )
        with open(path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        return cls(chunks, **kwargs)

    def retrieve(
        self,
        query: str,
        k: int = 5,
        return_scores: bool = True,
    ) -> list[tuple[dict, float]]:
        """
        Retrieve the top-k most relevant chunks for a query.

        Parameters
        ----------
        query         : the user's query string
        k             : number of results to return
        return_scores : if True, return (chunk, score) tuples

        Returns
        -------
        List of (chunk_dict, bm25_score) tuples, sorted by score descending.
        """
        query_terms = tokenize(query)

        if not query_terms:
            # Empty query — return nothing
            return []

        scores = []
        for i, doc_tokens in enumerate(self.doc_tokens):
            s = bm25_score(
                query_terms=query_terms,
                doc_terms=doc_tokens,
                doc_lengths=self.doc_lengths,
                avg_doc_len=self.avg_doc_len,
                df=self.df,
                n_docs=self.n_docs,
                k1=self.k1,
                b=self.b,
            )
            scores.append((self.chunks[i], s))

        # Sort by score descending, then by chunk id for stable ties
        scores.sort(key=lambda x: (-x[1], x[0]["id"]))
        return scores[:k]

    def get_chunk_by_id(self, chunk_id: str) -> Optional[dict]:
        """Return the chunk dict for a given chunk_id, or None."""
        for chunk in self.chunks:
            if chunk["id"] == chunk_id:
                return chunk
        return None

    def index_summary(self) -> None:
        """Print a summary of the BM25 index."""
        print(f"BM25 Index Summary")
        print(f"  Documents:       {self.n_docs}")
        print(f"  Vocabulary size: {len(self.df)} unique terms")
        print(f"  Avg doc length:  {self.avg_doc_len:.1f} tokens (after stopword removal)")
        print(f"  k1={self.k1}, b={self.b}")


# ---------------------------------------------------------------------------
# Simple keyword baseline (for comparison in evaluate_retrieval.py)
# ---------------------------------------------------------------------------

def keyword_retrieve(
    query: str,
    chunks: list[dict],
    k: int = 5,
) -> list[tuple[dict, float]]:
    """
    Naive keyword matching: score = number of query words found in chunk content.
    No IDF weighting, no length normalization.

    This is the baseline we compare BM25 against.
    """
    query_words = set(tokenize(query))
    scores = []
    for chunk in chunks:
        chunk_words = set(tokenize(chunk["content"]))
        overlap = len(query_words & chunk_words)
        scores.append((chunk, float(overlap)))
    scores.sort(key=lambda x: (-x[1], x[0]["id"]))
    return scores[:k]


# ---------------------------------------------------------------------------
# Demo when run as a script
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("BM25 Retriever Demo")
    print("=" * 65)
    print()

    retriever = BM25Retriever.from_file()
    retriever.index_summary()
    print()

    sample_queries = [
        "What happens if someone bids right before an auction closes?",
        "What internet speed do I need to go live?",
        "Can buyers from the UK participate in eBay Live?",
        "What fees do sellers pay when an item sells?",
        "What categories can I sell on eBay Live?",
        "How are buyers protected if an item doesn't arrive?",
        "What platforms compete with eBay Live?",
        "How often should I broadcast to build an audience?",
    ]

    for query in sample_queries:
        print(f"Query: \"{query}\"")
        results = retriever.retrieve(query, k=3)
        for rank, (chunk, score) in enumerate(results, 1):
            print(f"  #{rank}  [{chunk['id']}]  score={score:.3f}  {chunk['section_name']}")
        print()
