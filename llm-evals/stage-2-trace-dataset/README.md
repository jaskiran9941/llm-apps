# Stage 2 — Create a Trace Dataset

> **Course reference:** Chapter 3 §3.2 of *Application-Centric AI Evals for Engineers and Technical Product Managers* — Shankar & Husain (2026)

---

## Terminology Box

Before diving in, pin down four terms that this stage introduces. They will carry through every subsequent stage.

| Term | Definition |
|------|-----------|
| **Query** | The raw input text submitted by a user before the application processes it. A query is what the user typed. |
| **Trace** | The full ordered record of everything the application did in response — the query, the response, and any intermediate steps (retrieval, tool calls, chain-of-thought). A trace is the unit of analysis in evals. |
| **Dimension** | An axis of variation that describes a meaningful way the input space can differ. Choosing the right dimensions is the core skill of this stage. |
| **Tuple** | A specific combination of dimension values, e.g., `(buyer, eligibility, edge-case)`. Each tuple becomes one test query. |

---

## What Is a Trace, and Why Does It Matter?

The distinction between a query and a trace is the foundation of application-centric evals.

A **query** is just the input string:

```
"Can I cancel a bid after placing it?"
```

A **trace** is the complete record the application produces in response:

```json
{
  "id": "5",
  "user_type": "buyer",
  "query_type": "policy",
  "scenario": "clear",
  "query": "Can I cancel a bid after placing it?",
  "response": "All bids on eBay Live are final and cannot be retracted once placed.",
  "timestamp": "2026-04-19T11:34:14.390415",
  "open_code": "",
  "first_failure": "",
  "acceptable": null
}
```

This distinction matters because **you cannot evaluate an application from queries alone**. Consider:

- Two different chatbot implementations could answer the same query in radically different ways.
- In a RAG system, the retrieval step might succeed while the generation step hallucinates — you can only see this in the trace.
- A bug might only manifest when a specific query type reaches a specific part of the knowledge base — again, only visible in the trace.

> "The trace is not a log. It is the primary artifact of analysis. Everything else — failure labels, judges, metrics — is derived from traces."
>
> — Shankar & Husain (2026), Ch. 3

In later stages (open coding, axial coding, LLM judge), you will always work with traces, never raw queries. Stage 2 exists to build that corpus.

For this chatbot, a trace contains:
- `query` — the user's question
- `response` — the chatbot's complete answer
- `user_type`, `query_type`, `scenario` — the dimension values that generated the query
- `open_code`, `first_failure`, `acceptable` — fields left blank here, filled in Stage 3

---

## Why ~36–50 Traces, Not 1000?

A natural instinct is to gather as many test cases as possible. More data means better coverage, right?

Not for error analysis.

The goal of this stage is not statistical coverage — it is **failure mode discovery**. You are looking for categories of things that go wrong, not measuring the rate at which they go wrong. These are fundamentally different tasks.

The concept from Chapter 3 is **theoretical saturation**: the point at which new traces stop revealing new failure categories. In practice, for a focused application like a customer support chatbot with a bounded knowledge base, saturation arrives much earlier than you'd expect.

The empirical pattern from the course:

- **Traces 1–10:** Several distinct failure modes emerge clearly
- **Traces 11–25:** A few new failure types appear, but many traces repeat patterns you've already seen
- **Traces 26–50:** Mostly confirmation. Rare edge-case failures occasionally surface.
- **Traces 51+:** Almost entirely redundant for the purpose of identifying failure categories

At ~36–50 traces, you have:
1. Covered the major dimensions systematically
2. Seen each failure mode at least 2–3 times (enough to name it confidently)
3. Not yet spent so much time collecting that you've delayed getting to the analysis

The practical implication: **don't optimize for volume. Optimize for coverage of the input space.** That's what dimensions are for.

---

## The Problem with Naive Generation

