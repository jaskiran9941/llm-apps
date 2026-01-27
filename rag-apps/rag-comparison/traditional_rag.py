"""Traditional RAG: Simple retrieve-then-generate without evaluation or correction."""

from typing import Dict, List
from openai import OpenAI
import config
from tools import LocalDocumentRetriever


class TraditionalRAG:
    """Baseline RAG implementation: single retrieval + generation."""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.local_retriever = LocalDocumentRetriever()

    def initialize_knowledge_base(self):
        """Initialize or load the vector database."""
        result = self.local_retriever.load_existing()
        if result["status"] == "loaded":
            return result
        return self.local_retriever.initialize()

    def _generate_answer(self, question: str, documents: List[Dict]) -> str:
        """Generate answer from retrieved documents."""
        if not documents:
            return "No relevant documents found to answer this question."

        docs_text = "\n\n---\n\n".join([
            f"Source {i+1} ({doc.get('metadata', {}).get('source', 'Unknown')}):\n{doc['content']}"
            for i, doc in enumerate(documents)
        ])

        answer_prompt = f"""Answer the question based on the provided sources.

Question: {question}

Sources:
{docs_text}

Instructions:
- Provide a comprehensive answer based on the sources
- Cite sources when making specific claims
- If sources don't contain the answer, say so clearly
- Be clear and concise

Answer:"""

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": answer_prompt}],
            temperature=config.TEMPERATURE
        )

        return response.choices[0].message.content

    def answer(self, question: str) -> Dict:
        """Traditional RAG: retrieve once, generate answer."""
        # Single retrieval from local docs
        result = self.local_retriever.search(question)

        if not result["success"]:
            return {
                "answer": f"Error retrieving documents: {result['error']}",
                "documents": [],
                "retrieval_count": 0,
                "success": False
            }

        documents = result["documents"]

        # Generate answer directly without evaluation
        answer = self._generate_answer(question, documents)

        return {
            "answer": answer,
            "documents": documents,
            "retrieval_count": 1,
            "llm_calls": 1,
            "success": True
        }
