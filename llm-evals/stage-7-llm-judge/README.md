# Stage 5 — LLM-as-Judge

*Application-Centric AI Evals for Engineers and Technical Product Managers*
*Shankar & Husain (2026) — Chapter 5*

---

## What We Are Building

In Stage 2 you collected 36 traces from the eBay Live chatbot. You read every one of them by hand. In Stage 3 you open-coded them. In Stage 4 you collapsed those codes into five canonical failure modes.

Now the question is: **can an LLM judge those failure modes automatically, at scale, with measurable accuracy?**

This is the core question of Chapter 5. The answer is yes — but only if you build the judge correctly, validate it against human labels, and correct for its errors when estimating success rates.

---

## 1. Why Manual Labeling Doesn't Scale

You labeled 36 traces. That took time. Imagine you push the eBay Live chatbot to production and it handles 500 conversations a day. In a week you have 3,500 new traces. No human team can read all of them.

You need automation. But you can't just ask an LLM "was this response good?" and trust the answer. An imprecise judge makes systematic errors — it misses some failures and flags some passes — and those errors compound when you try to compute a success rate.

The workflow in Chapter 5 solves this in three steps:

1. **Build a precise judge prompt** for each failure mode (§5.3)
2. **Measure the judge's accuracy** with human-labeled ground truth (§5.5)
3. **Correct for judge errors** when computing pass rates (§5.6)

Each step depends on the previous. You can't skip measurement, and you can't skip correction.

---

## 2. The Five Failure Modes (From Stage 4)

These are the failure modes from the eBay Live axial coding exercise:

| ID  | Name                           | Definition                                                                                          |
|-----|--------------------------------|-----------------------------------------------------------------------------------------------------|
| FM1 | Confident Out-of-Scope Claim   | Bot states eBay Live "does not support X" or "cannot do X" for a topic not in the knowledge base.  |
| FM2 | Invented Troubleshooting Steps | Bot gives technical advice (clear cache, avoid VPNs, restart device) not present in the KB.        |
| FM3 | Invented Process Details       | Bot invents specific URLs, feature names, workflow steps, or form locations not in the KB.          |
| FM4 | Failure to Escalate            | Bot gives a confident answer where it should say "I don't know" and direct to ebay.com/help.       |
| FM5 | Potentially Misleading Inference | Bot makes a plausible but unverified claim stated as fact ("eBay bids are final... so X must be"). |

In this stage we build judges for FM1, FM2, and FM3 as worked examples. The same approach applies to FM4 and FM5.

---

## 3. The Four Components of a Good Judge Prompt (Ch5 §5.3)

This is the most important section of the chapter. Bad judge prompts are the most common reason LLM-as-Judge fails in practice. Here is what every judge prompt must have:

### 3.1 A Clear, Single Criterion

The prompt evaluates exactly one failure mode. Not "is this a good response?" Not "does this response have any problems?" One thing: does this response exhibit FM1?

Why does this matter? Because an LLM asked to evaluate multiple things at once will weight them inconsistently. You lose the ability to interpret the output. You lose the ability to measure accuracy against a specific human label. The criterion must be narrow enough that two humans reading it would apply it the same way.

Compare:

**Vague (bad):**
> "Evaluate whether the chatbot response is accurate and helpful."

**Specific (good):**
> "Determine if the response states a definitive negative claim — that eBay Live does not support or cannot do something — for a topic not covered in the knowledge base, instead of admitting uncertainty."

The difference is precision. The second one tells you exactly what to look for, which topics count as "in scope," and what the correct behavior is when the bot doesn't know.

### 3.2 Precise Pass and Fail Definitions

Every judge prompt must spell out exactly what Pass and Fail mean for this failure mode. Not approximately. Exactly.

For FM1:
- **FAIL**: The bot stated a definitive negative claim ("does not support", "is not available", "cannot do") about a topic not covered in the knowledge base.
- **PASS**: Either (a) the bot correctly answered from the knowledge base, OR (b) the bot correctly admitted uncertainty and directed the user to ebay.com/help or the eBay Live FAQ.