The obvious approach: open a chat window and say "give me 50 questions a user might ask an eBay Live chatbot." Why doesn't this work?

> "Naively generated queries tend to be generic, repetitive, and fail to capture real usage patterns."
>
> — Shankar & Husain (2026), Ch. 3

What you actually get from naive generation:

```
1. What is eBay Live?
2. How do I use eBay Live?
3. Can I buy things on eBay Live?
4. How does eBay Live work?
5. What can I sell on eBay Live?
6. Is eBay Live free?
7. How do I sign up for eBay Live?
8. What categories does eBay Live support?
...
```

These queries share three problems:

**1. Generic framing.** They sound like FAQ bullets, not like real users typing in a chat. A real buyer who just watched a stream disappear mid-auction types "I placed a bid but the stream froze right after — did my bid go through?" not "How do auctions work on eBay Live?"

**2. Clustering around the easy cases.** Naive generation gravitates toward what the model knows well — the core happy path. It vastly underrepresents out-of-scope questions, edge cases, and seller-specific questions. These are precisely where chatbots fail.

**3. Missing the buyer/seller split.** A buyer and a seller have completely different mental models of eBay Live. A seller asking "how do I go live?" has different eligibility concerns, technical requirements, and knowledge gaps than a buyer asking "how do I watch?" Naive generation blurs this distinction.

The result: you run 50 generic queries, find 0–1 failures (or worse, find only the most obvious failure), declare the system "working," and deploy. The real failures — hallucinations on out-of-scope questions, seller eligibility edge cases, category boundary ambiguity — never surface until production.

---

## The Dimensions Concept: Mapping the Failure Space

Instead of asking "what questions might users ask?" ask a different question first:

**Along what axes does user input vary in ways that are likely to cause different failure modes?**

This reframe is the core insight of §3.2. You are not sampling questions. You are mapping a space.

For eBay Live, the analysis produces three dimensions:

### Dimension 1: User Type

Who is asking?

| Value | Description |
|-------|-------------|
| `buyer` | Watching and bidding. Cares about payment, bids, eligibility to participate, what categories are available. |
| `seller` | Hosting streams. Cares about approval process, technical setup, fees, allowed categories, stream management. |

**Why this dimension matters:** Buyers and sellers interact with completely different parts of the knowledge base. A question about "eligibility" means something entirely different to each: buyers need to know about US/Canada account registration and saved payment details; sellers need to know about the invite-only beta, the Seller Interest Form, and account standing requirements. A chatbot that handles buyer eligibility questions well might completely mishandle seller eligibility questions — and you will never see this unless you sample both user types systematically.

### Dimension 2: Query Type

What kind of information are they seeking?

| Value | Description |
|-------|-------------|
| `policy` | Rules, restrictions, what is and isn't allowed |
| `how-to` | Step-by-step process questions |
| `eligibility` | "Can I do X? Do I qualify?" |
| `categories` | What can be sold or bought |
| `troubleshooting` | Something went wrong, or they're confused about behavior |
| `out-of-scope` | A question the chatbot genuinely cannot answer from its knowledge base |

**Why this dimension matters:** Each query type exercises a different part of the system. Policy questions test whether the chatbot accurately represents rules without softening or inventing them. How-to questions test whether it can sequence steps correctly. Out-of-scope questions test the single most important failure mode: **does the chatbot know what it doesn't know?** Hallucinations live almost entirely in the out-of-scope and edge-case categories.

### Dimension 3: Scenario

How well-formed is the query?

| Value | Description |
|-------|-------------|
| `clear` | Specific, unambiguous. Easy to route to a definitive answer. |
| `ambiguous` | Underspecified, could be interpreted multiple ways. Tests whether the chatbot handles vagueness gracefully. |
| `edge-case` | Unusual situation at the boundary of what the knowledge base covers. Tests whether the chatbot recognizes and handles knowledge limits. |

