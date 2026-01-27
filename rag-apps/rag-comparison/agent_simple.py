"""Simplified agentic RAG with web search only (no ChromaDB dependency)."""

from typing import Dict, List
from openai import OpenAI
import json
import os
from duckduckgo_search import DDGS

class WebSearchRetriever:
    """Searches the web using DuckDuckGo."""

    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 5) -> Dict:
        """Search the web."""
        try:
            results = list(self.ddgs.text(query, max_results=max_results))

            documents = []
            for result in results:
                documents.append({
                    "content": f"{result.get('title', '')}\n\n{result.get('body', '')}",
                    "metadata": {
                        "source": result.get('href', ''),
                        "title": result.get('title', '')
                    },
                    "url": result.get('href', '')
                })

            return {
                "success": True,
                "documents": documents,
                "count": len(documents)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "documents": []
            }


class AgenticRAG:
    """A truly autonomous research agent with self-evaluation."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-openai-api-key-here":
            raise ValueError("Please set OPENAI_API_KEY in .env file")

        self.client = OpenAI(api_key=api_key)
        self.web_retriever = WebSearchRetriever()
        self.max_iterations = 3
        self.evaluation_threshold = 7

    def _plan_next_action(self, question: str, history: List[Dict]) -> Dict:
        """Agent decides what to do next."""

        attempts_context = ""
        if history:
            attempts_context = "\n\nPrevious attempts:\n"
            for i, attempt in enumerate(history, 1):
                attempts_context += f"\nAttempt {i}:\n"
                attempts_context += f"- Query: {attempt['query']}\n"
                attempts_context += f"- Result: {attempt['observation'][:150]}...\n"
                attempts_context += f"- Evaluation: {attempt.get('reflection', 'N/A')[:100]}...\n"

        planning_prompt = f"""You are an autonomous research agent. Analyze the question and decide your next search strategy.

Question: {question}
{attempts_context}

Based on the question and previous attempts (if any), decide:
1. What specific query to search for (you can refine/rephrase the original question)
2. Your reasoning for this search strategy

Respond in JSON format:
{{
    "thought": "Your reasoning about what information is needed and why",
    "query": "The specific search query to use (be specific and detailed)",
    "reasoning": "Why you chose this query and what you expect to find"
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": planning_prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        plan = json.loads(response.choices[0].message.content)
        plan["tool"] = "search_web"  # Only web search in simplified version
        return plan

    def _evaluate_results(self, question: str, documents: List[Dict]) -> Dict:
        """Agent evaluates if retrieved documents answer the question."""

        if not documents:
            return {
                "score": 0,
                "reasoning": "No documents were retrieved.",
                "is_sufficient": False
            }

        docs_text = "\n\n---\n\n".join([
            f"Document {i+1} ({doc.get('metadata', {}).get('title', 'Untitled')}):\n{doc['content'][:400]}..."
            for i, doc in enumerate(documents[:3])
        ])

        eval_prompt = f"""Evaluate if these web search results can answer the question.

Question: {question}

Retrieved Web Pages:
{docs_text}

Rate on a scale of 1-10 how well these results answer the question:
- 1-3: Results are irrelevant or off-topic
- 4-6: Results have some relevant information but missing key details
- 7-8: Results have most of the needed information
- 9-10: Results fully answer the question with comprehensive information

Respond in JSON format:
{{
    "score": <number 1-10>,
    "reasoning": "Brief explanation of why you gave this score",
    "is_sufficient": <true if score >= {self.evaluation_threshold}, false otherwise>,
    "missing_info": "What information is missing, if any"
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _generate_answer(self, question: str, documents: List[Dict]) -> str:
        """Generate final answer from retrieved documents."""

        docs_text = "\n\n---\n\n".join([
            f"Source {i+1}: {doc.get('metadata', {}).get('title', 'Untitled')}\n"
            f"URL: {doc.get('url', 'N/A')}\n"
            f"Content: {doc['content']}"
            for i, doc in enumerate(documents)
        ])

        answer_prompt = f"""Answer the question based on the provided web sources.

Question: {question}

Web Sources:
{docs_text}

Instructions:
- Provide a comprehensive answer based on the sources
- Cite sources when making specific claims (mention the source title or URL)
- If sources partially answer the question, say what's covered and what isn't
- Be clear and concise

Answer:"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": answer_prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content

    def research(self, question: str) -> Dict:
        """Main agentic research loop with self-evaluation and replanning."""

        reasoning_trace = []
        all_retrieved_docs = []
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # THOUGHT: Plan next action
            plan = self._plan_next_action(question, reasoning_trace)

            reasoning_trace.append({
                "iteration": iteration,
                "thought": plan["thought"],
                "tool": plan["tool"],
                "query": plan["query"],
                "reasoning": plan["reasoning"]
            })

            # ACTION: Execute web search
            result = self.web_retriever.search(plan["query"])

            if not result["success"]:
                reasoning_trace[-1]["observation"] = f"ERROR: {result['error']}"
                reasoning_trace[-1]["reflection"] = "Search failed, will try different approach"
                continue

            documents = result["documents"]
            reasoning_trace[-1]["observation"] = f"Retrieved {len(documents)} web pages"
            all_retrieved_docs.extend(documents)

            # REFLECTION: Evaluate results
            evaluation = self._evaluate_results(question, documents)

            reasoning_trace[-1]["reflection"] = evaluation["reasoning"]
            reasoning_trace[-1]["evaluation_score"] = evaluation["score"]
            reasoning_trace[-1]["is_sufficient"] = evaluation["is_sufficient"]

            # If results are good enough, generate answer
            if evaluation["is_sufficient"]:
                answer = self._generate_answer(question, all_retrieved_docs)

                return {
                    "answer": answer,
                    "reasoning_trace": reasoning_trace,
                    "documents_used": all_retrieved_docs,
                    "iterations": iteration,
                    "success": True
                }

        # Max iterations reached
        if all_retrieved_docs:
            answer = self._generate_answer(question, all_retrieved_docs)
            answer = f"⚠️ I reached my maximum search attempts. Based on what I found:\n\n{answer}"
        else:
            answer = "I couldn't find sufficient information after multiple attempts."

        return {
            "answer": answer,
            "reasoning_trace": reasoning_trace,
            "documents_used": all_retrieved_docs,
            "iterations": iteration,
            "success": False,
            "reason": "max_iterations_reached"
        }
