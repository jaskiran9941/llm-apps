# Agent vs Skills Demo

An interactive Streamlit app that teaches the difference between **Skills** and **Agents** in LLM applications.

> **Agent = LLM + Tools + Loop + Skills**

## What You'll Learn
 
| Concept | What It Is | In This Demo |
|---------|-----------|--------------|
| **Skill** | A prompt template — just text that tells the LLM how to respond | Code Reviewer, Research Analyst, Data Analyst, Email Drafter |
| **Agent** | An orchestrator that uses skills + tools + a reasoning loop | Autonomous skill selection with tool calling |
| **Tool** | A function the agent can invoke during its loop | `select_skill`, `analyze_code`, `search_web` |

## Available Skills

| Skill | Description | Output Format |
|-------|-------------|---------------|
| Code Reviewer | Reviews code for security vulnerabilities, bugs, and quality issues | Severity-rated findings with fixes |
| Research Analyst | Synthesizes information with citations and multiple perspectives | Cited findings with multiple perspectives |
| Data Analyst | SQL/pandas expertise for data questions | Code + explanation + insights |
| Email Drafter | Professional email composition | Subject + body + variants + notes |

## How It Works

### Skill Mode (Tab 1)

You manually pick a skill, and the LLM follows its prompt template. One query, one response, no tools, no loops.

```
User Query ──> Skill Prompt (template) ──> LLM ──> Response (1 API call)
```

### Agent Mode (Tab 2)

The agent decides which skill to use, calls tools, and reasons through multiple steps autonomously.

```
User Query ──> Agent System Prompt ──> LLM
                                        │
                                   Tool calls?
                                   Yes ──> Execute tools (select_skill, analyze_code, search_web)
                                        │
                                   Loop back to LLM ──> More tools? or Done?
                                        │
                                       Done
                                        │
                                   Final Response (multiple API calls)
```

### Learn Tab (Tab 3)

Side-by-side comparison, architecture diagrams, and an interactive quiz.

## Project Structure

```text
agent-skills-demo/
├── app.py              # Streamlit UI with three tabs
├── skills.py           # Skill definitions (prompt templates + metadata)
├── agent.py            # Agent orchestrator (LLM + tools + loop)
├── tools.py            # Tool schemas and implementations
├── requirements.txt    # Dependencies
├── .env.example        # Environment variable template
└── README.md
```

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the app:**

   ```bash
   streamlit run app.py
   ```

## Key Takeaway

A **skill** is a single system prompt — one API call, one response. An **agent** wraps the same LLM in a loop with tools so it can decide which skill to use, gather context, and iterate until it has a complete answer. Same model, different architecture.
