# P1 results — trend-following × all 8 tickers × daily

> **Status:** `reference` — first P1 known-indicator sweep
> (lane `trend-following__all8__daily`, 2026-07-09). Findings are
> walk-forward out-of-sample only, per the binding methodology in
> [founding-plan.md](founding-plan.md). Raw evidence:
> `experiments/sweeps/p1-trend-following-daily/` + `experiments/index.jsonl`.

## Method

- **Strategies (4):** SMA crossover, EMA crossover, MACD (line > signal),
  Donchian channel breakout — all long/flat, implemented in
  `src/trading_lab/strategies/`, causality unit-tested (prefix invariance).
- **Data:** daily bars, pre-holdout dev period only (2010-01-04 → 2025-01-08;
  META from its 2012-05-18 IPO). Holdout untouched.
- **Costs on:** 5 bps slippage + 1 bp commission per side, t+1-open fills
  (engine defaults).
- **Evaluation:** `trading_lab.walkforward.walk_forward` — train 1008 bars
  (~4y), test 252 bars (~1y), contiguous test windows; per split the best
  in-train-Sharpe grid point is applied to the following unseen year. The
  stitched OOS series (2014-01-06 → 2024-01-09; META 2016-05-23 → 2024-05-24;
  10 splits, META 8) is the finding. The last partial year of the dev period
  is not covered by a full test window and is unused.
- **Benchmark:** buy-and-hold of the same ticker over the *exact same*
  stitched OOS period, same costs.

## Grids and multiple-testing burden

Grids live in `trading_lab.sweeps` (unit-tested counts):

| family | axes | variants |
|---|---|---|
| sma_crossover | fast ∈ {5,10,15,20,25,30,40,50} × slow ∈ {30,50,75,100,150,200}, fast<slow | 44 |
| ema_crossover | same axes as SMA | 44 |
| macd | fast ∈ {5,8,12,16} × slow ∈ {21,26,35,50} × signal ∈ {5,9,13}, fast<slow | 48 |
| donchian | entry ∈ {10,15,20,30,40,55,80,100} × exit ∈ {5,10,15,20,30,40,55}, exit≤entry | 41 |

**Lane total: 177 configurations**, each backtested on all 8 tickers
(1,416 full-period backtests recorded as per-variant rows in the sweep
files), plus walk-forward re-selection (grid × ~10 splits ≈ 410–480
train evaluations per family × ticker). Any single "winner" below must be
discounted against this burden; the per-variant rows are the raw material
for deflated-Sharpe analysis in P2.

## Headline table — walk-forward OOS Sharpe (net of costs) vs buy-and-hold

`*` = beat buy-and-hold Sharpe over the same OOS period.

| ticker | B&H | SMA | EMA | MACD | Donchian | best | worst |
|---|---|---|---|---|---|---|---|
| AAPL | 0.96 | 1.04* | 0.94 | 1.04* | **1.18*** | donchian | ema |
| MSFT | 1.10 | 0.92 | 0.90 | 0.24 | 0.38 | sma | macd |
| NVDA | 1.30 | 1.29 | 1.27 | 0.77 | 0.85 | sma | macd |
| GOOGL | 0.72 | 0.27 | 0.44 | −0.02 | 0.39 | ema | macd |
| AMZN | 0.76 | 0.37 | 0.53 | 0.24 | 0.64 | donchian | macd |
| META | 0.65 | **0.93*** | 0.83* | −0.04 | 0.80* | sma | macd |
| GLD | 0.40 | 0.20 | −0.01 | 0.31 | 0.13 | macd | ema |
| SLV | 0.17 | −0.15 | −0.24 | 0.22* | −0.21 | macd | ema |

OOS CAGR / max-drawdown detail is in the sweep files; two illustrative rows:

| ticker | B&H CAGR / MDD | best family CAGR / MDD |
|---|---|---|
| AAPL | +26.9% / −37.4% | donchian +21.5% / −21.3% |
| META | +19.3% / −76.4% | sma +25.9% / −36.9% |

## Honest read

- **7 of 32 family × ticker lanes beat buy-and-hold on OOS Sharpe.** With
  177 configurations tried and per-split re-selection, a ~22% hit rate with
  mostly small margins is weak evidence, not a discovery. Nothing here
  clears a multiple-testing-adjusted bar on its own.
- **The negative result is the headline:** on daily bars in a decade-long
  tech bull market, long/flat trend-following mostly *lags* buy-and-hold
  after realistic costs (MSFT, NVDA, GOOGL, AMZN, GLD: 0 of 20 lanes beat).
- **Where trend-following earned something:** META — all three MA/breakout
  families beat B&H by sidestepping part of the 2022 −76% drawdown (best
  MDD −33.7% vs −76.4%). AAPL donchian (1.18 vs 0.96) with MDD −21% vs −37%.
  The family's classic profile shows up as **drawdown reduction more than
  return enhancement** — potentially useful, but it must survive P2/P4
  robustness before it means anything.
- **MACD is the worst family** on 5 of 8 tickers — the fast signal line
  churns (turnover far above the crossovers), and costs eat it.
- **SLV MACD "beating" B&H (0.22 vs 0.17)** is a near-zero Sharpe on the
  weakest instrument — noise until proven otherwise.
- **Survivors for P2 walk-forward/deflated-Sharpe scrutiny:** AAPL donchian,
  META sma/ema/donchian — carried forward as *candidates*, not findings.

## Reproduce

```
python3 scripts/run_p1_trend_sweep.py
```
