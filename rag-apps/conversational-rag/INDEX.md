# 📖 Conversational RAG - Complete Index

Quick reference guide to all files and their purposes.

## 🚀 Getting Started

1. **First Time Users** → `QUICKSTART.md`
2. **Want Full Details** → `README.md`
3. **Presenting/Demoing** → `DEMO.md`
4. **Technical Deep Dive** → `IMPLEMENTATION_SUMMARY.md`
5. **Check Status** → `PROJECT_STATUS.md`

## 📁 File Directory

### 🎯 Main Application

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | 274 | Main Streamlit application with chat UI |

### 🧠 Core Source Code (`src/`)

#### Data Models
| File | Lines | Purpose |
|------|-------|---------|
| `src/models.py` | 89 | ConversationHistory, ConversationMessage, Chunk, RetrievalResult |

#### Document Processing
| File | Lines | Purpose |
|------|-------|---------|
| `src/document_processor.py` | 104 | PDF text extraction and semantic chunking |

#### Retrieval System (`src/retrieval/`)
| File | Lines | Purpose |
|------|-------|---------|
| `src/retrieval/vector_search.py` | 106 | Semantic search using ChromaDB + embeddings |
| `src/retrieval/bm25_search.py` | 81 | Keyword search using BM25 algorithm |
| `src/retrieval/hybrid_fusion.py` | 76 | Reciprocal Rank Fusion (RRF) for combining results |
| `src/retrieval/conversational_retriever.py` | 117 | **⭐ Query enhancement with conversation context** |

#### Generation System (`src/generation/`)
| File | Lines | Purpose |
|------|-------|---------|
| `src/generation/embedder.py` | 45 | OpenAI text embeddings (text-embedding-3-small) |
| `src/generation/conversational_generator.py` | 110 | **⭐ GPT-4 chat with conversation awareness** |

#### Utilities (`src/utils/`)
| File | Lines | Purpose |
|------|-------|---------|
| `src/utils/config.py` | 31 | Configuration management and environment variables |

### 📚 Documentation

| File | Lines | Purpose | Read When... |
|------|-------|---------|--------------|
| `README.md` | 203 | Comprehensive guide | You want full documentation |
| `QUICKSTART.md` | 47 | 5-minute setup guide | You want to get started fast |
| `DEMO.md` | 238 | Demo script & scenarios | You're presenting or demoing |
| `IMPLEMENTATION_SUMMARY.md` | 483 | Technical details | You're a developer/technical user |
| `PROJECT_STATUS.md` | 208 | Project completion status | You want to verify deliverables |
| `INDEX.md` | - | This file! | You need a quick reference |

### 🔧 Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (9 packages) |
| `.env.example` | Environment variable template |
| `.gitignore` | Git ignore rules |

### 🧪 Testing & Verification

| File | Lines | Purpose |
|------|-------|---------|
| `verify_installation.py` | 105 | Quick installation checker (recommended) |
| `test_setup.py` | 152 | Detailed setup tester with dependency checks |

### 💾 Data Directories

| Directory | Purpose |
|-----------|---------|
| `data/documents/` | Stores uploaded PDF files |
| `data/chroma_conversational/` | ChromaDB vector database storage |

## 🎓 Learning Path

### Beginner Path
1. `QUICKSTART.md` - Setup in 5 minutes
2. `README.md` (Features & Usage sections) - Understand what it does
3. Try the app with a sample PDF
4. `DEMO.md` (Example Conversation section) - See it in action

### Developer Path
1. `README.md` (Architecture section) - Understand the design
2. `IMPLEMENTATION_SUMMARY.md` - Technical decisions
3. `src/models.py` - Data structures
4. `src/retrieval/conversational_retriever.py` - Query enhancement logic
5. `src/generation/conversational_generator.py` - Answer generation
6. `app.py` - UI implementation

### Presenter Path
1. `PROJECT_STATUS.md` - Quick overview
2. `DEMO.md` - Full demo script
3. Practice with the app
4. `README.md` (Features section) - Key talking points

## 🔑 Key Concepts by File

### Conversation Management
- **Models**: `src/models.py` → ConversationHistory, ConversationMessage
- **UI**: `app.py` → Session state management
- **Generation**: `src/generation/conversational_generator.py` → History formatting

### Query Enhancement (Follow-up Questions)
- **Detection**: `src/retrieval/conversational_retriever.py` → `_is_followup_query()`
- **Enhancement**: `src/retrieval/conversational_retriever.py` → `_build_enhanced_query()`
- **Patterns**: "tell me more", "what else", "clarify", etc.

