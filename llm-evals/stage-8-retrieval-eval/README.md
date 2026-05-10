# Stage 6 — Retrieval Eval (RAG)

**Book reference**: "Application-Centric AI Evals for Engineers and Technical Product Managers"  
by Shankar & Husain (2026) — Chapter 7: Evaluating Retrieval-Augmented Generation

---

## The Problem This Stage Solves

The eBay Live chatbot currently has its entire knowledge base baked into the system prompt. Every API call sends all 600+ words of policy text to the model, whether it is relevant or not. This is fine for a small knowledge base, but it does not scale.

In a production RAG system you would:

1. Store the knowledge base as indexed chunks
2. At query time, retrieve only the chunks relevant to the user's question
3. Pass only those chunks in the system prompt

This raises a new question: **how do you know the retriever is finding the right chunks?**

That is what this stage teaches you to measure.

---

## 1. Why Evaluate Retrieval Independently

The most important principle in Chapter 7 is this:

> "We start by evaluating the retrieval component on its own. Before we assess the quality of generated answers, we need to verify that the system consistently finds the right context."

Here is why this matters. Suppose your end-to-end chatbot scores 62% on answer correctness. Should you improve the retriever or the generator? A single end-to-end score cannot tell you. But if you measure retrieval independently and get Recall@5 = 0.55, you know immediately that the retriever is missing relevant chunks on nearly half of queries — and no amount of prompt engineering will fix that.

The diagnostic framework from Chapter 7:

```
End-to-end score is low
        │
        ├── Is Recall@5 low?  → Yes → Fix the retriever (chunking, indexing, query expansion)
        │
        └── Is Recall@5 high? → Yes → Fix the generator (prompt, model, context formatting)
```

Retrieval failures are silent. If the right chunk is not in the top-k results, the LLM never sees the relevant information. It may hallucinate, or politely say "I don't know." Either way, the root cause is retrieval, not generation.

---

## 2. The Two-Stage RAG Pipeline (Ch7 §7.1)

Production RAG systems use two retrieval stages:

```
User query
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Stage 1: First-pass Retrieval (High Recall)        │
│                                                      │
│  Method: BM25 or embedding similarity               │
│  Goal:   Don't miss relevant chunks                  │
│  Speed:  Fast (milliseconds)                         │
│  Typical k: 20-100 candidates                        │
│  Metric:  Recall@k                                   │
└─────────────────────────────────────────────────────┘
    │
    ▼ top-k candidates
┌─────────────────────────────────────────────────────┐
│  Stage 2: Reranking (High Precision)                │
│                                                      │
│  Method: Cross-encoder, LLM-based reranker          │
│  Goal:   Rank the best chunk first                   │
│  Speed:  Slower (100ms-2s)                           │
│  Typical k: 3-5 final chunks                         │
│  Metric:  MRR, NDCG@k                               │
└─────────────────────────────────────────────────────┘
    │
    ▼ top-3 final chunks
┌─────────────────────────────────────────────────────┐
│  LLM Generation                                      │
│                                                      │
│  The retrieved chunks are injected into the prompt  │
│  The LLM synthesizes an answer from them            │
└─────────────────────────────────────────────────────┘
```

The key insight is that **each stage has a different job** and therefore a different evaluation metric:

- Stage 1 must have **high recall** — if the relevant chunk is not in the candidate set, Stage 2 cannot recover it. We measure Recall@k.
- Stage 2 must have **high precision at rank 1** — the best chunk should be ranked first so it appears prominently in the LLM's context. We measure MRR and NDCG@k.

For this eBay Live eval, we implement Stage 1 only (BM25 retrieval) and measure Recall@k, MRR, and NDCG@k across all queries.

---

## 3. What a Chunk Is

A **chunk** is a contiguous span of text used as the retrieval unit. When a user asks a question, the retriever returns the top-k chunks — not the entire document.

Chunk design is one of the most consequential decisions in RAG. The same LLM with the same prompt will give dramatically different answers depending on whether the retriever returns the right chunk.

### Chunking Strategies

**Fixed-size windows** split text every N tokens with optional overlap:
```
[token 0 ... token 512]
                   [token 462 ... token 974]
                                       [token 924 ... token 1436]
```
Simple to implement. Chunks may cut mid-sentence or mid-paragraph, scattering related information.

