"""
Agent vs Skills Demo — Interactive Streamlit app.

Three tabs:
1. Skill Mode: Manual skill selection, one-shot LLM calls
2. Agent Mode: Autonomous orchestration with reasoning trace
3. Learn: Educational content explaining the difference
"""

import os
import json

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from skills import SKILLS, apply_skill, list_skills
from agent import SkillAgent

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Agent vs Skills Demo",
    page_icon="🤖",
    layout="wide",
)

# ── Helper functions ─────────────────────────────────────────────────────────

def get_client():
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar.")
        st.stop()
    return OpenAI(api_key=api_key)


def render_trace(trace, total_tokens, skills_used):
    """Render the agent's reasoning trace in an expander."""
    with st.expander(f"Reasoning Trace — {len(trace)} steps, {total_tokens} tokens"):
        if skills_used:
            st.markdown(f"**Skills used:** {', '.join(skills_used)}")

        for step in trace:
            st.markdown(f"---\n**Step {step['iteration']}** — {step['action']}")

            if step.get("tokens"):
                st.caption(f"Tokens this step: {step['tokens']}")

            for tc in step.get("tool_calls", []):
                st.markdown(f"Tool: `{tc['tool']}`")
                st.json(tc["args"])
                with st.expander("Tool result"):
                    st.json(tc["result"])

        st.metric("Total Tokens", total_tokens)


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Agent vs Skills Demo")
    st.caption("See how skills and agents differ")

    st.divider()

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key or set OPENAI_API_KEY in .env",
    )

    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0,
        help="gpt-4o-mini is cheaper and good enough for this demo",
    )

    st.divider()
    st.subheader("Example Queries")

    example_categories = {
        "Code Review": "Review this code for security issues:\n```python\nquery = \"SELECT * FROM users WHERE id = '\" + user_input + \"'\"\ncursor.execute(query)\n```",
        "Research": "Compare REST vs GraphQL for mobile applications",
        "Data Analysis": "How would I find duplicate customers in a pandas DataFrame?",
        "Email": "Draft a follow-up email after a client meeting about a new project proposal",
    }

    for label, query in example_categories.items():
        if st.button(f"{label}", key=f"example_{label}", use_container_width=True):
            st.session_state["example_query"] = query

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Skill Chat", use_container_width=True):
            st.session_state["skill_messages"] = []
            st.rerun()
    with col2:
        if st.button("Clear Agent Chat", use_container_width=True):
            st.session_state["agent_messages"] = []
            st.session_state["agent_history"] = []
            st.rerun()


# ── Session state init ───────────────────────────────────────────────────────

if "skill_messages" not in st.session_state:
    st.session_state["skill_messages"] = []
if "agent_messages" not in st.session_state:
    st.session_state["agent_messages"] = []
if "agent_history" not in st.session_state:
    st.session_state["agent_history"] = []


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_skill, tab_agent, tab_learn = st.tabs(["Skill Mode", "Agent Mode", "Learn"])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1: SKILL MODE
# ═══════════════════════════════════════════════════════════════════════════

