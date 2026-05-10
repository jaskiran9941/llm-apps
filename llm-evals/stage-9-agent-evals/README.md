# Stage 7 — Agent Evals

**Book**: *Application-Centric AI Evals for Engineers and Technical Product Managers* — Shankar & Husain (2026)
**Chapter**: 8, Sections 8.1–8.3

---

## Overview

In Stage 2, the eBay Live chatbot was a single-turn system: one query goes in, one LLM call happens, one response comes out. That is easy to evaluate — there is exactly one thing to measure and one place where failures can occur.

In Stage 7, we give that chatbot **tools** it can call: a category eligibility checker, a seller eligibility checker, a bidding rules lookup, and an escalation tool. The moment the LLM can call external functions, the system becomes an **agent** — a multi-step pipeline where decisions compound and errors cascade. Evaluation must change to match.

This stage covers three interconnected ideas from Chapter 8:

1. What structurally changes when a chatbot gains tools (§8.1)
2. How to position your agent on the agency spectrum before writing a single eval (§8.2)
3. How to use a state-transition failure matrix to pinpoint where failures originate, not just that they occurred (§8.3)

---

## Part 1 — What Changes When a Chatbot Becomes an Agent

### The Single-Turn Mental Model

Before tools, the eBay Live chatbot worked like this:

```
User Query
    │
    ▼
LLM (with static knowledge base in system prompt)
    │
    ▼
Response
```

There is one step and one failure point. The LLM either used the knowledge base correctly or it did not. Every single eval in Stage 2 measured exactly this: did the final response answer the question well?

When something went wrong, the diagnosis was simple: the system prompt was inadequate, the model hallucinated, or the question was genuinely outside the knowledge base.

### The Agent Mental Model

With tools, the same user query now flows through a sequence of decisions:

```
User Query
    │
    ▼
[ParseIntent] — LLM reads the query and decides what the user wants
    │            (Is this a buyer or seller question? What topic?)
    ▼
[SelectTool] — LLM decides which tool (if any) to call
    │            (Is this a category question → check_category_eligibility?
    │             A seller eligibility question → check_seller_eligibility?)
    ▼
[CallTool] — The chosen tool executes with LLM-generated arguments
    │          (Did the LLM pass "luxury watches" or "luxury watch" or "watches"?)
    ▼
[InterpretResult] — LLM reads the tool's structured output
    │                 (Did it understand what {eligible: false, failed_requirements: [...]} means?)
    ▼
[GenerateResponse] — LLM produces the final answer to the user
```

Now there are **five steps** and five independent places where something can go wrong. Worse, they are not independent in their consequences — a mistake at step 1 corrupts every step that follows.

### Why This Matters for Evaluation

The single-turn eval metric — "is the final response good?" — is still necessary, but it is no longer sufficient. Consider this scenario:

- User: "I sell sports cards, am I eligible for eBay Live?"
- ParseIntent: CORRECT — identified as a seller eligibility question
- SelectTool: INCORRECT — called `check_category_eligibility("sports cards")` instead of `check_seller_eligibility`
- CallTool: The category tool runs and returns `{supported: true}`
- InterpretResult: LLM reads "supported: true" and concludes "yes, you're eligible"
- GenerateResponse: "Yes, sports cards are a supported category on eBay Live!"

The final response is confidently wrong. If you only evaluated the final output, you would record a failure. But which step do you fix? The problem was in **SelectTool** — the LLM picked the wrong tool — but the final-output eval gives you no information about that. You might spend days improving the response generation logic when the real fix is clarifying the tool descriptions.

This is the core motivation for agent-specific evaluation: **measure each step, not just the final outcome**.

---

## Part 2 — The Agency Spectrum (Ch8 §8.2)

### Why the Spectrum Must Be Defined First

Before writing any evals, you must decide where your agent sits on the agency spectrum. This is not a philosophical exercise — it determines whether a given behavior is a bug or a feature.

The spectrum runs from low agency to high agency:

**Low Agency** (cautious, deferential)
- "If I am uncertain about what the user is asking, I will ask a clarifying question before calling any tools."
- "If the tool returns an unexpected result, I will acknowledge uncertainty and escalate."
- "I will not attempt to answer if I do not have high confidence the tool covers this question."

**High Agency** (autonomous, persistent)
- "I will make reasonable assumptions about the user's intent and proceed immediately."
- "I will keep calling tools until I have enough information to give a definitive answer."
- "I will try multiple approaches before giving up or escalating."

