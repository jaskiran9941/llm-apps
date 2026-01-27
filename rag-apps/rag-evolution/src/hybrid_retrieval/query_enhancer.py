"""
Query enhancement techniques
"""
from typing import List
import openai
from ..common.config import Config

openai.api_key = Config.OPENAI_API_KEY


class QueryEnhancer:
    """Enhance queries for better retrieval"""

    def __init__(self, model: str = None):
        self.model = model or Config.TEXT_MODEL

    def rewrite_query(self, query: str) -> str:
        """Rewrite query to be more search-friendly"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Rewrite the user's question as a search query with important keywords. Keep it concise."
                    },
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nSearch query:"
                    }
                ],
                temperature=0.3,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except:
            return query

    def expand_query(self, query: str) -> List[str]:
        """Generate multiple query variations (Multi-Query)"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate 3 alternative versions of the question that would retrieve the same information."
                    },
                    {
                        "role": "user",
                        "content": f"Original question: {query}\n\nAlternative questions (one per line):"
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )

            # Parse response
            content = response.choices[0].message.content
            variations = [line.strip() for line in content.split('\n') if line.strip()]

            # Remove numbering if present
            import re
            variations = [re.sub(r'^\d+[\.\)]\s*', '', v) for v in variations]

            return [query] + variations[:3]
        except:
            return [query]

    def generate_hypothetical_answer(self, query: str) -> str:
        """
        HyDE: Generate hypothetical answer, then search for similar docs.
        Often more accurate than searching with the question.
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a hypothetical answer to the question as it might appear in a document."
                    },
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nHypothetical answer:"
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except:
            return query

    def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the most important keywords from the query. Output as comma-separated list."
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nKeywords:"
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )

            # Parse keywords
            content = response.choices[0].message.content
            keywords = [k.strip() for k in content.split(',')]
            return keywords
        except:
            # Fallback to simple splitting
            return query.lower().split()
