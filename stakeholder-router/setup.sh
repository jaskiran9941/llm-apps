#!/bin/bash

# Stakeholder Router - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🎯 Stakeholder Router - Setup Script"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi
echo "✅ Python version OK: $python_version"
echo ""

# Create virtual environment
echo "🔨 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Setup .env file
echo "🔐 Setting up environment file..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping creation."
    echo "   Please ensure ANTHROPIC_API_KEY is set."
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "⚠️  IMPORTANT: Please edit .env and add your ANTHROPIC_API_KEY"
fi
echo ""

# Run tests
echo "🧪 Running tests..."
if pytest tests/ -v --tb=short; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed (this is OK if API key not configured yet)"
fi
echo ""

echo "===================================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the app: streamlit run app.py"
echo ""
echo "For more information, see QUICKSTART.md"
