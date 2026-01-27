"""Quick test script to verify all three RAG implementations work."""

from traditional_rag import TraditionalRAG
from corrective_rag import CorrectiveRAG
from agent import AgenticRAG


def test_all_systems():
    """Test that all three systems can be initialized and run."""

    print("=" * 60)
    print("Testing RAG Comparison Systems")
    print("=" * 60)

    # Initialize systems
    print("\n1. Initializing Traditional RAG...")
    trad = TraditionalRAG()
    result = trad.initialize_knowledge_base()
    print(f"   Status: {result['status']} - {result['message']}")

    print("\n2. Initializing Corrective RAG...")
    corr = CorrectiveRAG()
    result = corr.initialize_knowledge_base()
    print(f"   Status: {result['status']} - {result['message']}")

    print("\n3. Initializing Agentic RAG...")
    agent = AgenticRAG()
    result = agent.initialize_knowledge_base()
    print(f"   Status: {result['status']} - {result['message']}")

    # Test query
    test_query = "What is machine learning?"

    print(f"\n" + "=" * 60)
    print(f"Test Query: {test_query}")
    print("=" * 60)

    # Test Traditional RAG
    print("\n[Traditional RAG]")
    try:
        result = trad.answer(test_query)
        print(f"✅ Success: {result['success']}")
        print(f"   LLM Calls: {result.get('llm_calls', 'N/A')}")
        print(f"   Documents: {len(result.get('documents', []))}")
        print(f"   Answer preview: {result['answer'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test Corrective RAG
    print("\n[Corrective RAG]")
    try:
        result = corr.answer(test_query)
        print(f"✅ Success: {result['success']}")
        print(f"   LLM Calls: {result.get('llm_calls', 'N/A')}")
        print(f"   Documents: {len(result.get('documents', []))}")
        print(f"   Grade: {result.get('final_grade', {}).get('relevance', 'N/A')}")
        print(f"   Corrections: {len(result.get('correction_history', []))} steps")
        print(f"   Answer preview: {result['answer'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test Agentic RAG
    print("\n[Agentic RAG]")
    try:
        result = agent.research(test_query)
        print(f"✅ Success: {result['success']}")
        print(f"   Iterations: {result.get('iterations', 'N/A')}")
        print(f"   Documents: {len(result.get('documents_used', []))}")
        print(f"   Answer preview: {result['answer'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
    print("\nTo run the comparison UI:")
    print("  streamlit run app_comparison.py")


if __name__ == "__main__":
    test_all_systems()
