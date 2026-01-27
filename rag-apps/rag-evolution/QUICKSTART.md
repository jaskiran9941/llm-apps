# 🚀 Quick Start Guide

Get started with RAG Evolution in 5 minutes!

## Step 1: Setup (2 minutes)

```bash
# Navigate to project directory
cd /Users/jaskisingh/Desktop/llm-apps/rag-apps/rag-evolution

# Run setup script
./setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -c "import nltk; nltk.download('punkt')"
```

## Step 2: Configure OpenAI API Key (30 seconds)

```bash
# Edit .env file
nano .env

# Add your OpenAI API key:
OPENAI_API_KEY=sk-your-key-here

# Save and exit (Ctrl+X, Y, Enter)
```

## Step 3: Run the App (30 seconds)

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run Streamlit
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step 4: Try Each Tab (2 minutes each)

### Tab 1: Baseline RAG
1. Upload any PDF document
2. Click "Process Document"
3. Ask a question
4. Notice the warnings about incomplete chunks and ignored images

### Tab 2: Smart Chunking
1. Upload the same PDF
2. Try different chunking strategies (Fixed, Sentence, Semantic)
3. Click "Process Document" for each
4. Compare the results - see 100% chunk completeness!

### Tab 3: Hybrid Retrieval
1. Upload a PDF with specific codes/terms (or use the same one)
2. Process the document
3. Select multiple strategies to compare
4. Ask a question with exact terms (like "SKU-12345")
5. See how Hybrid outperforms Semantic-only

### Tab 4: Vision RAG
1. Upload a PDF with images/charts (required!)
2. Enable "Vision RAG" checkbox
3. Process (this takes longer - GPT-4V describes each image)
4. Choose "Side-by-Side Comparison" mode
5. Ask about something in an image (e.g., "What's the revenue growth?")
6. See the dramatic difference!

## Sample Queries to Try

**For any document:**
- "What is the main topic of this document?"
- "Summarize the key points"
- "What are the recommendations?"

**For documents with specific terms:**
- "What is product SKU-XXX?"
- "Find information about [specific code]"

**For documents with charts/images (Tab 4 only):**
- "What does the chart show?"
- "What was the growth rate?"
- "Describe the diagram"

## Troubleshooting

**App won't start:**
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**"Module not found" errors:**
```bash
# Make sure you're running from project root
cd /Users/jaskisingh/Desktop/llm-apps/rag-apps/rag-evolution
streamlit run app.py
```

**"OpenAI API key not set":**
```bash
# Check .env file exists and has your key
cat .env
```

**ChromaDB errors:**
```bash
# Delete and recreate database
rm -rf data/chroma_multimodal
# Then restart the app
```

## Next Steps

1. **Read the full README.md** for detailed explanations
2. **Try your own documents** - see what works best
3. **Experiment with settings** - chunk sizes, strategies, etc.
4. **Check the cost** - estimate how much your queries cost

## Cost Awareness

**Typical costs during testing:**
- Processing 1 small PDF (10 pages, 5 images): ~$0.20
- Processing 1 large PDF (50 pages, 20 images): ~$0.70
- Each query: ~$0.01-0.03

**Total for learning session:** ~$2-5 (very affordable!)

## Learning Tips

1. **Start simple** - Use Tab 1 first to understand basics
2. **Progress sequentially** - Each tab builds on previous
3. **Use same document** - Compare results across tabs
4. **Read expandable sections** - Educational content in each tab
5. **Experiment** - Try different queries and documents

## Getting Help

If you get stuck:
1. Check the expandable "Learn" sections in each tab
2. Read the full README.md
3. Check the code - it's well-commented!

---

**You're ready to go! Have fun learning RAG! 🎓**
