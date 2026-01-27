# RAG System Architecture Comparison

This document compares three RAG implementations: Traditional, Corrective, and Agentic.

## Traditional RAG - High-Level Flow

```
┌─────────────┐
│   Question  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Retrieve Docs  │  ← Single retrieval from vector DB
│   (Vector DB)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Generate Answer │  ← LLM generates directly
│      (LLM)      │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│   Answer    │
└─────────────┘
```

## Corrective RAG (CRAG) - High-Level Flow

```
┌─────────────┐
│   Question  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Retrieve Local  │  ← Step 1: Retrieve
│   Documents     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Grade Relevance │  ← Step 2: LLM grades
│      (LLM)      │
└──────┬──────────┘
       │
       ├─────────────┬──────────────┐
       │             │              │
   Relevant    Ambiguous      Not Relevant
       │             │              │
       │             ▼              ▼
       │      ┌──────────────┐ ┌──────────────┐
       │      │ Rewrite Query│ │ Web Search   │  ← Step 3: Correction
       │      │     (LLM)    │ │  (External)  │
       │      └──────┬───────┘ └──────┬───────┘
       │             │              │
       │             ▼              │
       │      ┌──────────────┐     │
       │      │  Retrieve    │     │
       │      │  Again       │     │
       │      └──────┬───────┘     │
       │             │              │
       └─────────────┴──────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │ Generate Answer │  ← Step 4: Generate
              │      (LLM)      │
              └──────┬──────────┘
                     │
                     ▼
              ┌─────────────┐
              │   Answer    │
              └─────────────┘
```

