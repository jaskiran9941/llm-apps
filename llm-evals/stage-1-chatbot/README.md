# Stage 1 — eBay Live Support Chatbot

A customer support chatbot for **eBay Live**, eBay's livestream shopping platform. Built on real public information scraped from eBay's help pages and seller center. This is the baseline we'll evaluate and improve through stages 2–7.

## Setup

```bash
cd stage-1-chatbot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API key
```

## Run

```bash
uvicorn backend.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

## What it covers

- How eBay Live works for buyers (bidding, soft close, max bid, payment)
- How eBay Live works for sellers (eligibility, interest form, formats, fees)
- Available categories (Collectibles, Luxury)
- Technical requirements for sellers
- Beta status and US-only availability

## Why this is evaluable

The system prompt is grounded in real, public eBay Live policies. If the bot says something wrong, you'll know — because you know the actual policies. That's what makes evals meaningful.

## Next: Stage 2 — Manual Testing

Ask ~20 questions covering things you know the answer to, and record every response that surprises or misleads you.
