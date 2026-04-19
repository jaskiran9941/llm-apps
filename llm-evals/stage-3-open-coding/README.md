# Stage 3 — Open Coding

Read every trace and write a freeform note about what you observe. No categories yet — just raw observations. This is **open coding** from grounded theory (Ch 3 §3.3).

## The principle

> "For each trace, read carefully and write brief notes about what you observe: where outputs are incorrect, where actions are surprising, or where the behavior feels wrong or unexpected." — Shankar & Husain (2026)

Focus on the **first (most upstream) failure** in each trace. Errors often cascade — fixing the first one resolves everything downstream.

## Key questions to ask per trace

- Does the response stay within the knowledge base, or does it invent facts?
- Does it correctly handle the user type (buyer vs. seller)?
- Does it know when it doesn't know something?
- Is the tone and specificity appropriate for the scenario?

## What's in here

| File | Purpose |
|------|---------|
| `open_coding.py` | Interactive CLI — shows traces one at a time, collects your notes |
| `open_codes/` | Saved annotation JSONs |

## How to run

```bash
python3 open_coding.py [path/to/traces.json]
```

Shows each trace, prompts for:
1. A freeform note (what went wrong?)
2. The point of first failure (one phrase)
3. Overall: acceptable or not (y/n)

Press Enter to skip a trace. Saves progress automatically.

## When to stop

Keep going until you've seen at least 20 bad traces and no fundamentally new failure types are appearing — this is **theoretical saturation**.

## Next: Stage 4 — Axial Coding

Take all your open codes and cluster similar ones into a small, coherent set of binary failure modes.
