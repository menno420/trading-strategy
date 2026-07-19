#!/usr/bin/env python3
"""Round 9 — signal-confluence vote (cross-class ≥K-of-N) × 15 daily tickers.

POST-HOLDOUT, DEV-ONLY (live owner turn 2026-07-19 / ORDER 019; pre-registered
protocol ``docs/research-round-9-plan.md``, merged as PR #153 BEFORE any
Round-9 outcome existed). Promotion is CLOSED: nothing this script produces can
be an out-of-sample claim; KEEPs are dev-candidates only.

The owner's idea, verbatim: *"isn't it a good idea to find multiple strategies
and wait untill at least 2 or 3 give the same signals?"* Round 9 tests exactly
that — a binary cross-thesis-class ≥K-of-N majority VOTE
(``trading_lab.ensemble.confluence_positions``): long (1.0) on a bar iff at
least K of N DISTINCT-class members are simultaneously long, else flat. Members
run at their FIXED ``DEFAULT_PARAMS`` (NO per-member re-search — pre-registered
§3): the only searched axis is (member-set, K). Two panels (SET-3
trend/mean-rev/breakout; SET-5 adds drawdown STATE + volume), K ∈ {2, 3} ⇒ 4
vote configs, over the committed 15-ticker daily surface = 15 × 4 = **60**
registered configs (``sweeps.r9_total_configs()`` = 60); program cumulative
**5,793 → 5,853**.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; holdout SPENT, never read). Costs: 5 bps slippage +
1 bp commission per side. Execution: signal at bar t fills at bar t+1 open.

For every (instrument × vote config) lane this script produces:

1. **A full-dev-period backtest** of the confluence positions (members fixed at
   default params, so the full-period run IS a fixed-config evaluation — no
   in-sample parameter selection lives inside a lane). Sharpe-delta t vs
   full-period buy-and-hold via ``promotion.grade_promotion`` (the SAME
   machinery every prior round uses), Bonferroni K = 4 (the vote configs
   searched on the instrument); ``classify_verdict`` for KILL-SIG. The
   informational t is ALSO reported against the program-wide K = 60 bar.
2. **The selection-fair standing gate** ([D-0002], round-6+) on EVERY lane —
   ``run_selection_gate`` over contiguous 1008/252 walk-forward test windows,
   the searched arm armed with the instrument's BEST-of-4 stitched OOS Sharpe
   (the round's (member-set, K) search dimension, plan §9), folded through
   ``apply_gate`` BEFORE the verdict is written. The gate block doubles as the
   R5-D fixed-config row: ``fixed_sharpe`` (this config, selection-free over
   the windows), ``searched_sharpe`` (best-of-4), ``selection_gap = searched −
   fixed`` (informational, no registered threshold).
3. **The pre-registered correlation check** (§6) per instrument: pairwise
   member POSITION correlation (0/1 lanes), signal-overlap Jaccard, member
   daily RETURN correlation; the mean pairwise position-correlation and the
   >~0.5 disqualification flag ("one signal counted twice").
4. **The pre-registered trade-count / power impact** (§7) per instrument:
   trades(single-member mean), trades(K=2), trades(K=3), the shrinkage factor
   vs single members, and the implied Sharpe-SE inflation (SE ∝
   sqrt((1 + SR²/2) / N)). Zero/near-zero-trade K=3 lanes are flagged
   degenerate, never hidden.

The round's top vote config per instrument is LEDGERED with ``variants_tried=4``
(gate replays are report-only rows in the lane JSON — R4-B precedent).

Runtime cap (self-enforced): <= 900 s wall-clock. The cap is checked before
each instrument; a would-be overrun STOPS the slice and records CAP-HIT — no
silent truncation.

Usage: python3 scripts/run_r9_confluence_sweep.py
"""

import csv
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from trading_lab import (config, ledger, metrics, promotion,  # noqa: E402
                         selection_gate, sweeps)
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import (BacktestResult, buy_and_hold_result,  # noqa: E402
                                run_backtest)