**Semantic / section-based** splitting respects document structure (headers, paragraphs, sections):
```
## How It Works for Buyers       ← chunk 1 boundary
...buyer content...
## Buyer Protections              ← chunk 2 boundary
...protections content...
```
More natural. Chunks align with the author's intent. Better suited to structured documents like policy files.

**Hierarchical** chunking stores both a large parent chunk and smaller child chunks. Retrieval runs on children; context expands to the parent for generation.

### The eBay Live Knowledge Base Chunks

The system prompt is organized by `##` section headers. We split on those headers to create 10 natural chunks:

| chunk_id | section_name                    | word_count |
|----------|---------------------------------|------------|
| chunk_00 | What is eBay Live?              | ~45        |
| chunk_01 | Availability                    | ~22        |
| chunk_02 | Available Categories            | ~50        |
| chunk_03 | How It Works for Buyers         | ~145       |
| chunk_04 | Buyer Protections               | ~55        |
| chunk_05 | How It Works for Sellers        | ~100       |
| chunk_06 | Shipping & Fulfillment          | ~50        |
| chunk_07 | Technical Requirements          | ~45        |
| chunk_08 | Seller Tips for Success         | ~95        |
| chunk_09 | Competitive Landscape           | ~35        |

This section-based approach is natural for the eBay Live knowledge base because each section covers a distinct topic. A question about bidding rules maps cleanly to chunk_03. A question about fees maps to chunk_05. There is minimal overlap between sections.

### How Chunk Size Affects Recall@k

Chunk size creates a fundamental tradeoff:

**Chunks too small** (e.g., single sentences):
- Pro: precise retrieval, less noise in LLM context
- Con: facts that require multiple sentences to understand are scattered across chunks; a query about "how auctions work" needs 8+ chunks

**Chunks too large** (e.g., entire document):
- Pro: Recall@1 is trivially 1.0 (there is only one chunk)
- Con: the LLM context is flooded with irrelevant text, degrading generation quality; this is just the original problem

**Section-based chunks** for eBay Live:
- Each section is ~30-150 words
- Small enough to be topically coherent
- Large enough to contain complete explanations
- Natural alignment with document structure

A practical way to choose chunk size: run your retrieval eval at multiple chunk sizes and pick the size that maximizes Recall@5 while keeping individual chunk sizes below your context budget.

---

## 4. Synthetic QA Generation (Ch7 §7.2)

To evaluate retrieval, you need labeled pairs: (query, gold_chunk_id). The gold chunk is the chunk that contains the correct answer to the query.

In most real deployments, you do not have these labels. Users do not annotate which document answered their question. Chapter 7 addresses this directly:

> "Generate synthetic evaluation datasets by prompting an LLM to write questions that can only be answered by a specific chunk."

### The Two-Step Generation Process

**Step 1: Extract a fact**

Ask the LLM to extract a specific, verifiable fact from a chunk:

```
Given this chunk from the eBay Live knowledge base:

{chunk_content}

Extract one specific, verifiable fact from this chunk. The fact should be:
- A concrete piece of information (a number, a rule, a requirement)
- Not vague or general
- Something a user could specifically ask about

Respond with just the fact as a single sentence.
```

Example output for chunk_03 (How It Works for Buyers):
> "If a bid is placed in the last 5 seconds of an auction, the timer extends by 5 more seconds."

**Step 2: Write a discriminative question**

Now write a question that is ONLY answerable by that specific fact — not by other chunks:

```
You extracted this fact from a chunk about "{section_name}":

Fact: {fact}

Write a realistic customer support question that:
1. Can ONLY be answered using this exact fact
2. Sounds like something a real eBay Live user would ask
3. Does NOT mention the section name or obvious keywords from the fact
4. Would be HARD to answer from other sections of the knowledge base

The question should be discriminative — a retriever should need the specific chunk
containing this fact to answer it correctly.

Respond with just the question.
```

Example output:
> "What happens if someone places a bid right before an auction closes?"

