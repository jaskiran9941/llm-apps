# RAG Approaches Comparison

A comprehensive side-by-side comparison of three different RAG (Retrieval-Augmented Generation) approaches: Traditional RAG, Corrective RAG (CRAG), and Agentic RAG.

## 🎯 Overview

This project demonstrates the evolution of RAG systems through three distinct implementations:

1. **Traditional RAG**: Simple retrieve-then-generate
2. **Corrective RAG (CRAG)**: Adds relevance grading and corrective actions
3. **Agentic RAG**: Full autonomous reasoning with multi-iteration refinement

## 🔥 Key Features

- **Side-by-side comparison** in a single Streamlit UI
- **Python 3.14 compatible** (solved pydantic/langchain compatibility issues)
- **Three complete implementations** ready to use
- **FAISS vector store** (lightweight, no external dependencies)
- **Custom document loaders** (no problematic langchain loaders)
- **Detailed reasoning traces** for each approach
- **Performance metrics** (LLM calls, time, cost)

## 📊 Comparison at a Glance

| Approach | Speed | Quality | LLM Calls | Retrievals | Cost/Query |
|----------|-------|---------|-----------|------------|------------|
| Traditional | ⚡⚡⚡ | ⭐⭐ | 1 | 1 | $0.001 |
| Corrective | ⚡⚡ | ⭐⭐⭐ | 2-4 | 1-2 | $0.003 |
| Agentic | ⚡ | ⭐⭐⭐⭐ | 3-7+ | 1-3 | $0.010 |

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run the app
streamlit run app_comparison.py
```

Open your browser at **http://localhost:8501**

## 📁 Project Structure

```
rag-comparison/
├── app_comparison.py          # Main Streamlit UI
├── traditional_rag.py         # Traditional RAG
├── corrective_rag.py          # Corrective RAG
├── agent.py                   # Agentic RAG
├── tools.py                   # Retrieval tools
├── config.py                  # Configuration
├── documents/                 # Your documents
└── README.md                  # This file
```

## 🎓 How Each Approach Works

### Traditional RAG
```
Question → Retrieve (1x) → Generate → Answer
```

### Corrective RAG
```
Question → Retrieve → Grade → [Correct if needed] → Generate → Answer
```

### Agentic RAG
```
Question → [ReAct Loop] → Generate → Answer
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture.

## 🔧 Configuration

Edit `config.py` to adjust parameters.

## 📚 Documentation

- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation

## 📄 License

MIT License
