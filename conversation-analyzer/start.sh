#!/bin/bash

# Conversation Analyzer - Start Script

# Change to script directory
cd "$(dirname "$0")"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Copy .env.example to .env and add your API keys:"
    echo "  cp .env.example .env"
    echo ""
fi

# Run the Streamlit app
echo "Starting Conversation Analyzer..."
echo "Open http://localhost:8501 in your browser"
echo ""
streamlit run app.py --server.port 8501
