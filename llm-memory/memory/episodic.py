from typing import List, Dict
from datetime import datetime
from config.config import MAX_CONVERSATION_HISTORY

class EpisodicMemory:
    """Manages conversation history (episodic memory)."""

    def __init__(self, max_history: int = MAX_CONVERSATION_HISTORY):
        self.max_history = max_history
        self.conversation_turns = []

    def add_turn(self, user_message: str, assistant_response: str, tokens_used: int = 0):
        """Add a conversation turn to episodic memory."""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "tokens_used": tokens_used
        }
        self.conversation_turns.append(turn)

        # Keep only max_history turns (sliding window)
        if len(self.conversation_turns) > self.max_history:
            self.conversation_turns = self.conversation_turns[-self.max_history:]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history in Claude API format.

        Returns:
            List of message dicts: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        messages = []
        for turn in self.conversation_turns:
            messages.append({
                "role": "user",
                "content": turn["user_message"]
            })
            messages.append({
                "role": "assistant",
                "content": turn["assistant_response"]
            })
        return messages

    def get_turns(self) -> List[Dict]:
        """Get raw conversation turns with metadata."""
        return self.conversation_turns

    def get_total_tokens(self) -> int:
        """Calculate total tokens used in stored conversation."""
        return sum(turn["tokens_used"] for turn in self.conversation_turns)

    def get_context_length(self) -> int:
        """Estimate context length from all stored turns."""
        total_length = 0
        for turn in self.conversation_turns:
            total_length += len(turn["user_message"]) + len(turn["assistant_response"])
        return total_length // 4  # Rough token estimate (4 chars per token)

    def clear(self):
        """Clear all conversation history."""
        self.conversation_turns = []

    def __len__(self):
        return len(self.conversation_turns)
