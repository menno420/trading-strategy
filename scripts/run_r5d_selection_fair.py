#!/usr/bin/env python3
"""Round 5 slice R5-D — selection-fair fixed-config replay of the top-5
KEEP-dev lanes (round-4 synthesis item 1).

POST-HOLDOUT, DEV-ONLY. Promotion is CLOSED: nothing this script produces
can be an out-of-sample claim; a lane that keeps its status is a
dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-5-plan.md`` § R5-D, merged BEFORE
this script existed. Registered method: replay each target lane's
committed top full-period variant (the plan's frozen table, pinned in
``trading_lab.sweeps.R5A_TARGET_LANES``) SELECTION-FREE — one fixed
config, no training pick — over the lane's exact committed walk-forward
test windows at baseline costs; report its stitched OOS Sharpe vs
same-window B&H and ``selection_gap = searched_stitched_sharpe -
fixed_stitched_sharpe`` machine-readably per lane.

Pre-registered decision rule (per lane): the lane KEEPS dev-candidate
status iff the fixed-config replay's stitched OOS Sharpe beats
same-window B&H; otherwise DEMOTED to KILL (the edge exists only through
in-window re-selection). ``selection_gap`` is informational — no
registered threshold. Informational t at the lane's committed K (12; bar
never lowered); KILL-SIG via ``classify_verdict``.

FIDELITY GUARD (standing rail, R4-B precedent): each lane's committed
searched walk-forward is replayed at baseline first and must reproduce
its committed stitched OOS Sharpe within 1e-8; an irreproducible lane is
recorded SKIPPED with the verbatim reason.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail
(``data_end <= 2025-01-08`` asserted per lane); ``unlock_holdout`` is
never passed. All ``experiments/sweeps/r3-*/`` files stay byte-untouched;
this slice writes ``experiments/sweeps/r5-selection-fair/``.

LEDGER DECISION (deliberate, R4-B precedent): report-only, NOT ledgered —
0 new registered configs (the fixed config IS the lane's
already-committed, already-ledgered top variant; a new row would
duplicate the r3 top-variant rows), and the R5-A grid commit covers any
neighbor overlap; ``experiments/index.jsonl`` untouched.

Runtime cap (pre-registered): <= 5 minutes wall-clock for the slice.

Usage: python3 scripts/run_r5d_selection_fair.py
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

SWEEP_NAME = "r5-selection-fair"
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


def stitched_replay(ohlcv, strategy_fn, rows, timeframe):
    """Replay per-split positions ([t0, t1] windows + params per row) at
    baseline costs and stitch the OOS returns. Signals for a test window
    may use trailing history before test_start (indicators are causal) but
    never anything >= test_end. No selection of any kind happens here."""
    rets, per = [], []
    for row in rows:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        res = run_backtest(ohlcv.iloc[t0:t1], pos, timeframe=timeframe,
                           **BASELINE_COSTS)
        rets.append(res.returns)
        per.append({"test": [t0, t1], "params": row["params"],
                    "test_sharpe": _clean(metrics.sharpe(res.returns,
                                                         timeframe))})
    return pd.concat(rets), per


def prepare_lane(lane: dict):
    """Load data and run the searched-arm fidelity guard. Raises LaneSkip
    with a verbatim reason on any mismatch."""
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
    searched, _ = stitched_replay(ohlcv, STRATEGIES[fam], per_split, tf)
    got_sharpe = metrics.sharpe(searched, tf)
    rec_sharpe = source["walk_forward"]["oos_metrics"]["sharpe"]
    if not (abs(got_sharpe - rec_sharpe) <= REPLAY_TOL):
        raise LaneSkip(f"baseline replay mismatch for {lane['source_file']}: "
                       f"replayed stitched OOS Sharpe {got_sharpe!r} vs "
                       f"recorded {rec_sharpe!r} (tol {REPLAY_TOL}) — "
                       f"refusing to grade an unreproduced lane")
    return source, ohlcv, per_split, got_sharpe


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    lanes = sweeps.R5A_TARGET_LANES  # the one frozen Round-5 target set
    print(f"R5-D target set: {len(lanes)} frozen lanes")
    rollup_rows, skipped = [], []

    for i, lane in enumerate(lanes, 1):
        fam, tick, tf = lane["family"], lane["instrument"], lane["timeframe"]
        tag = f"{lane['sweep']} {fam} {tick} {tf}"
        row = {"lane_id": lane["lane_id"], "sweep": lane["sweep"],
               "strategy": fam, "instrument": tick, "timeframe": tf,
               "source_file": lane["source_file"],
               "fixed_config": lane["top_variant"]}
        try:
            source, ohlcv, per_split, searched_sharpe = prepare_lane(lane)
        except LaneSkip as exc:
            row["status"] = STATUS_SKIPPED
            row["skip_reason"] = str(exc)
            skipped.append(row)
            rollup_rows.append(row)
            print(f"[{i}/{len(lanes)}] {tag}: SKIPPED — {exc}")
            continue

        row["status"] = "GRADED"
        windows = [[int(r["test"][0]), int(r["test"][1])]
                   for r in per_split]
        fixed_rows = [{"test": w, "params": lane["top_variant"]}
                      for w in windows]
        fixed, fixed_per = stitched_replay(ohlcv, STRATEGIES[fam],
                                           fixed_rows, tf)
        fixed_sharpe = metrics.sharpe(fixed, tf)
        oos_slice = ohlcv.iloc[windows[0][0]:windows[-1][1]]
        bench = buy_and_hold_result(oos_slice, timeframe=tf,
                                    **BASELINE_COSTS)
        bench_sharpe = metrics.sharpe(bench.returns, tf)
        selection_gap = searched_sharpe - fixed_sharpe

        keep = (not math.isnan(fixed_sharpe)
                and not math.isnan(bench_sharpe)
                and fixed_sharpe > bench_sharpe)
        verdict = VERDICT_KEEP if keep else VERDICT_KILL
        grade = promotion.grade_promotion(
            strategy_sharpe=fixed_sharpe, benchmark_sharpe=bench_sharpe,
            n_periods=int(len(fixed)), timeframe=tf,
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
            "preregistered_in": ("docs/research-round-5-plan.md § R5-D — "
                                 "Selection-fair fixed-config replay"),
            "lane_id": lane["lane_id"],
            "source_lane": lane["source_file"],
            "fixed_config": lane["top_variant"],
            "costs": BASELINE_COSTS,
            "execution": "signal at bar t fills at bar t+1 open",
            "no_research": ("selection-free replay of the lane's committed "
                            "top full-period variant over the identical "
                            "positional test windows — one fixed config, "
                            "no training pick, 0 new registered configs"),
            "fidelity_guard": {"replayed_searched_oos_sharpe":
                                   searched_sharpe,
                               "matches_recorded": True,
                               "tolerance": REPLAY_TOL},
            "data_start": source["data_start"],
            "data_end": source["data_end"],
            "n_bars": source["n_bars"],
            "searched_stitched_sharpe": _clean(searched_sharpe),
            "fixed_stitched_sharpe": _clean(fixed_sharpe),
            "benchmark_stitched_sharpe": _clean(bench_sharpe),
            "selection_gap": _clean(selection_gap),
            "selection_gap_note": ("searched_stitched_sharpe - "
                                   "fixed_stitched_sharpe; informational "
                                   "only — no registered threshold"),
            "fixed_per_split": fixed_per,
            "decision_rule": ("KEEP dev-candidate status iff the "
                              "fixed-config replay's stitched OOS Sharpe "
                              "beats same-window B&H; else DEMOTED to KILL "
                              "(edge exists only through in-window "
                              "re-selection)"),
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "promotion_grade": {
                "note": ("informational t at the lane's committed K — "
                         "promotion is CLOSED post-holdout"),
                **{k: _clean(v) for k, v in grade.items()},
            },
            "ledger": ("report-only slice, NOT ledgered (R4-B precedent): "
                       "the fixed config is the lane's already-ledgered "
                       "committed top variant; experiments/index.jsonl "
                       "untouched"),
        }
        out = SWEEP_DIR / f"{lane['sweep']}__{fam}__{tick}__{tf}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        row.update({"searched_stitched_sharpe": _clean(searched_sharpe),
                    "fixed_stitched_sharpe": _clean(fixed_sharpe),
                    "benchmark_stitched_sharpe": _clean(bench_sharpe),
                    "selection_gap": _clean(selection_gap),
                    "verdict": verdict, "sweep_verdict": sweep_verdict,
                    "tstat": _clean(grade["tstat"]),
                    "detail_file": str(out.relative_to(config.REPO_ROOT))})
        rollup_rows.append(row)
        print(f"[{i}/{len(lanes)}] {tag}: fixed {fixed_sharpe:.3f} vs bench "
              f"{bench_sharpe:.3f} (searched {searched_sharpe:.3f}, gap "
              f"{selection_gap:+.3f}) -> {verdict}")

    graded = [r for r in rollup_rows if r["status"] == "GRADED"]
    counts = {
        "target_lanes": len(lanes),
        "graded": len(graded),
        "skipped": len(skipped),
        "keep": sum(1 for r in graded if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in graded if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in graded
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
        "positive_selection_gap": sum(1 for r in graded
                                      if r["selection_gap"] is not None
                                      and r["selection_gap"] > 0),
    }
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "preregistered_in": ("docs/research-round-5-plan.md § R5-D — "
                             "Selection-fair fixed-config replay"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "target_set": ("the FROZEN top-5 KEEP-dev lanes of the plan "
                       "(trading_lab.sweeps.R5A_TARGET_LANES)"),
        "rule": ("per lane: KEEP iff the fixed-config (committed top "
                 "full-period variant) selection-free replay beats "
                 "same-window B&H on stitched OOS Sharpe; else DEMOTED to "
                 "KILL; selection_gap informational"),
        "fidelity_guard": (f"every graded lane's searched replay reproduced "
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
          f"{counts['kill_sig']} KILL-SIG of {counts['graded']} graded; "
          f"{counts['positive_selection_gap']} positive selection gaps "
          f"({counts['skipped']} skipped, {elapsed:.1f}s) -> {out}")
    for r in skipped:
        print(f"  SKIPPED: {r['lane_id']} — {r['skip_reason']}")
    if elapsed > RUNTIME_CAP_SECONDS:
        print(f"  RUNTIME CAP EXCEEDED: {elapsed:.1f}s > "
              f"{RUNTIME_CAP_SECONDS}s — record in the results doc")


if __name__ == "__main__":
    main()
