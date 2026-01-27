"""Corrective RAG (CRAG): Retrieve → Grade → Correct → Generate."""

from typing import Dict, List
from openai import OpenAI
import json
import config
from tools import LocalDocumentRetriever, WebSearchRetriever


class CorrectiveRAG:
    """CRAG implementation with relevance grading and corrective actions."""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.local_retriever = LocalDocumentRetriever()
        self.web_retriever = WebSearchRetriever()
        self.correction_history = []

    def initialize_knowledge_base(self):
        """Initialize or load the vector database."""
        result = self.local_retriever.load_existing()
        if result["status"] == "loaded":
            return result
        return self.local_retriever.initialize()

    def _retrieve_documents(self, query: str, source: str = "local") -> Dict:
        """Retrieve documents from specified source."""
        if source == "local":
            return self.local_retriever.search(query)
        elif source == "web":
            return self.web_retriever.search(query)
        else:
            return {"success": False, "error": f"Unknown source: {source}", "documents": []}

    def _grade_relevance(self, question: str, documents: List[Dict]) -> Dict:
        """Grade the relevance of retrieved documents."""
        if not documents:
            return {
                "relevance": "not_relevant",
                "confidence": 1.0,
                "reason": "No documents were retrieved",
                "action": "web_search"
            }

        docs_text = "\n\n---\n\n".join([
            f"Document {i+1}:\n{doc['content'][:400]}..."
            for i, doc in enumerate(documents[:3])
        ])

        grading_prompt = f"""You are a relevance grader. Evaluate if the retrieved documents can answer the question.

Question: {question}

Retrieved Documents:
{docs_text}

Grade the relevance and recommend an action:

Relevance levels:
- "relevant": Documents contain sufficient information to answer the question
- "ambiguous": Documents have partial information; a query rewrite might find better results
- "not_relevant": Documents are off-topic or don't address the question; need different knowledge source

Actions:
- "none": Documents are relevant, proceed to generate answer
- "rewrite": Rewrite query and try local retrieval again
- "web_search": Switch to web search for external knowledge

Respond in JSON format:
{{
    "relevance": "relevant|ambiguous|not_relevant",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation of why you assigned this grade",
    "action": "none|rewrite|web_search"
}}"""

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": grading_prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _rewrite_query(self, original_query: str, reason: str) -> str:
        """Rewrite query for better retrieval."""
        rewrite_prompt = f"""You are a query optimization expert. Rewrite the query to improve retrieval results.

Original query: {original_query}

Reason for rewrite: {reason}

Generate a better query that:
- Uses more specific keywords
- Expands abbreviations or clarifies ambiguous terms
- Reformulates the question for better semantic matching

Respond with only the rewritten query, no explanation."""

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": rewrite_prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content.strip()

    def _generate_answer(self, question: str, documents: List[Dict]) -> str:
        """Generate final answer from documents."""
        if not documents:
            return "I couldn't find relevant information to answer this question."

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
- If sources partially answer the question, say what's covered and what isn't
- Be clear and concise

Answer:"""

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": answer_prompt}],
            temperature=config.TEMPERATURE
        )

        return response.choices[0].message.content

    def answer(self, question: str) -> Dict:
        """Main Corrective RAG flow."""
        self.correction_history = []
        all_documents = []
        llm_calls = 0

        # Step 1: Initial retrieval from local docs
        self.correction_history.append({
            "step": "initial_retrieval",
            "action": "Retrieving from local documents",
            "query": question
        })

        result = self._retrieve_documents(question, source="local")
        if not result["success"]:
            return {
                "answer": f"Error: {result['error']}",
                "correction_history": self.correction_history,
                "documents": [],
                "llm_calls": llm_calls,
                "success": False
            }

        initial_docs = result["documents"]
        all_documents.extend(initial_docs)

        self.correction_history[-1]["documents_found"] = len(initial_docs)

        # Step 2: Grade relevance
        self.correction_history.append({
            "step": "grading",
            "action": "Grading relevance of retrieved documents"
        })

        grade = self._grade_relevance(question, initial_docs)
        llm_calls += 1

        self.correction_history[-1]["grade"] = grade["relevance"]
        self.correction_history[-1]["confidence"] = grade["confidence"]
        self.correction_history[-1]["reason"] = grade["reason"]
        self.correction_history[-1]["recommended_action"] = grade["action"]

        # Step 3: Corrective action if needed
        if grade["action"] == "rewrite":
            # Rewrite query and retrieve again
            self.correction_history.append({
                "step": "corrective_action",
                "action": "Rewriting query for better results"
            })

            rewritten_query = self._rewrite_query(question, grade["reason"])
            llm_calls += 1

            self.correction_history[-1]["original_query"] = question
            self.correction_history[-1]["rewritten_query"] = rewritten_query

            # Retrieve with rewritten query
            result = self._retrieve_documents(rewritten_query, source="local")
            if result["success"]:
                corrected_docs = result["documents"]
                all_documents = corrected_docs  # Use new documents
                self.correction_history[-1]["documents_found"] = len(corrected_docs)
            else:
                self.correction_history[-1]["error"] = result["error"]

        elif grade["action"] == "web_search":
            # Switch to web search
            self.correction_history.append({
                "step": "corrective_action",
                "action": "Switching to web search for external knowledge"
            })

            result = self._retrieve_documents(question, source="web")
            if result["success"]:
                web_docs = result["documents"]
                all_documents = web_docs  # Replace with web results
                self.correction_history[-1]["documents_found"] = len(web_docs)
            else:
                self.correction_history[-1]["error"] = result["error"]

        # Step 4: Generate answer
        self.correction_history.append({
            "step": "generation",
            "action": "Generating final answer"
        })

        answer = self._generate_answer(question, all_documents)
        llm_calls += 1

        self.correction_history[-1]["documents_used"] = len(all_documents)

        return {
            "answer": answer,
            "correction_history": self.correction_history,
            "documents": all_documents,
            "llm_calls": llm_calls,
            "success": True,
            "final_grade": grade
        }
