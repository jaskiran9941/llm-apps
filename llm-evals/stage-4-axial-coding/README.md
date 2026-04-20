# Stage 4 — Axial Coding: Build Failure Taxonomy

**Book reference**: "Application-Centric AI Evals for Engineers and Technical Product Managers" — Shankar & Husain (2026), Chapter 3, §3.4–3.6

**Where you are in the pipeline**:

```
Stage 2: Collect Traces
       ↓
Stage 3: Open Coding   ← freeform observation notes per trace
       ↓
Stage 4: Axial Coding  ← YOU ARE HERE — cluster notes into named failure modes
       ↓
Stage 5: LLM Judge     ← write Pass/Fail prompts for each failure mode
       ↓
Stage 6: Retrieval Eval
```

---

## What Is Axial Coding?

Open coding (Stage 3) leaves you with a pile of raw, freeform observations — one per trace. Each note is individual: it describes what was wrong in a specific exchange, in your own words in the moment. After coding 36 traces, you might have notes like:

- "bot said pre-recorded video is not supported but this is never mentioned in the KB"
- "invented URL: ebay.com/live doesn't exist as a form submission page"
- "confidently told user scheduling is available — scheduling isn't in the KB at all"
- "recommended clearing cache and restarting — these steps are not in the KB"
- "avoided saying 'I don't know' and instead made up a plausible-sounding workflow"

That pile is rich but unusable for systematic evaluation. You cannot build an automated judge for "invented URL" as a one-off — there are too many specific forms a hallucination can take. You need to abstract up one level.

**Axial coding** is the process of taking that raw, chaotic pile and imposing structure — identifying the recurring *patterns* that underlie many individual observations, and naming them as coherent failure modes.

The term comes from grounded theory research methodology (Strauss & Corbin, 1990), where "axial" means rotating around an axis — you take the linear list of open codes and spin them into a multi-dimensional structure. In practice, for AI evals, it means clustering.

> "The goal is to define a small, coherent, non-overlapping set of binary failure types, each easy to recognize and apply consistently during trace annotation." — Shankar & Husain (2026)

---

## The Transition From Observation to Category

Here is the core intellectual move of axial coding, demonstrated with real eBay Live traces.

### Step 1: Gather all your open codes

After open coding 36 traces, you have notes including these four:

| Trace | Open Code |
|-------|-----------|
| 24 | "Bot stated pre-recorded video is not supported — this is never mentioned in the KB. Bot invented a negative policy." |
| 36 | "Bot said eBay Live does not support scheduling. Scheduling isn't mentioned in the KB at all — bot made up a negative claim." |
| 30 | "Bot stated digital products are not supported for live sale. No policy about this in the KB." |
| 11 | "Bot said 'eBay Live does not currently support multi-camera setups' — nothing in the KB about this." |

### Step 2: Find the shared pattern

What do these four traces have in common? It is not that the bot "hallucinated" in general — that is too broad. The specific pattern is:

- The user asked about something the KB does not cover
- Instead of saying "I don't know", the bot stated a definitive *negative policy*: "X is not supported", "X is not available"
- The bot did not invent something that exists — it invented a restriction that doesn't exist

This is a specific, dangerous failure mode with its own mechanism and its own risk profile. You can name it: **Confident Out-of-Scope Claim**.

### Step 3: Compare with a different cluster

Now look at these traces:

| Trace | Open Code |
|-------|-----------|
| 7 | "Bot told user to 'try restarting the app or browser and clearing cache' — no such troubleshooting steps in the KB." |
| 14 | "Bot advised user to avoid VPNs and cell signal boosters — invented technical advice with no KB basis." |
| 22 | "Bot gave specific encoder settings as if they were standard guidance — not in the KB." |

These are also hallucinations, but the mechanism is different. The bot is not asserting a negative policy — it is inventing *troubleshooting steps*, specific technical advice. The risk is different too: a user might follow the bad advice and waste time, or conclude their real problem is unsolvable.