This is a good discriminative question because:
- It requires the soft-close rule from chunk_03
- It does NOT contain the phrase "5 seconds" or "soft close"
- It sounds like a real user question
- It could plausibly relate to other chunks (sellers, auctions) but only chunk_03 has the answer

### Hard Negatives

Chapter 7 also recommends generating "hard negative" questions — questions whose surface form resembles multiple chunks but only has one correct answer. For example:

> "Do sellers have to pay fees when items sell in an auction?"

This question contains words that appear in chunk_03 (buyers), chunk_05 (sellers), and chunk_06 (shipping), but the correct answer is only in chunk_05 (final value fees). A retriever that relies on simple keyword overlap may return chunk_03 or chunk_06 instead of chunk_05.

Hard negatives stress-test the retriever's ability to distinguish between topically similar chunks.

### Filtering with Realism Scoring

Not all generated questions are good. Some are too extractive (they copy words directly from the chunk), too vague, or unrealistic. Chapter 7 recommends a filtering step:

```
Score this question on a 1-5 scale for how realistic it is as a customer support question:

1 = Clearly machine-generated, no real user would ask this
2 = Awkward phrasing, unlikely
3 = Plausible but stilted
4 = Realistic, sounds like a real user
5 = Highly realistic, could appear in a real support queue

Question: {question}

Respond with just the number.
```

Keep questions with score >= 4. This filters out extractive questions like "What is the minimum upload speed for sellers?" (too close to the source text) while keeping naturalistic ones like "My stream keeps dropping — what internet speed do I need?"

---

## 5. Retrieval Metrics (Ch7 §7.3)

Once you have (query, gold_chunk_id) pairs and a retriever, you can compute retrieval metrics. Each metric captures a different aspect of retrieval quality.

### Recall@k

**Definition**: The fraction of queries for which the gold chunk appears in the top-k results.

```
Recall@k = (number of queries where gold_chunk_id ∈ top-k results)
           ────────────────────────────────────────────────────────
                            total queries
```

**Example** with k=3 and 5 queries:

| Query | Gold chunk | Top-3 returned                | In top-3? |
|-------|------------|-------------------------------|-----------|
| Q1    | chunk_03   | [chunk_03, chunk_05, chunk_01] | Yes       |
| Q2    | chunk_05   | [chunk_01, chunk_03, chunk_07] | No        |
| Q3    | chunk_01   | [chunk_01, chunk_09, chunk_02] | Yes       |
| Q4    | chunk_07   | [chunk_07, chunk_05, chunk_03] | Yes       |
| Q5    | chunk_03   | [chunk_09, chunk_01, chunk_06] | No        |

Recall@3 = 3/5 = 0.60

**Why it matters for RAG**: In Stage 1 retrieval (first-pass), your primary goal is not to miss relevant chunks. If the gold chunk is not in the top-k candidates you pass to Stage 2 (or directly to the LLM), generation will fail regardless of how good your generator is. Recall@k directly measures this risk.

**Typical targets**:
- Recall@1: >= 0.70 (the right chunk is the top result most of the time)
- Recall@3: >= 0.85
- Recall@5: >= 0.90

**Limitation**: Recall@k treats all positions in the top-k equally. A system that always puts the gold chunk at rank k and a system that always puts it at rank 1 have the same Recall@k — but the first one is much worse in practice.

### MRR (Mean Reciprocal Rank)

**Definition**: The average of 1/rank(first_relevant_result) across all queries.

```
MRR = (1/N) × Σᵢ (1 / rank_i)
```

Where rank_i is the rank of the first relevant chunk for query i (1-indexed).

**Example** continuing from above:

| Query | Gold chunk rank | 1/rank |
|-------|----------------|--------|
| Q1    | 1              | 1.000  |
| Q2    | not found      | 0.000  |
| Q3    | 1              | 1.000  |
| Q4    | 1              | 1.000  |
| Q5    | not found      | 0.000  |

MRR = (1.000 + 0.000 + 1.000 + 1.000 + 0.000) / 5 = 0.600

**Why it matters**: MRR rewards systems that rank the relevant chunk first. It penalizes a system that finds the right chunk but ranks it 3rd instead of 1st — even though Recall@3 would count both the same way.