Notice the PASS definition has two valid cases. This is important. A response that says "I don't know, please check ebay.com/help" is a PASS even if it doesn't answer the question — because the bot did the right thing. Not specifying this causes the judge to flag appropriate escalations as failures, which inflates the false positive rate.

### 3.3 Few-Shot Examples Drawn From the Training Set

This is the most commonly omitted component, and the most costly to omit.

The few-shot examples do three things:
1. They show the judge what Pass and Fail look like in your specific domain
2. They force you to be precise about the definition (you have to commit to labels)
3. They dramatically improve judge consistency

The examples must come from your **training split** — a subset of human-labeled traces set aside for this purpose. They must never appear in the dev or test sets used to measure accuracy.

The book is explicit about this: *"A common mistake is inadvertently including evaluation cases as few-shot examples in the prompt. This leaks information and inflates measured accuracy."* If the same trace appears as a few-shot example AND in the dev set, the judge has seen the answer. Your TPR/TNR numbers become unreliable.

Concretely: if you have 36 labeled traces, use 5 as training (for examples in the prompt), 15 as dev (to iterate the prompt), and 16 as test (for final measurement). Use a fixed random seed when splitting so the split is reproducible.

### 3.4 Structured JSON Output with `reasoning` and `answer`

The judge must return:

```json
{
  "reasoning": "The response states 'not supported on the platform' for pre-recorded video, a topic not in the KB...",
  "answer": "Fail"
}
```

The `reasoning` field is not optional. Here is why:

- **Debugging**: When the judge disagrees with your human label, you need to know why. The reasoning tells you whether the judge misunderstood the definition, missed a detail, or whether your label was wrong.
- **Prompt iteration**: During dev-set refinement, you inspect reasoning for systematic patterns. "The judge keeps calling FM1 on responses that correctly say 'not listed in our categories' — I need to clarify that in-scope negative claims are not FM1."
- **Trust**: Stakeholders and teammates are more likely to trust a judge that explains itself.

Always parse the JSON reliably. Use a regex to extract the `{...}` block in case the LLM wraps it in markdown.

---

## 4. Data Splits (Ch5 §5.4)

The train/dev/test split is not a formality. Each split serves a specific and incompatible purpose. Using data from one split for another purpose destroys the value of that split.

### The Three Splits

| Split    | Size (approx) | Purpose                                                       |
|----------|---------------|---------------------------------------------------------------|
| Train    | 10–20%        | Source of few-shot examples embedded in the judge prompt      |
| Dev      | 40–45%        | Iterative prompt refinement — you look at this data often     |
| Test     | 40–45%        | Final, one-time measurement — you must not look at this early |

For 36 traces, a 15%/42%/43% split gives approximately 5 train / 15 dev / 16 test.

### Why Train Must Be Kept Separate

The few-shot examples you put in the prompt ARE part of the judge. If a trace appears as a few-shot example, the judge has been trained on the correct label for that trace. Including it in your dev or test evaluation is the same as including training data in a test set. The accuracy measurement is no longer meaningful.

Operationally: after you split with a fixed seed, write the train IDs to a file. Every time you add an example to the prompt, verify its ID is in the train split.

### Why Test Must Be Held Out Completely

During development, you run the judge on dev traces, look at where it fails, and adjust the prompt. This is correct. But it means your intuitions and the prompt are now adapted to the dev set — even subconsciously.

If you then measure accuracy on the dev set, you are measuring how well you overfit to that 15 traces. You need a completely separate held-out test set that you evaluate exactly once, only when you believe the judge is ready.

This is the same discipline as train/test splits in machine learning. It protects against overfitting. The book states this explicitly: *"Do not look at the test set during development. Evaluate on it once, at the end."*

### The Split Warning

The book gives a concrete warning: *"A common mistake is inadvertently including evaluation cases as few-shot examples in the prompt. This leaks information."*