### Why This Must Be Explicit

Without a defined position on the spectrum, your team will disagree about whether bugs are bugs.

Consider a trace where the user asks: "Can I go live on eBay?" — and the agent responds: "Could you tell me a bit more? Are you asking about technical requirements, account eligibility, or something else?"

Is that response good or bad?

- If you designed a **low-agency** agent: it is good. The intent was genuinely ambiguous. The agent correctly asked for clarification before making assumptions.
- If you designed a **high-agency** agent: it is bad. The agent should have used heuristics, called multiple tools, and synthesized an answer covering all relevant angles.

The same output, evaluated differently depending on the intended agency level. If you never wrote down the intended agency level, your evals will be inconsistent and your team will argue indefinitely.

### eBay Live Support Bot: Moderate-Low Agency

For this chatbot, we define the following position:

> **Moderate-Low Agency**: The agent will attempt to answer from tools when it can confidently identify the user's intent. It will ask one clarifying question if the intent is genuinely ambiguous. It will escalate to a human agent (via `escalate_to_human`) when the question falls outside its tools' coverage. It will not keep retrying alternative tools if the first attempt fails — instead, it will acknowledge the limitation and escalate.

This means:
- Asking for clarification = **intended behavior** (not a failure)
- Using escalation tool for out-of-scope questions = **intended behavior** (not a failure)
- Not retrying with a different tool after a failed first attempt = **intended behavior** (the agent is not designed to be persistent)
- Calling no tool and answering from static knowledge = **acceptable** for questions clearly answerable from the system prompt

Write this down. Put it in the system prompt. Refer to it in every eval rubric.

---

## Part 3 — The Four Failure Modes in Tool Calling (Ch8 §8.1)

Every agent trace can be broken down into four types of events, each with its own failure mode.

### Failure Mode 1: Tool Selection

**What it is**: The LLM chooses the wrong tool, chooses no tool when it should, or calls a tool when it should answer directly.

**In practice for eBay Live**:

Correct behavior:
```
User: "Is seller_123 eligible to host a stream?"
→ LLM calls check_seller_eligibility(seller_id="seller_123")   ✓
```

Tool selection failure:
```
User: "Is seller_123 eligible to host a stream?"
→ LLM calls check_category_eligibility(category="eBay Live")   ✗
  (Wrong tool entirely — eligibility != category support)
```

Another tool selection failure:
```
User: "Am I eligible as a new seller?"
→ LLM does not call any tool, answers from static knowledge base
  "You need an active eBay account in good standing..."        ✗
  (Should have called check_seller_eligibility — the knowledge
   base gives general info but not account-specific eligibility)
```

**How to evaluate it**: After collecting a trace, check whether the tool name in the first `tool_call` event matches the expected tool for the query type. Build a lookup table: `{query_type → expected_tool}`.

### Failure Mode 2: Argument Generation

**What it is**: The LLM calls the correct tool but with wrong, malformed, or missing arguments.

**In practice for eBay Live**:

Correct behavior:
```
User: "Are luxury watches allowed on eBay Live?"
→ check_category_eligibility(category="luxury watches")         ✓
  Tool returns: {supported: true, category_group: "luxury_fashion"}
```

Argument generation failure:
```
User: "Are luxury watches allowed on eBay Live?"
→ check_category_eligibility(category="watches")               ✗
  Tool returns: {supported: false, ...}
  (The category "watches" doesn't match any known subcategory.
   The correct argument was "luxury watches".)
```

Another argument failure:
```
User: "Check if account ABC-123 can stream"
→ check_seller_eligibility(seller_id="account ABC-123")        ✗
  (Should extract just "ABC-123" — the prefix "account " is noise)
```

**How to evaluate it**: Log the exact arguments passed to each tool. Compare against a known-valid set of arguments. For category checks, verify the argument appears in `SUPPORTED_CATEGORIES` or is a reasonable alias.

### Failure Mode 3: Execution Success

**What it is**: The tool call was correctly formed but the execution failed, returned an empty result, or returned an unexpected structure that the LLM cannot interpret.

**In practice for eBay Live**:

Correct behavior:
```
check_seller_eligibility("seller_123")
→ {"eligible": true, "requirements_met": {...}}                 ✓
```

Execution failure:
```
check_seller_eligibility("unknown_seller_xyz")
→ {"eligible": false, "reasons": ["Seller not found"], ...}

LLM reads "Seller not found" and says:
"I wasn't able to verify your account. Please contact eBay support."  ✓
(Handled the empty/negative result gracefully)
```

