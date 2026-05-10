# Stage 2 — Evaluation Foundations

> **Course reference:** Chapter 2 — *LLMs, Prompts, and Evaluation Basics*
> Shankar & Husain (2026)

This stage has no code to run. It is a conceptual foundation. Every technical decision in Stages 3–10 connects back to the ideas here. Read this before touching any scripts.

---

## 1. What LLMs Are Good and Bad At

Understanding LLM limitations is not optional context — it directly determines what your evals must catch.

### Strengths
- Fluent, coherent text generation
- Summarization, translation, question answering
- Following instructions from a prompt without retraining
- Generalizing to new tasks with few examples (few-shot learning)

### Weaknesses — The Ones That Matter for Evals

**Hallucination.** LLMs have no internal notion of truth. Their objective is to produce statistically likely text, not factually verified text. A model can confidently assert incorrect claims. This is not a bug that will be fixed — it is a structural property of how they work.

> "There is no inherent mechanism to cross-check outputs against trusted knowledge sources."
> — Shankar & Husain (2026), Ch. 2

For the eBay Live chatbot: this is why FM1, FM3, FM4 exist. The model invents confident-sounding policies not because it is trying to deceive — it is doing exactly what it was trained to do, which is produce plausible text.

**Prompt sensitivity.** Small changes in phrasing — rewording a question, shifting example order, introducing irrelevant tokens — can produce dramatically different outputs. This means your test queries must be representative of real user phrasings, not cleaned-up versions.

For the eBay Live chatbot: this is why Stage 3 uses structured dimensions instead of hand-crafting "the best possible" test questions. You want to see the chatbot under realistic query variation, not ideal conditions.

**Reliability.** Identical prompts can yield different outputs (especially at temperature > 0). Evaluation infrastructure must tolerate this — either by running multiple samples or by using deterministic checks where possible.

---

## 2. Reference-Based vs. Reference-Free Metrics

This is the most fundamental classification in eval design. Every metric you build in Stages 7–10 is one or the other.

### Reference-Based Metrics

Compare the model's output against a **known correct answer** (a "golden" or "reference" output).

```
model output ──→ compare ──→ score
reference    ──→
```

Examples:
- Does the response contain the correct fee percentage (12.9–15%)?
- Does the SQL output match the expected query?
- Does the generated email contain all required fields?

**When to use:** When you can define a correct answer in advance. Strong for factual questions, structured outputs, regression testing.

**For eBay Live:** "Does the response correctly state that bids cannot be retracted?" — this is reference-based. The KB has the answer. You check against it.

### Reference-Free Metrics

Evaluate the output based on **inherent properties** — without a golden answer.

```
model output ──→ check property ──→ score
```

Examples:
- Does the response invent troubleshooting steps? (FM2)
- Does the response make a confident negative claim about something not in the KB? (FM1)
- Does the response admit uncertainty when it should?

**When to use:** When correct outputs vary (multiple valid answers exist) or when you are measuring behavioural properties of the model rather than factual accuracy.

**For eBay Live:** Most of our Stage 7 (LLM Judge) checks are reference-free. We are not checking whether the response matches a golden answer — we are checking whether it exhibits a specific failure pattern.

### Why This Distinction Matters

Reference-based metrics are more reliable but require labeled ground truth. Reference-free metrics are more flexible but harder to validate — you must check that the automated evaluator agrees with human judgment (which is what TPR/TNR measures in Stage 7).

> "Hamel's Note: Reference-based metrics are preferred when it is feasible to have them."
> — Shankar & Husain (2026), Ch. 2

Practical rule: use reference-based where you can, reference-free where you must.

---

## 3. Foundation Model Evals vs. Application-Centric Evals

This distinction explains why leaderboard scores don't tell you whether your chatbot works.

### Foundation Model Evals (Benchmarks)

Assess the general capabilities of the base LLM: MMLU, HELM, GSM8k. They measure math, coding, general reasoning. They are standardized, public, and comparable across models.

**Use them for:** Initial model selection. A higher benchmark score is a weak prior that the model might work better for your task.

**Do not use them for:** Deciding whether your specific chatbot works for your specific users.

### Application-Centric Evals

Assess whether **your specific pipeline** performs well on **your specific task** with **your realistic data**.

For the eBay Live chatbot, this means:
- Does it correctly apply the eBay Money Back Guarantee to counterfeit item questions?
- Does it correctly identify when a seller question requires the Seller Interest Form?
- Does it correctly stay within the knowledge base on out-of-scope questions?