This is a different failure mode: **Invented Troubleshooting Steps**.

### Step 4: Write the cluster definition

For each cluster you identify, write a single crisp sentence that captures the essential difference from all other clusters:

- FM1: Bot states that eBay Live does *not* support X, for a topic not in the KB, instead of saying "I don't know."
- FM2: Bot provides specific technical troubleshooting advice (steps, settings, workarounds) that is not present in the KB.
- FM3: Bot describes specific workflows, URLs, or feature details that are not present in the KB.
- FM4: Bot gives a confident, substantive answer to a question that is genuinely outside its knowledge, instead of escalating.
- FM5: Bot makes a reasonable-sounding inference from KB content, stated as established fact, that could mislead users.

---

## Properties of Good Failure Modes

Shankar & Husain (2026) identify four properties every failure mode in your taxonomy should have.

### 1. Small (4-6 categories)

More categories is not better. If you have 15 failure modes, you will:
- Have difficulty training raters to apply them consistently
- End up with many modes that fire rarely and are statistically invisible
- Make your Stage 5 LLM judge unwieldy

**Target: 4–6 failure modes**. Resist the urge to create specialized sub-categories. If "FM3: Invented Process Details" covers both invented URLs and invented workflow steps, that is fine — the category is more powerful for being general.

### 2. Coherent

Each category must have a definition you can state in one sentence, and that definition must clearly distinguish it from every other category. Test this: if two annotators each read the definition and 20 traces, do they agree 90%+ of the time about whether the mode is present? If not, the definition is not coherent.

Bad definition: "Bot says something wrong"
Good definition: "Bot asserts a definitive negative policy ('X is not supported', 'X is not available') for a topic not covered in the KB"

The good definition gives the annotator a concrete test: Is the claim negative? Is the topic absent from the KB? If both yes, it's an FM1.

### 3. Non-Overlapping

A single trace should not be ambiguously classifiable in two categories. This is different from a trace being classifiable in *both* — a trace can exhibit FM1 and FM2 simultaneously (bot both invents a negative policy and gives troubleshooting steps). Non-overlapping means: if you see FM1, it does not automatically mean FM2. The presence of one does not imply the other.

A warning sign that categories overlap: if you find yourself repeatedly unable to decide between category A and category B for the same trace, the definitions are likely not distinct enough. Either merge them or sharpen the definitions.

### 4. Binary

Each failure mode is either present (1) or absent (0) in a trace. Not:
- "How bad is the hallucination on a scale of 1-5?"
- "How many invented details does the response contain?"

Binary scoring enables clean automation in Stage 5 (you ask the LLM judge: Pass or Fail?) and clean reporting (you can say "FM3 appeared in 28% of traces"). Likert scales introduce subjectivity and complicate everything downstream.

---

## Using LLM Assistance vs. Human Judgment

The `axial_coding.py` script uses an LLM to propose initial clusters. This is a legitimate and useful technique. Here is the exact prompt structure from the book:

```
Below are open-coded annotations describing failures in an eBay Live customer
support chatbot.

Please group them into 4-6 coherent failure categories. Each category should:
- Have a short descriptive title (2-4 words)
- Have a one-line definition
- Be binary (either present or absent in a trace)
- Be non-overlapping with other categories

Do not invent new failure types. Only cluster what is present in the notes.

Annotations:
[list of open codes]

Output format:
**[Category Name]**: [one-line definition]
Examples from the notes: [2-3 representative quotes]
```

**Important constraints on LLM-assisted clustering**:

The LLM is good at spotting surface-level similarity in language. It will correctly notice that "invented URL" and "made up feature" sound similar. But you must review and adjust its proposals because:

1. **The LLM does not know your risk model.** FM1 (confident negative policy claim) and FM4 (failure to escalate) might look similar to an LLM, but they have different downstream consequences and different fix strategies. You split them based on domain knowledge.

2. **The LLM might over-cluster.** It may lump FM2 (invented troubleshooting) and FM3 (invented process details) together as "hallucination". You need to keep them separate because they have different triggers and different mitigations.

