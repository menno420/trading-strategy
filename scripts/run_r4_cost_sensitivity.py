#!/usr/bin/env python3
"""Round 4 slice R4-B — execution-cost sensitivity re-grade of round-3 KEEPs.

POST-HOLDOUT, DEV-ONLY (ORDER 012 generative rung, 2026-07-13 night-run
direct order "continue with some new ideas"). Promotion is closed: nothing
this script produces can be an out-of-sample claim; a lane that survives
the stressed tiers is a dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-4-plan.md`` § "R4-B —
Execution-cost sensitivity re-grade of round-3 KEEPs", merged to main
BEFORE this script existed. Registered method: re-run the KEEP/KILL
grading of all round-3 KEEP-dev lanes at two stressed cost tiers —
**2×** baseline (10 bps slippage + 2 bp commission per side) and **4×**
baseline (20 bps + 4 bp) — "same rail, same walk-forward windows, same
chosen top variant per lane (no re-search: stressing costs must not
become a second selection pass)".

NO RE-SEARCH, implemented literally: this script never re-runs the
train-window grid selection. Each lane's committed r3 per-lane summary
records the walk-forward's chosen params per split (``walk_forward.
per_split[].params``) and the exact positional test windows; the script
recomputes those frozen positions (positions depend only on price data,
never on costs — the trades are IDENTICAL across tiers) and re-prices the
same stitched OOS at each stressed tier, benchmarked against same-window
buy-and-hold at the SAME stressed costs.

KEEP universe: the **58** lanes with ``new_verdict == "KEEP"`` in
``experiments/sweeps/r4-killsig-regrade/summary.json`` (R4-A, PR #100) —
the plan's "64 after PR #95" tally referred to the extended-round prose
count; the committed, machine-readable KEEP surface is these 58 rows
(same reconciliation as R4-A's 302-vs-~312 scope note).

Pre-registered kill criterion (per lane, per tier): KILL at that tier iff
stitched OOS Sharpe <= benchmark B&H Sharpe (same window, same stressed
costs) **or** <= 0; ties/ambiguity KILL. A lane keeps its dev-candidate
status only if it survives the 2× tier; the 4× tier is reported as a
robustness gradient. The ORDER 007 t-stat
(``trading_lab.promotion.grade_promotion``, the lane's own recorded K) is
recorded alongside — informational only — and
``trading_lab.promotion.classify_verdict`` flags any KILL-SIG at stressed
costs (R4-A's mirrored bar; evidence AGAINST a lane, never an inversion
signal).

FIDELITY GUARD (honesty rule): before stressing, every lane is replayed at
baseline costs (5 bps + 1 bp) and the stitched OOS Sharpe must reproduce
the committed number bit-for-bit (tolerance 1e-8). Any lane that cannot be
reproduced exactly — data drift, schema gap, missing strategy — is
recorded as **SKIPPED with the verbatim reason**, never approximated
silently.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (holdout
bars >= 2025-01-09 excluded; ``data_end <= 2025-01-08`` asserted per
lane); ``unlock_holdout`` is never passed. All ``experiments/sweeps/r3-*/``
files and ``experiments/runs/`` stay byte-untouched — this slice is
additive only, writing ``experiments/sweeps/r4-cost-sensitivity/``:
per-lane-per-tier JSONs (r3 per-lane schema core plus ``cost_tier``) and
one rollup ``summary.json``.

LEDGER DECISION (deliberate): report-only, NOT ledgered. No new config was
searched — the replayed variants are the lanes' already-committed choices,
so "top variant per lane per tier" ledger rows would duplicate the 58
r3-ledgered rows (same strategy/instrument/params) differing only in
costs, polluting ``experiments/index.jsonl`` with confusing near-identical
entries. The rollup and the results doc record this choice explicitly.

Usage: python3 scripts/run_r4_cost_sensitivity.py
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEP_NAME = "r4-cost-sensitivity"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME
KEEP_UNIVERSE_FILE = (config.EXPERIMENTS_DIR / "sweeps"
                      / "r4-killsig-regrade" / "summary.json")
EXPECTED_KEEP_COUNT = 58

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09.
DEV_DATA_END_MAX = "2025-01-08"

# Pre-registered stressed tiers — exact integer multiples of the committed
# baseline (config.DEFAULT_SLIPPAGE_BPS = 5, DEFAULT_COMMISSION_BPS = 1).
COST_TIERS = {
    "2x": {"slippage_bps": 2.0 * config.DEFAULT_SLIPPAGE_BPS,
           "commission_bps": 2.0 * config.DEFAULT_COMMISSION_BPS},
    "4x": {"slippage_bps": 4.0 * config.DEFAULT_SLIPPAGE_BPS,
           "commission_bps": 4.0 * config.DEFAULT_COMMISSION_BPS},
}
assert COST_TIERS["2x"] == {"slippage_bps": 10.0, "commission_bps": 2.0}
assert COST_TIERS["4x"] == {"slippage_bps": 20.0, "commission_bps": 4.0}

BASELINE_COSTS = {"slippage_bps": float(config.DEFAULT_SLIPPAGE_BPS),
                  "commission_bps": float(config.DEFAULT_COMMISSION_BPS)}

# Fidelity guard tolerance on the baseline stitched OOS Sharpe replay.
REPLAY_TOL = 1e-8

VERDICT_KEEP = "KEEP (dev-candidate only)"
VERDICT_KILL = "KILL"
STATUS_SKIPPED = "SKIPPED"


class LaneSkip(Exception):
    """Lane cannot be reproduced exactly — recorded verbatim, never
    approximated silently (pre-registered honesty rule)."""


def _clean(x):
    """NaN -> None for JSON."""
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def series_metrics(returns, equity, timeframe) -> dict:
    """Metrics computable from stitched OOS returns/equity alone (r3 shape)."""
    out = {
        "sharpe": metrics.sharpe(returns, timeframe),
        "sortino": metrics.sortino(returns, timeframe),
        "cagr": metrics.cagr(equity, timeframe),
        "total_return": metrics.total_return(equity),
        "max_drawdown": metrics.max_drawdown(equity),
        "n_bars": int(len(returns)),
    }
    return {k: _clean(v) for k, v in out.items()}


def frozen_positions(ohlcv, strategy_fn, per_split):
    """Recompute the walk-forward's already-chosen positions per test split.

    ``per_split`` rows come verbatim from the committed r3 summary: frozen
    params + positional test window. Signals for a test window may use
    trailing history from before test_start (indicators are causal) but
    never anything >= test_end — identical to trading_lab.walkforward.
    Positions depend only on price data, never on costs.
    """
    out = []
    for row in per_split:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        out.append({"test": [t0, t1], "params": row["params"],
                    "positions": pos})
    return out


def replay_at_costs(ohlcv, frozen, timeframe, *, slippage_bps,
                    commission_bps) -> dict:
    """Re-price the frozen per-split positions at the given per-side costs
    and stitch the OOS returns — the SAME trades, different execution
    costs. No selection of any kind happens here."""
    rets, per = [], []
    for row in frozen:
        t0, t1 = row["test"]
        res = run_backtest(ohlcv.iloc[t0:t1], row["positions"],
                           slippage_bps=slippage_bps,
                           commission_bps=commission_bps,
                           timeframe=timeframe)
        rets.append(res.returns)
        per.append({"test": [t0, t1], "params": row["params"],
                    "test_sharpe": _clean(metrics.sharpe(res.returns,
                                                         timeframe))})
    stitched = pd.concat(rets)
    equity = (1.0 + stitched).cumprod()
    return {"returns": stitched, "equity": equity, "per_split": per}


def grade_tier(oos_sharpe, bench_sharpe) -> bool:
    """Pre-registered R4-B rule: KEEP at a tier iff stitched OOS Sharpe >
    same-window same-cost B&H Sharpe AND > 0; ties/ambiguity KILL."""
    return (oos_sharpe is not None and bench_sharpe is not None
            and not (isinstance(oos_sharpe, float) and math.isnan(oos_sharpe))
            and not (isinstance(bench_sharpe, float) and math.isnan(bench_sharpe))
            and oos_sharpe > bench_sharpe and oos_sharpe > 0)


def load_keep_universe() -> list[dict]:
    report = json.loads(KEEP_UNIVERSE_FILE.read_text())
    keeps = [r for r in report["lanes"] if r["new_verdict"] == "KEEP"]
    if len(keeps) != EXPECTED_KEEP_COUNT:
        raise SystemExit(f"KEEP universe drifted: expected "
                         f"{EXPECTED_KEEP_COUNT}, found {len(keeps)} in "
                         f"{KEEP_UNIVERSE_FILE}")
    return keeps


def prepare_lane(source: dict, lane_path: str):
    """Load data, rebuild frozen positions, and run the baseline fidelity
    guard. Raises LaneSkip with a verbatim reason on any mismatch."""
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
            raise LaneSkip(f"cache drift vs committed lane {lane_path}: "
                           f"{field} recorded {source[field]!r}, loaded "
                           f"{got!r} — positional windows would misalign")
    per_split = source["walk_forward"]["per_split"]
    frozen = frozen_positions(ohlcv, STRATEGIES[fam], per_split)
    # Fidelity guard: baseline replay must reproduce the committed numbers.
    base = replay_at_costs(ohlcv, frozen, tf, **BASELINE_COSTS)
    got_sharpe = metrics.sharpe(base["returns"], tf)
    rec_sharpe = source["walk_forward"]["oos_metrics"]["sharpe"]
    if not (abs(got_sharpe - rec_sharpe) <= REPLAY_TOL):
        raise LaneSkip(f"baseline replay mismatch for {lane_path}: replayed "
                       f"stitched OOS Sharpe {got_sharpe!r} vs recorded "
                       f"{rec_sharpe!r} (tol {REPLAY_TOL}) — refusing to "
                       f"grade an unreproduced lane")
    return ohlcv, frozen, got_sharpe


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    keeps = load_keep_universe()
    print(f"KEEP universe: {len(keeps)} lanes "
          f"(from {KEEP_UNIVERSE_FILE.name}, R4-A / PR #100)")
    rollup_rows, skipped = [], []

    for i, lane in enumerate(sorted(keeps, key=lambda r: r["source_file"]), 1):
        lane_path = lane["source_file"]
        source = json.loads((config.REPO_ROOT / lane_path).read_text())
        fam, tick, tf = (source["family"], source["instrument"],
                         source["timeframe"])
        tag = f"{lane['sweep']} {fam} {tick} {tf}"
        row = {
            "sweep": lane["sweep"], "strategy": fam, "instrument": tick,
            "timeframe": tf, "source_file": lane_path,
            "baseline": {
                "costs": BASELINE_COSTS,
                "verdict": source["verdict"],
                "oos_sharpe": source["walk_forward"]["oos_metrics"]["sharpe"],
                "benchmark_oos_sharpe":
                    source["walk_forward"]["benchmark_oos_metrics"]["sharpe"],
                "tstat": source["promotion_grade"]["tstat"],
            },
        }
        try:
            ohlcv, frozen, base_sharpe = prepare_lane(source, lane_path)
        except LaneSkip as exc:
            row["status"] = STATUS_SKIPPED
            row["skip_reason"] = str(exc)
            skipped.append(row)
            rollup_rows.append(row)
            print(f"[{i}/{len(keeps)}] {tag}: SKIPPED — {exc}")
            continue

        row["status"] = "GRADED"
        row["baseline"]["replay_check"] = {
            "replayed_oos_sharpe": base_sharpe,
            "matches_recorded": True, "tolerance": REPLAY_TOL,
        }
        oos_lo, oos_hi = frozen[0]["test"][0], frozen[-1]["test"][1]
        oos_slice = ohlcv.iloc[oos_lo:oos_hi]
        row["tiers"] = {}
        for tier, costs in COST_TIERS.items():
            replay = replay_at_costs(ohlcv, frozen, tf, **costs)
            bench = buy_and_hold_result(oos_slice, timeframe=tf, **costs)
            oos_m = series_metrics(replay["returns"], replay["equity"], tf)
            bench_m = {k: _clean(v)
                       for k, v in metrics.compute_all(bench).items()}
            keep = grade_tier(oos_m["sharpe"], bench_m["sharpe"])
            verdict = VERDICT_KEEP if keep else VERDICT_KILL
            grade = promotion.grade_promotion(
                strategy_sharpe=oos_m["sharpe"],
                benchmark_sharpe=bench_m["sharpe"],
                n_periods=oos_m["n_bars"], timeframe=tf,
                variants_tried=source["variants_tried"])
            sweep_verdict = promotion.classify_verdict(
                keep, grade["tstat"], grade["min_tstat"])

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
                "order": "ORDER 012 night-run (control/inbox.md)",
                "preregistered_in": ("docs/research-round-4-plan.md § R4-B "
                                     "— Execution-cost sensitivity re-grade "
                                     "of round-3 KEEPs"),
                "cost_tier": tier,
                "cost_multiplier": {"2x": 2, "4x": 4}[tier],
                "costs": costs,
                "execution": "signal at bar t fills at bar t+1 open",
                "no_research": ("frozen replay of the lane's committed "
                                "walk-forward per-split params — the "
                                "train-window grid selection was NOT re-run "
                                "at stressed costs (pre-registered: "
                                "stressing costs must not become a second "
                                "selection pass); trades identical across "
                                "tiers, only execution costs differ"),
                "source_lane": lane_path,
                "source_sweep": lane["sweep"],
                "baseline": row["baseline"],
                "data_start": source["data_start"],
                "data_end": source["data_end"],
                "n_bars": source["n_bars"],
                "variants_tried": source["variants_tried"],
                "walk_forward": {
                    "train_size": source["walk_forward"]["train_size"],
                    "test_size": source["walk_forward"]["test_size"],
                    "n_splits": source["walk_forward"]["n_splits"],
                    "variants_tried":
                        source["walk_forward"]["variants_tried"],
                    "oos_start": source["walk_forward"]["oos_start"],
                    "oos_end": source["walk_forward"]["oos_end"],
                    "oos_metrics": oos_m,
                    "benchmark_oos_metrics": bench_m,
                    "per_split": replay["per_split"],
                },
                "kill_criterion": ("KILL at this tier iff stitched OOS "
                                   "Sharpe <= same-window same-cost B&H "
                                   "Sharpe or <= 0; ties/ambiguity KILL"),
                "verdict": verdict,
                "sweep_verdict": sweep_verdict,
                "promotion_grade": {
                    "note": ("ORDER 007 bar at the lane's own recorded K — "
                             "INFORMATIONAL ONLY, promotion is CLOSED "
                             "post-holdout (nothing here is a finding)"),
                    **grade,
                },
                "ledger": ("report-only sweep, NOT ledgered — no new config "
                           "was searched (frozen replay of committed "
                           "choices); ledgering would duplicate the r3 top-"
                           "variant rows at different costs"),
            }
            out = SWEEP_DIR / f"{lane['sweep']}__{fam}__{tick}__{tier}.json"
            out.write_text(json.dumps(record, indent=2, sort_keys=True)
                           + "\n")
            row["tiers"][tier] = {
                "verdict": verdict,
                "sweep_verdict": sweep_verdict,
                "oos_sharpe": oos_m["sharpe"],
                "benchmark_oos_sharpe": bench_m["sharpe"],
                "tstat": _clean(grade["tstat"]),
                "min_tstat": grade["min_tstat"],
                "detail_file": str(out.relative_to(config.REPO_ROOT)),
            }
        row["r4b_dev_candidate"] = (
            row["tiers"]["2x"]["verdict"] == VERDICT_KEEP)
        rollup_rows.append(row)
        t2, t4 = row["tiers"]["2x"], row["tiers"]["4x"]
        print(f"[{i}/{len(keeps)}] {tag}: base={base_sharpe:.3f} | "
              f"2x {t2['oos_sharpe']:.3f} vs bench {t2['benchmark_oos_sharpe']:.3f}"
              f" -> {t2['verdict']} | 4x {t4['oos_sharpe']:.3f} vs "
              f"{t4['benchmark_oos_sharpe']:.3f} -> {t4['verdict']}")

    graded = [r for r in rollup_rows if r["status"] == "GRADED"]
    counts = {
        "keep_universe": len(keeps),
        "graded": len(graded),
        "skipped": len(skipped),
        "survive_2x": sum(1 for r in graded
                          if r["tiers"]["2x"]["verdict"] == VERDICT_KEEP),
        "survive_4x": sum(1 for r in graded
                          if r["tiers"]["4x"]["verdict"] == VERDICT_KEEP),
        "kill_sig_2x": sum(1 for r in graded
                           if r["tiers"]["2x"]["sweep_verdict"]
                           == promotion.SWEEP_KILL_SIG),
        "kill_sig_4x": sum(1 for r in graded
                           if r["tiers"]["4x"]["sweep_verdict"]
                           == promotion.SWEEP_KILL_SIG),
    }
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "order": "ORDER 012 (generative rung)",
        "preregistered_in": ("docs/research-round-4-plan.md § R4-B — "
                             "Execution-cost sensitivity re-grade of "
                             "round-3 KEEPs"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "survivor is a dev-candidate only, never "
                                  "a finding"),
        "keep_universe": (f"the {EXPECTED_KEEP_COUNT} new_verdict==KEEP "
                          f"lanes of experiments/sweeps/r4-killsig-regrade/"
                          f"summary.json (R4-A, PR #100)"),
        "cost_tiers": {"baseline": BASELINE_COSTS, **COST_TIERS},
        "rule": ("per lane per tier: KILL iff stitched OOS Sharpe <= "
                 "same-window same-cost B&H Sharpe or <= 0; a lane keeps "
                 "dev-candidate status only if it survives the 2x tier; "
                 "4x is a robustness gradient"),
        "no_research": ("frozen replay of each lane's committed walk-forward "
                        "per-split params on the same test windows — NO "
                        "second selection pass (pre-registered); trades "
                        "identical across tiers"),
        "fidelity_guard": (f"every graded lane's baseline replay reproduced "
                           f"its committed stitched OOS Sharpe within "
                           f"{REPLAY_TOL}; irreproducible lanes recorded "
                           f"SKIPPED with the verbatim reason"),
        "ledger_decision": ("report-only sweep, NOT ledgered (deliberate): "
                            "no new config was searched, so top-variant "
                            "ledger rows would duplicate the 58 committed "
                            "r3 rows at different costs — "
                            "experiments/index.jsonl untouched"),
        "runtime_seconds": round(elapsed, 1),
        "counts": counts,
        "lanes": rollup_rows,
    }
    out = SWEEP_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: of {counts['keep_universe']} KEEP-dev lanes — "
          f"{counts['survive_2x']} survive 2x, {counts['survive_4x']} "
          f"survive 4x, {counts['kill_sig_2x']}/{counts['kill_sig_4x']} "
          f"KILL-SIG at 2x/4x, {counts['skipped']} skipped "
          f"({elapsed:.1f}s) -> {out}")
    for r in skipped:
        print(f"  SKIPPED: {r['sweep']} {r['strategy']} {r['instrument']} "
              f"{r['timeframe']} — {r['skip_reason']}")


if __name__ == "__main__":
    main()
