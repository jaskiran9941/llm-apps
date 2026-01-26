"""
Side-by-side comparison demonstrating the difference between
traditional RAG and truly agentic RAG.
"""

from openai import OpenAI
import config

def traditional_rag_simulation(question: str):
    """Simulates a traditional RAG pipeline."""
    print("\n" + "="*80)
    print("TRADITIONAL RAG (Simple Pipeline)")
    print("="*80 + "\n")

    print("Step 1: Embed query and search vector DB...")
    print("  → Query: 'What is quantum entanglement?'")
    print("  → Retrieved: 1 document (brief mention only)")
    print()

    print("Step 2: Generate answer from retrieved context...")
    print("  → Generating...")
    print()

    print("ANSWER:")
    print("-" * 80)
    print("Based on the available documents, quantum entanglement is mentioned")
    print("as a physics concept. [Answer is vague because only one poor-quality")
    print("document was retrieved]")
    print("-" * 80)
    print()

    print("LIMITATIONS:")
    print("  ❌ Only one retrieval attempt")
    print("  ❌ No quality evaluation")
    print("  ❌ Can't adapt to poor results")
    print("  ❌ No alternative sources tried")
    print()

def conditional_rag_simulation(question: str):
    """Simulates a conditional RAG with fallback (marketed as 'agentic')."""
    print("\n" + "="*80)
    print("CONDITIONAL RAG (Marketed as 'Agentic')")
    print("="*80 + "\n")

    print("Step 1: Search vector DB...")
    print("  → Query: 'What is quantum entanglement?'")
    print("  → Retrieved: 1 document")
    print("  → Average score: 0.3")
    print()

    print("Step 2: Check threshold...")
    print("  → if score < 0.5: trigger web search  # Hardcoded rule")
    print("  → Condition TRUE, executing web search...")
    print()

    print("Step 3: Web search (fallback)...")
    print("  → Query: 'What is quantum entanglement?'  # Same query, no refinement")
    print("  → Retrieved: 5 web results")
    print()

    print("Step 4: Generate answer...")
    print()

    print("ANSWER:")
    print("-" * 80)
    print("Quantum entanglement is a quantum mechanical phenomenon where particles")
    print("become correlated. [Better answer due to web results]")
    print("-" * 80)
    print()

    print("IMPROVEMENTS OVER TRADITIONAL:")
    print("  ✅ Has fallback to web search")
    print("  ✅ Gets better results")
    print()
    print("STILL NOT TRULY AGENTIC:")
    print("  ❌ Fixed if/then logic (no autonomous reasoning)")
    print("  ❌ No query refinement")
    print("  ❌ Can't evaluate or iterate")
    print("  ❌ Predetermined tool selection order")
    print()

