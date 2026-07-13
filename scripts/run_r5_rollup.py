#!/usr/bin/env python3
"""Round 5 — round-level aggregation of the four verdict-bearing slices.

POST-HOLDOUT, DEV-ONLY. Pre-registered aggregation rule
(``docs/research-round-5-plan.md`` § "Round-level aggregation"): a target
lane exits Round 5 as KEEP-dev only if it keeps dev-candidate status
under ALL FOUR verdict-bearing slices (R5-A, R5-B, R5-C, R5-D); any
single demotion is a KILL for the lane, recorded with the slice(s) that
killed it. The R5-C escalate branch changes no verdict (it is carried as
a flag pointing at the owner-gated proposal doc).

Pure re-aggregation of the four committed slice summaries — no data
loaded, no backtest run, nothing ledgered. Writes
``experiments/sweeps/r5-rollup/summary.json`` (the machine-readable
rollup the plan's honesty rail names for recording demotions).

Usage: python3 scripts/run_r5_rollup.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, sweeps  # noqa: E402

SLICES = {
    "R5-A": "r5-neighborhood",
    "R5-B": "r5-split-stability",
    "R5-C": "r5-bootstrap",
    "R5-D": "r5-selection-fair",
}
VERDICT_KEEP = "KEEP (dev-candidate only)"
OUT_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r5-rollup"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = {
        s: json.loads((config.EXPERIMENTS_DIR / "sweeps" / d /
                       "summary.json").read_text())
        for s, d in SLICES.items()
    }
    lanes = []
    for lane in sweeps.R5A_TARGET_LANES:
        lane_id = lane["lane_id"]
        per_slice, killed_by, escalate = {}, [], False
        for s, summary in summaries.items():
            row = next(r for r in summary["lanes"]
                       if r["lane_id"] == lane_id)
            per_slice[s] = {"verdict": row.get("verdict", row["status"]),
                            "sweep_verdict": row.get("sweep_verdict"),
                            "status": row["status"]}
            if row["status"] == "GRADED" \
                    and row["verdict"] != VERDICT_KEEP:
                killed_by.append(s)
            if s == "R5-C" and row.get("escalate_to_owner"):
                escalate = True
        final = VERDICT_KEEP if not killed_by else "KILL"
        lanes.append({
            "lane_id": lane_id, "sweep": lane["sweep"],
            "strategy": lane["family"], "instrument": lane["instrument"],
            "timeframe": lane["timeframe"],
            "slices": per_slice,
            "killed_by": killed_by,
            "escalate_to_owner": escalate,
            "round5_verdict": final,
        })
    counts = {
        "target_lanes": len(lanes),
        "keep_dev": sum(1 for l in lanes
                        if l["round5_verdict"] == VERDICT_KEEP),
        "kill": sum(1 for l in lanes if l["round5_verdict"] == "KILL"),
        "escalate_to_owner": sum(1 for l in lanes
                                 if l["escalate_to_owner"]),
    }
    report = {
        "schema_version": 1,
        "slice": "r5-rollup",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "preregistered_in": ("docs/research-round-5-plan.md § Round-level "
                             "aggregation"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; a "
                                  "Round-5 KEEP is a dev-candidate only, "
                                  "never a finding; a Round-5 KILL is a "
                                  "demotion of a round-3 dev-candidate"),
        "rule": ("KEEP-dev iff KEEP under ALL FOUR of R5-A/B/C/D; any "
                 "single demotion is a KILL recorded with the killing "
                 "slice(s); the R5-C escalate branch changes no verdict"),
        "escalate_proposal": ("docs/proposals/"
                              "r5c-btc-bollinger-breakout-oos-proposal.md"),
        "slice_summaries": {s: f"experiments/sweeps/{d}/summary.json"
                            for s, d in SLICES.items()},
        "burden": {"round5_new_registered_configs":
                       sweeps.r5a_total_configs(),
                   "program_cumulative_before": 4345,
                   "program_cumulative_after":
                       4345 + sweeps.r5a_total_configs()},
        "counts": counts,
        "lanes": lanes,
    }
    out = OUT_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"round 5 rollup: {counts['keep_dev']} KEEP-dev / "
          f"{counts['kill']} KILL of {counts['target_lanes']} target "
          f"lanes; {counts['escalate_to_owner']} escalate-to-owner -> "
          f"{out}")
    for l in lanes:
        flags = (f" (killed by {', '.join(l['killed_by'])})"
                 if l["killed_by"] else "")
        flags += " [escalate-to-owner]" if l["escalate_to_owner"] else ""
        print(f"  {l['lane_id']}: {l['round5_verdict']}{flags}")


if __name__ == "__main__":
    main()
