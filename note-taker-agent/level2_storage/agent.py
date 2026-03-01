"""
agent.py — Level 2: Agent with session persistence

What changed from Level 1:
  - Accepts session_id so it knows where to save messages
  - After each completed exchange, saves user message + final response to SQLite

What did NOT change:
  - The agent loop is identical to Level 1 (while True, stop_reason, tool_use)
  - The tool calling mechanism is identical

Key insight: persistence is added AROUND the loop, not inside it.
The loop itself doesn't know or care about SQLite. It just runs.
"""

import anthropic
from dotenv import load_dotenv, find_dotenv
import storage
from tools import TOOL_SCHEMAS, execute_tool

load_dotenv(find_dotenv())

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a helpful note-taking assistant with two capabilities:
1. Save, list, read, and delete notes
2. Search notes semantically — find notes by meaning, not just exact title

When to use which tool:
- save_note: user wants to capture something
- list_notes: user wants to see all notes
- read_note: user wants to see a specific note
- delete_note: user wants to remove a note
- search_notes: user wants to FIND notes about a topic (use this over list_notes for discovery)

Be concise and friendly. You now remember previous conversations."""


def run_agent(user_message: str, messages: list, session_id: str) -> tuple[str, list]:
    """
    Run one turn of the agent loop.

    Args:
        user_message: What the user just said
        messages: Conversation history (may include messages loaded from SQLite)
        session_id: Used to save this exchange to the DB

    The loop is identical to Level 1.
    The only addition is the save_message calls at the end.
    """
    messages.append({"role": "user", "content": user_message})

    # ── THE AGENT LOOP (identical to Level 1) ────────────────────────────────
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_use_block = next(
                block for block in response.content
                if block.type == "tool_use"
            )

            tool_result = execute_tool(tool_use_block.name, tool_use_block.input)

            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": tool_result
                }]
            })
            continue

        else:
            final_text = next(
                (block.text for block in response.content if hasattr(block, 'text')),
                "Done."
            )
            messages.append({"role": "assistant", "content": response.content})

            # ── Level 2 addition: persist the exchange to SQLite ─────────────
            # We save clean text only (not tool_use blocks).
            # When loaded next session, Claude sees a clean conversation history.
            storage.save_message(session_id, "user", user_message)
            storage.save_message(session_id, "assistant", final_text)

            return final_text, messages
