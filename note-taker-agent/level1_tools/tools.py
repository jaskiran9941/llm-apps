"""
tools.py — Level 1: Tool definitions and implementations

This file has two jobs:
1. Define TOOL_SCHEMAS — the JSON that tells Claude what tools exist and what they take
2. Implement the actual Python functions that execute when Claude calls a tool

Key insight: Tool schemas are NOT the same as tool implementations.
The schema is for Claude (so it can decide what to call).
The implementation is for Python (so you can actually do the work).
"""

import json
import os
from datetime import datetime

# Where notes live on disk
NOTES_DIR = os.path.join(os.path.dirname(__file__), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# TOOL SCHEMAS
# These are sent to Claude in every API call. Claude reads them to understand
# what actions it can take. The structure must follow Anthropic's format exactly.
# ─────────────────────────────────────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "save_note",
        "description": "Save a new note with a title and content. Use this when the user wants to capture information, ideas, or meeting notes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A short, descriptive title for the note"
                },
                "content": {
                    "type": "string",
                    "description": "The full content/body of the note"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of tags to categorize the note (e.g. ['meeting', 'product'])"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "list_notes",
        "description": "List all saved notes with their titles, dates, and tags. Use this when the user wants to see what notes exist.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "read_note",
        "description": "Read the full content of a specific note by its title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The exact title of the note to read"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "delete_note",
        "description": "Permanently delete a note by its title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The exact title of the note to delete"
                }
            },
            "required": ["title"]
        }
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# Pure Python functions. No Claude involved. Just file operations.
# ─────────────────────────────────────────────────────────────────────────────

def save_note(title: str, content: str, tags: list = None) -> str:
    """Save a note as a JSON file."""
    note = {
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().isoformat()
    }
    # Use title as filename (replace spaces with underscores)
    filename = f"{title.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(NOTES_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(note, f, indent=2)
    return f"✓ Note '{title}' saved successfully."


def list_notes() -> str:
    """List all notes with their metadata."""
    files = [f for f in os.listdir(NOTES_DIR) if f.endswith('.json')]
    if not files:
        return "No notes found. Save your first note!"

    notes = []
    for filename in sorted(files):
        filepath = os.path.join(NOTES_DIR, filename)
        with open(filepath) as f:
            note = json.load(f)
        date = note.get('created_at', '')[:10]
        tags = ', '.join(note.get('tags', [])) or 'no tags'
        notes.append(f"• {note['title']} — {date} [{tags}]")

    return f"Found {len(notes)} note(s):\n" + "\n".join(notes)


def read_note(title: str) -> str:
    """Read a note's full content. Tries exact match first, then case-insensitive."""
    # Try exact filename match
    filename = f"{title.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(NOTES_DIR, filename)

    if not os.path.exists(filepath):
        # Try case-insensitive search across all notes
        for f in os.listdir(NOTES_DIR):
            if not f.endswith('.json'):
                continue
            with open(os.path.join(NOTES_DIR, f)) as fp:
                note = json.load(fp)
            if note['title'].lower() == title.lower():
                return _format_note(note)
        return f"Note '{title}' not found. Use 'list notes' to see available notes."

    with open(filepath) as f:
        note = json.load(f)
    return _format_note(note)


def delete_note(title: str) -> str:
    """Delete a note file."""
    filename = f"{title.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(NOTES_DIR, filename)

    if not os.path.exists(filepath):
        # Try case-insensitive search
        for f in os.listdir(NOTES_DIR):
            if not f.endswith('.json'):
                continue
            full_path = os.path.join(NOTES_DIR, f)
            with open(full_path) as fp:
                note = json.load(fp)
            if note['title'].lower() == title.lower():
                os.remove(full_path)
                return f"✓ Note '{title}' deleted."
        return f"Note '{title}' not found."

    os.remove(filepath)
    return f"✓ Note '{title}' deleted."


def _format_note(note: dict) -> str:
    """Format a note dict for display."""
    date = note.get('created_at', '')[:10]
    tags = ', '.join(note.get('tags', [])) or 'none'
    return f"Title: {note['title']}\nDate: {date}\nTags: {tags}\n\n{note['content']}"


# ─────────────────────────────────────────────────────────────────────────────
# TOOL DISPATCHER
# Routes Claude's tool calls to the right Python function.
# Called by the agent loop in agent.py.
# ─────────────────────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name with the given inputs. Returns result as string."""
    if tool_name == "save_note":
        return save_note(**tool_input)
    elif tool_name == "list_notes":
        return list_notes()
    elif tool_name == "read_note":
        return read_note(**tool_input)
    elif tool_name == "delete_note":
        return delete_note(**tool_input)
    else:
        return f"Unknown tool: {tool_name}"