vs.

```
LLM reads "Seller not found" and says:
"You are not eligible to host eBay Live streams."                ✗
(Conflated "not found" with "ineligible" — these are different!)
```

**How to evaluate it**: Check whether the tool's response contained an error flag (`eligible: false` with `reasons: ["Seller not found"]`), and whether the LLM correctly distinguished "error/unknown" from "definitively ineligible".

### Failure Mode 4: Output Handling

**What it is**: The tool call succeeded and returned a correct result, but the LLM ignored, misread, or contradicted that result in the final response.

**In practice for eBay Live**: This is perhaps the most insidious failure mode because the tool worked perfectly — the failure is entirely in the LLM's reading comprehension.

Correct behavior:
```
check_seller_eligibility("seller_456")
→ {
    "eligible": false,
    "failed_requirements": ["sufficient_transaction_history", "prior_livestream_experience"],
    "recommendation": "Fill out eBay Live Seller Interest Form"
  }

LLM response: "Your account has good standing, but you don't yet meet the
transaction history or livestreaming experience requirements. You can still
fill out the eBay Live Seller Interest Form to express interest."          ✓
```

Output handling failure:
```
check_seller_eligibility("seller_456")
→ {eligible: false, failed_requirements: [...]}

LLM response: "Great news! Your account is in good standing and you
should be able to apply for eBay Live."                                   ✗
(The tool said ineligible. The LLM said eligible. Output was ignored.)
```

**How to evaluate it**: For binary outcomes (eligible/not eligible, supported/not supported), check that the final response aligns with the `eligible` or `supported` boolean in the tool result. Disagreements between tool output and final response indicate output handling failure.

---

## Part 4 — Why Trace First-Failure Matters (Ch8 §8.3)

### The Cascade Problem

In a multi-step pipeline, errors cascade. A failure at step 1 does not just cause one wrong output — it causes every subsequent step to operate on corrupted inputs.

Consider this trace:

```
Step 1 ParseIntent:    LLM misreads "I want to sell cards" as buyer intent
Step 2 SelectTool:     Calls get_bidding_rules("buyer bidding") [wrong tool for a seller]
Step 3 CallTool:       get_bidding_rules executes, returns buyer auction rules
Step 4 InterpretResult: LLM reads buyer auction rules (correct interpretation of wrong data)
Step 5 GenerateResponse: LLM explains buyer bidding rules to someone who asked about selling
```

If you evaluate all five steps, you find failures at steps 1, 2, 4, and 5.

- Steps 4 and 5 are not really failures — the LLM interpreted the tool's output correctly, it just had the wrong question.
- Step 2 looks like a failure, but it is entirely explained by step 1 — given that the LLM thought this was a buyer question, calling the bidding rules tool is reasonable.
- **The real failure is in step 1**: the intent was misclassified.

If you count failures at all steps, your matrix says: ParseIntent failed once, SelectTool failed once, InterpretResult failed once, GenerateResponse failed once. That is misleading. There was one failure — it just propagated.

### First-Failure Tracking

The principle from Shankar (2026): for each failed trace, identify the **first state** where the agent went off-track, and attribute the failure to that state. Downstream states that failed only because of the upstream mistake are not root-cause failures.

```python
# During trace analysis, find the first failure:
def find_first_failure(trace: list) -> str | None:
    for step in trace["states"]:
        if not step["success"]:
            return step["state"]
    return None  # No failure — overall success
```

This keeps your failure counts honest. A single cascading failure counted once at its source.

### The State-Transition Failure Matrix

The matrix captures not just *where* a failure first occurred, but *what came before it*. The rows represent "the last state that was working correctly" (From State). The columns represent "the state where failure first appeared" (In State / First Failure State).

```
                        First Failure State
                  ┌──────────────┬────────────┬──────────┬─────────────────┬──────────────────┐
                  │ ParseIntent  │ SelectTool │ CallTool │ InterpretResult │ GenerateResponse │
Last Good  ───────┼──────────────┼────────────┼──────────┼─────────────────┼──────────────────┤
State      Start  │      4       │     0      │    0     │        0        │        0         │
           ParseI │      0       │     6      │    0     │        0        │        2         │
           Select │      0       │     0      │    3     │        0        │        0         │
           CallT  │      0       │     0      │    0     │        5        │        0         │
           Interp │      0       │     0      │    0     │        0        │        1         │
                  └──────────────┴────────────┴──────────┴─────────────────┴──────────────────┘
```

