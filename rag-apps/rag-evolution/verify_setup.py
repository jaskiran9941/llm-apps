#!/usr/bin/env python3
"""
Verification script for RAG Evolution project
Run this to check if everything is set up correctly
"""

import sys
from pathlib import Path
import os

def check_mark(condition):
    return "✅" if condition else "❌"

def main():
    print("🔍 Verifying RAG Evolution Setup...\n")

    all_good = True

    # Check Python version
    print("1. Checking Python version...")
    version = sys.version_info
    python_ok = version.major == 3 and version.minor >= 8
    print(f"   {check_mark(python_ok)} Python {version.major}.{version.minor}.{version.micro}")
    if not python_ok:
        print("   ⚠️  Python 3.8+ required")
        all_good = False

    # Check directory structure
    print("\n2. Checking directory structure...")
    required_dirs = [
        "src",
        "src/baseline_rag",
        "src/advanced_chunking",
        "src/hybrid_retrieval",
        "src/vision_rag",
        "src/common",
        "tabs",
        "tests",
        "data",
        "data/sample_docs",
        "data/images",
    ]

    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        print(f"   {check_mark(exists)} {dir_path}/")
        if not exists:
            all_good = False

    # Check required files
    print("\n3. Checking required files...")
    required_files = [
        "app.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "QUICKSTART.md",
        # Tab files
        "tabs/tab1_baseline.py",
        "tabs/tab2_chunking.py",
        "tabs/tab3_hybrid.py",
        "tabs/tab4_vision.py",
        # Common files
        "src/common/models.py",
        "src/common/config.py",
        "src/common/utils.py",
        # Baseline RAG
        "src/baseline_rag/simple_chunker.py",
        "src/baseline_rag/text_embedder.py",
        "src/baseline_rag/vector_search.py",
        "src/baseline_rag/generator.py",
        # Advanced chunking
        "src/advanced_chunking/sentence_chunker.py",
        "src/advanced_chunking/semantic_chunker.py",
        "src/advanced_chunking/preprocessors.py",
        # Hybrid retrieval
        "src/hybrid_retrieval/bm25_searcher.py",
        "src/hybrid_retrieval/hybrid_fusion.py",
        "src/hybrid_retrieval/reranker.py",
        "src/hybrid_retrieval/query_enhancer.py",
        # Vision RAG
        "src/vision_rag/image_extractor.py",
        "src/vision_rag/vision_embedder.py",
        "src/vision_rag/multimodal_store.py",
        "src/vision_rag/multimodal_retriever.py",
        "src/vision_rag/vision_generator.py",
    ]

    for file_path in required_files:
        exists = Path(file_path).exists()
        print(f"   {check_mark(exists)} {file_path}")
        if not exists:
            all_good = False

    # Check .env file
    print("\n4. Checking configuration...")
    env_exists = Path(".env").exists()
    print(f"   {check_mark(env_exists)} .env file exists")

    if env_exists:
        # Check if API key is set
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY", "")
        key_set = len(api_key) > 0 and not api_key.startswith("your_")
        print(f"   {check_mark(key_set)} OpenAI API key configured")
        if not key_set:
            print("   ⚠️  Set your OPENAI_API_KEY in .env file")
            all_good = False
    else:
        print("   ⚠️  Copy .env.example to .env and add your OpenAI API key")
        all_good = False

    # Try importing key modules
    print("\n5. Checking Python dependencies...")

    dependencies = [
        ("streamlit", "Streamlit"),
        ("openai", "OpenAI"),
        ("chromadb", "ChromaDB"),
        ("PyPDF2", "PyPDF2"),
        ("fitz", "PyMuPDF"),
        ("PIL", "Pillow"),
        ("nltk", "NLTK"),
        ("rank_bm25", "rank-bm25"),
        ("pandas", "Pandas"),
        ("sklearn", "scikit-learn"),
    ]

    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name}")
        except ImportError:
            print(f"   ❌ {display_name} - run: pip install -r requirements.txt")
            all_good = False

    # Check NLTK data
    print("\n6. Checking NLTK data...")
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
            print("   ✅ NLTK punkt tokenizer")
        except LookupError:
            print("   ❌ NLTK punkt not found")
            print("   Run: python -c \"import nltk; nltk.download('punkt')\"")
            all_good = False
    except ImportError:
        print("   ⚠️  NLTK not installed")

    # Final summary
    print("\n" + "="*50)
    if all_good:
        print("✅ Everything looks good!")
        print("\nNext steps:")
        print("1. Make sure .env has your OpenAI API key")
        print("2. Run: streamlit run app.py")
        print("3. Start learning RAG!")
        return 0
    else:
        print("❌ Some issues found")
        print("\nPlease fix the issues above and run again")
        print("\nQuick fix:")
        print("  ./setup.sh")
        return 1

if __name__ == "__main__":
    exit(main())
