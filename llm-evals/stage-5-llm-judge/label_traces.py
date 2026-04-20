#!/usr/bin/env python3
"""
label_traces.py — Human labeling tool with train/dev/test split.

Loads traces from Stage 2, splits them into train/dev/test (15%/42%/43%)
using a fixed random seed, then prompts you to label each trace for FM1–FM5.

Usage:
    python3 label_traces.py

Options:
    --split {train,dev,test,all}   Label a specific split (default: all)
    --resume                        Skip already-labeled traces
    --show-split                    Print the split assignments and exit

Output:
    labeled_data/train_ids.json    IDs reserved for few-shot examples in judge prompts
    labeled_data/dev.json          Human-labeled dev traces
    labeled_data/test.json         Human-labeled test traces (hold out until final eval!)

The five failure modes:
    FM1: Confident Out-of-Scope Claim
    FM2: Invented Troubleshooting Steps
    FM3: Invented Process Details
    FM4: Failure to Escalate
    FM5: Potentially Misleading Inference
"""

import argparse
import json
import os
import random
from pathlib import Path

# -----------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------

# Path to Stage 2 traces
TRACES_DIR = Path(__file__).parent.parent / "stage-2-trace-dataset" / "traces"

# Output directory for labeled data
LABELED_DIR = Path(__file__).parent / "labeled_data"

# Split ratios — must sum to 1.0
TRAIN_RATIO = 0.15   # ~5-6 traces from 36 — used for few-shot examples in prompts
DEV_RATIO   = 0.42   # ~15 traces — used for iterative prompt refinement
TEST_RATIO  = 0.43   # ~15-16 traces — held out for final TPR/TNR measurement

# Fixed random seed ensures the split is reproducible and stable across runs
SPLIT_SEED = 42

# Failure mode definitions shown to the labeler
FAILURE_MODES = {
    "FM1": "Confident Out-of-Scope Claim — bot says 'eBay Live does not support X' for topic NOT in KB",
    "FM2": "Invented Troubleshooting Steps — bot gives technical advice (clear cache, avoid VPNs) not in KB",
    "FM3": "Invented Process Details — bot invents URLs, feature names, or workflow steps not in KB",
    "FM4": "Failure to Escalate — bot gives confident answer when should say 'I don't know'",
    "FM5": "Potentially Misleading Inference — bot makes plausible but unverified claim stated as fact",
}


# -----------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------

def load_traces() -> list[dict]:
    """Load all traces from the Stage 2 traces directory."""
    trace_files = sorted(TRACES_DIR.glob("*.json"))
    if not trace_files:
        raise FileNotFoundError(
            f"No trace files found in {TRACES_DIR}. "
            "Run Stage 2 collect_traces.py first."
        )

    all_traces = []
    for f in trace_files:
        with open(f) as fh:
            data = json.load(fh)
            if isinstance(data, list):
                all_traces.extend(data)
            else:
                all_traces.append(data)

    print(f"Loaded {len(all_traces)} traces from {len(trace_files)} file(s)")
    return all_traces


# -----------------------------------------------------------------------
# Split assignment
# -----------------------------------------------------------------------

def assign_splits(traces: list[dict]) -> dict[str, list[str]]:
    """
    Assign trace IDs to train/dev/test splits using a fixed seed.

    Returns: {"train": [...ids], "dev": [...ids], "test": [...ids]}

    IMPORTANT: The train IDs are written to labeled_data/train_ids.json.
    When you add few-shot examples to a judge prompt, verify the trace ID
    is in train_ids.json — NEVER use dev or test IDs as examples.
    """
    ids = [str(t["id"]) for t in traces]

    rng = random.Random(SPLIT_SEED)
    shuffled = ids[:]
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = max(1, round(n * TRAIN_RATIO))
    n_dev   = max(1, round(n * DEV_RATIO))
    # test gets everything remaining
    n_test  = n - n_train - n_dev

    splits = {
        "train": shuffled[:n_train],
        "dev":   shuffled[n_train : n_train + n_dev],
        "test":  shuffled[n_train + n_dev :],
    }

    print(f"\nSplit assignment (seed={SPLIT_SEED}):")
    print(f"  Train: {len(splits['train'])} traces (few-shot examples only)")
    print(f"  Dev:   {len(splits['dev'])} traces (iterate prompt here)")
    print(f"  Test:  {len(splits['test'])} traces (hold out — final eval only)")
    print()

    return splits


# -----------------------------------------------------------------------
# Human labeling loop
# -----------------------------------------------------------------------

def label_trace(trace: dict, split_name: str, existing_labels: dict) -> dict | None:
    """
    Display a single trace and prompt the user for FM1–FM5 labels.

    Returns a labels dict, or None if the user chose to quit.
    """
    trace_id = str(trace["id"])

    print("\n" + "=" * 70)
    print(f"TRACE  id={trace_id}  split={split_name}")
    print(f"User type : {trace.get('user_type', 'unknown')}")
    print(f"Query type: {trace.get('query_type', 'unknown')}")
    print(f"Scenario  : {trace.get('scenario', 'unknown')}")
    print()
    print(f"QUERY:\n  {trace['query']}")
    print()
    print(f"RESPONSE:\n  {trace['response']}")
    print()

    # Show existing labels if resuming
    if trace_id in existing_labels:
        prev = existing_labels[trace_id].get("labels", {})
        print(f"(Previously labeled: {prev})")
        print()

    labels = {}

    print("Label each failure mode: [p]ass / [f]ail / [s]kip / [q]uit")
    print()

    for fm_id, fm_desc in FAILURE_MODES.items():
        while True:
            try:
                raw = input(f"  {fm_id} ({fm_desc[:60]}...)\n  Your label [p/f/s/q]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nLabeling interrupted.")
                return None

            if raw == "q":
                return None
            elif raw == "p":
                labels[fm_id] = "Pass"
                break
            elif raw == "f":
                labels[fm_id] = "Fail"
                break
            elif raw == "s":
                labels[fm_id] = None  # skipped / uncertain
                break
            else:
                print("  Please enter p, f, s, or q.")

    print()
    print(f"  Labels recorded: {labels}")
    return labels


