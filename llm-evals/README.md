# LLM Evals — Learning Evaluations Progressively

A customer support chatbot for **eBay Live** built and evaluated across 8 progressive stages, following the **Analyze → Measure → Improve** lifecycle from Shankar & Husain (2026).

| Stage | Topic | What you learn | Course chapter |
|-------|-------|----------------|---------------|
| [1 - Chatbot](./stage-1-chatbot/) | Build the chatbot | FastAPI + LiteLLM baseline | — |
| [2 - Trace Dataset](./stage-2-trace-dataset/) | Create structured traces | Dimensions, tuples, synthetic query generation | Ch 3 §3.2 |
| [3 - Open Coding](./stage-3-open-coding/) | Read and label traces | Freeform annotation, first-failure principle | Ch 3 §3.3 |
| [4 - Axial Coding](./stage-4-axial-coding/) | Build failure taxonomy | Cluster open codes into binary failure modes | Ch 3 §3.4–3.6 |
| [5 - LLM Judge](./stage-5-llm-judge/) | Automate grading | TPR/TNR, bias correction, train/dev/test splits | Ch 5 |
| [6 - Retrieval Eval](./stage-6-retrieval-eval/) | Add RAG | Synthetic QA pairs, Recall@k, MRR | Ch 7 |
| [7 - Agent Evals](./stage-7-agent-evals/) | Add tools | State-transition failure matrix | Ch 8 |
| [8 - CI/Monitoring](./stage-8-ci-monitoring/) | Production eval loop | Golden dataset, CI regression tests, online monitoring | Ch 9 |

## The lifecycle

```
Analyze  →  Measure  →  Improve
(Stages 2–4)  (Stages 5–6)  (Stages 7–8)
```

The key unit of analysis throughout is a **trace** — the complete record of inputs, LLM outputs, and intermediate steps for a single user query. Not just the final answer.

## Philosophy

Each stage builds on the previous one. By stage 8 you'll have a full eval pipeline you built yourself — grounded in real eBay Live knowledge, not copied from a tutorial.