### Hybrid Retrieval
- **Semantic**: `src/retrieval/vector_search.py` → ChromaDB + embeddings
- **Keyword**: `src/retrieval/bm25_search.py` → BM25 algorithm
- **Fusion**: `src/retrieval/hybrid_fusion.py` → Reciprocal Rank Fusion

### Document Processing
- **PDF Extraction**: `src/document_processor.py` → PyPDF2
- **Chunking**: `src/document_processor.py` → SemanticChunker
- **Indexing**: `src/retrieval/vector_search.py` + `src/retrieval/bm25_search.py`

## 📊 Statistics

- **Total Files**: 23
- **Python Modules**: 13 (11 core + 2 tests)
- **Documentation**: 6 markdown files
- **Total Code**: ~777 lines
- **Total Documentation**: ~971 lines
- **Code-to-Docs Ratio**: 1:1.25 (well documented!)

## 🎯 Quick Commands

```bash
# Verify installation
python3 verify_installation.py

# Run the app
streamlit run app.py

# Check dependencies
pip list | grep -E "streamlit|openai|chromadb"

# View project structure
cat PROJECT_TREE.txt

# Count lines of code
find ./src -name "*.py" | xargs wc -l
```

## 🔍 Finding Things

### "How do I...?"

- **Set up the environment?** → `QUICKSTART.md` or `.env.example`
- **Understand the architecture?** → `README.md` (Architecture section)
- **Add a new feature?** → `IMPLEMENTATION_SUMMARY.md` (Future Enhancements)
- **Fix an error?** → `QUICKSTART.md` (Troubleshooting) or `README.md`
- **Present the project?** → `DEMO.md`
- **Understand query enhancement?** → `src/retrieval/conversational_retriever.py`
- **Modify the chat prompt?** → `src/generation/conversational_generator.py`
- **Change chunk size?** → `app.py` (sidebar settings) or `src/utils/config.py`

### "Where is...?"

- **The main logic?** → `app.py` (UI) + `src/` (core)
- **Follow-up detection?** → `src/retrieval/conversational_retriever.py:42`
- **Hybrid fusion?** → `src/retrieval/hybrid_fusion.py`
- **System prompt?** → `src/generation/conversational_generator.py:54`
- **Configuration?** → `src/utils/config.py` and `.env.example`
- **Dependencies?** → `requirements.txt`

## 🌟 Core Features by File

| Feature | Implementation | File |
|---------|---------------|------|
| Chat Interface | Streamlit chat components | `app.py:147-190` |
| Conversation History | ConversationHistory model | `src/models.py:46-73` |
| Follow-up Detection | Pattern matching | `src/retrieval/conversational_retriever.py:42-65` |
| Query Enhancement | Context extraction | `src/retrieval/conversational_retriever.py:67-96` |
| Hybrid Retrieval | RRF fusion | `src/retrieval/hybrid_fusion.py:18-76` |
| Answer Generation | GPT-4 + history | `src/generation/conversational_generator.py:17-72` |
| Source Citation | Expandable UI | `app.py:157-164` |
| PDF Processing | PyPDF2 + chunking | `src/document_processor.py:51-108` |

## 🎨 Architecture Overview

```
User Question
    ↓
[Query Enhancement] ← Conversation History
    ↓
[Hybrid Retrieval]
    ├─→ [Semantic Search] (embeddings)
    └─→ [Keyword Search] (BM25)
    ↓
[RRF Fusion]
    ↓
[Top-K Results]
    ↓
[Answer Generation] ← Conversation History
    ↓
Response + Sources
```

Files involved:
1. `src/retrieval/conversational_retriever.py` - Query enhancement
2. `src/retrieval/vector_search.py` - Semantic search
3. `src/retrieval/bm25_search.py` - Keyword search
4. `src/retrieval/hybrid_fusion.py` - RRF fusion
5. `src/generation/conversational_generator.py` - Answer generation
6. `app.py` - UI and orchestration

## 📞 Support Resources

- **Installation Issues**: `verify_installation.py` → `QUICKSTART.md` (Troubleshooting)
- **Usage Questions**: `README.md` (Usage section) → `DEMO.md`
- **Technical Questions**: `IMPLEMENTATION_SUMMARY.md`
- **Feature Requests**: `IMPLEMENTATION_SUMMARY.md` (Future Enhancements)

---

**Last Updated**: January 27, 2026
**Version**: 1.0
**Status**: Complete ✅