from trading_lab.ensemble import confluence_positions  # noqa: E402
from trading_lab.strategies import DEFAULT_PARAMS, STRATEGIES  # noqa: E402
from trading_lab.walkforward import generate_splits  # noqa: E402

SLICE = "r9-confluence"
TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; contiguous non-overlapping test windows
CAP_SECONDS = 900  # self-enforced: <= 15 min wall-clock for the slice

# Program burden prior to this slice: 5,793 registered configs
# (docs/cross-round-meta-analysis.md closing tally, Round 8). Round 9 lands
# its 60 on top: 5,793 -> 5,853.
PROGRAM_PRIOR_CONFIGS = 5793

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SLICE

COSTS = {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
         "commission_bps": config.DEFAULT_COMMISSION_BPS}

# Pre-registered correlation-disqualification threshold (plan §6, verbatim):
# "if mean pairwise member position-correlation on an instrument exceeds ~0.5,
# any apparent vote edge is not diversified and must be reported as such."
CORR_FLAG = 0.5

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


def confluence_strategy(ohlcv: pd.DataFrame, *, members, k) -> pd.Series:
    """The R9 lane compositor as a ``strategy(ohlcv, **params)`` callable so
    the selection-fair gate can replay it exactly like any family. Each member
    is generated at its FIXED default params over ``ohlcv`` (causal — the gate
    passes trailing history ``ohlcv.iloc[:test_end]``), then the binary
    ≥k-of-N vote is applied on the shared index."""
    member_pos = [STRATEGIES[m](ohlcv, **DEFAULT_PARAMS[m]) for m in members]
    return confluence_positions(member_pos, k)


def member_positions(ohlcv: pd.DataFrame, members) -> dict:
    """Full-dev-period 0/1 position series for each panel member (fixed
    default params)."""
    return {m: STRATEGIES[m](ohlcv, **DEFAULT_PARAMS[m]) for m in members}


def member_returns(ohlcv: pd.DataFrame, pos_by_member: dict) -> dict:
    """Per-member net daily RETURN streams (each member backtested alone at
    baseline costs) — for the pre-registered return-correlation matrix."""
    out = {}
    for m, pos in pos_by_member.items():
        res = run_backtest(ohlcv, pos, timeframe=TIMEFRAME, **COSTS)
        out[m] = res.returns
    return out


def member_trade_counts(ohlcv: pd.DataFrame, pos_by_member: dict) -> dict:
    out = {}
    for m, pos in pos_by_member.items():
        res = run_backtest(ohlcv, pos, timeframe=TIMEFRAME, **COSTS)
        out[m] = int(len(res.trades))
    return out


def _mean_offdiag(corr: pd.DataFrame) -> float:
    cols = list(corr.columns)
    n = len(cols)
    vals = [corr.iloc[i, j] for i in range(n) for j in range(i + 1, n)
            if not pd.isna(corr.iloc[i, j])]
    return float(sum(vals) / len(vals)) if vals else float("nan")


def _jaccard_matrix(pos_by_member: dict) -> dict:
    """Pairwise signal-overlap Jaccard = bars-both-long / bars-either-long."""
    members = list(pos_by_member)
    out = {}
    for a in members:
        row = {}
        pa = pos_by_member[a] > 0
        for b in members:
            pb = pos_by_member[b] > 0
            either = int((pa | pb).sum())
            both = int((pa & pb).sum())
            row[b] = (both / either) if either > 0 else None
        out[a] = row
    return out