3. **The LLM might under-cluster.** It may propose 10 categories where 5 would do. You need to apply the "merge if the distinction doesn't matter for your fix strategy" heuristic.

**Rule of thumb**: treat the LLM output as a first draft. Budget 30–60 minutes of human review and iteration before finalizing.

---

## When to Split vs. Merge

This is the hardest judgment call in axial coding. Here are concrete examples from the eBay Live project.

### When to Split

**Example: "hallucination" is too broad**

Your LLM might propose a single category called "hallucination" covering all invented content. Split it when:
- The two types of hallucination have different *mechanisms* (negative policy assertion vs. invented workflow details)
- They have different *consequences* (user believes a false restriction vs. user follows a non-existent workflow)
- They require different *fixes* (different system prompt constraints or retrieval strategies)

In our case: FM1 (confident out-of-scope claim) is about making negative assertions. FM3 (invented process details) is about describing workflows and URLs. Same broad type (hallucination), different enough to warrant splitting.

**Decision rule**: Split if you would write meaningfully different LLM judge prompts for the two sub-types.

### When to Merge

**Example: "invented URL" and "invented feature description" are too specific**

You might have open codes like:
- "bot made up a URL: ebay.com/live/interest-form"
- "bot described a scheduling feature that doesn't exist"
- "bot invented a multi-seller collaboration option"

These are all instances of the same underlying failure: **FM3: Invented Process Details**. The specific form (URL vs. feature vs. workflow step) does not matter for your evaluation strategy. Merge them.

**Decision rule**: Merge if you would write the same LLM judge prompt for both types. If the judge prompt is identical except for examples, that is a strong signal to merge.

---

## Iteration: It's Normal to Do 2–3 Rounds

Your first pass at clustering will be imperfect. Expect to revise.

### Round 1 Example: FM2 and FM4 look the same

In round 1, you might propose:
- "Invented Advice": bot gives advice not in the KB
- "Failure to Escalate": bot doesn't say "I don't know"

These look like the same thing — giving invented advice *is* failing to escalate. Why are they separate?

### Round 2: The critical distinction

After reviewing more traces, you notice:

**FM2 traces** (Invented Troubleshooting Steps): The bot gives *specific technical steps* — "clear your cache", "avoid VPNs", "restart the app". The failure is that it invents *technical depth* it doesn't have.

**FM4 traces** (Failure to Escalate): The bot gives a high-level framing answer to a completely out-of-scope question — "eBay Live is best used as a complementary sales channel" for an inventory management question. The failure is that it *doesn't recognize* the question is outside its domain.

The distinction matters because:
- FM2 fix: add explicit KB note that troubleshooting steps are not available; instruct bot to say "I don't have troubleshooting guidance"
- FM4 fix: improve the bot's out-of-scope detection; add explicit escalation instructions

And note: FM2 is specifically *troubleshooting* — the bot is inventing steps to fix a problem. FM4 is broader topic drift. A trace can have FM4 without FM2 (bot confidently addresses inventory management) and FM2 without FM4 (the topic is broadly eBay Live, but bot invents specific technical steps).

### Round 3: Validate non-overlap with 5 hard cases

Pick 5 traces that felt ambiguous during round 2 coding. Apply both the round 2 category definitions. If you can classify each one unambiguously, you're done. If not, refine the definitions one more time.

---

## Worked Examples: Open Codes Mapped to Failure Modes

These show how specific open codes from Stage 3 map to the final failure modes.

### FM1: Confident Out-of-Scope Claim

**Open code (Trace 24)**: "Bot said 'Using a pre-recorded video is not currently supported for eBay Live.' The KB never mentions video formats at all. Bot invented a restriction."

**Why FM1**: The bot is asserting a *negative policy* for a topic not in the KB. It did not say "I don't have information about that." It said "X is not supported" — which implies knowledge it does not have.

**Open code (Trace 36)**: "Bot stated eBay Live does not support scheduling livestreams. No scheduling information anywhere in the KB. Complete invention."

