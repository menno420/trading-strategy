#!/usr/bin/env python3
"""Round 11 — cross-asset regime conditioning (continuous, causal) × 3 targets.

POST-HOLDOUT, DEV-ONLY (live owner turn 2026-07-19 / ORDER 021; pre-registered
protocol ``docs/research-round-11-plan.md``, merged as PR #158 BEFORE any
Round-11 outcome existed). Promotion is CLOSED: nothing this script produces can
be an out-of-sample claim; KEEPs are dev-candidates only.

The direction (scoping memo §2.1, PR #157): cross-asset / macro-regime is the
LOWEST-cost, SELF-SERVE first step from the new-data-source frontier — the only
candidate testable with data the lab ALREADY holds (the committed daily cache's
SPY / QQQ / GLD / TLT legs). Round 11 tests whether conditioning a RISK-LEG
target's exposure CONTINUOUSLY on a CAUSAL cross-asset regime score beats plain
buy-and-hold of that same leg — the CONTINUOUS form the burned binary R4
``crossasset_gate`` (0/2) / ``regime_switch`` (0/6) never tried.

The target's position at bar t is the CAUSAL rolling-percentile-rank (trailing
``_R11_PERCENTILE_WINDOW`` = 252) of the chosen regime score, clipped to [0, 1]
(``trading_lab.xasset_regime.regime_conditioned_positions``) — exposure scales
smoothly with how risk-on the regime is relative to its own recent history. This
is CONTINUOUS conditioning, NOT a binary gate; the normalization is ROLLING,
never full-sample (the classic regime-lookahead leak this round forecloses).

Grid: 3 regime signals (``xasset_eq_bond_mom``, ``xasset_metals_riskoff``,
``xasset_breadth``) × 3 windows (63, 126, 252) × 3 targets (SPY, QQQ, NVDA) =
**27** registered configs (``sweeps.r11_total_configs()`` = 27); program
cumulative **5,913 → 5,940**. The search dimension for the selection-fair gate is
(signal, window) PER TARGET — the 9 configs searched for a single target
(per-lane K = 9); the program-wide bar is K = 27.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; holdout SPENT, never read). All 5 tickers (3 targets +
4 regime legs, SPY/QQQ shared) are on the NYSE calendar — one shared index, so
alignment is an intersection, no cross-calendar as-of reindex. Costs: 5 bps
slippage + 1 bp commission per side. Execution: signal at bar t fills at bar
t+1 open. The benchmark is **buy-and-hold** of the target (position ≡ 1.0, the
mandatory unconditioned CONTROL ARM), so each lane's edge is its deviation from
the hold, and the base buy-and-hold Sharpe is reported next to every lane.

For every (signal × window × target) lane this script produces:

1. **A full-dev-period backtest** of the conditioned positions (regime score +
   causal rolling-percentile conditioning, so the full-period run IS a
   fixed-config evaluation — no in-sample parameter selection lives inside a
   lane). Sharpe-delta t vs full-period buy-and-hold via
   ``promotion.grade_promotion`` (the SAME machinery every prior round uses),
   Bonferroni K = 9 (the (signal, window) configs searched on the target);
   ``classify_verdict`` for KILL-SIG. The informational t is ALSO reported
   against the program-wide K = 27 bar.
2. **The mandatory unconditioned CONTROL ARM** (plan §5, headline): the base
   buy-and-hold Sharpe of each target (position ≡ 1.0) is recorded and reported
   RIGHT NEXT TO its conditioned lane's Sharpe/t. The round rolls up how many of
   the 27 lanes even EXCEED their own base hold (before significance), and by how
   much.
3. **The selection-fair standing gate** ([D-0002], round-6+) on EVERY lane —
   ``run_selection_gate`` over contiguous 1008/252 walk-forward test windows, the
   searched arm armed with the target's BEST-of-9 (signal, window) stitched OOS
   Sharpe (plan §7 search dimension), folded through ``apply_gate`` BEFORE the
   verdict is written. The gate block doubles as the R5-D fixed-config row:
   ``fixed_sharpe`` (this config, selection-free over the windows),
   ``searched_sharpe`` (best-of-9), ``selection_gap = searched − fixed``
   (informational, no registered threshold); ``bench_sharpe`` is the same-window
   buy-and-hold control.
4. **The exposure / degeneracy diagnostics** (plan §5): each lane's conditioned
   position mean / std / nunique and fully-invested fraction. A lane whose
   conditioned position is ~constant (regime rarely varies) is flagged
   degenerate / ≈ buy-and-hold and NEVER hidden. (A percentile-rank position is
   ~uniform in [0, 1] by construction, so its mean exposure is ~0.5 — a
   structural half-invested drag vs a hold, reported honestly.)
5. **A RUN-side re-assertion of the no-lookahead / prefix-invariance property**
   (plan §4, THE headline control) on the REAL cached panels: for a spread of
   bars t across all 3 signals × 3 windows, the regime score AND the conditioned
   position at bar t are IDENTICAL whether computed on the full panel or on the
   panel TRUNCATED at bar t. If this ever fails on the real data the design leaks
   and the round STOPS — the reported edge (if any) would be a hindsight
   artifact.

The round's top config per target is LEDGERED with ``variants_tried=9`` (gate
replays are report-only rows in the lane JSON — R4-B precedent).

Runtime cap (self-enforced): <= 900 s wall-clock. The grid is tiny (27 configs,
seconds); the cap is checked before each target with no silent truncation.

Usage: python3 scripts/run_r11_xasset_regime_sweep.py
"""