**Why this dimension matters:** Real users rarely ask perfectly formed questions. Ambiguous queries expose whether the chatbot makes reasonable default assumptions or confidently answers the wrong question. Edge cases directly probe the seams of the knowledge base — the precise places where a model is most likely to hallucinate rather than say "I don't know."

### The Full Space

```
user_type  ×  query_type  ×  scenario
   2        ×      6       ×     3     =  36 tuples
```

Thirty-six combinations. Each one becomes a test query. This is not arbitrary coverage — it is deliberate sampling of the failure space.

---

## Why These Three Dimensions?

This is where most practitioners make the first mistake: treating the choice of dimensions as obvious or arbitrary.

**The wrong approach:** Choose dimensions that seem reasonable ("maybe we should test formal vs. casual phrasing") or that produce nice round numbers.

**The right approach:** Choose dimensions that map to distinct failure modes. Ask: if I varied this dimension while holding others constant, would I expect the chatbot to fail differently? If yes, it's a real dimension.

For eBay Live, the three dimensions survive this test:

- **user_type:** A buyer's eligibility question and a seller's eligibility question pull from entirely different parts of the KB. Different failure modes.
- **query_type:** Out-of-scope questions cause hallucinations; how-to questions cause step omissions; policy questions cause rule softening. Different failure modes.
- **scenario:** Clear questions tend to succeed; edge-case questions tend to surface knowledge boundaries; ambiguous questions expose assumption failures. Different failure modes.

If you had chosen dimensions like "short vs. long queries" or "questions with question marks vs. without," you would not be mapping failure modes — you would be sampling randomly with extra steps.

> "The dimensions you choose encode your hypothesis about where the system will fail. Choosing them thoughtlessly means you will miss the failures you don't already know about."
>
> — Shankar & Husain (2026), Ch. 3

---

## The Two-Step Process: Tuples First, Queries Second

Once you have dimensions, the naive instinct is to ask an LLM: "Give me one question for each of these 36 combinations."

The book recommends a different approach: **separate the structural step from the linguistic step**.

### Step 1 — Generate Structured Tuples

First, enumerate all combinations mechanically. This is pure Python — no LLM needed:

```python
from itertools import product

DIMENSIONS = {
    "user_type": ["buyer", "seller"],
    "query_type": ["policy", "how-to", "eligibility", "categories", "troubleshooting", "out-of-scope"],
    "scenario": ["clear", "ambiguous", "edge-case"],
}

all_tuples = list(product(*DIMENSIONS.values()))
# 36 tuples: (buyer, policy, clear), (buyer, policy, ambiguous), ...
```

### Step 2 — Convert Each Tuple to Natural Language

Then, for each tuple, ask an LLM to produce a single realistic question. Critically, the LLM's only job is **naturalization** — making the query sound like something a real person would type. The structure (what dimensions to cover) has already been decided.

```python
def generate_query(user_type: str, query_type: str, scenario: str) -> str:
    prompt = f"""You are generating test queries for an eBay Live customer support chatbot.

Given a tuple of dimensions, write a single realistic question a user might ask.
The question should reflect the scenario type:
- clear: specific, unambiguous
- ambiguous: underspecified, could mean multiple things
- edge-case: unusual situation at the boundary of what the bot knows

Here are examples:
Tuple: (buyer, policy, clear)
Query: Can I cancel a bid after I've placed it on eBay Live?

Tuple: (seller, eligibility, ambiguous)
Query: I've been selling on eBay for a while — how do I know if I can go live?

Now generate ONE question for:
Tuple: ({user_type}, {query_type}, {scenario})
Query:"""

    response = litellm.completion(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["choices"][0]["message"]["content"].strip()
```

**Why does this separation matter?**

When you ask "give me 50 diverse questions," the LLM must simultaneously decide what topics to cover and how to phrase them. These two concerns interfere with each other. The model defaulting to generic phrasing drags the topic selection toward the obvious cases, and topic selection anchoring on the familiar pulls phrasing toward textbook examples.

