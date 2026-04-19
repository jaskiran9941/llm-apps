# Stage 8 — CI/Monitoring

Embed your evaluators into a continuous integration loop and monitor real-world performance (Ch 9).

## The distinction (Ch 9 §9.1–9.2)

| | CI | Online Monitoring |
|---|---|---|
| **What** | Regression tests on known failures | Sampling production traces |
| **When** | Every pipeline change | Continuously in production |
| **Dataset** | Golden dataset (curated, small) | Live traffic (sampled) |
| **Goal** | Stability — don't break what works | Discovery — find unknown unknowns |

> "CI prevents regressions on known issues. CD surfaces new failure modes."

## Golden dataset (Ch 9 §9.1)

A hand-curated set of inputs with correct reference outputs. Built from:
- Traces labeled as failures during Stages 3–4 (regression examples)
- Edge cases uncovered during error analysis
- Examples covering each core feature

**Rule**: never use golden dataset examples as few-shot examples in your judge prompt (data leakage). Keep them strictly for evaluation.

## CI checks

For each golden example, run the pipeline and evaluate with your Stage 5 judges. Fail the build if any previously-passing check regresses.

```bash
python3 ci_runner.py   # runs all golden examples, reports pass/fail
```

## Online monitoring

Sample 1–5% of production traces. Run automated judges asynchronously. Track the bias-corrected success rate θ̂ (from Stage 5) over time. Alert if the lower bound of the confidence interval drops below your threshold.

## What's in here

| File | Purpose |
|------|---------|
| `golden_dataset/` | Curated examples with reference outputs |
| `ci_runner.py` | Runs golden dataset through chatbot + judges |
| `monitoring_sampler.py` | Samples and evaluates production traces |

## Coming in this stage

- Populate `golden_dataset/` from your best-labeled Stage 3–4 traces
- `ci_runner.py` — automated CI check script
- `monitoring_sampler.py` — online monitoring with corrected success rate tracking