def correlation_block(ohlcv: pd.DataFrame, set5_members) -> dict:
    """The full pre-registered §6 correlation/overlap report for one
    instrument (SET-5 superset; SET-3 is its 3×3 sub-block)."""
    pos = member_positions(ohlcv, set5_members)
    pos_df = pd.DataFrame(pos)
    rets = member_returns(ohlcv, pos)
    ret_df = pd.DataFrame(rets)

    pos_corr = pos_df.corr()
    ret_corr = ret_df.corr()
    jac = _jaccard_matrix(pos)

    set3 = set5_members[:3]
    mean_pos_set5 = _mean_offdiag(pos_corr)
    mean_pos_set3 = _mean_offdiag(pos_corr.loc[set3, set3])
    return {
        "members_set5": list(set5_members),
        "members_set3": list(set3),
        "position_correlation": {a: {b: _clean(float(pos_corr.loc[a, b]))
                                     for b in set5_members}
                                 for a in set5_members},
        "return_correlation": {a: {b: _clean(float(ret_corr.loc[a, b]))
                                   for b in set5_members}
                               for a in set5_members},
        "signal_overlap_jaccard": jac,
        "mean_pairwise_position_corr": {
            "set3": _clean(mean_pos_set3),
            "set5": _clean(mean_pos_set5),
        },
        "flag_gt_0p5": {
            "set3": bool(mean_pos_set3 > CORR_FLAG),
            "set5": bool(mean_pos_set5 > CORR_FLAG),
            "threshold": CORR_FLAG,
            "rule": ("Confluence between correlated members is one signal "
                     "counted twice; if mean pairwise member "
                     "position-correlation on an instrument exceeds ~0.5, any "
                     "apparent vote edge is not diversified and must be "
                     "reported as such."),
        },
    }


def _stitched_sharpe(ohlcv, members, k, windows) -> float:
    """Selection-free stitched OOS Sharpe of a vote config over the committed
    test windows, computed with the SAME ``selection_gate.stitched_replay``
    the gate uses internally (so the fidelity guard reproduces it bit-for-bit)."""
    rows = [{"test": [w[0], w[1]], "params": {"members": members, "k": k}}
            for w in windows]

    def strat(o, **params):
        return confluence_strategy(o, **params)

    stitched, _ = selection_gate.stitched_replay(
        ohlcv, strat, rows, TIMEFRAME, costs=COSTS)
    return metrics.sharpe(stitched, TIMEFRAME)


