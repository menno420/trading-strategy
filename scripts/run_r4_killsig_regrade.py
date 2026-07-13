#!/usr/bin/env python3
"""Round 4 slice R4-A — KILL-SIG retroactive re-grade of the round-3 sweeps.

POST-HOLDOUT, DEV-ONLY (ORDER 012 generative rung, 2026-07-13 night-run
direct order "continue with some new ideas"). Promotion is closed: nothing
this script produces can be an out-of-sample claim; a KILL-SIG is evidence
AGAINST a lane, never a long/short inversion signal (inverting a loser
selected on the very data that graded it would be a new untested strategy).

Pre-registration: ``docs/research-round-4-plan.md`` § "R4-A — KILL-SIG
verdict class (retroactive, non-destructive)", merged to main BEFORE this
script existed. Pre-registered rule: **KILL-SIG iff tstat <= -min_tstat(K)**
at the lane's own recorded K (−2.64 at the standard K=12) — the same
Bonferroni bar, mirrored. Zero new arithmetic: both fields (``tstat``,
``min_tstat``) are read verbatim from the already-committed round-3 sweep
summary JSONs; nothing is recomputed, no backtest runs, no data is loaded.

NON-DESTRUCTIVE by pre-registration: every ``experiments/sweeps/r3-*/``
summary JSON stays byte-untouched. This script only READS them and WRITES
one separate report artifact, ``experiments/sweeps/r4-killsig-regrade/
summary.json`` (per-lane rows: sweep, instrument, strategy, timeframe,
original verdict, tstat, min_tstat, new verdict). Lanes whose summaries
carry no recorded verdict/t-stat (the two XSEC bookkeeping-only summaries)
are recorded as ``UNGRADEABLE`` and counted honestly — never recomputed.
No ledger run is executed, so ``experiments/index.jsonl`` is untouched.

Usage: python3 scripts/run_r4_killsig_regrade.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, promotion  # noqa: E402

SWEEPS_DIR = config.EXPERIMENTS_DIR / "sweeps"
OUT_DIR = SWEEPS_DIR / "r4-killsig-regrade"
UNGRADEABLE = "UNGRADEABLE"


def regrade_lane(summary: dict) -> dict:
    """Build one report row from a committed r3 per-lane summary dict.

    Reads only already-recorded fields. A lane is UNGRADEABLE when it has
    no recorded verdict or no recorded ``promotion_grade`` tstat/min_tstat
    (per the pre-registered honesty rule: count, never recompute).
    """
    grade = summary.get("promotion_grade") or {}
    original = summary.get("verdict")
    tstat = grade.get("tstat")
    min_t = grade.get("min_tstat")
    keep = isinstance(original, str) and original.startswith("KEEP")
    if original is None or tstat is None or min_t is None:
        new_verdict = UNGRADEABLE
    else:
        new_verdict = promotion.classify_verdict(keep, tstat, min_t)
    return {
        "sweep": summary.get("sweep"),
        "instrument": summary.get("instrument"),
        "strategy": summary.get("family"),
        "timeframe": summary.get("timeframe"),
        "original_verdict": original,
        "tstat": tstat,
        "min_tstat": min_t,
        "new_verdict": new_verdict,
    }


def main() -> None:
    lane_files = sorted(SWEEPS_DIR.glob("r3-*/*.json"))
    if not lane_files:
        raise SystemExit("no r3 per-lane summaries found — nothing to re-grade")
    rows = []
    for path in lane_files:
        summary = json.loads(path.read_text())
        row = regrade_lane(summary)
        row["source_file"] = str(path.relative_to(config.REPO_ROOT))
        rows.append(row)
    counts = {"total": len(rows)}
    for verdict in (promotion.SWEEP_KEEP, promotion.SWEEP_KILL,
                    promotion.SWEEP_KILL_SIG, UNGRADEABLE):
        counts[verdict] = sum(1 for r in rows if r["new_verdict"] == verdict)
    report = {
        "schema_version": 1,
        "slice": "r4-killsig-regrade",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "order": "ORDER 012 (generative rung)",
        "preregistered_in": ("docs/research-round-4-plan.md § R4-A — "
                             "KILL-SIG verdict class (retroactive, "
                             "non-destructive)"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; "
                                  "re-grade of committed dev-rail sweep "
                                  "summaries only — no runs, no data loads, "
                                  "zero new arithmetic"),
        "rule": ("KILL-SIG iff tstat <= -min_tstat at the lane's own "
                 "recorded K; KEEP lanes unchanged; missing tstat => "
                 "UNGRADEABLE (counted, never recomputed)"),
        "non_destructive": ("all experiments/sweeps/r3-*/ summaries "
                            "byte-untouched; this report is the only "
                            "artifact written"),
        "inversion_warning": ("a KILL-SIG is evidence AGAINST the lane and "
                              "NOT a signal to invert: the inversion would "
                              "be a new untested strategy selected on the "
                              "very data that graded it"),
        "counts": counts,
        "lanes": rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"re-graded {counts['total']} r3 lanes -> {out}")
    print("counts:", {k: v for k, v in counts.items() if k != "total"})
    for r in rows:
        if r["new_verdict"] == promotion.SWEEP_KILL_SIG:
            print(f"  KILL-SIG: {r['sweep']} {r['strategy']} "
                  f"{r['instrument']} {r['timeframe']} t={r['tstat']:.2f} "
                  f"bar={r['min_tstat']:.2f}")


if __name__ == "__main__":
    main()
