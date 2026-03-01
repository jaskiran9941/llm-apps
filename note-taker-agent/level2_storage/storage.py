"""
storage.py — Level 2: SQLite session persistence

What this solves from Level 1's wall:
  Before: messages = [] reset on every session → agent forgot everything
  After:  every exchange saved to DB → new session loads it back in

Why SQLite?
- Built into Python (no install needed)
- File-based (you can open sessions.db in any SQLite viewer and see the data)
- More than enough for a single-user local agent

The table is simple: session_id, role, content, timestamp.
Each row is one message (user or assistant).
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "sessions.db")


def init_db():
    """Create the messages table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            timestamp   TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_message(session_id: str, role: str, content: str):
    """
    Save one message to the database.

    We only save clean text (user message + final assistant response).
    We do NOT save the intermediate tool_use blocks — those are internal
    plumbing that Claude doesn't need to see when reconstructing context.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def load_recent_messages(session_id: str, limit: int = 20) -> list:
    """
    Load the last N messages for a session, in chronological order.

    These get injected into the messages list at session start.
    Claude reads them as prior conversation context.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT role, content FROM messages
           WHERE session_id = ?
           ORDER BY id DESC LIMIT ?""",
        (session_id, limit)
    )
    rows = c.fetchall()
    conn.close()

    # Reverse: we fetched newest-first, need oldest-first for the messages list
    return [{"role": role, "content": content} for role, content in reversed(rows)]


def list_sessions() -> list:
    """List all sessions with message counts, newest first."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT session_id, COUNT(*) as count, MAX(timestamp) as last_active
        FROM messages
        GROUP BY session_id
        ORDER BY last_active DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {"session_id": r[0], "message_count": r[1], "last_active": r[2]}
        for r in rows
    ]
