# Stage 2 — Manual Testing

Run a structured set of questions against the eBay Live chatbot and record what it gets right, wrong, or makes up.

## Why this matters

Before automating anything, you need to know what failure looks like. Manual testing forces you to read every response and judge it against what you actually know — that's the only way to build a reliable eval dataset.

## What's in here

| File | Purpose |
|------|---------|
| `test_questions.csv` | 24 questions across 6 categories with expected answer hints |
| `run_tests.py` | Sends each question to the chatbot and saves responses to JSON |
| `results/` | Raw output from each test run |

## Question categories

- **buyer_basics** — account requirements, US-only availability
- **bidding** — soft close, max bid, bid retraction, auction duration
- **payment** — what happens after winning
- **seller_eligibility** — invite-only, interest form, selling formats
- **categories** — what's allowed (Collectibles, Luxury) and what isn't
- **technical** — upload speed, equipment requirements
- **fees** — final value fees
- **hallucination** — questions outside the knowledge base to catch invented answers

## How to run

Make sure the Stage 1 chatbot is running on port 8001, then:

```bash
python3 run_tests.py
```

Results are saved to `results/results_YYYYMMDD_HHMMSS.json`. Open the file and set `"pass": true` or `false` for each response based on what you know is correct.

## What we found

- **22/24 responses** were accurate and grounded in the system prompt
- **2 hallucinations** detected:
  - Q22: Bot invented that eBay Live is "accessed via the regular eBay app" — not in any source
  - Q24: Bot stated scheduling is not supported — stated a definitive fact it doesn't know
- **1 borderline**: Q3 — bot correctly distinguished watching vs. participating, but made an inference not explicitly in the system prompt

## Next: Stage 3 — Bulk Testing

Scale from 24 to 50+ queries, run them concurrently, and collect responses automatically for deeper analysis.
