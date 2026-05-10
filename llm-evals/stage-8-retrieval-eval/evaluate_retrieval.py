"""
evaluate_retrieval.py

Comprehensive retrieval evaluation for the eBay Live RAG pipeline.

Computes:
  - Recall@1, Recall@3, Recall@5
  - MRR (Mean Reciprocal Rank)
  - NDCG@3 (Normalized Discounted Cumulative Gain)
  - Per-chunk difficulty analysis
  - BM25 vs simple keyword matching comparison

Inputs:
  data/chunks.json     (output of chunk_knowledge_base.py)
  data/qa_pairs.json   (output of generate_qa_pairs.py)

Usage:
  python evaluate_retrieval.py
  python evaluate_retrieval.py --k 10        # use Recall@10
  python evaluate_retrieval.py --all         # include pairs that failed realism filter
"""

import argparse
import json
import math
import os
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKS_PATH = os.path.join(SCRIPT_DIR, "data", "chunks.json")
QA_PAIRS_PATH = os.path.join(SCRIPT_DIR, "data", "qa_pairs.json")


# ---------------------------------------------------------------------------
# Import retriever (works whether run from this dir or elsewhere)
# ---------------------------------------------------------------------------
sys.path.insert(0, SCRIPT_DIR)
from retriever import BM25Retriever, keyword_retrieve  # noqa: E402


# ---------------------------------------------------------------------------
# Metric implementations
# ---------------------------------------------------------------------------

def recall_at_k(ranked_ids: list[str], gold_id: str, k: int) -> float:
    """
    Recall@k: 1.0 if gold_id appears in the first k positions, else 0.0.

    In single-relevant-document retrieval, Recall@k equals Precision@k
    (it is either 0 or 1 per query). We average across queries.
    """
    return 1.0 if gold_id in ranked_ids[:k] else 0.0


def reciprocal_rank(ranked_ids: list[str], gold_id: str) -> float:
    """
    Reciprocal rank for one query: 1/rank if gold_id is found, else 0.

    rank is 1-indexed (rank 1 = first result).
    """
    for i, chunk_id in enumerate(ranked_ids, 1):
        if chunk_id == gold_id:
            return 1.0 / i
    return 0.0


def dcg_at_k(ranked_ids: list[str], gold_id: str, k: int) -> float:
    """
    Discounted Cumulative Gain at k (binary relevance: 1 if gold, 0 otherwise).

    DCG@k = Σ_{i=1}^{k}  rel_i / log2(i + 1)

    With binary relevance and a single relevant document, DCG@k simplifies to:
      1 / log2(rank + 1)  if gold_id appears in top-k, else 0
    """
    dcg = 0.0
    for i, chunk_id in enumerate(ranked_ids[:k], 1):
        if chunk_id == gold_id:
            dcg += 1.0 / math.log2(i + 1)
    return dcg


def ndcg_at_k(ranked_ids: list[str], gold_id: str, k: int) -> float:
    """
    Normalized DCG@k.

    NDCG@k = DCG@k / IDCG@k

    With a single relevant document, IDCG@k = 1/log2(2) = 1.0 (if we place
    it at rank 1). So NDCG@k = DCG@k for binary single-relevant-doc retrieval.
    """
    dcg = dcg_at_k(ranked_ids, gold_id, k)
    # IDCG = ideal case: relevant doc at rank 1
    idcg = 1.0 / math.log2(2)  # = 1.0
    if idcg == 0:
        return 0.0
    return dcg / idcg


def mean(values: list[float]) -> float:
    """Safe mean — returns 0.0 for empty lists."""
    return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# Per-query evaluation
# ---------------------------------------------------------------------------

def evaluate_pair(
    pair: dict,
    retriever: BM25Retriever,
    ks: list[int],
) -> dict:
    """
    Run retrieval for one QA pair and compute all metrics.

    Returns a result dict with:
      question, gold_chunk_id, ranked_ids, rank_of_gold,
      recall@k for each k, reciprocal_rank, ndcg@3
    """
    query = pair["question"]
    gold_id = pair["answer_chunk_id"]

    # Retrieve top-max(ks) results
    max_k = max(ks)
    results = retriever.retrieve(query, k=max_k)
    ranked_ids = [chunk["id"] for chunk, _ in results]
    ranked_scores = [score for _, score in results]

    # Find rank of gold chunk (1-indexed; 0 = not found)
    rank_of_gold = 0
    for i, cid in enumerate(ranked_ids, 1):
        if cid == gold_id:
            rank_of_gold = i
            break

    result = {
        "question": query,
        "gold_chunk_id": gold_id,
        "answer_section": pair.get("answer_section", ""),
        "question_type": pair.get("question_type", "standard"),
        "realism_score": pair.get("realism_score", 5),
        "ranked_ids": ranked_ids,
        "ranked_scores": ranked_scores,
        "rank_of_gold": rank_of_gold,
        "reciprocal_rank": reciprocal_rank(ranked_ids, gold_id),
        "ndcg_3": ndcg_at_k(ranked_ids, gold_id, 3),
    }

    for k in ks:
        result[f"recall_{k}"] = recall_at_k(ranked_ids, gold_id, k)

    return result


