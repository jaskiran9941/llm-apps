"""
Quick setup test script
"""
import sys

def test_imports():
    """Test that all dependencies can be imported"""
    print("Testing imports...")

    try:
        import streamlit
        print("✓ streamlit")
    except ImportError as e:
        print(f"✗ streamlit: {e}")
        return False

    try:
        import openai
        print("✓ openai")
    except ImportError as e:
        print(f"✗ openai: {e}")
        return False

    try:
        import chromadb
        print("✓ chromadb")
    except ImportError as e:
        print(f"✗ chromadb: {e}")
        return False

    try:
        import PyPDF2
        print("✓ PyPDF2")
    except ImportError as e:
        print(f"✗ PyPDF2: {e}")
        return False

    try:
        from pydantic import BaseModel
        print("✓ pydantic")
    except ImportError as e:
        print(f"✗ pydantic: {e}")
        return False

    try:
        from rank_bm25 import BM25Okapi
        print("✓ rank-bm25")
    except ImportError as e:
        print(f"✗ rank-bm25: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False

    try:
        import nltk
        print("✓ nltk")
    except ImportError as e:
        print(f"✗ nltk: {e}")
        return False

    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False

    return True


def test_module_imports():
    """Test that custom modules can be imported"""
    print("\nTesting custom modules...")

    try:
        from src.models import ConversationHistory, ConversationMessage
        print("✓ src.models")
    except ImportError as e:
        print(f"✗ src.models: {e}")
        return False

    try:
        from src.document_processor import DocumentProcessor
        print("✓ src.document_processor")
    except ImportError as e:
        print(f"✗ src.document_processor: {e}")
        return False

    try:
        from src.retrieval.vector_search import VectorSearch
        print("✓ src.retrieval.vector_search")
    except ImportError as e:
        print(f"✗ src.retrieval.vector_search: {e}")
        return False

    try:
        from src.retrieval.bm25_search import BM25Searcher
        print("✓ src.retrieval.bm25_search")
    except ImportError as e:
        print(f"✗ src.retrieval.bm25_search: {e}")
        return False

    try:
        from src.retrieval.conversational_retriever import ConversationalRetriever
        print("✓ src.retrieval.conversational_retriever")
    except ImportError as e:
        print(f"✗ src.retrieval.conversational_retriever: {e}")
        return False

    try:
        from src.generation.conversational_generator import ConversationalGenerator
        print("✓ src.generation.conversational_generator")
    except ImportError as e:
        print(f"✗ src.generation.conversational_generator: {e}")
        return False

    try:
        from src.utils.config import Config
        print("✓ src.utils.config")
    except ImportError as e:
        print(f"✗ src.utils.config: {e}")
        return False

    return True


def test_env_file():
    """Check if .env file exists"""
    print("\nChecking environment...")
    import os
    from pathlib import Path

    env_path = Path(".env")
    if env_path.exists():
        print("✓ .env file exists")

        # Check for API key
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("✓ OPENAI_API_KEY is set")
            return True
        else:
            print("⚠ OPENAI_API_KEY not found in .env")
            print("  Please add your OpenAI API key to .env file")
            return False
    else:
        print("⚠ .env file not found")
        print("  Please copy .env.example to .env and add your API key")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Conversational RAG Setup Test")
    print("=" * 50)

    all_passed = True

    if not test_imports():
        all_passed = False
        print("\n❌ Some dependencies are missing. Run: pip install -r requirements.txt")

    if not test_module_imports():
        all_passed = False
        print("\n❌ Some custom modules failed to import")

    env_ok = test_env_file()

    print("\n" + "=" * 50)
    if all_passed and env_ok:
        print("✅ All tests passed! You're ready to run the app.")
        print("\nRun: streamlit run app.py")
    elif all_passed:
        print("⚠️  Dependencies OK, but .env needs configuration")
        print("\n1. Copy .env.example to .env")
        print("2. Add your OPENAI_API_KEY")
        print("3. Run: streamlit run app.py")
    else:
        print("❌ Setup incomplete. Please fix the errors above.")

    print("=" * 50)


if __name__ == "__main__":
    main()
