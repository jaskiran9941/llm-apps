"""
tools.py — Level 2: Tools with storage + knowledge integration

What changed from Level 1:
  - save_note: also indexes the note in ChromaDB
  - delete_note: also removes from ChromaDB index
  - NEW tool: search_notes — semantic search via ChromaDB

Everything else (schemas format, execute_tool dispatcher) is identical to Level 1.
This is intentional — the agent loop doesn't change, only the tools do.
"""

import json
import os
from datetime import datetime
import knowledge  # ChromaDB integration from this folder

NOTES_DIR = os.path.join(os.path.dirname(__file__), "notes")
os.makedirs(NOTES_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# TOOL SCHEMAS (what Claude sees)
# ─────────────────────────────────────────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "name": "save_note",
        "description": "Save a new note. Also indexes it for semantic search so it can be found by meaning later.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "A short, descriptive title"},
                "content": {"type": "string", "description": "The full content of the note"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "list_notes",
        "description": "List all saved notes with titles, dates, and tags.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "read_note",
        "description": "Read the full content of a specific note by title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the note to read"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "delete_note",
        "description": "Permanently delete a note by title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the note to delete"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "search_notes",
        "description": "Search notes by meaning, not just keywords. Use this when the user asks to find notes about a topic, concept, or idea. Better than list_notes for discovery.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for, described naturally"
                }
            },
            "required": ["query"]
        }
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS (what Python runs)
# ─────────────────────────────────────────────────────────────────────────────

def save_note(title: str, content: str, tags: list = None) -> str:
    note = {
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().isoformat()
    }
    filename = f"{title.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(NOTES_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(note, f, indent=2)

    # Level 2: also index in ChromaDB
    knowledge.add_note(title, content, tags)

    return f"✓ Note '{title}' saved and indexed for semantic search."


def list_notes() -> str:
    files = [f for f in os.listdir(NOTES_DIR) if f.endswith('.json')]
    if not files:
        return "No notes found."

    notes = []
    for filename in sorted(files):
        with open(os.path.join(NOTES_DIR, filename)) as f:
            note = json.load(f)
        date = note.get('created_at', '')[:10]
        tags = ', '.join(note.get('tags', [])) or 'no tags'
        notes.append(f"• {note['title']} — {date} [{tags}]")

    return f"Found {len(notes)} note(s):\n" + "\n".join(notes)


def read_note(title: str) -> str:
    filename = f"{title.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(NOTES_DIR, filename)

    if not os.path.exists(filepath):
        for f in os.listdir(NOTES_DIR):
            if not f.endswith('.json'):
                continue
            with open(os.path.join(NOTES_DIR, f)) as fp:
                note = json.load(fp)
            if note['title'].lower() == title.lower():
                return _format_note(note)
        return f"Note '{title}' not found."

    with open(filepath) as f:
        note = json.load(f)
    return _format_note(note)


def delete_note(title: str) -> str:
    filename = f"{title.replace(' ', '_').replace('/', '-')}.json"
    filepath = os.path.join(NOTES_DIR, filename)

    if not os.path.exists(filepath):
        for f in os.listdir(NOTES_DIR):
            if not f.endswith('.json'):
                continue
            full_path = os.path.join(NOTES_DIR, f)
            with open(full_path) as fp:
                note = json.load(fp)
            if note['title'].lower() == title.lower():
                os.remove(full_path)
                knowledge.remove_note(title)  # Level 2: also remove from index
                return f"✓ Note '{title}' deleted."
        return f"Note '{title}' not found."

    os.remove(filepath)
    knowledge.remove_note(title)
    return f"✓ Note '{title}' deleted."


def search_notes(query: str) -> str:
    """New in Level 2: semantic search via ChromaDB."""
    return knowledge.search_notes(query)


def _format_note(note: dict) -> str:
    date = note.get('created_at', '')[:10]
    tags = ', '.join(note.get('tags', [])) or 'none'
    return f"Title: {note['title']}\nDate: {date}\nTags: {tags}\n\n{note['content']}"


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "save_note":
        return save_note(**tool_input)
    elif tool_name == "list_notes":
        return list_notes()
    elif tool_name == "read_note":
        return read_note(**tool_input)
    elif tool_name == "delete_note":
        return delete_note(**tool_input)
    elif tool_name == "search_notes":
        return search_notes(**tool_input)
    else:
        return f"Unknown tool: {tool_name}"