import csv
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from trading_lab import (config, ledger, metrics, promotion,  # noqa: E402
                         selection_gate, sweeps)
from trading_lab import xasset_regime as xr  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import (buy_and_hold_result,  # noqa: E402
                                run_backtest)
from trading_lab.walkforward import generate_splits  # noqa: E402

SLICE = "r11-xasset-regime"
TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; contiguous non-overlapping test windows
CAP_SECONDS = 900  # self-enforced: <= 15 min wall-clock for the slice

# Program burden prior to this slice: 5,913 registered configs
# (docs/research-round-10-results.md closing tally, Round 10). Round 11 lands
# its 27 on top: 5,913 -> 5,940.
PROGRAM_PRIOR_CONFIGS = 5913

# Every ticker R11 reads: the 4 regime legs + the 3 targets (SPY/QQQ shared).
ALL_TICKERS = ("SPY", "QQQ", "GLD", "TLT", "NVDA")

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SLICE

COSTS = {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
         "commission_bps": config.DEFAULT_COMMISSION_BPS}

PWIN = sweeps._R11_PERCENTILE_WINDOW  # 252, FIXED (not swept)

# A lane whose conditioned position barely varies (std below this) is flagged
# degenerate / ≈ buy-and-hold (plan §5) — the regime rarely moves the exposure.
DEGENERATE_POS_STD = 0.02

# Bars probed for the RUN-side truncation / prefix-invariance re-assertion.
TRUNCATION_PROBE_BARS_FROM_END = (1, 30, 120)

VARIANT_METRIC_KEYS = ("sharpe", "sortino", "cagr", "total_return",
                       "max_drawdown", "win_rate", "turnover_per_year",
                       "n_trades")


def _clean(x):
    """NaN → None for JSON."""
    if x is None:
        return None
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def load_aligned_panel() -> dict:
    """Load every R11 ticker on the dev rail and align on the common NYSE index.

    Returns a dict of aligned close Series (one per ticker) sharing one index.
    All tickers are on the NYSE calendar; the intersection is defensive — in the
    committed cache the five daily frames already share an identical index.
    """
    frames = {t: load_ohlcv(t, TIMEFRAME) for t in ALL_TICKERS}
    common = None
    for t in ALL_TICKERS:
        common = frames[t].index if common is None else common.intersection(
            frames[t].index)
    closes = {t: frames[t]["close"].reindex(common) for t in ALL_TICKERS}
    return {"frames": frames, "closes": closes, "index": common}


def make_regime_strategy(panel_closes: dict):
    """A ``strategy(ohlcv, **params)`` closure so the selection-fair gate can
    replay the multi-ticker conditioned lane exactly like any single-instrument
    family. The gate's ``stitched_replay`` calls this on the TARGET frame
    (possibly truncated to ``ohlcv.iloc[:test_end]``); the closure reindexes the
    aligned regime legs to that (prefix) index — because the panel and the target
    share one calendar, reindexing to a prefix returns the prefix closes, and the
    module's prefix-invariance guarantee makes the causal positions identical to
    the full-panel computation on those bars."""
    def regime_strategy(ohlcv: pd.DataFrame, *, signal, window, target,
                        percentile_window=PWIN) -> pd.Series:
        idx = ohlcv.index
        closes = {tk: s.reindex(idx) for tk, s in panel_closes.items()}
        closes[target] = ohlcv["close"].astype(float)  # target from the frame
        return xr.regime_conditioned_positions(
            closes, target=target, signal=signal, window=window,
            percentile_window=percentile_window)
    return regime_strategy