When you separate the steps, each step gets the model's full attention. The structural step guarantees coverage by construction (36 combinations, no gaps). The linguistic step can focus entirely on sounding realistic without worrying about coverage.

The result is measurably more diverse: you get seller questions about crowdfunding restrictions, buyer questions about cross-platform purchasing, edge cases about pre-recorded video streams — queries that would essentially never appear in naive generation.

---

## What We Actually Generated: 36 Queries

Running `generate_queries.py` produces one query per tuple. Here is a representative sample from each major category:

### Buyer queries

| Tuple | Generated query |
|-------|----------------|
| `(buyer, policy, clear)` | What is the refund policy for items purchased during an eBay Live stream? |
| `(buyer, policy, edge-case)` | If I win a bid during a seller's stream but the item is later reported as counterfeit, what's eBay Live's policy on refunds? |
| `(buyer, how-to, ambiguous)` | How do I participate in an eBay Live auction? |
| `(buyer, eligibility, edge-case)` | Am I allowed to participate in an eBay Live auction if I'm located outside the US but have an eBay account? |
| `(buyer, categories, edge-case)` | Are limited-edition digital art collectibles allowed to be purchased through eBay Live streams? |
| `(buyer, troubleshooting, edge-case)` | I placed a bid but the stream froze right after — did my bid go through or do I need to try again? |
| `(buyer, out-of-scope, clear)` | Does eBay Live support virtual reality shopping experiences? |
| `(buyer, out-of-scope, edge-case)` | Can I use eBay Live to make payments directly within the livestream chat? |

### Seller queries

| Tuple | Generated query |
|-------|----------------|
| `(seller, policy, edge-case)` | Are there any specific restrictions for hosting live streams that feature crowdfunding or pre-order products on eBay Live? |
| `(seller, how-to, edge-case)` | How do I set up a live stream if I only have a pre-recorded video, not a live camera feed? |
| `(seller, eligibility, edge-case)` | I recently opened a new eBay store — can I start hosting eBay Live streams immediately, or is there a waiting period? |
| `(seller, categories, clear)` | Can I livestream and sell handmade jewelry on eBay Live? |
| `(seller, categories, edge-case)` | Can I host a live sale for digital products like downloadable art on eBay Live? |
| `(seller, troubleshooting, edge-case)` | My stream keeps disconnecting whenever I switch from my phone's Wi-Fi to mobile data — how can I fix this? |
| `(seller, out-of-scope, clear)` | Can I use eBay Live to manage my entire eBay store inventory? |
| `(seller, out-of-scope, edge-case)` | Can I schedule a live stream to automatically start at midnight in a different time zone? |

The full 36-query CSV is at `queries/queries_20260419_113323.csv`.

---

## Where Hallucinations Live: The Disproportionate Value of Out-of-Scope and Edge Cases

After you collect all 36 traces, you will notice a pattern that holds across almost every chatbot eval:

**The in-scope, clear queries almost always succeed. The edge-case and out-of-scope queries are where failures concentrate.**

This is not surprising once you understand why. A well-built chatbot with a decent knowledge base will handle the main cases: "how does max bidding work?", "what are the seller fees?", "can I cancel a bid?" These are exactly the questions the KB was written to answer, and the model has seen countless similar questions in training.

The dangerous cases are different:

**Out-of-scope queries** ask about things genuinely not in the KB. The correct behavior is to say "I don't have that information — please check eBay's help pages." The failure mode is confident confabulation: the model produces a plausible-sounding answer using its general knowledge of e-commerce, which may be wrong for eBay Live specifically.

Consider query 36: *"Can I schedule a live stream to automatically start at midnight in a different time zone?"* The KB does not mention scheduled streams at all. The chatbot responded that eBay Live does not support this — which may be true, but is asserted with more confidence than the knowledge base warrants. In the V1 manual test (24 hand-crafted questions), query 24 — *"Can I schedule an eBay Live event in advance?"* — was flagged as a likely hallucination for exactly this reason.

