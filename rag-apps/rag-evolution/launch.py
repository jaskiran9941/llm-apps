#!/usr/bin/env python3
"""
Launch script for RAG Evolution app
Checks for API key before starting
"""
import os
import sys
from pathlib import Path

# Check for .env file
env_file = Path(".env")
if not env_file.exists():
    print("❌ .env file not found!")
    print("Run: cp .env.example .env")
    print("Then add your OPENAI_API_KEY to .env")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check for API key
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key or api_key == "your_openai_api_key_here":
    print("⚠️  WARNING: OpenAI API key not set!")
    print("")
    print("The app will launch, but you need to add your API key to use it.")
    print("")
    print("To fix:")
    print("1. Edit .env file")
    print("2. Replace 'your_openai_api_key_here' with your actual OpenAI API key")
    print("3. Get your key from: https://platform.openai.com/api-keys")
    print("")
    print("Press Enter to continue anyway (app will show errors without key)...")
    print("Or press Ctrl+C to exit and add your key first.")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nExiting. Add your API key to .env and try again!")
        sys.exit(0)
else:
    print("✓ OpenAI API key found!")
    print("✓ Launching RAG Evolution Showcase...")
    print("")

# Launch Streamlit
os.system("streamlit run app.py")
