# Stage 7 — Agent Evals

Add tools to the chatbot and evaluate it as an agent. Analyze failure patterns using a **state-transition failure matrix** (Ch 8 §8.3).

## What changes

The chatbot gains tools it can call:
- `lookup_seller_eligibility(account_id)` — checks if a seller qualifies for eBay Live
- `lookup_category_policy(category)` — checks if a category is supported
- `escalate_to_human()` — transfers to a human agent

This turns the chatbot from a single LLM call into a **multi-step pipeline** where failures can occur at each step.

## Failure modes in tool-calling systems (Ch 8 §8.1)

Evaluate each step of the tool-calling cycle:
1. **Tool selection** — did it pick the right tool?
2. **Argument generation** — are the arguments valid and correct?
3. **Execution success** — did the tool call succeed?
4. **Output handling** — did the LLM correctly use the tool's response?

## State-transition failure matrix (Ch 8 §8.3)

Define pipeline states (e.g., `ParseIntent → SelectTool → CallTool → GenerateResponse`). For failed traces, record which state the first failure occurred in and what the preceding state was.

```
From State    | ParseIntent | SelectTool | CallTool | GenerateResponse
ParseIntent   |      0      |     3      |    0     |       0
SelectTool    |      0      |     0      |    7     |       0
CallTool      |      0      |     0      |    0     |       4
```

The hotspots tell you where to focus prompt engineering or tool description fixes.

## Coming in this stage

- `tools.py` — mock tool implementations
- `agent_backend.py` — updated chatbot that calls tools
- `collect_agent_traces.py` — collects multi-step traces with full tool call logs
- `transition_matrix.py` — builds and visualizes the state-transition failure matrix

## Next: Stage 8 — CI/Monitoring

Build a golden dataset from your best-labeled traces and run CI checks on every pipeline change.
