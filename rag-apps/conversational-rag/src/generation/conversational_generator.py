"""
Conversational answer generation with chat history
"""
from typing import List
import openai
from ..models import RetrievalResult, RAGResponse, ConversationHistory
from ..utils.config import Config


class ConversationalGenerator:
    """Generate answers with conversation context"""

    def __init__(self, model: str = None):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = model or Config.CHAT_MODEL

    def generate(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult],
        conversation_history: ConversationHistory
    ) -> RAGResponse:
        """
        Generate answer with conversation context

        System prompt includes:
        - Role definition
        - Instruction to use conversation context
        - Instruction to cite sources

        Messages include:
        - Conversation history (formatted)
        - Current retrieved context
        - Current query
        """
        # Build context from retrieved chunks
        context = self._format_context(retrieved_chunks)

        # Build messages
        messages = [
            {
                "role": "system",
                "content": self._build_system_prompt()
            }
        ]

        # Add conversation history (excluding the current query)
        messages.extend(conversation_history.format_for_llm())

        # Add current query with context
        messages.append({
            "role": "user",
            "content": f"""Context from documents:
{context}

Question: {query}"""
        })

        # Generate
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )

            answer = response.choices[0].message.content

            return RAGResponse(
                query=query,
                answer=answer,
                retrieved_chunks=retrieved_chunks,
                metrics={
                    "model": self.model,
                    "num_chunks": len(retrieved_chunks),
                    "conversation_length": len(conversation_history.messages)
                }
            )
        except Exception as e:
            error_answer = f"Error generating response: {str(e)}"
            return RAGResponse(
                query=query,
                answer=error_answer,
                retrieved_chunks=retrieved_chunks,
                metrics={"error": str(e)}
            )

    def _build_system_prompt(self) -> str:
        """Build system prompt for conversational RAG"""
        return """You are a helpful assistant that answers questions based on provided documents.

Guidelines:
- Use the conversation history to understand context and follow-up questions
- Answer follow-up questions naturally (e.g., "tell me more" refers to the previous topic)
- Always ground your answers in the provided context from the documents
- If you reference specific information, mention which part of the context it came from
- If the context doesn't contain enough information to answer the question, say so clearly
- Be conversational but accurate
- Maintain consistency with your previous answers in the conversation
- If asked to clarify or elaborate, build upon your previous responses"""

    def _format_context(self, chunks: List[RetrievalResult]) -> str:
        """Format retrieved chunks into context string"""
        if not chunks:
            return "No relevant context found in the documents."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i} - Page {chunk.page}]\n{chunk.content}\n"
            )

        return "\n".join(context_parts)
