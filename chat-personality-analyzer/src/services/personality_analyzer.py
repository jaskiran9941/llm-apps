"""Personality Analyzer Service using Gemini Vision."""

import json
import re
from typing import List, Dict, Any
from pathlib import Path
from PIL import Image
import google.generativeai as genai


class PersonalityAnalyzer:
    """Analyzes conversation screenshots to extract personalities and provide advice."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        """Initialize the analyzer with Gemini API."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def analyze_screenshots(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Main analysis pipeline for conversation screenshots.

        Args:
            image_paths: List of paths to screenshot images

        Returns:
            Dictionary containing extracted text, personalities, and advice
        """
        # Step 1: Extract conversation text from all screenshots
        extracted_text = self._extract_conversation(image_paths)

        # Step 2: Analyze personalities
        personalities = self._analyze_personalities(extracted_text)

        # Step 3: Generate approach advice
        advice = self._generate_advice(personalities)

        return {
            "extracted_text": extracted_text,
            "personalities": personalities,
            "advice": advice
        }

    def _extract_conversation(self, image_paths: List[str]) -> str:
        """Extract conversation text from screenshots using Gemini Vision."""
        images = [Image.open(path) for path in image_paths]

        prompt = """Extract ALL text from this conversation screenshot(s).
Identify each unique speaker and their messages.

Return in this exact format:
[Speaker Name]: message text
[Speaker Name]: message text
...

Important:
- Preserve chronological order across all screenshots
- Include timestamps if visible
- Identify speakers by their displayed name, profile picture position, or message bubble color/side
- If speaker names aren't visible, use descriptive identifiers like "Left Speaker" and "Right Speaker" or "Blue Bubble" and "Gray Bubble"
- Extract EVERY message visible in the screenshots"""

        content = [prompt] + images
        response = self.model.generate_content(content)

        return response.text

    def _analyze_personalities(self, extracted_text: str) -> Dict[str, Dict[str, Any]]:
        """Analyze personality traits of each conversation participant."""
        prompt = f"""Analyze each participant's personality from this conversation:

{extracted_text}

For each unique speaker, determine:
1. Communication Style: Are they direct or indirect? Formal or casual? Verbose or concise? Do they use emojis/slang?
2. Personality Traits: List 3-5 key traits (e.g., analytical, empathetic, assertive, humorous, reserved, enthusiastic)
3. Values & Interests: What do they seem to care about based on their messages?
4. Emotional Tendency: Are they calm, reactive, supportive, guarded, expressive?
5. Conversation Role: Are they leading the conversation, responding, mediating, etc.?

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
  "Person Name": {{
    "communication_style": {{
      "directness": "direct/indirect",
      "formality": "formal/casual/mixed",
      "verbosity": "verbose/concise/moderate",
      "emoji_usage": "frequent/occasional/rare/none"
    }},
    "personality_traits": ["trait1", "trait2", "trait3"],
    "values_interests": ["value1", "value2"],
    "emotional_tendency": "description of emotional patterns",
    "conversation_role": "their role in the conversation"
  }}
}}"""

        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)

    def _generate_advice(self, personalities: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate approach advice for each person based on their personality."""
        prompt = f"""Based on these personality profiles:

{json.dumps(personalities, indent=2)}

Provide specific, actionable advice for how to approach and communicate with each person effectively.

For each person include:
1. Best Communication Approach: How should you phrase things? What tone works best?
2. Topics to Focus On: What subjects or approaches will resonate with them?
3. Things to Avoid: What might put them off or cause friction?
4. Building Rapport: Specific tips for connecting with this person
5. Key Insight: One crucial thing to remember when interacting with them

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
  "Person Name": {{
    "communication_approach": "detailed advice on how to communicate",
    "topics_to_focus_on": ["topic1", "topic2"],
    "things_to_avoid": ["avoid1", "avoid2"],
    "building_rapport": "specific rapport-building tips",
    "key_insight": "the most important thing to remember"
  }}
}}"""

        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from Gemini response, handling potential formatting issues."""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Return error structure if parsing fails
            return {"error": "Failed to parse response", "raw_text": text}
