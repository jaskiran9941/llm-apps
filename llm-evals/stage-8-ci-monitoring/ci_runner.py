"""
Stage 8 — CI Runner

Runs every example in the golden dataset through the chatbot and
checks whether the response passes the expected criteria.

Usage: python3 ci_runner.py
Exit code 0 = all pass, 1 = one or more failures (for CI integration).
"""

import json
import sys
import urllib.request
from pathlib import Path

CHATBOT_URL = "http://localhost:8001/chat"
GOLDEN_DIR = Path(__file__).parent / "golden_dataset"


def ask(query: str) -> str:
    payload = json.dumps({"messages": [{"role": "user", "content": query}]}).encode()
    req = urllib.request.Request(
        CHATBOT_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["messages"][-1]["content"]


def load_golden_examples() -> list[dict]:
    examples = []
    for f in sorted(GOLDEN_DIR.glob("*.json")):
        with open(f) as fp:
            examples.extend(json.load(fp) if isinstance(json.load(open(f)), list) else [json.load(fp)])
    return examples


def check(example: dict, response: str) -> tuple[bool, str]:
    """
    Simple keyword-based check for golden examples.
    Replace with LLM-as-Judge calls from Stage 5 for subjective criteria.
    """
    required = example.get("required_keywords", [])
    forbidden = example.get("forbidden_keywords", [])
    response_lower = response.lower()

    for kw in required:
        if kw.lower() not in response_lower:
            return False, f"Missing required keyword: '{kw}'"
    for kw in forbidden:
        if kw.lower() in response_lower:
            return False, f"Contains forbidden keyword: '{kw}'"
    return True, "pass"


def main():
    examples = load_golden_examples()
    if not examples:
        print("No golden examples found in golden_dataset/.")
        print("Add JSON files with examples to run CI checks.")
        print("See golden_dataset/example_format.json for the schema.")
        sys.exit(0)

    print(f"Running CI checks on {len(examples)} golden examples...\n")
    print("=" * 70)

    failures = []
    for ex in examples:
        query = ex["query"]
        print(f"[{ex.get('id', '?')}] {query[:60]}...")
        try:
            response = ask(query)
            passed, reason = check(ex, response)
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}" + (f" — {reason}" if not passed else ""))
            if not passed:
                failures.append({"example": ex, "response": response, "reason": reason})
        except Exception as e:
            print(f"  ❌ ERROR — {e}")
            failures.append({"example": ex, "response": "", "reason": str(e)})

    print("\n" + "=" * 70)
    if failures:
        print(f"CI FAILED: {len(failures)}/{len(examples)} checks failed.")
        for f in failures:
            print(f"  - [{f['example'].get('id')}] {f['reason']}")
        sys.exit(1)
    else:
        print(f"CI PASSED: all {len(examples)} checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
