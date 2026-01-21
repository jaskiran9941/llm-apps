# LLM Memory Chat

A production-ready chatbot demonstrating how memory transforms LLM capabilities through episodic (conversation history) and semantic (knowledge retrieval) memory.

## Features

- **Side-by-Side Comparison**: See WITH vs WITHOUT memory in real-time
- **Episodic Memory**: Maintains conversation history and context
- **Semantic Memory**: RAG (Retrieval Augmented Generation) with document search
- **Flexible Embeddings**: Choose from 6 embedding providers (HuggingFace, OpenAI, Cohere, Voyage, FastEmbed, Ollama)
- **Multiple Versions**: Simple production app, flexible provider app, and Mem0 integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_key_here
```

Get your key from: https://console.anthropic.com/

### 3. Run the App

**Option A: Simple Production App**
```bash
streamlit run app_production.py
```

**Option B: Flexible Embedding Providers**
```bash
streamlit run app_flexible.py
```

**Option C: With Mem0 (Advanced)**
```bash
pip install mem0ai
streamlit run app_mem0.py
```

### 4. Use the App

1. Click "Load Documents" in sidebar
2. Enter your API key (or add to `.env`)
3. Start chatting!

## How It Works

### Episodic Memory
- Stores last N conversation turns
- Provides context from earlier in conversation
- Enables natural, flowing dialogue

### Semantic Memory (RAG)
1. Documents split into chunks (500 tokens each)
2. Chunks embedded into vectors (384 dimensions)
3. User query embedded to same vector space
4. Similar chunks retrieved via cosine similarity
5. Retrieved chunks added to LLM prompt as context

## Embedding Provider Options

| Provider | Type | Cost | Speed | Quality |
|----------|------|------|-------|---------|
| HuggingFace | Local | Free | Medium | Good |
| FastEmbed | Local | Free | Fast | Good |
| Ollama | Local | Free | Fast | Very Good |
| OpenAI | API | $0.02/1M | Fast | Excellent |
| Cohere | API | $0.10/1M | Fast | Excellent |
| Voyage | API | $0.13/1M | Fast | Best for RAG |

**Recommendation**: Start with HuggingFace (default, free). Upgrade to OpenAI or Voyage for production.

## Project Structure

```
llm-memory/
├── app_production.py           # Simple production app
├── app_flexible.py             # Multiple embedding providers
├── app_mem0.py                 # Using Mem0 library
├── config/
│   └── config.py               # Configuration
├── llm/
│   └── claude_wrapper.py       # Claude API integration
├── memory/
│   ├── episodic.py             # Conversation history
│   ├── semantic_simple.py      # Simple RAG implementation
│   └── embeddings.py           # Multi-provider embeddings
├── knowledge_base/
│   └── sample_docs/            # Sample documents (4 policy files)
└── requirements.txt
```

## Configuration

Adjust settings in sidebar or `config/config.py`:

- **Conversation History**: 3-20 turns (default: 10)
- **Documents to Retrieve**: 1-10 (default: 3)
- **Similarity Threshold**: 0.0-1.0 (default: 0.7)
- **Temperature**: 0.0-1.0 (default: 0.7)

## Adding Your Own Documents

1. Place `.txt` files in `knowledge_base/sample_docs/`
2. Click "Load Documents" in the app
3. Documents will be indexed and searchable

## Sample Questions to Try

- "How many vacation days do I get?"
- "Can I work remotely?"
- "What's the parental leave policy?"
- "What can I expense for meals?"
- "Can I carry over vacation days?"

## Troubleshooting

**API Key Error**
- Make sure `.env` file exists with valid key
- Or enter key directly in sidebar

**No Documents Loaded**
- Click "Load Documents" button in sidebar
- Wait ~10 seconds for indexing

**Slow Performance**
- Switch to FastEmbed provider
- Reduce "Documents to Retrieve" setting
- Use Haiku model (default)

## Advanced: Using Mem0

Mem0 provides automated memory management:

```bash
pip install mem0ai
streamlit run app_mem0.py
```

Features:
- Automatic memory extraction
- Long-term memory across sessions
- User-specific memory isolation
- Memory search and management

## Documentation

- `PRODUCTION_GUIDE.md` - Detailed production deployment guide
- `EMBEDDING_COMPARISON.md` - Comprehensive embedding provider comparison
- `USAGE_GUIDE.md` - Detailed feature documentation

## Requirements

- Python 3.8+
- Anthropic API key
- Optional: OpenAI/Cohere/Voyage API keys for alternative embeddings

## License

MIT

## Contributing

Issues and pull requests welcome!
