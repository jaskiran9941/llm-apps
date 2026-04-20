"""
Stage 8 — Online Monitoring Sampler
=====================================
Simulates the online monitoring loop described in Ch 9 §9.2.

In production, traces arrive continuously from your live application.  This
script demonstrates the full monitoring pipeline by sampling from the Stage 2
trace dataset (36 traces) as a stand-in for real production traffic.

What it does:
  1. Loads traces from stage-2-trace-dataset/traces/ (or a custom path).
  2. Samples them at a configurable rate (default 20% for demo; use 1-5% in prod).
  3. Runs FM1 and FM2 keyword-based judges on each sampled trace.
     (In production, replace with the LLM judges from Stage 5.)
  4. Computes the raw observed pass rate p_obs for each failure mode.
  5. Applies the Rogan-Gladen bias correction:
         theta_hat = (p_obs + TNR - 1) / (TPR + TNR - 1)
  6. Estimates a 95% bootstrap confidence interval around theta_hat.
  7. Prints a monitoring dashboard with status indicators.
  8. Exits with code 1 if any lower CI bound is below the alert threshold.

Usage:
    python3 monitoring_sampler.py                    # demo with Stage 2 traces
    python3 monitoring_sampler.py --rate 0.05        # 5% sample rate
    python3 monitoring_sampler.py --traces /path/to/traces.json
    python3 monitoring_sampler.py --threshold 0.80   # alert threshold

Nightly cron job (see bottom of file for full instructions):
    0 8 * * * cd /path/to/stage-8-ci-monitoring && python3 monitoring_sampler.py >> /var/log/ebay_monitor.log 2>&1

IMPORTANT — never run judges in the critical path:
    Monitoring runs asynchronously, AFTER the chatbot has already responded.
    Adding judge latency to live request handling would degrade user experience.
    Instead: write traces to a queue/file/database and process them offline.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default path to the Stage 2 trace dataset (used as production traffic sim)
DEFAULT_TRACES_PATH = (
    Path(__file__).parent.parent
    / "stage-2-trace-dataset"
    / "traces"
    / "traces_20260419_113459.json"
)

# Sampling rate — 20% for this demo; use 1-5% in production
DEFAULT_SAMPLE_RATE = 0.20

# Alert threshold: lower bound of CI must be above this to be "OK"
DEFAULT_THRESHOLD = 0.85

# Rogan-Gladen judge calibration parameters.
# These should come from your Stage 5 evaluate_judge.py test-set results.
# Defaults are conservative estimates for an uncalibrated judge.
# TPR = P(judge says Fail | trace is actually a failure)
# TNR = P(judge says Pass | trace is actually a pass)
DEFAULT_TPR = 0.85
DEFAULT_TNR = 0.90

# Number of bootstrap resamples for CI estimation
BOOTSTRAP_N = 2000

# Random seed for reproducibility in demo mode (set to None for true randomness)
RANDOM_SEED = 42

# Width of separator lines
SEP = "=" * 72

# ---------------------------------------------------------------------------
# Console colour helpers
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


def cyan(s: str) -> str:
    return f"\033[96m{s}\033[0m" if _supports_colour() else s


# ---------------------------------------------------------------------------
# Trace loader
# ---------------------------------------------------------------------------

def load_traces(path: Path) -> list[dict]:
    """Load traces from a JSON file.  Accepts a list of trace objects."""
    with open(path, encoding="utf-8") as fp:
        data = json.load(fp)
    if isinstance(data, list):
        return data
    # If the file wraps traces in a key, unwrap it
    for key in ("traces", "results", "data"):
        if key in data:
            return data[key]
    raise ValueError(f"Cannot parse traces from {path}: unexpected JSON structure.")


# ---------------------------------------------------------------------------
# Inline judges (keyword-based simulation of Stage 5 LLM judges)
# ---------------------------------------------------------------------------
# In production, replace these functions with real LLM judge calls from Stage 5.
# The interface is the same: (trace: dict) -> bool (True = Pass, False = Fail).

def judge_fm1(trace: dict) -> bool:
    """
    FM1 Judge — Confident Out-of-Scope Claim.

    Pass: response either acknowledges uncertainty OR the query is in-scope.
    Fail: response contains definitive negative claims for KB-absent topics.

    KB-absent topics that trigger FM1 if the bot says "not supported":
      - pre-recorded video, scheduling, digital products, VR, third-party integrations
    """
    response = trace.get("response", "").lower()
    query = trace.get("query", "").lower()

    # Topics not in the KB where "not supported" is a fabricated negative claim
    out_of_scope_topics = [
        "pre-recorded", "pre recorded", "prerecorded",
        "schedul",           # scheduling a stream
        "virtual reality", "vr shopping",
        "digital product",   # digital art, downloads
        "third-party",
    ]

    # Check if the query is about an out-of-scope topic
    query_is_oos = any(topic in query for topic in out_of_scope_topics)

    if not query_is_oos:
        # In-scope query — FM1 cannot fire on in-scope topics
        return True

    # Definitive negative phrases that signal FM1 failure
    negative_claims = [
        "not supported",
        "does not support",
        "not currently supported",
        "not available",
        "cannot be used",
        "is not allowed",
    ]
    for phrase in negative_claims:
        if phrase in response:
            return False  # FM1 failure: invented a negative policy

    return True  # Correctly escalated or hedged


def judge_fm2(trace: dict) -> bool:
    """
    FM2 Judge — Invented Troubleshooting Steps.

    Pass: response stays within KB guidance (mentions 20 Mbps, basic setup,
          directs to Help) without inventing specific technical steps.
    Fail: response gives specific troubleshooting steps not in the KB.
    """
    response = trace.get("response", "").lower()
    query_type = trace.get("query_type", "").lower()

    # Only applies to troubleshooting queries
    if "troubleshoot" not in query_type and "troubleshoot" not in query:
        return True

    # Specific invented steps that are NOT in the eBay Live KB
    invented_steps = [
        "clear cache",
        "clear your cache",
        "clearing cache",
        "avoid vpn",
        "avoid using vpn",
        "cell signal booster",
        "encoder settings",
        "restart your router",
        "flush your dns",
        "lower your bitrate",
    ]
    for step in invented_steps:
        if step in response:
            return False  # FM2 failure: invented troubleshooting step

    return True


def run_judges(trace: dict) -> dict[str, bool]:
    """Run all active judges on a single trace.  Returns {fm_id: passed}."""
    return {
        "FM1": judge_fm1(trace),
        "FM2": judge_fm2(trace),
    }


# ---------------------------------------------------------------------------
# Rogan-Gladen bias correction
# ---------------------------------------------------------------------------

def rogan_gladen(p_obs: float, tpr: float, tnr: float) -> float:
    """
    Apply the Rogan-Gladen formula to correct for judge bias.

        theta_hat = (p_obs + TNR - 1) / (TPR + TNR - 1)

    p_obs : raw observed pass rate from the judge
    tpr   : judge's true positive rate (P(judge=Fail | truly a failure))
    tnr   : judge's true negative rate (P(judge=Pass | truly a pass))

    Returns the corrected estimate theta_hat, clamped to [0, 1].

    Reference: Rogan & Gladen (1978), "Estimating Prevalence from
    the Results of a Screening Test", American Journal of Epidemiology.
    See also Ch 5 §5.6 of the course textbook.
    """
    denominator = tpr + tnr - 1.0
    if abs(denominator) < 1e-9:
        # Degenerate case: judge is no better than chance
        return p_obs
    theta = (p_obs + tnr - 1.0) / denominator
    return max(0.0, min(1.0, theta))


# ---------------------------------------------------------------------------
# Bootstrap confidence interval
# ---------------------------------------------------------------------------

def bootstrap_ci(
    observations: list[bool],
    tpr: float,
    tnr: float,
    n_resamples: int = BOOTSTRAP_N,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """
    Compute a bootstrap confidence interval for the Rogan-Gladen corrected
    pass rate theta_hat.

    observations : list of bool (True = Pass, False = Fail) from the judge
    tpr, tnr     : judge calibration parameters
    n_resamples  : number of bootstrap iterations
    alpha        : significance level (default 0.05 → 95% CI)

    Returns (lower, upper) bounds.
    """
    n = len(observations)
    if n == 0:
        return (0.0, 1.0)

    theta_hats: list[float] = []
    rng = random.Random(RANDOM_SEED)

    for _ in range(n_resamples):
        sample = [rng.choice(observations) for _ in range(n)]
        p_obs_boot = sum(1 for x in sample if x) / n
        theta_boot = rogan_gladen(p_obs_boot, tpr, tnr)
        theta_hats.append(theta_boot)

    theta_hats.sort()
    lower_idx = int(math.floor(alpha / 2 * n_resamples))
    upper_idx = int(math.ceil((1 - alpha / 2) * n_resamples)) - 1
    return (
        theta_hats[max(0, lower_idx)],
        theta_hats[min(len(theta_hats) - 1, upper_idx)],
    )


# ---------------------------------------------------------------------------
# Dashboard renderer
# ---------------------------------------------------------------------------

FM_LABELS = {
    "FM1": "Out-of-Scope Claim",
    "FM2": "Invented Troubleshooting",
}


def render_dashboard(
    results: dict[str, list[bool]],
    total_traces: int,
    sampled_count: int,
    sample_rate: float,
    tpr: float,
    tnr: float,
    threshold: float,
) -> tuple[bool, list[str]]:
    """
    Render the monitoring dashboard to stdout.

    Returns (any_alert: bool, alert_messages: list[str]).
    """
    lines: list[str] = []

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    lines.append("")
    lines.append(SEP)
    lines.append(bold("eBay Live Chatbot  —  Quality Monitor"))
    lines.append(SEP)
    lines.append(f"  Run time        : {timestamp}")
    lines.append(f"  Total traces    : {total_traces}")
    lines.append(
        f"  Sampled         : {sampled_count}/{total_traces} "
        f"({sample_rate * 100:.0f}%)"
    )
    lines.append(f"  Alert threshold : {threshold:.0%}")
    lines.append(f"  Judge TPR/TNR   : {tpr:.2f} / {tnr:.2f}  (Rogan-Gladen correction)")
    lines.append("")
    lines.append(
        f"  {'Failure Mode':<28} {'n':>4}  "
        f"{'Raw Pass':>9}  {'Corrected θ̂':>13}  "
        f"{'95% CI':>16}  Status"
    )
    lines.append(f"  {'-' * 68}")

    any_alert = False
    alert_messages: list[str] = []

    for fm_id, observations in sorted(results.items()):
        n = len(observations)
        if n == 0:
            label = FM_LABELS.get(fm_id, fm_id)
            lines.append(f"  {fm_id}: {label:<24} {'0':>4}  {'n/a':>9}  {'n/a':>13}  {'[n/a]':>16}  (no data)")
            continue

        n_pass = sum(1 for x in observations if x)
        p_obs = n_pass / n
        theta_hat = rogan_gladen(p_obs, tpr, tnr)
        lower, upper = bootstrap_ci(observations, tpr, tnr)

        label = FM_LABELS.get(fm_id, fm_id)

        # Determine status
        if lower < threshold:
            status_text = "BELOW THRESHOLD"
            status_display = red(f"ALERT  [{status_text}]")
            any_alert = True
            alert_messages.append(
                f"{fm_id} ({label}): lower CI bound {lower:.2f} < threshold {threshold:.2f}"
            )
        else:
            status_display = green("OK")

        lines.append(
            f"  {fm_id}: {label:<24} {n:>4}  "
            f"{p_obs:>8.2%}  "
            f"{theta_hat:>12.2%}  "
            f"[{lower:.2f}, {upper:.2f}]  "
            f"{status_display}"
        )

    lines.append("")
    lines.append(SEP)

    if any_alert:
        lines.append(bold(red("MONITORING ALERT — one or more failure modes below threshold.")))
        for msg in alert_messages:
            lines.append(f"  - {msg}")
        lines.append("")
        lines.append("  Next steps:")
        lines.append("  1. Pull the flagged traces and run manual error analysis (Stage 3).")
        lines.append("  2. Identify whether this is a new failure mode or a regression.")
        lines.append("  3. If new: update the failure taxonomy (Stage 4) and judge (Stage 5).")
        lines.append("  4. Add a golden example to the CI dataset so future regressions are caught.")
        lines.append("  5. Deploy the improved pipeline and resume monitoring.")
    else:
        lines.append(bold(green("All failure modes within acceptable bounds.")))

    lines.append(SEP)

    for line in lines:
        print(line)

    return any_alert, alert_messages


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="eBay Live online monitoring sampler — simulates production trace sampling."
    )
    parser.add_argument(
        "--traces",
        type=Path,
        default=DEFAULT_TRACES_PATH,
        help=f"Path to traces JSON file.  Default: {DEFAULT_TRACES_PATH}",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=DEFAULT_SAMPLE_RATE,
        help=f"Sampling rate (0.0–1.0).  Default: {DEFAULT_SAMPLE_RATE} ({DEFAULT_SAMPLE_RATE*100:.0f}%)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Alert threshold for CI lower bound.  Default: {DEFAULT_THRESHOLD}",
    )
    parser.add_argument(
        "--tpr",
        type=float,
        default=DEFAULT_TPR,
        help=f"Judge true positive rate (from Stage 5).  Default: {DEFAULT_TPR}",
    )
    parser.add_argument(
        "--tnr",
        type=float,
        default=DEFAULT_TNR,
        help=f"Judge true negative rate (from Stage 5).  Default: {DEFAULT_TNR}",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help=f"Random seed for reproducibility.  Default: {RANDOM_SEED}",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Disable fixed random seed (true random sampling).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    global RANDOM_SEED
    RANDOM_SEED = None if args.no_seed else args.seed
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    # --- Load traces ---
    if not args.traces.exists():
        print(red(f"ERROR: Traces file not found: {args.traces}"))
        print("Run the Stage 2 trace collector first, or pass --traces <path>.")
        sys.exit(1)

    all_traces = load_traces(args.traces)
    total_count = len(all_traces)

    # --- Sample ---
    k = max(1, round(total_count * args.rate))
    sampled = random.sample(all_traces, min(k, total_count))
    sampled_count = len(sampled)

    print(f"\nLoaded {total_count} traces from {args.traces.name}")
    print(f"Sampling {sampled_count} traces ({args.rate * 100:.1f}%)...")

    # --- Run judges ---
    # Structure: {fm_id: [True/False, ...]} — one entry per sampled trace
    judge_results: dict[str, list[bool]] = {fm_id: [] for fm_id in ("FM1", "FM2")}

    for trace in sampled:
        verdicts = run_judges(trace)
        for fm_id, passed in verdicts.items():
            judge_results[fm_id].append(passed)

    # --- Render dashboard ---
    any_alert, _ = render_dashboard(
        results=judge_results,
        total_traces=total_count,
        sampled_count=sampled_count,
        sample_rate=args.rate,
        tpr=args.tpr,
        tnr=args.tnr,
        threshold=args.threshold,
    )

    sys.exit(1 if any_alert else 0)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Nightly cron job instructions
# ---------------------------------------------------------------------------
#
# To schedule this as a nightly monitoring job:
#
# 1. Edit your crontab:
#        crontab -e
#
# 2. Add a line (runs at 08:00 UTC every day):
#        0 8 * * * cd /path/to/stage-8-ci-monitoring && \
#            python3 monitoring_sampler.py \
#                --rate 0.05 \
#                --threshold 0.85 \
#                >> /var/log/ebay_live_monitor.log 2>&1
#
#    Adjust the path and parameters as needed.
#
# 3. To also send an email alert on failure, add:
#        0 8 * * * cd /path/to/stage-8-ci-monitoring && \
#            python3 monitoring_sampler.py --rate 0.05 \
#            || mail -s "eBay Live monitor ALERT" you@example.com < /var/log/ebay_live_monitor.log
#
# 4. For production, wire the output to a metrics store (Datadog, Prometheus,
#    Grafana) rather than a flat log file so you can track theta_hat trends
#    over time and see gradual degradation before it becomes an alert.
#
# 5. In production, replace the inline keyword judges with the Stage 5 LLM
#    judges.  The interface is identical: (trace: dict) -> bool.
#    Example:
#        from stage5.judge import run_fm1_judge, run_fm2_judge
#
#        def judge_fm1(trace):
#            return run_fm1_judge(
#                query=trace["query"],
#                response=trace["response"],
#            )
#
# 6. Production sampling note:
#    Use --rate 0.01 to 0.05 in production (1-5%).  The 20% default is only
#    suitable for this 36-trace demo because with too few samples the CI is
#    very wide and the estimates are noisy.  In production with thousands of
#    daily traces, 1% gives you 10+ samples per day at typical traffic levels.
