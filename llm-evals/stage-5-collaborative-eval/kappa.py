"""
Stage 5 — Cohen's Kappa Calculator

Measures inter-annotator agreement between two people labeling the same traces.
Target: κ ≥ 0.60 (Substantial agreement) before building automated judges.

Usage:
    python3 kappa.py                          # runs built-in eBay Live example
    python3 kappa.py labels_a.json labels_b.json   # from JSON files
"""

import json
import sys
from collections import Counter
from pathlib import Path


def cohens_kappa(rater_a: list, rater_b: list) -> float:
    assert len(rater_a) == len(rater_b), "Both raters must label the same traces."
    n = len(rater_a)
    p_obs = sum(a == b for a, b in zip(rater_a, rater_b)) / n
    labels = set(rater_a) | set(rater_b)
    count_a, count_b = Counter(rater_a), Counter(rater_b)
    p_exp = sum((count_a[l] / n) * (count_b[l] / n) for l in labels)
    if p_exp == 1.0:
        return 1.0 if p_obs == 1.0 else 0.0
    return (p_obs - p_exp) / (1 - p_exp)


def interpret_kappa(k: float) -> str:
    if k < 0:     return "Poor — systematic disagreement"
    if k < 0.20:  return "Slight"
    if k < 0.40:  return "Fair — rubric needs significant work"
    if k < 0.60:  return "Moderate — iterate rubric before proceeding"
    if k < 0.80:  return "Substantial ✓ — acceptable for eval use"
    return "Almost perfect ✓"


def print_report(rater_a: list, rater_b: list, failure_mode: str = "FM?"):
    n = len(rater_a)
    kappa = cohens_kappa(rater_a, rater_b)
    p_obs = sum(a == b for a, b in zip(rater_a, rater_b)) / n

    print(f"\n{'='*60}")
    print(f"  Cohen's Kappa Report — {failure_mode}")
    print(f"{'='*60}")
    print(f"  Traces labeled:      {n}")
    print(f"  Percent agreement:   {p_obs:.1%}")
    print(f"  Cohen's Kappa (κ):   {kappa:.3f}")
    print(f"  Interpretation:      {interpret_kappa(kappa)}")
    print(f"{'='*60}")

    disagreements = [(i+1, a, b) for i, (a, b) in enumerate(zip(rater_a, rater_b)) if a != b]
    if disagreements:
        print(f"\n  Disagreements ({len(disagreements)} traces):")
        for trace_num, a, b in disagreements:
            print(f"    Trace {trace_num:2d}: Rater A = {a:4s}  |  Rater B = {b}")
        print()
        print("  → Review these traces in your alignment session.")
        print("  → For each: identify which part of the rubric caused the disagreement.")
        print("  → Fix the RUBRIC DEFINITION, not just the label.\n")
    else:
        print("\n  No disagreements — perfect agreement on this set.\n")

    if kappa < 0.60:
        print("  ⚠️  κ < 0.60. Do not proceed to Stage 7 yet.")
        print("  Run an alignment session, revise the rubric, re-label, and recompute.\n")
    else:
        print("  ✓  κ ≥ 0.60. Rubric is reliable enough for Stage 7.\n")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Load from JSON files: each file is a list of "Pass" or "Fail" strings
        with open(sys.argv[1]) as f:
            rater_a = json.load(f)
        with open(sys.argv[2]) as f:
            rater_b = json.load(f)
        print_report(rater_a, rater_b, failure_mode="From files")

    else:
        # Built-in eBay Live example for FM1 (Confident Out-of-Scope Claim)
        # Based on our 36 real traces — 20 selected for collaborative labeling
        # Traces 1,4,7,9,10,13,15,16,19,21,22,23,24,25,30,31,33,34,35,36

        rater_a = [
            "Pass",  # Trace 1  - MBG policy, correctly in KB
            "Pass",  # Trace 4  - How to bid, correctly in KB
            "Pass",  # Trace 7  - Buyer eligibility, correctly in KB
            "Pass",  # Trace 9  - Outside US edge case, correctly handled
            "Pass",  # Trace 10 - Categories, correctly in KB
            "Fail",  # Trace 13 - Invented troubleshooting (clear cache)
            "Fail",  # Trace 15 - Invented re-bidding guidance
            "Fail",  # Trace 16 - "Focuses on standard devices" — invented framing
            "Pass",  # Trace 19 - Correctly deferred on pricing policy
            "Pass",  # Trace 21 - Correctly deferred on crowdfunding
            "Fail",  # Trace 22 - Invented URL (ebay.com/live)
            "Fail",  # Trace 23 - Invented scheduling feature
            "Fail",  # Trace 24 - "Pre-recorded video not supported" — not in KB
            "Pass",  # Trace 25 - Seller eligibility, correctly in KB
            "Fail",  # Trace 30 - "Digital products not supported" — not in KB
            "Pass",  # Trace 31 - Troubleshooting with KB-grounded advice
            "Fail",  # Trace 33 - Invented VPN/cell booster advice
            "Fail",  # Trace 34 - Invented "complementary sales channel" framing
            "Fail",  # Trace 35 - Invented transaction integration details
            "Fail",  # Trace 36 - "Does not support scheduling" — not in KB
        ]

        # Simulated second annotator — agrees on most, differs on borderlines
        rater_b = [
            "Pass",  # Trace 1
            "Pass",  # Trace 4
            "Pass",  # Trace 7
            "Pass",  # Trace 9
            "Pass",  # Trace 10
            "Fail",  # Trace 13
            "Pass",  # Trace 15 - Rater B: "all bids are final" is correct, re-bidding guidance is borderline
            "Pass",  # Trace 16 - Rater B: "standard devices" is a reasonable inference, not FM1
            "Pass",  # Trace 19
            "Pass",  # Trace 21
            "Fail",  # Trace 22
            "Fail",  # Trace 23
            "Fail",  # Trace 24
            "Pass",  # Trace 25
            "Fail",  # Trace 30
            "Pass",  # Trace 31
            "Fail",  # Trace 33
            "Pass",  # Trace 34 - Rater B: "complementary sales channel" is reasonable framing, not FM1
            "Fail",  # Trace 35
            "Fail",  # Trace 36
        ]

        print_report(rater_a, rater_b, failure_mode="FM1 — Confident Out-of-Scope Claim")

        print("  Alignment session notes for disagreements:")
        print("  Trace 15: Is 'avoid placing duplicate bids' an FM1?")
        print("    → FM1 requires a confident negative claim about a topic NOT in KB.")
        print("    → Bids being final IS in the KB. Re-bidding nuance is FM5 (misleading inference).")
        print("    → Consensus: Pass for FM1, flag for FM5 review.")
        print()
        print("  Trace 16: Is 'focuses on standard devices' an FM1?")
        print("    → The KB doesn't say what eBay Live 'focuses on' for device support.")
        print("    → Bot invented a framing statement as if it were policy.")
        print("    → Consensus: Fail for FM1 — invented policy framing counts.")
        print()
        print("  Trace 34: Is 'complementary sales channel' an FM4?")
        print("    → FM1 requires 'does not support X'. This is positive framing, not negative.")
        print("    → Better classified as FM4 (failure to escalate) or FM5 (misleading inference).")
        print("    → Consensus: Pass for FM1, Fail for FM4.")
