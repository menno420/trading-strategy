#!/usr/bin/env python3
"""PHASE 2 - MTF BOLLINGER GRID (DEV-ONLY, research-only, promotion-closed).

Frozen rule: go long (+1) on a lower-TF lower-band touch (z_L <= -k) ONLY when
the higher TF is in-range (|z_H| < k, causally aligned); exit to flat when
z_L >= 0 (mid-band target); otherwise flat. No shorting. Costs ON (engine
defaults 5 bps slippage + 1 bp commission per side). Causal t+1-open execution
via trading_lab.engine.run_backtest.

Pre-declared SMALL grid (FROZEN): k in {2, 2.5}; lookback in {20, 50}
(same lookback both TFs); TF pairs in {1h/4h, 2h/daily, daily/weekly}
= 2 x 2 x 3 = 12 configs. Each config run per applicable ticker; OOS pooled
across tickers per config.

RAILS: no holdout (load_ohlcv only), no network, no ledger writes. Everything
here is dev-only / illustrative. A positive net Sharpe delta is at most a
"RULE-PASS candidate (dev, promotion-closed)", never a finding.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab import mtf  # noqa: E402
from trading_lab.mtf import (  # noqa: E402
    align_higher_to_lower, boll_z, resample_ohlcv,
)

HOURLY_TICKERS = ["AAPL", "AMZN", "GLD", "GOOGL", "META", "MSFT", "NVDA", "SLV"]
DAILY_TICKERS = ["AAPL", "AMZN", "BTC-USD", "GLD", "GOOGL", "META", "MSFT",
                 "NVDA", "SLV"]

# (name, lower_kind, higher_kind, lower_tf_label, ppy_key, tickers)
PAIRS = [
    ("1h/4h", "native:hourly", "resample:hourly:4h", "hourly", HOURLY_TICKERS),
    ("2h/daily", "resample:hourly:2h", "native:daily", "2h", HOURLY_TICKERS),
    ("daily/weekly", "native:daily", "resample:daily:W", "daily", DAILY_TICKERS),
]
K_GRID = [2.0, 2.5]
LOOKBACK_GRID = [20, 50]

ALPHA = 0.05

# Denominator bookkeeping (headline).
PRIOR_PROGRAM_CONFIGS = 590
LANE_CONFIGS = len(K_GRID) * len(LOOKBACK_GRID) * len(PAIRS)  # 12
PRIOR_HOLDOUT_READS = 13


def _frame(kind: str, ticker: str) -> pd.DataFrame:
    tag, *rest = kind.split(":")
    if tag == "native":
        return load_ohlcv(ticker, rest[0])
    if tag == "resample":
        base, rule = rest
        return resample_ohlcv(load_ohlcv(ticker, base), rule)
    raise ValueError(kind)


def build_positions(lo: pd.DataFrame, z_h_aligned: pd.Series,
                    k: float, lookback: int) -> pd.Series:
    """Frozen MTF rule -> positions in {0,1}, causal."""
    z_l = boll_z(lo["close"], lookback, ddof=0)
    higher_in_range = z_h_aligned.abs() < k
    raw = pd.Series(np.nan, index=lo.index)
    raw[z_l >= 0.0] = 0.0                                  # mid-band exit
    raw[(z_l <= -k) & higher_in_range.fillna(False)] = 1.0  # gated entry
    pos = raw.ffill().fillna(0.0)
    pos[z_l.isna()] = 0.0                                  # warm-up flat
    pos[z_h_aligned.isna()] = 0.0                          # no higher info -> flat
    pos.name = "position"
    return pos


def sharpe_ppy(returns: pd.Series, ppy: float) -> float:
    sd = returns.std(ddof=1)
    if sd == 0 or math.isnan(sd):
        return float("nan")
    return float(returns.mean() / sd * math.sqrt(ppy))


def grade_ppy(strategy_sharpe: float, benchmark_sharpe: float,
              n_periods: int, ppy: float, variants_tried: int) -> dict:
    """ORDER 007 Lo(2002) grade with an explicit periods-per-year (handles the
    resampled 2h timeframe that trading_lab.metrics does not know)."""
    delta = strategy_sharpe - benchmark_sharpe
    sr_per = strategy_sharpe / math.sqrt(ppy)
    se = math.sqrt((1.0 + sr_per ** 2 / 2.0) / n_periods) * math.sqrt(ppy)
    t = delta / se if se else float("nan")
    thr = NormalDist().inv_cdf(1.0 - ALPHA / max(1, variants_tried))
    if delta <= 0:
        verdict = "KILLED"
    elif t >= thr:
        verdict = "RULE-PASS-candidate(dev,promotion-closed)"  # never PROMOTED
    else:
        verdict = "RULE-PASS-candidate-below-bar(dev,promotion-closed)"
    return {"sharpe_delta": delta, "sharpe_se": se, "tstat": t,
            "min_tstat": thr, "variants_tried": variants_tried,
            "verdict": verdict}


def per_trade_returns(held: pd.Series, returns: pd.Series) -> list[float]:
    """Net round-trip P&L per held episode (nonzero-position runs)."""
    episode = (held != held.shift()).cumsum()
    out = []
    for _, seg in returns.groupby(episode):
        if held.loc[seg.index[0]] == 0:
            continue
        out.append(float((1.0 + seg).prod() - 1.0))
    return out


def choose_train(n: int) -> int:
    if n >= 1008 + 252:
        return 1008
    if n >= 504 + 252:
        return 504
    return max(60, n // 2)


def run_config(k: float, lookback: int, pair) -> dict:
    name, lower_kind, higher_kind, ppy_key, tickers = pair
    ppy = mtf.periods_per_year(ppy_key)
    pooled_ret, pooled_bh, pooled_trades = [], [], []
    n_oos_total = 0
    per_ticker = {}
    train_used = None
    std_splits = None

    for tk in tickers:
        lo = _frame(lower_kind, tk)
        hi = _frame(higher_kind, tk)
        z_h = boll_z(hi["close"], lookback, ddof=0)
        z_h_al = align_higher_to_lower(z_h, lo.index)
        pos_full = build_positions(lo, z_h_al, k, lookback)

        n = len(lo)
        train = choose_train(n)
        train_used = train
        # standard-window feasibility (for honesty about "how thin").
        from trading_lab.walkforward import generate_splits
        std_splits = len(generate_splits(n, 1008, 252))

        oos_idx = lo.index[train:]
        if len(oos_idx) < 30:
            continue
        oos = lo.loc[oos_idx]
        res = run_backtest(oos, pos_full.loc[oos_idx],
                           timeframe="daily" if ppy_key == "daily" else "hourly")
        bh = buy_and_hold_result(
            oos, timeframe="daily" if ppy_key == "daily" else "hourly")
        pooled_ret.append(res.returns)
        pooled_bh.append(bh.returns)
        trs = per_trade_returns(res.held, res.returns)
        pooled_trades.extend(trs)
        n_oos_total += len(oos_idx)
        per_ticker[tk] = {
            "n_oos_bars": int(len(oos_idx)),
            "n_trades": len(trs),
            "strat_sharpe": sharpe_ppy(res.returns, ppy),
            "bh_sharpe": sharpe_ppy(bh.returns, ppy),
        }

    strat_all = pd.concat(pooled_ret) if pooled_ret else pd.Series(dtype=float)
    bh_all = pd.concat(pooled_bh) if pooled_bh else pd.Series(dtype=float)
    s_sharpe = sharpe_ppy(strat_all, ppy) if len(strat_all) else float("nan")
    b_sharpe = sharpe_ppy(bh_all, ppy) if len(bh_all) else float("nan")

    trades = np.array(pooled_trades, dtype=float)
    n_trades = len(trades)
    wins = trades[trades > 0]
    losses = trades[trades <= 0]
    expectancy = float(trades.mean()) if n_trades else None
    win_rate = float(len(wins) / n_trades) if n_trades else None
    tail = {
        "worst_trade": float(trades.min()) if n_trades else None,
        "best_trade": float(trades.max()) if n_trades else None,
        "median_win": float(np.median(wins)) if len(wins) else None,
        "median_loss": float(np.median(losses)) if len(losses) else None,
        "p05_trade": float(np.percentile(trades, 5)) if n_trades else None,
        "p95_trade": float(np.percentile(trades, 95)) if n_trades else None,
        "worst_over_median_win": (
            float(trades.min() / np.median(wins))
            if len(wins) and np.median(wins) != 0 else None),
    }

    grade = None
    if n_trades and not math.isnan(s_sharpe) and not math.isnan(b_sharpe) \
            and (s_sharpe - b_sharpe) > 0:
        grade = {
            "K1": grade_ppy(s_sharpe, b_sharpe, len(strat_all), ppy, 1),
            "K12": grade_ppy(s_sharpe, b_sharpe, len(strat_all), ppy,
                             LANE_CONFIGS),
            "K602": grade_ppy(s_sharpe, b_sharpe, len(strat_all), ppy,
                              PRIOR_PROGRAM_CONFIGS + LANE_CONFIGS),
        }

    return {
        "pair": name, "k": k, "lookback": lookback,
        "ppy": ppy, "train_size_used": train_used,
        "std_window_splits_feasible": std_splits,
        "n_tickers": len(per_ticker), "n_oos_bars_pooled": n_oos_total,
        "n_trades_pooled": n_trades,
        "net_expectancy_per_trade": expectancy,
        "win_rate": win_rate,
        "strat_oos_sharpe": s_sharpe, "bh_oos_sharpe": b_sharpe,
        "sharpe_delta": (s_sharpe - b_sharpe
                         if not math.isnan(s_sharpe) and not math.isnan(b_sharpe)
                         else None),
        "tail_loss_profile": tail,
        "order007": grade,
        "per_ticker": per_ticker,
    }


def main():
    configs = []
    for pair in PAIRS:
        for k in K_GRID:
            for lb in LOOKBACK_GRID:
                print(f"[config] pair={pair[0]} k={k} lookback={lb}")
                configs.append(run_config(k, lb, pair))

    results = {
        "meta": {
            "phase": "PHASE 2 grid (DEV-ONLY, promotion-closed)",
            "rule": ("long on lower-band touch z_L<=-k gated by higher-TF "
                     "in-range |z_H|<k; exit z_L>=0; long/flat; costs ON"),
            "costs": "5 bps slippage + 1 bp commission per side (engine defaults)",
            "grid": {"k": K_GRID, "lookback": LOOKBACK_GRID,
                     "pairs": [p[0] for p in PAIRS], "n_configs": LANE_CONFIGS},
            "aggregation": ("OOS pooled across tickers per config (per-bar "
                            "returns concatenated; trades pooled)"),
            "holdout": "excluded (load_ohlcv default, < 2025-01-09)",
        },
        "denominator": {
            "this_config": 1,
            "this_lane_configs": LANE_CONFIGS,
            "program_prior_configs": PRIOR_PROGRAM_CONFIGS,
            "program_cumulative_configs": PRIOR_PROGRAM_CONFIGS + LANE_CONFIGS,
            "prior_holdout_reads": PRIOR_HOLDOUT_READS,
            "conditioning_descriptive_passes": 4,
        },
        "configs": configs,
    }
    out = REPO / "scratchpad" / "mtf_grid_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))

    # human table
    print("\n" + "=" * 100)
    print("PHASE 2 GRID - HUMAN TABLE (dev-only, costs ON, promotion-closed)")
    print("=" * 100)
    hdr = (f"{'pair':>12} {'k':>4} {'lb':>3} {'trades':>7} {'exp/trade':>11} "
           f"{'win%':>6} {'sharpe':>8} {'bh_sh':>8} {'Δsh':>8} "
           f"{'worst':>8} {'medwin':>8} {'splits':>6}")
    print(hdr)
    print("-" * 100)
    for c in configs:
        t = c["tail_loss_profile"]
        exp = c["net_expectancy_per_trade"]
        wr = c["win_rate"]
        dsh = c["sharpe_delta"]
        exp_s = "" if exp is None else f"{exp:>11.5f}"
        wr_s = "" if wr is None else f"{wr*100:>5.1f}%"
        dsh_s = "" if dsh is None else f"{dsh:>8.3f}"
        worst_s = "" if t["worst_trade"] is None else f"{t['worst_trade']:>8.4f}"
        medwin_s = "" if t["median_win"] is None else f"{t['median_win']:>8.4f}"
        print(f"{c['pair']:>12} {c['k']:>4} {c['lookback']:>3} "
              f"{c['n_trades_pooled']:>7} {exp_s:>11} {wr_s:>6} "
              f"{c['strat_oos_sharpe']:>8.3f} {c['bh_oos_sharpe']:>8.3f} "
              f"{dsh_s:>8} {worst_s:>8} {medwin_s:>8} "
              f"{c['std_window_splits_feasible']:>6}")
    print("-" * 100)

    # ORDER 007 for any positive config
    print("\nORDER 007 (positive Δsharpe configs only):")
    any_pos = False
    for c in configs:
        if c["order007"]:
            any_pos = True
            g = c["order007"]
            print(f"  {c['pair']} k={c['k']} lb={c['lookback']}: "
                  f"Δsh={c['sharpe_delta']:.3f} "
                  f"K1 t={g['K1']['tstat']:.2f}/{g['K1']['min_tstat']:.2f} "
                  f"[{g['K1']['verdict']}]  "
                  f"K12 t={g['K12']['tstat']:.2f}/{g['K12']['min_tstat']:.2f} "
                  f"[{g['K12']['verdict']}]  "
                  f"K602 t={g['K602']['tstat']:.2f}/{g['K602']['min_tstat']:.2f} "
                  f"[{g['K602']['verdict']}]")
    if not any_pos:
        print("  NONE - no config beat buy-and-hold net of costs (all KILLED).")

    d = results["denominator"]
    print("\nDENOMINATOR:")
    print(f"  this lane: {d['this_lane_configs']} grid configs "
          f"(+ {d['conditioning_descriptive_passes']} descriptive TF-pair passes)")
    print(f"  program cumulative: {d['program_prior_configs']} prior + "
          f"{d['this_lane_configs']} = {d['program_cumulative_configs']} configs")
    print(f"  prior holdout reads: {d['prior_holdout_reads']} (separate burden)")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