**Why FM1**: Same mechanism — negative policy claim for a KB-absent topic.

**Open code (Trace 30)**: "Bot said digital products are not supported for live sale. The KB covers categories but doesn't address this specific restriction."

**Why FM1**: Pattern holds. Bot extrapolated from what the KB *does* cover (some categories) to invent a restriction about what it *doesn't* cover.

---

### FM2: Invented Troubleshooting Steps

**Open code (Trace 7)**: "Bot told user to restart the app and clear cache. These specific troubleshooting steps are not in the KB. Bot invented technical remediation."

**Why FM2**: Specific technical steps (restart, clear cache) that are not KB-grounded.

**Open code (Trace 14)**: "Bot advised user to avoid using VPNs and cell signal boosters during live sessions. The KB says nothing about this. Bot invented connectivity troubleshooting guidance."

**Why FM2**: Same — invented specific technical advice.

**Why not FM4**: The question was about eBay Live (in scope), but the bot invented technical depth it doesn't have. FM4 would be if the question was about something completely outside eBay Live.

---

### FM3: Invented Process Details

**Open code (Trace 3)**: "Bot said 'submit the interest form at ebay.com/live.' No such URL exists in the KB or anywhere."

**Why FM3**: Invented specific workflow detail (URL).

**Open code (Trace 17)**: "Bot described how to schedule a livestream in detail. Scheduling is not mentioned in the KB at all."

**Why FM3**: Invented feature description with workflow steps.

**Why not FM1**: FM1 is specifically *negative* assertions ("not supported"). FM3 is *positive* assertions about workflows that don't exist. A bot can commit FM3 while sounding helpful.

---

### FM4: Failure to Escalate on Truly Unknown Topics

**Open code (Trace 8)**: "User asked about inventory management integration with eBay Live. Bot gave a paragraph about how eBay Live is a 'complementary sales channel' — completely off-topic and confident."

**Why FM4**: The topic (inventory management integrations) is genuinely outside the eBay Live support KB. The bot should have said "I don't have information about that, please check ebay.com/help." Instead it confidently addressed an adjacent topic.

**Contrast with FM1**: FM1 is the bot asserting a specific negative policy. FM4 is the bot drifting into an adjacent topic with confident framing. Traces 19 and 21 are *correct*: the bot appropriately deferred when asked genuinely out-of-scope questions. FM4 is specifically when that deferral fails.

---

### FM5: Potentially Misleading Inference

**Open code (Trace 29)**: "User asked about duplicate bids. Bot said 'avoid placing duplicate bids for the same amount.' The KB doesn't cover bidding mechanics in this detail — bot stated an inference as fact."

**Why FM5**: The advice might be reasonable, but it is not KB-grounded. It is stated as authoritative guidance. If wrong, user is misled.

**Why not FM1, FM2, or FM3**: This is not a negative policy claim (FM1), not troubleshooting steps (FM2), not a workflow/URL (FM3). It is a plausible inference from adjacent KB content stated as fact.

**Why not FM4**: The topic is within the eBay Live domain. The bot is not drifting to inventory management. It is applying inference within domain but overstating confidence.

---

## The Output of Axial Coding

Axial coding produces your **failure taxonomy**: a structured document with 4–6 named failure modes, each with:

1. **A crisp one-sentence definition** (the test for membership)
2. **A Pass criterion** (what a correct response looks like)
3. **A Fail criterion** (what the failure looks like)
4. **Canonical example traces** (ground truth for annotator training)

This taxonomy feeds directly into Stage 5: for each failure mode, you write an LLM-as-Judge prompt using the Pass/Fail criteria as the evaluation rubric.

### Example: FM1 in Stage 5 format