Reading this matrix:

**Row "Start → ParseIntent" = 4**
The very first step (intent parsing) failed. These are traces where the LLM couldn't understand the question at all — probably unusual phrasing, missing context, or ambiguous pronouns.

**Row "ParseIntent → SelectTool" = 6**
ParseIntent succeeded, but then the LLM picked the wrong tool. This is the most common failure pattern. Diagnosis: the tool descriptions in the LLM prompt are not clear enough to distinguish when to use `check_seller_eligibility` vs `check_category_eligibility`. Fix: rewrite tool descriptions with more specific trigger phrases.

**Row "ParseIntent → GenerateResponse" = 2**
ParseIntent succeeded, no tool was called, but the final response was wrong. The LLM tried to answer from static knowledge when it should have called a tool. Diagnosis: the static knowledge base is incomplete for these question types, or the prompt doesn't push the LLM hard enough to use tools. Fix: adjust the system prompt to require tool use for specific question categories.

**Row "SelectTool → CallTool" = 3**
The right tool was selected, but the tool call failed. Likely argument generation errors — passing "watches" instead of "luxury watches". Fix: add argument formatting examples to tool descriptions.

**Row "CallTool → InterpretResult" = 5**
The tool call succeeded, but the LLM didn't correctly use the result. This is output handling failure. Diagnosis: the structured JSON output format from the tools is being misread. Fix: add explicit instructions to the prompt about how to interpret `failed_requirements` arrays.

**The key insight**: the matrix tells you not just that failures happened, but the transition that produced them. High counts in a particular column point to a specific component. High counts in a specific row tell you what normal operation looked like before the failure.

---

## Part 5 — Traceability: Log Everything

### The Principle

From Shankar (2026): "Log everything — all artifacts generated as part of the path to answering a query!"

This is not just good engineering hygiene. It is an epistemological requirement. Without complete trace logs, you cannot:
- Distinguish tool selection failures from argument generation failures
- Determine whether a bad response came from a bad tool call or bad output handling
- Reproduce a failure to test a fix
- Build the first-failure matrix at all

### What to Log at Each State

**ParseIntent**
- The raw user query (input)
- The LLM's internal reasoning (if available via chain-of-thought or reasoning trace)
- The identified intent: user type (buyer/seller), topic category, any extracted entities (seller_id, category name)

**SelectTool**
- Which tool was chosen (or that no tool was chosen)
- The full tool call request including name and arguments
- If multiple tool calls were planned: all of them

**CallTool**
- The exact arguments passed to the tool
- The complete tool response (raw JSON)
- Whether the tool raised an exception or returned an error flag

**InterpretResult**
- The tool response that was fed back into the LLM
- The LLM's continuation message (the synthesis step)

**GenerateResponse**
- The final response text
- Whether it was consistent with the tool result (auto-checked)

### What the Trace Object Looks Like

```json
{
  "query_id": "q_042",
  "query": "I sell sports cards — am I eligible for eBay Live?",
  "timestamp": "2026-04-18T14:23:11.445Z",
  "states": [
    {
      "state": "ParseIntent",
      "input": "I sell sports cards — am I eligible for eBay Live?",
      "identified_intent": {"user_type": "seller", "topic": "eligibility"},
      "success": true
    },
    {
      "state": "SelectTool",
      "tool_name": "check_seller_eligibility",
      "args": {"seller_id": "seller_123"},
      "success": true
    },
    {
      "state": "CallTool",
      "tool_name": "check_seller_eligibility",
      "result": {
        "eligible": true,
        "seller_id": "seller_123",
        "requirements_met": {
          "account_in_good_standing": true,
          "sufficient_transaction_history": true,
          "has_eligible_category": true,
          "prior_livestream_experience": true
        },
        "failed_requirements": [],
        "recommendation": "You qualify to apply"
      },
      "success": true
    },
    {
      "state": "InterpretResult",
      "tool_name": "check_seller_eligibility",
      "result_summary": "eligible=true, all requirements met",
      "success": true
    },
    {
      "state": "GenerateResponse",
      "response": "Great news! Based on your account (seller_123), you meet all the requirements to apply for eBay Live. Your account is in good standing, you have sufficient transaction history, you have eligible categories, and you have prior livestreaming experience. You qualify to apply!",
      "success": true
    }
  ],
  "first_failure_state": null,
  "overall_success": true,
  "tool_calls_made": 1,
  "tools_used": ["check_seller_eligibility"]
}
```

