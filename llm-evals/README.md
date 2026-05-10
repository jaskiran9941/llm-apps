# LLM Evals — Learning Evaluations Progressively

## What This Project Is

An **eBay Live customer support chatbot** used as a hands-on vehicle for learning LLM evaluation end-to-end.

The chatbot is real. It answers questions about eBay Live policies, bidding rules, seller eligibility, and categories. Every eval stage is applied to it using real responses from a real model. By the end, you will have built a complete evaluation pipeline from scratch — not copied from a tutorial.

The course it follows: **Application-Centric AI Evals for Engineers and Technical Product Managers** by Shreya Shankar and Hamel Husain (Spring 2026).

---

## What the Chatbot Is Built On

| Component | Technology |
|-----------|-----------|
| **Web framework** | FastAPI |
| **LLM routing** | LiteLLM (model-agnostic — swap providers without changing code) |
| **Default model** | `openai/gpt-4.1-mini` |
| **Knowledge base** | eBay Live system prompt (real public info scraped from eBay help pages) |
| **Frontend** | Plain HTML/JS (no framework) |
| **Environment** | Python 3.9+, `.env` for API keys |

The chatbot has **no database, no retrieval, no tools** in Stage 1. Each subsequent stage adds capability and complexity — and a new layer of evaluation to match.

---

## The Eval Lifecycle

```
ANALYZE          →          MEASURE          →         IMPROVE
(Stages 2–6)                (Stages 7–8)               (Stages 9–10)

Understand what            Quantify it with            Fix and maintain
is failing and why         automated metrics           the pipeline
```

---

## All 10 Stages

| # | Stage | What It Is | PDF Chapter |
|---|-------|-----------|-------------|
| [1](./stage-1-chatbot/) | **Build the Chatbot** | FastAPI + LiteLLM + eBay Live knowledge base. The thing we will evaluate. | — |
| [2](./stage-2-eval-foundations/) | **Evaluation Foundations** | Before measuring anything, understand what "good" means. Reference-based vs reference-free metrics. Why binary beats Likert. Prompting fundamentals. | Ch 2 |
| [3](./stage-3-trace-dataset/) | **Trace Dataset** | Collect ~36 structured traces using dimensions (user_type × query_type × scenario). A trace is the unit of analysis — not just the query, the full response record. | Ch 3 §3.2 |
| [4](./stage-4-open-coding/) | **Open Coding** | Read every trace and write freeform notes about what went wrong. No categories yet. Build a simple annotation interface. | Ch 3 §3.3 + Ch 10 |
| [5](./stage-5-collaborative-eval/) | **Collaborative Evaluation** | Have multiple people label the same traces. Measure agreement with Cohen's Kappa. Run an alignment session. Build rubrics that two annotators apply consistently (κ ≥ 0.6). | Ch 4 |
| [6](./stage-6-axial-coding/) | **Axial Coding** | Cluster open codes into a small, coherent, non-overlapping set of binary failure modes (FM1–FM5). This taxonomy feeds every downstream stage. | Ch 3 §3.4–3.6 |
| [7](./stage-7-llm-judge/) | **LLM Judge** | Automate grading using an LLM evaluator. Build Pass/Fail prompts for each failure mode. Measure accuracy with TPR/TNR. Correct for judge bias using Rogan-Gladen. | Ch 5 |
| [8](./stage-8-retrieval-eval/) | **Retrieval Eval (RAG)** | Convert the chatbot to RAG. Evaluate whether the retriever finds the right knowledge base chunks. Measure Recall@k, MRR, NDCG@k. | Ch 7 |
| [9](./stage-9-agent-evals/) | **Agent Evals** | Give the chatbot tools. Evaluate each step of the tool-calling cycle. Build a state-transition failure matrix to pinpoint where failures originate. | Ch 8 |
| [10](./stage-10-ci-monitoring/) | **CI, Monitoring & Improvement** | Build a golden dataset. Run CI regression tests. Monitor live traffic. Apply prompt refinement, task decomposition, and model cascades to improve quality and cut cost. | Ch 9 + Ch 11 |

---

## The 5 Failure Modes (From Stage 6)

Derived from open coding 36 real eBay Live traces:

| ID | Name | Example |
|----|------|---------|
| FM1 | Confident Out-of-Scope Claim | "Pre-recorded video is not supported" — policy not in KB |
| FM2 | Invented Troubleshooting Steps | "Try clearing cache and restarting the app" — not in KB |
| FM3 | Invented Process Details | "Submit at ebay.com/live" — invented URL |
| FM4 | Failure to Escalate | Answers confidently on topics it genuinely doesn't know |
| FM5 | Potentially Misleading Inference | "Avoid placing duplicate bids" — stated as policy, not in KB |

---

## How to Run

```bash
# Clone and navigate
cd llm-evals/stage-1-chatbot

# Set up
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your OPENAI_API_KEY

# Run
uvicorn backend.main:app --reload --port 8001
```

Open http://localhost:8001 — that's Stage 1. Each subsequent stage runs from its own directory, using the same venv.

---

## Stage Dependencies

```
Stage 1 (chatbot running)
    └── Stage 2 (concepts — read the README)
         └── Stage 3 (collect traces from Stage 1)
              └── Stage 4 (annotate Stage 3 traces)
                   └── Stage 5 (measure annotation agreement from Stage 4)
                        └── Stage 6 (cluster Stage 4 annotations into taxonomy)
                             └── Stage 7 (build judges for Stage 6 taxonomy)
                                  └── Stage 8 (add RAG to Stage 1 chatbot)
                                       └── Stage 9 (add tools to Stage 1 chatbot)
                                            └── Stage 10 (CI + monitoring + improve)
```
