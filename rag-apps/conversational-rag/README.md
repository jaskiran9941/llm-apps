# 🗣️ Conversational RAG

A production-ready conversational RAG (Retrieval-Augmented Generation) application that enables natural multi-turn conversations with your documents. Built with Streamlit, OpenAI, and ChromaDB.

## ✨ Features

- **Multi-turn Conversations**: Full conversation history support with context-aware responses
- **Follow-up Question Handling**: Automatically understands references like "tell me more", "what else?", "clarify that"
- **Hybrid Retrieval**: Combines semantic search (embeddings) with keyword search (BM25) using Reciprocal Rank Fusion
- **Interactive UI**: Clean Streamlit interface with expandable source citations
- **Configurable**: Adjustable chunk size, retrieval settings, and model selection

## 🏗️ Architecture

### Core Components

1. **Document Processing**
   - PDF text extraction with PyPDF2
   - Semantic chunking with configurable size and overlap
   - Page-aware metadata preservation

2. **Conversational Retrieval**
   - Query enhancement using conversation history
   - Follow-up pattern detection (rule-based)
   - Hybrid retrieval (semantic + keyword)
   - Reciprocal Rank Fusion (RRF) for result merging

3. **Answer Generation**
   - GPT-4 with conversation-aware system prompt
   - Source citation in responses
   - Context grounding to prevent hallucination

### How It Works

```
User Query
    ↓
Query Enhancement (if follow-up detected)
    ↓
Hybrid Retrieval
    ├─→ Semantic Search (embeddings)
    └─→ Keyword Search (BM25)
    ↓
Reciprocal Rank Fusion
    ↓
Top-K Results
    ↓
Answer Generation (with conversation history)
    ↓
Response + Sources
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
cd conversational-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-...
```

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Application

1. **Upload a PDF**: Click "Browse files" in the sidebar
2. **Adjust Settings** (optional):
   - Chunk size (256-1024)
   - Chunk overlap (0-200)
   - Number of retrieval results (3-10)
   - Semantic vs keyword balance (0.0-1.0)
3. **Process Document**: Click "Process Document"
4. **Start Chatting**: Ask questions in the chat input

### Example Conversation

```
User: What is this document about?
Assistant: This document discusses [topic]...

User: Tell me more about that
Assistant: [Provides additional details from the document]...

User: What else does it mention?
Assistant: [Continues with more information]...
```

## 🎯 Key Features Explained

### 1. Follow-up Question Detection

The system automatically detects follow-up patterns:
- "tell me more", "what else", "elaborate"
- "clarify that", "explain that"
- "continue", "go on", "anything else"
- Short queries with context words ("what about", "how so")

### 2. Query Enhancement

When a follow-up is detected:
```python
Original: "tell me more"
Enhanced: "Previous question: What is RAG? Current question: tell me more"
```

This ensures retrieval finds relevant chunks even for vague follow-ups.

### 3. Hybrid Retrieval

**Semantic Search**: Finds chunks similar in meaning using embeddings
**Keyword Search**: Finds chunks with exact term matches using BM25
**Fusion**: Combines both using Reciprocal Rank Fusion (RRF)

Benefits:
- Semantic handles conceptual queries
- Keyword handles specific terms
- Fusion provides best of both worlds

### 4. Conversation Memory

Full conversation history is:
- Stored in session state
- Displayed in chat interface
- Passed to LLM for context-aware generation
- Used for query enhancement

## 📁 Project Structure

```
conversational-rag/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── README.md                       # This file
├── src/
│   ├── __init__.py
│   ├── models.py                   # Data models
│   ├── document_processor.py      # PDF processing & chunking
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_search.py       # Semantic search
│   │   ├── bm25_search.py         # Keyword search
│   │   ├── hybrid_fusion.py       # RRF fusion
│   │   └── conversational_retriever.py  # Query enhancement
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── embedder.py            # Text embeddings
│   │   └── conversational_generator.py  # Chat generation
│   └── utils/
│       ├── __init__.py
│       └── config.py              # Configuration
└── data/
    ├── documents/                 # Uploaded PDFs
    └── chroma_conversational/     # Vector DB
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
OPENAI_API_KEY=your-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
```

### UI Settings

All settings are adjustable in the Streamlit sidebar:

- **Chunk Size**: Larger = more context per chunk, fewer chunks
- **Chunk Overlap**: Higher = more redundancy, smoother retrieval
- **Top K**: More chunks = more context for LLM, higher cost
- **Alpha (0-1)**: 0=keyword only, 1=semantic only, 0.5=balanced
- **Model**: gpt-4 (best quality) vs gpt-3.5-turbo (faster, cheaper)

## 📊 How Hybrid Retrieval Works

### Reciprocal Rank Fusion (RRF)

```python
# For each chunk in semantic results
score += alpha / (60 + rank)

# For each chunk in keyword results
score += (1 - alpha) / (60 + rank)

# Sort by combined score
```

Benefits:
- Rank-based (handles different score scales)
- Combines evidence from both methods
- Configurable via alpha parameter

## 🧪 Testing

### Manual Testing

1. Upload a sample PDF (e.g., research paper, documentation)
2. Test basic questions:
   - "What is this document about?"
   - "Summarize the main points"
3. Test follow-ups:
   - "Tell me more about that"
   - "What else does it mention?"
   - "Clarify the last point"
4. Verify:
   - Answers are grounded in the document
   - Follow-ups understand context
   - Sources are displayed correctly
   - Conversation persists properly

### Clear Conversation

Click "🗑️ Clear Conversation" to reset and start fresh.

## 🎓 Technical Details

### Models Used

- **Embeddings**: `text-embedding-3-small` (1536 dimensions)
- **Chat**: `gpt-4` (default), `gpt-4-turbo`, or `gpt-3.5-turbo`

### Vector Database

- **ChromaDB**: Local persistent vector store
- **Similarity**: Cosine similarity for semantic search
- **Storage**: `data/chroma_conversational/`

### Chunking Strategy

- **Approach**: Sentence-boundary semantic chunking
- **Size**: 512 tokens (default)
- **Overlap**: 50 tokens (default)
- **Metadata**: Page numbers, chunk size

## 🚧 Limitations

- Single document at a time (no multi-document support)
- Session-based only (no persistent conversation storage)
- Simple rule-based query enhancement (no LLM-based enhancement)
- Text-only (no image/table extraction)

## 🔮 Future Enhancements

- Multi-document support
- Conversation export (markdown/JSON)
- LLM-based query enhancement
- Advanced reranking
- Conversation summarization for long chats
- Persistent conversation storage
- Vision RAG integration

## 📝 License

MIT License - feel free to use for educational or commercial purposes.

## 🤝 Contributing

This is an educational project. Feel free to fork and extend!

## 📚 References

- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