This happens because the judge prompt and the evaluation script are developed separately. The developer adds an example to the prompt because it looks useful, without checking whether it came from the dev or test set. The fix is simple: keep a `train_ids.json` file and check it before adding any example to a prompt.

---

## 5. Iterative Prompt Refinement (Ch5 §5.5)

Writing a judge prompt is not a one-shot task. It requires iteration on the dev set. Here is the loop:

```
1. Write the initial judge prompt (with Pass/Fail definitions and few-shot examples)
2. Run the judge on the entire dev split
3. Compare judge labels to human labels — compute TPR and TNR
4. Inspect every case where judge and human disagree
5. Identify the systematic pattern in disagreements
6. Edit the prompt to address that pattern
7. Go to step 2
8. Repeat until TPR > 90% and TNR > 90%
```

### What to Look for When Inspecting Disagreements

When the judge labels something Fail and the human labeled it Pass (false positive), look for:
- Is the judge applying the failure mode definition too broadly?
- Is the in-scope/out-of-scope boundary unclear in the prompt?
- Did the judge miss that the bot correctly escalated?

When the judge labels something Pass and the human labeled it Fail (false negative), look for:
- Is the judge missing a subtle form of the failure mode?
- Are the few-shot examples only covering obvious cases?
- Does the Fail definition need a more specific example?

In practice, FM1 false positives often come from responses where the bot correctly says something like "digital products are not in our supported categories" — which is an in-scope negative claim (the categories ARE in the KB), not an out-of-scope one. Fixing this requires clarifying the distinction in the prompt and adding a few-shot example that shows this case.

### The 90% Threshold

The book recommends TPR > 90% and TNR > 90% before using the judge in production. This is a guideline, not a law. But it matters because:

- Below 90% TPR, you are missing more than 10% of real failures. The corrected success rate estimate has wider confidence intervals.
- Below 90% TNR, you are flagging more than 10% of good responses as failures. The correction works, but the wider the error, the less confidence you have in the estimate.

If you can't reach 90% after several iterations, that is diagnostic: either the failure mode definition is too vague (tighten it), or the judge model is not capable of the required reasoning (use a larger model).

---

## 6. TPR and TNR — Why These Metrics and Not F1

When evaluating a binary classifier, you have choices: precision, recall, F1, accuracy, TPR, TNR. The book uses TPR and TNR. Here is why.

### Definitions

Let:
- TP = judge says Fail, human says Fail
- TN = judge says Pass, human says Pass
- FP = judge says Fail, human says Pass
- FN = judge says Pass, human says Fail

Then:
- **TPR** (True Positive Rate) = TP / (TP + FN) = fraction of actual failures the judge correctly labels Fail
- **TNR** (True Negative Rate) = TN / (TN + FP) = fraction of actual passes the judge correctly labels Pass

### Why Not F1?

F1 is the harmonic mean of precision and recall. It is appropriate when you care about a classifier's performance at a specific operating threshold. It is not appropriate here because our goal is not to rank or filter — it is to estimate a proportion.

We are using the judge to estimate the **true pass rate** of the chatbot: what fraction of responses would a human label Pass? The judge sees every production trace and returns a label. Those labels give us an observed pass rate `p_obs`. But `p_obs` is biased because the judge makes errors in two directions:

- Some failures are mislabeled Pass (FN). This makes `p_obs` too high.
- Some passes are mislabeled Fail (FP). This makes `p_obs` too low.

TPR tells you how often the judge catches real failures. TNR tells you how often it avoids flagging real passes. These are exactly the two error modes that bias `p_obs` in opposite directions. The Rogan-Gladen formula (next section) takes TPR and TNR as inputs to correct the bias.

F1 does not map cleanly to these two directions of bias. Accuracy does not either, because it conflates the two. Only TPR and TNR decompose the error in the way the bias correction formula requires.

---

