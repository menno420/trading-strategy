#!/usr/bin/env python3
"""Round 10 — inverse-confluence EXIT vote (go-flat when cross-class ≥K-of-N
agree OUT) × 15 daily tickers.

POST-HOLDOUT, DEV-ONLY (live owner turn 2026-07-19 / ORDER 020; pre-registered
protocol ``docs/research-round-10-plan.md``, merged as PR #155 BEFORE any
Round-10 outcome existed). Promotion is CLOSED: nothing this script produces
can be an out-of-sample claim; KEEPs are dev-candidates only.

The owner's idea, verbatim: *"isn't it a good idea to find multiple strategies
and wait untill at least 2 or 3 give the same signals?"* Round 9 tested the
ENTRY framing (require ≥K agreement to ENTER). Round 10 tests the INVERTED
complement the coordinator authorized on the same live owner turn: a binary
cross-thesis-class ≥K-of-N EXIT vote
(``trading_lab.ensemble.exit_confluence_positions``) — hold long (1.0) by
DEFAULT and go FLAT (0.0) on a bar iff at least K of N DISTINCT-class members
are simultaneously FLAT (signalling OUT). This is a **risk-OFF de-risking
overlay on buy-and-hold**: in-market unless ≥K members want out. It is the
**De Morgan DUAL** of the R9 entry vote (SAME members, SAME grid, SAME
instruments; only the compositor differs), implemented as
``1 - confluence_positions([1 - m for m in members], k)``.

Members run at their FIXED ``DEFAULT_PARAMS`` (NO per-member re-search —
pre-registered §3): the only searched axis is (member-set, K). Two panels
(SET-3 trend/mean-rev/breakout; SET-5 adds drawdown STATE + volume), K ∈ {2, 3}
⇒ 4 exit-vote configs, over the committed 15-ticker daily surface = 15 × 4 =
**60** registered configs (``sweeps.r10_total_configs()`` = 60); program
cumulative **5,853 → 5,913**.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; holdout SPENT, never read). Costs: 5 bps slippage +
1 bp commission per side. Execution: signal at bar t fills at bar t+1 open.
The benchmark is **buy-and-hold** (the exit vote is an overlay ON the hold), so
each lane's edge is measured as its deviation from the hold.

For every (instrument × exit-vote config) lane this script produces:

1. **A full-dev-period backtest** of the exit-confluence positions (members
   fixed at default params, so the full-period run IS a fixed-config evaluation
   — no in-sample parameter selection lives inside a lane). Sharpe-delta t vs
   full-period buy-and-hold via ``promotion.grade_promotion`` (the SAME
   machinery every prior round uses), Bonferroni K = 4 (the exit-vote configs
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
3. **The pre-registered correlation check** (§6) per instrument, on the member
   EXIT-SIGNAL series (the members' FLAT-bars, the "out" votes): pairwise
   exit-signal correlation, pairwise signal-overlap Jaccard (bars-both-flat /
   bars-either-flat), member daily RETURN correlation; the mean pairwise
   exit-signal correlation and the >~0.5 disqualification flag. Because
   ``corr(1-x, 1-y) = corr(x, y)`` for 0/1 series, the exit-signal correlation
   EQUALS the R9 position correlation — the run confirms this identity
   numerically (max |exit_corr − pos_corr| reported per instrument), not to
   re-derive a different number.
4. **The pre-registered trade-count / power impact** (§7) per instrument: the
   count of EXITS fired (step-aside events) at K=2 vs K=3, the flat-bar count
   and flat fraction, the trade count vs buy-and-hold (B&H trades once), and
   the implied Sharpe-SE inflation (SE ∝ sqrt((1 + SR²/2) / N), N ~ the bars
   that DIFFER from the hold). A rarely-firing strict K=3 exit ≈ buy-and-hold
   (near-zero deviation ⇒ near-zero t, ungradeable AS an edge); a
   frequently-firing loose K=2 exit sheds market drift. Any (instrument, K)
   lane with ~0 exits is flagged degenerate / indistinguishable-from-B&H, never
   hidden.

The round's top exit-vote config per instrument is LEDGERED with
``variants_tried=4`` (gate replays are report-only rows in the lane JSON —
R4-B precedent).

Runtime cap (self-enforced): <= 900 s wall-clock. The cap is checked before
each instrument; a would-be overrun STOPS the slice and records CAP-HIT — no
silent truncation.

Usage: python3 scripts/run_r10_exit_confluence_sweep.py
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
from trading_lab.ensemble import exit_confluence_positions  # noqa: E402
from trading_lab.strategies import DEFAULT_PARAMS, STRATEGIES  # noqa: E402
from trading_lab.walkforward import generate_splits  # noqa: E402

SLICE = "r10-exit-confluence"
TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; contiguous non-overlapping test windows
CAP_SECONDS = 900  # self-enforced: <= 15 min wall-clock for the slice

# Program burden prior to this slice: 5,853 registered configs
# (docs/research-round-9-results.md closing tally, Round 9). Round 10 lands
# its 60 on top: 5,853 -> 5,913.
PROGRAM_PRIOR_CONFIGS = 5853

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SLICE

COSTS = {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
         "commission_bps": config.DEFAULT_COMMISSION_BPS}

# Pre-registered correlation-disqualification threshold (plan §6, verbatim):
# "if mean pairwise member position-correlation on an instrument exceeds ~0.5,
# any apparent vote edge is not diversified and must be reported as such."
# For R10 this is applied to the member EXIT-SIGNAL series (flat-bars); by the
# Pearson identity corr(1-x,1-y)=corr(x,y) it equals the R9 position corr.
CORR_FLAG = 0.5

# A lane with <= this many step-aside events is flagged degenerate /
# indistinguishable-from-buy-and-hold (plan §7).
DEGENERATE_EXITS = 5

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


def exit_confluence_strategy(ohlcv: pd.DataFrame, *, members, k) -> pd.Series:
    """The R10 lane compositor as a ``strategy(ohlcv, **params)`` callable so
    the selection-fair gate can replay it exactly like any family. Each member
    is generated at its FIXED default params over ``ohlcv`` (causal — the gate
    passes trailing history ``ohlcv.iloc[:test_end]``), then the binary
    ≥k-of-N EXIT vote is applied on the shared index (long by default, flat when
    ≥k members are flat)."""
    member_pos = [STRATEGIES[m](ohlcv, **DEFAULT_PARAMS[m]) for m in members]
    return exit_confluence_positions(member_pos, k)


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


def _mean_offdiag(corr: pd.DataFrame) -> float:
    cols = list(corr.columns)
    n = len(cols)
    vals = [corr.iloc[i, j] for i in range(n) for j in range(i + 1, n)
            if not pd.isna(corr.iloc[i, j])]
    return float(sum(vals) / len(vals)) if vals else float("nan")


def _exit_jaccard_matrix(exit_by_member: dict) -> dict:
    """Pairwise exit-signal overlap Jaccard = bars-both-flat / bars-either-flat
    (flat = the member's "out" vote, exit_signal == 1)."""
    members = list(exit_by_member)
    out = {}
    for a in members:
        row = {}
        ea = exit_by_member[a] > 0
        for b in members:
            eb = exit_by_member[b] > 0
            either = int((ea | eb).sum())
            both = int((ea & eb).sum())
            row[b] = (both / either) if either > 0 else None
        out[a] = row
    return out


def correlation_block(ohlcv: pd.DataFrame, set5_members) -> dict:
    """The full pre-registered §6 correlation/overlap report for one
    instrument, computed on the member EXIT-SIGNAL series (SET-5 superset;
    SET-3 is its 3×3 sub-block). Also confirms the Pearson identity
    corr(1-x,1-y)=corr(x,y): the exit-signal correlation must EQUAL the R9
    member position correlation, so max |exit_corr − pos_corr| ≈ 0."""
    pos = member_positions(ohlcv, set5_members)
    exit_sig = {m: (1.0 - p.astype(float)) for m, p in pos.items()}
    pos_df = pd.DataFrame(pos)
    exit_df = pd.DataFrame(exit_sig)
    rets = member_returns(ohlcv, pos)
    ret_df = pd.DataFrame(rets)

    pos_corr = pos_df.corr()
    exit_corr = exit_df.corr()
    ret_corr = ret_df.corr()
    jac = _exit_jaccard_matrix(exit_sig)

    # Confirm corr(1-x,1-y) = corr(x,y) numerically (correctness check on the
    # round): the largest off-diagonal deviation between the exit-signal and
    # position correlation matrices.
    identity_max_abs_diff = float(
        (exit_corr - pos_corr).abs().to_numpy().max())

    set3 = set5_members[:3]
    mean_exit_set5 = _mean_offdiag(exit_corr)
    mean_exit_set3 = _mean_offdiag(exit_corr.loc[set3, set3])
    mean_pos_set5 = _mean_offdiag(pos_corr)
    mean_pos_set3 = _mean_offdiag(pos_corr.loc[set3, set3])
    return {
        "members_set5": list(set5_members),
        "members_set3": list(set3),
        "exit_signal_correlation": {a: {b: _clean(float(exit_corr.loc[a, b]))
                                        for b in set5_members}
                                    for a in set5_members},
        "position_correlation": {a: {b: _clean(float(pos_corr.loc[a, b]))
                                     for b in set5_members}
                                 for a in set5_members},
        "return_correlation": {a: {b: _clean(float(ret_corr.loc[a, b]))
                                   for b in set5_members}
                               for a in set5_members},
        "exit_signal_overlap_jaccard": jac,
        "corr_identity_check": {
            "note": ("Pearson identity corr(1-x,1-y)=corr(x,y) for 0/1 series: "
                     "the member EXIT-signal (flat-bar) correlation must EQUAL "
                     "the R9 member POSITION (long-bar) correlation. A "
                     "correctness check on the round, not a re-derivation."),
            "max_abs_diff_exit_vs_position": identity_max_abs_diff,
            "identity_confirmed": bool(identity_max_abs_diff < 1e-9),
        },
        "mean_pairwise_exit_signal_corr": {
            "set3": _clean(mean_exit_set3),
            "set5": _clean(mean_exit_set5),
        },
        "mean_pairwise_position_corr": {
            "set3": _clean(mean_pos_set3),
            "set5": _clean(mean_pos_set5),
        },
        "flag_gt_0p5": {
            "set3": bool(mean_exit_set3 > CORR_FLAG),
            "set5": bool(mean_exit_set5 > CORR_FLAG),
            "threshold": CORR_FLAG,
            "rule": ("Confluence between correlated members is one signal "
                     "counted twice; if mean pairwise member "
                     "exit-signal-correlation on an instrument exceeds ~0.5, "
                     "any apparent vote edge is not diversified and must be "
                     "reported as such."),
        },
    }


def _exit_stats(positions: pd.Series) -> dict:
    """Step-aside statistics for one exit-vote lane: flat-bar count, flat
    fraction, and the number of EXIT events (transitions into flat — the "count
    of step-aside events" of plan §7)."""
    p = positions.astype(float)
    flat = (p < 0.5)
    flat_bars = int(flat.sum())
    n_bars = int(len(p))
    # Exit events = rising edges of the flat lane (held -> flat transitions).
    prev = p.shift(1).fillna(1.0)  # default long before the first bar
    exit_events = int(((prev >= 0.5) & (p < 0.5)).sum())
    return {
        "flat_bars": flat_bars,
        "n_bars": n_bars,
        "flat_fraction": (flat_bars / n_bars) if n_bars else None,
        "exit_events": exit_events,
    }


def _stitched_sharpe(ohlcv, members, k, windows) -> float:
    """Selection-free stitched OOS Sharpe of an exit-vote config over the
    committed test windows, computed with the SAME
    ``selection_gate.stitched_replay`` the gate uses internally (so the
    fidelity guard reproduces it bit-for-bit)."""
    rows = [{"test": [w[0], w[1]], "params": {"members": members, "k": k}}
            for w in windows]

    def strat(o, **params):
        return exit_confluence_strategy(o, **params)

    stitched, _ = selection_gate.stitched_replay(
        ohlcv, strat, rows, TIMEFRAME, costs=COSTS)
    return metrics.sharpe(stitched, TIMEFRAME)


def run_instrument(ticker: str, program_cumulative: int) -> dict:
    """Run all 4 exit-vote-config lanes on one instrument, plus the §6
    correlation block and §7 exit-count block. Returns per-lane result rows."""
    ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
    set5 = list(sweeps._R10_MEMBER_SET_5)
    vote_configs = sweeps.r10_vote_configs()

    bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME, **COSTS)
    bench_full_m = metrics.compute_all(bench_full)
    bench_sharpe = bench_full_m["sharpe"]
    bench_trades = int(len(bench_full.trades))

    # §6 correlation / overlap on the exit-signal series (superset panel;
    # SET-3 is a sub-block). Also confirms corr(1-x,1-y)=corr(x,y) vs R9.
    corr = correlation_block(ohlcv, set5)

    # §7 building block: full-dev-period member positions at fixed params.
    pos5 = member_positions(ohlcv, set5)

    # Walk-forward test windows (contiguous, 1008/252) for the gate.
    splits = generate_splits(len(ohlcv), TRAIN_SIZE, TEST_SIZE)
    windows = [[s.test_start, s.test_end] for s in splits]

    # Pre-compute each exit-vote config's selection-free stitched OOS Sharpe
    # over the windows, and pick the instrument's BEST-of-4 (the round's
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

    program_min_t = promotion.min_tstat(sweeps.R10_K)  # K=60 program bar

    lane_rows = []
    per_set_exit_stats = {"set3": {}, "set5": {}}
    lane_full_sharpe = {}
    for c in vote_configs:
        set_name, members, k = c["set"], c["members"], c["k"]

        # 1) Full-dev-period backtest of the exit-confluence positions.
        positions = exit_confluence_positions(
            [pos5[m] for m in members], k)
        res = run_backtest(ohlcv, positions, timeframe=TIMEFRAME, **COSTS)
        full_m = metrics.compute_all(res)
        lane_sharpe = full_m["sharpe"]
        n_trades = int(len(res.trades))
        estats = _exit_stats(positions)
        per_set_exit_stats[set_name][f"k{k}"] = {
            "n_trades": n_trades, **estats}
        lane_full_sharpe[(set_name, k)] = lane_sharpe

        # Round-2 KEEP/KILL rule; ties/ambiguity resolve KILL.
        keep = (lane_sharpe is not None and bench_sharpe is not None
                and lane_sharpe > bench_sharpe and lane_sharpe > 0)
        if lane_sharpe is not None and bench_sharpe is not None:
            grade = promotion.grade_promotion(
                strategy_sharpe=lane_sharpe, benchmark_sharpe=bench_sharpe,
                n_periods=full_m["n_bars"], timeframe=TIMEFRAME,
                variants_tried=len(vote_configs))
        else:  # degenerate (e.g. never-exiting lane) — honest KILL, no arithmetic
            grade = {"verdict": None, "tstat": None,
                     "min_tstat": promotion.min_tstat(len(vote_configs)),
                     "note": "not computable: lane or benchmark Sharpe is "
                             "NaN (degenerate / never-exiting confluence)"}
        verdict_pre_gate = promotion.classify_verdict(
            keep, grade.get("tstat"), grade.get("min_tstat"))

        # 2) Selection-fair gate. searched arm = instrument BEST-of-4 (armed
        #    for the fidelity guard); fixed arm = this lane's config.
        searched_per_split = [
            {"test": w, "params": {"members": best_cfg["members"],
                                   "k": best_cfg["k"]}} for w in windows]
        gate = selection_gate.run_selection_gate(
            ohlcv=ohlcv, strategy=exit_confluence_strategy,
            per_split=searched_per_split,
            top_variant={"members": members, "k": k},
            timeframe=TIMEFRAME, costs=COSTS,
            recorded_searched_sharpe=best_stitched)
        verdict = selection_gate.apply_gate(verdict_pre_gate, gate)

        mean_exit_corr = corr["mean_pairwise_exit_signal_corr"][set_name]
        degenerate = bool(estats["exit_events"] <= DEGENERATE_EXITS)
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
            "order": ("live owner turn 2026-07-19 / ORDER 020; "
                      "pre-registered docs/research-round-10-plan.md"),
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "costs": dict(COSTS),
            "execution": "signal at bar t fills at bar t+1 open",
            "benchmark": "buy-and-hold (exit vote is an overlay ON the hold)",
            "lane_variants_tried": len(vote_configs),
            "program_variants_tried": program_cumulative,
            "full_period_metrics": {k2: full_m[k2]
                                    for k2 in VARIANT_METRIC_KEYS
                                    if k2 in full_m} | {
                "n_bars": full_m["n_bars"]},
            "benchmark_full_period_metrics": bench_full_m,
            "exit_stats": {**estats, "n_trades": n_trades,
                           "benchmark_trades": bench_trades,
                           "degenerate_near_bh": degenerate},
            "member_correlation": {
                "mean_pairwise_exit_signal_corr": mean_exit_corr,
                "mean_pairwise_position_corr": (
                    corr["mean_pairwise_position_corr"][set_name]),
                "flag_gt_0p5": bool(mean_exit_corr is not None
                                    and mean_exit_corr > CORR_FLAG),
            },
            "selection_gate": {
                "note": ("standing gate [D-0002] (docs/selection-fair-gate.md) "
                         "on EVERY R10 lane; doubles as the R5-D fixed-config "
                         "row. searched arm = instrument BEST-of-4 exit-vote "
                         "config (plan §9 (member-set, K) search dimension); "
                         "fixed arm = this lane's config; selection_gap "
                         "informational, no registered threshold; gate replay "
                         "report-only (R4-B precedent), not ledgered"),
                "searched_config": {"set": best_cfg["set"], "k": best_cfg["k"]},
                **gate,
            },
            "verdict_pre_gate": verdict_pre_gate,
            "verdict": verdict,
            "promotion_grade": {
                "note": ("Lo-2002 Sharpe-delta t on the full-dev-period lane "
                         "Sharpe vs same-instrument buy-and-hold (the exit "
                         "overlay modifies a hold), Bonferroni K = 4 exit-vote "
                         "configs on this instrument — INFORMATIONAL ONLY, "
                         "promotion is CLOSED post-holdout"),
                "program_min_tstat_K60": program_min_t,
                **grade,
            },
        }
        out = SWEEP_DIR / f"{set_name}_k{k}__{ticker}.json"
        out.write_text(json.dumps(lane_record, indent=2, sort_keys=True) + "\n")
        print(f"{ticker} {set_name}/k{k}: full_sharpe={lane_sharpe} "
              f"bench={bench_sharpe} t={grade.get('tstat')} "
              f"exits={estats['exit_events']} flat_bars={estats['flat_bars']} "
              f"trades={n_trades} gate={gate['gate']} {verdict}")

        lane_rows.append({
            "instrument": ticker, "set": set_name, "k": k,
            "lane_sharpe": lane_sharpe, "bench_sharpe": bench_sharpe,
            "n_trades": n_trades, "bench_trades": bench_trades,
            "exit_events": estats["exit_events"],
            "flat_bars": estats["flat_bars"],
            "flat_fraction": estats["flat_fraction"],
            "degenerate_near_bh": degenerate,
            "tstat": grade.get("tstat"), "min_tstat_K4": grade.get("min_tstat"),
            "min_tstat_K60": program_min_t,
            "gate": gate["gate"], "gate_reason": gate["reason"],
            "reason_class": gate["reason_class"],
            "fixed_sharpe": gate["fixed_sharpe"],
            "searched_sharpe": gate["searched_sharpe"],
            "selection_gap": gate["selection_gap"],
            "mean_exit_corr": mean_exit_corr,
            "verdict_pre_gate": verdict_pre_gate, "verdict": verdict})

    # Ledger the instrument's BEST-of-4 (by full-period Sharpe) exit-vote
    # config, variants_tried=4 (plan: top exit-vote config LEDGERED with the
    # round's searched K per instrument).
    best_full_key = max(
        lane_full_sharpe,
        key=lambda kk: (lane_full_sharpe[kk]
                        if lane_full_sharpe[kk] is not None else float("-inf")))
    best_full_cfg = next(c for c in vote_configs
                         if (c["set"], c["k"]) == best_full_key)
    best_positions = exit_confluence_positions(
        [pos5[m] for m in best_full_cfg["members"]], best_full_cfg["k"])
    best_res = run_backtest(ohlcv, best_positions, timeframe=TIMEFRAME, **COSTS)
    ledger_rec = ledger.build_record(
        strategy=f"r10_exit_confluence_{best_full_cfg['set']}_k{best_full_cfg['k']}",
        params={"members": list(best_full_cfg["members"]),
                "k": best_full_cfg["k"],
                "vote": "exit_confluence_flat_when>=k-of-N"},
        instrument=ticker, timeframe=TIMEFRAME, ohlcv=ohlcv,
        result=best_res, benchmark=bench_full,
        variants_tried=len(vote_configs),
        notes=(f"Round 10 inverse-confluence EXIT vote (post-holdout DEV-ONLY, "
               f"promotion CLOSED — live owner turn 2026-07-19 / ORDER 020; "
               f"pre-registered docs/research-round-10-plan.md): instrument "
               f"top exit-vote config of {len(vote_configs)} tried "
               f"(post-hoc selection — the per-lane grades and the "
               f"selection-fair gate blocks live in "
               f"experiments/sweeps/{SLICE}/*__{ticker}.json)"))
    ledger.write_run(ledger_rec)

    # §7 exit-count / power impact for this instrument.
    trade_block = {}
    for set_name in ("set3", "set5"):
        k2 = per_set_exit_stats[set_name].get("k2", {})
        k3 = per_set_exit_stats[set_name].get("k3", {})
        block = {
            "benchmark_trades": bench_trades,
            "exits_k2": k2.get("exit_events"),
            "exits_k3": k3.get("exit_events"),
            "flat_bars_k2": k2.get("flat_bars"),
            "flat_bars_k3": k3.get("flat_bars"),
            "flat_fraction_k2": k2.get("flat_fraction"),
            "flat_fraction_k3": k3.get("flat_fraction"),
            "trades_k2": k2.get("n_trades"),
            "trades_k3": k3.get("n_trades"),
            "degenerate_k2": bool(k2.get("exit_events", 0) <= DEGENERATE_EXITS),
            "degenerate_k3": bool(k3.get("exit_events", 0) <= DEGENERATE_EXITS),
            "se_inflation_k2": _se_inflation_frac(k2.get("flat_fraction")),
            "se_inflation_k3": _se_inflation_frac(k3.get("flat_fraction")),
        }
        trade_block[set_name] = block
    return {"ticker": ticker, "lanes": lane_rows,
            "correlation": corr, "exit_counts": trade_block}