None of these appear in MMLU. A model that scores 90% on MMLU might score 60% on your eBay Live eval — or vice versa. The only way to know is to build your own evals.

> "Shreya's Note: Think of foundation model evals as standardized tests. When hiring people, we rely on more than standardized test scores."
> — Shankar & Husain (2026), Ch. 2

---

## 4. How to Elicit Evaluation Labels

Before you build automated evaluators, someone — a human — must label some traces as Pass or Fail. There are three methods.

### Direct Grading (Pass/Fail)

An evaluator reads the trace and assigns a binary label: Pass or Fail.

**Pros:** Simple, fast, clear, easy to compute TPR/TNR against.
**Cons:** Requires very precise rubric definitions to be consistent across annotators.

**This is what we use** in Stages 4–6.

### Direct Grading (Likert Scale 1–5)

An evaluator rates quality on a 1–5 scale.

**Pros:** More nuanced than binary.
**Cons:** Inconsistent across annotators without a very detailed rubric. Hard to compute TPR/TNR against. Hard to automate.

> "Forcing binary decisions about specific failure modes — whether a problem occurred or not — produces more reproducible annotations."
> — Shankar & Husain (2026), Ch. 3

**We avoid Likert scales.** Binary is harder to define but far more reliable and automatable.

### Pairwise Comparison

Present two responses (A and B) to the same query. Ask: which is better?

**When to use:** When you are comparing two versions of the chatbot (e.g., before and after a prompt change) and single-trace scoring is too noisy.

**For eBay Live:** Useful in Stage 10 when measuring whether a prompt improvement actually helped.

---

## 5. Prompting Fundamentals

The system prompt is the most important variable in your chatbot. Understanding its structure determines how well you can diagnose failures.

A well-structured prompt has 7 components (Ch. 2 §2.2). Here is how each applies to the eBay Live chatbot:

| Component | eBay Live Example |
|-----------|------------------|
| **Role and Objective** | "You are a helpful customer support agent for eBay Live" |
| **Instructions / Response Rules** | "Only state facts explicitly listed above. Never invent fees, features, or policies." |
| **Context** | The full eBay Live knowledge base (policies, categories, fees, etc.) |
| **Examples (Few-Shot)** | Not currently used — a Stage 10 improvement opportunity |
| **Reasoning Steps (CoT)** | Not currently used |
| **Output Format** | "Keep responses concise and friendly" |
| **Delimiters** | `##` section headers in the system prompt |

**Key insight:** The "Rules" section of the eBay Live system prompt is doing a lot of heavy lifting. It says "Never invent fees, features, or policies." But as Stage 4 (open coding) will show, the model violates this rule in ~30% of out-of-scope traces. The rule is not sufficient — you need evals to catch the violations.

---

## 6. What "Good" Means for the eBay Live Chatbot

Before building any metric, you must define what you are measuring. For the eBay Live chatbot, "good" means:

| Property | Definition | How measured |
|----------|-----------|-------------|
| **Groundedness** | Every factual claim is traceable to the KB | FM1, FM3, FM5 judges (Stage 7) |
| **Completeness** | Key details (fees, requirements, caveats) are included | Reference-based checks (Stage 7) |
| **Appropriate escalation** | Bot says "I don't know" when genuinely outside KB | FM4 judge (Stage 7) |
| **Retrieval quality** | Correct KB chunk is retrieved (when using RAG) | Recall@k (Stage 8) |
| **No invented troubleshooting** | No technical steps not in KB | FM2 judge (Stage 7) |

These five properties define the evaluation space for this project. Every metric in Stages 7–10 measures one or more of them.

---

## 7. Key Takeaways Before You Start

1. **Every failure mode we find in Stage 4 is a hallucination variant.** The eBay Live chatbot hallucinates negative policies, troubleshooting steps, URLs, and inferences. Understanding why (structural LLM limitation, not a fixable bug) helps you build evals that are durable.

2. **Use binary labels, not Likert scales.** Binary is harder to define but far more reliable and automatable downstream.

3. **Reference-free metrics are powerful but must be validated.** An LLM judge that says "FM1 is present" must be tested against human labels before you trust it.

4. **Benchmark scores don't predict your chatbot's quality.** Only application-centric evals do.

5. **The system prompt is a hypothesis.** "Never invent policies" is a hypothesis about the model's behaviour. Stage 4 tests that hypothesis. Stages 6–7 quantify how often it holds.

---

## Next: Stage 3 — Trace Dataset

Now that you know what "good" means and how metrics work, collect the data you'll need to measure it.
