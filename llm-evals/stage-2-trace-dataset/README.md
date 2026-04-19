# Stage 2 — Create Trace Dataset

Before you can do error analysis, you need **traces** — not just questions. A trace is the full record of a user query + the chatbot's complete response. This stage builds ~50 diverse traces using structured **dimensions** (Ch 3 §3.2).

## Why dimensions?

Naively asking "give me 50 questions" produces generic, repetitive queries. Instead, we define axes of variation that reflect where the system is likely to fail, then sample queries that cover the space.

## eBay Live dimensions

| Dimension | Values |
|-----------|--------|
| **User Type** | buyer, seller |
| **Query Type** | policy/rules, how-to, eligibility, categories, troubleshooting, out-of-scope |
| **Scenario** | specific/clear, ambiguous, edge-case |

These 3 dimensions give 36 possible combinations (tuples). We sample ~50 queries across them.

## What's in here

| File | Purpose |
|------|---------|
| `dimensions.md` | Full definition of dimensions and example tuples |
| `generate_queries.py` | Uses LLM to turn (tuple → natural language query) |
| `collect_traces.py` | Sends each query to the chatbot, saves full trace to JSON |
| `queries/` | Generated query CSVs |
| `traces/` | Collected trace JSONs |
| `test_questions.csv` | V1: 24 hand-crafted questions from initial exploration |
| `run_tests.py` | V1: test runner from initial manual testing |
| `results/` | V1: results from initial 24-question run |

## V1 findings (from initial 24-question run)

- **22/24 accurate** and grounded in the knowledge base
- **2 hallucinations**: Q22 (invented mobile app access method), Q24 (invented scheduling policy)
- **1 borderline**: Q3 (inferred watching-vs-participating distinction not in KB)

## How to run (V2 — dimension-based)

Make sure Stage 1 chatbot is running on port 8001, then:

```bash
python3 generate_queries.py   # generates queries from dimensions
python3 collect_traces.py     # runs them, saves traces/traces_YYYYMMDD.json
```

## Next: Stage 3 — Open Coding

Read every trace and write a freeform note about what went wrong. Don't categorize yet — just observe.
