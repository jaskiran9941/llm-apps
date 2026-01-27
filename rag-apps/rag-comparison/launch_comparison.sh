#!/bin/bash
# Launch script for RAG Comparison UI

echo "================================================"
echo "  RAG Comparison: Traditional vs CRAG vs Agentic"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create .env with: OPENAI_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Check if documents directory exists
if [ ! -d documents ]; then
    echo "📁 Creating documents directory..."
    mkdir -p documents
    echo "⚠️  Please add PDF or TXT files to ./documents/ directory"
    echo ""
fi

# Check if documents exist
if [ -z "$(ls -A documents 2>/dev/null)" ]; then
    echo "⚠️  Warning: No documents found in ./documents/"
    echo "The system will work but you should add documents for better testing"
    echo ""
fi

echo "🚀 Launching Streamlit comparison UI..."
echo ""
streamlit run app_comparison.py
