"""
agent.py — Level 1: The Agent Loop

This is the core of all agentic software. Read this carefully.

The fundamental pattern:
  1. Send user message to Claude (with available tools)
  2. Claude responds with EITHER:
     a. A tool call (stop_reason == "tool_use") → execute the tool, feed result back, repeat
     b. A final answer (stop_reason == "end_turn") → return the text, we're done

The loop runs until Claude decides it's done. You don't control when it stops.
That's what makes it an agent: Claude drives the control flow, not your code.
"""

import os
import anthropic
from dotenv import load_dotenv
from tools import TOOL_SCHEMAS, execute_tool

# Load ANTHROPIC_API_KEY from .env file if it exists
load_dotenv()

# Initialize the Anthropic client.
# It reads ANTHROPIC_API_KEY from environment automatically.
client = anthropic.Anthropic()

# The system prompt tells Claude its role and when to use tools.
# This is injected at the start of every API call.
SYSTEM_PROMPT = """You are a helpful note-taking assistant. You help users save, organize, and retrieve their notes.

Guidelines:
- When users want to capture information → use save_note
- When users ask what notes exist → use list_notes
- When users want to see a specific note → use read_note
- When users want to remove a note → use delete_note
- For casual conversation, just respond directly without using tools

Be concise and friendly. If you're unsure which note the user means, ask for clarification."""


def run_agent(user_message: str, messages: list) -> tuple[str, list]:
    """
    Run one turn of the agent loop.

    Args:
        user_message: What the user just said
        messages: The conversation history so far (will be mutated)

    Returns:
        (final_response_text, updated_messages)

    This function may call the Claude API multiple times in a single turn —
    once for each tool call Claude decides to make. The user sees only the
    final response, but multiple API calls may happen under the hood.
    """
    # Add the user's message to conversation history
    messages.append({"role": "user", "content": user_message})

    # ─────────────────────────────────────────────────────────────────────────
    # THE AGENT LOOP
    # This while True runs until Claude says "end_turn" (no more tool calls).
    # ─────────────────────────────────────────────────────────────────────────
    while True:

        # Send the full conversation history to Claude along with available tools
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        # ── BRANCH 1: Claude wants to call a tool ────────────────────────────
        if response.stop_reason == "tool_use":

            # Add Claude's response to history (it contains the tool call intent)
            messages.append({"role": "assistant", "content": response.content})

            # Find the tool_use block in the response
            # (There could be multiple, but we'll handle one at a time for clarity)
            tool_use_block = next(
                block for block in response.content
                if block.type == "tool_use"
            )

            # Execute the actual Python function
            tool_result = execute_tool(tool_use_block.name, tool_use_block.input)

            # Feed the result back to Claude as a "tool_result" message
            # Claude needs to see what happened before it can respond
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,  # Must match the tool call ID
                    "content": tool_result
                }]
            })

            # Loop again — Claude will now react to the tool result
            # (It might call another tool, or it might give a final answer)
            continue

        # ── BRANCH 2: Claude is done (no more tool calls) ────────────────────
        else:
            # stop_reason == "end_turn" means Claude has finished
            # Extract the text from the response
            final_text = next(
                (block.text for block in response.content if hasattr(block, 'text')),
                "Done."
            )
            # Add final response to history
            messages.append({"role": "assistant", "content": response.content})
            return final_text, messages