## 7. The Rogan-Gladen Bias Correction (Ch5 §5.6)

### The Problem

Suppose you run the FM1 judge on 500 production traces. The judge says 420 are Pass and 80 are Fail. Raw observed pass rate: `p_obs = 420/500 = 0.84`.

But the judge has TPR = 0.82 and TNR = 0.91. It misses 18% of real failures and flags 9% of real passes. The true pass rate is not 0.84.

### The Formula

The Rogan-Gladen estimator corrects for this:

```
θ̂ = (p_obs + TNR - 1) / (TPR + TNR - 1)
```

Where:
- `p_obs` = raw observed pass rate from the judge
- `TPR` = true positive rate measured on your labeled test set
- `TNR` = true negative rate measured on your labeled test set
- `θ̂` = estimated **true** pass rate (what a human would observe)

### Working Through the Example

With `p_obs = 0.84`, `TPR = 0.82`, `TNR = 0.91`:

```
θ̂ = (0.84 + 0.91 - 1) / (0.82 + 0.91 - 1)
   = 0.75 / 0.73
   = 1.027...
```

Wait — that's above 1.0, which is impossible for a probability. This can happen when the observed pass rate is higher than what the error rates can consistently explain. In practice, clamp to [0, 1]. It signals the judge may be better calibrated than estimated, or the sample has noise.

With more realistic numbers — `p_obs = 0.78`, `TPR = 0.88`, `TNR = 0.93`:

```
θ̂ = (0.78 + 0.93 - 1) / (0.88 + 0.93 - 1)
   = 0.71 / 0.81
   = 0.877
```

The judge said 78% pass. The corrected estimate is 87.7% pass. The gap (about 10 percentage points) represents the bias introduced by the judge's error rate.

### Why This Matters Practically

A product team tracking "what fraction of chatbot responses are acceptable?" needs a reliable number to monitor. If the judge systematically misses failures, the metric looks better than reality. If the judge over-flags, it looks worse. The Rogan-Gladen correction gives you the unbiased estimate — the number that corresponds to what you would get if humans labeled every trace.

This is the same correction used in epidemiology to estimate true disease prevalence from an imperfect test. The mathematical derivation assumes the judge errors are independent of each other and of the true label. In practice this is approximately true for LLM judges on well-defined criteria.

### The Confidence Interval

Because `p_obs` is estimated from a finite sample, `θ̂` is also uncertain. We compute a 95% bootstrap confidence interval:

```
Algorithm 1 (from the course):
1. Collect N judge predictions (0=Pass, 1=Fail) on unlabeled traces
2. B = 2000 bootstrap iterations
3. For each iteration b:
   a. Sample N predictions with replacement
   b. Compute p_obs_b = mean of sampled predictions  (fraction labeled Pass)
   c. Apply Rogan-Gladen: θ̂_b = (p_obs_b + TNR - 1) / (TPR + TNR - 1)
   d. Clamp θ̂_b to [0, 1]
4. Sort the B estimates θ̂_1, ..., θ̂_B
5. 95% CI = [2.5th percentile, 97.5th percentile]
```

The bootstrap CI captures sampling uncertainty in `p_obs` but not uncertainty in TPR/TNR (those come from the test set, which is also finite). For a complete uncertainty estimate you would propagate uncertainty in TPR/TNR as well, but the bootstrap on `p_obs` is usually the dominant source.

---

## 8. The `judgy` Library

The course provides a reference implementation of the Rogan-Gladen estimator and bootstrap CI as a Python library:

```
https://github.com/ai-evals-course/judgy
```

### Installation

```bash
pip install judgy
```

### Basic Usage

```python
from judgy import estimate_success_rate

# judge_labels: list of "Pass" or "Fail" strings from your judge
# tpr: measured on your labeled test set
# tnr: measured on your labeled test set

result = estimate_success_rate(
    judge_labels=judge_labels,
    tpr=0.88,
    tnr=0.93,
    n_bootstrap=2000,
    confidence=0.95,
)

print(f"Corrected pass rate: {result.theta:.3f}")
print(f"95% CI: [{result.ci_low:.3f}, {result.ci_high:.3f}]")
```

