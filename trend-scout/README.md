# Trend Scout

A multi-source tech trend aggregator that pulls from Reddit and web sources, analyzes with Gemini, and delivers a digest via email.

## What It Does

- **Scouts Reddit** via Composio (r/MachineLearning, r/LocalLLaMA, etc.)
- **Searches Web** via Tavily (TechCrunch, HackerNews, ProductHunt, Twitter/X)
- **Analyzes trends** with Gemini 2.0 Flash
- **Generates HTML digest** with top findings
- **Sends email** via Gmail (optional)

## Architecture

```
Topics → Reddit Scout → Web Scout → Gemini Analysis → HTML Digest → Email
              ↓              ↓
          Composio        Tavily
```

**Note:** This is a **workflow/pipeline**, not an autonomous agent. The LLM is used for analysis only, not for deciding which sources to query.

## Tech Stack

- **LangGraph** - Workflow orchestration
- **Composio** - Reddit & Gmail OAuth integration
- **Tavily** - Web search API
- **Gemini 2.0 Flash** - Analysis
- **Streamlit** - Dashboard UI

## Quick Start

```bash
# Setup
cd trend-scout
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

Open http://localhost:8501 and add your API keys in the sidebar.

## API Keys Required

| Key | Get it from |
|-----|-------------|
| COMPOSIO_API_KEY | [app.composio.dev/settings](https://app.composio.dev/settings) |
| GOOGLE_API_KEY | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| TAVILY_API_KEY | [tavily.com](https://tavily.com) |

## Usage

### Streamlit Dashboard
```bash
streamlit run app.py
```

### CLI
```bash
# Preview (no email)
python main.py preview

# Run with email
python main.py run

# Schedule daily at 8am
python main.py schedule
```

## Project Structure

```
trend-scout/
├── app.py              # Streamlit dashboard
├── main.py             # CLI entry point
├── agent.py            # LangGraph workflow
├── config.py           # Topics & settings
├── email_sender.py     # Composio Gmail
├── scouts/
│   ├── reddit_scout.py # Composio Reddit
│   └── web_scout.py    # Tavily search
└── digests/            # Generated HTML digests
```

## Customizing Topics

Edit in the Streamlit sidebar or modify `config.py`:

```python
TOPICS = [
    "AI agents",
    "LLM applications",
    "developer tools",
    "startups funding",
]
```
