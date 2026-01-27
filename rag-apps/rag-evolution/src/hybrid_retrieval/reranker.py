"""
Reranking using OpenAI models
"""
from typing import List
import openai
from ..common.models import RetrievalResult
from ..common.config import Config

openai.api_key = Config.OPENAI_API_KEY


class OpenAIReranker:
    """Rerank results using OpenAI GPT"""

    def __init__(self, model: str = None):
        self.model = model or Config.TEXT_MODEL

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Rerank results using GPT to assess relevance.

        This is more expensive but more accurate than simple similarity.
        """
        if not results:
            return []

        # Create relevance assessment prompt
        prompt = self._create_rerank_prompt(query, results)

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a relevance assessor. Rate how relevant each passage is to the query on a scale of 0-10."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )

            # Parse scores
            scores = self._parse_scores(response.choices[0].message.content, len(results))

            # Update results with new scores
            reranked = []
            for i, result in enumerate(results):
                if i < len(scores):
                    reranked_result = RetrievalResult(
                        content=result.content,
                        score=scores[i] / 10.0,  # Normalize to 0-1
                        chunk_id=result.chunk_id,
                        page=result.page,
                        result_type=result.result_type,
                        metadata={
                            **result.metadata,
                            "retrieval_method": "hybrid_reranked",
                            "original_score": result.score,
                            "rerank_score": scores[i]
                        }
                    )
                    reranked.append(reranked_result)

            # Sort by new scores
            reranked.sort(key=lambda x: x.score, reverse=True)

            return reranked[:top_k]

        except Exception as e:
            print(f"Error reranking: {e}")
            return results[:top_k]

    def _create_rerank_prompt(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> str:
        """Create prompt for reranking"""
        passages_text = []
        for i, result in enumerate(results, 1):
            passages_text.append(f"Passage {i}:\n{result.content[:300]}...")

        prompt = f"""Query: {query}

Rate the relevance of each passage to the query on a scale of 0-10.
Output only the scores as a comma-separated list (e.g., "8,6,9,4,7").

{chr(10).join(passages_text)}

Scores:"""
        return prompt

    def _parse_scores(self, response: str, num_results: int) -> List[float]:
        """Parse scores from GPT response"""
        try:
            # Extract numbers from response
            import re
            numbers = re.findall(r'\d+', response)
            scores = [float(n) for n in numbers[:num_results]]

            # Ensure we have enough scores
            while len(scores) < num_results:
                scores.append(5.0)  # Default medium score

            return scores
        except:
            # Return default scores if parsing fails
            return [5.0] * num_results
