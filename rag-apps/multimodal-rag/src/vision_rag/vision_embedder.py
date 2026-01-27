"""
Vision embeddings using GPT-4 Vision
"""
from typing import List
import base64
import openai
from ..common.models import ImageInfo
from ..common.config import Config
from ..baseline_rag.text_embedder import TextEmbedder

openai.api_key = Config.OPENAI_API_KEY


class VisionEmbedder:
    """Generate embeddings for images using GPT-4 Vision"""

    def __init__(self, vision_model: str = None, embedding_model: str = None):
        self.vision_model = vision_model or Config.VISION_MODEL
        self.text_embedder = TextEmbedder(model=embedding_model)

    def describe_image(self, image_path: str) -> str:
        """Use GPT-4 Vision to describe image"""
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()

            # Call GPT-4 Vision
            response = openai.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Describe this image in detail.

If it's a chart or graph:
- Identify the type (bar chart, line graph, pie chart, etc.)
- List all axis labels, data points, and values
- Describe trends and patterns

If it's a diagram:
- Describe all components and their relationships
- List any labels or text

If it's a photo or illustration:
- Describe the main subjects and context
- Note any relevant text or labels

Be thorough and precise."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error describing image {image_path}: {e}")
            return f"Image at {image_path}"

    def embed_image(self, image_info: ImageInfo) -> List[float]:
        """
        Generate embedding for image.
        Strategy: Describe with GPT-4V, then embed the description.
        """
        # Get description if not already available
        if not image_info.description:
            description = self.describe_image(image_info.image_path)
            image_info.description = description
        else:
            description = image_info.description

        # Embed the description
        embedding = self.text_embedder.embed_text(description)
        return embedding

    def embed_image_batch(self, image_infos: List[ImageInfo]) -> List[List[float]]:
        """Generate embeddings for multiple images"""
        embeddings = []

        for image_info in image_infos:
            embedding = self.embed_image(image_info)
            embeddings.append(embedding)

        return embeddings

    def describe_batch(self, image_paths: List[str]) -> List[str]:
        """Describe multiple images"""
        descriptions = []

        for image_path in image_paths:
            description = self.describe_image(image_path)
            descriptions.append(description)

        return descriptions
