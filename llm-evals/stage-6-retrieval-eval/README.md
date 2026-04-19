# Stage 6 — Retrieval Eval (RAG)

Add a knowledge base to the chatbot and evaluate whether it retrieves the right chunks. Measure **Recall@k** and **MRR** (Ch 7).

## Why retrieval matters

The current chatbot has the knowledge base baked into the system prompt. In production, you'd retrieve relevant chunks from a larger document corpus. A weak retriever means the LLM never sees the right information — no amount of generation quality fixes that.

## The RAG eval pipeline (Ch 7 §7.1–7.3)

```
Knowledge base → chunks → synthetic (query, gold_chunk) pairs → retriever → Recall@k / MRR
```

Evaluate retrieval independently before evaluating generation. A single end-to-end score doesn't tell you which component failed.

## Synthetic QA generation (Ch 7 §7.2)

We don't have labeled (query, document) pairs. So we generate them synthetically:

1. Split knowledge base into chunks
2. For each chunk, prompt LLM: *"Extract one fact from this chunk, then write a question only answerable by that fact"*
3. Output: `{"fact": "...", "question": "...", "source_chunk": "..."}`
4. Filter unrealistic questions using few-shot LLM scoring

## Metrics (Ch 7 §7.3)

- **Recall@k** — does the relevant chunk appear in the top k results? (prioritize for RAG stage 1)
- **MRR** — how early does the first relevant chunk appear? (good for single-fact queries)
- **NDCG@k** — graded relevance ranking (useful when some chunks are more relevant than others)

## Coming in this stage

- `chunk_knowledge_base.py` — splits system prompt into retrievable chunks
- `generate_qa_pairs.py` — synthetically generates (query, gold_chunk) pairs
- `retriever.py` — BM25 + embedding-based retrieval
- `evaluate_retrieval.py` — computes Recall@k and MRR

## Next: Stage 7 — Agent Evals

Add tools (account lookup, policy lookup) to the chatbot and analyze where in the agent's decision chain failures occur.
