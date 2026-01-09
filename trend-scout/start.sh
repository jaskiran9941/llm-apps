#!/bin/bash
# Start Trend Scout Streamlit app

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check for .env
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copy .env.example to .env and fill in your API keys."
    cp .env.example .env
fi

# Run streamlit
streamlit run app.py
