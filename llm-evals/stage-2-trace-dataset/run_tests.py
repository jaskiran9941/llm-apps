"""
Stage 2 — Manual Testing
Sends each test question to the chatbot and saves responses for review.
"""

import csv
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

CHATBOT_URL = "http://localhost:8001/chat"
QUESTIONS_FILE = Path(__file__).parent / "test_questions.csv"
RESULTS_DIR = Path(__file__).parent / "results"


def ask(question: str) -> str:
    payload = json.dumps({"messages": [{"role": "user", "content": question}]}).encode()
    req = urllib.request.Request(CHATBOT_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["messages"][-1]["content"]


def run():
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    with open(QUESTIONS_FILE) as f:
        rows = list(csv.DictReader(f))

    print(f"\nRunning {len(rows)} test questions against {CHATBOT_URL}\n")
    print("=" * 70)

    for row in rows:
        qid = row["id"]
        category = row["category"]
        question = row["question"]
        hint = row["expected_answer_hint"]

        print(f"\n[{qid}] [{category}] {question}")
        print(f"  Expected: {hint}")

        try:
            actual = ask(question)
        except Exception as e:
            actual = f"ERROR: {e}"

        print(f"  Actual:   {actual}")

        results.append({
            "id": qid,
            "category": category,
            "question": question,
            "expected_hint": hint,
            "actual_response": actual,
            "pass": None,   # fill in manually after reviewing
            "notes": "",    # fill in manually
        })

    out_file = RESULTS_DIR / f"results_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"Results saved to {out_file}")
    print("Open the file, review each response, and set 'pass' to true/false.")


if __name__ == "__main__":
    run()
