# Stage 5 — LLM-as-Judge

Build an automated evaluator for each failure mode from Stage 4. Validate it with TPR/TNR, correct for judge bias using the Rogan-Gladen formula (Ch 5).

## The workflow (from Ch 5 §5.2–5.6)

```
1. Write judge prompt  →  2. Split data (train/dev/test)  →  3. Iterate on dev  →  4. Estimate true success rate
```

## Judge prompt structure (Ch 5 §5.3)

Each judge prompt needs 4 things:
1. **Clear task** — one narrowly scoped failure mode (not "is this good?")
2. **Pass/Fail definitions** — directly from your failure taxonomy (Stage 4)
3. **Few-shot examples** — drawn from your training split, not dev/test
4. **Structured output** — JSON with `reasoning` + `answer` fields

## Data splits (Ch 5 §5.4)

From your labeled traces, split into:
- **Train (10–20%)** — few-shot examples for the judge prompt
- **Dev (40–45%)** — iterate and refine the prompt here
- **Test (40–45%)** — final unbiased TPR/TNR measurement (never look at this during development)

## Metrics (Ch 5 §5.5)

- **TPR** = fraction of actual failures the judge correctly labels as Fail
- **TNR** = fraction of actual passes the judge correctly labels as Pass
- Target: both > 90%

## Bias correction (Ch 5 §5.6)

The judge is imperfect. Correct for its errors using the Rogan-Gladen formula:

```
θ̂ = (p_obs + TNR - 1) / (TPR + TNR - 1)
```

Where `p_obs` is the raw observed pass rate. Use the `judgy` library:
```bash
pip install judgy
```

## Coming in this stage

- `judge_prompts/` — one prompt per failure mode
- `label_traces.py` — human labeling tool (train/dev/test split)
- `evaluate_judge.py` — computes TPR/TNR on test set
- `estimate_success_rate.py` — applies bias correction via judgy

## Next: Stage 6 — Retrieval Eval

Add a knowledge base (RAG), synthetically generate (query, gold chunk) pairs, measure Recall@k and MRR.