### What the Library Returns

- `result.p_obs`: raw observed pass rate from the judge
- `result.theta`: Rogan-Gladen corrected estimate
- `result.ci_low`, `result.ci_high`: 95% bootstrap confidence interval bounds

The library also validates that `TPR + TNR > 1` — if this condition is violated, the formula is undefined (the denominator is zero or negative) and the estimator should not be used. This condition means the judge is better than random chance, which should be true for any well-designed judge.

---

## 9. Files in This Stage

```
stage-5-llm-judge/
├── README.md                  ← this file
├── judge_prompts/
│   ├── fm1_out_of_scope.py    ← FM1: Confident Out-of-Scope Claim
│   ├── fm2_invented_troubleshooting.py  ← FM2: Invented Troubleshooting Steps
│   └── fm3_invented_process.py          ← FM3: Invented Process Details
├── label_traces.py            ← human labeling CLI with train/dev/test split
├── evaluate_judge.py          ← computes TPR/TNR on labeled test or dev set
├── estimate_success_rate.py   ← Rogan-Gladen correction + bootstrap CI
└── labeled_data/
    ├── train_ids.json         ← IDs in training split (used for prompt examples)
    ├── dev.json               ← human-labeled dev traces
    └── test.json              ← human-labeled test traces (hold out until final eval)
```

---

## 10. Running the Workflow End to End

### Step 1: Label traces

```bash
cd stage-5-llm-judge
python3 label_traces.py
```

This loads all 36 traces from Stage 2, splits them 15/42/43 with a fixed seed, and prompts you to label each trace for FM1–FM5. Labels are saved to `labeled_data/`.

When labeling, you will see:
```
=== TRACE dev/003 ===
Query: My stream keeps disconnecting whenever I switch from Wi-Fi to mobile...
Response: ...avoid using cell signal boosters or VPNs that might interfere...

FM1 - Confident Out-of-Scope Claim [p/f/s]? s
FM2 - Invented Troubleshooting Steps [p/f/s]? f
FM3 - Invented Process Details [p/f/s]? s
FM4 - Failure to Escalate [p/f/s]? s
FM5 - Potentially Misleading Inference [p/f/s]? s
```

Enter `p` for Pass, `f` for Fail, `s` to skip (unlabeled).

### Step 2: Iterate the judge on dev

```bash
python3 evaluate_judge.py --judge fm1 --split dev
```

Output:
```
FM1 Judge Evaluation — Dev Split (15 traces)

Confusion Matrix:
              Judge: Pass    Judge: Fail
Human: Pass       11             1
Human: Fail        2             1

TPR: 0.333  (1 / 3 actual failures caught)
TNR: 0.917  (11 / 12 actual passes correctly labeled)

Disagreements to inspect:
  Trace dev/012: Human=Fail, Judge=Pass
    Query: "Can I schedule a live stream to start at midnight..."
    Response: "eBay Live does not support scheduling..."
    Judge reasoning: "The response answers about scheduling which may be partially in KB..."
  ...
```

The low TPR (0.33) tells you the judge is missing failures. Inspect the reasoning, identify the pattern, refine the prompt. Re-run. Repeat until TPR and TNR both exceed 90%.

### Step 3: Final evaluation on test (do this once)

```bash
python3 evaluate_judge.py --judge fm1 --split test
```

This is the final, official measurement. Do not look at test traces during development. Do not iterate after seeing test results.

### Step 4: Estimate the true production success rate

```bash
python3 estimate_success_rate.py --judge fm1 --traces ../stage-2-trace-dataset/traces/traces_20260419_113459.json
```

