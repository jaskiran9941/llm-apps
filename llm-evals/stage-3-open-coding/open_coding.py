"""
Stage 3 — Open Coding

Loads traces from Stage 2 and walks through them one at a time,
collecting freeform annotations. Saves progress after each trace.

Usage: python3 open_coding.py [path/to/traces.json]
If no file given, uses the most recent traces file from Stage 2.

Output: open_codes/open_codes_YYYYMMDD.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

TRACES_DIR = Path(__file__).parent.parent / "stage-2-trace-dataset" / "traces"
OUTPUT_DIR = Path(__file__).parent / "open_codes"


def get_latest_traces() -> Path:
    files = sorted(TRACES_DIR.glob("traces_*.json"))
    if not files:
        raise FileNotFoundError("No trace files found. Run Stage 2 collect_traces.py first.")
    return files[-1]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    traces_file = Path(sys.argv[1]) if len(sys.argv) > 1 else get_latest_traces()
    print(f"Loading traces from: {traces_file}\n")

    with open(traces_file) as f:
        traces = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"open_codes_{timestamp}.json"
    annotations = []

    print("=" * 70)
    print("OPEN CODING — eBay Live Chatbot Traces")
    print("For each trace, write what you observe. Focus on the FIRST failure.")
    print("Press Enter with no input to skip a trace.")
    print("Type 'quit' to save and exit.")
    print("=" * 70)

    for i, trace in enumerate(traces, 1):
        print(f"\n[{i}/{len(traces)}] ID={trace['id']} | {trace['user_type']} | {trace['query_type']} | {trace['scenario']}")
        print(f"\nQUERY:\n  {trace['query']}")
        print(f"\nRESPONSE:\n  {trace['response']}")
        print()

        note = input("Open code (what went wrong? leave blank to skip): ").strip()
        if note.lower() == "quit":
            break
        if not note:
            continue

        first_failure = input("First failure (one phrase): ").strip()
        acceptable_raw = input("Acceptable? (y/n): ").strip().lower()
        acceptable = True if acceptable_raw == "y" else False if acceptable_raw == "n" else None

        annotations.append({
            "trace_id": trace["id"],
            "user_type": trace["user_type"],
            "query_type": trace["query_type"],
            "scenario": trace["scenario"],
            "query": trace["query"],
            "response": trace["response"],
            "open_code": note,
            "first_failure": first_failure,
            "acceptable": acceptable,
        })

        # save after every annotation
        with open(out_file, "w") as f:
            json.dump(annotations, f, indent=2)

        bad_count = sum(1 for a in annotations if a["acceptable"] is False)
        print(f"  ✓ Saved. ({bad_count} bad traces so far)")

    print(f"\n{'=' * 70}")
    print(f"Done. {len(annotations)} traces annotated.")
    print(f"Saved to: {out_file}")
    print("\nNext: run Stage 4 axial_coding.py to cluster these into failure modes.")


if __name__ == "__main__":
    main()
