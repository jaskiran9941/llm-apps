# Quick Start Guide

Get up and running with Conversational RAG in 5 minutes.

## Step 1: Install Dependencies

```bash
cd conversational-rag
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

## Step 3: Verify Installation

```bash
python3 verify_installation.py
```

You should see all green checkmarks ✓

## Step 4: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Step 5: Try It Out

1. **Upload a PDF**: Click "Browse files" in the sidebar
2. **Process**: Click "Process Document" button
3. **Chat**: Start asking questions!

### Example Conversation

```
You: What is this document about?
Bot: [Answers based on the document]

You: Tell me more about that
Bot: [Provides additional details]

You: What else does it mention?
Bot: [Continues with more information]
```

## Tips

- **Chunk Size**: Larger (512-1024) = more context, fewer chunks
- **Top K**: More results (5-10) = better context but slower
- **Alpha**: 0.5 (balanced), 1.0 (semantic only), 0.0 (keyword only)

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure you created `.env` file (not `.env.example`)
- Add your API key: `OPENAI_API_KEY=sk-...`

### "No text could be extracted"
- Try a different PDF
- Make sure it's not a scanned image (needs OCR)

### Import errors
- Run: `pip install -r requirements.txt`

### ChromaDB errors
- Delete `data/chroma_conversational/` folder
- Restart the app

## What's Next?

- Try different chunk sizes and retrieval settings
- Experiment with follow-up questions
- Check the sources to see what chunks were retrieved
- Clear conversation and start fresh with new questions

## Need Help?

Check the full README.md for detailed documentation.