Every field in this structure is load-bearing. Remove any one of them and your failure analysis becomes a guess.

---

## Part 6 — The eBay Live Agent: Tools and States

### Available Tools

This stage adds four tools to the eBay Live support bot:

**`check_category_eligibility(category: str)`**
Determines whether a product category is supported on eBay Live. Use this when a buyer or seller asks whether their type of item can be sold or bid on during a stream.

Input: category name (string)
Output: `{supported: bool, category_group: str, subcategories: list}`

Example valid categories: "sports trading cards", "luxury watches", "collectibles", "sneakers"
Common argument mistakes: passing a brand name ("Rolex") instead of a category ("luxury watches"), passing a plural vs. singular mismatch

**`check_seller_eligibility(seller_id: str)`**
Checks whether a specific seller account meets eBay Live's requirements. Use this when a seller asks about their own eligibility to host a livestream.

Input: seller_id (string)
Output: `{eligible: bool, requirements_met: dict, failed_requirements: list, recommendation: str}`

Requirements checked: account standing, transaction history (min 50), eligible category enrollment, prior livestream experience

Common failure modes: passing the full name "seller ABC" instead of extracting the ID "ABC"; passing an unknown seller_id and misinterpreting "Seller not found" as "Seller is ineligible"

**`get_bidding_rules(topic: str)`**
Retrieves specific bidding rules for a given topic. Use this for precise rule questions about auction mechanics.

Valid topics: "soft_close", "bid_retraction", "max_bidding", "payment"
Output: `{rules: list, relevant_to: str}`

Common failure modes: calling this tool for eligibility questions instead of `check_seller_eligibility`; passing a topic the tool doesn't know about and getting an empty response, then not handling the empty response

**`escalate_to_human(reason: str, urgency: str)`**
Creates a human agent ticket. Use this when the user's question is out-of-scope, requires account access, or cannot be resolved by the other tools.

Output: `{ticket_id: str, estimated_wait: str, message: str}`

Agency note: with moderate-low agency, this tool should be called when the agent cannot confidently answer — not held as a last resort after many failed attempts.

### Pipeline States

The eBay Live agent moves through five named states per query:

| State | Description | What goes wrong here |
|---|---|---|
| ParseIntent | LLM reads the query and identifies user type, topic, any entities | Ambiguous query misclassified as buyer vs. seller |
| SelectTool | LLM chooses which tool to call (or no tool) | Wrong tool selected, tool called unnecessarily, tool not called when needed |
| CallTool | Tool executes with LLM-generated arguments | Malformed arguments, unknown category strings, wrong seller ID format |
| InterpretResult | LLM reads the tool's structured JSON response | Binary result misread, "not found" confused with "ineligible", empty array ignored |
| GenerateResponse | LLM produces the final natural language response | Result contradicted, partial information given, incorrect recommendation |

---

## Part 7 — Common Pitfalls

### Pitfall 1: Evaluating Only Final Task Outcomes

It is tempting to re-use Stage 2's approach: collect responses, run an LLM judge, report a pass rate. That approach tells you nothing about which component broke.

Two agents can have identical pass rates but completely different failure distributions:
- Agent A: passes 80% because tool selection is almost always right
- Agent B: passes 80% because output handling is almost always right, but tool selection is terrible and the agent got lucky on questions that don't need tools

You would not know the difference from final-outcome evals alone. The transition matrix reveals this immediately.

### Pitfall 2: Not Defining the Agency Spectrum Upfront

If you do not write down where your agent sits on the spectrum, every ambiguous trace will generate disagreement. "The agent asked for clarification — is that a failure?" becomes unanswerable without a written spectrum definition.

The spectrum definition is also what tells you how to score escalation behavior. For moderate-low agency: escalating is correct. For high agency: escalating prematurely is a failure. Same behavior, opposite scores, depending on the spec.

### Pitfall 3: Missing Traceability

The most expensive pitfall. If you don't log the exact tool arguments and tool responses, debugging agent failures becomes reverse engineering. You have a wrong final answer and no idea whether the problem was in SelectTool, CallTool, or InterpretResult.

Log the arguments. Log the raw response. Log which tool was called. Log whether the call succeeded. Log whether the final response was consistent with the tool output. Do this from day one.

### Pitfall 4: Counting Cascade Failures Multiple Times