def run_instrument(ticker: str, program_cumulative: int) -> dict:
    """Run all 4 vote-config lanes on one instrument, plus the §6 correlation
    block and §7 trade-count block. Returns per-lane result rows."""
    ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
    set5 = list(sweeps._R9_MEMBER_SET_5)
    vote_configs = sweeps.r9_vote_configs()

    bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME, **COSTS)
    bench_full_m = metrics.compute_all(bench_full)
    bench_sharpe = bench_full_m["sharpe"]

    # §6 correlation / overlap (superset panel; SET-3 is a sub-block).
    corr = correlation_block(ohlcv, set5)

    # §7 trade-count building blocks: single members at fixed params.
    pos5 = member_positions(ohlcv, set5)
    single_trades = member_trade_counts(ohlcv, pos5)

    # Walk-forward test windows (contiguous, 1008/252) for the gate.
    splits = generate_splits(len(ohlcv), TRAIN_SIZE, TEST_SIZE)
    windows = [[s.test_start, s.test_end] for s in splits]

    # Pre-compute each vote config's selection-free stitched OOS Sharpe over
    # the windows, and pick the instrument's BEST-of-4 (the round's
    # (member-set, K) search dimension — plan §9). This best is the searched
    # arm the gate fidelity-guards on every lane of this instrument.
    stitched_by_cfg = {}
    for c in vote_configs:
        key = (c["set"], c["k"])
        stitched_by_cfg[key] = _stitched_sharpe(
            ohlcv, c["members"], c["k"], windows)
    best_key = max(
        stitched_by_cfg,
        key=lambda kk: (stitched_by_cfg[kk]
                        if not (isinstance(stitched_by_cfg[kk], float)
                                and math.isnan(stitched_by_cfg[kk]))
                        else float("-inf")))
    best_stitched = stitched_by_cfg[best_key]
    best_cfg = next(c for c in vote_configs
                    if (c["set"], c["k"]) == best_key)

    program_min_t = promotion.min_tstat(sweeps.R9_K)  # K=60 program bar

    lane_rows = []
    per_set_vote_trades = {"set3": {}, "set5": {}}
    lane_full_sharpe = {}
    for c in vote_configs:
        set_name, members, k = c["set"], c["members"], c["k"]

        # 1) Full-dev-period backtest of the confluence positions.
        positions = confluence_positions(
            [pos5[m] for m in members], k)
        res = run_backtest(ohlcv, positions, timeframe=TIMEFRAME, **COSTS)
        full_m = metrics.compute_all(res)
        lane_sharpe = full_m["sharpe"]
        n_trades = int(len(res.trades))
        per_set_vote_trades[set_name][f"k{k}"] = n_trades
        lane_full_sharpe[(set_name, k)] = lane_sharpe

        # Round-2 KEEP/KILL rule; ties/ambiguity resolve KILL.
        keep = (lane_sharpe is not None and bench_sharpe is not None
                and lane_sharpe > bench_sharpe and lane_sharpe > 0)
        if lane_sharpe is not None and bench_sharpe is not None:
            grade = promotion.grade_promotion(
                strategy_sharpe=lane_sharpe, benchmark_sharpe=bench_sharpe,
                n_periods=full_m["n_bars"], timeframe=TIMEFRAME,
                variants_tried=len(vote_configs))
        else:  # degenerate (e.g. all-flat lane) — honest KILL, no arithmetic
            grade = {"verdict": None, "tstat": None,
                     "min_tstat": promotion.min_tstat(len(vote_configs)),
                     "note": "not computable: lane or benchmark Sharpe is "
                             "NaN (degenerate / never-trading confluence)"}
        verdict_pre_gate = promotion.classify_verdict(
            keep, grade.get("tstat"), grade.get("min_tstat"))

        # 2) Selection-fair gate. searched arm = instrument BEST-of-4 (armed
        #    for the fidelity guard); fixed arm = this lane's config.
        searched_per_split = [
            {"test": w, "params": {"members": best_cfg["members"],
                                   "k": best_cfg["k"]}} for w in windows]
        gate = selection_gate.run_selection_gate(
            ohlcv=ohlcv, strategy=confluence_strategy,
            per_split=searched_per_split,
            top_variant={"members": members, "k": k},
            timeframe=TIMEFRAME, costs=COSTS,
            recorded_searched_sharpe=best_stitched)
        verdict = selection_gate.apply_gate(verdict_pre_gate, gate)

        mean_pos_corr = corr["mean_pairwise_position_corr"][set_name]
        lane_record = {
            "schema_version": 1,
            "sweep": SLICE,
            "created_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "instrument": ticker,
            "set": set_name,
            "k": k,
            "members": list(members),
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": ("live owner turn 2026-07-19 / ORDER 019; "
                      "pre-registered docs/research-round-9-plan.md"),
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "costs": dict(COSTS),
            "execution": "signal at bar t fills at bar t+1 open",
            "lane_variants_tried": len(vote_configs),
            "program_variants_tried": program_cumulative,
            "full_period_metrics": {k2: full_m[k2]
                                    for k2 in VARIANT_METRIC_KEYS
                                    if k2 in full_m} | {
                "n_bars": full_m["n_bars"]},
            "benchmark_full_period_metrics": bench_full_m,
            "member_correlation": {
                "mean_pairwise_position_corr": mean_pos_corr,
                "flag_gt_0p5": bool(mean_pos_corr is not None
                                    and mean_pos_corr > CORR_FLAG),
            },
            "selection_gate": {
                "note": ("standing gate [D-0002] (docs/selection-fair-gate.md) "
                         "on EVERY R9 lane; doubles as the R5-D fixed-config "
                         "row. searched arm = instrument BEST-of-4 vote config "
                         "(plan §9 (member-set, K) search dimension); fixed arm "
                         "= this lane's config; selection_gap informational, no "
                         "registered threshold; gate replay report-only "
                         "(R4-B precedent), not ledgered"),
                "searched_config": {"set": best_cfg["set"], "k": best_cfg["k"]},
                **gate,
            },
            "verdict_pre_gate": verdict_pre_gate,
            "verdict": verdict,
            "promotion_grade": {
                "note": ("Lo-2002 Sharpe-delta t on the full-dev-period lane "
                         "Sharpe vs same-instrument buy-and-hold, Bonferroni "
                         "K = 4 vote configs on this instrument — INFORMATIONAL "
                         "ONLY, promotion is CLOSED post-holdout"),
                "program_min_tstat_K60": program_min_t,
                **grade,
            },
        }
        out = SWEEP_DIR / f"{set_name}_k{k}__{ticker}.json"
        out.write_text(json.dumps(lane_record, indent=2, sort_keys=True) + "\n")
        print(f"{ticker} {set_name}/k{k}: full_sharpe={lane_sharpe} "
              f"bench={bench_sharpe} t={grade.get('tstat')} "
              f"trades={n_trades} gate={gate['gate']} {verdict}")

        lane_rows.append({
            "instrument": ticker, "set": set_name, "k": k,
            "lane_sharpe": lane_sharpe, "bench_sharpe": bench_sharpe,
            "n_trades": n_trades,
            "tstat": grade.get("tstat"), "min_tstat_K4": grade.get("min_tstat"),
            "min_tstat_K60": program_min_t,
            "gate": gate["gate"], "gate_reason": gate["reason"],
            "reason_class": gate["reason_class"],
            "fixed_sharpe": gate["fixed_sharpe"],
            "searched_sharpe": gate["searched_sharpe"],
            "selection_gap": gate["selection_gap"],
            "mean_pos_corr": mean_pos_corr,
            "verdict_pre_gate": verdict_pre_gate, "verdict": verdict})

    # Ledger the instrument's BEST-of-4 (by full-period Sharpe) vote config,
    # variants_tried=4 (plan: top vote config LEDGERED with the round's
    # searched K per instrument).
    best_full_key = max(
        lane_full_sharpe,
        key=lambda kk: (lane_full_sharpe[kk]
                        if lane_full_sharpe[kk] is not None else float("-inf")))
    best_full_cfg = next(c for c in vote_configs
                         if (c["set"], c["k"]) == best_full_key)
    best_positions = confluence_positions(
        [pos5[m] for m in best_full_cfg["members"]], best_full_cfg["k"])
    best_res = run_backtest(ohlcv, best_positions, timeframe=TIMEFRAME, **COSTS)
    ledger_rec = ledger.build_record(
        strategy=f"r9_confluence_{best_full_cfg['set']}_k{best_full_cfg['k']}",
        params={"members": list(best_full_cfg["members"]),
                "k": best_full_cfg["k"], "vote": "confluence>=k-of-N"},
        instrument=ticker, timeframe=TIMEFRAME, ohlcv=ohlcv,
        result=best_res, benchmark=bench_full,
        variants_tried=len(vote_configs),
        notes=(f"Round 9 signal-confluence vote (post-holdout DEV-ONLY, "
               f"promotion CLOSED — live owner turn 2026-07-19 / ORDER 019; "
               f"pre-registered docs/research-round-9-plan.md): instrument "
               f"top vote config of {len(vote_configs)} tried "
               f"(post-hoc selection — the per-lane grades and the "
               f"selection-fair gate blocks live in "
               f"experiments/sweeps/{SLICE}/*__{ticker}.json)"))
    ledger.write_run(ledger_rec)

    # §7 trade-count / power impact for this instrument.
    trade_block = {}
    for set_name, mem in (("set3", set5[:3]), ("set5", set5)):
        single_mean = sum(single_trades[m] for m in mem) / len(mem)
        tk2 = per_set_vote_trades[set_name].get("k2")
        tk3 = per_set_vote_trades[set_name].get("k3")
        block = {
            "single_member_trades": {m: single_trades[m] for m in mem},
            "single_member_mean": single_mean,
            "trades_k2": tk2,
            "trades_k3": tk3,
            "shrink_k2": (tk2 / single_mean) if single_mean else None,
            "shrink_k3": (tk3 / single_mean) if single_mean else None,
            "degenerate_k3": bool(tk3 is not None and tk3 <= 5),
        }
        trade_block[set_name] = block
    return {"ticker": ticker, "lanes": lane_rows,
            "correlation": corr, "trade_counts": trade_block}


