# Stage 4 — Axial Coding: Build Failure Taxonomy

Take all the raw open codes from Stage 3 and cluster them into a **small, coherent, non-overlapping set of binary failure modes**. This is **axial coding** from grounded theory (Ch 3 §3.4–3.6).

## The principle

> "The goal is to define a small, coherent, non-overlapping set of binary failure types, each easy to recognize and apply consistently during trace annotation." — Shankar & Husain (2026)

Each failure mode must be:
- **Binary**: either present (1) or absent (0) in a trace
- **Specific**: not "hallucination" in general, but *how* it hallucinated for eBay Live
- **Non-overlapping**: a trace shouldn't be ambiguously classifiable

## What's in here

| File | Purpose |
|------|---------|
| `axial_coding.py` | Loads open codes, uses LLM to propose failure clusters, lets you refine |
| `failure_taxonomy.md` | The finalized failure taxonomy (fill in after running axial coding) |
| `taxonomies/` | Saved taxonomy JSONs from each run |

## How to run

```bash
python3 axial_coding.py [path/to/open_codes.json]
```

The script:
1. Loads your open codes from Stage 3
2. Pastes them into an LLM prompt asking for preliminary groupings
3. Prints the proposed clusters
4. You review, rename, or split as needed
5. Saves the final taxonomy

## Expected output: eBay Live failure taxonomy

From our early observations, likely failure modes include:

| Failure Mode | Definition |
|---|---|
| **Out-of-scope hallucination** | Bot states a confident fact about a topic not in the knowledge base |
| **Incorrect policy claim** | Bot states a policy detail that contradicts the knowledge base |
| **Wrong user type framing** | Bot gives buyer advice to a seller question or vice versa |
| **Failure to escalate** | Bot doesn't say "I don't know" when it should |
| **Incomplete answer** | Bot omits a key detail that's clearly in the knowledge base |

## Next: Stage 5 — LLM Judge

Use these failure modes to build an automated evaluator. For each failure mode, write a Pass/Fail LLM-as-Judge prompt, validate it with TPR/TNR, and correct for judge bias.
