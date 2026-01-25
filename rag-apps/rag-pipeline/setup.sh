#!/bin/bash

# RAG System Setup Script

echo "Setting up RAG Learning System..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/uploads
mkdir -p data/chroma_db
mkdir -p data/cache

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env with your OpenAI API key!"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "Setup complete! Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the app: streamlit run ui/app.py"
echo ""
