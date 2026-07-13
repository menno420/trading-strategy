#!/usr/bin/env python3
"""Round 5 slice R5-B — time-split stability / leave-one-split-out of the
top-5 KEEP-dev lanes.

POST-HOLDOUT, DEV-ONLY. Promotion is CLOSED: nothing this script produces
can be an out-of-sample claim; a lane that keeps its status is a
dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-5-plan.md`` § R5-B, merged BEFORE
this script existed. Registered method: replay each target lane's
committed walk-forward per-split params over its exact committed
positional test windows at baseline costs (frozen replay, fidelity guard
first), then recompute the stitched OOS Sharpe delta vs same-window B&H
leaving each test split out in turn (N splits -> N leave-one-out deltas).
Reported: per-split strategy-vs-benchmark Sharpe deltas and the
worst-case leave-one-out stitched delta — i.e. with the lane's single
BEST split removed, where the best split is the one whose removal
minimizes the remaining stitched delta (argmin over the N leave-one-out
deltas; identical to the plan's phrasing, mechanized).

Pre-registered decision rule (per lane): the lane KEEPS dev-candidate
status iff the stitched OOS Sharpe delta vs B&H remains > 0 after
removing the lane's single best test split; otherwise DEMOTED to KILL
(single-window luck). The informational t is reported at the lane's
committed K (12; bar never lowered); KILL-SIG via
``trading_lab.promotion.classify_verdict`` on the lane's replayed
full-set t at that bar.

Benchmark convention: ONE same-window same-cost B&H over the full
stitched OOS span (the committed r3 convention), with its per-bar return
segments dropped positionally alongside the strategy's when a split is
left out — so the leave-nothing-out delta equals the committed stitched
delta exactly.

FIDELITY GUARD (standing rail, R4-B precedent): each lane's baseline
replay must reproduce its committed stitched OOS Sharpe within 1e-8; an
irreproducible lane is recorded SKIPPED with the verbatim reason.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail
(``data_end <= 2025-01-08`` asserted per lane); ``unlock_holdout`` is
never passed. Splits are the DEV walk-forward windows only — the spent
holdout is never touched. All ``experiments/sweeps/r3-*/`` files stay
byte-untouched; this slice writes ``experiments/sweeps/r5-split-stability/``.

LEDGER DECISION (deliberate, R4-B precedent): report-only, NOT ledgered —
0 new registered configs (pure replay/re-aggregation of committed
choices); ``experiments/index.jsonl`` untouched.

Runtime cap (pre-registered): <= 5 minutes wall-clock for the slice.

Usage: python3 scripts/run_r5b_split_stability.py
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEP_NAME = "r5-split-stability"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME

DEV_DATA_END_MAX = "2025-01-08"

BASELINE_COSTS = {"slippage_bps": float(config.DEFAULT_SLIPPAGE_BPS),
                  "commission_bps": float(config.DEFAULT_COMMISSION_BPS)}
assert BASELINE_COSTS == {"slippage_bps": 5.0, "commission_bps": 1.0}

REPLAY_TOL = 1e-8

VERDICT_KEEP = "KEEP (dev-candidate only)"
VERDICT_KILL = "KILL"
STATUS_SKIPPED = "SKIPPED"

RUNTIME_CAP_SECONDS = 300  # pre-registered: <= 5 minutes wall-clock


class LaneSkip(Exception):
    """Lane cannot be reproduced exactly — recorded verbatim, never
    approximated silently (pre-registered honesty rule)."""


def _clean(x):
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def frozen_split_returns(ohlcv, strategy_fn, per_split, timeframe):
    """Replay the committed frozen per-split params on the committed
    positional test windows at baseline costs; return the per-split
    strategy return segments. No selection of any kind happens here."""
    segs = []
    for row in per_split:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        res = run_backtest(ohlcv.iloc[t0:t1], pos, timeframe=timeframe,
                           **BASELINE_COSTS)
        segs.append({"test": [t0, t1], "params": row["params"],
                     "returns": res.returns})
    return segs


def prepare_lane(lane: dict):
    """Load data, replay frozen splits, run the fidelity guard, and slice
    the single full-window B&H's returns per split. Raises LaneSkip with a
    verbatim reason on any mismatch."""
    source = json.loads((config.REPO_ROOT / lane["source_file"]).read_text())
    fam, tick, tf = source["family"], source["instrument"], source["timeframe"]
    if fam not in STRATEGIES:
        raise LaneSkip(f"strategy {fam!r} not in trading_lab.strategies."
                       f"STRATEGIES — original rail cannot be rebuilt")
    ohlcv = load_ohlcv(tick, tf)  # dev rail: holdout excluded by default
    data_end = str(ohlcv.index[-1])
    assert data_end[:10] <= DEV_DATA_END_MAX, \
        f"{tick}: dev rail breached (data_end {data_end})"
    for field, got in (("data_start", str(ohlcv.index[0])),
                       ("data_end", data_end),
                       ("n_bars", int(len(ohlcv)))):
        if got != source[field]:
            raise LaneSkip(f"cache drift vs committed lane "
                           f"{lane['source_file']}: {field} recorded "
                           f"{source[field]!r}, loaded {got!r} — positional "
                           f"windows would misalign")
    per_split = source["walk_forward"]["per_split"]
    segs = frozen_split_returns(ohlcv, STRATEGIES[fam], per_split, tf)
    stitched = pd.concat([s["returns"] for s in segs])
    got_sharpe = metrics.sharpe(stitched, tf)
    rec_sharpe = source["walk_forward"]["oos_metrics"]["sharpe"]
    if not (abs(got_sharpe - rec_sharpe) <= REPLAY_TOL):
        raise LaneSkip(f"baseline replay mismatch for {lane['source_file']}: "
                       f"replayed stitched OOS Sharpe {got_sharpe!r} vs "
                       f"recorded {rec_sharpe!r} (tol {REPLAY_TOL}) — "
                       f"refusing to grade an unreproduced lane")
    # One same-window same-cost B&H over the full stitched OOS span (the
    # committed convention); its returns sliced positionally per split.
    oos_lo, oos_hi = segs[0]["test"][0], segs[-1]["test"][1]
    bench = buy_and_hold_result(ohlcv.iloc[oos_lo:oos_hi], timeframe=tf,
                                **BASELINE_COSTS)
    lengths = [len(s["returns"]) for s in segs]
    if sum(lengths) != len(bench.returns):
        raise LaneSkip(f"benchmark alignment failure for "
                       f"{lane['source_file']}: strategy segments total "
                       f"{sum(lengths)} bars vs benchmark "
                       f"{len(bench.returns)} — cannot pair splits")
    bench_segs, pos = [], 0
    for n in lengths:
        bench_segs.append(bench.returns.iloc[pos:pos + n])
        pos += n
    return source, segs, bench_segs, got_sharpe


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    lanes = sweeps.R5A_TARGET_LANES  # the one frozen Round-5 target set
    print(f"R5-B target set: {len(lanes)} frozen lanes")
    rollup_rows, skipped = [], []

    for i, lane in enumerate(lanes, 1):
        fam, tick, tf = lane["family"], lane["instrument"], lane["timeframe"]
        tag = f"{lane['sweep']} {fam} {tick} {tf}"
        row = {"lane_id": lane["lane_id"], "sweep": lane["sweep"],
               "strategy": fam, "instrument": tick, "timeframe": tf,
               "source_file": lane["source_file"]}
        try:
            source, segs, bench_segs, base_sharpe = prepare_lane(lane)
        except LaneSkip as exc:
            row["status"] = STATUS_SKIPPED
            row["skip_reason"] = str(exc)
            skipped.append(row)
            rollup_rows.append(row)
            print(f"[{i}/{len(lanes)}] {tag}: SKIPPED — {exc}")
            continue

        row["status"] = "GRADED"
        n_splits = len(segs)
        full_strat = pd.concat([s["returns"] for s in segs])
        full_bench = pd.concat(bench_segs)
        full_delta = (metrics.sharpe(full_strat, tf)
                      - metrics.sharpe(full_bench, tf))

        per_split_rows = []
        for k, (seg, bseg) in enumerate(zip(segs, bench_segs)):
            s_sh = metrics.sharpe(seg["returns"], tf)
            b_sh = metrics.sharpe(bseg, tf)
            per_split_rows.append({
                "split": k, "test": seg["test"], "params": seg["params"],
                "strategy_sharpe": _clean(s_sh),
                "benchmark_sharpe": _clean(b_sh),
                "delta": _clean(s_sh - b_sh),
            })

        loo_rows = []
        for k in range(n_splits):
            strat_loo = pd.concat([s["returns"]
                                   for j, s in enumerate(segs) if j != k])
            bench_loo = pd.concat([b for j, b in enumerate(bench_segs)
                                   if j != k])
            delta = (metrics.sharpe(strat_loo, tf)
                     - metrics.sharpe(bench_loo, tf))
            loo_rows.append({"left_out_split": k,
                             "stitched_delta": _clean(delta)})
        worst = min(loo_rows, key=lambda r: (r["stitched_delta"]
                                             if r["stitched_delta"]
                                             is not None else math.inf))
        worst_delta = worst["stitched_delta"]
        best_split = worst["left_out_split"]

        keep = worst_delta is not None and worst_delta > 0
        verdict = VERDICT_KEEP if keep else VERDICT_KILL
        grade = promotion.grade_promotion(
            strategy_sharpe=metrics.sharpe(full_strat, tf),
            benchmark_sharpe=metrics.sharpe(full_bench, tf),
            n_periods=int(len(full_strat)), timeframe=tf,
            variants_tried=source["variants_tried"])
        sweep_verdict = promotion.classify_verdict(keep, grade["tstat"],
                                                   grade["min_tstat"])

        record = {
            "schema_version": 1,
            "sweep": SWEEP_NAME,
            "created_utc": datetime.now(timezone.utc)
                                   .isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": fam,
            "instrument": tick,
            "timeframe": tf,
            "post_holdout_dev_only": True,
            "preregistered_in": ("docs/research-round-5-plan.md § R5-B — "
                                 "Time-split stability / "
                                 "leave-one-split-out"),
            "lane_id": lane["lane_id"],
            "source_lane": lane["source_file"],
            "costs": BASELINE_COSTS,
            "execution": "signal at bar t fills at bar t+1 open",
            "no_research": ("frozen replay of the lane's committed "
                            "walk-forward per-split params on the identical "
                            "positional test windows, then pure "
                            "re-aggregation — no selection pass, 0 new "
                            "registered configs"),
            "fidelity_guard": {"replayed_oos_sharpe": base_sharpe,
                               "matches_recorded": True,
                               "tolerance": REPLAY_TOL},
            "data_start": source["data_start"],
            "data_end": source["data_end"],
            "n_bars": source["n_bars"],
            "n_splits": n_splits,
            "full_stitched_delta": _clean(full_delta),
            "per_split": per_split_rows,
            "leave_one_out": loo_rows,
            "worst_case_loo_delta": _clean(worst_delta),
            "best_split_removed": best_split,
            "decision_rule": ("KEEP dev-candidate status iff the stitched "
                              "OOS Sharpe delta vs B&H remains > 0 after "
                              "removing the lane's single best test split "
                              "(argmin leave-one-out delta); else DEMOTED "
                              "to KILL (single-window luck)"),
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "promotion_grade": {
                "note": ("informational t at the lane's committed K — "
                         "promotion is CLOSED post-holdout"),
                **{k: _clean(v) for k, v in grade.items()},
            },
            "ledger": ("report-only slice, NOT ledgered (R4-B precedent): "
                       "0 new registered configs — pure replay/"
                       "re-aggregation of committed choices; "
                       "experiments/index.jsonl untouched"),
        }
        out = SWEEP_DIR / f"{lane['sweep']}__{fam}__{tick}__{tf}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        row.update({"full_stitched_delta": _clean(full_delta),
                    "worst_case_loo_delta": _clean(worst_delta),
                    "best_split_removed": best_split,
                    "verdict": verdict, "sweep_verdict": sweep_verdict,
                    "tstat": _clean(grade["tstat"]),
                    "detail_file": str(out.relative_to(config.REPO_ROOT))})
        rollup_rows.append(row)
        print(f"[{i}/{len(lanes)}] {tag}: full delta {full_delta:+.3f}, "
              f"worst LOO delta {worst_delta:+.3f} (split {best_split} "
              f"removed) -> {verdict}")

    graded = [r for r in rollup_rows if r["status"] == "GRADED"]
    counts = {
        "target_lanes": len(lanes),
        "graded": len(graded),
        "skipped": len(skipped),
        "keep": sum(1 for r in graded if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in graded if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in graded
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
    }
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "preregistered_in": ("docs/research-round-5-plan.md § R5-B — "
                             "Time-split stability / leave-one-split-out"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "target_set": ("the FROZEN top-5 KEEP-dev lanes of the plan "
                       "(trading_lab.sweeps.R5A_TARGET_LANES)"),
        "rule": ("per lane: KEEP iff the stitched OOS Sharpe delta vs B&H "
                 "remains > 0 with the single best test split removed "
                 "(worst-case leave-one-out); else DEMOTED to KILL"),
        "fidelity_guard": (f"every graded lane's baseline replay reproduced "
                           f"its committed stitched OOS Sharpe within "
                           f"{REPLAY_TOL}"),
        "burden": {"new_registered_configs": 0},
        "ledger_decision": ("report-only, NOT ledgered (R4-B precedent); "
                            "experiments/index.jsonl untouched"),
        "runtime_seconds": round(elapsed, 1),
        "runtime_cap_seconds": RUNTIME_CAP_SECONDS,
        "counts": counts,
        "lanes": rollup_rows,
    }
    out = SWEEP_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts['keep']} KEEP / {counts['kill']} KILL / "
          f"{counts['kill_sig']} KILL-SIG of {counts['graded']} graded "
          f"({counts['skipped']} skipped, {elapsed:.1f}s) -> {out}")
    for r in skipped:
        print(f"  SKIPPED: {r['lane_id']} — {r['skip_reason']}")
    if elapsed > RUNTIME_CAP_SECONDS:
        print(f"  RUNTIME CAP EXCEEDED: {elapsed:.1f}s > "
              f"{RUNTIME_CAP_SECONDS}s — record in the results doc")


if __name__ == "__main__":
    main()