```
You are evaluating an eBay Live support chatbot response.

FAILURE MODE: Confident Out-of-Scope Claim
DEFINITION: The bot asserts that eBay Live does NOT support or have something,
for a topic not covered in the knowledge base, instead of saying "I don't know."

Knowledge Base Summary:
[KB content here]

Conversation:
User: [user message]
Bot: [bot response]

PASS if: The bot says it doesn't have information about that and directs the user
to ebay.com/help or the eBay Live FAQ.

FAIL if: The bot states "eBay Live does not support X" or "X is not available"
for a topic that is not addressed in the knowledge base.

Output exactly one word: PASS or FAIL
```

Notice how the crisp taxonomy definitions translate directly and cleanly into judge prompts. Vague taxonomy → vague judge prompts → unreliable evaluation. Clear taxonomy → clear judge prompts → reliable evaluation.

---

## Common Pitfalls (From the Book)

Shankar & Husain (2026) identify four failure modes in the axial coding process itself:

### Pitfall 1: Skipping Open Coding and Jumping Straight to Taxonomy

It is tempting to look at a few traces and immediately propose failure categories based on intuition. Resist this. Open coding forces you to encounter many specific failure forms before you generalize. If you jump to taxonomy first, you will:
- Miss failure modes that only appear in edge cases
- Overfit your categories to the first few traces you happen to look at
- Create categories that feel right but don't cover the actual distribution

**Rule**: Do at least 20 traces of open coding before starting axial coding.

### Pitfall 2: Defining Too Many Categories

More than 6 categories creates practical problems:
- Annotator disagreement increases (more categories = more ambiguity)
- LLM judge accuracy degrades (longer, more complex rubrics)
- Statistical signal per category weakens (fewer examples per category)
- Category maintenance burden grows when the application changes

If you have 8+ proposed categories, ask: which two could be merged without losing actionable signal?

### Pitfall 3: Using Overlapping Categories

The test: can you think of a trace where you genuinely cannot decide between category A and category B? If yes, one of two things is wrong:
- The definitions are not distinct enough (fix: sharpen the language)
- The two categories are genuinely the same thing (fix: merge)

Overlapping categories produce inflated counts, confused annotators, and unreliable LLM judges.

### Pitfall 4: Freezing the Taxonomy Too Early

After your first pass at axial coding, you will have a working taxonomy. Resist finalizing it immediately. Run a second pass: code 10 more traces *using the new taxonomy*. Ask:
- Does every trace fit cleanly into the taxonomy?
- Are you repeatedly inventing a new category?
- Are any categories never firing?

If you repeatedly want a new category, add it (if it pushes past 6, merge something else). If a category never fires in 20+ traces, consider whether it is real or theoretical.

---

## What's In This Directory

| File | Purpose |
|------|---------|
| `axial_coding.py` | Loads open codes from Stage 3, uses LLM to propose clusters, interactive finalization |
| `failure_taxonomy.md` | The finalized eBay Live failure taxonomy (derived from 36 traces) |
| `taxonomies/` | Saved taxonomy JSONs (machine-readable, used by Stage 5) |

## How to Run

```bash
cd stage-4-axial-coding
python3 axial_coding.py [path/to/open_codes.json]
```

If no file is specified, the script finds the most recent open codes file from Stage 3 automatically.

The script:
1. Loads your open codes from Stage 3
2. Filters to traces marked as failures (`acceptable: false`)
3. Sends them to an LLM with the clustering prompt
4. Prints proposed clusters
5. Prompts you to enter your final failure modes interactively
6. Saves the taxonomy to `taxonomies/taxonomy_YYYYMMDD.json`

## Next: Stage 5 — LLM Judge

Use the failure taxonomy from this stage to build automated evaluators. For each failure mode:

1. Write a Pass/Fail LLM-as-Judge prompt using the Pass/Fail criteria
2. Validate the judge on your 36 traces: measure True Positive Rate and True Negative Rate
3. Correct for judge bias (LLM judges often have systematic pass or fail bias)
4. Wire the validated judge into your CI/CD pipeline

The quality of your Stage 5 judges is bounded by the quality of your Stage 4 taxonomy. Crisp, non-overlapping, binary failure modes → reliable automated evaluation.
