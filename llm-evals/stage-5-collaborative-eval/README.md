# Stage 5 — Collaborative Evaluation

> **Course reference:** Chapter 4 — *Collaborative Evaluation Practices*
> Shankar & Husain (2026)

---

## Why This Stage Exists

In Stage 4 (open coding) you annotated traces alone. That is a necessary starting point, but it is not sufficient.

The problem: **your labels reflect your interpretation of the rubric, not the rubric itself.** If a teammate reads the same trace with the same rubric definition and labels it differently, you do not have a reliable rubric — you have two people's opinions. An automated evaluator built on inconsistent labels will inherit that inconsistency.

This stage teaches you to measure annotation consistency, resolve disagreements, and produce labels reliable enough to train and validate automated judges.

---

## 1. The Benevolent Dictator Model

For small teams and solo projects, the book recommends starting with a **principal domain expert** — one person whose judgment defines correctness.

> "In smaller companies, there are usually one (maybe two) key individuals whose judgment is crucial for the success of the AI product."
> — Shankar & Husain (2026), Ch. 4

For the eBay Live chatbot, **you are the domain expert.** You know the eBay Live policies (or can verify them against the knowledge base). Your labels are the ground truth.

But even a solo expert needs to be consistent with **themselves** across time. The collaborative workflow below makes your rubric explicit enough that a second person — or your future self — can apply it reproducibly.

---

## 2. The Collaborative Annotation Workflow

When working with a team (or a second annotator), follow these 9 steps from Ch. 4 §4.2:

1. **Assemble the team.** At minimum: 2 people with domain knowledge.
2. **Draft an initial rubric.** Define Pass/Fail for each failure mode in one sentence. Include 2–3 concrete examples.
3. **Select a shared annotation set.** 20–50 traces all annotators will label. Include borderline cases.
4. **Label independently.** No discussion. Each person labels all traces alone.
5. **Measure IAA.** Compute Cohen's Kappa (see below).
6. **Alignment session.** Discuss disagreements. Focus on improving the rubric, not re-litigating past labels.
7. **Revise the rubric.** Clarify definitions, add examples, split criteria if needed.
8. **Iterate.** Repeat steps 4–7 until κ ≥ 0.6.
9. **Finalize.** Document the rubric. Generate consensus labels. Use as ground truth for Stage 7.

---

## 3. Inter-Annotator Agreement: Cohen's Kappa

**Percent Agreement** is the fraction of traces where two annotators agreed. It is easy to compute but misleading — if both annotators label 90% of traces as "Pass," they will agree 90% of the time by chance alone.

**Cohen's Kappa (κ)** corrects for chance agreement:

```
κ = (P_observed - P_expected) / (1 - P_expected)
```

