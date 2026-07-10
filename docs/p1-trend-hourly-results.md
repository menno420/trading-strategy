# P1 results — trend-following × all 8 tickers × hourly

> **Status:** `reference` — third P1 known-indicator sweep, first on hourly
> bars (lane `trend-following__all8__hourly`, 2026-07-10). Findings are
> walk-forward out-of-sample only, per the binding methodology in
> [founding-plan.md](founding-plan.md). Raw evidence:
> `experiments/sweeps/p1-trend-hourly/` + `experiments/index.jsonl`.

## Method

- **Strategies (4):** SMA crossover, EMA crossover, MACD (line > signal),
  Donchian channel breakout — all long/flat, implemented in
  `src/trading_lab/strategies/`, causality unit-tested (prefix invariance).
  Same grids as the daily trend lane; on hourly bars the same lookback
  *numbers* mean hours-to-weeks instead of weeks-to-months.
- **Data:** hourly bars from the committed cache (no network fetches),
  pre-holdout dev period only: 2023-08-10 → 2025-01-08, 2,476 bars per
  ticker (GLD 2,475). Holdout untouched (loader-enforced; the sweep script
  additionally asserts `data_end < HOLDOUT_START` per ticker).
- **Costs on:** 5 bps slippage + 1 bp commission per side, t+1-open fills
  (engine defaults). At 1,638 hourly bars/year this cost model bites harder
  than on daily bars — see the honest read.
- **Evaluation:** `trading_lab.walkforward.walk_forward` with the lab's
  1008/252/252 **bar** convention, kept deliberately for cross-lane
  comparability (decide-and-flag). On hourly bars that means ~7.4-month
  train windows and ~7.4-week test windows; on ~2,476 bars it yields
  5 splits and a stitched OOS of 1,260 bars ≈ 8.5 months
  (2024-03-07 → 2024-11-22). The last ~208 bars of the dev period are not
  covered by a full test window and are unused.
- **Benchmark:** buy-and-hold of the same ticker over the *exact same*
  stitched OOS period, same costs.

## Grids and multiple-testing burden

Grids live in `trading_lab.sweeps` (unit-tested counts) — identical to the
daily trend lane:

| family | axes | variants |
|---|---|---|
| sma_crossover | fast ∈ {5,10,15,20,25,30,40,50} × slow ∈ {30,50,75,100,150,200}, fast<slow | 44 |
| ema_crossover | same axes as SMA | 44 |
| macd | fast ∈ {5,8,12,16} × slow ∈ {21,26,35,50} × signal ∈ {5,9,13}, fast<slow | 48 |
| donchian | entry ∈ {10,15,20,30,40,55,80,100} × exit ∈ {5,10,15,20,30,40,55}, exit≤entry | 41 |

**Lane total: 177 configurations**, each backtested on all 8 tickers
(1,416 full-period backtests recorded as per-variant rows in the sweep
files), plus walk-forward re-selection (grid × 5 splits = 205–240 train
evaluations per family × ticker). Any single "winner" below must be
discounted against this burden; the per-variant rows are the raw material
for deflated-Sharpe analysis in P2.

## Headline table — walk-forward OOS Sharpe (net of costs) vs buy-and-hold

`*` = beat buy-and-hold Sharpe over the same OOS period
(2024-03-07 → 2024-11-22, 1,260 hourly bars ≈ 8.5 months — one regime).

| ticker | B&H | SMA | EMA | MACD | Donchian | best | worst |
|---|---|---|---|---|---|---|---|
| AAPL | 1.57 | 0.72 | 0.76 | −0.63 | −0.69 | ema | donchian |
| MSFT | 0.15 | −0.12 | −0.20 | −2.25 | −0.49 | sma | macd |
| NVDA | 1.39 | 1.01 | 1.13 | 0.14 | 0.76 | ema | macd |
| GOOGL | 1.01 | **1.25*** | 1.06* | −0.49 | 1.05* | sma | macd |
| AMZN | 0.61 | 0.05 | −0.46 | −0.08 | **0.91*** | donchian | ema |
| META | 0.49 | −0.34 | 0.11 | **1.40*** | −1.19 | macd | donchian |
| GLD | 2.06 | 0.50 | 0.73 | −0.17 | 1.24 | donchian | macd |
| SLV | 1.19 | 0.77 | 0.68 | −0.27 | 0.48 | sma | macd |

OOS CAGR / max-drawdown detail is in the sweep files; the beats' rows:

| ticker | B&H CAGR / MDD | family CAGR / MDD |
|---|---|---|
| GOOGL | +29.8% / −22.8% | sma +31.9% / −11.2% |
| AMZN | +14.6% / −22.1% | donchian +15.8% / −10.5% |
| META | +11.8% / −20.4% | macd +34.0% / −9.3% |

## Honest read

- **5 of 32 family × ticker lanes beat buy-and-hold on OOS Sharpe** — with
  **177 configurations tried** (plus per-split re-selection, 205–240 train
  evaluations per family × ticker), a ~16% hit rate concentrated in two
  tickers is weak evidence, not a discovery. Nothing here clears a
  multiple-testing-adjusted bar on its own.
- **The OOS window is one regime, and that caveat dominates everything.**
  The stitched OOS is a single ~8.5-month stretch (2024-03 → 2024-11) in
  which buy-and-hold itself was strong (GLD B&H Sharpe 2.06, AAPL 1.57).
  The daily trend lane's OOS spans a decade and multiple regimes; this
  lane's does not, and its ~7.4-month train windows fit to one regime too.
  Hourly conclusions here are provisional in a way the daily lane's are not.
- **The negative result is the headline:** long/flat trend-following on
  hourly bars mostly lags buy-and-hold after realistic costs — 27 of 32
  lanes lose, including all four families on AAPL, MSFT, NVDA, GLD and SLV.
  On the metals — the OOS window's best performers — the best trend lane
  (GLD donchian, 1.24) still trails B&H (2.06) badly: being flat in an
  uptrend is the family's tax, and at hourly speed it is charged hourly.
- **Costs bite hardest at this frequency, and MACD shows it:** MACD is the
  worst family on 5 of 8 tickers and negative outright on 6, with top
  variants churning ~80–210 position changes/year (vs ~20–40 for the
  crossovers) at 6 bps/side per change. The daily lane's cost-churn lesson
  transfers and amplifies at 1,638 bars/year.
- **Where trend earned something:** GOOGL — all three MA/breakout families
  beat B&H by thin margins (1.25/1.06/1.05 vs 1.01), again with the
  drawdown-reduction profile (sma MDD −11% vs −23%). AMZN donchian
  (0.91 vs 0.61, MDD −10.5% vs −22.1%) similar. META macd (1.40 vs 0.49) is
  the largest margin but the least trustworthy: it re-selected the *fastest*
  grid corner (5/26/5, ~210 changes/year), its per-split test Sharpes swing
  from +3.8 to −1.1, and it beats while MACD loses on 6 of 8 other tickers.
- **Survivors for P2 walk-forward/deflated-Sharpe scrutiny:** GOOGL
  sma/ema/donchian, AMZN donchian, META macd — carried forward as
  *candidates*, not findings (177 variants tried, single-regime OOS). The
  thin GOOGL margins and the unstable META macd lane are unlikely to
  survive regime-diverse validation; treat P2 as the test, not a formality.

## Reproduce

```
python3 scripts/run_p1_trend_hourly_sweep.py
```
