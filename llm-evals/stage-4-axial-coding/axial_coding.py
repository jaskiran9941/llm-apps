"""
Stage 4 — Axial Coding

Loads open codes from Stage 3 and uses an LLM to propose preliminary
failure mode clusters. You review and confirm the final taxonomy.

Usage: python3 axial_coding.py [path/to/open_codes.json]
If no file given, uses the most recent open_codes file from Stage 3.

Output: taxonomies/taxonomy_YYYYMMDD.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import litellm
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / "stage-1-chatbot" / ".env")

OPEN_CODES_DIR = Path(__file__).parent.parent / "stage-3-open-coding" / "open_codes"
OUTPUT_DIR = Path(__file__).parent / "taxonomies"
MODEL = "openai/gpt-4.1-mini"


def get_latest_open_codes() -> Path:
    files = sorted(OPEN_CODES_DIR.glob("open_codes_*.json"))
    if not files:
        raise FileNotFoundError("No open codes found. Run Stage 3 open_coding.py first.")
    return files[-1]


def propose_clusters(open_codes: list[dict]) -> str:
    notes = "\n".join(
        f"- [{a['user_type']}/{a['query_type']}/{a['scenario']}] {a['open_code']}"
        for a in open_codes
        if a.get("open_code")
    )

    prompt = f"""Below are open-coded annotations describing failures in an eBay Live customer support chatbot.

Please group them into 4-6 coherent failure categories. Each category should:
- Have a short descriptive title (2-4 words)
- Have a one-line definition
- Be binary (either present or absent in a trace)
- Be non-overlapping with other categories

Do not invent new failure types. Only cluster what is present in the notes.

Annotations:
{notes}

Output format:
**[Category Name]**: [one-line definition]
Examples from the notes: [2-3 representative quotes]
"""

    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
    )
    return response["choices"][0]["message"]["content"].strip()


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    codes_file = Path(sys.argv[1]) if len(sys.argv) > 1 else get_latest_open_codes()
    print(f"Loading open codes from: {codes_file}\n")

    with open(codes_file) as f:
        open_codes = json.load(f)

    bad_traces = [a for a in open_codes if a.get("acceptable") is False]
    print(f"Found {len(open_codes)} annotated traces ({len(bad_traces)} marked as failures)\n")

    if len(bad_traces) < 5:
        print("Warning: fewer than 5 failure traces. Run more open coding first for better clusters.")

    print("=" * 70)
    print("Proposing failure mode clusters via LLM...\n")
    clusters = propose_clusters(bad_traces if bad_traces else open_codes)
    print(clusters)

    print("\n" + "=" * 70)
    print("Review the proposed clusters above.")
    print("Now define your final failure taxonomy.\n")

    taxonomy = []
    print("Enter each failure mode (blank name to finish):")
    while True:
        name = input("  Failure mode name: ").strip()
        if not name:
            break
        definition = input("  One-line definition: ").strip()
        taxonomy.append({"name": name, "definition": definition})
        print(f"  ✓ Added: {name}")

    if not taxonomy:
        print("No taxonomy entered. Saving proposed clusters as draft.")
        taxonomy = [{"name": "DRAFT", "definition": clusters}]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"taxonomy_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump({
            "created": timestamp,
            "source_file": str(codes_file),
            "failure_modes": taxonomy,
        }, f, indent=2)

    print(f"\nTaxonomy saved to: {out_file}")
    print("Update failure_taxonomy.md with your final definitions.")
    print("\nNext: Stage 5 — build an LLM-as-Judge for each failure mode.")


if __name__ == "__main__":
    main()