def _position_stats(pos: pd.Series, window: int) -> dict:
    """Exposure / degeneracy diagnostics for a conditioned lane. The warmed
    region drops the leading (window + PWIN) undefined-resolved-to-0 bars."""
    p = pos.astype(float)
    warm = p.iloc[window + PWIN:]
    warm_std = float(warm.std()) if len(warm) else float("nan")
    return {
        "pos_mean_all": float(p.mean()),
        "pos_mean_warm": float(warm.mean()) if len(warm) else None,
        "pos_std_warm": _clean(warm_std),
        "pos_nunique_warm": int(warm.nunique()) if len(warm) else 0,
        "frac_fully_invested_warm": (float((warm > 0.99).mean())
                                     if len(warm) else None),
        "frac_flat_warm": float((warm < 0.01).mean()) if len(warm) else None,
        "warm_bars": int(len(warm)),
        "degenerate_near_constant": bool(
            not math.isnan(warm_std) and warm_std < DEGENERATE_POS_STD),
    }


def assert_prefix_invariance(panel_closes: dict, index) -> dict:
    """RUN-side re-assertion of the plan §4 headline control on the REAL cached
    panels: for a spread of bars t across all 3 signals × 3 windows, the regime
    score AND the conditioned position at bar t are IDENTICAL on the full panel
    vs the panel truncated at bar t (``series.iloc[:t+1]``). Trailing windows +
    rolling (never full-sample) normalization forbid any dependence on data with
    timestamp > t. Returns a machine-readable report; raises AssertionError (STOP)
    on any leak."""
    n = len(index)
    max_score_diff = 0.0
    max_pos_diff = 0.0
    checks = 0
    for signal in xr.REGIME_SIGNALS:
        for window in sweeps._R11_WINDOWS:
            full_score = xr.regime_score(panel_closes, signal, window)
            full_pos = xr.regime_conditioned_positions(
                panel_closes, target="NVDA", signal=signal, window=window,
                percentile_window=PWIN)
            probe_ts = sorted({window + PWIN + 1, window + PWIN + 40,
                               n // 2, n - 60, n - 1})
            for t in probe_ts:
                if not (0 <= t < n):
                    continue
                trunc = {k: v.iloc[:t + 1] for k, v in panel_closes.items()}
                ts = xr.regime_score(trunc, signal, window)
                tp = xr.regime_conditioned_positions(
                    trunc, target="NVDA", signal=signal, window=window,
                    percentile_window=PWIN)
                a, b = full_score.iloc[t], ts.iloc[t]
                if not ((np.isnan(a) and np.isnan(b)) or a == b):
                    raise AssertionError(
                        f"SCORE LEAK on real panel at t={t} signal={signal} "
                        f"W={window}: full={a!r} trunc={b!r}")
                if not (np.isnan(a) and np.isnan(b)):
                    max_score_diff = max(max_score_diff, abs(float(a) - float(b)))
                pa, pb = full_pos.iloc[t], tp.iloc[t]
                if pa != pb:
                    raise AssertionError(
                        f"POSITION LEAK on real panel at t={t} signal={signal} "
                        f"W={window}: full={pa!r} trunc={pb!r}")
                max_pos_diff = max(max_pos_diff, abs(float(pa) - float(pb)))
                checks += 1
    return {
        "test": "tests/test_xasset_regime.py::TestNoLookahead (RUN-side "
                "re-assertion on the REAL cached panels)",
        "passed": True,
        "checks": checks,
        "signals": list(xr.REGIME_SIGNALS),
        "windows": list(sweeps._R11_WINDOWS),
        "max_score_abs_diff_full_vs_trunc": max_score_diff,
        "max_position_abs_diff_full_vs_trunc": max_pos_diff,
        "note": ("Prefix invariance holds bit-for-bit on the real dev panels: "
                 "the causal regime labels use only data with timestamp <= t, so "
                 "any reported edge is NOT a hindsight artifact. This is the #1 "
                 "failure mode for this class, reported as a first-class result."),
    }


def _stitched_sharpe(strategy, ohlcv, params, windows) -> float:
    """Selection-free stitched OOS Sharpe of one config over the committed test
    windows, computed with the SAME ``selection_gate.stitched_replay`` the gate
    uses internally (so the fidelity guard reproduces it bit-for-bit)."""
    rows = [{"test": [w[0], w[1]], "params": params} for w in windows]
    stitched, _ = selection_gate.stitched_replay(
        ohlcv, strategy, rows, TIMEFRAME, costs=COSTS)
    return metrics.sharpe(stitched, TIMEFRAME)


def run_target(target: str, panel: dict, program_cumulative: int) -> dict:
    """Run all 9 (signal, window) lanes on one target, graded against the
    target's unconditioned buy-and-hold control. Returns per-lane result rows."""
    ohlcv = panel["frames"][target]              # holdout excluded by default
    panel_closes = panel["closes"]               # aligned legs (shared index)
    strategy = make_regime_strategy(panel_closes)

    # Unconditioned CONTROL ARM: plain buy-and-hold of the target (position ≡ 1).
    bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME, **COSTS)
    bench_full_m = metrics.compute_all(bench_full)
    bench_sharpe = bench_full_m["sharpe"]
    bench_trades = int(len(bench_full.trades))

    # Walk-forward test windows (contiguous, 1008/252) for the gate.
    splits = generate_splits(len(ohlcv), TRAIN_SIZE, TEST_SIZE)
    windows = [[s.test_start, s.test_end] for s in splits]

    # The 9 (signal, window) configs searched for THIS target (plan §7). Precompute
    # each config's selection-free stitched OOS Sharpe and pick the BEST-of-9 —
    # the searched arm the gate fidelity-guards on every lane of this target.
    lane_configs = [{"signal": s, "window": w}
                    for s in sweeps._R11_SIGNALS for w in sweeps._R11_WINDOWS]
    stitched_by_cfg = {}
    for c in lane_configs:
        params = {"signal": c["signal"], "window": c["window"],
                  "target": target, "percentile_window": PWIN}
        stitched_by_cfg[(c["signal"], c["window"])] = _stitched_sharpe(
            strategy, ohlcv, params, windows)
    best_key = max(
        stitched_by_cfg,
        key=lambda kk: (stitched_by_cfg[kk]
                        if not (isinstance(stitched_by_cfg[kk], float)
                                and math.isnan(stitched_by_cfg[kk]))
                        else float("-inf")))
    best_stitched = stitched_by_cfg[best_key]
    best_cfg = {"signal": best_key[0], "window": best_key[1]}

    per_lane_min_t = promotion.min_tstat(len(lane_configs))   # K=9 per-lane bar
    program_min_t = promotion.min_tstat(sweeps.R11_K)         # K=27 program bar

    lane_rows = []
    lane_full_sharpe = {}
    for c in lane_configs:
        signal, window = c["signal"], c["window"]

        # 1) Full-dev-period backtest of the conditioned positions.
        positions = xr.regime_conditioned_positions(
            panel_closes, target=target, signal=signal, window=window,
            percentile_window=PWIN)
        # positions are indexed on the common panel index == ohlcv.index.
        res = run_backtest(ohlcv, positions, timeframe=TIMEFRAME, **COSTS)
        full_m = metrics.compute_all(res)
        lane_sharpe = full_m["sharpe"]
        n_trades = int(len(res.trades))
        pstats = _position_stats(positions, window)
        lane_full_sharpe[(signal, window)] = lane_sharpe

        # Round-2 KEEP/KILL rule; ties/ambiguity resolve KILL. The control arm IS
        # the benchmark (beats-its-own-buy-and-hold-Sharpe).
        beats_base = (lane_sharpe is not None and bench_sharpe is not None
                      and lane_sharpe > bench_sharpe)
        keep = bool(beats_base and lane_sharpe > 0)
        if lane_sharpe is not None and bench_sharpe is not None:
            grade = promotion.grade_promotion(
                strategy_sharpe=lane_sharpe, benchmark_sharpe=bench_sharpe,
                n_periods=full_m["n_bars"], timeframe=TIMEFRAME,
                variants_tried=len(lane_configs))
        else:  # degenerate — honest KILL, no arithmetic
            grade = {"verdict": None, "tstat": None,
                     "min_tstat": per_lane_min_t,
                     "note": "not computable: lane or benchmark Sharpe is NaN"}
        verdict_pre_gate = promotion.classify_verdict(
            keep, grade.get("tstat"), grade.get("min_tstat"))

        # 2) Selection-fair gate. searched arm = target BEST-of-9 (armed for the
        #    fidelity guard); fixed arm = this lane's config.
        searched_per_split = [
            {"test": w, "params": {"signal": best_cfg["signal"],
                                   "window": best_cfg["window"],
                                   "target": target,
                                   "percentile_window": PWIN}}
            for w in windows]
        gate = selection_gate.run_selection_gate(
            ohlcv=ohlcv, strategy=strategy,
            per_split=searched_per_split,
            top_variant={"signal": signal, "window": window, "target": target,
                         "percentile_window": PWIN},
            timeframe=TIMEFRAME, costs=COSTS,
            recorded_searched_sharpe=best_stitched)
        verdict = selection_gate.apply_gate(verdict_pre_gate, gate)

        base_gap = (lane_sharpe - bench_sharpe
                    if (lane_sharpe is not None and bench_sharpe is not None)
                    else None)
        lane_record = {
            "schema_version": 1,
            "sweep": SLICE,
            "created_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "target": target,
            "signal": signal,
            "window": window,
            "percentile_window": PWIN,
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": ("live owner turn 2026-07-19 / ORDER 021; "
                      "pre-registered docs/research-round-11-plan.md"),
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "costs": dict(COSTS),
            "execution": "signal at bar t fills at bar t+1 open",
            "benchmark": ("unconditioned buy-and-hold of the target "
                          "(position == 1.0, the mandatory control arm)"),
            "lane_variants_tried": len(lane_configs),
            "program_variants_tried": program_cumulative,
            "full_period_metrics": {k2: full_m[k2]
                                    for k2 in VARIANT_METRIC_KEYS
                                    if k2 in full_m} | {
                "n_bars": full_m["n_bars"]},
            "benchmark_full_period_metrics": bench_full_m,
            "control_arm": {
                "note": ("mandatory unconditioned control arm (plan §5): base "
                         "buy-and-hold Sharpe of the target reported next to the "
                         "conditioned lane; a lane that fails to beat its own "
                         "hold is not a candidate"),
                "base_hold_sharpe": bench_sharpe,
                "conditioned_sharpe": lane_sharpe,
                "beats_base_hold": bool(beats_base),
                "sharpe_gap_vs_base_hold": base_gap,
            },
            "position_stats": pstats,
            "selection_gate": {
                "note": ("standing gate [D-0002] (docs/selection-fair-gate.md) "
                         "on EVERY R11 lane; doubles as the R5-D fixed-config "
                         "row. searched arm = target BEST-of-9 (signal, window) "
                         "config (plan §7 search dimension); fixed arm = this "
                         "lane's config; selection_gap informational, no "
                         "registered threshold; gate replay report-only "
                         "(R4-B precedent), not ledgered"),
                "searched_config": {"signal": best_cfg["signal"],
                                    "window": best_cfg["window"]},
                **gate,
            },
            "verdict_pre_gate": verdict_pre_gate,
            "verdict": verdict,
            "promotion_grade": {
                "note": ("Lo-2002 Sharpe-delta t on the full-dev-period lane "
                         "Sharpe vs same-target buy-and-hold (the unconditioned "
                         "control), Bonferroni K = 9 (signal, window) configs on "
                         "this target — INFORMATIONAL ONLY, promotion is CLOSED "
                         "post-holdout"),
                "program_min_tstat_K27": program_min_t,
                **grade,
            },
        }
        out = SWEEP_DIR / f"{signal}__w{window}__{target}.json"
        out.write_text(json.dumps(lane_record, indent=2, sort_keys=True) + "\n")
        print(f"{target} {signal}/w{window}: sharpe={lane_sharpe} "
              f"base_hold={bench_sharpe} t={grade.get('tstat')} "
              f"beats_hold={beats_base} pos_mean={pstats['pos_mean_warm']} "
              f"pos_std={pstats['pos_std_warm']} gate={gate['gate']} {verdict}")

        lane_rows.append({
            "target": target, "signal": signal, "window": window,
            "lane_sharpe": lane_sharpe, "bench_sharpe": bench_sharpe,
            "beats_base_hold": bool(beats_base),
            "sharpe_gap_vs_base_hold": base_gap,
            "n_trades": n_trades, "bench_trades": bench_trades,
            "pos_mean_warm": pstats["pos_mean_warm"],
            "pos_std_warm": pstats["pos_std_warm"],
            "pos_nunique_warm": pstats["pos_nunique_warm"],
            "frac_fully_invested_warm": pstats["frac_fully_invested_warm"],
            "degenerate_near_constant": pstats["degenerate_near_constant"],
            "tstat": grade.get("tstat"), "min_tstat_K9": grade.get("min_tstat"),
            "min_tstat_K27": program_min_t,
            "gate": gate["gate"], "gate_reason": gate["reason"],
            "reason_class": gate["reason_class"],
            "fixed_sharpe": gate["fixed_sharpe"],
            "searched_sharpe": gate["searched_sharpe"],
            "selection_gap": gate["selection_gap"],
            "verdict_pre_gate": verdict_pre_gate, "verdict": verdict})

    # Ledger the target's BEST-of-9 (by full-period Sharpe) config,
    # variants_tried=9 (plan: top config LEDGERED with the round's searched K
    # per target).
    best_full_key = max(
        lane_full_sharpe,
        key=lambda kk: (lane_full_sharpe[kk]
                        if lane_full_sharpe[kk] is not None else float("-inf")))
    best_positions = xr.regime_conditioned_positions(
        panel_closes, target=target, signal=best_full_key[0],
        window=best_full_key[1], percentile_window=PWIN)
    best_res = run_backtest(ohlcv, best_positions, timeframe=TIMEFRAME, **COSTS)
    ledger_rec = ledger.build_record(
        strategy=f"r11_xasset_regime_{best_full_key[0]}_w{best_full_key[1]}",
        params={"signal": best_full_key[0], "window": best_full_key[1],
                "target": target, "percentile_window": PWIN,
                "conditioning": "causal_rolling_percentile_rank"},
        instrument=target, timeframe=TIMEFRAME, ohlcv=ohlcv,
        result=best_res, benchmark=bench_full,
        variants_tried=len(lane_configs),
        notes=(f"Round 11 cross-asset regime conditioning (post-holdout "
               f"DEV-ONLY, promotion CLOSED — live owner turn 2026-07-19 / "
               f"ORDER 021; pre-registered docs/research-round-11-plan.md): "
               f"target top config of {len(lane_configs)} (signal, window) "
               f"tried (post-hoc selection — the per-lane grades and the "
               f"selection-fair gate blocks live in "
               f"experiments/sweeps/{SLICE}/*__{target}.json)"))
    ledger.write_run(ledger_rec)

    return {"target": target, "lanes": lane_rows,
            "bench_sharpe": bench_sharpe}


