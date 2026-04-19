"""
Stage 2 — Collect Traces

Step 2 of 2: Sends each query to the chatbot and saves the full trace.
A trace = {query, response, user_type, query_type, scenario, timestamp}.

Usage: python3 collect_traces.py [path/to/queries.csv]
If no CSV is provided, uses the most recent file in queries/.

Output: traces/traces_YYYYMMDD.json
"""

import csv
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

CHATBOT_URL = "http://localhost:8001/chat"
QUERIES_DIR = Path(__file__).parent / "queries"
TRACES_DIR = Path(__file__).parent / "traces"


def ask(query: str) -> str:
    payload = json.dumps({"messages": [{"role": "user", "content": query}]}).encode()
    req = urllib.request.Request(
        CHATBOT_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["messages"][-1]["content"]


def get_latest_queries_file() -> Path:
    files = sorted(QUERIES_DIR.glob("queries_*.csv"))
    if not files:
        raise FileNotFoundError("No query files found in queries/. Run generate_queries.py first.")
    return files[-1]


def main():
    TRACES_DIR.mkdir(exist_ok=True)

    queries_file = Path(sys.argv[1]) if len(sys.argv) > 1 else get_latest_queries_file()
    print(f"Loading queries from: {queries_file}\n")

    with open(queries_file) as f:
        rows = list(csv.DictReader(f))

    print(f"Collecting traces for {len(rows)} queries against {CHATBOT_URL}\n")
    print("=" * 70)

    traces = []
    for row in rows:
        query = row["query"]
        print(f"[{row['id']}] ({row['user_type']}, {row['query_type']}, {row['scenario']})")
        print(f"  Q: {query}")
        try:
            response = ask(query)
            print(f"  A: {response[:120]}{'...' if len(response) > 120 else ''}")
            traces.append({
                "id": row["id"],
                "user_type": row["user_type"],
                "query_type": row["query_type"],
                "scenario": row["scenario"],
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                # open coding fields (filled in Stage 3)
                "open_code": "",
                "first_failure": "",
                "acceptable": None,
            })
        except Exception as e:
            print(f"  ERROR: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = TRACES_DIR / f"traces_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump(traces, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"{len(traces)} traces saved to {out_file}")
    print("Next: run Stage 3 open_coding.py to annotate these traces.")


if __name__ == "__main__":
    main()