# ---------------------------------------------------------------------------
# Keyword baseline comparison
# ---------------------------------------------------------------------------

def evaluate_keyword_baseline(pairs: list[dict], chunks: list[dict], ks: list[int]) -> dict:
    """
    Evaluate simple keyword matching (no BM25) on the same QA pairs.
    Returns aggregate metrics for comparison.
    """
    recall_lists = {k: [] for k in ks}
    rr_list = []

    for pair in pairs:
        query = pair["question"]
        gold_id = pair["answer_chunk_id"]
        max_k = max(ks)

        results = keyword_retrieve(query, chunks, k=max_k)
        ranked_ids = [chunk["id"] for chunk, _ in results]

        for k in ks:
            recall_lists[k].append(recall_at_k(ranked_ids, gold_id, k))
        rr_list.append(reciprocal_rank(ranked_ids, gold_id))

    return {
        **{f"recall_{k}": mean(recall_lists[k]) for k in ks},
        "mrr": mean(rr_list),
    }


# ---------------------------------------------------------------------------
# Printing helpers
# ---------------------------------------------------------------------------

RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"


def found_label(rank: int, k: int) -> str:
    """Return a colored FOUND/MISS label."""
    if rank == 0:
        return f"{RED}[MISS]    {RESET}"
    if rank == 1:
        return f"{GREEN}[FOUND@1] {RESET}"
    if rank <= k:
        return f"{YELLOW}[FOUND@{rank}] {RESET}"
    return f"{RED}[MISS]    {RESET}"


def truncate(s: str, n: int) -> str:
    return s[:n] + "..." if len(s) > n else s


def print_query_table(results: list[dict], k: int) -> None:
    """Print a table showing per-query retrieval results."""
    print(f"\n{'='*72}")
    print(f"  Per-Query Results  (showing top-{k} retrieval, gold chunk in results?)")
    print(f"{'='*72}")
    print(f"  {'#':<4} {'Status':<12} {'Gold Chunk':<12} {'Section':<28} Question")
    print(f"  {'-'*68}")

    for i, r in enumerate(results, 1):
        status = found_label(r["rank_of_gold"], k)
        section = truncate(r["answer_section"], 26)
        question = truncate(r["question"], 55)
        print(f"  {i:<4} {status} {r['gold_chunk_id']:<12} {section:<28} {question}")

    print(f"  {'-'*68}")


def print_top_k_details(results: list[dict], k: int, retriever: BM25Retriever) -> None:
    """Print the top-k ranked chunks for each query."""
    print(f"\n{'='*72}")
    print(f"  Top-{k} Retrieved Chunks per Query")
    print(f"{'='*72}")

    for i, r in enumerate(results, 1):
        gold_label = f"  (gold={r['gold_chunk_id']})"
        print(f"\n  Q{i:02d}: {truncate(r['question'], 60)}{gold_label}")

        for rank, (cid, score) in enumerate(
            zip(r["ranked_ids"][:k], r["ranked_scores"][:k]), 1
        ):
            chunk = retriever.get_chunk_by_id(cid)
            section = chunk["section_name"] if chunk else cid
            is_gold = " <-- GOLD" if cid == r["gold_chunk_id"] else ""
            print(f"    #{rank}  [{cid}]  score={score:.3f}  {section}{is_gold}")


def print_aggregate_metrics(results: list[dict], ks: list[int]) -> None:
    """Print aggregate Recall@k, MRR, NDCG@3."""
    n = len(results)
    print(f"\n{'='*72}")
    print(f"  Aggregate Metrics  (N={n} queries)")
    print(f"{'='*72}")

    for k in sorted(ks):
        r_at_k = mean([r[f"recall_{k}"] for r in results])
        found = sum(1 for r in results if r[f"recall_{k}"] == 1.0)
        print(f"  Recall@{k:<3}:  {r_at_k:.3f}   ({found}/{n} queries found in top-{k})")

    mrr = mean([r["reciprocal_rank"] for r in results])
    ndcg3 = mean([r["ndcg_3"] for r in results])
    print(f"  MRR    :  {mrr:.3f}")
    print(f"  NDCG@3 :  {ndcg3:.3f}")
    print(f"{'='*72}")


