"""
Gemini-powered tone and personality analyzer.
"""

import json
from typing import Optional
from dataclasses import dataclass, field
import google.generativeai as genai


@dataclass
class ToneAnalysis:
    """Tone analysis for a single utterance."""
    primary_tone: str
    secondary_tone: Optional[str]
    energy_level: str  # low, medium, high
    emotional_state: str
    communication_style: str
    confidence: float


@dataclass
class PersonalityProfile:
    """Personality profile built from conversation."""
    communication_style: str
    emotional_expression: str
    conflict_approach: str
    listening_style: str
    focus_orientation: str
    key_traits: list[str]
    summary: str


@dataclass
class SpeakerAnalysis:
    """Complete analysis for a speaker."""
    speaker_id: int
    latest_tone: Optional[ToneAnalysis] = None
    personality: Optional[PersonalityProfile] = None
    utterance_count: int = 0
    tone_history: list[str] = field(default_factory=list)


class ConversationAnalyzer:
    """Analyzes conversation tone and personality using Gemini."""

    TONE_CATEGORIES = [
        "calm", "warm", "enthusiastic", "neutral",
        "frustrated", "anxious", "defensive", "dismissive",
        "aggressive", "passive", "passive-aggressive", "assertive",
        "supportive", "critical", "sarcastic", "empathetic",
        "curious", "confused", "excited", "tired"
    ]

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use gemini-2.0-flash which is available and fast
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        print(f"[Analyzer] Initialized with model: gemini-2.0-flash", flush=True)
        self.speakers: dict[int, SpeakerAnalysis] = {}
        self.conversation_history: list[dict] = []

    def analyze_tone(self, text: str, speaker_id: int) -> ToneAnalysis:
        """Analyze the tone of a single utterance."""
        print(f"[Analyzer] Analyzing: Speaker {speaker_id}: '{text[:80]}...'", flush=True)

        # Initialize speaker if new
        if speaker_id not in self.speakers:
            self.speakers[speaker_id] = SpeakerAnalysis(speaker_id=speaker_id)

        prompt = f"""Analyze the tone of this utterance from a conversation.

Utterance: "{text}"

Respond with ONLY a JSON object (no markdown, no code blocks):
{{
    "primary_tone": "<one of: {', '.join(self.TONE_CATEGORIES)}>",
    "secondary_tone": "<optional secondary tone or null>",
    "energy_level": "<low/medium/high>",
    "emotional_state": "<brief description of emotional state>",
    "communication_style": "<direct/indirect/assertive/passive/aggressive>",
    "confidence": <0.0-1.0 confidence in analysis>
}}"""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            tone = ToneAnalysis(
                primary_tone=result.get("primary_tone", "neutral"),
                secondary_tone=result.get("secondary_tone"),
                energy_level=result.get("energy_level", "medium"),
                emotional_state=result.get("emotional_state", ""),
                communication_style=result.get("communication_style", "direct"),
                confidence=result.get("confidence", 0.5),
            )

            # Update speaker data
            self.speakers[speaker_id].latest_tone = tone
            self.speakers[speaker_id].utterance_count += 1
            self.speakers[speaker_id].tone_history.append(tone.primary_tone)

            # Add to conversation history
            self.conversation_history.append({
                "speaker": speaker_id,
                "text": text,
                "tone": tone.primary_tone,
            })

            return tone

        except Exception as e:
            print(f"Error analyzing tone: {e}")
            return ToneAnalysis(
                primary_tone="neutral",
                secondary_tone=None,
                energy_level="medium",
                emotional_state="unknown",
                communication_style="direct",
                confidence=0.0,
            )

    def analyze_personality(self, speaker_id: int) -> Optional[PersonalityProfile]:
        """Analyze personality based on conversation history."""
        if speaker_id not in self.speakers:
            return None

        speaker = self.speakers[speaker_id]
        if speaker.utterance_count < 3:
            return None  # Need more data

        # Gather this speaker's utterances
        speaker_utterances = [
            entry for entry in self.conversation_history
            if entry["speaker"] == speaker_id
        ]

        if not speaker_utterances:
            return None

        conversation_text = "\n".join([
            f"- \"{entry['text']}\" (tone: {entry['tone']})"
            for entry in speaker_utterances[-15:]  # Last 15 utterances
        ])

        tone_summary = ", ".join(speaker.tone_history[-10:])

        prompt = f"""Based on this person's utterances in a conversation, analyze their personality and communication style.

Their recent utterances:
{conversation_text}

Their recent tones: {tone_summary}

Respond with ONLY a JSON object (no markdown, no code blocks):
{{
    "communication_style": "<Direct/Indirect/Diplomatic/Blunt/Thoughtful>",
    "emotional_expression": "<Expressive/Reserved/Balanced/Variable>",
    "conflict_approach": "<Confrontational/Avoidant/Collaborative/Competitive>",
    "listening_style": "<Active/Passive/Interruptive/Patient>",
    "focus_orientation": "<Solution-focused/Feeling-focused/Detail-focused/Big-picture>",
    "key_traits": ["<trait1>", "<trait2>", "<trait3>"],
    "summary": "<2-3 sentence personality summary>"
}}"""

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            profile = PersonalityProfile(
                communication_style=result.get("communication_style", "Direct"),
                emotional_expression=result.get("emotional_expression", "Balanced"),
                conflict_approach=result.get("conflict_approach", "Collaborative"),
                listening_style=result.get("listening_style", "Active"),
                focus_orientation=result.get("focus_orientation", "Balanced"),
                key_traits=result.get("key_traits", []),
                summary=result.get("summary", ""),
            )

            self.speakers[speaker_id].personality = profile
            return profile

        except Exception as e:
            print(f"Error analyzing personality: {e}")
            return None

    def get_conversation_dynamics(self) -> dict:
        """Analyze overall conversation dynamics between speakers."""
        if len(self.speakers) < 2 or len(self.conversation_history) < 6:
            return {}

        # Build conversation excerpt
        recent_exchanges = self.conversation_history[-20:]
        conversation_text = "\n".join([
            f"Speaker {entry['speaker']}: \"{entry['text']}\" [{entry['tone']}]"
            for entry in recent_exchanges
        ])

        prompt = f"""Analyze the dynamics of this conversation between two people.

Recent exchanges:
{conversation_text}

Respond with ONLY a JSON object (no markdown, no code blocks):
{{
    "overall_mood": "<positive/negative/neutral/tense/warm>",
    "balance": "<balanced/one-sided/back-and-forth>",
    "tension_level": "<low/medium/high>",
    "connection_quality": "<strong/moderate/weak/strained>",
    "dominant_speaker": <speaker_id or null if balanced>,
    "interaction_pattern": "<collaborative/competitive/supportive/conflictual>",
    "advice": "<brief advice for improving the conversation>"
}}"""

        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            print(f"Error analyzing dynamics: {e}")
            return {}

    def get_speaker(self, speaker_id: int) -> Optional[SpeakerAnalysis]:
        """Get analysis for a specific speaker."""
        return self.speakers.get(speaker_id)

    def get_all_speakers(self) -> dict[int, SpeakerAnalysis]:
        """Get all speaker analyses."""
        return self.speakers

    def reset(self):
        """Reset all analysis data."""
        self.speakers = {}
        self.conversation_history = []

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from Gemini response, handling common issues."""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last lines (```json and ```)
            text = "\n".join(lines[1:-1])

        # Try to find JSON object
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)

        return {}