Without first-failure tracking, a single cascading error inflates your failure counts at every downstream state. You see high counts in InterpretResult and spend weeks improving output handling, when the real problem was SelectTool misidentifying the tool two steps earlier.

Always find the first failure in a trace. Every subsequent failure in that trace is likely noise.

### Pitfall 5: Building the Matrix Without Enough Traces

The transition matrix is only useful when you have enough traces to see patterns. With 5 traces, every cell is noise. With 50 traces, you start to see which transitions are systematically risky. Aim for at least 30-50 traces per question type in your test set before drawing conclusions from the matrix.

---

## Files in This Stage

| File | Purpose |
|---|---|
| `tools.py` | Mock implementations of all four eBay Live tools |
| `agent_backend.py` | Updated chatbot backend that runs the ReAct loop and produces structured traces |
| `collect_agent_traces.py` | Loads Stage 2 questions, runs each through the agent, saves full traces to `agent_traces/` |
| `transition_matrix.py` | Loads all saved traces, builds the state-transition failure matrix, identifies top hotspots |
| `agent_traces/` | Directory where collected trace JSON files are stored |

---

## How to Run

### Setup

```bash
# From the project root
cd /path/to/stage-7-agent-evals

# Activate the Stage 1 venv
source ../stage-1-chatbot/.venv/bin/activate

# Ensure OPENAI_API_KEY is set
export $(grep -v '^#' ../stage-1-chatbot/.env | xargs)
```

### Step 1: Collect Agent Traces

```bash
python collect_agent_traces.py
```

This loads questions from Stage 2, runs each through the agent, and saves full traces to `agent_traces/`. Output:

```
Collecting agent traces...
  [1/24] buyer_basics: What is eBay Live?  → no tool call
  [2/24] seller_eligibility: How do I become an eBay Live seller?  → check_seller_eligibility
  ...
Done. 24 traces collected.
  - 14 traces with at least one tool call
  - 21 fully successful
  - 3 with failures
Saved to agent_traces/traces_YYYYMMDD_HHMMSS.json
```

### Step 2: Analyze the Transition Matrix

```bash
python transition_matrix.py
```

This loads all trace files, builds the failure matrix, and prints the analysis:

```
State-Transition Failure Matrix
================================

               ParseIntent  SelectTool  CallTool  InterpretResult  GenerateResponse
Start                    1           0         0                0                 0
ParseIntent              0           2         0                0                 1
SelectTool               0           0         1                0                 0
CallTool                 0           0         0                1                 0
InterpretResult          0           0         0                0                 0

Top 3 Hotspot Transitions:
  1. ParseIntent → SelectTool (2 failures)
     Suggestion: Tool descriptions may not clearly distinguish when to use
     check_seller_eligibility vs check_category_eligibility. Add trigger phrases.

  2. ParseIntent → GenerateResponse (1 failure)
     Suggestion: LLM answered from static knowledge when a tool was needed.
     Strengthen system prompt to require tool use for eligibility questions.

  3. Start → ParseIntent (1 failure)
     Suggestion: Query was too ambiguous to parse. Consider adding a
     clarification prompt for very short or vague inputs.
```

---

## Connection to Earlier Stages

**Stage 2 (Trace Dataset)**: The test questions from Stage 2's `test_questions.csv` are reused here as the agent's input queries. The agent must handle all 24 question types.

**Stage 3/4 (Open & Axial Coding)**: The failure dimensions identified in axial coding (hallucination, policy misstatement, wrong user type) map directly onto the failure modes here. ParseIntent failures often correspond to the "wrong user type" dimension. Output handling failures often correspond to "hallucination" (the LLM invents an answer instead of using the tool result).

**Stage 5 (LLM Judge)**: The LLM judge can be re-applied at the step level, not just the final response level. An LLM judge that evaluates tool selection ("was the correct tool called?") is a natural extension of the Stage 5 rubric.

**Stage 8 (CI/Monitoring)**: The transition matrix from this stage becomes the baseline for Stage 8's regression tests. Any future change to tool descriptions, the system prompt, or the ReAct loop should not increase failure counts in the hotspot transitions identified here.

---

## Further Reading

- Shankar & Husain (2026), Chapter 8, §8.1: Failure modes in tool-calling systems
- Shankar & Husain (2026), Chapter 8, §8.2: The agency spectrum and why it must be specified
- Shankar & Husain (2026), Chapter 8, §8.3: State-transition failure matrices
- ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)
- LiteLLM tool calling documentation: https://docs.litellm.ai/docs/completion/function_call
