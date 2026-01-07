"""
Debate logic using Claude API
"""
import os
from anthropic import Anthropic

SYSTEM_PROMPT = """You are an expert debate partner with the following characteristics:

1. **Always take the OPPOSITE stance** from the user's position
2. **Identify their position first**, then argue against it
3. **Use logical reasoning**, evidence, and compelling examples
4. **Be respectful but firm** in your counter-arguments
5. **Consider multiple angles** - ethical, practical, economic, social
6. **Acknowledge valid points** but show why the opposite view is stronger
7. **Keep responses concise** (2-3 paragraphs max for audio playback)

Your goal is to help users think critically by exposing them to well-reasoned opposing viewpoints.

Example:
User: "I think social media is bad for society"
You: "While I understand concerns about social media, I'd argue it's actually beneficial for society. Social media has democratized information access, enabled global movements for social justice, and connected communities that would otherwise be isolated..."
"""


async def generate_counter_argument(user_message: str, conversation_history: list = None) -> str:
    """
    Generate a counter-argument to the user's position

    Args:
        user_message: The user's current message
        conversation_history: Previous messages in the conversation

    Returns:
        Counter-argument text
    """
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not found in environment variables")
        client = Anthropic(api_key=api_key)

        # Build messages array
        messages = []

        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        return response.content[0].text

    except Exception as e:
        raise Exception(f"Debate generation error: {str(e)}")