with tab_skill:
    st.header("Skill Mode — Manual Selection")
    st.caption(
        "You pick the skill, the LLM follows its prompt template. "
        "One query → one response. No tools, no loops."
    )

    skill_keys = list(SKILLS.keys())
    skill_labels = [SKILLS[k]["name"] for k in skill_keys]
    selected_idx = st.selectbox(
        "Select a skill",
        range(len(skill_keys)),
        format_func=lambda i: f"{skill_labels[i]} — {SKILLS[skill_keys[i]]['description']}",
    )
    selected_skill_key = skill_keys[selected_idx]
    selected_skill = SKILLS[selected_skill_key]

    with st.expander("View Skill Prompt (this is all a skill is — just text)"):
        st.code(selected_skill["system_prompt"], language="markdown")
        st.caption(f"Output format: {selected_skill['output_format']}")

    # Display chat history
    for msg in st.session_state["skill_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "tokens" in msg:
                st.caption(f"Tokens used: {msg['tokens']}")

    # Chat input
    skill_input = st.chat_input("Ask something using the selected skill...", key="skill_chat")

    # Handle example query
    example_q = st.session_state.pop("example_query", None)
    if example_q and not skill_input:
        skill_input = example_q

    if skill_input:
        # Show user message
        st.session_state["skill_messages"].append({"role": "user", "content": skill_input})
        with st.chat_message("user"):
            st.markdown(skill_input)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Applying skill (single LLM call)..."):
                client = get_client()
                result = apply_skill(selected_skill_key, skill_input, client, model)

            st.markdown(result["response"])
            st.caption(f"Tokens used: {result['tokens']}")

        st.session_state["skill_messages"].append({
            "role": "assistant",
            "content": result["response"],
            "tokens": result["tokens"],
        })


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2: AGENT MODE
# ═══════════════════════════════════════════════════════════════════════════

with tab_agent:
    st.header("Agent Mode — Autonomous Orchestration")
    st.caption(
        "The agent decides which skill to use, calls tools, and reasons "
        "through multiple steps. Same LLM, but with a loop."
    )

    # Display chat history
    for msg in st.session_state["agent_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "trace" in msg:
                render_trace(msg["trace"], msg.get("total_tokens", 0), msg.get("skills_used", []))

    # Chat input
    agent_input = st.chat_input("Ask anything — the agent will figure out which skill to use...", key="agent_chat")

    if agent_input:
        # Show user message
        st.session_state["agent_messages"].append({"role": "user", "content": agent_input})
        with st.chat_message("user"):
            st.markdown(agent_input)

        # Run agent
        with st.chat_message("assistant"):
            with st.spinner("Agent is reasoning (loop running)..."):
                client = get_client()
                agent = SkillAgent(client, model)
                result = agent.run(agent_input, st.session_state["agent_history"])

            st.markdown(result["final_response"])
            render_trace(result["reasoning_trace"], result["total_tokens"], result["skills_used"])

        # Update conversation history for multi-turn
        st.session_state["agent_history"].append({"role": "user", "content": agent_input})
        st.session_state["agent_history"].append({
            "role": "assistant",
            "content": result["final_response"],
        })

        st.session_state["agent_messages"].append({
            "role": "assistant",
            "content": result["final_response"],
            "trace": result["reasoning_trace"],
            "total_tokens": result["total_tokens"],
            "skills_used": result["skills_used"],
        })


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3: LEARN
# ═══════════════════════════════════════════════════════════════════════════

with tab_learn:
    st.header("Skills vs Agents — What's the Difference?")

    # Side-by-side comparison
    col_skill, col_agent = st.columns(2)

    with col_skill:
        st.subheader("Skill")
        st.markdown(
            "**What it is:** A prompt template — just text that tells the LLM "
            "how to respond.\n\n"
            "**How it works:**\n"
            "- Human selects the skill\n"
            "- One system prompt + one user query\n"
            "- One API call → one response\n"
            "- No decisions, no tools, no loops\n\n"
            "**Good for:**\n"
            "- Predictable, structured outputs\n"
            "- When you know exactly which format you need\n"
            "- Lower cost (single API call)"
        )

        st.code(
            '# Skill = single API call\n'
            'response = openai.chat.completions.create(\n'
            '    model="gpt-4o-mini",\n'
            '    messages=[\n'
            '        {"role": "system", "content": skill_prompt},\n'
            '        {"role": "user", "content": query}\n'
            '    ]\n'
            ')',
            language="python",
        )

    with col_agent:
        st.subheader("Agent")
        st.markdown(
            "**What it is:** An orchestrator that uses skills + tools + a "
            "reasoning loop to solve problems autonomously.\n\n"
            "**How it works:**\n"
            "- Agent receives the query\n"
            "- Decides which skill fits best (tool call)\n"
            "- May call additional tools (code analysis, search)\n"
            "- Loops until it has enough context\n"
            "- Produces final response\n\n"
            "**Good for:**\n"
            "- Ambiguous queries that need routing\n"
            "- Multi-step problems\n"
            "- When you don't know which skill to use"
        )

        st.code(
            '# Agent = LLM + Tools + Loop\n'
            'while not done:\n'
            '    response = openai.chat.completions.create(\n'
            '        model="gpt-4o-mini",\n'
            '        messages=messages,\n'
            '        tools=tool_schemas  # <-- key difference\n'
            '    )\n'
            '    if response.tool_calls:\n'
            '        execute_tools(response.tool_calls)\n'
            '        continue  # loop back\n'
            '    else:\n'
            '        break  # done reasoning',
            language="python",
        )

    st.divider()

    # Architecture diagrams
    st.subheader("Architecture Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Skill Mode Flow:**")
        st.code(
            "┌──────────┐    ┌───────────────┐    ┌──────────┐\n"
            "│   User   │───>│  Skill Prompt │───>│   LLM    │\n"
            "│  Query   │    │  (template)   │    │          │\n"
            "└──────────┘    └───────────────┘    └────┬─────┘\n"
            "                                          │\n"
            "                                     ┌────▼─────┐\n"
            "                                     │ Response  │\n"
            "                                     │ (1 call)  │\n"
            "                                     └──────────┘",
            language="text",
        )

    with col2:
        st.markdown("**Agent Mode Flow:**")
        st.code(
            "┌──────────┐    ┌───────────────┐    ┌──────────┐\n"
            "│   User   │───>│  Agent System │───>│   LLM    │\n"
            "│  Query   │    │   Prompt      │    │          │\n"
            "└──────────┘    └───────────────┘    └────┬─────┘\n"
            "                                          │\n"
            "                  ┌───────────────────────┘\n"
            "                  │ Tool calls?\n"
            "                  ▼ Yes\n"
            "            ┌──────────┐\n"
            "            │ Execute  │──> select_skill\n"
            "            │  Tools   │──> analyze_code\n"
            "            │          │──> search_web\n"
            "            └────┬─────┘\n"
            "                 │ Results\n"
            "                 ▼\n"
            "            ┌──────────┐\n"
            "            │ Loop back│──> LLM decides:\n"
            "            │ to LLM   │    more tools? or done?\n"
            "            └────┬─────┘\n"
            "                 │ Done\n"
            "                 ▼\n"
            "            ┌──────────┐\n"
            "            │  Final   │\n"
            "            │ Response │\n"
            "            └──────────┘",
            language="text",
        )

    st.divider()

    # Key formula
    st.subheader("The Key Formula")
    st.info("**Agent = LLM + Tools + Loop + Skills**")
    st.markdown(
        "| Component | What it does | In this demo |\n"
        "|-----------|-------------|---------------|\n"

        "| **LLM** | Reasons and generates text | GPT-4o-mini / GPT-4o |\n"
        "| **Tools** | Actions the agent can take | `select_skill`, `analyze_code`, `search_web` |\n"
        "| **Loop** | Keeps going until done | Max 5 iterations with tool call checking |\n"
        "| **Skills** | Prompt templates for specific tasks | Code Reviewer, Research Analyst, etc. |"
    )

    st.divider()

    # Quiz
    st.subheader("Quick Quiz")

    q1 = st.radio(
        "1. What is a 'skill' in the context of LLM applications?",
        [
            "A. A fine-tuned model for a specific task",
            "B. A prompt template that shapes LLM output",
            "C. A Python function that processes data",
            "D. A trained neural network module",
        ],
        index=None,
        key="quiz_q1",
    )
    if q1:
        if q1.startswith("B"):
            st.success("Correct! A skill is just a system prompt — text that tells the LLM how to behave and format its response.")
        else:
            st.error("Not quite. A skill is a prompt template (system prompt) — no fine-tuning or special code, just text.")

    q2 = st.radio(
        "2. What makes an agent different from using a skill directly?",
        [
            "A. Agents use a more powerful LLM",
            "B. Agents can call tools and loop until they have enough context",
            "C. Agents are faster because they skip the system prompt",
            "D. Agents don't use skills at all",
        ],
        index=None,
        key="quiz_q2",
    )
    if q2:
        if q2.startswith("B"):
            st.success("Correct! The agent adds a decision loop and tool calling on top of the same LLM. It can select skills, gather context, and iterate.")
        else:
            st.error("Not quite. The key difference is the loop + tools. An agent can call tools (including skills) and keep reasoning until done.")

    q3 = st.radio(
        "3. Why does Agent Mode typically use more tokens than Skill Mode?",
        [
            "A. It uses a bigger model",
            "B. It generates longer responses",
            "C. Each loop iteration and tool call requires additional API calls",
            "D. The agent prompt is encrypted and takes more tokens to decode",
        ],
        index=None,
        key="quiz_q3",
    )
    if q3:
        if q3.startswith("C"):
            st.success("Correct! The agent makes multiple API calls — one per loop iteration, plus calls to apply the skill. More calls = more tokens.")
        else:
            st.error("Not quite. The extra tokens come from multiple API calls: the reasoning loop iterations plus the skill application call.")
