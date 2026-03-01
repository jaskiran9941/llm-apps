"""
app.py — Level 2: Streamlit UI with session persistence

What changed from Level 1:
  - Session ID created on first load (UUID per browser session)
  - On startup: loads last 20 messages from SQLite → agent has context
  - "New Session" no longer makes the agent forget — just starts fresh UI
    but the SQLite history carries over

The wall you'll hit:
  Tell it "I always prefer notes in bullet point format"
  Click New Session
  Ask it to save a note without specifying format
  It won't use bullet points — it has no user model, just conversation history
  That preference is buried in old messages, not extracted or stored as a fact
"""

import streamlit as st
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent
import storage

st.set_page_config(
    page_title="Note-Taker — Level 2: Storage + Knowledge",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Level 2: Storage + Knowledge")
st.caption("Remembers across sessions. Searches by meaning.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🎓 What's new in L2")
    st.markdown("""
    **Two additions to Level 1:**

    **1. SQLite (storage.py)**
    Every exchange saved to a DB file.
    New session? Last 20 messages loaded back.
    Agent has conversational continuity.

    **2. ChromaDB (knowledge.py)**
    Notes embedded as vectors on save.
    New tool: `search_notes` — finds notes
    by meaning, not exact keywords.

    ---
    **Try the new behavior:**
    1. Save 3 notes on different topics
    2. Click "New Session"
    3. Ask "what have we discussed?" → it knows
    4. Ask "find notes about [topic]" → semantic match

    ---
    **Then hit the wall:**
    - Say "I prefer notes in bullet points"
    - New Session → ask to save a note
    - Watch it ignore your preference
    - It has conversation history, not a user model
    """)

    st.divider()

    # Session info
    session_id = st.session_state.get("session_id", "not started")
    st.caption(f"Session ID: `{session_id[:8]}...`")

    sessions = storage.list_sessions()
    if sessions:
        st.caption(f"Total sessions in DB: {len(sessions)}")
        st.caption(f"Most recent: {sessions[0]['last_active'][:16]}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.history_loaded = False
            st.rerun()

    with col2:
        if st.button("🗑️ Wipe DB", use_container_width=True):
            db_path = os.path.join(os.path.dirname(__file__), "sessions.db")
            if os.path.exists(db_path):
                os.remove(db_path)
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.session_state.history_loaded = False
            st.rerun()

    if st.checkbox("Show raw message history"):
        st.json(st.session_state.get("messages", []))

# ── Session state init ────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

# ── Load history from SQLite on first run ────────────────────────────────────
# This is what Level 2 adds vs Level 1: inject prior conversation into messages
if not st.session_state.history_loaded:
    sessions = storage.list_sessions()
    if sessions:
        most_recent_id = sessions[0]["session_id"]
        prior_messages = storage.load_recent_messages(most_recent_id, limit=20)
        if prior_messages:
            st.session_state.messages = prior_messages
            st.info(
                f"Loaded {len(prior_messages)} messages from your last session. "
                f"The agent remembers your previous conversation."
            )
    st.session_state.history_loaded = True

# ── Chat display ──────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Chat with your note-taking agent..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text, st.session_state.messages = run_agent(
                prompt,
                st.session_state.messages,
                st.session_state.session_id
            )
        st.write(response_text)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_text
    })