**Edge-case queries** probe the boundary between what's documented and what isn't. Query 3 — *"If I win a bid during a seller's stream but the item is later reported as counterfeit, what's eBay Live's policy on refunds?"* — requires the chatbot to combine its knowledge of the eBay Money Back Guarantee with eBay Live auction mechanics. The KB might support each piece individually but not the combination. Confident synthesis of two partial knowledge sources is a reliable hallucination trigger.

The practical consequence for your eval design: **weight your sampling toward the edges.** Six query types × three scenarios gives you 18 cells per user type. The `out-of-scope + edge-case`, `out-of-scope + ambiguous`, and `categories + edge-case` cells will produce the most failures per trace collected. If you are budget-constrained and need to cut traces, cut from `how-to + clear` before you cut from `out-of-scope + edge-case`.

---

## Collecting Traces: Connecting Queries to the Running Chatbot

With queries in hand, `collect_traces.py` sends each one to the Stage 1 chatbot and saves the complete response:

```python
def ask(query: str) -> str:
    payload = json.dumps({"messages": [{"role": "user", "content": query}]}).encode()
    req = urllib.request.Request(
        "http://localhost:8001/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["messages"][-1]["content"]
```

Each trace is saved with the full metadata from the generating tuple, plus three blank fields — `open_code`, `first_failure`, `acceptable` — that Stage 3 will fill in:

```json
{
  "id": "27",
  "user_type": "seller",
  "query_type": "eligibility",
  "scenario": "edge-case",
  "query": "I recently opened a new eBay store — can I start hosting eBay Live streams immediately, or is there a waiting period?",
  "response": "To host eBay Live streams, sellers must be invited and are currently required to fill out the eBay Live Seller Interest Form...",
  "timestamp": "2026-04-19T11:34:49.080600",
  "open_code": "",
  "first_failure": "",
  "acceptable": null
}
```

The metadata is critical. When you read 36 traces during open coding, knowing that a trace came from `(seller, eligibility, edge-case)` immediately contextualizes the failure you're seeing. Was this an eligibility question that a new seller asked in an unusual way? That's a different failure mode than an eligibility question from an experienced seller who expected a clear "yes/no" and got hedging.

---

## How to Run (V2 — Dimension-Based)

Make sure the Stage 1 chatbot is running on port 8001, then:

```bash
# Step 1: Generate queries from dimension tuples
python3 generate_queries.py
# → queries/queries_YYYYMMDD_HHMMSS.csv  (36 rows)

# Step 2: Run each query against the chatbot and save full traces
python3 collect_traces.py
# → traces/traces_YYYYMMDD_HHMMSS.json  (36 trace objects)

# Or pass a specific query file
python3 collect_traces.py queries/queries_20260419_113323.csv
```

Both scripts require `OPENAI_API_KEY` (or equivalent) to be set. They load from the Stage 1 `.env` file automatically.

---

## V1 Findings (Manual 24-Question Run)

Before the dimension-based approach, this stage ran a hand-crafted set of 24 questions (`test_questions.csv`), covering buyer basics, bidding mechanics, payment, seller eligibility, categories, technical requirements, and fees, plus three explicit hallucination probes.

Results from the V1 run:

- **22/24 accurate** — grounded in the knowledge base, no fabrication
- **2 confirmed hallucinations:**
  - Q22: invented a mobile app access method not mentioned in the KB
  - Q24: invented a scheduling policy for eBay Live events
- **1 borderline:**
  - Q3: inferred a watching-vs-participating distinction that is not explicitly in the KB

The hallucinations clustered in exactly the category the dimension framework calls `out-of-scope` — questions about features the KB does not document. This validates the dimension choice: `out-of-scope` is where the chatbot fails.

