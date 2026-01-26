#!/bin/bash

# RAG Evolution Setup Script

echo "🚀 Setting up RAG Evolution Showcase..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "📥 Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True)"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/sample_docs data/images data/chroma_multimodal

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the app: streamlit run app.py"
echo ""
echo "Happy learning! 🎓"
