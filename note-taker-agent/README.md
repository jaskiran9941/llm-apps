# Note-Taker Agent: 5 Levels of Agentic Software

A learning project for product managers who want to understand agent architecture from first principles.
Built with raw `anthropic` SDK — no frameworks, so you see every decision explicitly.

---

## The Big Idea

We build a note-taking app 5 times. Each version adds exactly one architectural capability and then hits a natural wall. The wall is the lesson.

| Level | What it adds | The wall you hit |
|-------|-------------|-----------------|
| **L1: Tools** | Agent loop + 4 tools | Stateless — forgets everything on session restart |
| **L2: Storage + Knowledge** | SQLite history + ChromaDB semantic search | No user model — can't adapt to preferences |
| **L3: Memory + Learning** | Extracts and persists user preferences | One agent overloaded on complex tasks |
| **L4: Multi-Agent** | Orchestrator + specialist agents | Runs locally only, no real-world deployment |
| **L5: Production** | Architecture walkthrough (reading, not building) | — |

---

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY=your_key_here
# Or create a .env file:
echo "ANTHROPIC_API_KEY=your_key" > .env
```

---

## Level 1: Agent with Tools

**The question answered:** What is an agent, actually?

```bash
cd level1_tools
streamlit run app.py
```

**What to read first:** `agent.py` — every line matters. The `while True` loop IS the agent.

**The agent loop in plain English:**
1. Send user message to Claude (with tool schemas attached)
2. Claude says "I want to call save_note" → you execute it → feed result back
3. Claude says "done" → you show the response
4. Repeat from step 1 on next message

**What makes this "agentic":**
- Claude *decides* whether to use a tool or respond directly
- Claude *decides* which tool to call
- Claude *decides* when it's done (via `stop_reason`)
- The loop runs until Claude stops it — not until your code stops it

**What to do:**
1. Read `tools.py` — notice the split between tool schemas (for Claude) and implementations (for Python)
2. Read `agent.py` — follow the loop logic
3. Run it: `streamlit run app.py`
4. Save 3 notes, list them, delete one
5. Click "New Session" and ask about your notes → watch it fail

**The wall:** `messages = []` resets every session. The agent is stateless. Notes survive on disk, but Claude's context doesn't.

---

## Level 2: Agent with Storage and Knowledge

*(Coming next)*

Two additions:
- **SQLite:** Session history persists. Start a new session, agent remembers your conversation.
- **ChromaDB:** Notes are embedded. Ask "find notes about strategy" → finds semantically similar notes even without exact keyword match.

---

## Level 3: Agent with Memory and Learning

*(Coming later)*

One addition: After every interaction, a second Claude call extracts what's worth remembering about *you* — your preferences, your formatting style, how you tag things. Injected at session start.

---

## Level 4: Multi-Agent Team

*(Coming later)*

The orchestrator receives requests and delegates to specialists:
- **Tagger:** Classifies notes (read-only)
- **Summarizer:** Digests and extracts action items (read-only)
- **Connector:** Finds relationships between notes (read-only)
- **Writer:** The only agent with write access

---

## Level 5: Production Architecture

*(Coming later)*

Reading only — what it takes to ship this to real users: PostgreSQL, FastAPI, auth, tracing, async execution, cost management.

---

## Learning Philosophy

For each level:
1. **Read** the code before running (understand every line)
2. **Run** it and interact naturally
3. **Break** it intentionally (ask something it can't do)
4. **Understand** why it failed
5. **Read** what the next level adds

The failures are the curriculum.