def _se_inflation(shrink: float) -> float:
    """Implied Sharpe-SE inflation from trade-count shrinkage. With SE(SR) ∝
    sqrt((1 + SR²/2)/N) and N ~ effective trades, the (1 + SR²/2) factor is
    ≈1 for the small Sharpes here, so SE_vote / SE_single ≈ 1/sqrt(shrink)."""
    if not shrink or shrink <= 0:
        return None
    return 1.0 / math.sqrt(shrink)


def main() -> None:
    t0 = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    instruments = list(sweeps.R9_INSTRUMENTS)
    executed = sweeps.r9_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + executed
    # Verify the pinned grid == the configs actually run. STOP on drift.
    planned = len(instruments) * len(sweeps.r9_vote_configs())
    assert executed == 60 and planned == 60, (
        f"grid drifted from the pinned Round-9 plan: r9_total_configs()="
        f"{executed}, instruments×votes={planned} (expected 60)")
    print(f"R9 confluence: {len(instruments)} instruments × "
          f"{len(sweeps.r9_vote_configs())} vote configs = {executed} "
          f"registered configs (program cumulative {program_cumulative}); "
          f"cap {CAP_SECONDS} s")

    results, cap_hit, skipped = [], False, []
    for i, ticker in enumerate(instruments):
        elapsed = time.monotonic() - t0
        if elapsed >= CAP_SECONDS:
            cap_hit = True
            skipped = list(instruments[i:])
            print(f"CAP-HIT: elapsed {elapsed:.1f} s >= cap {CAP_SECONDS} s "
                  f"before {ticker}; STOPPING with {len(skipped)} "
                  f"instruments skipped (no silent truncation)")
            break
        results.append(run_instrument(ticker, program_cumulative))

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

    # Correlation rollup: which instruments trip the >0.5 flag.
    corr_rollup = []
    for res in results:
        c = res["correlation"]
        corr_rollup.append({
            "instrument": res["ticker"],
            "mean_pos_corr_set3": c["mean_pairwise_position_corr"]["set3"],
            "mean_pos_corr_set5": c["mean_pairwise_position_corr"]["set5"],
            "flag_set3": c["flag_gt_0p5"]["set3"],
            "flag_set5": c["flag_gt_0p5"]["set5"]})
    flagged = [r["instrument"] for r in corr_rollup
               if r["flag_set3"] or r["flag_set5"]]

    # Trade-count rollup + median shrinkage / SE-inflation.
    trade_rollup = []
    degenerate_k3 = []
    for res in results:
        for set_name, blk in res["trade_counts"].items():
            trade_rollup.append({"instrument": res["ticker"], "set": set_name,
                                 **blk})
            if blk["degenerate_k3"]:
                degenerate_k3.append({"instrument": res["ticker"],
                                      "set": set_name, "trades_k3": blk["trades_k3"]})
    def _median(vals):
        v = sorted(x for x in vals if x is not None)
        return v[len(v) // 2] if v else None

    median_shrink_k2 = _median(r["shrink_k2"] for r in trade_rollup)
    median_shrink_k3 = _median(r["shrink_k3"] for r in trade_rollup)
    # Per-set medians: pooling the strict all-agree corner (SET-3/K=3, which
    # genuinely COLLAPSES trades) with the looser votes (which INFLATE trades)
    # masks the mechanism, so report each set separately.
    per_set_shrink = {}
    for s in ("set3", "set5"):
        rows_s = [r for r in trade_rollup if r["set"] == s]
        mk2 = _median(r["shrink_k2"] for r in rows_s)
        mk3 = _median(r["shrink_k3"] for r in rows_s)
        per_set_shrink[s] = {
            "median_shrink_k2": mk2, "median_shrink_k3": mk3,
            "se_inflation_median_k2": _se_inflation(mk2),
            "se_inflation_median_k3": _se_inflation(mk3)}

    # Write correlation + trade-count artifact files.
    for res in results:
        (SWEEP_DIR / f"correlations__{res['ticker']}.json").write_text(
            json.dumps(res["correlation"], indent=2, sort_keys=True) + "\n")
    (SWEEP_DIR / "trade_counts.json").write_text(
        json.dumps({"per_instrument": trade_rollup,
                    "median_shrink_k2": median_shrink_k2,
                    "median_shrink_k3": median_shrink_k3,
                    "se_inflation_median_k2": _se_inflation(median_shrink_k2),
                    "se_inflation_median_k3": _se_inflation(median_shrink_k3),
                    "per_set": per_set_shrink,
                    "degenerate_k3_lanes": degenerate_k3},
                   indent=2, sort_keys=True) + "\n")

    # Flat results CSV.
    with (SWEEP_DIR / "results.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["instrument", "set", "k", "lane_sharpe", "bench_sharpe",
                    "n_trades", "tstat", "min_tstat_K4", "min_tstat_K60",
                    "fixed_sharpe", "searched_sharpe", "selection_gap",
                    "mean_pos_corr", "gate", "reason_class", "verdict"])
        for r in lanes:
            w.writerow([r["instrument"], r["set"], r["k"], r["lane_sharpe"],
                        r["bench_sharpe"], r["n_trades"], r["tstat"],
                        r["min_tstat_K4"], r["min_tstat_K60"],
                        r["fixed_sharpe"], r["searched_sharpe"],
                        r["selection_gap"], r["mean_pos_corr"], r["gate"],
                        r["reason_class"], r["verdict"]])

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
        "order": ("live owner turn 2026-07-19 / ORDER 019; pre-registered "
                  "docs/research-round-9-plan.md"),
        "post_holdout_dev_only": True,
        "registered_configs": executed,
        "program_variants_tried": program_cumulative,
        "min_tstat_K4": promotion.min_tstat(4),
        "min_tstat_K60": promotion.min_tstat(sweeps.R9_K),
        "instruments_planned": len(instruments),
        "instruments_run": len(results),
        "lanes_run": len(lanes),
        "runtime_seconds": round(runtime, 3),
        "cap_seconds": CAP_SECONDS,
        "cap_hit": cap_hit,
        "instruments_skipped_on_cap": skipped,
        "verdict_counts": counts,
        "gate_counts": gate_counts,
        "keeps_demoted_by_gate": demoted,
        "reason_class_rollup": reason_rollup,
        "ungradeable_lanes": ungradeable,
        "correlation_rollup": corr_rollup,
        "instruments_tripping_corr_flag": flagged,
        "median_shrink_k2": median_shrink_k2,
        "median_shrink_k3": median_shrink_k3,
        "se_inflation_median_k2": _se_inflation(median_shrink_k2),
        "se_inflation_median_k3": _se_inflation(median_shrink_k3),
        "per_set_shrink": per_set_shrink,
        "degenerate_k3_lanes": degenerate_k3,
        "best_keep_lane": best_keep,
        "best_tstat_lane": best_any,
        "lanes": lanes,
    }
    (SWEEP_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts} · gate {gate_counts} · {demoted} KEEP "
          f"demoted by gate · UNGRADEABLE {ungradeable} · "
          f"corr-flagged {flagged} · median shrink k2={median_shrink_k2} "
          f"k3={median_shrink_k3} · runtime {runtime:.1f} s "
          f"(cap {CAP_SECONDS} s{' — CAP-HIT' if cap_hit else ' — not hit'})")
    if best_any:
        print(f"best t any lane: {best_any['instrument']} "
              f"{best_any['set']}/k{best_any['k']} t={best_any['tstat']:.3f} "
              f"(K4 bar {promotion.min_tstat(4):.3f}, K60 bar "
              f"{promotion.min_tstat(sweeps.R9_K):.3f})")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