The V2 dimension-based dataset reproduces this finding more systematically: 12 out of 36 queries (all `out-of-scope` and most `edge-case` queries) directly probe the knowledge boundary where hallucination pressure is highest.

---

## Common Pitfall: Arbitrary Dimension Choice

The most common mistake when applying this framework to a new system is choosing dimensions that feel reasonable without asking whether they map to failure modes.

**Example of bad dimension choices for eBay Live:**

```
Dimension 1: Query length (short, medium, long)
Dimension 2: Politeness (formal, casual, blunt)
Dimension 3: Question format (direct question, scenario, hypothetical)
```

These dimensions describe surface form, not failure modes. A long casual hypothetical about bidding mechanics and a short formal direct question about bidding mechanics will exercise exactly the same part of the chatbot. You have 36 combinations but effectively 1 failure mode — or none, because none of these dimensions predict where the chatbot will fail.

**The test for a good dimension:**

> If I hold all other dimensions constant and vary only this one, will I observe meaningfully different chatbot behavior?

For `user_type`: yes, because buyer and seller questions pull from different KB sections.
For `query_type`: yes, because `out-of-scope` questions trigger hallucinations that `how-to` questions don't.
For `scenario`: yes, because `edge-case` queries probe knowledge limits that `clear` queries don't reach.
For `query_length`: no, because the chatbot does not fail differently on long vs. short inputs.

Run this test on every dimension you are considering. Reject dimensions that don't pass it.

---

## Repository Layout

```
stage-2-trace-dataset/
├── README.md              ← This file
├── dimensions.md          ← Full definition of dimensions and example tuples
├── generate_queries.py    ← Step 1: LLM turns (tuple → natural language query)
├── collect_traces.py      ← Step 2: sends each query to chatbot, saves full trace JSON
├── queries/
│   └── queries_20260419_113323.csv   ← 36 generated queries with dimension labels
├── traces/
│   └── traces_20260419_113459.json   ← 36 collected traces (query + response + metadata)
├── test_questions.csv     ← V1: 24 hand-crafted questions from initial exploration
├── run_tests.py           ← V1: test runner from initial manual testing
└── results/               ← V1: results from initial 24-question run
```

---

## What Happens Next: Stage 3 — Open Coding

You now have 36 traces. Each is a `(query, response)` pair tagged with its originating dimensions.

Stage 3 is **open coding**: reading every trace, and for each one writing a short freeform note about what went wrong (if anything). The rule is: do not categorize yet. Just observe.

Examples of open codes you might write:

- *"Chatbot answered with confidence but KB doesn't actually say this"*
- *"Correct answer but answered the wrong interpretation of an ambiguous question"*
- *"Good response, correctly acknowledged knowledge limit"*
- *"Invented a feature detail not in the KB"*

After open coding all 36 traces, Stage 4 (axial coding) clusters those freeform notes into a formal taxonomy of failure modes — the binary labels that become the training signal for a Stage 5 LLM judge.

The dimension metadata collected here is what makes that clustering principled rather than arbitrary. When you see that 8 of your 10 open codes mentioning hallucination came from `out-of-scope` or `edge-case` tuples, you have not just a label but an explanation — and a fix hypothesis.

---

## Summary

| Concept | What it means in practice |
|---------|--------------------------|
| Trace vs. query | Run `collect_traces.py`, not just a list of questions |
| Theoretical saturation | ~36–50 traces is enough for failure discovery; 1000 is overkill |
| Dimensions | Map the failure space before generating queries |
| Naive generation failure | Generic, clustered around easy cases, misses out-of-scope |
| Two-step process | `product()` for structure, LLM for naturalization |
| eBay Live specifics | `user_type` splits KB sections; `query_type` controls hallucination exposure; `scenario` stress-tests knowledge limits |
| Where failures live | Out-of-scope + edge-case cells are disproportionately valuable |
| Dimension pitfall | Surface-form dimensions (length, tone) don't predict failure modes |