**When to use MRR**: Queries with a single correct answer. For example:
- "What is the final value fee percentage?" → exactly one chunk has the answer
- "What countries does eBay Live support?" → exactly one chunk has the answer

**Limitation**: MRR only considers the rank of the FIRST relevant result. If a query has multiple relevant chunks, MRR only looks at the one that appears earliest in the ranking.

### NDCG@k (Normalized Discounted Cumulative Gain)

**Definition**: A metric that rewards placing more relevant chunks higher in the ranking. It handles graded relevance (some chunks are more relevant than others).

```
DCG@k = Σᵢ₌₁ᵏ  rel_i / log₂(i + 1)

NDCG@k = DCG@k / IDCG@k
```

Where:
- `rel_i` = relevance score of the chunk at rank i (0 or 1 in binary case; could be 0/1/2 with graded relevance)
- `IDCG@k` = the ideal DCG@k (what you would get if all relevant chunks were ranked first)
- Dividing by IDCG normalizes the score to [0, 1]

**Example** with graded relevance (chunk_03 = 2 points, chunk_05 = 1 point, others = 0):

Retriever returns: [chunk_05, chunk_03, chunk_01, chunk_07, chunk_09]

```
DCG@3 = 1/log₂(2) + 2/log₂(3) + 0/log₂(4)
      = 1/1.0 + 2/1.585 + 0
      = 1.000 + 1.262
      = 2.262

IDCG@3 = 2/log₂(2) + 1/log₂(3) + 0/log₂(4)
       = 2/1.0 + 1/1.585
       = 2.000 + 0.631
       = 2.631

NDCG@3 = 2.262 / 2.631 = 0.860
```

**Why it matters**: NDCG@k is the right metric when chunks have graded relevance. For example, when answering "How do I start selling on eBay Live?", chunk_05 (How It Works for Sellers) is highly relevant, chunk_08 (Seller Tips) is somewhat relevant, and chunk_07 (Technical Requirements) is marginally relevant. NDCG@k captures the quality of the entire ranking, not just whether one chunk appeared.

**When to use NDCG@k**: Multi-faceted questions that benefit from multiple chunks. For example:
- "What do I need to start selling on eBay Live?" (eligibility + technical requirements + tips)
- "How are buyers protected?" (protections + payment rules + return policy)

### Summary: When to Use Each Metric

| Metric    | Use when...                                          | Stage           |
|-----------|------------------------------------------------------|-----------------|
| Recall@k  | You want to know if the right chunk is retrieved at all | Stage 1 (first-pass) |
| MRR       | Each query has exactly one correct chunk             | Stage 2 (reranking)  |
| NDCG@k    | Chunks have graded relevance; ranking quality matters | Stage 2 (reranking)  |

In practice, report all three. Recall@5 tells you if your retrieval architecture is fundamentally sound. MRR and NDCG@3 tell you if the ranking quality is good enough for generation.

---

## 6. BM25 Retrieval

BM25 (Best Match 25) is the most widely used first-pass retrieval algorithm. It is a probabilistic extension of TF-IDF that accounts for document length normalization and term frequency saturation.

### BM25 Formula

```
BM25(q, d) = Σ_{t ∈ q}  IDF(t) × [ tf(t,d) × (k1 + 1) ]
                                    ───────────────────────────────────────────
                                    [ tf(t,d) + k1 × (1 - b + b × |d|/avgdl) ]
```

Where:
- `tf(t, d)` = term frequency of term t in document d
- `IDF(t)` = inverse document frequency: log((N - df + 0.5) / (df + 0.5))
- `|d|` = length of document d (in tokens)
- `avgdl` = average document length across the corpus
- `k1` = term frequency saturation parameter (typically 1.2–2.0)
- `b` = length normalization parameter (typically 0.75)

### Why k1 and b Matter

**k1** controls term frequency saturation. With k1=1.5, a term appearing 10 times adds almost the same score as a term appearing 5 times. Higher k1 gives more weight to repeated terms.

**b** controls length normalization. With b=0.75, longer documents are penalized — a term appearing once in a short document scores higher than the same term appearing once in a long document (because it is more "concentrated"). b=0 turns off length normalization; b=1 fully normalizes by length.