def print_chunk_difficulty(results: list[dict], ks: list[int]) -> None:
    """
    For each gold chunk, compute Recall@max_k and show the hardest chunks.
    """
    max_k = max(ks)
    chunk_results: dict[str, list[float]] = defaultdict(list)

    for r in results:
        chunk_results[r["gold_chunk_id"]].append(r[f"recall_{max_k}"])

    chunk_recall = {
        cid: (mean(vals), len(vals))
        for cid, vals in chunk_results.items()
    }

    sorted_chunks = sorted(chunk_recall.items(), key=lambda x: x[1][0])

    print(f"\n{'='*72}")
    print(f"  Chunk Difficulty  (Recall@{max_k} per gold chunk)")
    print(f"{'='*72}")
    print(f"  {'Chunk ID':<12} {'Recall@'+str(max_k):<12} {'N queries':<12} Section")
    print(f"  {'-'*60}")

    # Find sections for display
    for cid, (recall, n_q) in sorted_chunks:
        section = next(
            (r["answer_section"] for r in results if r["gold_chunk_id"] == cid),
            cid,
        )
        bar = "#" * int(recall * 20)
        print(f"  {cid:<12} {recall:.2f}   [{bar:<20}]  ({n_q}q)  {section}")

    print(f"  {'-'*60}")

    # Diagnosis
    hard_chunks = [(cid, rec, nq) for cid, (rec, nq) in sorted_chunks if rec < 0.80]
    if hard_chunks:
        print(f"\n  Chunks with Recall@{max_k} < 0.80 (retrieval gaps):")
        for cid, rec, nq in hard_chunks:
            section = next(
                (r["answer_section"] for r in results if r["gold_chunk_id"] == cid),
                cid,
            )
            print(f"    {cid}  ({section}): {rec:.2f} on {nq} queries")
            print(f"    -> Consider: query expansion, synonyms, or re-chunking this section")
    else:
        print(f"\n  All chunks have Recall@{max_k} >= 0.80.")

    print(f"{'='*72}")


def print_comparison_table(
    bm25_metrics: dict,
    kw_metrics: dict,
    ks: list[int],
) -> None:
    """Print BM25 vs keyword baseline comparison."""
    print(f"\n{'='*72}")
    print(f"  BM25 vs Keyword Baseline Comparison")
    print(f"{'='*72}")
    print(f"  {'Metric':<14} {'Keyword':>10} {'BM25':>10} {'Delta':>10}")
    print(f"  {'-'*44}")

    for k in sorted(ks):
        kw = kw_metrics.get(f"recall_{k}", 0.0)
        bm = bm25_metrics.get(f"recall_{k}", 0.0)
        delta = bm - kw
        delta_str = f"+{delta:.3f}" if delta >= 0 else f"{delta:.3f}"
        print(f"  Recall@{k:<7} {kw:>10.3f} {bm:>10.3f} {delta_str:>10}")

    kw_mrr = kw_metrics.get("mrr", 0.0)
    bm_mrr = bm25_metrics.get("mrr", 0.0)
    delta_mrr = bm_mrr - kw_mrr
    delta_str = f"+{delta_mrr:.3f}" if delta_mrr >= 0 else f"{delta_mrr:.3f}"
    print(f"  {'MRR':<14} {kw_mrr:>10.3f} {bm_mrr:>10.3f} {delta_str:>10}")

    print(f"  {'-'*44}")
    print(
        f"\n  BM25 improves over keyword matching because it:\n"
        f"  - Weights rare terms more heavily (IDF)\n"
        f"  - Normalizes for document length (b parameter)\n"
        f"  - Saturates term frequency to avoid over-counting repeated words (k1)"
    )
    print(f"{'='*72}")


