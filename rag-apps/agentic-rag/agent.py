"""Truly agentic RAG with ReAct loop, self-evaluation, and dynamic replanning."""

from typing import Dict, List, Optional
from openai import OpenAI
import json
import config
from tools import LocalDocumentRetriever, WebSearchRetriever, TOOLS


class AgenticRAG:
    """An autonomous research agent with self-evaluation and dynamic replanning."""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.local_retriever = LocalDocumentRetriever()
        self.web_retriever = WebSearchRetriever()
        self.conversation_history = []

    def initialize_knowledge_base(self):
        """Initialize or load the vector database."""
        # Try loading existing first
        result = self.local_retriever.load_existing()
        if result["status"] == "loaded":
            return result

        # If not found, initialize new
        return self.local_retriever.initialize()

    def _call_tool(self, tool_name: str, query: str) -> Dict:
        """Execute a retrieval tool."""
        if tool_name == "search_local_docs":
            return self.local_retriever.search(query)
        elif tool_name == "search_web":
            return self.web_retriever.search(query)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

    def _plan_next_action(self, question: str, history: List[Dict]) -> Dict:
        """Agent decides what to do next based on question and history."""

        # Build context from previous attempts
        attempts_context = ""
        if history:
            attempts_context = "\n\nPrevious attempts:\n"
            for i, attempt in enumerate(history, 1):
                attempts_context += f"\nAttempt {i}:\n"
                attempts_context += f"- Tool: {attempt['tool']}\n"
                attempts_context += f"- Query: {attempt['query']}\n"
                attempts_context += f"- Result: {attempt['observation'][:200]}...\n"
                attempts_context += f"- Evaluation: {attempt.get('reflection', 'N/A')}\n"

        tools_desc = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in TOOLS.values()
        ])

        planning_prompt = f"""You are an autonomous research agent. Analyze the question and decide what action to take.

Question: {question}
{attempts_context}

Available tools:
{tools_desc}

Based on the question and any previous attempts, decide:
1. Which tool to use (search_local_docs or search_web)
2. What query to use (may need to rephrase/refine from original question)
3. Your reasoning for this choice

Respond in JSON format:
{{
    "thought": "Your reasoning about what information is needed and why",
    "tool": "search_local_docs or search_web",
    "query": "The specific query to use",
    "reasoning": "Why you chose this tool and query"
}}"""

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": planning_prompt}],
            temperature=config.TEMPERATURE,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _evaluate_results(self, question: str, documents: List[Dict]) -> Dict:
        """Agent evaluates if retrieved documents answer the question."""

        if not documents:
            return {
                "score": 0,
                "reasoning": "No documents were retrieved.",
                "is_sufficient": False
            }

        docs_text = "\n\n---\n\n".join([
            f"Document {i+1}:\n{doc['content'][:500]}..."
            for i, doc in enumerate(documents[:3])  # Only show first 3 for evaluation
        ])

        eval_prompt = f"""Evaluate if these retrieved documents can answer the question.

Question: {question}

Retrieved Documents:
{docs_text}

Rate on a scale of 1-10 how well these documents answer the question:
- 1-3: Documents are irrelevant or off-topic
- 4-6: Documents have some relevant information but missing key details
- 7-8: Documents have most of the needed information
- 9-10: Documents fully answer the question

Respond in JSON format:
{{
    "score": <number 1-10>,
    "reasoning": "Brief explanation of why you gave this score",
    "is_sufficient": <true if score >= {config.EVALUATION_THRESHOLD}, false otherwise>,
    "missing_info": "What information is missing, if any"
}}"""

        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.3,  # Lower temperature for more consistent evaluation
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _generate_answer(self, question: str, documents: List[Dict]) -> str:
        """Generate final answer from retrieved documents."""

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

    def research(self, question: str) -> Dict:
        """Main agentic research loop with self-evaluation and replanning."""

        reasoning_trace = []
        all_retrieved_docs = []
        iteration = 0

        while iteration < config.MAX_ITERATIONS:
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

            # ACTION: Execute tool
            result = self._call_tool(plan["tool"], plan["query"])

            if not result["success"]:
                reasoning_trace[-1]["observation"] = f"ERROR: {result['error']}"
                reasoning_trace[-1]["reflection"] = "Tool failed, will try different approach"
                continue

            documents = result["documents"]
            reasoning_trace[-1]["observation"] = f"Retrieved {len(documents)} documents"
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

            # Otherwise, continue loop (agent will replan with history)

        # Max iterations reached
        if all_retrieved_docs:
            # Generate best-effort answer from what we have
            answer = self._generate_answer(question, all_retrieved_docs)
            answer = f"⚠️ I reached my maximum search attempts. Based on what I found:\n\n{answer}"
        else:
            answer = "I couldn't find sufficient information to answer this question after multiple attempts."

        return {
            "answer": answer,
            "reasoning_trace": reasoning_trace,
            "documents_used": all_retrieved_docs,
            "iterations": iteration,
            "success": False,
            "reason": "max_iterations_reached"
        }
