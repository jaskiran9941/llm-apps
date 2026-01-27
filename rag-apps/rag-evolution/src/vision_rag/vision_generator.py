"""
Generate answers with multimodal context
"""
from typing import List
import openai
from ..common.models import RetrievalResult, RAGResponse
from ..common.config import Config
from ..common.utils import calculate_metrics

openai.api_key = Config.OPENAI_API_KEY


class VisionGenerator:
    """Generate answers using both text and image context"""

    def __init__(self, model: str = None):
        self.model = model or Config.TEXT_MODEL

    def generate(
        self,
        query: str,
        text_results: List[RetrievalResult],
        image_results: List[RetrievalResult]
    ) -> RAGResponse:
        """Generate answer with multimodal context"""

        # Format context
        context = self._format_multimodal_context(text_results, image_results)

        # Create prompt
        prompt = self._create_prompt(query, context)

        # Generate answer
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that answers questions using both text and image information.
When referencing information from images, mention that it comes from a chart/diagram/image.
Be specific about numbers and details visible in the images."""
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

        # Collect all results
        all_results = text_results + image_results

        # Calculate metrics
        metrics = calculate_metrics(query, all_results)
        metrics["num_images"] = len(image_results)
        metrics["num_text_chunks"] = len(text_results)

        # Get image paths
        image_paths = [r.image_path for r in image_results if r.image_path]

        return RAGResponse(
            query=query,
            answer=answer,
            retrieved_chunks=all_results,
            images=image_paths,
            metrics=metrics
        )

    def _format_multimodal_context(
        self,
        text_results: List[RetrievalResult],
        image_results: List[RetrievalResult]
    ) -> str:
        """Format context from both text and images"""
        context_parts = []

        # Add text context
        if text_results:
            context_parts.append("=== Text Information ===")
            for i, result in enumerate(text_results, 1):
                context_parts.append(f"\n[Text {i}]\n{result.content}")

        # Add image descriptions
        if image_results:
            context_parts.append("\n\n=== Visual Information ===")
            for i, result in enumerate(image_results, 1):
                context_parts.append(f"\n[Image {i}]\n{result.content}")

        return "\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """Create generation prompt"""
        return f"""Based on the following text and visual information, answer the question.

{context}

Question: {query}

Answer (reference specific information from the text and images):"""