For the eBay Live knowledge base, our chunks have very different lengths (chunk_01 has ~22 words; chunk_03 has ~145 words). Without length normalization (b=0.75), a term match in the short "Availability" chunk would unfairly dominate a match in the longer "How It Works for Buyers" chunk.

### Why BM25 Over Embeddings Here

Embedding-based retrieval (dense retrieval) is powerful for semantic matching — finding chunks that are conceptually related to a query even without keyword overlap. However, for structured factual knowledge bases like eBay Live policy:

- Queries tend to use specific terminology that appears verbatim in the KB
- The KB is small (~10 chunks), making the ranking problem easy
- BM25 is interpretable: you can see exactly which terms drove the score
- BM25 requires no GPU, no embedding model, no API calls

In production with a larger, more diverse knowledge base, you would add a dense retrieval stage alongside BM25 and combine their scores (hybrid retrieval).

---

## 7. The Evaluation Pipeline End-to-End

Here is the complete pipeline implemented in this stage:

```
system_prompt.md
     │
     ▼  chunk_knowledge_base.py
data/chunks.json          (10 section-based chunks)
     │
     ▼  generate_qa_pairs.py
data/qa_pairs.json        (~20-30 synthetic query/gold_chunk pairs)
     │
     ▼  evaluate_retrieval.py
                          ┌──────────────────────────────────────┐
                          │  For each query in qa_pairs.json:    │
                          │  1. Run BM25 retrieval (top-5)       │
                          │  2. Check if gold_chunk in top-k     │
                          │  3. Record rank of gold_chunk        │
                          └──────────────────────────────────────┘
                               │
                               ▼
                          Recall@1, Recall@3, Recall@5
                          MRR
                          NDCG@3
                          Per-chunk difficulty analysis
                          Keyword vs BM25 comparison
```

### Running the Pipeline

```bash
# Set up virtual environment
source /path/to/stage-1-chatbot/.venv/bin/activate

# Step 1: Chunk the knowledge base
python chunk_knowledge_base.py

# Step 2: Generate synthetic QA pairs (requires OPENAI_API_KEY)
python generate_qa_pairs.py

# Step 3: Evaluate retrieval
python evaluate_retrieval.py
```

---

## 8. Common Pitfalls (Ch7 §7.6)

### Pitfall 1: Relying Only on End-to-End Metrics

If you only measure whether the chatbot gives correct answers, you cannot diagnose retrieval failures. A bot that says "I don't have information about that" on 30% of queries might have a perfect generator — but a broken retriever.

**Fix**: Always report Recall@k separately from answer correctness. If Recall@5 < 0.85, fix retrieval before evaluating generation.

### Pitfall 2: Overfitting to Synthetic Datasets

Synthetic QA pairs skew toward extractive questions — questions whose answer appears almost verbatim in the source chunk. Real users ask paraphrased, contextual, multi-step questions. A retriever that scores 0.95 Recall@5 on synthetic data may score 0.65 on real user queries.

**Fix**: 
- Mix synthetic questions with real user queries (even a small number — 10-20 real queries dramatically improves evaluation validity)
- Use the realism scoring filter to remove overly extractive synthetic questions
- Monitor retrieval quality on production queries once deployed

### Pitfall 3: Wrong Metric for the Task

Using MRR for a multi-document synthesis question ("What should I know before starting to sell on eBay Live?") is misleading. MRR rewards getting one chunk ranked first — but this question benefits from 3-4 chunks.

**Fix**: Match the metric to the query type:
- Single-fact queries → MRR
- Coverage/completeness queries → Recall@k
- Graded relevance → NDCG@k

When in doubt, report all three and let the specific eval task guide which number you optimize for.

### Pitfall 4: Ignoring Chunking Strategy

Many teams spend weeks tuning retrieval algorithms while using arbitrary chunk boundaries. Chunking is upstream of retrieval — a bad chunking strategy cannot be fixed by a better retriever.

**Fix**: Run your retrieval eval at multiple chunk sizes and strategies. For document-structured knowledge bases (like the eBay Live system prompt), section-based chunking almost always outperforms fixed-size windows.

### Pitfall 5: Not Testing Edge Cases

