"""
Stage 8 — CI Runner
===================
Runs every example in the golden dataset through the eBay Live chatbot and
evaluates whether each response passes its expected criteria.

Usage:
    python3 ci_runner.py               # Run all golden examples
    python3 ci_runner.py --dry-run     # Print examples without calling the chatbot
    python3 ci_runner.py --verbose     # Show full bot response for each example

Exit code 0 = all pass, 1 = one or more failures (for CI gate integration).

CI integration notes (Ch 9 §9.1):
  - Add this script to your GitHub Actions or CI pipeline.
  - Run it on every commit that changes: system prompt, model, retrieval logic, or tools.
  - Block the merge if exit code is 1.
  - Judge-based checks ("judge" type) are marked as flaky and re-run up to MAX_RETRIES
    times before being counted as a failure, per Ch 9 guidance on LLM test flakiness.
  - Pin the judge model to a specific version string (see JUDGE_MODEL below) so that
    model updates to your judge don't silently change CI behaviour.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration — adjust these for your deployment
# ---------------------------------------------------------------------------

CHATBOT_URL = "http://localhost:8001/chat"

# Path to the golden dataset directory (relative to this script)
GOLDEN_DIR = Path(__file__).parent / "golden_dataset"

# Which golden file to use
GOLDEN_FILE = GOLDEN_DIR / "ebay_live_golden.json"

# Stage 5 judge directory — used when judge_type == "judge"
STAGE5_DIR = Path(__file__).parent.parent / "stage-5-llm-judge"

# Judge model to use for LLM-based checks.
# IMPORTANT: pin to a specific version so CI doesn't break silently when
# the provider updates the underlying model weights.
JUDGE_MODEL = "openai/gpt-4.1-mini"

# LLM judge checks can be non-deterministic.  Retry up to this many extra
# times before counting a failure — reduces flakiness noise in CI.
MAX_RETRIES = 2

# Timeout in seconds for each HTTP call to the chatbot
REQUEST_TIMEOUT = 30

# Width of the separator lines in console output
SEP = "=" * 78

# ---------------------------------------------------------------------------
# Console helpers — colour output (degrades gracefully if terminal lacks ANSI)
# ---------------------------------------------------------------------------

def _supports_colour() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def green(s: str) -> str:
    return f"\033[92m{s}\033[0m" if _supports_colour() else s


def red(s: str) -> str:
    return f"\033[91m{s}\033[0m" if _supports_colour() else s


def yellow(s: str) -> str:
    return f"\033[93m{s}\033[0m" if _supports_colour() else s


def bold(s: str) -> str:
    return f"\033[1m{s}\033[0m" if _supports_colour() else s


# ---------------------------------------------------------------------------
# Chatbot interaction
# ---------------------------------------------------------------------------

def ask_chatbot(query: str) -> str:
    """Send a single-turn query to the chatbot and return the assistant reply."""
    payload = json.dumps({
        "messages": [{"role": "user", "content": query}]
    }).encode("utf-8")
    req = urllib.request.Request(
        CHATBOT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        data = json.loads(resp.read())
    # The chatbot returns the full messages list; the last item is the reply.
    return data["messages"][-1]["content"]


# ---------------------------------------------------------------------------
# Keyword-based checker (no LLM required)
# ---------------------------------------------------------------------------

def check_keywords(example: dict, response: str) -> tuple[bool, str]:
    """
    Evaluate a response against required_keywords and forbidden_keywords.

    Returns (passed: bool, reason: str).

    Rules:
      - Every string in required_keywords must appear in the response
        (case-insensitive).
      - No string in forbidden_keywords may appear in the response
        (case-insensitive).
    """
    required: list[str] = example.get("required_keywords", [])
    forbidden: list[str] = example.get("forbidden_keywords", [])
    response_lower = response.lower()

    for kw in required:
        if kw.lower() not in response_lower:
            return False, f"Missing required keyword: '{kw}'"

    for kw in forbidden:
        if kw.lower() in response_lower:
            return False, f"Contains forbidden keyword: '{kw}'"

    return True, "pass"


# ---------------------------------------------------------------------------
# LLM judge checker (uses Stage 5 judge prompts when available)
# ---------------------------------------------------------------------------

def _load_judge_prompt(failure_mode: str) -> Optional[str]:
    """
    Try to load a judge prompt from Stage 5.

    Looks for a file named <failure_mode>.txt or <failure_mode>.md in the
    stage-5-llm-judge/judge_prompts/ directory.  Returns None if not found.
    """
    prompt_dir = STAGE5_DIR / "judge_prompts"
    for suffix in (".txt", ".md"):
        candidate = prompt_dir / f"{failure_mode}{suffix}"
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return None


def _call_llm_judge(system_prompt: str, query: str, response: str) -> tuple[bool, str]:
    """
    Call a lightweight LLM to evaluate a (query, response) pair using the
    provided system_prompt.

    This is a thin wrapper that uses the openai SDK if available, or falls
    back to a urllib call against the OpenAI API if the SDK is not installed.

    Returns (passed: bool, reasoning: str).

    Raises RuntimeError if the LLM call fails.
    """
    import os

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No OPENAI_API_KEY (or LLM_API_KEY) found in environment. "
            "Set one to enable LLM-judge checks."
        )

    # Build the user message — a standard eval format
    user_message = (
        f"QUERY: {query}\n\n"
        f"RESPONSE: {response}\n\n"
        "Evaluate the response and reply with JSON: "
        '{"reasoning": "<one sentence>", "answer": "Pass" or "Fail"}'
    )

    # Prefer openai SDK if installed
    try:
        import openai  # type: ignore

        # Strip "openai/" prefix if present (litellm style)
        model_id = JUDGE_MODEL.replace("openai/", "")
        client = openai.OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content or "{}"
        result = json.loads(raw)
        passed = str(result.get("answer", "")).strip().lower() == "pass"
        reasoning = result.get("reasoning", "")
        return passed, reasoning

    except ImportError:
        # Fallback: call OpenAI HTTP API directly
        model_id = JUDGE_MODEL.replace("openai/", "")
        payload = json.dumps({
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)
        passed = str(result.get("answer", "")).strip().lower() == "pass"
        reasoning = result.get("reasoning", "")
        return passed, reasoning


def check_with_judge(example: dict, response: str) -> tuple[bool, str]:
    """
    Evaluate a response using an LLM judge.

    Uses the failure_mode_tested field to locate a Stage 5 judge prompt.
    If no judge prompt is found, falls back to keyword check with a warning.

    Retries up to MAX_RETRIES times on judge uncertainty (flaky test handling).
    """
    failure_mode = example.get("failure_mode_tested", "")
    judge_prompt = _load_judge_prompt(failure_mode)

    if judge_prompt is None:
        # No Stage 5 judge prompt available — fall back gracefully
        print(
            yellow(
                f"  [WARN] No judge prompt found for '{failure_mode}' in "
                f"{STAGE5_DIR / 'judge_prompts'}. Falling back to keyword check."
            )
        )
        return check_keywords(example, response)

    last_error: Optional[str] = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            passed, reasoning = _call_llm_judge(judge_prompt, example["query"], response)
            return passed, reasoning
        except Exception as exc:
            last_error = str(exc)
            if attempt < MAX_RETRIES:
                time.sleep(1)  # brief pause before retry

    # All retries exhausted
    return False, f"Judge error after {1 + MAX_RETRIES} attempts: {last_error}"


# ---------------------------------------------------------------------------
# Orchestrator: evaluate one example
# ---------------------------------------------------------------------------

def evaluate_example(
    example: dict, response: str
) -> tuple[bool, str]:
    """Dispatch to the appropriate checker based on example['judge_type']."""
    judge_type = example.get("judge_type", "keyword")

    if judge_type == "keyword":
        return check_keywords(example, response)
    elif judge_type == "judge":
        return check_with_judge(example, response)
    else:
        # Unknown type — default to keyword
        return check_keywords(example, response)


# ---------------------------------------------------------------------------
# Golden dataset loader
# ---------------------------------------------------------------------------

def load_golden_examples() -> list[dict]:
    """Load examples from ebay_live_golden.json (preferred) or any JSON in golden_dataset/."""
    if GOLDEN_FILE.exists():
        with open(GOLDEN_FILE, encoding="utf-8") as fp:
            data = json.load(fp)
        return data if isinstance(data, list) else [data]

    # Fallback: scan directory for any JSON files
    examples: list[dict] = []
    for f in sorted(GOLDEN_DIR.glob("*.json")):
        if f.name == "example_format.json":
            continue  # skip placeholder
        with open(f, encoding="utf-8") as fp:
            raw = json.load(fp)
        if isinstance(raw, list):
            examples.extend(raw)
        else:
            examples.append(raw)
    return examples


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------

def print_dry_run(examples: list[dict]) -> None:
    """Print a summary of all golden examples without querying the chatbot."""
    print(bold("\nDRY RUN — Golden Dataset Preview"))
    print(SEP)
    print(f"{'ID':<6} {'Category':<22} {'Failure Mode':<28} {'Check Type'}")
    print("-" * 78)
    for ex in examples:
        print(
            f"{ex.get('id', '?'):<6} "
            f"{ex.get('category', ''):<22} "
            f"{ex.get('failure_mode_tested', ''):<28} "
            f"{ex.get('judge_type', 'keyword')}"
        )
    print(SEP)
    print(f"Total: {len(examples)} examples")
    print("\nRequired keywords sample:")
    for ex in examples[:3]:
        print(f"  [{ex.get('id')}] required={ex.get('required_keywords')} "
              f"forbidden={ex.get('forbidden_keywords')}")


# ---------------------------------------------------------------------------
# Main CI run
# ---------------------------------------------------------------------------

def run_ci(examples: list[dict], verbose: bool = False) -> int:
    """
    Run all golden examples through the chatbot and evaluate each one.

    Returns the number of failures (0 = CI pass, >0 = CI fail).
    """
    print(bold(f"\neBay Live Chatbot — CI Runner"))
    print(SEP)
    print(f"Golden examples : {len(examples)}")
    print(f"Chatbot URL     : {CHATBOT_URL}")
    print(f"Golden dataset  : {GOLDEN_FILE.name}")
    print(SEP)

    failures: list[dict] = []
    errors: list[dict] = []

    # Track statistics by category
    category_counts: dict[str, dict] = {}

    for i, ex in enumerate(examples, start=1):
        ex_id = ex.get("id", f"#{i}")
        category = ex.get("category", "unknown")
        query = ex["query"]
        judge_type = ex.get("judge_type", "keyword")

        print(f"\n[{ex_id}] {bold(ex.get('description', query[:60]))}")
        print(f"  Category : {category}  |  Check : {judge_type}")
        print(f"  Query    : {query[:72]}")

        # --- Query the chatbot ---
        response = ""
        try:
            response = ask_chatbot(query)
        except urllib.error.URLError as exc:
            msg = (
                f"Cannot reach chatbot at {CHATBOT_URL}: {exc}. "
                "Is the backend running? (cd stage-1-chatbot && uvicorn backend.main:app --port 8001)"
            )
            print(f"  {red('ERROR')} — {msg}")
            errors.append({"example": ex, "response": "", "reason": msg})
            _update_category(category_counts, category, passed=False)
            continue
        except Exception as exc:
            msg = str(exc)
            print(f"  {red('ERROR')} — {msg}")
            errors.append({"example": ex, "response": "", "reason": msg})
            _update_category(category_counts, category, passed=False)
            continue

        if verbose:
            print(f"  Response : {response[:120]}{'...' if len(response) > 120 else ''}")

        # --- Evaluate the response ---
        passed, reason = evaluate_example(ex, response)

        status = green("PASS") if passed else red("FAIL")
        print(f"  Result   : {status}" + (f" — {reason}" if not passed else ""))

        _update_category(category_counts, category, passed=passed)

        if not passed:
            failures.append({
                "example": ex,
                "response": response,
                "reason": reason,
            })

    # --- Summary ---
    print(f"\n{SEP}")
    print(bold("CI SUMMARY"))
    print(SEP)

    total = len(examples)
    n_pass = total - len(failures) - len(errors)
    n_fail = len(failures)
    n_error = len(errors)

    print(f"  Passed : {green(str(n_pass))}/{total}")
    if n_fail:
        print(f"  Failed : {red(str(n_fail))}/{total}")
    if n_error:
        print(f"  Errors : {yellow(str(n_error))}/{total}")

    # Per-category breakdown
    if category_counts:
        print(f"\n  {'Category':<26} {'Pass':>5} {'Fail':>5}")
        print(f"  {'-'*38}")
        for cat, counts in sorted(category_counts.items()):
            p = counts["pass"]
            f = counts["fail"]
            indicator = green("OK") if f == 0 else red("FAIL")
            print(f"  {cat:<26} {green(str(p)):>5} {red(str(f)) if f else str(f):>5}  {indicator}")

    # Failure details
    if failures:
        print(f"\n{SEP}")
        print(bold("FAILURE DETAILS"))
        print(SEP)
        for item in failures:
            ex = item["example"]
            print(f"\n  [{ex.get('id')}] {ex.get('description', ex.get('query', ''))}")
            print(f"  Failure mode : {ex.get('failure_mode_tested', 'n/a')}")
            print(f"  Reason       : {red(item['reason'])}")
            if item["response"]:
                snippet = item["response"][:200].replace("\n", " ")
                print(f"  Bot response : {snippet}{'...' if len(item['response']) > 200 else ''}")
            print(f"  Fix hint     : {ex.get('notes', '')[:120]}")

    print(f"\n{SEP}")
    if n_fail == 0 and n_error == 0:
        print(bold(green(f"CI PASSED — all {total} checks passed.")))
    else:
        total_bad = n_fail + n_error
        print(bold(red(f"CI FAILED — {total_bad}/{total} check(s) did not pass.")))
        print("  Merge blocked. Fix the regressions above before merging.")
    print(SEP)

    return n_fail + n_error


def _update_category(
    counts: dict[str, dict], category: str, passed: bool
) -> None:
    if category not in counts:
        counts[category] = {"pass": 0, "fail": 0}
    if passed:
        counts[category]["pass"] += 1
    else:
        counts[category]["fail"] += 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="eBay Live CI runner — validates golden dataset against the chatbot."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print all golden examples without querying the chatbot.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show the full bot response snippet for each example.",
    )
    parser.add_argument(
        "--chatbot-url",
        default=CHATBOT_URL,
        help=f"Override the chatbot endpoint. Default: {CHATBOT_URL}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Allow URL override from CLI
    global CHATBOT_URL
    CHATBOT_URL = args.chatbot_url

    examples = load_golden_examples()
    if not examples:
        print(yellow("No golden examples found."))
        print(f"Expected: {GOLDEN_FILE}")
        print("Create it or populate golden_dataset/ with JSON files.")
        sys.exit(0)

    if args.dry_run:
        print_dry_run(examples)
        sys.exit(0)

    n_failures = run_ci(examples, verbose=args.verbose)
    sys.exit(0 if n_failures == 0 else 1)


if __name__ == "__main__":
    main()
