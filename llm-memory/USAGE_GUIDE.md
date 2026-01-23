# 📖 Detailed Usage Guide

This guide walks you through all features of the LLM Memory Learning Platform.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Tab 1: Side-by-Side Comparison](#tab-1-side-by-side-comparison)
3. [Tab 2: Memory Deep Dives](#tab-2-memory-deep-dives)
4. [Tab 3: Memory Internals](#tab-3-memory-internals)
5. [Tab 4: Playground](#tab-4-playground)
6. [Understanding the Sidebar](#understanding-the-sidebar)
7. [Advanced Topics](#advanced-topics)

---

## Getting Started

### First Launch

1. **Load Knowledge Base**
   - Look for "📚 Load Sample Knowledge Base" button in sidebar
   - Click it and wait ~10 seconds for indexing
   - You'll see "✅ Knowledge Base Loaded" when ready

2. **Choose Your Path**
   - **Quick Learner**: Go to Tab 1 (Side-by-Side Comparison)
   - **Deep Diver**: Start with Tab 2 (Memory Deep Dives)
   - **Visual Learner**: Check out Tab 3 (Memory Internals)
   - **Experimenter**: Jump to Tab 4 (Playground)

---

## Tab 1: Side-by-Side Comparison

**Purpose**: See the dramatic difference memory makes in LLM responses.

### What You See
- **Left Column**: Chatbot WITH memory (uses episodic + semantic)
- **Right Column**: Chatbot WITHOUT memory (no context)
- **Input Box**: Send same question to both

### How to Use

1. **Simple Knowledge Query**
   ```
   Type: "How many vacation days do I get?"
   Click: "Send to Both"
   Compare: LEFT gives "15 days" | RIGHT gives generic answer
   ```

2. **Multi-Turn Conversation**
   ```
   Turn 1: "I'm planning a team event for 20 people"
   Turn 2: "What's a good budget per person?"
   Turn 3: "Can you suggest some activities?"

   WITH memory: Remembers "team event for 20" throughout
   WITHOUT memory: Confused after Turn 1
   ```

3. **Knowledge Retrieval Test**
   ```
   Try these:
   - "Can I work remotely?"
   - "What's the parental leave policy?"
   - "What can I expense for meals?"

   WITH memory: Specific answers from documents
   WITHOUT memory: Generic suggestions
   ```

### Understanding the Results

**"🔍 Memory Used" Expander** (only on WITH memory side)
- Shows which documents were retrieved
- Displays similarity scores (0.0 to 1.0)
- Shows how many conversation turns are in context

**Token Comparison** (bottom of tab)
- Shows token usage for both sides
- Explains why WITH memory uses more tokens
- Demonstrates the accuracy vs. cost trade-off

---

## Tab 2: Memory Deep Dives

**Purpose**: Understand each memory type in detail.

### Episodic Memory Explorer

**What It Shows**:
- Complete conversation history
- Token usage per turn
- Context window visualization
- Sliding window mechanism

**How to Use**:
1. Select "Episodic Memory" from dropdown
2. Read the concept explanation
3. Review your conversation turns (if any)
4. Study the token usage chart
5. See which turns are kept vs. dropped

**Key Insights**:
- Each turn has timestamp and token count
- Total tokens shown with context window limit
- Older turns are dropped when limit reached
- This is why LLMs can't remember infinite history

### Semantic Memory Explorer

**What It Shows**:
- Indexed documents and chunk counts
- Interactive retrieval testing
- 2D embedding space visualization
- Similarity scores

**How to Use**:
1. Select "Semantic Memory" from dropdown
2. Review indexed documents
3. Type a test query (e.g., "vacation policy")
4. See which chunks are retrieved
5. Study the 2D embedding plot

**Understanding the Visualization**:
- **Dots** = Document chunks
- **Colors** = Different documents
- **Star** = Your query
- **Lines** = Retrieval connections
- **Proximity** = Semantic similarity

**Key Insights**:
- Similar content clusters together in vector space
- Your query appears near relevant chunks
- Similarity scores show retrieval confidence
- Higher threshold = fewer, more precise results

### Working Memory Explorer

**What It Shows**:
- Concept of chain-of-thought reasoning
- How LLMs break down complex problems
- Step-by-step thought process

**Note**: This is demonstrated through LLM responses rather than explicit visualization. Try complex questions to see multi-step reasoning.

---

## Tab 3: Memory Internals

**Purpose**: Understand HOW memory works under the hood.

### Step-by-Step Process

**Step 1: Document Upload**
- Shows how documents enter the system
- Understanding: This is your knowledge source

**Step 2: Text Chunking**
- Shows document split into chunks
- Understanding: Smaller chunks = better retrieval precision

**Step 3: Embedding**
- Shows conversion to 384-dimensional vectors
- Understanding: Neural network creates semantic representations

**Step 4: Storage**
- Shows vectors stored in ChromaDB
- Understanding: Fast similarity search becomes possible

**Step 5: Retrieval**
- Shows complete query → retrieval → augmentation flow
- Understanding: This is the full RAG pipeline

### Prompt Assembly

**What It Shows**:
The EXACT prompt the LLM receives, including:
1. System instructions
2. Retrieved context (semantic memory)
3. Conversation history (episodic memory)
4. Current question

**Why This Matters**:
- Makes it clear the LLM doesn't "know" things
- Shows how context is assembled
- Explains token usage
- Reveals why memory improves accuracy

**How to Use**:
1. Use the slider to navigate steps 1-5
2. Read each step carefully
3. Study the prompt assembly at the bottom
4. Expand each section to see the full content

---

## Tab 4: Playground

**Purpose**: Experiment with settings and see their impact.

### Controls

**Memory Toggles**:
- ☑️ Use Episodic Memory: On/Off
- ☑️ Use Semantic Memory: On/Off

**Retrieval Parameters**:
- **Top-K** (1-10): Number of chunks to retrieve
- **Threshold** (0.0-1.0): Minimum similarity score

### Experiments to Try

**Experiment 1: No Memory Baseline**
```
Settings: Both toggles OFF
Query: "How many vacation days?"
Result: Generic answer (no specific info)
```

**Experiment 2: Semantic Only**
```
Settings: Episodic OFF, Semantic ON
Query: "How many vacation days?"
Result: Accurate but no conversation context
```

**Experiment 3: Both Memory Types**
```
Settings: Both ON
Query: "Tell me about vacation"
Then: "Can I carry days over?"
Result: Accurate + maintains conversation context
```

**Experiment 4: Top-K Impact**
```
Settings: Top-K = 1 vs Top-K = 10
Query: "Tell me about employee benefits"
Compare: Focused vs. comprehensive context
```

**Experiment 5: Threshold Impact**
```
Settings: Threshold = 0.5 vs 0.9
Query: "remote work"
Compare: Many results vs. only highly relevant
```

### Understanding Results

The playground shows:
- **Response**: LLM's answer
- **Memory Usage Metrics**:
  - Episodic turns included
  - Semantic chunks retrieved
  - Total tokens used
- **Retrieved Chunks**: What was found and similarity scores

---

## Understanding the Sidebar

### Settings Panel

**Episodic Memory**:
- **Max History** (3-20): How many turns to keep
  - Lower = less memory, cheaper, faster
  - Higher = more context, better continuity

**Semantic Memory**:
- **Top-K** (1-10): Chunks to retrieve
  - Lower = focused, precise
  - Higher = comprehensive, may include noise

- **Similarity Threshold** (0.0-1.0): Minimum match quality
  - Lower = more results, less precise
  - Higher = fewer results, highly relevant

**LLM Settings**:
- **Model**: haiku (fast) | sonnet (balanced) | opus (powerful)
- **Temperature** (0.0-1.0): Response creativity
  - 0.0 = Deterministic, focused
  - 1.0 = Creative, varied

### Demo Scenarios

**Pre-Built Scenarios**:
- Click to auto-fill questions
- Designed to showcase specific memory features
- Great for learning or demonstrations

**Quick Questions**:
- One-click common queries
- Test knowledge retrieval
- See immediate results

### Memory Statistics

**Live Metrics**:
- **Conv Turns**: Episodic memory size
- **Doc Chunks**: Semantic memory size
- **Retrievals**: Times semantic memory was used
- **Tokens Used**: Cumulative token consumption

### Reset Button

**🔄 Reset All Conversations**:
- Clears episodic memory (both WITH and WITHOUT)
- Clears chat display
- Resets token counters
- Does NOT clear knowledge base

---

## Advanced Topics

### Token Management

**Why Tokens Matter**:
- APIs charge per token
- Context windows have limits
- More context = better accuracy BUT higher cost

**Strategies**:
1. Use Haiku for learning (cheapest)
2. Reduce max history for long conversations
3. Increase similarity threshold to retrieve less
4. Monitor token usage in statistics

### Optimizing Retrieval

**For Better Accuracy**:
- Increase Top-K (get more context)
- Lower similarity threshold (cast wider net)
- Add more documents to knowledge base

**For Better Precision**:
- Decrease Top-K (only best matches)
- Increase similarity threshold (only highly relevant)
- Use more focused queries

**For Speed/Cost**:
- Use Haiku model
- Decrease Top-K
- Increase similarity threshold
- Reduce max history

### Understanding Similarity Scores

**Score Ranges**:
- **0.90-1.00**: Excellent match (highly relevant)
- **0.80-0.89**: Very good match (relevant)
- **0.70-0.79**: Good match (likely relevant)
- **0.60-0.69**: Fair match (may be relevant)
- **Below 0.60**: Weak match (likely not relevant)

**Default threshold of 0.7** balances precision and recall.

### Adding Your Own Documents

**Method 1: Add to sample_docs/**
1. Create `.txt` file in `knowledge_base/sample_docs/`
2. Restart app
3. Click "Load Sample Knowledge Base"

**Method 2: Programmatically** (requires code edit)
```python
# In sidebar, after KB loaded:
uploaded_file = st.file_uploader("Upload document")
if uploaded_file:
    content = uploaded_file.read().decode()
    st.session_state.semantic.add_document(
        document_text=content,
        document_name=uploaded_file.name
    )
```

### Interpreting Embedding Visualizations

**What You're Seeing**:
- High-dimensional vectors (384-D) projected to 2D
- PCA preserves variance, shows major patterns
- t-SNE would preserve local structure better (slower)

**What It Means**:
- Clusters = topically related content
- Distance = semantic difference
- Query near cluster = good retrieval candidate

**Limitations**:
- 2D projection loses information
- Exact distances are approximate
- Colors are for visual distinction only

---

## Tips for Learning

1. **Start Simple**: Use side-by-side with basic questions
2. **Observe Patterns**: Notice when memory helps most
3. **Experiment**: Try playground with different settings
4. **Study Internals**: Understand the process, not just results
5. **Take Notes**: Document your insights
6. **Ask Complex Questions**: See multi-step reasoning
7. **Compare Models**: Try Haiku vs Sonnet responses

## Common Questions

**Q: Why does WITH memory sometimes take longer?**
A: It's doing extra work (retrieval + more tokens to process)

**Q: Can I use this with my own documents?**
A: Yes! Add `.txt` files to `knowledge_base/sample_docs/`

**Q: Why are some retrievals low quality?**
A: Try adjusting similarity threshold or rephrasing your query

**Q: What's the best model to use?**
A: Haiku for learning (fast/cheap), Sonnet for quality, Opus for best results

**Q: How much does this cost?**
A: Very little with Haiku. Most queries cost fractions of a cent.

---

## Next Steps

After mastering this platform:
1. Build your own RAG application
2. Experiment with different embedding models
3. Try different vector databases (Pinecone, Weaviate)
4. Implement custom memory strategies
5. Explore advanced prompting techniques

**Happy Learning! 🧠**