## Agentic RAG (ReAct) - High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER QUESTION                               │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AGENTIC RAG SYSTEM                              │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              ITERATION LOOP (Max: 3)                         │   │
│  │                                                               │   │
│  │  ┌──────────────────────────────────────────────────┐       │   │
│  │  │  STEP 1: REASONING (LLM-Powered)                  │       │   │
│  │  │  ┌──────────────────────────────────────────┐    │       │   │
│  │  │  │ Input:                                    │    │       │   │
│  │  │  │  - User question                          │    │       │   │
│  │  │  │  - Previous attempts & results            │    │       │   │
│  │  │  │  - Available tools                        │    │       │   │
│  │  │  │                                           │    │       │   │
│  │  │  │ Agent Thinks:                            │    │       │   │
│  │  │  │  "What information do I need?"           │    │       │   │
│  │  │  │  "Which tool is best for this?"          │    │       │   │
│  │  │  │  "How should I refine my query?"         │    │       │   │
│  │  │  │                                           │    │       │   │
│  │  │  │ Output:                                  │    │       │   │
│  │  │  │  - Chosen tool                           │    │       │   │
│  │  │  │  - Query to use                          │    │       │   │
│  │  │  │  - Reasoning trace                       │    │       │   │
│  │  │  └──────────────────────────────────────────┘    │       │   │
│  │  └──────────────────────┬───────────────────────────┘       │   │
│  │                         │                                     │   │
│  │                         ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────┐       │   │
│  │  │  STEP 2: ACTION (Tool Execution)                  │       │   │
│  │  │                                                    │       │   │
│  │  │  ┌──────────────────┐    ┌──────────────────┐   │       │   │
│  │  │  │ search_local_docs│    │   search_web     │   │       │   │
│  │  │  ├──────────────────┤    ├──────────────────┤   │       │   │
│  │  │  │ • ChromaDB       │    │ • DuckDuckGo API │   │       │   │
│  │  │  │ • OpenAI Embed   │    │ • Returns web    │   │       │   │
│  │  │  │ • Vector search  │    │   search results │   │       │   │
│  │  │  │ • Returns docs   │    │                  │   │       │   │
│  │  │  └──────────────────┘    └──────────────────┘   │       │   │
│  │  │                                                    │       │   │
│  │  └──────────────────────┬───────────────────────────┘       │   │
│  │                         │                                     │   │
│  │                         ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────┐       │   │
│  │  │  STEP 3: OBSERVATION                              │       │   │
│  │  │  ┌──────────────────────────────────────────┐    │       │   │
│  │  │  │ Record:                                   │    │       │   │
│  │  │  │  - Retrieved documents                    │    │       │   │
│  │  │  │  - Number of results                      │    │       │   │
│  │  │  │  - Any errors                             │    │       │   │
│  │  │  └──────────────────────────────────────────┘    │       │   │
│  │  └──────────────────────┬───────────────────────────┘       │   │
│  │                         │                                     │   │
│  │                         ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────┐       │   │
│  │  │  STEP 4: REFLECTION (LLM-Powered Evaluation)     │       │   │
│  │  │  ┌──────────────────────────────────────────┐    │       │   │
│  │  │  │ Agent Evaluates:                         │    │       │   │
│  │  │  │  "Do these docs answer the question?"    │    │       │   │
│  │  │  │  "Quality score: ?/10"                   │    │       │   │
│  │  │  │  "What's missing?"                       │    │       │   │
│  │  │  │                                           │    │       │   │
│  │  │  │ Decision:                                │    │       │   │
│  │  │  │  Score >= 7 → SUFFICIENT ✓              │    │       │   │
│  │  │  │  Score < 7  → TRY AGAIN ↻               │    │       │   │
│  │  │  └──────────────────────────────────────────┘    │       │   │
│  │  └──────────────────────┬───────────────────────────┘       │   │
│  │                         │                                     │   │
│  │                         ▼                                     │   │
│  │             ┌─────────────────────┐                          │   │
│  │             │  Sufficient?         │                          │   │
│  │             └─────────┬───────────┘                          │   │
│  │                       │                                       │   │
│  │          NO ◄─────────┴────────► YES                         │   │
│  │           │                       │                           │   │
│  │   ┌───────▼────────┐             │                          │   │
│  │   │ Loop back to   │             │                          │   │
│  │   │ STEP 1 with    │             │                          │   │
│  │   │ updated context│             │                          │   │
│  │   └────────────────┘             │                          │   │
│  │                                   │                           │   │
│  └───────────────────────────────────┼───────────────────────────┘
│                                      │                            │
└──────────────────────────────────────┼────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL ANSWER GENERATION                           │
│                                                                       │
│  Input:                                                              │
│   - Original question                                                │
│   - ALL retrieved documents (from all iterations)                   │
│   - Context from multiple sources                                   │
│                                                                       │
│  LLM synthesizes comprehensive answer with citations                │
│                                                                       │
│  Output:                                                             │
│   - Answer text                                                      │
│   - Source citations                                                │
│   - Full reasoning trace                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Agent Core (`agent.py`)

**Responsibilities:**
- Orchestrates the ReAct loop
- Manages conversation state
- Coordinates between reasoning, action, and evaluation

**Key Methods:**
- `research(question)` - Main entry point
- `_plan_next_action()` - Reasoning step
- `_call_tool()` - Action execution
- `_evaluate_results()` - Reflection step
- `_generate_answer()` - Final synthesis

---

### 2. Retrieval Tools (`tools.py`)

#### LocalDocumentRetriever
```
Documents → Text Splitter → OpenAI Embeddings → ChromaDB
                                                      ↓
Query → OpenAI Embeddings → Vector Search → Top K Docs
```

**Features:**
- Loads PDFs, .txt, .md files
- Chunks with overlap for context preservation
- Semantic search via embeddings
- Persistent vector storage

#### WebSearchRetriever
```
Query → DuckDuckGo API → Search Results → Formatted Docs
```

**Features:**
- Real-time web search
- No API key required (DuckDuckGo)
- Returns title, snippet, URL

---

### 3. Configuration (`config.py`)

**Tunable Parameters:**
- `MAX_ITERATIONS`: How many times agent tries (default: 3)
- `EVALUATION_THRESHOLD`: Quality bar for accepting results (default: 7/10)
- `LLM_MODEL`: Which OpenAI model (default: gpt-4o-mini)
- `EMBEDDING_MODEL`: Embedding model for vectors
- `CHUNK_SIZE`: Document chunk size

---

### 4. Streamlit UI (`app.py`)

