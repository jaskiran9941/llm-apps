# Truly Agentic RAG Research Assistant

A genuinely agentic RAG system with self-evaluation, dynamic replanning, and multi-step reasoning.

## What Makes This "Truly Agentic"

Unlike simple RAG pipelines, this system:

✅ **Self-Evaluation** - Judges if retrieved information answers the question
✅ **Dynamic Replanning** - Changes strategy when initial approach fails
✅ **Multi-Step Reasoning** - Can retrieve multiple times, refining queries
✅ **Tool Selection** - Autonomously chooses between local docs and web search
✅ **Loop Prevention** - Tracks attempts to avoid infinite loops
✅ **Transparent Reasoning** - Shows its thought process

## Architecture

```
User Query
    ↓
Agent Reasoning: "What do I know? What do I need?"
    ↓
Choose Tool: Local Vector DB or Web Search
    ↓
Retrieve Information
    ↓
Self-Evaluate: "Does this answer the question?"
    ↓
If YES → Generate Answer
If NO  → Refine query and try again (different tool/strategy)
    ↓
Max 3 retrieval attempts to prevent loops
```

## Features

1. **Dual Retrieval**: Vector database (local docs) + Web search fallback
2. **ReAct Loop**: Reasoning → Action → Observation → Reflection
3. **Quality Control**: Self-critique before answering
4. **Strategy Adaptation**: Learns from failed retrievals
5. **Conversation Memory**: Maintains context across queries

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# (Optional) Set Tavily API key for better web search
export TAVILY_API_KEY="your-key-here"

# Add your documents to /documents folder
mkdir documents
# Add PDFs, text files, or markdown files

# Run the Streamlit app
streamlit run app.py
```

## Usage

1. **Add Documents**: Place PDFs/text files in `documents/` folder
2. **Initialize**: Click "Initialize Knowledge Base" in the UI
3. **Ask Questions**: The agent will autonomously decide how to find answers
4. **Watch Reasoning**: See the agent's thought process in real-time

## Example Agent Behavior

**Query**: "What is quantum entanglement?"

```
[THOUGHT] I need to find information about quantum entanglement.
          Let me check local documents first.

[ACTION] search_local_docs("quantum entanglement")

[OBSERVATION] Found 2 documents, but they only mention entanglement
              briefly without detailed explanation.

[REFLECTION] The local docs don't have enough detail. I should search
             the web for a comprehensive explanation.

[ACTION] search_web("quantum entanglement detailed explanation")

[OBSERVATION] Found comprehensive Wikipedia and physics articles
              explaining the concept.

[REFLECTION] Good! This information is detailed and authoritative.
             I can now answer the question.

[ANSWER] Quantum entanglement is a phenomenon where...
```

## Configuration

Edit `config.py` to customize:
- `MAX_ITERATIONS`: Maximum retrieval attempts (default: 3)
- `EVALUATION_THRESHOLD`: Quality threshold for accepting results (default: 7/10)
- `EMBEDDING_MODEL`: Which embedding model to use
- `LLM_MODEL`: Which language model for reasoning

## Tech Stack

- **Vector DB**: ChromaDB (local, embedded)
- **Web Search**: Tavily API (or DuckDuckGo fallback)
- **LLM**: OpenAI GPT-4 (configurable)
- **Embeddings**: OpenAI text-embedding-3-small
- **UI**: Streamlit
- **Agent Loop**: Custom ReAct implementation

## File Structure

```
├── app.py                 # Streamlit UI
├── agent.py              # Agentic reasoning loop
├── tools.py              # Retrieval tools (vector DB + web)
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── documents/            # Your knowledge base
└── chroma_db/           # Vector database storage
```

## Why This is Actually Agentic

Most "agentic RAG" systems are just:
```python
if vector_search_fails:
    web_search()
```

This system actually:
1. **Reasons** about what information it needs
2. **Evaluates** if retrieved info is good enough
3. **Adapts** its strategy based on results
4. **Persists** until satisfied or max attempts reached
5. **Explains** its decision-making process

## Limitations

- Requires API keys (OpenAI, optionally Tavily)
- More LLM calls = slower and more expensive than simple RAG
- Can still get stuck on truly unanswerable questions (but will fail gracefully)
- Local vector DB needs documents to be useful

## License

MIT