# -----------------------------------------------------------------------
# Persistence helpers
# -----------------------------------------------------------------------

def load_existing_labels(split_file: Path) -> dict:
    """Load previously saved labels from a JSON file, keyed by trace ID."""
    if not split_file.exists():
        return {}
    with open(split_file) as fh:
        records = json.load(fh)
    return {str(r["id"]): r for r in records}


def save_labels(split_file: Path, records: dict):
    """Save all labeled records to a JSON file."""
    split_file.parent.mkdir(parents=True, exist_ok=True)
    output = sorted(records.values(), key=lambda r: str(r["id"]))
    with open(split_file, "w") as fh:
        json.dump(output, fh, indent=2)


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Human labeling tool for eBay Live traces")
    parser.add_argument(
        "--split",
        choices=["train", "dev", "test", "all"],
        default="all",
        help="Which split to label (default: all). Note: train IDs are for few-shot examples.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip traces that already have labels saved.",
    )
    parser.add_argument(
        "--show-split",
        action="store_true",
        help="Print split assignments and exit without labeling.",
    )
    args = parser.parse_args()

    LABELED_DIR.mkdir(parents=True, exist_ok=True)

    # Load traces
    traces = load_traces()
    trace_by_id = {str(t["id"]): t for t in traces}

    # Assign splits
    splits = assign_splits(traces)

    # Save train IDs immediately (used by judge prompts as guard)
    train_ids_file = LABELED_DIR / "train_ids.json"
    with open(train_ids_file, "w") as fh:
        json.dump(splits["train"], fh, indent=2)
    print(f"Train IDs saved to: {train_ids_file}")
    print("REMINDER: Only use train IDs as few-shot examples in judge prompts.")
    print()

    if args.show_split:
        for split_name, ids in splits.items():
            print(f"\n{split_name.upper()} ({len(ids)} traces): {ids}")
        return

    # Determine which splits to label
    splits_to_label = (
        ["train", "dev", "test"] if args.split == "all" else [args.split]
    )

    for split_name in splits_to_label:
        split_ids = splits[split_name]
        split_file = LABELED_DIR / f"{split_name}.json"
        existing = load_existing_labels(split_file)

        print(f"\n{'=' * 70}")
        if split_name == "train":
            print(f"LABELING TRAIN SPLIT ({len(split_ids)} traces)")
            print("These traces may become few-shot examples in your judge prompts.")
            print("Label them carefully — they directly influence judge behavior.")
        elif split_name == "dev":
            print(f"LABELING DEV SPLIT ({len(split_ids)} traces)")
            print("Use these to iterate and improve your judge prompts.")
            print("You will run evaluate_judge.py --split dev repeatedly.")
        elif split_name == "test":
            print(f"LABELING TEST SPLIT ({len(split_ids)} traces)")
            print("*** HOLD OUT: do not look at these during prompt development. ***")
            print("Run evaluate_judge.py --split test ONCE when the judge is ready.")

        input(f"\nPress Enter to start labeling the {split_name} split... ")

        records = dict(existing)  # copy existing labels
        labeled_count = 0
        skipped_count = 0

        for trace_id in split_ids:
            if trace_id not in trace_by_id:
                print(f"Warning: trace ID {trace_id} not found in traces — skipping.")
                continue

            # If resuming, skip already-labeled traces
            if args.resume and trace_id in existing:
                skipped_count += 1
                continue

            trace = trace_by_id[trace_id]
            labels = label_trace(trace, split_name, existing)

            if labels is None:
                # User quit — save what we have and exit
                print(f"\nLabeling stopped early. Saving {len(records)} records.")
                save_labels(split_file, records)
                print(f"Progress saved to: {split_file}")
                return

            # Record the labeled trace
            records[trace_id] = {
                "id": trace_id,
                "split": split_name,
                "user_type": trace.get("user_type", ""),
                "query_type": trace.get("query_type", ""),
                "scenario": trace.get("scenario", ""),
                "query": trace["query"],
                "response": trace["response"],
                "labels": labels,
            }
            labeled_count += 1

            # Save after each trace (safe against interruption)
            save_labels(split_file, records)

        print(f"\n{split_name.upper()} split complete:")
        print(f"  Labeled: {labeled_count}")
        if args.resume:
            print(f"  Skipped (already labeled): {skipped_count}")
        print(f"  Saved to: {split_file}")

    print("\n" + "=" * 70)
    print("Labeling complete!")
    print()
    print("Next steps:")
    print("  1. Run evaluate_judge.py --judge fm1 --split dev to measure judge accuracy")
    print("  2. Inspect disagreements and iterate the judge prompt")
    print("  3. Repeat until TPR > 90% and TNR > 90% on dev")
    print("  4. Run evaluate_judge.py --judge fm1 --split test for final measurement")
    print("  5. Run estimate_success_rate.py to get the bias-corrected pass rate")


if __name__ == "__main__":
    main()