**Features:**
- Chat interface
- Expandable reasoning traces
- Knowledge base management
- Real-time streaming
- Source citations

---

## Data Flow Example

### Query: "What is quantum entanglement?"

```
INPUT: "What is quantum entanglement?"
  │
  ▼
[ITERATION 1]
  │
  ├─ REASONING:
  │    Input: Question + empty history + 2 tools
  │    LLM Thinks: "Physics question, check local docs first"
  │    Output: {tool: "search_local_docs", query: "quantum entanglement"}
  │
  ├─ ACTION:
  │    Execute: LocalDocumentRetriever.search("quantum entanglement")
  │    Result: [1 document with brief mention]
  │
  ├─ OBSERVATION:
  │    Record: "Found 1 doc, content: 'quantum entanglement is...'"
  │
  ├─ REFLECTION:
  │    LLM Evaluates: "This doc only mentions it briefly. Score: 3/10"
  │    Decision: NOT SUFFICIENT (3 < 7)
  │
  └─ CONTINUE TO ITERATION 2
       │
       ▼
[ITERATION 2]
  │
  ├─ REASONING:
  │    Input: Question + {attempt 1: local search failed} + 2 tools
  │    LLM Thinks: "Local docs insufficient. Need comprehensive source.
  │                 Try web search with detailed query."
  │    Output: {tool: "search_web",
  │             query: "quantum entanglement detailed explanation physics"}
  │
  ├─ ACTION:
  │    Execute: WebSearchRetriever.search("quantum entanglement...")
  │    Result: [5 web pages from Wikipedia, physics sites]
  │
  ├─ OBSERVATION:
  │    Record: "Found 5 high-quality sources"
  │
  ├─ REFLECTION:
  │    LLM Evaluates: "Excellent sources with detailed explanations. Score: 9/10"
  │    Decision: SUFFICIENT! (9 >= 7)
  │
  └─ EXIT LOOP
       │
       ▼
[FINAL GENERATION]
  │
  ├─ Input:
  │    - Question: "What is quantum entanglement?"
  │    - All docs: [1 local doc + 5 web results]
  │
  ├─ LLM Synthesis:
  │    Combines information from multiple sources
  │    Provides comprehensive answer
  │    Cites Wikipedia and physics sources
  │
  └─ Output:
       Answer: "Quantum entanglement is a phenomenon in quantum physics where..."
       Sources: [Wikipedia URL, Physics Today URL, ...]
       Trace: [Full reasoning from both iterations]
```

---

## Why This Architecture is Truly Agentic

1. **Autonomous Decision-Making**
   - Agent chooses tools based on context, not hardcoded rules
   - Decides when to stop based on quality evaluation

2. **Self-Awareness**
   - Evaluates its own retrieval results
   - Knows what it doesn't know

3. **Adaptive Behavior**
   - Changes strategy based on failures
   - Refines queries iteratively

4. **Goal-Directed**
   - Persists until quality threshold met
   - Has clear success criteria

5. **Transparent**
   - Full reasoning trace available
   - Explainable decision process

---

## Scalability Considerations

**Current Implementation:**
- Single-user, local deployment
- Synchronous execution
- In-memory state

**Production Enhancements:**
- [ ] Add caching layer for repeated queries
- [ ] Implement async/parallel tool execution
- [ ] Add conversation persistence (database)
- [ ] Rate limiting and cost controls
- [ ] Multi-tenant vector database
- [ ] Streaming responses
- [ ] Tool result caching
- [ ] User feedback loop for fine-tuning

---

## Cost Analysis

**Per Query Cost (Estimated):**

Iteration 1:
- Planning: ~500 tokens ($0.0015)
- Evaluation: ~400 tokens ($0.0012)
- Embedding: ~100 tokens ($0.00002)

Iteration 2:
- Planning: ~700 tokens ($0.0021)
- Evaluation: ~400 tokens ($0.0012)

Final Answer:
- Generation: ~1000 tokens ($0.003)

**Total per query: ~$0.009 - $0.015**
(vs ~$0.003 for traditional RAG)

**Cost is 3-5x higher, but answer quality is significantly better for complex questions.**
