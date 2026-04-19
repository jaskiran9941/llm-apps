"""
Stage 2 — Generate Queries from Dimensions

Step 1 of 2: Uses an LLM to generate realistic eBay Live queries
from structured (user_type, query_type, scenario) tuples.

Output: queries/queries_YYYYMMDD.csv
"""

import csv
import json
import os
from datetime import datetime
from itertools import product
from pathlib import Path

import litellm
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "stage-1-chatbot" / ".env")

OUTPUT_DIR = Path(__file__).parent / "queries"
MODEL = os.environ.get("MODEL_NAME", "openai/gpt-4.1-mini")

DIMENSIONS = {
    "user_type": ["buyer", "seller"],
    "query_type": ["policy", "how-to", "eligibility", "categories", "troubleshooting", "out-of-scope"],
    "scenario": ["clear", "ambiguous", "edge-case"],
}

EXAMPLES = """
Tuple: (buyer, policy, clear)
Query: Can I cancel a bid after I've placed it on eBay Live?

Tuple: (seller, eligibility, ambiguous)
Query: I've been selling on eBay for a while — how do I know if I can go live?

Tuple: (buyer, out-of-scope, clear)
Query: Does eBay Live have a dedicated mobile app I can download?

Tuple: (seller, categories, edge-case)
Query: I sell vintage streetwear — can I sell that on eBay Live?

Tuple: (buyer, troubleshooting, ambiguous)
Query: I tried to bid but something went wrong, what should I check?
"""


def generate_query(user_type: str, query_type: str, scenario: str) -> str:
    prompt = f"""You are generating test queries for an eBay Live customer support chatbot.

eBay Live is eBay's livestream shopping platform. Users can be buyers (watching/bidding) or sellers (hosting streams).

Given a tuple of dimensions, write a single realistic question a user might ask.
The question should reflect the scenario type:
- clear: specific, unambiguous
- ambiguous: underspecified, could mean multiple things
- edge-case: unusual situation at the boundary of what the bot knows

Here are examples:
{EXAMPLES}

Now generate ONE question for:
Tuple: ({user_type}, {query_type}, {scenario})
Query:"""

    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    return response["choices"][0]["message"]["content"].strip().strip('"')


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"queries_{timestamp}.csv"

    all_tuples = list(product(*DIMENSIONS.values()))
    print(f"Generating queries for {len(all_tuples)} dimension combinations...\n")

    rows = []
    for i, (user_type, query_type, scenario) in enumerate(all_tuples, 1):
        print(f"[{i}/{len(all_tuples)}] ({user_type}, {query_type}, {scenario})")
        try:
            query = generate_query(user_type, query_type, scenario)
            rows.append({
                "id": i,
                "user_type": user_type,
                "query_type": query_type,
                "scenario": scenario,
                "query": query,
            })
            print(f"  → {query}")
        except Exception as e:
            print(f"  ERROR: {e}")

    with open(out_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "user_type", "query_type", "scenario", "query"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{len(rows)} queries saved to {out_file}")


if __name__ == "__main__":
    main()
