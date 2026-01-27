"""
Answer generation using OpenAI GPT-4
"""
from typing import List
import openai
from ..common.models import RetrievalResult, RAGResponse
from ..common.config import Config
from ..common.utils import format_context, calculate_metrics

openai.api_key = Config.OPENAI_API_KEY


class Generator:
    """Generate answers from retrieved context"""

    def __init__(self, model: str = None):
        self.model = model or Config.TEXT_MODEL

    def generate(
        self,
        query: str,
        retrieved_chunks: List[RetrievalResult]
    ) -> RAGResponse:
        """Generate answer from query and retrieved chunks"""

        # Format context
        context = format_context(
            [chunk.content for chunk in retrieved_chunks],
            max_chunks=Config.MAX_CHUNKS
        )

        # Create prompt
        prompt = self._create_prompt(query, context)

        # Generate answer
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context. Be concise and accurate."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            answer = response.choices[0].message.content

        except Exception as e:
            answer = f"Error generating answer: {str(e)}"

        # Calculate metrics
        metrics = calculate_metrics(query, retrieved_chunks)

        return RAGResponse(
            query=query,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            metrics=metrics
        )

    def _create_prompt(self, query: str, context: str) -> str:
        """Create generation prompt"""
        return f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