Where:
- `P_observed` = fraction of traces where annotators agreed
- `P_expected` = fraction expected to agree by chance (based on each annotator's marginal label distribution)

### Interpretation (Landis & Koch, 1977)

| κ value | Interpretation |
|---------|---------------|
| < 0.00  | Poor (systematic disagreement) |
| 0.00–0.20 | Slight |
| 0.21–0.40 | Fair |
| 0.41–0.60 | Moderate |
| 0.61–0.80 | **Substantial ← target minimum** |
| 0.81–1.00 | Almost perfect |

**Target: κ ≥ 0.60.** Below this, the rubric is too ambiguous to trust for automated evaluation.

### Worked Example for eBay Live

Two annotators label 20 traces for **FM1 (Confident Out-of-Scope Claim)**:

```
Annotator A: [F, P, F, P, F, F, P, P, P, F, F, P, F, P, P, F, P, F, P, F]
Annotator B: [F, P, F, P, P, F, P, P, P, F, F, P, P, P, P, F, P, F, P, F]
```

Agreements: 18/20 → P_observed = 0.90

Annotator A: 10 Fail, 10 Pass → p_A_fail = 0.50, p_A_pass = 0.50
Annotator B: 8 Fail, 12 Pass → p_B_fail = 0.40, p_B_pass = 0.60

P_expected = (0.50 × 0.40) + (0.50 × 0.60) = 0.20 + 0.30 = 0.50

κ = (0.90 - 0.50) / (1 - 0.50) = 0.40 / 0.50 = **0.80** → Substantial ✓

---

## 4. Computing Kappa in Python

```python
# kappa.py — run after both annotators label the same traces

from collections import Counter

def cohens_kappa(rater_a: list, rater_b: list) -> float:
    """
    Compute Cohen's Kappa for two raters with binary labels.
    
    Args:
        rater_a: list of labels ("Pass" or "Fail") from annotator A
        rater_b: list of labels ("Pass" or "Fail") from annotator B
    
    Returns:
        κ (float) — ranges from -1.0 (perfect disagreement) to 1.0 (perfect agreement)
    """
    assert len(rater_a) == len(rater_b), "Both raters must label the same traces"
    n = len(rater_a)
    
    # Observed agreement
    p_obs = sum(a == b for a, b in zip(rater_a, rater_b)) / n
    
    # Expected agreement by chance
    labels = set(rater_a) | set(rater_b)
    count_a = Counter(rater_a)
    count_b = Counter(rater_b)
    p_exp = sum((count_a[l] / n) * (count_b[l] / n) for l in labels)
    
    if p_exp == 1.0:
        return 1.0 if p_obs == 1.0 else 0.0
    
    return (p_obs - p_exp) / (1 - p_exp)


def interpret_kappa(kappa: float) -> str:
    if kappa < 0:      return "Poor (systematic disagreement)"
    if kappa < 0.20:   return "Slight"
    if kappa < 0.40:   return "Fair"
    if kappa < 0.60:   return "Moderate — rubric needs refinement"
    if kappa < 0.80:   return "Substantial ✓"
    return "Almost perfect ✓"


if __name__ == "__main__":
    # Example: FM1 annotations from two reviewers on 20 traces
    annotator_a = ["Fail","Pass","Fail","Pass","Fail","Fail","Pass","Pass","Pass","Fail",
                   "Fail","Pass","Fail","Pass","Pass","Fail","Pass","Fail","Pass","Fail"]
    annotator_b = ["Fail","Pass","Fail","Pass","Pass","Fail","Pass","Pass","Pass","Fail",
                   "Fail","Pass","Pass","Pass","Pass","Fail","Pass","Fail","Pass","Fail"]
    
    kappa = cohens_kappa(annotator_a, annotator_b)
    print(f"Cohen's Kappa: {kappa:.3f}")
    print(f"Interpretation: {interpret_kappa(kappa)}")
    
    # Disagreement analysis
    print("\nDisagreements:")
    for i, (a, b) in enumerate(zip(annotator_a, annotator_b)):
        if a != b:
            print(f"  Trace {i+1}: A={a}, B={b}")
```

---

## 5. Running a Collaborative Eval on eBay Live Traces

### Step 1 — Select your annotation set

From the 36 Stage 3 traces, pick 20 to label collaboratively. Include:
- 5 clear passes (bot correctly answers from KB)
- 5 clear fails (obvious hallucination)
- 10 borderline cases (where reasonable people might disagree)

The borderline cases drive rubric improvement. If you only label easy cases, κ will be artificially high.

### Step 2 — Label independently

Both annotators apply the FM1 rubric to all 20 traces without discussion.

FM1 rubric reminder:
- **Fail**: Response states "eBay Live does not support X" / "X is not available" for a topic not in the knowledge base
- **Pass**: Response correctly answers from KB, OR correctly says "I don't know" and directs to help

### Step 3 — Compute κ

```bash
source ../stage-1-chatbot/.venv/bin/activate
python3 kappa.py
```

### Step 4 — Run an alignment session

For each disagreement:
1. Read the trace together
2. Ask: "Which part of the rubric definition caused the disagreement?"
3. Update the rubric definition to resolve it
4. Do NOT just vote on the label — fix the definition

Common eBay Live alignment issues:
- **Does "focused on standard devices" count as FM1?** (Trace 16 — bot said eBay Live "focuses on livestream video shopping through standard devices like smartphones and computers") → Probably FM1 because this is invented framing, not a KB statement.
- **Does correctly deferring count as FM4?** (Trace 19 — bot said "information does not specify") → No. FM4 is when the bot answers confidently on an out-of-scope topic. Correctly deferring is the desired behavior.

### Step 5 — Iterate until κ ≥ 0.60

After each rubric revision, re-label the disagreement cases and recompute κ. Two rounds is usually sufficient for a well-scoped failure mode.

---

## 6. Connecting Collaborative Labels to Stage 7

The outputs of this stage feed directly into Stage 7 (LLM Judge) in two ways:

**The rubric becomes the judge prompt.** The precise Pass/Fail definition you refined in alignment sessions is exactly what you paste into the FM1 judge prompt. A rubric clear enough for two humans to agree on is clear enough for an LLM to apply.

**The consensus labels become the test set.** The 20 consensus-labeled traces are split into train/dev/test for Stage 7. The judge's TPR and TNR are measured against these labels. If your labels are inconsistent, your TPR/TNR measurements are unreliable.

> "The consensus-labeled dataset provides a trusted ground truth for evaluating the LLM judge's accuracy."
> — Shankar & Husain (2026), Ch. 4

---

## 7. Common Pitfalls

**Skipping independent annotation.** If annotators discuss before labeling, their labels reflect group consensus, not rubric clarity. You cannot measure real disagreement.

**Treating κ > 0.6 as "done."** High κ after a discussion session means the discussion resolved the disagreement, not that the rubric is inherently clear. Always measure κ on independent labels.

**Using majority vote to resolve disagreements.** Voting resolves the label but not the rubric ambiguity. The same disagreement will reappear with the next batch of traces. Fix the definition instead.

**Excluding domain experts.** For eBay Live, the labeler must know the knowledge base. General developers labeling "hallucination / not hallucination" without knowing what is in the KB will produce unreliable labels.

---

## Files in This Stage

| File | Purpose |
|------|---------|
| `kappa.py` | Compute Cohen's Kappa from two annotation lists |
| `annotation_template.csv` | Template for recording labels during collaborative sessions |

## Next: Stage 6 — Axial Coding

Once your rubrics are reliable (κ ≥ 0.6), cluster the open codes into a formal failure taxonomy.