Short queries ("fees?"), ambiguous queries ("how does it work?"), and queries that span multiple sections ("what do buyers and sellers both need to know?") behave very differently from typical synthetic questions.

**Fix**: Include edge-case queries in your eval set. Add a few manually written ambiguous or short queries alongside the synthetic ones.

### Pitfall 6: Chunk Overlap Is Not Free

Adding 50-token overlap between chunks improves recall for questions that straddle chunk boundaries — but it also duplicates content, inflating the effective corpus size and increasing retrieval noise. 

**Fix**: Measure whether overlap actually improves Recall@k for your specific query distribution before committing to it.

---

## 9. Interpreting Results

After running `evaluate_retrieval.py`, you will see output like:

```
=== Retrieval Evaluation Results ===

Query Results:
  Q01  [FOUND@1]  chunk_03  "What happens if someone bids in the last few seconds?"
  Q02  [FOUND@2]  chunk_05  "Are there fees when items sell on eBay Live?"
  Q03  [MISS]     chunk_01  "Can buyers from the UK participate?"
  ...

=== Aggregate Metrics ===
  Recall@1:  0.65
  Recall@3:  0.80
  Recall@5:  0.90
  MRR:       0.72
  NDCG@3:    0.74

=== Hardest Chunks to Retrieve ===
  chunk_01 (Availability):  Recall@5 = 0.50  (2/4 queries found)
  chunk_09 (Competitive):   Recall@5 = 0.67  (2/3 queries found)
```

### How to Read This

**Recall@1 = 0.65**: The right chunk is the top result 65% of the time. This means 35% of queries require the user (or LLM) to look past the first result.

**Recall@5 = 0.90**: In 90% of queries, the gold chunk appears somewhere in the top-5 results. If you pass top-5 chunks to the LLM, it will have the right information 90% of the time.

**Recall gap (R@1 to R@5 = 0.25)**: A large gap means the retriever finds the right chunk but does not rank it first. This points to a reranking problem — Stage 2 improvements would help more than Stage 1 improvements.

**MRR = 0.72**: The average reciprocal rank is 0.72. Reciprocal rank of 1.0 = found at rank 1; 0.5 = found at rank 2; 0.33 = found at rank 3.

**Hardest chunks**: chunk_01 (Availability) and chunk_09 (Competitive Landscape) have low recall. Typically this means:
- The chunk has unusual vocabulary not shared with user queries
- User queries about this topic use different terminology
- Consider adding synonyms or query expansion for these topics

---

## 10. What This Stage Builds Toward

Stage 6 is the foundation for the remaining stages:

- **Stage 7 (Agent Evals)**: Agents use retrieval to look up policies and account data. The same Recall@k evaluation applies — but now you also evaluate whether the agent decides to retrieve at all.

- **Stage 8 (CI/Monitoring)**: Retrieval metrics should be part of your CI pipeline. A code change that improves generation but drops Recall@5 from 0.90 to 0.75 should fail the CI check.

The broader lesson from Chapter 7: **RAG quality = retrieval quality × generation quality.** You can improve either one independently. But you cannot know which one to improve without measuring them separately.

---

## Files in This Stage

| File                        | Purpose                                                  |
|-----------------------------|----------------------------------------------------------|
| `chunk_knowledge_base.py`   | Splits system_prompt.md into section-based chunks        |
| `generate_qa_pairs.py`      | Synthetically generates (query, gold_chunk_id) pairs     |
| `retriever.py`              | BM25 retrieval over the chunked knowledge base           |
| `evaluate_retrieval.py`     | Computes Recall@k, MRR, NDCG@k and prints detailed results |
| `data/chunks.json`          | Output of chunk_knowledge_base.py                        |
| `data/qa_pairs.json`        | Output of generate_qa_pairs.py                           |

---

## Further Reading

- Chapter 7 of Shankar & Husain (2026): full treatment of RAG evaluation
- Robertson & Zaragoza (2009): "The Probabilistic Relevance Framework: BM25 and Beyond"
- BEIR benchmark (Thakur et al., 2021): a heterogeneous retrieval evaluation benchmark
- RAGAS (Es et al., 2023): an end-to-end RAG evaluation framework that builds on these primitives