Output:
```
FM1 Success Rate Estimation
===========================
Traces evaluated: 36
Raw pass rate (judge): 0.833
TPR (from test set):   0.909
TNR (from test set):   0.923

Rogan-Gladen corrected rate: 0.871
95% Bootstrap CI:            [0.798, 0.944]

Interpretation: An estimated 87.1% of chatbot responses are free of the
FM1 failure mode (Confident Out-of-Scope Claim), with 95% confidence the
true rate is between 79.8% and 94.4%.
```

---

## 11. Common Pitfalls

These are the mistakes the book specifically warns about, drawn from the authors' experience building eval systems in production.

### 11.1 Omitting Examples from the Prompt

The most common error. A judge prompt with clear definitions but no examples performs significantly worse than one with two or three examples. LLMs apply abstract definitions inconsistently without anchor cases.

Fix: always include at least one PASS example and one FAIL example. Use borderline cases from your training split — not the obvious ones.

### 11.2 Evaluating Multiple Criteria in One Prompt

Tempting because it seems efficient: "Does this response have FM1, FM2, or FM3?" But the judge conflates them, misses the subtle ones, and you can't measure accuracy for each separately.

Fix: one judge per failure mode. Run them in parallel on the same trace if needed.

### 11.3 Skipping the Alignment Step

Writing the judge and assuming it works without ever comparing against human labels. This is the most dangerous mistake because it gives you a metric that looks credible but may have 40% error rate.

Fix: always compute TPR and TNR on a human-labeled test set before using the judge for any business decision.

### 11.4 Not Having a Test Set (Evaluating on Dev = Overfitting)

If you iterate the prompt on dev and then measure accuracy on dev, you are measuring how well you adapted to that specific set of 15 traces. The reported accuracy is optimistic.

Fix: hold out a test set from the beginning. Never look at it during development. Evaluate on it exactly once.

### 11.5 Using a Too-Weak Judge Model

GPT-4.1-mini works well for FM1 and FM2 because the criteria are concrete. For FM5 (Potentially Misleading Inference), the judge needs to reason about what is and is not stated in the knowledge base — a subtler task. If accuracy is stuck below 80% after multiple iterations, try a stronger model (GPT-4.1 or o4-mini).

### 11.6 Forgetting to Clamp the Rogan-Gladen Output

The formula can return values outside [0, 1] due to sampling noise. Always clamp to [0, 1] before reporting. A value slightly above 1.0 (e.g., 1.01) means the judge is performing better than estimated and the corrected rate is effectively 100%.

---

## 12. Connection to Chapters 1–4

The chapter sequence in the book is deliberate:

| Chapter | Stage | What You Built                                                          |
|---------|-------|-------------------------------------------------------------------------|
| Ch 1–2  | 1–2   | The chatbot and a representative trace dataset                          |
| Ch 3    | 3     | Open coding — raw observations about what could go wrong                |
| Ch 4    | 4     | Axial coding — consolidated failure modes with clear definitions        |
| Ch 5    | 5     | LLM judges that operationalize those definitions + statistical rigor    |

Stage 5 only works because Stages 3 and 4 produced precise failure mode definitions. A vague definition like "the bot hallucinated" cannot be operationalized as a judge prompt. "The bot stated a definitive negative claim about a topic not in the knowledge base" can.

This is why the book emphasizes the qualitative work in Chapters 3 and 4. The sharpness of your judges is bounded by the sharpness of your failure mode definitions.

---

## 13. Next: Stage 6 — Retrieval Eval

Stage 5 evaluates the chatbot's *output*. Stage 6 evaluates the *retrieval* step — if the chatbot uses RAG, does the retriever actually find the right knowledge base chunks?

Stage 6 builds:
- Synthetic (query, gold chunk) pairs
- Recall@k and Mean Reciprocal Rank (MRR) metrics
- A pipeline that measures retrieval quality independently of generation quality

The failures you found in Stage 5 (FM1, FM3) are often retrieval failures in disguise: the bot gave a wrong answer because the retriever didn't return the relevant KB chunk. Stage 6 lets you separate those two failure sources.
