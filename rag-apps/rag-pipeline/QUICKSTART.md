# Quick Start Guide

Get your RAG system up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Navigate to project directory
cd /Users/jaskisingh/Desktop/RAG

# Run setup script
./setup.sh

# Edit .env file and add your API key
nano .env  # or use your preferred editor

# Run the app
streamlit run ui/app.py
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads data/chroma_db data/cache

# Configure API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# Run the app
streamlit run ui/app.py
```

## First Steps

1. **Open your browser** - The app will automatically open at http://localhost:8501

2. **Upload a document**:
   - Go to "Upload Documents" tab
   - Click "Choose PDF files"
   - Select a PDF from your computer
   - Click "Upload and Index"
   - Wait for processing to complete

3. **Ask a question**:
   - Go to "Query Interface" tab
   - Type a question about your document
   - Click "Ask with RAG"
   - View the answer and retrieved chunks

4. **Experiment**:
   - Try "Compare Both" to see RAG vs non-RAG
   - Adjust parameters in the sidebar
   - Explore the "Experiments" and "Documentation" tabs

## Example Workflow

```
1. Upload: research_paper.pdf
   → System creates ~42 chunks
   → Cost: ~$0.004

2. Ask: "What are the main findings?"
   → Retrieves 5 relevant chunks
   → Generates answer with citations
   → Cost: ~$0.02

3. Compare: RAG vs non-RAG
   → See how context improves answers
   → Understand when RAG is necessary

4. Experiment: Adjust chunk size
   → Try 300, 500, 700 character chunks
   → Compare retrieval quality
```

## Troubleshooting

### API Key Issues

If you see "Configuration Error: OPENAI_API_KEY not set":

```bash
# Check .env file exists
ls -la .env

# Verify API key is set
cat .env | grep OPENAI_API_KEY

# Make sure there are no quotes around the key
# Good: OPENAI_API_KEY=sk-...
# Bad:  OPENAI_API_KEY="sk-..."
```

### Import Errors

If you see "ModuleNotFoundError":

```bash
# Verify virtual environment is activated
which python  # Should show path to venv/bin/python

# If not activated:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

If port 8501 is busy:

```bash
# Run on different port
streamlit run ui/app.py --server.port 8502
```

### PDF Loading Fails

Some PDFs are encrypted or have complex layouts. Try:
- A different PDF
- Using a simpler/text-based PDF
- Check error message for details

## What to Try

### For Learning:

1. **Read the Documentation tab** in the app
2. **Experiment with parameters** - see their effects
3. **Compare RAG vs non-RAG** on different questions
4. **Read the code** - it's heavily commented
5. **Check `docs/rag_concepts.md`** for deep dives

### For Testing:

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src

# Run specific test
pytest tests/test_document_processing.py -v
```

### For Development:

1. Modify chunk size in sidebar
2. Try different similarity thresholds
3. Adjust temperature for generation
4. Experiment with top-k values

## Cost Management

**Initial testing** (recommended):
- Upload 1-2 small PDFs (5-10 pages)
- Ask 5-10 questions
- Total cost: ~$0.10-0.20

**Monitor costs**:
- Check cost displayed after each operation
- Use the Cost Calculator in sidebar
- Set a budget in your OpenAI account

**Typical costs**:
- Small document indexing: $0.001-0.005
- Single query: $0.01-0.03
- Daily usage (50 queries): ~$1-2

## Next Steps

1. **Upload your own documents** - Try PDFs relevant to your domain
2. **Experiment with parameters** - Find optimal settings
3. **Compare strategies** - RAG vs non-RAG, different chunk sizes
4. **Read the architecture** - `docs/architecture.md`
5. **Explore the code** - Start with `src/pipeline/`
6. **Plan enhancements** - This is Project 1, Projects 2-4 add advanced features

## Getting Help

1. Check the **Documentation tab** in the app
2. Read **docs/rag_concepts.md** for RAG fundamentals
3. Review **docs/architecture.md** for system design
4. Look at **test files** for usage examples
5. Check error messages carefully - they're descriptive

## Key Files

- `ui/app.py` - Main Streamlit app
- `src/pipeline/query_pipeline.py` - Query execution flow
- `src/pipeline/indexing_pipeline.py` - Document indexing flow
- `config/settings.py` - Configuration parameters
- `config/prompts.py` - RAG prompt templates

## Pro Tips

1. **Start with defaults** - They're tuned for most use cases
2. **Use the sidebar** - All key parameters are there
3. **Check retrieved chunks** - See what context was used
4. **Compare modes** - RAG vs non-RAG shows the value
5. **Monitor costs** - Displayed after each operation
6. **Read the code** - Educational comments throughout

## Success Checklist

- ✅ Setup completed successfully
- ✅ App opens in browser
- ✅ Can upload a PDF
- ✅ Document gets indexed (chunks created)
- ✅ Can ask a question
- ✅ Get an answer with citations
- ✅ See retrieved chunks and scores
- ✅ Can compare RAG vs non-RAG

If all checked, you're ready to explore! 🚀

## Common Questions

**Q: How much will this cost?**
A: Minimal for learning. ~$0.01-0.05 per document, ~$0.01-0.03 per query. Set a budget in OpenAI.

**Q: Can I use local models instead of OpenAI?**
A: Yes! The architecture supports this. You'd need to implement `BaseEmbeddingManager` and `LLMManager` for local models. (Future enhancement)

**Q: How many documents can I index?**
A: With ChromaDB local storage, 1000s of documents, 100,000s of chunks. For more, use cloud vector DBs.

**Q: Is my data private?**
A: Data stays local in ChromaDB. Only queries go to OpenAI for embeddings/generation. Don't upload sensitive docs if concerned.

**Q: Can I deploy this?**
A: Yes! Dockerize it and deploy to cloud (AWS, GCP, etc.). See architecture.md for deployment notes.

Happy learning! 📚
