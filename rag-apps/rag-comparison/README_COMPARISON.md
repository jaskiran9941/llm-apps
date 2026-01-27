# RAG Approaches Comparison

This project demonstrates three different RAG (Retrieval-Augmented Generation) approaches side-by-side:

1. **Traditional RAG**: Simple retrieve-then-generate baseline
2. **Corrective RAG (CRAG)**: Adds relevance grading and corrective actions
3. **Agentic RAG**: Full autonomous reasoning with multi-iteration refinement

## Key Differences

### Traditional RAG
- **Flow**: Retrieve → Generate
- **LLM Calls**: 1 (generation only)
- **Retrievals**: 1 (no retry)
- **Best for**: Fast responses when documents are known to be relevant
- **Limitations**: No quality check, returns whatever is retrieved

### Corrective RAG (CRAG)
- **Flow**: Retrieve → Grade → Correct (if needed) → Generate
- **LLM Calls**: 2-4 (grade + optional rewrite + generate)
- **Retrievals**: 1-2 (may retry with rewritten query or web search)
- **Best for**: Balancing quality and efficiency
- **Features**:
  - Relevance grading (relevant/ambiguous/not_relevant)
  - Query rewriting for better retrieval
  - Automatic fallback to web search
  - Explicit correction trace

### Agentic RAG
- **Flow**: Multi-iteration ReAct loop (Thought → Action → Observation → Reflection)
- **LLM Calls**: 3-7+ (planning + evaluation per iteration + generation)
- **Retrievals**: 1-3 (adaptive based on self-evaluation)
- **Best for**: Complex queries requiring thorough research
- **Features**:
  - Autonomous tool selection
  - Self-evaluation (1-10 score)
  - Dynamic replanning based on results
  - Full reasoning trace

## Project Structure

```
RAG/
├── traditional_rag.py      # Simple baseline RAG
├── corrective_rag.py       # CRAG implementation
├── agent.py                # Agentic RAG (existing)
├── tools.py                # Shared retrieval tools
├── config.py               # Configuration
├── app_comparison.py       # Streamlit comparison UI
├── test_comparison.py      # Quick test script
└── documents/              # Your documents go here
```

## Setup

1. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

2. **Add your OpenAI API key**:
Create a `.env` file:
```
OPENAI_API_KEY=your_key_here
```

3. **Add documents**:
Place PDF or text files in the `./documents/` directory

4. **Run the comparison UI**:
```bash
streamlit run app_comparison.py
```

## Quick Test

To verify all systems work:
```bash
python test_comparison.py
```

## Using the Comparison UI

1. **Launch the app**:
   ```bash
   streamlit run app_comparison.py
   ```

2. **Enter a question** in the text input

3. **Run comparison**:
   - Click "🚀 Run All" to test all three approaches
   - Or click individual buttons to run specific approaches

4. **Compare results**:
   - View answers side-by-side in three columns
   - Expand sections to see reasoning traces
   - Check metrics (LLM calls, time, retrievals)

## Example Queries

### Query in local docs
**Question**: "What is our product roadmap?"
- Traditional: Fast, direct answer
- Corrective: Grades as "relevant", proceeds to generate
- Agentic: May do 1-2 iterations, highest quality

### Query NOT in local docs
**Question**: "What is the latest news about AI?"
- Traditional: Poor answer from irrelevant docs
- Corrective: Grades as "not_relevant", switches to web search
- Agentic: Tries local first, then web search, evaluates results

### Ambiguous query
**Question**: "How does it work?"
- Traditional: Confusing answer
- Corrective: Rewrites to "How does [product] work?", better results
- Agentic: Multiple iterations to clarify and refine

## Understanding the Traces

### Corrective RAG Trace
Shows 4 steps:
1. **Initial Retrieval**: Documents found from local DB
2. **Grading**: Relevance assessment with confidence score
3. **Corrective Action**: Query rewrite OR web search (if needed)
4. **Generation**: Final answer from best documents

### Agentic RAG Trace
Shows per iteration:
- **Thought**: Agent's reasoning about what to do
- **Action**: Tool choice and query
- **Observation**: What was found
- **Reflection**: Self-evaluation (score 1-10)

## Performance Comparison

| Approach | Speed | Quality | LLM Calls | Retrieval Attempts |
|----------|-------|---------|-----------|-------------------|
| Traditional | ⚡⚡⚡ | ⭐⭐ | 1 | 1 |
| Corrective | ⚡⚡ | ⭐⭐⭐ | 2-4 | 1-2 |
| Agentic | ⚡ | ⭐⭐⭐⭐ | 3-7+ | 1-3 |

## When to Use Each Approach

### Use Traditional RAG when:
- Speed is critical
- Documents are highly relevant and well-indexed
- Budget is very limited
- Simple factual queries

### Use Corrective RAG when:
- Need quality assurance
- Document relevance is uncertain
- Want explicit correction tracking
- Moderate complexity queries

### Use Agentic RAG when:
- Highest quality required
- Complex research tasks
- Multiple retrieval strategies needed
- Full transparency desired

## Configuration

Edit `config.py` to adjust:
- `MAX_ITERATIONS`: Max agentic iterations (default: 3)
- `EVALUATION_THRESHOLD`: Min score to accept (default: 7/10)
- `MAX_DOCS_PER_RETRIEVAL`: Documents per retrieval (default: 5)
- `LLM_MODEL`: Model to use (default: gpt-4o-mini)
- `TEMPERATURE`: Response creativity (default: 0.7)

## Troubleshooting

### "No documents found"
- Add PDF or TXT files to `./documents/`
- Restart the app

### "Vector database not initialized"
- Make sure documents are in `./documents/`
- Check file permissions

### Web search fails
- Corrective/Agentic RAG will fall back to local docs
- Check internet connection

## Technical Details

### Corrective RAG Grading Logic
```python
if relevance == "relevant":
    action = "none"  # Proceed to generation
elif relevance == "ambiguous":
    action = "rewrite"  # Rewrite query, try local again
else:  # not_relevant
    action = "web_search"  # Switch to web search
```

### Agentic RAG Iteration Logic
```python
while iteration < MAX_ITERATIONS:
    plan = _plan_next_action()  # LLM decides tool & query
    result = _call_tool(plan)
    evaluation = _evaluate_results()  # LLM scores 1-10

    if evaluation.score >= THRESHOLD:
        return generate_answer()
    # else: continue loop with new strategy
```

## License

MIT License - see LICENSE file

## Credits

Built with:
- OpenAI GPT-4o-mini
- LangChain
- ChromaDB
- Streamlit
- DuckDuckGo Search
