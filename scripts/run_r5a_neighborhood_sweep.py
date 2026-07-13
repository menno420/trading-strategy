#!/usr/bin/env python3
"""Round 5 slice R5-A — parameter-neighborhood stability of the top-5
KEEP-dev lanes.

POST-HOLDOUT, DEV-ONLY. Promotion is CLOSED: nothing this script produces
can be an out-of-sample claim; a lane that keeps its status is a
dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-5-plan.md`` § R5-A, merged BEFORE
this script existed. The ±1-grid-step neighbors of each target lane's
committed top full-period variant were pre-declared in
``trading_lab.sweeps`` (``R5A_TARGET_LANES`` / ``r5a_neighbors``) WITH
tests and committed BEFORE this sweep ran. Registered method: replay each
neighbor SELECTION-FREE (one fixed config, no training pick) over the
lane's exact committed walk-forward test windows at baseline costs
(5 bps + 1 bp per side) and compare its stitched OOS Sharpe to
same-window B&H.

Pre-registered decision rule (per lane): the lane KEEPS dev-candidate
status iff >= 50% of its replayed neighbors beat same-window B&H stitched
OOS Sharpe; otherwise DEMOTED to KILL (knife-edge). KILL-SIG per
``trading_lab.promotion.classify_verdict`` if any lane-level t crosses
the mirrored bar — mechanized here as: a KILLed lane is KILL-SIG iff its
WORST neighbor's informational t (graded at the lane's committed K = 12;
the bar is never lowered) crosses -min_tstat. No neighbor can become a
candidate itself: neighbors are probes, not entrants, and no Round-5
result selects a configuration.

FIDELITY GUARD (standing rail, R4-B precedent): before any neighbor is
replayed, the lane's committed walk-forward per-split params are replayed
at baseline costs and the stitched OOS Sharpe must reproduce the
committed number within 1e-8. An irreproducible lane is recorded SKIPPED
with the verbatim reason, never silently regraded.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail
(holdout bars >= 2025-01-09 excluded; ``data_end <= 2025-01-08`` asserted
per lane); ``unlock_holdout`` is never passed. All
``experiments/sweeps/r3-*/`` files stay byte-untouched — this slice is
additive only, writing ``experiments/sweeps/r5-neighborhood/``.

LEDGER DECISION (deliberate, the R4-C side of the R4-B/R4-C precedent):
LEDGERED — each neighbor replay is a genuinely NEW run with a return
stream no existing ledger row describes (the r3 lanes ledgered only the
searched top variant per lane; the neighbors' selection-free stitched OOS
replays are new). One row per neighbor, ``variants_tried=1`` (the literal
count — no search inside a probe), probe-not-entrant caveat in the notes;
``experiments/index.jsonl`` rebuilt.

Runtime cap (pre-registered): <= 10 minutes wall-clock for the slice.

Usage: python3 scripts/run_r5a_neighborhood_sweep.py
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
from trading_lab.engine import (BacktestResult, buy_and_hold_result,  # noqa: E402
                                run_backtest)
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEP_NAME = "r5-neighborhood"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09.
DEV_DATA_END_MAX = "2025-01-08"

BASELINE_COSTS = {"slippage_bps": float(config.DEFAULT_SLIPPAGE_BPS),
                  "commission_bps": float(config.DEFAULT_COMMISSION_BPS)}
assert BASELINE_COSTS == {"slippage_bps": 5.0, "commission_bps": 1.0}

# Fidelity guard tolerance on the baseline stitched OOS Sharpe replay.
REPLAY_TOL = 1e-8

VERDICT_KEEP = "KEEP (dev-candidate only)"
VERDICT_KILL = "KILL"
STATUS_SKIPPED = "SKIPPED"

RUNTIME_CAP_SECONDS = 600  # pre-registered: <= 10 minutes wall-clock


class LaneSkip(Exception):
    """Lane cannot be reproduced exactly — recorded verbatim, never
    approximated silently (pre-registered honesty rule)."""


def _clean(x):
    """NaN -> None for JSON."""
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def fixed_config_positions(ohlcv, strategy_fn, params, windows):
    """SELECTION-FREE positions for one fixed config over the committed
    positional test windows: signals for a test window may use trailing
    history from before test_start (indicators are causal) but never
    anything >= test_end — identical to trading_lab.walkforward. There is
    no training pick anywhere in this function."""
    out = []
    for t0, t1 in windows:
        pos = strategy_fn(ohlcv.iloc[:t1], **params).iloc[t0:t1]
        out.append({"test": [t0, t1], "params": params, "positions": pos})
    return out


def frozen_positions(ohlcv, strategy_fn, per_split):
    """Recompute the walk-forward's already-chosen positions per test
    split (committed frozen params + positional test windows, verbatim
    from the r3 summary) — the R4-B fidelity-guard replay."""
    out = []
    for row in per_split:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        out.append({"test": [t0, t1], "params": row["params"],
                    "positions": pos})
    return out


def replay_stitched(ohlcv, frozen, timeframe) -> dict:
    """Re-price per-split positions at baseline costs and stitch the OOS.
    No selection of any kind happens here."""
    rets, helds, trades, per = [], [], [], []
    for row in frozen:
        t0, t1 = row["test"]
        res = run_backtest(ohlcv.iloc[t0:t1], row["positions"],
                           timeframe=timeframe, **BASELINE_COSTS)
        rets.append(res.returns)
        helds.append(res.held)
        trades.append(res.trades)
        per.append({"test": [t0, t1],
                    "test_sharpe": _clean(metrics.sharpe(res.returns,
                                                         timeframe))})
    returns = pd.concat(rets)
    equity = (1.0 + returns).cumprod()
    result = BacktestResult(
        equity=equity, returns=returns, held=pd.concat(helds),
        trades=pd.concat(trades, ignore_index=True),
        cost_bps_per_side=(BASELINE_COSTS["slippage_bps"]
                           + BASELINE_COSTS["commission_bps"]),
        timeframe=timeframe,
        meta={**BASELINE_COSTS,
              "execution": "signal at bar t fills at bar t+1 open"})
    return {"result": result, "per_split": per}


def prepare_lane(lane: dict):
    """Load data, run the baseline fidelity guard, and return the
    ingredients every neighbor replay shares. Raises LaneSkip with a
    verbatim reason on any mismatch."""
    source = json.loads((config.REPO_ROOT / lane["source_file"]).read_text())
    fam, tick, tf = source["family"], source["instrument"], source["timeframe"]
    assert (fam, tick, tf) == (lane["family"], lane["instrument"],
                               lane["timeframe"]), "target table drifted"
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
    frozen = frozen_positions(ohlcv, STRATEGIES[fam], per_split)
    base = replay_stitched(ohlcv, frozen, tf)
    got_sharpe = metrics.sharpe(base["result"].returns, tf)
    rec_sharpe = source["walk_forward"]["oos_metrics"]["sharpe"]
    if not (abs(got_sharpe - rec_sharpe) <= REPLAY_TOL):
        raise LaneSkip(f"baseline replay mismatch for {lane['source_file']}: "
                       f"replayed stitched OOS Sharpe {got_sharpe!r} vs "
                       f"recorded {rec_sharpe!r} (tol {REPLAY_TOL}) — "
                       f"refusing to grade an unreproduced lane")
    windows = [tuple(row["test"]) for row in per_split]
    return source, ohlcv, windows, got_sharpe


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    lanes = sweeps.R5A_TARGET_LANES
    print(f"R5-A target set: {len(lanes)} frozen lanes, "
          f"{sweeps.r5a_total_configs()} pre-declared neighbors")
    rollup_rows, skipped, ledger_files = [], [], []

    for i, lane in enumerate(lanes, 1):
        fam, tick, tf = lane["family"], lane["instrument"], lane["timeframe"]
        tag = f"{lane['sweep']} {fam} {tick} {tf}"
        neighbors = sweeps.r5a_neighbors(lane["lane_id"])
        row = {
            "lane_id": lane["lane_id"], "sweep": lane["sweep"],
            "strategy": fam, "instrument": tick, "timeframe": tf,
            "source_file": lane["source_file"],
            "top_variant": lane["top_variant"],
            "n_neighbors": len(neighbors),
        }
        try:
            source, ohlcv, windows, base_sharpe = prepare_lane(lane)
        except LaneSkip as exc:
            row["status"] = STATUS_SKIPPED
            row["skip_reason"] = str(exc)
            skipped.append(row)
            rollup_rows.append(row)
            print(f"[{i}/{len(lanes)}] {tag}: SKIPPED — {exc}")
            continue

        row["status"] = "GRADED"
        row["baseline"] = {
            "costs": BASELINE_COSTS,
            "verdict": source["verdict"],
            "oos_sharpe": source["walk_forward"]["oos_metrics"]["sharpe"],
            "benchmark_oos_sharpe":
                source["walk_forward"]["benchmark_oos_metrics"]["sharpe"],
            "tstat": source["promotion_grade"]["tstat"],
            "replay_check": {"replayed_oos_sharpe": base_sharpe,
                             "matches_recorded": True,
                             "tolerance": REPLAY_TOL},
        }
        oos_slice = ohlcv.iloc[windows[0][0]:windows[-1][1]]
        bench = buy_and_hold_result(oos_slice, timeframe=tf,
                                    **BASELINE_COSTS)
        bench_sharpe = metrics.sharpe(bench.returns, tf)
        neighbor_rows, tstats = [], []
        for nb in neighbors:
            fixed = fixed_config_positions(ohlcv, STRATEGIES[fam], nb,
                                           windows)
            replay = replay_stitched(ohlcv, fixed, tf)
            nb_sharpe = metrics.sharpe(replay["result"].returns, tf)
            beats = (not math.isnan(nb_sharpe)
                     and not math.isnan(bench_sharpe)
                     and nb_sharpe > bench_sharpe)
            grade = promotion.grade_promotion(
                strategy_sharpe=nb_sharpe, benchmark_sharpe=bench_sharpe,
                n_periods=int(len(replay["result"].returns)), timeframe=tf,
                variants_tried=source["variants_tried"])
            tstats.append(grade["tstat"])
            neighbor_rows.append({
                "params": nb,
                "oos_sharpe": _clean(nb_sharpe),
                "benchmark_oos_sharpe": _clean(bench_sharpe),
                "beats_bh": beats,
                "tstat": _clean(grade["tstat"]),
                "min_tstat": grade["min_tstat"],
                "per_split": replay["per_split"],
            })
            # Ledger: one row per neighbor — a genuinely NEW run (see
            # module docstring). variants_tried=1 is the literal count.
            led = ledger.build_record(
                strategy=fam, params=nb, instrument=tick, timeframe=tf,
                ohlcv=oos_slice, result=replay["result"], benchmark=bench,
                variants_tried=1,
                notes=("R5-A parameter-neighborhood PROBE "
                       "(docs/research-round-5-plan.md § R5-A; post-holdout "
                       "DEV-ONLY, promotion closed). Selection-free stitched "
                       "walk-forward OOS replay of a pre-declared +/-1-step "
                       "neighbor of the committed top variant of "
                       f"{lane['lane_id']} — a probe, NEVER an entrant or "
                       "candidate; metrics are over the stitched OOS window, "
                       "not a single-window run."))
            ledger_files.append(str(ledger.write_run(led)
                                    .relative_to(config.REPO_ROOT)))

        n_beat = sum(1 for r in neighbor_rows if r["beats_bh"])
        frac = n_beat / len(neighbor_rows)
        keep = frac >= 0.5
        verdict = VERDICT_KEEP if keep else VERDICT_KILL
        worst_t = min(tstats)
        bar = promotion.min_tstat(source["variants_tried"])
        sweep_verdict = promotion.classify_verdict(keep, worst_t, bar)

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
            "preregistered_in": ("docs/research-round-5-plan.md § R5-A — "
                                 "Parameter-neighborhood stability"),
            "lane_id": lane["lane_id"],
            "source_lane": lane["source_file"],
            "top_variant": lane["top_variant"],
            "costs": BASELINE_COSTS,
            "execution": "signal at bar t fills at bar t+1 open",
            "no_research": ("selection-free fixed-config replays of "
                            "pre-declared +/-1-step neighbors over the "
                            "lane's exact committed walk-forward test "
                            "windows — no training pick, no selection on "
                            "outcome; neighbors are probes, not entrants"),
            "baseline": row["baseline"],
            "data_start": source["data_start"],
            "data_end": source["data_end"],
            "n_bars": source["n_bars"],
            "neighbors": neighbor_rows,
            "decision_rule": ("KEEP dev-candidate status iff >= 50% of "
                              "replayed neighbors beat same-window B&H "
                              "stitched OOS Sharpe; else DEMOTED to KILL "
                              "(knife-edge). KILL-SIG iff a KILLed lane's "
                              "worst neighbor t <= -min_tstat(K=12) — the "
                              "mirrored bar, never lowered."),
            "n_neighbors": len(neighbor_rows),
            "n_beat_bh": n_beat,
            "frac_beat_bh": frac,
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "promotion_grade_note": ("neighbor t-stats graded at the lane's "
                                     "committed K = "
                                     f"{source['variants_tried']} (bar "
                                     f"{bar:.6f}) — INFORMATIONAL ONLY, "
                                     "promotion is CLOSED post-holdout"),
            "ledger": ("LEDGERED (deliberate, R4-C precedent): each "
                       "neighbor replay is a genuinely new run with a "
                       "return stream no existing row describes; one row "
                       "per neighbor, variants_tried=1, probe caveat in "
                       "the notes"),
        }
        out = SWEEP_DIR / f"{lane['sweep']}__{fam}__{tick}__{tf}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        row.update({"n_beat_bh": n_beat, "frac_beat_bh": frac,
                    "verdict": verdict, "sweep_verdict": sweep_verdict,
                    "worst_neighbor_tstat": _clean(worst_t),
                    "detail_file": str(out.relative_to(config.REPO_ROOT))})
        rollup_rows.append(row)
        print(f"[{i}/{len(lanes)}] {tag}: {n_beat}/{len(neighbor_rows)} "
              f"neighbors beat B&H ({frac:.0%}) -> {verdict}")

    ledger.rebuild_index()
    graded = [r for r in rollup_rows if r["status"] == "GRADED"]
    counts = {
        "target_lanes": len(lanes),
        "graded": len(graded),
        "skipped": len(skipped),
        "keep": sum(1 for r in graded if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in graded if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in graded
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
        "neighbors_replayed": sum(r.get("n_neighbors", 0) for r in graded),
    }
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "preregistered_in": ("docs/research-round-5-plan.md § R5-A — "
                             "Parameter-neighborhood stability"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "target_set": ("the FROZEN top-5 KEEP-dev lanes of the plan "
                       "(trading_lab.sweeps.R5A_TARGET_LANES) — no "
                       "swap-ins, no re-ranking"),
        "rule": ("per lane: KEEP iff >= 50% of pre-declared +/-1-step "
                 "neighbors beat same-window B&H stitched OOS Sharpe in a "
                 "selection-free replay; else DEMOTED to KILL (knife-edge); "
                 "KILL-SIG at the mirrored K=12 bar via classify_verdict"),
        "fidelity_guard": (f"every graded lane's baseline replay reproduced "
                           f"its committed stitched OOS Sharpe within "
                           f"{REPLAY_TOL}; irreproducible lanes recorded "
                           f"SKIPPED with the verbatim reason"),
        "burden": {"new_registered_configs": sweeps.r5a_total_configs(),
                   "program_cumulative_before": 4345,
                   "program_cumulative_after":
                       4345 + sweeps.r5a_total_configs()},
        "ledger_decision": ("LEDGERED (R4-C precedent): genuinely-new "
                            "neighbor replays, one row each, "
                            "variants_tried=1, probe caveat in notes; "
                            "experiments/index.jsonl rebuilt"),
        "ledger_files": ledger_files,
        "runtime_seconds": round(elapsed, 1),
        "runtime_cap_seconds": RUNTIME_CAP_SECONDS,
        "counts": counts,
        "lanes": rollup_rows,
    }
    out = SWEEP_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts['keep']} KEEP / {counts['kill']} KILL / "
          f"{counts['kill_sig']} KILL-SIG of {counts['graded']} graded "
          f"({counts['neighbors_replayed']} neighbors, {counts['skipped']} "
          f"skipped, {elapsed:.1f}s) -> {out}")
    for r in skipped:
        print(f"  SKIPPED: {r['lane_id']} — {r['skip_reason']}")
    if elapsed > RUNTIME_CAP_SECONDS:
        print(f"  RUNTIME CAP EXCEEDED: {elapsed:.1f}s > "
              f"{RUNTIME_CAP_SECONDS}s — record in the results doc")


if __name__ == "__main__":
    main()
