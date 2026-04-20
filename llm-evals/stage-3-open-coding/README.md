# Stage 3 — Open Coding

> "For each trace, read carefully and write brief notes about what you observe: where outputs are incorrect, where actions are surprising, or where the behavior feels wrong or unexpected."
> — Shankar & Husain, *Application-Centric AI Evals for Engineers and Technical Product Managers* (2026), Ch. 3 §3.3

---

## What This Stage Is

You have collected traces. You do not yet know what is wrong with them. Stage 3 is how you find out.

Open coding is the first pass over your trace data. You read each trace and write a short, specific, descriptive note about what you observe — what is surprising, wrong, or suspicious. You are not yet building categories. You are not yet counting. You are observing and labeling, one trace at a time.

The term comes from **grounded theory**, a qualitative research methodology developed by Glaser and Strauss (1967). In grounded theory, open coding means reading raw data and attaching short descriptive labels to what you see — labels that are grounded in the data itself, not in a framework you brought in ahead of time. The categories emerge from the data. You don't impose them.

For LLM evals, open coding means: annotate traces with freeform notes before you have a taxonomy. The taxonomy will come in Stage 4 (axial coding). Right now, your job is to observe.

---

## The Core Principle: Annotate at the Trace Level, Not the Turn Level

This is the most important methodological point in Ch. 3 §3.3, and it is easy to miss.

In a multi-turn conversation, it is tempting to annotate each turn individually — "this turn had a hallucination," "this turn was fine." Do not do this. **Annotate at the trace level.** Read the entire conversation from start to finish before writing anything.

Why? Because many failures are only visible across the full flow.

Consider a trace where the first user message asks about seller eligibility and the agent correctly recites the KB. The second message asks a follow-up and the agent invents a scheduling feature. If you annotated turn by turn, you might call the first turn a pass and the second a fail. But viewed as a full trace, the failure is in turn 2, and it is the *first* failure — the agent satisfied the buyer's initial question, then went off-KB when the conversation got more specific. The trace-level view lets you see that.

In the eBay Live context: a buyer asking how to place a bid might get a mostly-correct first response. But if the agent then invents re-bidding guidance ("avoid placing duplicate bids") in response to a follow-up about a frozen stream, the failure is at the trace level. You can only catch it by reading the whole thing.

---

## Focus on the First (Most Upstream) Failure

When you identify a bad trace, your job is to locate the **first failure** — the earliest point where something goes wrong.

This matters because errors cascade. Once an agent states something incorrect, everything it builds on top of that statement is potentially contaminated. The downstream failures are not independent — they are consequences of the first one. Counting them separately inflates your failure count and obscures the actual root cause.

### Example: Cascade from a Single Upstream Error

**Trace 22** (seller/how-to/clear): The agent is asked how to set up a first eBay Live stream. It gives a mostly reasonable answer, then near the end says: *"If you want to get started, first submit the interest form at ebay.com/live and wait for approval."*

The KB mentions the "eBay Live Seller Interest Form" but does not provide a specific URL. `ebay.com/live` is invented. That is the first failure.

Everything after that sentence — advice about waiting for approval, downstream tips — may be fine, but the trace already crossed a line. You label the first failure, not the full list of subsequent suspect statements.

**Trace 15** (buyer/troubleshooting/edge-case): The agent is asked whether a bid went through after the stream froze. It says: *"it's safer to try placing your bid again once the stream is working. Just be aware that all bids are final, so avoid placing duplicate bids for the same amount."*

The "avoid placing duplicate bids" advice is internally contradictory — if all bids are final, the risk isn't placing duplicate bids of the same amount, it is placing a higher bid than intended. The invented guidance around re-bidding is the first failure. The cascade here is subtle: the agent was trying to be helpful, invented nuance that the KB doesn't contain, and produced contradictory advice in the same breath.

---

## The Difference Between Open Coding and Premature Categorization

This is the most common mistake made by annotators who come from a software quality background.

**Premature categorization** means you open the spreadsheet, create columns like "hallucination," "refusal failure," "out-of-scope error," and then try to assign each trace to one of those buckets. You have imported a taxonomy before you have earned it from the data.

The problem: your pre-imported categories will capture what you were already looking for. They will miss failure types you hadn't thought of. They will force genuinely distinct failures into the same bucket because the bucket names are too broad. And they will give you false confidence — "I've categorized all the failures" — when you've only sorted them into boxes you defined before looking.