def truly_agentic_simulation(question: str):
    """Simulates the truly agentic RAG we built."""
    print("\n" + "="*80)
    print("TRULY AGENTIC RAG (Our Implementation)")
    print("="*80 + "\n")

    print("="*80)
    print("ITERATION 1")
    print("="*80 + "\n")

    print("💭 REASONING:")
    print("   'This is a physics question about quantum mechanics. Let me first")
    print("   check if we have relevant documents in the local knowledge base")
    print("   before searching the web.'")
    print()

    print("🎯 PLAN:")
    print("   Tool: search_local_docs")
    print("   Query: 'quantum entanglement'")
    print("   Reasoning: Start with local docs for efficiency")
    print()

    print("🔧 ACTION: Executing search_local_docs...")
    print("   → Retrieved: 1 document")
    print()

    print("👀 OBSERVATION:")
    print("   Found 1 document with content:")
    print("   'In quantum physics, entanglement refers to correlated particles...'")
    print("   [Only 2 sentences, very brief]")
    print()

    print("🤔 REFLECTION (Self-Evaluation):")
    print("   'Let me evaluate if this answers the question...'")
    print("   ")
    print("   Analysis:")
    print("   - Document mentions entanglement but lacks detail")
    print("   - No explanation of the mechanism")
    print("   - Missing examples and applications")
    print("   ")
    print("   Score: 3/10")
    print("   Decision: NOT SUFFICIENT (threshold is 7/10)")
    print("   Missing: Detailed explanation, examples, scientific basis")
    print()

    print("🔄 AGENT DECISION: Continue to next iteration with different strategy")
    print()

    print("="*80)
    print("ITERATION 2")
    print("="*80 + "\n")

    print("💭 REASONING:")
    print("   'The local document was too brief. I need comprehensive, detailed")
    print("   information from authoritative sources. Web search would be better,")
    print("   and I should refine my query to get more detailed results.'")
    print()

    print("🎯 PLAN:")
    print("   Tool: search_web")
    print("   Query: 'quantum entanglement detailed explanation physics mechanism'")
    print("   Reasoning: Web search for detailed scientific explanation,")
    print("              refined query for better results")
    print()

    print("🔧 ACTION: Executing search_web...")
    print("   → Retrieved: 5 web documents")
    print()

    print("👀 OBSERVATION:")
    print("   Found comprehensive sources:")
    print("   1. Wikipedia: Quantum entanglement")
    print("   2. Physics Today: Understanding entanglement")
    print("   3. Stanford Encyclopedia: EPR paradox")
    print("   4. NASA: Quantum mechanics basics")
    print("   5. Scientific American: Spooky action at a distance")
    print()

    print("🤔 REFLECTION (Self-Evaluation):")
    print("   'Let me evaluate if these sources answer the question...'")
    print("   ")
    print("   Analysis:")
    print("   - Multiple authoritative sources")
    print("   - Detailed scientific explanations")
    print("   - Covers mechanism, history, and applications")
    print("   - Includes examples and implications")
    print("   ")
    print("   Score: 9/10")
    print("   Decision: SUFFICIENT! ✅")
    print()

    print("✅ AGENT DECISION: Quality threshold met, generate final answer")
    print()

    print("="*80)
    print("FINAL ANSWER GENERATION")
    print("="*80 + "\n")

    print("📝 Synthesizing from all retrieved sources (local + web)...")
    print()

    print("ANSWER:")
    print("-" * 80)
    print("Quantum entanglement is a fundamental phenomenon in quantum mechanics where")
    print("two or more particles become correlated in such a way that the quantum state")
    print("of each particle cannot be described independently, even when separated by")
    print("large distances.")
    print()
    print("Key aspects:")
    print()
    print("1. MECHANISM: When particles interact, they can become entangled, creating")
    print("   a shared quantum state. Measuring one particle instantly affects the state")
    print("   of the other, regardless of distance.")
    print()
    print("2. EPR PARADOX: Einstein called this 'spooky action at a distance' and")
    print("   initially believed it showed quantum mechanics was incomplete. However,")
    print("   experiments have confirmed entanglement is real.")
    print()
    print("3. APPLICATIONS: Used in quantum computing, quantum cryptography, and")
    print("   quantum teleportation.")
    print()
    print("Sources:")
    print("- Wikipedia: Quantum Entanglement")
    print("- Stanford Encyclopedia of Philosophy")
    print("- Local knowledge base: Introduction to Quantum Physics")
    print("-" * 80)
    print()

    print("AGENT CAPABILITIES DEMONSTRATED:")
    print("  ✅ Autonomous reasoning about information needs")
    print("  ✅ Self-evaluation of retrieval quality")
    print("  ✅ Dynamic replanning (switched tools)")
    print("  ✅ Query refinement (made query more specific)")
    print("  ✅ Multi-step iteration")
    print("  ✅ Transparent decision-making process")
    print("  ✅ Synthesized from multiple sources")
    print()

    print("REASONING TRACE:")
    print("  Iteration 1: local_docs → insufficient → continue")
    print("  Iteration 2: web_search → sufficient → answer")
    print("  Total LLM calls: 5 (plan + eval + plan + eval + generate)")
    print("  Cost: ~$0.012")
    print("  Time: ~8 seconds")
    print()

def main():
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  RAG COMPARISON DEMO: Traditional vs Conditional vs Truly Agentic".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)

    question = "What is quantum entanglement?"

    print(f"\n🔍 QUESTION: {question}\n")

    # Show all three approaches
    traditional_rag_simulation(question)
    input("\nPress Enter to see Conditional RAG...")

    conditional_rag_simulation(question)
    input("\nPress Enter to see Truly Agentic RAG...")

    truly_agentic_simulation(question)

    print("\n" + "="*80)
    print("SUMMARY COMPARISON")
    print("="*80 + "\n")

    print("┌────────────────────┬──────────────┬──────────────┬──────────────┐")
    print("│ Metric             │ Traditional  │ Conditional  │ Agentic      │")
    print("├────────────────────┼──────────────┼──────────────┼──────────────┤")
    print("│ Retrieval Attempts │ 1            │ 2 (fixed)    │ 1-3 (dynamic)│")
    print("│ Quality Eval       │ No           │ Basic        │ LLM-powered  │")
    print("│ Query Refinement   │ No           │ No           │ Yes          │")
    print("│ Tool Selection     │ Fixed        │ If/then      │ Autonomous   │")
    print("│ Reasoning          │ None         │ Hardcoded    │ LLM-based    │")
    print("│ Adaptability       │ None         │ Low          │ High         │")
    print("│ LLM Calls          │ 1            │ 1-2          │ 3-7          │")
    print("│ Cost               │ ~$0.003      │ ~$0.005      │ ~$0.012      │")
    print("│ Answer Quality     │ Poor         │ Good         │ Excellent    │")
    print("│ Explainability     │ None         │ Minimal      │ Full trace   │")
    print("└────────────────────┴──────────────┴──────────────┴──────────────┘")

    print("\n" + "="*80)
    print("The 'Truly Agentic' approach costs ~4x more but provides:")
    print("  • Autonomous decision-making")
    print("  • Self-evaluation and quality control")
    print("  • Adaptive behavior based on results")
    print("  • Full transparency in reasoning")
    print("  • Significantly better answers for complex questions")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
