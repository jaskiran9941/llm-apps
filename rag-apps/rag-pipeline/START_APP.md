# Starting the RAG Application

## ⚠️ Important Note about Python 3.14

Your system has Python 3.14, which is very new. Some dependencies (ChromaDB, pydantic-core) aren't fully compatible yet.

## Recommended Solution

### Option 1: Use Python 3.11 or 3.12 (Recommended)

```bash
# Install Python 3.11 or 3.12 using Homebrew
brew install python@3.11

# Create venv with specific Python version
python3.11 -m venv venv

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install streamlit openai python-dotenv PyPDF2 pdfplumber tiktoken tenacity chromadb

# Add your API key to .env
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the app
streamlit run ui/app.py
```

### Option 2: Use Docker

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "ui/app.py", "--server.address=0.0.0.0"]
EOF

# Build and run
docker build -t rag-system .
docker run -p 8501:8501 -v $(pwd)/data:/app/data rag-system
```

### Option 3: Fix Current Setup (if you must use Python 3.14)

Some packages might work with specific versions:

```bash
source venv/bin/activate

# Install core packages first
pip install streamlit openai python-dotenv PyPDF2 pdfplumber tiktoken tenacity

# Try installing an older ChromaDB version
pip install chromadb==0.4.22

# If that fails, create a mock ChromaDB wrapper for now
```

## Once Installation Works

1. **Add your API key**:
   ```bash
   echo "OPENAI_API_KEY=sk-your-actual-key" > .env
   ```

2. **Run the app**:
   ```bash
   streamlit run ui/app.py
   ```

3. **Open browser**: http://localhost:8501

## What You'll See

- **Tab 1: Upload Documents** - Upload PDFs
- **Tab 2: Query Interface** - Ask questions
- **Tab 3: Experiments** - Try different parameters
- **Tab 4: Documentation** - Learn about RAG

## Next Steps After Setup

1. Upload a small PDF (5-10 pages)
2. Wait for indexing to complete
3. Ask a question about the document
4. See the answer with citations and retrieved chunks!

## Need Help?

Check:
- README.md - Full documentation
- QUICKSTART.md - Setup guide
- docs/rag_concepts.md - Understanding RAG
- .env file - Make sure API key is set

The system is fully implemented and ready to run once the Python version compatibility is resolved!