**Open coding** means you resist naming categories until after you've read at least 20–30 traces. You write specific, descriptive notes. You let the categories emerge.

### Good Open Code vs. Bad Open Code

Here are two ways to annotate the same trace (Trace 13 — buyer getting an error placing a bid):

**Bad open code (too vague, pre-categorical):**
> "Hallucination — invented info"

This tells you nothing specific. Was it a hallucinated policy? A hallucinated URL? A hallucinated technical step? When you cluster codes in Stage 4, this label will be useless because it could apply to dozens of different failure types.

**Good open code (specific, descriptive, grounded in the trace):**
> "Invented troubleshooting step (restart app, clear cache) not in KB — agent escalated from KB-grounded prerequisites to generic tech support advice"

This tells you exactly what happened: the agent started with legitimate KB content (account eligibility, saved payment details) and then appended invented troubleshooting steps. When you cluster in Stage 4, you will be able to ask: "Is this the same pattern as Trace 33 (invented cell signal booster advice)? Is it the same as Trace 22 (invented URL)?" Maybe they all cluster under "invented specific technical detail" — but you let the data tell you that.

### The eBay Live Context

The eBay Live chatbot is grounded in a specific KB. The KB covers buyer eligibility, bidding mechanics, seller eligibility, approved categories, and technical setup requirements. It does not cover scheduling features, VPN interference, specific troubleshooting steps, or exact URLs. 

A good open code names *which specific thing* was invented or wrong — not just that something was invented. "Confident negative claim about feature not in KB" is more useful than "hallucination" because it points to a specific failure mode: the agent said something is *not* supported when the KB is simply silent on the question.

---

## The "Top-Down" Fallback: Using Known Categories as Lenses

Open coding is primarily **bottom-up**: you let observations from the data drive your labels. But sometimes you are stuck. You've read a trace, something seems off, but you can't articulate it.

In that case, Shankar & Husain recommend using known LLM failure categories as **lenses** — prompts to help you look, not buckets to assign into. Ch. 3 §3.3 names three common categories:

| Lens | What to look for |
|------|-----------------|
| **Hallucination** | Facts, URLs, features, steps that are stated with confidence but are not in the KB or are contradicted by it |
| **Structured output issues** | Responses that fail to follow format requirements, miss required fields, or misuse JSON/lists when the system prompt requires them |
| **Constraint violations** | Responses that violate explicit system-level rules — e.g., answering questions outside scope when the system prompt says to defer, or making claims beyond KB boundaries |

Use these as diagnostic questions: "Does this look like a hallucination? Does this look like a constraint violation?" But then write a specific open code that describes what *specifically* happened in *this* trace. "Constraint violation: stated definitive policy on pre-recorded video when KB is silent, should have deferred" is better than just "constraint violation."

Do not force traces into these categories. If none of the three lenses fit, that is fine — write your observation in plain language. The Stage 4 clustering step will sort it out.

---

## Binary Judgment: Acceptable or Unacceptable

For each trace, you make a binary judgment: acceptable or not acceptable.

This is intentional and deliberate. It would be easier to use a 5-point Likert scale. It would feel more nuanced. It would be less useful.

> "Making a clear yes or no decision forces sharper thinking than vague scores (e.g., 3 out of 5)."
> — Shankar & Husain (2026), Ch. 3 §3.3

A score of 3 is a way of avoiding the question. When you score something a 3, you are saying: "I'm not sure, and I don't want to commit." Open coding is not a place for that kind of hedging. You are building an eval dataset. The downstream stages — axial coding, failure mode definitions, automated eval criteria — all depend on clear signal.

The binary judgment forces you to decide: **Would a real user be harmed, misled, or left worse off than if they had received no answer?** If yes, the trace is unacceptable. If no — even if the response is imperfect or incomplete — it is acceptable.

### Applying the Binary in the eBay Live Context

**Trace 21** is a borderline case. The agent says: *"The platform focuses on real-time auctions and fixed-price sales of physical items in approved categories."* This is not exactly in the KB, but it is directionally accurate and not likely to mislead. A user reading this would not be harmed. Call it acceptable.