def print_question_type_breakdown(results: list[dict], ks: list[int]) -> None:
    """Break down metrics by question type (standard vs hard)."""
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_type[r.get("question_type", "standard")].append(r)

    if len(by_type) < 2:
        return  # Only one type, nothing to compare

    print(f"\n{'='*72}")
    print(f"  Results by Question Type")
    print(f"{'='*72}")

    for qtype, type_results in sorted(by_type.items()):
        n = len(type_results)
        max_k = max(ks)
        r_at_max = mean([r[f"recall_{max_k}"] for r in type_results])
        mrr = mean([r["reciprocal_rank"] for r in type_results])
        print(f"  {qtype:<12} N={n:<4} Recall@{max_k}={r_at_max:.3f}  MRR={mrr:.3f}")

    print(f"{'='*72}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate BM25 retrieval on synthetic QA pairs"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Maximum k for Recall@k (default: 5)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include QA pairs that failed the realism filter",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print top-k ranked chunks for each query",
    )
    args = parser.parse_args()

    ks = [1, 3, args.k]
    if args.k not in [1, 3, 5]:
        ks = sorted(set([1, 3, 5, args.k]))

    # ---------------------------------------------------------------------------
    # Load data
    # ---------------------------------------------------------------------------
    chunks_path = os.path.normpath(CHUNKS_PATH)
    qa_path = os.path.normpath(QA_PAIRS_PATH)

    if not os.path.exists(chunks_path):
        print(f"ERROR: {chunks_path} not found. Run chunk_knowledge_base.py first.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(qa_path):
        print(f"ERROR: {qa_path} not found. Run generate_qa_pairs.py first.", file=sys.stderr)
        sys.exit(1)

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(qa_path, "r", encoding="utf-8") as f:
        all_pairs = json.load(f)

    # Filter to passing pairs unless --all is set
    if args.all:
        pairs = all_pairs
    else:
        pairs = [p for p in all_pairs if p.get("passes_filter", True)]

    if not pairs:
        print(
            "No QA pairs to evaluate. If all pairs failed the realism filter,\n"
            "run with --all to include them anyway.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\n{'='*72}")
    print(f"  eBay Live Retrieval Evaluation")
    print(f"{'='*72}")
    print(f"  Chunks loaded:   {len(chunks)}")
    print(f"  QA pairs total:  {len(all_pairs)}")
    print(f"  QA pairs used:   {len(pairs)} ({'all' if args.all else 'realism >= filter'})")
    print(f"  Eval k values:   {ks}")

    # ---------------------------------------------------------------------------
    # Build retriever
    # ---------------------------------------------------------------------------
    retriever = BM25Retriever(chunks)
    retriever.index_summary()

    # ---------------------------------------------------------------------------
    # Run BM25 evaluation
    # ---------------------------------------------------------------------------
    bm25_results = [evaluate_pair(pair, retriever, ks) for pair in pairs]

    # ---------------------------------------------------------------------------
    # Print results
    # ---------------------------------------------------------------------------
    print_query_table(bm25_results, k=max(ks))

    if args.verbose:
        print_top_k_details(bm25_results, k=3, retriever=retriever)

    print_aggregate_metrics(bm25_results, ks)
    print_chunk_difficulty(bm25_results, ks)

    # ---------------------------------------------------------------------------
    # Run keyword baseline and compare
    # ---------------------------------------------------------------------------
    kw_metrics = evaluate_keyword_baseline(pairs, chunks, ks)

    bm25_agg = {
        **{f"recall_{k}": mean([r[f"recall_{k}"] for r in bm25_results]) for k in ks},
        "mrr": mean([r["reciprocal_rank"] for r in bm25_results]),
    }
    print_comparison_table(bm25_agg, kw_metrics, ks)

    # ---------------------------------------------------------------------------
    # Question type breakdown
    # ---------------------------------------------------------------------------
    print_question_type_breakdown(bm25_results, ks)

    # ---------------------------------------------------------------------------
    # Interpretation guidance
    # ---------------------------------------------------------------------------
    recall_5 = bm25_agg.get("recall_5", bm25_agg.get(f"recall_{max(ks)}", 0.0))
    mrr = bm25_agg["mrr"]

    print(f"\n{'='*72}")
    print(f"  Interpretation")
    print(f"{'='*72}")

    if recall_5 >= 0.90:
        print(f"  Recall@{max(ks)} = {recall_5:.3f}  GOOD — retriever finds the right chunk in top-{max(ks)} most of the time.")
    elif recall_5 >= 0.75:
        print(f"  Recall@{max(ks)} = {recall_5:.3f}  MODERATE — consider re-chunking or query expansion.")
    else:
        print(f"  Recall@{max(ks)} = {recall_5:.3f}  LOW — retriever is missing relevant chunks often.")
        print(f"  Action: check hard chunks above, consider embedding-based retrieval.")

    if mrr >= 0.70:
        print(f"  MRR = {mrr:.3f}  GOOD — the right chunk is typically ranked near the top.")
    else:
        print(f"  MRR = {mrr:.3f}  MODERATE — consider adding a reranking stage (Stage 2).")

    gap = recall_5 - mean([r["recall_1"] for r in bm25_results])
    if gap > 0.20:
        print(
            f"  Large Recall@1 → Recall@{max(ks)} gap ({gap:.2f}): retriever finds the right chunk"
            f" but does not rank it first.\n"
            f"  A reranking stage would likely improve MRR and answer quality."
        )

    print(f"\n  Next steps from Ch7 §7.6:")
    print(f"  1. Inspect questions where the retriever missed (MISS above)")
    print(f"  2. Check whether missed queries use terminology not in the chunk")
    print(f"  3. Consider adding a dense retrieval stage for semantic matching")
    print(f"  4. Add more diverse real-user queries to avoid overfitting to synthetic data")
    print(f"{'='*72}\n")


if __name__ == "__main__":
    main()
