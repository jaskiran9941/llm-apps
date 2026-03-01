"""
app.py — Level 1: Streamlit UI

A simple chat interface that talks to the agent.
The key thing to notice: messages = [] is a session-scoped list.
Refresh the page → it resets → the agent forgets everything.
That's the wall you'll hit at the end of this level.
"""

import streamlit as st
import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Note-Taker — Level 1: Agent with Tools",
    page_icon="📝",
    layout="centered"
)

st.title("📝 Level 1: Agent with Tools")
st.caption("Claude decides when to use tools. You just chat.")

# ── Sidebar: learning guide ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🎓 What to observe")
    st.markdown("""
    **Watch Claude decide:**
    - Does it use a tool? Which one?
    - How many API calls happen per message?
    - When does it respond without using any tool?

    **Try these in order:**
    1. "Save a note titled 'Product Strategy' about focusing on enterprise customers"
    2. "What notes do I have?"
    3. "Read my product strategy note"
    4. "Delete the product strategy note"

    **Then hit the wall:**
    - Click **New Session** below
    - Ask "what did I note earlier?"
    - Watch it fail — it has no idea
    - Notes are still on disk, but the *memory* is gone
    """)

    st.divider()
    st.header("⚙️ Session controls")

    if st.button("🔄 New Session (forget everything)", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.success("Session cleared. Notes still on disk, but agent forgot the conversation.")
        st.rerun()

    # Show raw messages for learning purposes
    if st.checkbox("Show raw message history"):
        st.caption("This is what Claude sees on each API call:")
        st.json(st.session_state.get("messages", []))

# ── Session state ─────────────────────────────────────────────────────────────
# messages: the raw API-format conversation history (sent to Claude)
# chat_history: the display-format history (shown in UI)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Chat display ──────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Talk to your note-taking agent..."):

    # Show user message immediately
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Run the agent (this may make multiple Claude API calls)
    with st.chat_message("assistant"):
        with st.spinner("Agent thinking..."):
            response_text, st.session_state.messages = run_agent(
                prompt,
                st.session_state.messages
            )
        st.write(response_text)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_text
    })
