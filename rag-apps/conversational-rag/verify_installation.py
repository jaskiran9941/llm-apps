"""
Simple installation verification
"""
import os
from pathlib import Path

def check_dependencies():
    """Check if dependencies are installed"""
    print("Checking dependencies...")

    deps = [
        "streamlit",
        "openai",
        "PyPDF2",
        "pydantic",
        "rank_bm25",
        "dotenv",
        "nltk",
        "numpy"
    ]

    all_ok = True
    for dep in deps:
        try:
            __import__(dep if dep != "rank_bm25" else "rank_bm25")
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - Not installed")
            all_ok = False

    return all_ok

def check_env():
    """Check environment configuration"""
    print("\nChecking environment...")

    env_path = Path(".env")
    if not env_path.exists():
        print("✗ .env file not found")
        print("  Run: cp .env.example .env")
        print("  Then add your OPENAI_API_KEY")
        return False

    print("✓ .env file exists")

    from dotenv import load_dotenv
    load_dotenv()

    if os.getenv("OPENAI_API_KEY"):
        print("✓ OPENAI_API_KEY is set")
        return True
    else:
        print("✗ OPENAI_API_KEY not set")
        print("  Add your OpenAI API key to .env file")
        return False

def check_structure():
    """Check project structure"""
    print("\nChecking project structure...")

    required_files = [
        "app.py",
        "requirements.txt",
        "src/models.py",
        "src/document_processor.py",
        "src/retrieval/vector_search.py",
        "src/retrieval/bm25_search.py",
        "src/retrieval/conversational_retriever.py",
        "src/generation/embedder.py",
        "src/generation/conversational_generator.py",
        "src/utils/config.py"
    ]

    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - Missing")
            all_ok = False

    return all_ok

def main():
    print("=" * 60)
    print("Conversational RAG - Installation Verification")
    print("=" * 60)
    print()

    deps_ok = check_dependencies()
    env_ok = check_env()
    struct_ok = check_structure()

    print("\n" + "=" * 60)

    if deps_ok and env_ok and struct_ok:
        print("✅ Installation verified! Ready to run.")
        print("\nNext steps:")
        print("  streamlit run app.py")
    elif not deps_ok:
        print("❌ Missing dependencies")
        print("\nNext steps:")
        print("  pip install -r requirements.txt")
    elif not env_ok:
        print("⚠️  Environment not configured")
        print("\nNext steps:")
        print("  1. cp .env.example .env")
        print("  2. Add your OPENAI_API_KEY to .env")
        print("  3. streamlit run app.py")
    else:
        print("❌ Installation incomplete")

    print("=" * 60)

if __name__ == "__main__":
    main()