def _se_inflation_frac(flat_fraction: float) -> float:
    """Implied Sharpe-SE inflation of the exit overlay's deviation-from-hold.
    The exit lane differs from buy-and-hold only on the bars it steps aside, so
    the effective sample carrying the edge signal is ~ flat_fraction × N. With
    SE(SR) ∝ sqrt((1 + SR²/2)/N) and (1 + SR²/2) ≈ 1 for the small Sharpes here,
    the SE of the deviation inflates ≈ 1/sqrt(flat_fraction) vs a full-sample
    estimate. flat_fraction → 0 (strict exit ≈ hold) ⇒ SE → ∞ ⇒ ungradeable AS
    an edge."""
    if flat_fraction is None or flat_fraction <= 0:
        return None
    return 1.0 / math.sqrt(flat_fraction)


def main() -> None:
    t0 = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    instruments = list(sweeps.R10_INSTRUMENTS)
    executed = sweeps.r10_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + executed
    # Verify the pinned grid == the configs actually run. STOP on drift.
    planned = len(instruments) * len(sweeps.r10_vote_configs())
    assert executed == 60 and planned == 60, (
        f"grid drifted from the pinned Round-10 plan: r10_total_configs()="
        f"{executed}, instruments×votes={planned} (expected 60)")
    print(f"R10 exit-confluence: {len(instruments)} instruments × "
          f"{len(sweeps.r10_vote_configs())} exit-vote configs = {executed} "
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

    # Correlation rollup: which instruments trip the >0.5 flag (on exit
    # signals) + the corr(1-x,1-y)=corr(x,y) identity confirmation.
    corr_rollup = []
    identity_ok = True
    max_identity_diff = 0.0
    for res in results:
        c = res["correlation"]
        idc = c["corr_identity_check"]
        identity_ok = identity_ok and idc["identity_confirmed"]
        max_identity_diff = max(max_identity_diff,
                                idc["max_abs_diff_exit_vs_position"])
        corr_rollup.append({
            "instrument": res["ticker"],
            "mean_exit_corr_set3": c["mean_pairwise_exit_signal_corr"]["set3"],
            "mean_exit_corr_set5": c["mean_pairwise_exit_signal_corr"]["set5"],
            "mean_pos_corr_set3": c["mean_pairwise_position_corr"]["set3"],
            "mean_pos_corr_set5": c["mean_pairwise_position_corr"]["set5"],
            "identity_max_abs_diff": idc["max_abs_diff_exit_vs_position"],
            "flag_set3": c["flag_gt_0p5"]["set3"],
            "flag_set5": c["flag_gt_0p5"]["set5"]})
    flagged = [r["instrument"] for r in corr_rollup
               if r["flag_set3"] or r["flag_set5"]]

    # Exit-count rollup + degenerate ~0-exit lanes.
    exit_rollup = []
    degenerate_lanes = []
    for res in results:
        for set_name, blk in res["exit_counts"].items():
            exit_rollup.append({"instrument": res["ticker"], "set": set_name,
                                **blk})
            for kk in ("k2", "k3"):
                if blk[f"degenerate_{kk}"]:
                    degenerate_lanes.append({
                        "instrument": res["ticker"], "set": set_name, "k": kk,
                        "exits": blk[f"exits_{kk}"]})

    def _median(vals):
        v = sorted(x for x in vals if x is not None)
        return v[len(v) // 2] if v else None

    median_exits_k2 = _median(r["exits_k2"] for r in exit_rollup)
    median_exits_k3 = _median(r["exits_k3"] for r in exit_rollup)
    median_flat_frac_k2 = _median(r["flat_fraction_k2"] for r in exit_rollup)
    median_flat_frac_k3 = _median(r["flat_fraction_k3"] for r in exit_rollup)
    # Per-set medians (strict K=3 collapses exits; loose K=2 fires often).
    per_set_exits = {}
    for s in ("set3", "set5"):
        rows_s = [r for r in exit_rollup if r["set"] == s]
        me2 = _median(r["exits_k2"] for r in rows_s)
        me3 = _median(r["exits_k3"] for r in rows_s)
        mf2 = _median(r["flat_fraction_k2"] for r in rows_s)
        mf3 = _median(r["flat_fraction_k3"] for r in rows_s)
        per_set_exits[s] = {
            "median_exits_k2": me2, "median_exits_k3": me3,
            "median_flat_fraction_k2": mf2, "median_flat_fraction_k3": mf3,
            "se_inflation_median_k2": _se_inflation_frac(mf2),
            "se_inflation_median_k3": _se_inflation_frac(mf3)}

    # Write correlation + exit-count artifact files.
    for res in results:
        (SWEEP_DIR / f"correlations__{res['ticker']}.json").write_text(
            json.dumps(res["correlation"], indent=2, sort_keys=True) + "\n")
    (SWEEP_DIR / "exit_counts.json").write_text(
        json.dumps({"per_instrument": exit_rollup,
                    "median_exits_k2": median_exits_k2,
                    "median_exits_k3": median_exits_k3,
                    "median_flat_fraction_k2": median_flat_frac_k2,
                    "median_flat_fraction_k3": median_flat_frac_k3,
                    "se_inflation_median_k2": _se_inflation_frac(
                        median_flat_frac_k2),
                    "se_inflation_median_k3": _se_inflation_frac(
                        median_flat_frac_k3),
                    "per_set": per_set_exits,
                    "degenerate_lanes": degenerate_lanes},
                   indent=2, sort_keys=True) + "\n")

    # Flat results CSV.
    with (SWEEP_DIR / "results.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["instrument", "set", "k", "lane_sharpe", "bench_sharpe",
                    "n_trades", "bench_trades", "exit_events", "flat_bars",
                    "flat_fraction", "tstat", "min_tstat_K4", "min_tstat_K60",
                    "fixed_sharpe", "searched_sharpe", "selection_gap",
                    "mean_exit_corr", "gate", "reason_class", "degenerate",
                    "verdict"])
        for r in lanes:
            w.writerow([r["instrument"], r["set"], r["k"], r["lane_sharpe"],
                        r["bench_sharpe"], r["n_trades"], r["bench_trades"],
                        r["exit_events"], r["flat_bars"], r["flat_fraction"],
                        r["tstat"], r["min_tstat_K4"], r["min_tstat_K60"],
                        r["fixed_sharpe"], r["searched_sharpe"],
                        r["selection_gap"], r["mean_exit_corr"], r["gate"],
                        r["reason_class"], r["degenerate_near_bh"],
                        r["verdict"]])

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
        "order": ("live owner turn 2026-07-19 / ORDER 020; pre-registered "
                  "docs/research-round-10-plan.md"),
        "post_holdout_dev_only": True,
        "registered_configs": executed,
        "program_variants_tried": program_cumulative,
        "min_tstat_K4": promotion.min_tstat(4),
        "min_tstat_K60": promotion.min_tstat(sweeps.R10_K),
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
        "corr_identity_confirmed_all": identity_ok,
        "corr_identity_max_abs_diff": max_identity_diff,
        "median_exits_k2": median_exits_k2,
        "median_exits_k3": median_exits_k3,
        "median_flat_fraction_k2": median_flat_frac_k2,
        "median_flat_fraction_k3": median_flat_frac_k3,
        "se_inflation_median_k2": _se_inflation_frac(median_flat_frac_k2),
        "se_inflation_median_k3": _se_inflation_frac(median_flat_frac_k3),
        "per_set_exits": per_set_exits,
        "degenerate_lanes": degenerate_lanes,
        "best_keep_lane": best_keep,
        "best_tstat_lane": best_any,
        "lanes": lanes,
    }
    (SWEEP_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts} · gate {gate_counts} · {demoted} KEEP "
          f"demoted by gate · UNGRADEABLE {ungradeable} · "
          f"corr-flagged {flagged} · identity_confirmed={identity_ok} "
          f"(max diff {max_identity_diff:.2e}) · median exits "
          f"k2={median_exits_k2} k3={median_exits_k3} · degenerate lanes "
          f"{len(degenerate_lanes)} · runtime {runtime:.1f} s "
          f"(cap {CAP_SECONDS} s{' — CAP-HIT' if cap_hit else ' — not hit'})")
    if best_any:
        print(f"best t any lane: {best_any['instrument']} "
              f"{best_any['set']}/k{best_any['k']} t={best_any['tstat']:.3f} "
              f"(K4 bar {promotion.min_tstat(4):.3f}, K60 bar "
              f"{promotion.min_tstat(sweeps.R10_K):.3f})")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
