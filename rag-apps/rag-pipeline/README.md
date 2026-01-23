# RAG Learning System - Project 1

A comprehensive, educational RAG (Retrieval-Augmented Generation) system built with Python, OpenAI, ChromaDB, and Streamlit. This project serves as a foundation for learning RAG fundamentals and as a base for more advanced RAG techniques in future projects.

## 🎯 Project Overview

This system demonstrates the complete RAG pipeline:
- **Document Processing**: Load PDFs, chunk text intelligently
- **Embedding Generation**: Convert text to vector representations
- **Vector Storage**: Store and search embeddings efficiently
- **Semantic Retrieval**: Find relevant context using similarity search
- **Answer Generation**: Use LLMs with retrieved context

## ✨ Features

- 📤 **Document Upload & Indexing**: Upload PDF files and automatically index them
- 🔍 **Intelligent Query System**: Ask questions and get contextual answers
- ⚖️ **RAG vs Non-RAG Comparison**: See the difference between context-based and general knowledge answers
- 📊 **Cost Tracking**: Monitor token usage and API costs
- 🎛️ **Parameter Experimentation**: Adjust chunk size, top-k, temperature, and more
- 📚 **Educational Content**: Learn RAG concepts through the UI
- 🧪 **Experiments Tab**: Explore how parameters affect performance

## 🏗️ Architecture

```
├── config/              # Configuration and prompts
├── src/
│   ├── document_processing/  # PDF loading, chunking, preprocessing
│   ├── embeddings/           # Embedding generation (OpenAI)
│   ├── vector_store/         # Vector storage (ChromaDB)
│   ├── retrieval/            # Semantic retrieval
│   ├── generation/           # LLM generation
│   ├── pipeline/             # End-to-end pipelines
│   └── utils/                # Utilities (metrics, logging, validation)
├── ui/                  # Streamlit interface
├── tests/               # Unit and integration tests
└── docs/                # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone or navigate to the project directory**

```bash
cd /Users/jaskisingh/Desktop/RAG
```

2. **Run the setup script**

```bash
chmod +x setup.sh
./setup.sh
```

3. **Configure your API key**

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

4. **Run the application**

```bash
streamlit run ui/app.py
```

The app will open in your browser at `http://localhost:8501`

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads data/chroma_db data/cache

# Copy and edit .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the app
streamlit run ui/app.py
```

## 📖 Usage Guide

### 1. Upload Documents

1. Navigate to the "Upload Documents" tab
2. Click "Choose PDF files" and select one or more PDFs
3. Click "Upload and Index"
4. Wait for processing to complete
5. View indexing statistics (chunks created, cost, time)

### 2. Ask Questions

1. Go to the "Query Interface" tab
2. Enter your question in the text area
3. Choose an option:
   - **Ask with RAG**: Get answer based on your documents
   - **Ask without RAG**: Get answer from model's general knowledge
   - **Compare Both**: See both answers side-by-side
4. View the answer, retrieved chunks, and metadata

### 3. Experiment

1. Visit the "Experiments" tab
2. Try different chunk sizes and see their impact
3. Compare RAG vs non-RAG for different types of questions
4. Use the sidebar to adjust parameters and see effects

## 🎓 Learning Path

This project is designed for learning. Here's a suggested path:

1. **Start Simple**: Upload a small PDF, ask basic questions
2. **Explore Parameters**: Adjust chunk size, top-k, temperature
3. **Compare Approaches**: Run RAG vs non-RAG comparisons
4. **Read the Code**: All code includes educational comments
5. **Read Documentation**: Check `docs/rag_concepts.md` for deep dives
6. **Run Tests**: Execute tests to understand components
7. **Experiment**: Try different documents and queries

## 💰 Cost Estimates

**Indexing (one-time per document):**
- Small PDF (10 pages): ~$0.001
- Medium PDF (50 pages): ~$0.005
- Large PDF (200 pages): ~$0.02

**Querying (per question):**
- Simple query (top-5): ~$0.01-0.02
- Complex query (top-10): ~$0.02-0.04

**Monthly estimate (example):**
- 50 documents (avg 30 pages): ~$0.10 indexing
- 100 queries/day: ~$30-60/month

*Costs vary based on document size and query complexity*

## 🔧 Configuration

Key parameters (adjust in sidebar or `.env`):

- **Chunk Size**: 200-2000 characters (default: 500)
- **Chunk Overlap**: 0-500 characters (default: 50)
- **Top-K**: 1-20 chunks (default: 5)
- **Temperature**: 0-2 (default: 0.7)
- **Max Tokens**: 100-2000 (default: 1000)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_document_processing.py -v
```

## 📚 Project Structure Details

### Core Components

- **Models** (`src/models.py`): Pydantic data models for type safety
- **Configuration** (`config/`): Centralized settings and prompts
- **Document Processing** (`src/document_processing/`):
  - `pdf_loader.py`: PDF text extraction
  - `chunker.py`: Text chunking strategies
  - `preprocessor.py`: Text cleaning and normalization
- **Embeddings** (`src/embeddings/`): Vector embedding generation
- **Vector Store** (`src/vector_store/`): ChromaDB integration
- **Retrieval** (`src/retrieval/`): Semantic search
- **Generation** (`src/generation/`): LLM-based answer generation
- **Pipelines** (`src/pipeline/`): End-to-end orchestration
- **UI** (`ui/`): Streamlit interface

### Design Patterns

- **Strategy Pattern**: Swappable chunkers, retrievers, generators
- **Dependency Injection**: Components injected into pipelines
- **Abstract Base Classes**: Enable extensibility for future projects

## 🚧 Future Enhancements (Projects 2-4)

This is Project 1. Future projects will add:

- **Project 2**: Advanced chunking (semantic, recursive)
- **Project 3**: Hybrid retrieval (BM25 + semantic), reranking
- **Project 4**: Context enhancement (parent-child chunks, query rewriting)

## 🐛 Troubleshooting

**API Key Error:**
- Make sure `.env` file exists and contains valid `OPENAI_API_KEY`

**Import Errors:**
- Verify virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**PDF Loading Fails:**
- Some PDFs are encrypted or corrupted
- Try a different PDF or check the error message

**No Chunks Retrieved:**
- Ensure documents are indexed (check "Upload Documents" tab)
- Lower the minimum similarity score
- Try rephrasing your question

**High Costs:**
- Reduce chunk size or top-k
- Use fewer queries
- Consider caching common questions

## 📄 License

This is an educational project. Use freely for learning purposes.

## 🙏 Acknowledgments

Built with:
- [OpenAI](https://openai.com/) for embeddings and LLM
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Streamlit](https://streamlit.io/) for the UI
- [LangChain](https://langchain.com/) concepts (implemented from scratch)

## 📧 Support

For issues or questions:
1. Check the "Documentation" tab in the app
2. Review `docs/rag_concepts.md` for deep dives
3. Run tests to verify setup
4. Check error messages carefully

## 🎯 Success Criteria

You'll know the system is working when you can:
- ✅ Upload a PDF and see it indexed
- ✅ Ask questions and get contextual answers with citations
- ✅ See which chunks were retrieved and their relevance scores
- ✅ Compare RAG vs non-RAG responses
- ✅ Experiment with different parameters and observe effects
- ✅ Understand the cost implications of your queries

Happy learning! 🚀