**Trace 30** fails the binary test. The agent says digital products "are not supported for live sale on eBay Live at this time." The KB doesn't say this. A seller who had digital products and read this response would take it as authoritative policy and would be misled. The KB is silent on this question; the agent should have said so. Call it unacceptable.

The difference: Trace 21 makes a general, reasonable, non-harmful inference. Trace 30 makes a specific, definitive, policy-like claim that is not grounded in the KB. Both involve text that isn't literally in the KB. Only one causes real potential harm to the user.

---

## What to Write in Each Annotation Field

| Field | What to write | Example |
|-------|--------------|---------|
| `open_code` | A specific, descriptive note about what you observed. Name the specific error, not just the category. 1–3 sentences. | "Agent gave KB-grounded eligibility requirements, then appended invented URL (ebay.com/live) not found in KB. URL invention is the departure point." |
| `first_failure` | One phrase identifying the earliest failure point in the trace. | "Invented specific URL for interest form" |
| `acceptable` | `true` or `false`. No maybes. | `false` |

### Rules for `open_code`

- Be specific about *what* was invented or wrong, not just *that* something was wrong
- Name the KB concept that was violated or departed from (e.g., "KB is silent on scheduling features")
- Note when the agent should have said "I don't know" instead of answering
- Note when correct KB content was stated first (partial credit in understanding the failure)

### Rules for `first_failure`

- One phrase only — not a sentence, not a paragraph
- Name the thing that went wrong, not the downstream effects
- Examples: "Invented re-bidding guidance", "Stated definitive policy not in KB", "Invented URL for seller interest form", "Added generic tech support steps beyond KB scope"

### Rules for `acceptable`

- `true` means: a real user could rely on this response without being harmed or materially misled
- `false` means: a real user would be worse off than if they had received no answer, or would be misled into a false belief about eBay Live
- A response can be incomplete and still be acceptable (Trace 19: correctly defers on discounts)
- A response can be partially correct and still be unacceptable if the incorrect part would mislead (Trace 15: correct explanation of bid confirmation, then wrong guidance on re-bidding)

---

## When to Stop: Theoretical Saturation

Open coding has a stopping criterion: **theoretical saturation**.

You have reached theoretical saturation when:
1. You have annotated at least 20 unacceptable traces, AND
2. You are no longer seeing fundamentally new failure types

The second condition is the important one. If your last five unacceptable traces all produced open codes that look like variations of patterns you've already seen, you are probably saturated. If each new trace is producing an open code that doesn't fit anything you've seen before, keep going.

In the eBay Live dataset (36 traces), you should expect to see a handful of distinct failure patterns — somewhere between 3 and 6 is typical for a well-scoped KB-grounded chatbot. The failure types you find might look something like:
- Invented technical steps not in KB
- Invented specific facts (URLs, feature names) not in KB
- Confident negative claims about features the KB is silent on
- Out-of-scope product framing invented to fill a gap

But do not pre-load these. Let the traces show you. Once you've seen the same pattern five or six times and your open codes are starting to repeat themselves, you have reached saturation for that pattern. When all patterns are saturating simultaneously, you are done with Stage 3.

---

## Common Pitfalls

**1. Over-categorizing too early**

You annotate three traces and notice "hallucination" shows up. You then start using "hallucination" as your open code for everything suspicious. By trace 20, all your open codes are "hallucination" and you have no idea what actually went wrong in each case. Stage 4 will be useless.

*Fix:* Commit to writing one new, specific sentence for every trace. Even if you've seen this pattern before, describe what happened in this trace.

**2. Skipping bad traces**

Open coding is tedious. You find a trace where the agent did something off, but it's subtle and you're tired. You mark it acceptable and move on. You lose data.

*Fix:* Use the binary judgment as a forcing function. Ask yourself: "Would a real eBay Live user be misled by this?" If the answer is "maybe," lean toward false. You can always revisit; you can't un-skip.

**3. Using generic labels like "hallucination" without specifics**

"Hallucination" is a category, not an observation. It belongs in Stage 4 (axial coding), not Stage 3. In Stage 3, your job is to describe what was hallucinated, in what context, and what the KB would have said instead.

*Fix:* Every time you write "hallucination," ask yourself: "Hallucinated *what*?" and write that instead.

**4. Conflating acceptable-with-caveats and unacceptable**

Sometimes the agent says something that is 80% correct and adds one invented detail. You feel bad calling it unacceptable because most of it was right. But if that 20% is something a user would rely on, it's unacceptable.

