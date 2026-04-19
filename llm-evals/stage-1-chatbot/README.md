# Stage 1 — Basic Chatbot

A customer support chatbot for **TaskFlow**, a fictional SaaS project management tool. This is the foundation we'll evaluate and improve through stages 2–7.

## Setup

```bash
cd stage-1-chatbot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API key
```

## Run

```bash
uvicorn backend.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

## What it does

- Answers questions about TaskFlow pricing, features, and troubleshooting
- Maintains conversation history
- Uses any LiteLLM-supported model (default: `openai/gpt-4.1-mini`)

## Next: Stage 2 — Manual Testing

Run it, ask ~20 questions, and record what breaks.