def main() -> None:
    t0 = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)

    executed = sweeps.r11_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + executed
    targets = list(sweeps._R11_TARGETS)
    # Verify the pinned grid == the configs actually run. STOP on drift.
    planned = (len(sweeps._R11_SIGNALS) * len(sweeps._R11_WINDOWS)
               * len(sweeps._R11_TARGETS))
    assert executed == 27 and planned == 27, (
        f"grid drifted from the pinned Round-11 plan: r11_total_configs()="
        f"{executed}, signals×windows×targets={planned} (expected 27)")
    print(f"R11 xasset-regime: {len(sweeps._R11_SIGNALS)} signals × "
          f"{len(sweeps._R11_WINDOWS)} windows × {len(targets)} targets = "
          f"{executed} registered configs (program cumulative "
          f"{program_cumulative}); cap {CAP_SECONDS} s")

    panel = load_aligned_panel()

    # HEADLINE control (plan §4): re-assert prefix invariance on the REAL panels
    # BEFORE grading. A leak here STOPS the round.
    print("re-asserting no-lookahead / prefix invariance on the REAL cached "
          "panels ...")
    prefix_report = assert_prefix_invariance(panel["closes"], panel["index"])
    print(f"  PASS: {prefix_report['checks']} checks, max |score diff| "
          f"{prefix_report['max_score_abs_diff_full_vs_trunc']:.2e}, "
          f"max |position diff| "
          f"{prefix_report['max_position_abs_diff_full_vs_trunc']:.2e}")

    results, cap_hit, skipped = [], False, []
    for i, target in enumerate(targets):
        elapsed = time.monotonic() - t0
        if elapsed >= CAP_SECONDS:
            cap_hit = True
            skipped = list(targets[i:])
            print(f"CAP-HIT: elapsed {elapsed:.1f} s >= cap {CAP_SECONDS} s "
                  f"before {target}; STOPPING with {len(skipped)} targets "
                  f"skipped (no silent truncation)")
            break
        results.append(run_target(target, panel, program_cumulative))

    lanes = [r for res in results for r in res["lanes"]]
    runtime = time.monotonic() - t0

    # Verdict + gate rollups.
    counts = {v: sum(1 for r in lanes if r["verdict"] == v)
              for v in (promotion.SWEEP_KEEP, promotion.SWEEP_KILL,
                        promotion.SWEEP_KILL_SIG)}
    gate_counts = {g: sum(1 for r in lanes if r["gate"] == g)
                   for g in (selection_gate.GATE_PASS,
                             selection_gate.GATE_FAIL)}
    demoted = sum(1 for r in lanes
                  if r["verdict_pre_gate"] == promotion.SWEEP_KEEP
                  and r["verdict"] != promotion.SWEEP_KEEP)
    reason_rollup = {rc: sum(1 for r in lanes if r["reason_class"] == rc)
                     for rc in sorted(selection_gate.REASON_CLASSES)}
    ungradeable = sum(v for rc, v in reason_rollup.items()
                      if rc in selection_gate.UNGRADEABLE_CLASSES)

    # Control-arm rollup: how many of the 27 lanes beat their own base hold.
    beat_lanes = [r for r in lanes if r["beats_base_hold"]]
    n_beat = len(beat_lanes)
    gaps = [r["sharpe_gap_vs_base_hold"] for r in lanes
            if r["sharpe_gap_vs_base_hold"] is not None]
    best_gap_lane = max(lanes, key=lambda r: (
        r["sharpe_gap_vs_base_hold"]
        if r["sharpe_gap_vs_base_hold"] is not None else float("-inf")))
    worst_gap_lane = min(lanes, key=lambda r: (
        r["sharpe_gap_vs_base_hold"]
        if r["sharpe_gap_vs_base_hold"] is not None else float("inf")))
    degenerate_lanes = [
        {"target": r["target"], "signal": r["signal"], "window": r["window"],
         "pos_std_warm": r["pos_std_warm"]}
        for r in lanes if r["degenerate_near_constant"]]

    # Flat results CSV.
    with (SWEEP_DIR / "results.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["target", "signal", "window", "lane_sharpe", "bench_sharpe",
                    "beats_base_hold", "sharpe_gap_vs_base_hold", "n_trades",
                    "pos_mean_warm", "pos_std_warm", "pos_nunique_warm",
                    "frac_fully_invested_warm", "degenerate_near_constant",
                    "tstat", "min_tstat_K9", "min_tstat_K27", "fixed_sharpe",
                    "searched_sharpe", "selection_gap", "gate", "reason_class",
                    "verdict"])
        for r in lanes:
            w.writerow([r["target"], r["signal"], r["window"], r["lane_sharpe"],
                        r["bench_sharpe"], r["beats_base_hold"],
                        r["sharpe_gap_vs_base_hold"], r["n_trades"],
                        r["pos_mean_warm"], r["pos_std_warm"],
                        r["pos_nunique_warm"], r["frac_fully_invested_warm"],
                        r["degenerate_near_constant"], r["tstat"],
                        r["min_tstat_K9"], r["min_tstat_K27"], r["fixed_sharpe"],
                        r["searched_sharpe"], r["selection_gap"], r["gate"],
                        r["reason_class"], r["verdict"]])

    # Base-hold comparison table (plan §5 artifact): every conditioned lane's
    # Sharpe/t next to its target's base buy-and-hold.
    base_hold_table = [{
        "target": r["target"], "signal": r["signal"], "window": r["window"],
        "conditioned_sharpe": r["lane_sharpe"], "base_hold_sharpe": r["bench_sharpe"],
        "beats_base_hold": r["beats_base_hold"],
        "sharpe_gap_vs_base_hold": r["sharpe_gap_vs_base_hold"],
        "tstat": r["tstat"], "verdict": r["verdict"]} for r in lanes]
    (SWEEP_DIR / "base_hold_comparison.json").write_text(
        json.dumps({"note": ("mandatory unconditioned control arm (plan §5): "
                             "each conditioned lane's Sharpe/t next to its "
                             "target's base buy-and-hold Sharpe"),
                    "lanes_beating_base_hold": n_beat,
                    "lanes_total": len(lanes),
                    "table": base_hold_table}, indent=2, sort_keys=True) + "\n")

    best_keep = None
    for r in lanes:
        if r["verdict"] == promotion.SWEEP_KEEP and r["tstat"] is not None:
            if best_keep is None or r["tstat"] > best_keep["tstat"]:
                best_keep = r
    best_any = None
    for r in lanes:
        if r["tstat"] is not None and (best_any is None
                                       or r["tstat"] > best_any["tstat"]):
            best_any = r

    summary = {
        "schema_version": 1,
        "sweep": SLICE,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": ledger.git_sha(),
        "order": ("live owner turn 2026-07-19 / ORDER 021; pre-registered "
                  "docs/research-round-11-plan.md"),
        "post_holdout_dev_only": True,
        "registered_configs": executed,
        "program_variants_tried": program_cumulative,
        "min_tstat_K9": promotion.min_tstat(9),
        "min_tstat_K27": promotion.min_tstat(sweeps.R11_K),
        "targets_planned": len(targets),
        "targets_run": len(results),
        "lanes_run": len(lanes),
        "runtime_seconds": round(runtime, 3),
        "cap_seconds": CAP_SECONDS,
        "cap_hit": cap_hit,
        "targets_skipped_on_cap": skipped,
        "prefix_invariance_control": prefix_report,
        "verdict_counts": counts,
        "gate_counts": gate_counts,
        "keeps_demoted_by_gate": demoted,
        "reason_class_rollup": reason_rollup,
        "ungradeable_lanes": ungradeable,
        "control_arm": {
            "lanes_beating_base_hold": n_beat,
            "lanes_total": len(lanes),
            "mean_sharpe_gap_vs_base_hold": (
                float(np.mean(gaps)) if gaps else None),
            "median_sharpe_gap_vs_base_hold": (
                float(np.median(gaps)) if gaps else None),
            "best_gap_lane": {
                "target": best_gap_lane["target"],
                "signal": best_gap_lane["signal"],
                "window": best_gap_lane["window"],
                "sharpe_gap_vs_base_hold":
                    best_gap_lane["sharpe_gap_vs_base_hold"]},
            "worst_gap_lane": {
                "target": worst_gap_lane["target"],
                "signal": worst_gap_lane["signal"],
                "window": worst_gap_lane["window"],
                "sharpe_gap_vs_base_hold":
                    worst_gap_lane["sharpe_gap_vs_base_hold"]},
        },
        "base_hold_sharpes": {res["target"]: res["bench_sharpe"]
                              for res in results},
        "degenerate_lanes": degenerate_lanes,
        "best_keep_lane": best_keep,
        "best_tstat_lane": best_any,
        "lanes": lanes,
    }
    (SWEEP_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts} · gate {gate_counts} · {demoted} KEEP demoted "
          f"by gate · UNGRADEABLE {ungradeable} · lanes beating base hold "
          f"{n_beat}/{len(lanes)} · degenerate lanes {len(degenerate_lanes)} · "
          f"runtime {runtime:.1f} s (cap {CAP_SECONDS} s"
          f"{' — CAP-HIT' if cap_hit else ' — not hit'})")
    if best_any:
        print(f"best t any lane: {best_any['target']} "
              f"{best_any['signal']}/w{best_any['window']} "
              f"t={best_any['tstat']:.3f} (K9 bar "
              f"{promotion.min_tstat(9):.3f}, K27 bar "
              f"{promotion.min_tstat(sweeps.R11_K):.3f})")
    print(f"best base-hold gap: {best_gap_lane['target']} "
          f"{best_gap_lane['signal']}/w{best_gap_lane['window']} "
          f"gap={best_gap_lane['sharpe_gap_vs_base_hold']}")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