*Fix:* In your `open_code`, note what was correct (this helps in Stage 4). But let the 20% determine your `acceptable` judgment. The binary is about whether a real user would be harmed, not about grading overall quality.

**5. Confusing "not in KB" with "wrong"**

Sometimes the agent says something that is probably true about eBay in general but is not in the KB. This is tricky. If the agent is drawing on correct general knowledge about eBay and it doesn't contradict the KB, it may be acceptable. If the agent is making a specific policy or technical claim that cannot be verified from the KB, it is unacceptable — because the chatbot's job is to answer from the KB, not to improvise.

*Fix:* Ask "Is the agent claiming to know something about eBay Live that it cannot know from the KB?" If yes, that is a failure, even if the claim happens to be true.

---

## Annotation Fields Summary Table

| Trace | What makes it interesting | Expected `acceptable` |
|-------|--------------------------|----------------------|
| buyer / policy / clear | Tests basic MBG knowledge | `true` |
| buyer / how-to / clear | Tests core bidding mechanics | `true` |
| buyer / eligibility / edge-case | Tests edge case (non-US account) | `true` |
| buyer / troubleshooting / clear | Classic KB-grounding failure | `false` |
| buyer / troubleshooting / edge-case | Subtle internally contradictory guidance | `false` |
| buyer / out-of-scope / clear | Invents product framing for OOS question | `false` |
| seller / policy / clear | Correct deferral on unknown topic | `true` |
| seller / policy / edge-case | Over-specific framing but directionally OK | `true` (borderline) |
| seller / how-to / clear | Invents specific URL | `false` |
| seller / how-to / ambiguous | Invents scheduling feature | `false` |
| seller / how-to / edge-case | Confident policy claim not in KB | `false` |
| seller / eligibility / clear | Comprehensive KB-grounded answer | `true` |
| seller / eligibility / edge-case | Correctly inferred from KB | `true` |
| seller / categories / edge-case | Confident "not supported" claim not in KB | `false` |
| seller / troubleshooting / edge-case | Invents specific technical advice (VPN, boosters) | `false` |
| seller / out-of-scope / clear | Invents product framing and redirect advice | `false` |
| seller / out-of-scope / ambiguous | Invents technical integration specificity | `false` |
| seller / out-of-scope / edge-case | Confident negative claim on feature not in KB | `false` |

---

## How to Run the Annotation Tool

```bash
cd /path/to/stage-3-open-coding
python3 open_coding.py [path/to/traces.json]
```

If no trace file is specified, it will look for the most recent `traces_*.json` file in `../stage-2-trace-dataset/traces/`.

The tool shows each trace one at a time and prompts for:
1. Your open code (freeform note — what did you observe?)
2. The first failure (one phrase)
3. Acceptable or not (y/n)

Press Enter with no input to skip a trace. The tool saves progress after every annotation to `open_codes/open_codes_YYYYMMDD_HHMMSS.json`.

---

## What's in This Directory

| File / Directory | Purpose |
|-----------------|---------|
| `open_coding.py` | Interactive CLI — walks through traces, collects annotations, saves progress |
| `open_codes/` | Saved annotation JSONs from each session |
| `open_codes/open_codes_sample.json` | Pre-populated sample annotations showing good open coding for 20 traces |

---

## Sample Annotations

See `open_codes/open_codes_sample.json` for worked examples of good open coding across 20 of the 36 traces. These demonstrate:
- What specific, grounded open codes look like vs. generic labels
- How to identify first failure points in cascade scenarios
- How to apply the binary judgment on borderline cases
- The range of failure types present in this dataset

---

## Next: Stage 4 — Axial Coding

Once you have open-coded at least 20 unacceptable traces and reached theoretical saturation, move to Stage 4. Axial coding takes all your open codes and clusters similar ones into a small, coherent set of binary failure modes.

The key question in Stage 4: "Which of my open codes are describing the same underlying failure, just in different surface forms?" A label like "invented re-bidding guidance" and "invented scheduling feature" might both be instances of "agent invented a capability/feature not documented in KB." That abstraction is what axial coding produces.

The quality of Stage 4 depends entirely on the quality of Stage 3. Vague open codes produce vague failure modes. Specific, grounded open codes produce actionable, automatable eval criteria.
