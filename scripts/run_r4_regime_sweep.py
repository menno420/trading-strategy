#!/usr/bin/env python3
"""Round 4 slice R4-D — regime-conditional allocation vs its MANDATORY
unconditional control arm.

POST-HOLDOUT, DEV-ONLY (ORDER 012 generative rung, 2026-07-13 night-run
direct order "continue with some new ideas"). Promotion is closed: nothing
this script produces can be an out-of-sample claim; a KEEP is a
dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-4-plan.md`` § "R4-D —
Regime-conditional allocation (with mandatory control arm)", merged to
main BEFORE this script existed. Motivating round-3 result: PR #92
(r3-gated-new-tickers) — the vol gate's ``vol_filter=False`` control arm
beat the gated arm on ALL SIX instruments; conditioning subtracted value
everywhere it was tried. R4-D tests a different conditioning axis (TREND
STRENGTH, not volatility) with the control-arm discipline now mandatory.
Registered hypothesis: **null expected** — regime-conditional family
switching does not beat its unconditional control after costs.

Method (grids committed to ``trading_lab.sweeps`` in the pre-declaration
commit BEFORE this script ran; strategy ``trading_lab.strategies
.regime_switch``): per instrument, TWO walk-forward arms on the identical
rail, costs and windows —

* **CONDITIONAL arm** (12 registered variants): family choice conditioned
  on trend-strength tercile buckets of a trailing percentile rank
  (boundaries 1/3 and 2/3 FIXED in the grid commit) of either Wilder
  ``ADX(14)`` or the |200d SMA slope| (both plan-named metrics swept as
  declared variants, rank windows {126, 252, 504}): trend component
  (ema_crossover 20/100, the committed PR #90 grid point) in the
  strong-trend bucket; flat OR reversion component (rsi_mean_reversion
  2/20/60, the committed PR #91 grid point) in the weak bucket; middle
  tercile holds the previous bucket; undefined regime is flat.
* **CONTROL arm** (2 registered variants): the SAME components with the
  regime condition removed — ``weak_family="flat"`` collapses to the
  ungated trend component (exactly the vol-gate control structure);
  ``weak_family="reversion"`` to the equal-weight mean of both components
  (the R4-C committee convention). The control never computes the metric
  (invariance pinned by tests); the arms differ ONLY in the condition.

Pre-registered kill criterion (the primary verdict): **KILL iff the
conditional arm's stitched OOS Sharpe <= the unconditional control's**; a
KEEP additionally requires beating same-window same-cost buy-and-hold
(and > 0, the Round-2 tie rule — ties/ambiguity KILL). A machine-readable
``control_arm_delta`` (conditional minus control stitched OOS Sharpe) is
recorded per lane. The standard Round-2 verdict legs and the ORDER 007
informational t are recorded alongside; ``promotion.classify_verdict``
is applied, so KILL-SIG is possible.

Significance K = 14 (``sweeps.R4_REGIME_K``): the honest count of EVERY
registered config this lane tries (12 conditional + 2 control). The plan
registers "~12 variants per lane, standard K=12"; counting the control
arm RAISES the bar (min_tstat(14) ~ 2.690 > 2.638) — K is never counted
down, the bar is never lowered. Informational only: promotion is CLOSED.

Instruments: the six slice-3 tickers (SPY, QQQ, TSLA, JPM, XOM, TLT),
verbatim — the same surface the PR #92 result was measured on, where both
component families exist as committed variants (PR #90 trend, PR #91
mean-reversion). Committed caches only; NO new data fetching. Program
burden prior to this lane: 4235 (the R4-C rollup's cumulative); program
cumulative after: 4319 (+84 = 14 x 6).

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; ``data_end <= 2025-01-08`` asserted per ticker);
``unlock_holdout`` is never passed. Costs: engine defaults, 5 bps
slippage + 1 bp commission per side, both arms. Walk-forward: train 1008
bars (~4y), test 252 bars (~1y), contiguous test windows; the two arms'
splits are asserted identical, and the benchmark is buy-and-hold over the
exact same stitched OOS window at the same costs. Execution: signal at
bar t fills at bar t+1 open.

Per instrument this script produces (r3 shape):

1. **Per-variant full-dev-period backtests** for all 14 grid points
   (both arms) — bookkeeping rows, NOT findings (single-split in-sample).
2. **Two walk-forward evaluations** (conditional over its 12 variants,
   control over its 2) — the stitched OOS comparison is the only
   reportable number.
3. **One standard ledger run file** for the CONDITIONAL arm's top
   full-period variant (round-3 convention; the control arm's numbers
   live in the sweep JSON — new runs are ledgered, one row per lane).

Output: ``experiments/sweeps/r4-regime/`` per-lane JSONs + one rollup
``summary.json``; ``experiments/index.jsonl`` rebuilt. All prior
``experiments/sweeps/**`` files stay byte-untouched — this slice is
additive only.

Usage: python3 scripts/run_r4_regime_sweep.py
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

SWEEP_NAME = "r4-regime"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME
TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09.
DEV_DATA_END_MAX = "2025-01-08"

# Program burden prior to this lane: 4235 = the R4-C rollup's cumulative
# (docs/research-round-4-results.md § R4-C burden ledger).
PROGRAM_PRIOR_CONFIGS = 4235

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
    conditional = sweeps.r4_regime_conditional_variants()
    control = sweeps.r4_regime_control_variants()
    per_arm = sweeps.r4_regime_variants_per_arm()
    lane_configs = sweeps.r4_regime_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert per_arm == {"conditional": 12, "control": 2} \
        and lane_configs == 84 \
        and sweeps.R4_REGIME_K == 14, \
        "grid drifted from the declared R4-D lane (trading_lab.sweeps)"
    strategy_fn = STRATEGIES[sweeps.R4_REGIME_STRATEGY_NAME]
    print(f"grids: {per_arm} x {len(sweeps.R4_REGIME_INSTRUMENTS)} "
          f"instruments = {lane_configs} registered configs "
          f"(program cumulative {program_cumulative}); K = "
          f"{sweeps.R4_REGIME_K}, bar "
          f"{promotion.min_tstat(sweeps.R4_REGIME_K):.3f}")
    rollup_rows, ledger_files = [], []

    for ticker in sweeps.R4_REGIME_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        data_end = str(ohlcv.index[-1])
        assert data_end[:10] <= DEV_DATA_END_MAX, \
            f"{ticker}: dev rail breached (data_end {data_end})"

        # 1) full-dev-period backtests, both arms (bookkeeping rows)
        rows = (full_period_rows(ohlcv, strategy_fn, conditional,
                                 "conditional")
                + full_period_rows(ohlcv, strategy_fn, control, "control"))

        # 2) walk-forward BOTH arms on the identical rail and windows
        wf_cond = walk_forward(ohlcv, strategy_fn, conditional,
                               train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                               timeframe=TIMEFRAME)
        wf_ctrl = walk_forward(ohlcv, strategy_fn, control,
                               train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                               timeframe=TIMEFRAME)
        assert ([s["split"] for s in wf_cond["splits"]]
                == [s["split"] for s in wf_ctrl["splits"]]), \
            f"{ticker}: arms diverged on walk-forward windows"
        first = wf_cond["splits"][0]["split"]
        last = wf_cond["splits"][-1]["split"]
        oos_slice = ohlcv.iloc[first.test_start:last.test_end]
        bench_oos = buy_and_hold_result(oos_slice, timeframe=TIMEFRAME)

        cond_block = wf_summary(wf_cond, oos_slice)
        ctrl_block = wf_summary(wf_ctrl, oos_slice)
        cond_m = cond_block["oos_metrics"]
        ctrl_m = ctrl_block["oos_metrics"]
        bench_m = {k: _clean(v)
                   for k, v in metrics.compute_all(bench_oos).items()}
        cond_sharpe = cond_m["sharpe"]
        ctrl_sharpe = ctrl_m["sharpe"]
        bench_sharpe = bench_m["sharpe"]

        # The machine-readable headline number of this slice.
        control_arm_delta = (None if cond_sharpe is None
                             or ctrl_sharpe is None
                             else cond_sharpe - ctrl_sharpe)
        beats_control = (control_arm_delta is not None
                         and control_arm_delta > 0)
        beats_benchmark = (cond_sharpe is not None
                           and bench_sharpe is not None
                           and cond_sharpe > bench_sharpe)
        # Pre-registered rule: KILL iff conditional <= control; KEEP
        # additionally requires beating B&H (and > 0 — ties/ambiguity KILL).
        keep = bool(beats_control and beats_benchmark
                    and cond_sharpe is not None and cond_sharpe > 0)
        verdict = VERDICT_KEEP if keep else VERDICT_KILL
        # ORDER 007 arithmetic — informational only, promotion CLOSED.
        grade = promotion.grade_promotion(
            strategy_sharpe=cond_sharpe, benchmark_sharpe=bench_sharpe,
            n_periods=cond_m["n_bars"], timeframe=TIMEFRAME,
            variants_tried=sweeps.R4_REGIME_K)
        sweep_verdict = promotion.classify_verdict(keep, grade["tstat"],
                                                   grade["min_tstat"])

        # 3) ledger row: the CONDITIONAL arm's top full-period variant
        # (round-3 convention; the control arm lives in the sweep JSON).
        cond_rows = [r for r in rows if r["arm"] == "conditional"]
        top = max(cond_rows,
                  key=lambda r: (r["metrics"]["sharpe"]
                                 if r["metrics"]["sharpe"] is not None
                                 else float("-inf")))
        run_path = ledger.run_and_record(
            strategy=sweeps.R4_REGIME_STRATEGY_NAME, instrument=ticker,
            timeframe=TIMEFRAME, ohlcv=ohlcv, params=top["params"],
            variants_tried=sweeps.R4_REGIME_K,
            notes=(f"Round 4 slice R4-D regime-conditional sweep "
                   f"(docs/research-round-4-plan.md § R4-D; post-holdout "
                   f"DEV-ONLY, promotion closed — ORDER 012): top "
                   f"full-dev-period CONDITIONAL variant of "
                   f"{sweeps.R4_REGIME_K} lane configs (post-hoc selection "
                   f"— in-sample; the walk-forward OOS numbers for BOTH "
                   f"arms and the control_arm_delta live in "
                   f"experiments/sweeps/{SWEEP_NAME}/"
                   f"regime_switch__{ticker}.json)"))
        ledger_files.append(str(run_path.relative_to(config.REPO_ROOT)))

        record = {
            "schema_version": 1,
            "sweep": SWEEP_NAME,
            "created_utc": datetime.now(timezone.utc)
                                   .isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": sweeps.R4_REGIME_STRATEGY_NAME,
            "instrument": ticker,
            "instrument_status": ("slice-3 lane-local instrument (not in "
                                  "the frozen config.UNIVERSE); committed "
                                  "PR #83 cache reused — the PR #92 "
                                  "vol-gate surface, verbatim"),
            "family_status": ("NEW strategy (regime_switch), committed in "
                              "the pre-declaration commit; components "
                              "FROZEN at committed r3 grid points "
                              "(ema_crossover 20/100 PR #90; "
                              "rsi_mean_reversion 2/20/60 PR #91) — no "
                              "new parameter territory beyond the "
                              "registered regime axes"),
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": "ORDER 012 night-run (control/inbox.md)",
            "preregistered_in": ("docs/research-round-4-plan.md § R4-D — "
                                 "Regime-conditional allocation (with "
                                 "mandatory control arm)"),
            "data_start": str(ohlcv.index[0]),
            "data_end": data_end,
            "n_bars": int(len(ohlcv)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "variants_tried": sweeps.R4_REGIME_K,
            "variants_per_arm": per_arm,
            "lane_variants_tried": lane_configs,
            "program_variants_tried": program_cumulative,
            "full_period_variants": {
                "note": ("single-split in-sample rows for deflated-Sharpe "
                         "bookkeeping, BOTH arms — NOT findings"),
                "rows": rows,
            },
            "walk_forward_conditional": cond_block,
            "walk_forward_control": ctrl_block,
            "benchmark_oos_metrics": bench_m,
            "conditional_oos_sharpe": cond_sharpe,
            "control_oos_sharpe": ctrl_sharpe,
            "benchmark_oos_sharpe": bench_sharpe,
            "control_arm_delta": control_arm_delta,
            "beats_control": beats_control,
            "beats_benchmark": beats_benchmark,
            "kill_criterion": ("pre-registered R4-D rule: KILL iff "
                               "conditional stitched OOS Sharpe <= the "
                               "unconditional control's; KEEP additionally "
                               "requires beating same-window same-cost B&H "
                               "and > 0; ties/ambiguity KILL"),
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "top_full_period_variant": {"arm": "conditional",
                                        "params": top["params"],
                                        "metrics": top["metrics"],
                                        "ledger_run": run_path.name},
            "promotion_grade": {
                "note": ("ORDER 007 bar on the conditional arm's stitched "
                         "OOS Sharpe delta vs B&H, Bonferroni K = 14 (every "
                         "registered config this lane, bar ~2.690 — RAISED "
                         "above the round-standard 2.638, never lowered) — "
                         "INFORMATIONAL ONLY, promotion is CLOSED "
                         "post-holdout (nothing here is a finding)"),
                **grade,
            },
            "ledger": ("ledgered: one row per lane — the CONDITIONAL arm's "
                       "top full-period variant (round-3 convention); the "
                       "control arm's numbers live in this sweep JSON"),
            "ledger_file": ledger_files[-1],
        }
        out = SWEEP_DIR / f"regime_switch__{ticker}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        rollup_rows.append({
            "instrument": ticker,
            "conditional_oos_sharpe": cond_sharpe,
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
        print(f"{ticker}: conditional={cond_sharpe:.3f} "
              f"control={ctrl_sharpe:.3f} delta={control_arm_delta:+.3f} "
              f"bench={bench_sharpe:.3f} t={grade['tstat']:.2f} "
              f"(min {grade['min_tstat']:.2f}) {verdict} [{sweep_verdict}]")

    counts = {
        "lanes": len(rollup_rows),
        "keep": sum(1 for r in rollup_rows if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in rollup_rows if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in rollup_rows
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
        "conditional_beats_control": sum(1 for r in rollup_rows
                                         if r["beats_control"]),
        "conditional_beats_benchmark": sum(1 for r in rollup_rows
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
        "preregistered_in": ("docs/research-round-4-plan.md § R4-D — "
                             "Regime-conditional allocation (with "
                             "mandatory control arm)"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "motivation": ("PR #92: the vol gate's control arm beat the gated "
                       "arm 6/6 — this slice asks the same question on the "
                       "trend-strength axis, control arm now mandatory"),
        "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                  "commission_bps": config.DEFAULT_COMMISSION_BPS},
        "rule": ("per lane: KILL iff conditional stitched OOS Sharpe <= "
                 "the unconditional control's (pre-registered primary "
                 "criterion, control_arm_delta recorded machine-readably); "
                 "KEEP additionally requires beating same-window same-cost "
                 "B&H and > 0; KILL-SIG at t <= -min_tstat(14) via "
                 "classify_verdict; t informational only at K=14 (bar "
                 "~2.690, raised above the round-standard 2.638 — never "
                 "lowered)"),
        "arms": ("conditional: 12 variants (metric {adx, sma_slope} x "
                 "rank_window {126, 252, 504} x weak_family {flat, "
                 "reversion}, tercile boundaries 1/3 and 2/3 fixed in the "
                 "grid commit, components frozen at committed r3 points); "
                 "control: the 2-variant conditionless collapse (trend "
                 "only / equal-weight mean), identical costs and windows"),
        "ledger_decision": ("ledgered: one row per lane — the CONDITIONAL "
                            "arm's top full-dev-period variant, round-3 "
                            "convention (new strategy = new runs); "
                            "variants_tried = K = 14; the control arm's "
                            "numbers live in the per-lane sweep JSONs; "
                            "experiments/index.jsonl rebuilt"),
        "ledger_files": ledger_files,
        "program_variants_tried": PROGRAM_PRIOR_CONFIGS
        + sweeps.r4_regime_total_configs(),
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
          f"conditional beat control on "
          f"{counts['conditional_beats_control']}/{counts['lanes']} "
          f"(deltas: {deltas}); beat B&H on "
          f"{counts['conditional_beats_benchmark']}/{counts['lanes']} "
          f"({elapsed:.1f}s) -> {out}")


if __name__ == "__main__":
    main()
