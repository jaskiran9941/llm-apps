# LLM Evals — Learning Evaluations Progressively

A customer support chatbot for **TaskFlow** (fictional SaaS) built and evaluated across 7 progressive stages.

| Stage | Topic | What you learn |
|-------|-------|----------------|
| [1 - Chatbot](./stage-1-chatbot/) | Build the chatbot | FastAPI + LiteLLM baseline |
| [2 - Manual Testing](./stage-2-manual-testing/) | Run it by hand | Spot failure modes qualitatively |
| [3 - Bulk Testing](./stage-3-bulk-testing/) | Fire 50+ queries | Collect responses at scale |
| [4 - Error Analysis](./stage-4-error-analysis/) | Open coding | Taxonomy of failure categories |
| [5 - LLM Judge](./stage-5-llm-judge/) | Automate grading | TPR/TNR, bias correction |
| [6 - Retrieval Eval](./stage-6-retrieval-eval/) | Add RAG | Recall@k, MRR |
| [7 - Agent Evals](./stage-7-agent-evals/) | Add tools | State-transition failure analysis |

## Philosophy

Each stage builds on the previous one. By stage 7 you'll have a full eval pipeline you built yourself — not copied.
