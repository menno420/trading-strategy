# P1 results — mean-reversion × all 8 tickers × daily

> **Status:** `reference` — second P1 known-indicator sweep
> (lane `mean-reversion__all8__daily`, 2026-07-10). Findings are
> walk-forward out-of-sample only, per the binding methodology in
> [founding-plan.md](founding-plan.md). Raw evidence:
> `experiments/sweeps/p1-mean-reversion-daily/` + `experiments/index.jsonl`.

## Method

- **Strategies (3):** RSI-threshold reversion (the P0 baseline
  `rsi_mean_reversion`, reused with a sweep grid), Bollinger/z-score band
  reversion (`bollinger_reversion`), short-horizon pullback dip-buying with
  and without a long-term trend filter (`pullback`) — all long/flat,
  implemented in `src/trading_lab/strategies/`, causality unit-tested
  (prefix invariance).
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
| rsi_mean_reversion | period ∈ {2,3,5,14} × oversold ∈ {10,20,25,30} × overbought ∈ {50,60,70}, oversold<overbought | 48 |
| bollinger_reversion | lookback ∈ {10,15,20,30} × z_entry ∈ {1.0,1.5,2.0,2.5} × z_exit ∈ {0.0,0.5,1.0} | 48 |
| pullback | entry_lookback ∈ {3,5,7,10} × exit_len ∈ {3,5,7,10} × trend_len ∈ {0,100,200} (0 = no trend filter) | 48 |

**Lane total: 144 configurations**, each backtested on all 8 tickers
(1,152 full-period backtests recorded as per-variant rows in the sweep
files), plus walk-forward re-selection (48 grid points × 10 splits = 480
train evaluations per family × ticker; META 384). Any single "winner" below
must be discounted against this burden; the per-variant rows are the raw
material for deflated-Sharpe analysis in P2.

## Headline table — walk-forward OOS Sharpe (net of costs) vs buy-and-hold

`*` = beat buy-and-hold Sharpe over the same OOS period.

| ticker | B&H | RSI | Bollinger | Pullback | best | worst |
|---|---|---|---|---|---|---|
| AAPL | 0.96 | 0.73 | 0.51 | 0.62 | rsi | bollinger |
| MSFT | 1.10 | 0.91 | 0.82 | 1.02 | pullback | bollinger |
| NVDA | 1.30 | 0.68 | 0.34 | 0.93 | pullback | bollinger |
| GOOGL | 0.72 | 0.54 | 0.49 | **0.85*** | pullback | bollinger |
| AMZN | 0.76 | 0.36 | 0.18 | 0.42 | pullback | bollinger |
| META | 0.65 | **0.79*** | 0.62 | 0.67* | rsi | bollinger |
| GLD | 0.40 | 0.22 | 0.14 | −0.15 | rsi | pullback |
| SLV | 0.17 | 0.07 | 0.07 | −0.13 | bollinger | pullback |

OOS CAGR / max-drawdown detail is in the sweep files; the two survivors'
rows:

| ticker | B&H CAGR / MDD | survivor CAGR / MDD |
|---|---|---|
| GOOGL | +17.5% / −43.5% | pullback +12.3% / −22.3% |
| META | +19.3% / −76.4% | rsi +14.0% / −35.0% |

## Honest read

- **3 of 24 family × ticker lanes beat buy-and-hold on OOS Sharpe** — with
  **144 configurations tried** (plus per-split re-selection, 480 train
  evaluations per family × ticker) a ~13% hit rate with thin margins is
  weak evidence, not a discovery. Nothing here clears a
  multiple-testing-adjusted bar on its own.
- **The negative result is the headline:** long/flat mean-reversion on
  daily bars mostly *lags* buy-and-hold after realistic costs — 21 of 24
  lanes lose, and the whole Bollinger sub-family goes 0 for 8. A long/flat
  reverter is out of the market most of the time, so it misses the decade's
  up-drift; the Sharpe it salvages from dip-buying does not make up for the
  foregone exposure, and 6 bps/side round trips (top variants churn ~20–45
  position changes/year) sand off the rest. The trend-lane cost lesson
  transfers: turnover is the tax, and mean-reversion pays it more often.
- **Metals are the family's worst case:** pullback is *negative outright*
  on GLD and SLV (−0.15, −0.13) — dips in the metals kept dipping. No
  mean-reversion sub-family earned its costs on either metal.
- **Where reversion earned something:** the same drawdown-reduction profile
  the trend lane found. GOOGL pullback (0.85 vs 0.72) with MDD −22% vs −44%;
  META rsi (0.79 vs 0.65) with MDD −35% vs −76% — again mostly by being flat
  through part of the 2022 collapse. META pullback (0.67 vs 0.65) is a
  rounding-margin third.
- **Every beat is a CANDIDATE, not a finding** (144 variants tried): GOOGL
  pullback, META rsi_mean_reversion, META pullback are carried forward as
  *candidates* pending P2 walk-forward validation outside their selection
  window (deflated Sharpe, untuned-instrument transfer). META pullback's
  0.02 Sharpe margin is unlikely to survive it.

## Reproduce

```
python3 scripts/run_p1_meanrev_sweep.py
```
