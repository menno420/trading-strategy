#!/usr/bin/env python3
"""Round 8 — hourly companion for the R7 families × 8 hourly tickers (lane r8-hourly).

POST-HOLDOUT, DEV-ONLY (owner GO 2026-07-18T13:47Z; pre-registered protocol:
``docs/research-round-8-plan.md``, merged BEFORE any Round-8 outcome existed as
PR #149). Promotion is CLOSED: nothing this script produces can be an
out-of-sample claim; KEEPs are dev-candidates only.

HOURLY COMPANION for the two NEWEST R7 single-instrument families — R7-A
``drawdown_reversion`` and R7-B ``high_proximity`` — with the IDENTICAL R7
12-variant grids (grid identity with the daily R7 axes pinned by tests), on
the committed 8-ticker hourly caches. NO new strategy code, NO new parameter
territory: the same window NUMBERS re-registered on hourly bars per the
p1-trend-hourly / R6-C convention, isolating the single variable of bar
frequency (the Round-3 slice-5/14/15 and Round-6 R6-C timeframe-expansion
precedent). Grid declared in ``trading_lab.sweeps`` BEFORE this script ran:
12 variants per family × 8 tickers = 192 registered configs. Program burden
prior to this slice: 5601 (round-7D closing tally); program cumulative after:
5793. KNOWN weakness recorded in the plan: the short dev-rail hourly history
gives ~5 walk-forward splits per lane — a SINGLE ~8.5-month 2024 regime, the
program's thinnest evidence-per-config; R5-B demoted the program's only prior
hourly KEEP for exactly this single-window-luck exposure, so any hourly KEEP
here inherits that caveat.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded). Costs: engine defaults, 5 bps slippage + 1 bp
commission per side. Execution: signal at bar t fills at bar t+1 open.

Per lane, the same four artifacts as R6-C (``run_r6_volume_hourly_sweep.py``):
full-period bookkeeping rows, the 1008/252-BAR walk-forward (lab convention on
hourly bars too) graded by the Round-2 rule + ``classify_verdict`` at K=12,
the selection-fair standing gate ([D-0002]) on EVERY lane (its block = the
R5-D fixed-config row), and one ledger run for the top full-period variant
(``variants_tried=12``). A cache too short for one 1008/252 split records the
honest first-class INSUFFICIENT-DATA verdict (r3-trend-hourly precedent) —
the method is never bent.

Runtime cap (pre-registered): <= 900 s wall-clock for the whole slice,
checked before each lane; overrun STOPS the slice and records the partial
state + skipped lanes — no silent truncation.

Usage: python3 scripts/run_r8_hourly_sweep.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, selection_gate, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

SLICE = "r8-hourly"
TIMEFRAME = "hourly"
TRAIN_SIZE = 1008  # lab convention, in BARS (~7 months of hourly bars)
TEST_SIZE = 252    # in BARS (~7 weeks); step defaults to TEST_SIZE
CAP_SECONDS = 900  # pre-registered: <= 15 min wall-clock for the slice

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SLICE

# Program burden prior to this slice: 5601 (round-7D closing tally), per the
# plan's burden ledger (5601 -> 5793, 192 new configs).
PROGRAM_PRIOR_CONFIGS = 5601

VERDICT_INSUFFICIENT = "INSUFFICIENT-DATA"

VARIANT_METRIC_KEYS = ("sharpe", "sortino", "cagr", "total_return",
                      "max_drawdown", "win_rate", "turnover_per_year",
                      "n_trades")

COSTS = {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
         "commission_bps": config.DEFAULT_COMMISSION_BPS}


def series_metrics(returns, equity) -> dict:
    """Metrics computable from stitched OOS returns/equity alone."""
    out = {
        "sharpe": metrics.sharpe(returns, TIMEFRAME),
        "sortino": metrics.sortino(returns, TIMEFRAME),
        "cagr": metrics.cagr(equity, TIMEFRAME),
        "total_return": metrics.total_return(equity),
        "max_drawdown": metrics.max_drawdown(equity),
        "n_bars": int(len(returns)),
    }
    return {k: (None if isinstance(v, float) and v != v else v)
            for k, v in out.items()}


def run_lane(ticker: str, family: str, grid_sizes: dict, lane_configs: int,
             program_cumulative: int) -> dict:
    """Run one family × ticker lane end-to-end and write its JSON."""
    ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
    variants = sweeps.r8_hourly_variants(family)
    strategy_fn = STRATEGIES[family]
    out = SWEEP_DIR / f"{family}__{ticker}.json"

    # Honest first-class insufficient-data verdict (r3-trend-hourly
    # precedent): the established split needs at least TRAIN+TEST bars;
    # do not bend the method.
    if len(ohlcv) < TRAIN_SIZE + TEST_SIZE:
        record = {
            "schema_version": 1,
            "sweep": SLICE,
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": family,
            "instrument": ticker,
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": "owner GO 2026-07-18T13:47Z; "
                     "pre-registered docs/research-round-8-plan.md",
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "verdict": VERDICT_INSUFFICIENT,
            "walk_forward": {
                "train_size": TRAIN_SIZE,
                "test_size": TEST_SIZE,
                "n_splits": 0,
                "note": (f"{len(ohlcv)} bars < {TRAIN_SIZE + TEST_SIZE} "
                         f"needed for one 1008/252 split — no OOS number "
                         f"exists for this lane"),
            },
        }
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(f"{ticker} {family}: n_bars={len(ohlcv)} "
              f"{VERDICT_INSUFFICIENT} -> {out.name}")
        return {"instrument": ticker, "family": family,
                "oos_sharpe": None, "bench_sharpe": None, "tstat": None,
                "min_tstat": None, "gate": None, "gate_reason": None,
                "fixed_sharpe": None, "selection_gap": None,
                "verdict_pre_gate": VERDICT_INSUFFICIENT,
                "verdict": VERDICT_INSUFFICIENT}

    # 1) full-dev-period backtest per variant (bookkeeping rows)
    rows = []
    for params in variants:
        res = run_backtest(ohlcv, strategy_fn(ohlcv, **params),
                           timeframe=TIMEFRAME)
        m = metrics.compute_all(res)
        rows.append({"params": params,
                     "metrics": {k: m[k] for k in VARIANT_METRIC_KEYS}})

    # 2) walk-forward OOS — the only reportable number (dev-only)
    wf = walk_forward(ohlcv, strategy_fn, variants,
                      train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                      timeframe=TIMEFRAME)
    first, last = wf["splits"][0]["split"], wf["splits"][-1]["split"]
    oos_slice = ohlcv.iloc[first.test_start:last.test_end]
    bench_oos = buy_and_hold_result(oos_slice, timeframe=TIMEFRAME)

    # 3) ledger run for the top full-period variant (variants_tried=12)
    top = max(rows, key=lambda r: (r["metrics"]["sharpe"]
                                   if r["metrics"]["sharpe"] is not None
                                   else float("-inf")))
    run_path = ledger.run_and_record(
        strategy=family, instrument=ticker, timeframe=TIMEFRAME,
        ohlcv=ohlcv, params=top["params"],
        variants_tried=len(variants),
        notes=(f"Round 8 hourly companion sweep (post-holdout DEV-ONLY, "
               f"promotion closed — owner GO 2026-07-18T13:47Z; "
               f"pre-registered docs/research-round-8-plan.md): top "
               f"full-dev-period variant of {len(variants)} tried "
               f"(post-hoc selection — in-sample; the walk-forward OOS "
               f"number and the selection-fair gate block live in "
               f"experiments/sweeps/{SLICE}/{family}__{ticker}.json)"),
    )

    oos_m = series_metrics(wf["oos_returns"], wf["oos_equity"])
    bench_oos_m = metrics.compute_all(bench_oos)
    oos_sharpe, bench_sharpe = oos_m["sharpe"], bench_oos_m["sharpe"]
    # Round-2 KEEP/KILL rule; ties/ambiguity resolve KILL.
    keep = (oos_sharpe is not None and bench_sharpe is not None
            and oos_sharpe > bench_sharpe and oos_sharpe > 0)
    # ORDER 007 promotion-bar arithmetic — informational only: promotion
    # is CLOSED post-holdout, nothing here can promote.
    if oos_sharpe is not None and bench_sharpe is not None:
        grade = promotion.grade_promotion(
            strategy_sharpe=oos_sharpe, benchmark_sharpe=bench_sharpe,
            n_periods=oos_m["n_bars"], timeframe=TIMEFRAME,
            variants_tried=len(variants))
    else:  # degenerate stitched returns — honest KILL, no arithmetic
        grade = {"verdict": None, "tstat": None,
                 "min_tstat": promotion.min_tstat(len(variants)),
                 "note": "not computable: stitched OOS or benchmark "
                         "Sharpe is NaN (degenerate returns)"}
    verdict_pre_gate = promotion.classify_verdict(
        keep, grade.get("tstat"), grade.get("min_tstat"))

    # Selection-fair standing gate ([D-0002]) — EVERY lane, fidelity guard
    # armed with the lane's own searched stitched OOS Sharpe. The gate
    # block doubles as the R5-D fixed-config row (standing rule 2).
    gate_per_split = [
        {"test": [s["split"].test_start, s["split"].test_end],
         "params": s["params"]} for s in wf["splits"]]
    gate = selection_gate.run_selection_gate(
        ohlcv=ohlcv, strategy=strategy_fn, per_split=gate_per_split,
        top_variant=top["params"], timeframe=TIMEFRAME, costs=COSTS,
        recorded_searched_sharpe=oos_sharpe)
    verdict = selection_gate.apply_gate(verdict_pre_gate, gate)

    bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
    sweep_record = {
        "schema_version": 1,
        "sweep": SLICE,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": ledger.git_sha(),
        "family": family,
        "instrument": ticker,
        "timeframe": TIMEFRAME,
        "post_holdout_dev_only": True,
        "order": "owner GO 2026-07-18T13:47Z; "
                 "pre-registered docs/research-round-8-plan.md",
        "data_start": str(ohlcv.index[0]),
        "data_end": str(ohlcv.index[-1]),
        "n_bars": int(len(ohlcv)),
        "costs": dict(COSTS),
        "execution": "signal at bar t fills at bar t+1 open",
        "variants_tried": len(variants),
        "family_variants_tried": (grid_sizes[family]
                                  * len(sweeps.R8_HOURLY_INSTRUMENTS)),
        "lane_variants_tried": lane_configs,
        "program_variants_tried": program_cumulative,
        "full_period_variants": {
            "note": ("single-split in-sample rows for deflated-Sharpe "
                     "bookkeeping — NOT findings"),
            "rows": rows,
        },
        "walk_forward": {
            "train_size": TRAIN_SIZE,
            "test_size": TEST_SIZE,
            "n_splits": len(wf["splits"]),
            "variants_tried": wf["variants_tried"],
            "oos_start": str(oos_slice.index[0]),
            "oos_end": str(oos_slice.index[-1]),
            "oos_metrics": oos_m,
            "benchmark_oos_metrics": bench_oos_m,
            "per_split": [{
                "train": [s["split"].train_start, s["split"].train_end],
                "test": [s["split"].test_start, s["split"].test_end],
                "params": s["params"],
                "train_score": (None if s["train_score"] != s["train_score"]
                                else s["train_score"]),
                "test_sharpe": (None if s["test_sharpe"] != s["test_sharpe"]
                                else s["test_sharpe"]),
            } for s in wf["splits"]],
        },
        "benchmark_full_period_metrics": metrics.compute_all(bench_full),
        "top_full_period_variant": {"params": top["params"],
                                    "metrics": top["metrics"],
                                    "ledger_run": run_path.name},
        "selection_gate": {
            "note": ("standing gate [D-0002] (docs/selection-fair-gate.md), "
                     "run on EVERY Round-8 lane; doubles as the R5-D "
                     "fixed-config row — selection_gap informational, no "
                     "registered threshold; gate replay is report-only "
                     "(R4-B precedent), not ledgered"),
            **gate,
        },
        "verdict_pre_gate": verdict_pre_gate,
        "verdict": verdict,
        "promotion_grade": {
            "note": ("ORDER 007 bar on the stitched OOS Sharpe delta, "
                     "Bonferroni K = variants this lane — INFORMATIONAL "
                     "ONLY, promotion is CLOSED post-holdout (nothing "
                     "here is a finding)"),
            **grade,
        },
    }
    out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
    print(f"{ticker} {family}: oos_sharpe={oos_sharpe} "
          f"bench={bench_sharpe} t={grade.get('tstat')} "
          f"gate={gate['gate']} {verdict} -> {out.name}")
    return {"instrument": ticker, "family": family,
            "oos_sharpe": oos_sharpe, "bench_sharpe": bench_sharpe,
            "tstat": grade.get("tstat"), "min_tstat": grade.get("min_tstat"),
            "gate": gate["gate"], "gate_reason": gate["reason"],
            "fixed_sharpe": gate["fixed_sharpe"],
            "selection_gap": gate["selection_gap"],
            "verdict_pre_gate": verdict_pre_gate, "verdict": verdict}


def main() -> None:
    t0 = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    grid_sizes = sweeps.r8_hourly_variants_per_family()
    lane_configs = sweeps.r8_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert grid_sizes == {"drawdown_reversion": 12, "high_proximity": 12} \
        and lane_configs == 192, \
        "grid drifted from the declared Round-8 hourly slice (trading_lab.sweeps)"
    for fam in sweeps.R8_HOURLY_FAMILIES:  # grid identity with the daily R7 axes
        assert (sweeps.r8_hourly_variants(fam)
                == sweeps.r7_variants(fam)), \
            f"R8 grid for {fam} drifted from the R7 daily grid (plan identity)"
    print(f"grids: {grid_sizes} × {len(sweeps.R8_HOURLY_INSTRUMENTS)} "
          f"instruments = {lane_configs} registered configs "
          f"(program cumulative {program_cumulative}); cap {CAP_SECONDS} s")

    lanes = [(t, f) for t in sweeps.R8_HOURLY_INSTRUMENTS
             for f in sweeps.R8_HOURLY_FAMILIES]
    results, cap_hit, skipped = [], False, []
    for i, (ticker, family) in enumerate(lanes):
        elapsed = time.monotonic() - t0
        if elapsed >= CAP_SECONDS:
            cap_hit = True
            skipped = [{"instrument": t, "family": f} for t, f in lanes[i:]]
            print(f"CAP-HIT: elapsed {elapsed:.1f} s >= cap {CAP_SECONDS} s "
                  f"before lane {ticker} {family}; STOPPING with "
                  f"{len(skipped)} lanes skipped (no silent truncation — "
                  f"re-registration required to continue)")
            break
        results.append(run_lane(ticker, family, grid_sizes, lane_configs,
                                program_cumulative))

    runtime = time.monotonic() - t0
    counts = {v: sum(1 for r in results if r["verdict"] == v)
              for v in (promotion.SWEEP_KEEP, promotion.SWEEP_KILL,
                        promotion.SWEEP_KILL_SIG, VERDICT_INSUFFICIENT)}
    gate_counts = {g: sum(1 for r in results if r["gate"] == g)
                   for g in (selection_gate.GATE_PASS,
                             selection_gate.GATE_FAIL)}
    demoted = sum(1 for r in results
                  if r["verdict_pre_gate"] == promotion.SWEEP_KEEP
                  and r["verdict"] != promotion.SWEEP_KEEP)
    summary = {
        "schema_version": 1,
        "sweep": SLICE,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": ledger.git_sha(),
        "order": "owner GO 2026-07-18T13:47Z; "
                 "pre-registered docs/research-round-8-plan.md",
        "post_holdout_dev_only": True,
        "registered_configs": lane_configs,
        "program_variants_tried": program_cumulative,
        "lanes_planned": len(lanes),
        "lanes_run": len(results),
        "runtime_seconds": round(runtime, 3),
        "cap_seconds": CAP_SECONDS,
        "cap_hit": cap_hit,
        "lanes_skipped_on_cap": skipped,
        "verdict_counts": counts,
        "gate_counts": gate_counts,
        "keeps_demoted_by_gate": demoted,
        "lanes": results,
    }
    (SWEEP_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts} · gate {gate_counts} · "
          f"{demoted} KEEP demoted by gate · runtime {runtime:.1f} s "
          f"(cap {CAP_SECONDS} s{' — CAP-HIT' if cap_hit else ' — not hit'})")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
