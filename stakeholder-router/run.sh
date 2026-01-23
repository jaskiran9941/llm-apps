#!/bin/bash

# Stakeholder Router - Run Script
# Quick script to activate venv and run Streamlit

set -e

echo "🎯 Starting Stakeholder Router..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run ./setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copying from .env.example..."
    cp .env.example .env
    echo "   Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check for API key
if ! grep -q "ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not configured in .env"
    echo "   The app will start but won't work without an API key"
    echo ""
fi

# Run Streamlit
echo "🚀 Launching Streamlit app..."
echo "   Press Ctrl+C to stop"
echo ""

streamlit run app.py
