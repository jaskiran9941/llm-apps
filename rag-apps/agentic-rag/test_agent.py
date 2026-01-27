"""Test script to verify the agentic RAG system works."""

from agent import AgenticRAG
import config
import os

def print_divider():
    print("\n" + "="*80 + "\n")

def test_agentic_rag():
    """Test the agentic RAG system."""

    print("🤖 Testing Truly Agentic RAG System")
    print_divider()

    # Check API key
    if not config.OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("\nPlease create a .env file with:")
        print("OPENAI_API_KEY=your-key-here")
        return

    print("✅ API key found")

    # Initialize agent
    print("\n🔧 Initializing agent...")
    agent = AgenticRAG()

    # Initialize knowledge base
    print("\n📚 Initializing knowledge base...")
    result = agent.initialize_knowledge_base()
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

    print_divider()

    # Test queries
    test_queries = [
        {
            "question": "What is an agentic AI system?",
            "description": "Should find info in local sample_knowledge.txt"
        },
        {
            "question": "What is quantum computing?",
            "description": "Should search the web"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {test['question']}")
        print(f"Expected: {test['description']}")
        print_divider()

        result = agent.research(test['question'])

        print(f"\n✅ Success: {result['success']}")
        print(f"🔄 Iterations: {result['iterations']}")
        print(f"📄 Documents Retrieved: {len(result['documents_used'])}")

        print("\n💭 REASONING TRACE:")
        for trace in result['reasoning_trace']:
            print(f"\n  Iteration {trace['iteration']}:")
            print(f"  💭 Thought: {trace['thought'][:100]}...")
            print(f"  🎯 Tool: {trace['tool']}")
            print(f"  🔍 Query: {trace['query']}")
            print(f"  👀 Observation: {trace['observation']}")
            print(f"  🤔 Reflection: {trace['reflection'][:100]}...")
            if 'evaluation_score' in trace:
                print(f"  ⭐ Score: {trace['evaluation_score']}/10")

        print(f"\n📝 ANSWER:")
        print("-" * 80)
        print(result['answer'][:500])
        if len(result['answer']) > 500:
            print("...(truncated)")
        print("-" * 80)

        print_divider()

    print("\n✅ All tests completed!")
    print("\n💡 To see the full UI, run: streamlit run app.py")

if __name__ == "__main__":
    test_agentic_rag()
