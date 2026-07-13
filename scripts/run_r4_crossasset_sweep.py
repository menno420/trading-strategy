#!/usr/bin/env python3
"""Round 4 slice R4-E — cross-asset lead-lag exposure gate vs its MANDATORY
ungated control arm. The LAST run slice of Round 4.

POST-HOLDOUT, DEV-ONLY (ORDER 012 generative rung, 2026-07-13 night-run
direct order "continue with some new ideas"). Promotion is closed: nothing
this script produces can be an out-of-sample claim; a KEEP is a
dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-4-plan.md`` § "R4-E — Cross-asset
lead-lag filter (with ungated control arm)", merged to main BEFORE this
script existed. Motivating results: the round-3 universe expansion
committed TLT, XOM and GLD caches (PRs #90-#92) but used them only as
standalone lanes — cross-asset information (bond/commodity momentum as an
equity risk gate) is an untested idea class — and the round's two
conditioning nulls (PR #92: vol-gate control beat the gate 6/6; PR #104:
trend-strength control split 3/3, conditioning produced zero candidates)
make the prior informed. Registered hypothesis: **null expected** — a
TLT-momentum exposure gate on SPY/QQQ trend lanes does not beat its
ungated control after costs.

Method (grids committed to ``trading_lab.sweeps`` in the pre-declaration
commit BEFORE this script ran; strategy ``trading_lab.strategies
.crossasset_gate`` — the program's first strategy consuming a SECOND
instrument's series): per equity instrument, TWO walk-forward arms on the
identical rail, costs and windows —

* **GATED arm** (12 registered variants): the frozen equity trend
  component (ema_crossover 20/100 — the committed PR #90 grid point, the
  same freeze PR #104 used) exposed ONLY while the gate asset's trailing
  momentum is positive: gate asset {TLT, XOM, GLD} × momentum lookback
  {21, 63, 126, 252} bars (~1/3/6/12 months). Gate momentum is computed
  on the gate asset's OWN calendar and aligned onto the equity index with
  a strictly-backward ffill join — the gate value applied at equity bar t
  uses gate-asset data <= t ONLY (no lookahead, pinned by tests); the
  engine then fills at bar t+1's open per house convention. Undefined
  gate (warm-up) resolves against the strategy: flat.
* **CONTROL arm** (1 registered variant): the SAME frozen component with
  the gate removed (``gated=False`` — exactly the vol-gate/R4-D control
  structure). The control never loads or computes any gate-asset data
  (invariance pinned by tests); the arms differ ONLY in the gate.

Pre-registered kill criterion (the primary verdict, same control-arm rule
as R4-D): **KILL iff the gated arm's stitched OOS Sharpe <= the ungated
control's**; a KEEP additionally requires beating same-window same-cost
buy-and-hold (and > 0, the Round-2 tie rule — ties/ambiguity KILL). A
machine-readable ``control_arm_delta`` (gated minus control stitched OOS
Sharpe) is recorded per lane. The standard Round-2 verdict legs and the
ORDER 007 informational t are recorded alongside;
``promotion.classify_verdict`` is applied, so KILL-SIG is possible.

Significance K = 13 (``sweeps.R4_CROSSASSET_K``): the honest count of
EVERY registered config this lane tries (12 gated + 1 control). The plan
registers "~12-variant pre-declared grid (K=12)"; counting the control
arm RAISES the bar (min_tstat(13) ~ 2.665 > 2.638) — K is never counted
down, the bar is never lowered (precedent PR #104). Informational only:
promotion is CLOSED.

Instruments: SPY and QQQ (the two plan-named equities). Gate assets: the
three plan-named round-3 caches, committed — NO new data fetching. Data
ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars >=
2025-01-09 excluded; ``data_end <= 2025-01-08`` asserted per ticker,
equities AND gate assets); ``unlock_holdout`` is never passed. Costs:
engine defaults, 5 bps slippage + 1 bp commission per side, both arms.
Walk-forward: train 1008 bars (~4y), test 252 bars (~1y), contiguous test
windows; the two arms' splits are asserted identical, and the benchmark
is buy-and-hold over the exact same stitched OOS window at the same
costs. Execution: signal at bar t fills at bar t+1 open. Program burden
prior to this lane: 4319 (the R4-D rollup's cumulative); program
cumulative after: 4345 (+26 = 13 x 2).

Per instrument this script produces (r3 shape):

1. **Per-variant full-dev-period backtests** for all 13 grid points
   (both arms) — bookkeeping rows, NOT findings (single-split in-sample).
2. **Two walk-forward evaluations** (gated over its 12 variants, control
   over its 1) — the stitched OOS comparison is the only reportable
   number.
3. **One standard ledger run file** for the GATED arm's top full-period
   variant (round-3 convention, PR #104 precedent; the control arm's
   numbers live in the sweep JSON — new runs are ledgered, one row per
   lane).

Output: ``experiments/sweeps/r4-crossasset/`` per-lane JSONs + one rollup
``summary.json``; ``experiments/index.jsonl`` rebuilt. All prior
``experiments/sweeps/**`` files stay byte-untouched — this slice is
additive only.

Usage: python3 scripts/run_r4_crossasset_sweep.py
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

SWEEP_NAME = "r4-crossasset"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME
TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09.
DEV_DATA_END_MAX = "2025-01-08"

# Program burden prior to this lane: 4319 = the R4-D rollup's cumulative
# (docs/research-round-4-results.md § R4-D burden ledger).
PROGRAM_PRIOR_CONFIGS = 4319

VERDICT_KEEP = "KEEP (dev-candidate only)"
VERDICT_KILL = "KILL"

VARIANT_METRIC_KEYS = ("sharpe", "sortino", "cagr", "total_return",
                       "max_drawdown", "win_rate", "turnover_per_year",
                       "n_trades")


def _clean(x):
    """NaN -> None for JSON."""
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


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
    return {k: _clean(v) for k, v in out.items()}


def full_period_rows(ohlcv, strategy_fn, variants, arm) -> list[dict]:
    """Single-split in-sample bookkeeping rows — NOT findings."""
    rows = []
    for params in variants:
        res = run_backtest(ohlcv, strategy_fn(ohlcv, **params),
                           timeframe=TIMEFRAME)
        m = metrics.compute_all(res)
        rows.append({"arm": arm, "params": params,
                     "metrics": {k: _clean(m[k])
                                 for k in VARIANT_METRIC_KEYS}})
    return rows


def wf_summary(wf, oos_slice) -> dict:
    """The JSON-ready walk-forward block for one arm (r3 shape)."""
    return {
        "train_size": TRAIN_SIZE,
        "test_size": TEST_SIZE,
        "n_splits": len(wf["splits"]),
        "variants_tried": wf["variants_tried"],
        "oos_start": str(oos_slice.index[0]),
        "oos_end": str(oos_slice.index[-1]),
        "oos_metrics": series_metrics(wf["oos_returns"], wf["oos_equity"]),
        "per_split": [{
            "train": [s["split"].train_start, s["split"].train_end],
            "test": [s["split"].test_start, s["split"].test_end],
            "params": s["params"],
            "train_score": _clean(s["train_score"]),
            "test_sharpe": _clean(s["test_sharpe"]),
        } for s in wf["splits"]],
    }


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    gated = sweeps.r4_crossasset_gated_variants()
    control = sweeps.r4_crossasset_control_variants()
    per_arm = sweeps.r4_crossasset_variants_per_arm()
    lane_configs = sweeps.r4_crossasset_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert per_arm == {"gated": 12, "control": 1} \
        and lane_configs == 26 \
        and sweeps.R4_CROSSASSET_K == 13, \
        "grid drifted from the declared R4-E lane (trading_lab.sweeps)"
    strategy_fn = STRATEGIES[sweeps.R4_CROSSASSET_STRATEGY_NAME]

    # Dev-rail assertion for the GATE assets too (the strategy loads them
    # internally via load_ohlcv's default holdout-excluding rail).
    gate_data_ends = {}
    for gate_ticker in sweeps.R4_CROSSASSET_GATE_ASSETS:
        g = load_ohlcv(gate_ticker, TIMEFRAME)
        gate_data_ends[gate_ticker] = str(g.index[-1])
        assert gate_data_ends[gate_ticker][:10] <= DEV_DATA_END_MAX, \
            (f"{gate_ticker}: gate dev rail breached "
             f"(data_end {gate_data_ends[gate_ticker]})")

    print(f"grids: {per_arm} x {len(sweeps.R4_CROSSASSET_INSTRUMENTS)} "
          f"instruments = {lane_configs} registered configs "
          f"(program cumulative {program_cumulative}); K = "
          f"{sweeps.R4_CROSSASSET_K}, bar "
          f"{promotion.min_tstat(sweeps.R4_CROSSASSET_K):.3f}; gate assets "
          f"{sweeps.R4_CROSSASSET_GATE_ASSETS} (dev rail asserted)")
    rollup_rows, ledger_files = [], []

    for ticker in sweeps.R4_CROSSASSET_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        data_end = str(ohlcv.index[-1])
        assert data_end[:10] <= DEV_DATA_END_MAX, \
            f"{ticker}: dev rail breached (data_end {data_end})"

        # 1) full-dev-period backtests, both arms (bookkeeping rows)
        rows = (full_period_rows(ohlcv, strategy_fn, gated, "gated")
                + full_period_rows(ohlcv, strategy_fn, control, "control"))

        # 2) walk-forward BOTH arms on the identical rail and windows
        wf_gated = walk_forward(ohlcv, strategy_fn, gated,
                                train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                                timeframe=TIMEFRAME)
        wf_ctrl = walk_forward(ohlcv, strategy_fn, control,
                               train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                               timeframe=TIMEFRAME)
        assert ([s["split"] for s in wf_gated["splits"]]
                == [s["split"] for s in wf_ctrl["splits"]]), \
            f"{ticker}: arms diverged on walk-forward windows"
        first = wf_gated["splits"][0]["split"]
        last = wf_gated["splits"][-1]["split"]
        oos_slice = ohlcv.iloc[first.test_start:last.test_end]
        bench_oos = buy_and_hold_result(oos_slice, timeframe=TIMEFRAME)

        gated_block = wf_summary(wf_gated, oos_slice)
        ctrl_block = wf_summary(wf_ctrl, oos_slice)
        gated_m = gated_block["oos_metrics"]
        ctrl_m = ctrl_block["oos_metrics"]
        bench_m = {k: _clean(v)
                   for k, v in metrics.compute_all(bench_oos).items()}
        gated_sharpe = gated_m["sharpe"]
        ctrl_sharpe = ctrl_m["sharpe"]
        bench_sharpe = bench_m["sharpe"]

        # The machine-readable headline number of this slice.
        control_arm_delta = (None if gated_sharpe is None
                             or ctrl_sharpe is None
                             else gated_sharpe - ctrl_sharpe)
        beats_control = (control_arm_delta is not None
                         and control_arm_delta > 0)
        beats_benchmark = (gated_sharpe is not None
                           and bench_sharpe is not None
                           and gated_sharpe > bench_sharpe)
        # Pre-registered rule: KILL iff gated <= ungated control; KEEP
        # additionally requires beating B&H (and > 0 — ties/ambiguity KILL).
        keep = bool(beats_control and beats_benchmark
                    and gated_sharpe is not None and gated_sharpe > 0)
        verdict = VERDICT_KEEP if keep else VERDICT_KILL
        # ORDER 007 arithmetic — informational only, promotion CLOSED.
        grade = promotion.grade_promotion(
            strategy_sharpe=gated_sharpe, benchmark_sharpe=bench_sharpe,
            n_periods=gated_m["n_bars"], timeframe=TIMEFRAME,
            variants_tried=sweeps.R4_CROSSASSET_K)
        sweep_verdict = promotion.classify_verdict(keep, grade["tstat"],
                                                   grade["min_tstat"])

        # 3) ledger row: the GATED arm's top full-period variant
        # (round-3 convention, PR #104 precedent; the control arm lives in
        # the sweep JSON).
        gated_rows = [r for r in rows if r["arm"] == "gated"]
        top = max(gated_rows,
                  key=lambda r: (r["metrics"]["sharpe"]
                                 if r["metrics"]["sharpe"] is not None
                                 else float("-inf")))
        run_path = ledger.run_and_record(
            strategy=sweeps.R4_CROSSASSET_STRATEGY_NAME, instrument=ticker,
            timeframe=TIMEFRAME, ohlcv=ohlcv, params=top["params"],
            variants_tried=sweeps.R4_CROSSASSET_K,
            notes=(f"Round 4 slice R4-E cross-asset gate sweep "
                   f"(docs/research-round-4-plan.md § R4-E; post-holdout "
                   f"DEV-ONLY, promotion closed — ORDER 012): top "
                   f"full-dev-period GATED variant of "
                   f"{sweeps.R4_CROSSASSET_K} lane configs (post-hoc "
                   f"selection — in-sample; the walk-forward OOS numbers "
                   f"for BOTH arms and the control_arm_delta live in "
                   f"experiments/sweeps/{SWEEP_NAME}/"
                   f"crossasset_gate__{ticker}.json)"))
        ledger_files.append(str(run_path.relative_to(config.REPO_ROOT)))

        record = {
            "schema_version": 1,
            "sweep": SWEEP_NAME,
            "created_utc": datetime.now(timezone.utc)
                                   .isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": sweeps.R4_CROSSASSET_STRATEGY_NAME,
            "instrument": ticker,
            "instrument_status": ("slice-3 lane-local instrument (not in "
                                  "the frozen config.UNIVERSE); committed "
                                  "PR #83 cache reused"),
            "family_status": ("NEW strategy (crossasset_gate — the "
                              "program's first cross-asset strategy), "
                              "committed in the pre-declaration commit; "
                              "equity component FROZEN at the committed "
                              "r3 grid point (ema_crossover 20/100, "
                              "PR #90 — the PR #104 freeze) — no new "
                              "parameter territory beyond the registered "
                              "gate axes"),
            "gate_assets": list(sweeps.R4_CROSSASSET_GATE_ASSETS),
            "gate_data_ends": gate_data_ends,
            "gate_alignment": ("gate momentum computed on the gate "
                               "asset's own calendar, aligned onto the "
                               "equity index by strictly-backward ffill "
                               "reindex — gate value at equity bar t uses "
                               "gate data <= t only (no lookahead, pinned "
                               "by tests); fill at t+1 open per house "
                               "convention"),
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": "ORDER 012 night-run (control/inbox.md)",
            "preregistered_in": ("docs/research-round-4-plan.md § R4-E — "
                                 "Cross-asset lead-lag filter (with "
                                 "ungated control arm)"),
            "data_start": str(ohlcv.index[0]),
            "data_end": data_end,
            "n_bars": int(len(ohlcv)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "variants_tried": sweeps.R4_CROSSASSET_K,
            "variants_per_arm": per_arm,
            "lane_variants_tried": lane_configs,
            "program_variants_tried": program_cumulative,
            "full_period_variants": {
                "note": ("single-split in-sample rows for deflated-Sharpe "
                         "bookkeeping, BOTH arms — NOT findings"),
                "rows": rows,
            },
            "walk_forward_gated": gated_block,
            "walk_forward_control": ctrl_block,
            "benchmark_oos_metrics": bench_m,
            "gated_oos_sharpe": gated_sharpe,
            "control_oos_sharpe": ctrl_sharpe,
            "benchmark_oos_sharpe": bench_sharpe,
            "control_arm_delta": control_arm_delta,
            "beats_control": beats_control,
            "beats_benchmark": beats_benchmark,
            "kill_criterion": ("pre-registered R4-E rule (same control-arm "
                               "rule as R4-D): KILL iff gated stitched OOS "
                               "Sharpe <= the ungated control's; KEEP "
                               "additionally requires beating same-window "
                               "same-cost B&H and > 0; ties/ambiguity "
                               "KILL"),
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "top_full_period_variant": {"arm": "gated",
                                        "params": top["params"],
                                        "metrics": top["metrics"],
                                        "ledger_run": run_path.name},
            "promotion_grade": {
                "note": ("ORDER 007 bar on the gated arm's stitched OOS "
                         "Sharpe delta vs B&H, Bonferroni K = 13 (every "
                         "registered config this lane, bar ~2.665 — RAISED "
                         "above the round-standard 2.638, never lowered; "
                         "precedent PR #104) — INFORMATIONAL ONLY, "
                         "promotion is CLOSED post-holdout (nothing here "
                         "is a finding)"),
                **grade,
            },
            "ledger": ("ledgered: one row per lane — the GATED arm's top "
                       "full-period variant (round-3 convention, PR #104 "
                       "precedent); the control arm's numbers live in this "
                       "sweep JSON"),
            "ledger_file": ledger_files[-1],
        }
        out = SWEEP_DIR / f"crossasset_gate__{ticker}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        rollup_rows.append({
            "instrument": ticker,
            "gated_oos_sharpe": gated_sharpe,
            "control_oos_sharpe": ctrl_sharpe,
            "benchmark_oos_sharpe": bench_sharpe,
            "control_arm_delta": control_arm_delta,
            "beats_control": beats_control,
            "beats_benchmark": beats_benchmark,
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "tstat": _clean(grade["tstat"]),
            "min_tstat": grade["min_tstat"],
            "detail_file": str(out.relative_to(config.REPO_ROOT)),
        })
        print(f"{ticker}: gated={gated_sharpe:.3f} "
              f"control={ctrl_sharpe:.3f} delta={control_arm_delta:+.3f} "
              f"bench={bench_sharpe:.3f} t={grade['tstat']:.2f} "
              f"(min {grade['min_tstat']:.2f}) {verdict} [{sweep_verdict}]")

    counts = {
        "lanes": len(rollup_rows),
        "keep": sum(1 for r in rollup_rows if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in rollup_rows if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in rollup_rows
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
        "gated_beats_control": sum(1 for r in rollup_rows
                                   if r["beats_control"]),
        "gated_beats_benchmark": sum(1 for r in rollup_rows
                                     if r["beats_benchmark"]),
    }
    ledger.rebuild_index()
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "order": "ORDER 012 (generative rung)",
        "preregistered_in": ("docs/research-round-4-plan.md § R4-E — "
                             "Cross-asset lead-lag filter (with ungated "
                             "control arm)"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "motivation": ("round 3 committed TLT/XOM/GLD but only as "
                       "standalone lanes; cross-asset momentum as an "
                       "equity exposure gate is the one untested idea "
                       "class, tested against the round's informed prior "
                       "(PR #92 control beat gate 6/6; PR #104 split 3/3, "
                       "zero candidates)"),
        "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                  "commission_bps": config.DEFAULT_COMMISSION_BPS},
        "rule": ("per lane: KILL iff gated stitched OOS Sharpe <= the "
                 "ungated control's (pre-registered primary criterion, "
                 "control_arm_delta recorded machine-readably); KEEP "
                 "additionally requires beating same-window same-cost B&H "
                 "and > 0; KILL-SIG at t <= -min_tstat(13) via "
                 "classify_verdict; t informational only at K=13 (bar "
                 "~2.665, raised above the round-standard 2.638 — never "
                 "lowered)"),
        "arms": ("gated: 12 variants (gate_asset {TLT, XOM, GLD} x "
                 "gate_lookback {21, 63, 126, 252}, long only while the "
                 "gate asset's trailing momentum > 0, gate rule and "
                 "warm-up convention fixed in the grid commit, equity "
                 "component frozen at the committed r3 point ema_crossover "
                 "20/100); control: the 1-variant gateless collapse (the "
                 "same component ungated), identical costs and windows; "
                 "gate alignment strictly backward (gate data <= t only)"),
        "ledger_decision": ("ledgered: one row per lane — the GATED arm's "
                            "top full-dev-period variant, round-3 "
                            "convention (new strategy = new runs; PR #104 "
                            "precedent); variants_tried = K = 13; the "
                            "control arm's numbers live in the per-lane "
                            "sweep JSONs; experiments/index.jsonl rebuilt"),
        "ledger_files": ledger_files,
        "program_variants_tried": PROGRAM_PRIOR_CONFIGS
        + sweeps.r4_crossasset_total_configs(),
        "runtime_seconds": round(elapsed, 1),
        "counts": counts,
        "lanes": rollup_rows,
    }
    out = SWEEP_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    deltas = ", ".join(f"{r['instrument']} {r['control_arm_delta']:+.3f}"
                       for r in rollup_rows)
    print(f"\nsummary: {counts['lanes']} lanes — {counts['keep']} KEEP / "
          f"{counts['kill']} KILL ({counts['kill_sig']} KILL-SIG); "
          f"gated beat control on "
          f"{counts['gated_beats_control']}/{counts['lanes']} "
          f"(deltas: {deltas}); beat B&H on "
          f"{counts['gated_beats_benchmark']}/{counts['lanes']} "
          f"({elapsed:.1f}s) -> {out}")


if __name__ == "__main__":
    main()
