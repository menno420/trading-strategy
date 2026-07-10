# P4 cross-instrument transfer validation — all 13 subjects

> **Status:** `reference` — P4 transfer verdicts for the 13 P2 subjects
> (lane `p4-transfer`, 2026-07-10, QUEUE item 7). Parameters frozen from
> P1; zero re-tuning; holdout untouched, per the binding methodology in
> [founding-plan.md](founding-plan.md). Raw evidence: `experiments/runs/`
> (99 new rows), `experiments/index.jsonl`,
> `experiments/sweeps/p4-transfer/` (per-subject JSON),
> `scripts/run_p4_transfer.py`.

## Purpose

The founding plan defines P4 in one line only ("cross-instrument
transfer"); the operational semantics below are **defined by this P4
lane** and were pre-registered in the script docstring before any run was
executed. Motivation: 12 of the 13 subjects are UNVALIDATABLE-PRE-HOLDOUT
(P1 consumed every pre-holdout bar in their home instrument×timeframe —
see [p2-validation-results.md](p2-validation-results.md)), so
cross-instrument transfer is the last falsification lever that does not
touch the sealed holdout. The 13th subject, AAPL-donchian
(PROMOTED-TO-FINDING at P2; re-graded 2026-07-10 to RULE-PASS / candidate
under the ORDER 007 significance bar —
[p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md)), is included
because the plan requires survivors to transfer too.

**No verdict in this document is a finding, and no verdict here promotes
a candidate to finding.** A transfer verdict only sharpens the prior for
the P5 test; the holdout (bars ≥ 2025-01-09) stays sealed until P5.

## Methodology

- **Subjects:** the 13 P2 subjects (12 UNVALIDATABLE-PRE-HOLDOUT + the
  then-promoted, since-demoted AAPL-donchian; GOOGL-pullback was KILLED
  at P2 and is excluded).
- **Frozen parameters:** pulled verbatim from each subject's
  `top_full_period_variant` in
  `experiments/sweeps/<sweep>/<family>__<ticker>.json` at run time and
  cross-checked against the pre-registered list — all 13 matched
  (`params_match_preregistered_list: true` in every summary JSON). Zero
  re-tuning, zero new variants.
- **Transfer instruments:** every OTHER instrument with a committed cache
  in the subject's timeframe. Daily: the other 8 of
  {AAPL, MSFT, NVDA, GOOGL, AMZN, META, GLD, SLV, BTC-USD}. Hourly: the
  other 7 UNIVERSE tickers (no BTC-USD hourly cache exists).
- **Data ranges:** full pre-holdout series per transfer instrument via
  `trading_lab.data.load_ohlcv` (holdout rail: `unlock_holdout` never
  passed; every ledger row's `data_end` ≤ 2025-01-08). Daily equities/ETFs
  2010-01-04 → 2025-01-08 (3,779 bars; META from its 2012-05-18 IPO,
  3,180 bars; BTC-USD from 2014-09-17, 3,767 bars). Hourly 2023-08-10 →
  2025-01-08 (~2,476 bars).
- **Costs/execution:** engine defaults — 5 bps slippage + 1 bps
  commission per side, t+1-open fills; benchmark = buy-and-hold on the
  same series.
- **Pre-registered verdict rule** (per subject, fixed in the script
  docstring before running): count transfer instruments where strategy
  Sharpe > B&H Sharpe. **TRANSFER-SUPPORTED** if ≥ 2/3 of that subject's
  transfer instruments; **TRANSFER-WEAK** if ≥ 1/3 and < 2/3;
  **TRANSFER-FAILED** if < 1/3.
- **Walk-forward degeneracy note:** the lane brief said "walk-forward",
  but walk-forward is degenerate for a single-variant grid — there is no
  per-split selection to do. Since the params are frozen and the transfer
  instrument never participated in the subject's selection, the entire
  pre-holdout period is out-of-selection; this full-period frozen-param
  protocol follows the P2 precedent. Recorded as a deliberate deviation.
- **Variants counted:** 13 subjects × their transfer instruments = 99
  backtests, **0 new variants** (`variants_tried = 1` in each of the 99
  ledger rows — each is the same frozen vector re-evaluated, not a new
  degree of freedom).

## Results — daily (8 transfer instruments per subject)

Cells are strategy Sharpe / B&H Sharpe; **bold** = strategy beats B&H.

| Subject (frozen params) | AAPL | MSFT | NVDA | GOOGL | AMZN | META | GLD | SLV | BTC-USD | Beats | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| donchian×AAPL (entry=15, exit=5) | — | 0.32/0.91 | 0.75/1.07 | −0.05/0.76 | 0.32/0.86 | 0.31/0.76 | 0.26/0.43 | 0.01/0.25 | **1.07/0.91** | 1/8 | **TRANSFER-FAILED** |
| sma_crossover×META (fast=15, slow=75) | 0.72/0.98 | 0.64/0.91 | 1.02/1.07 | 0.54/0.76 | 0.75/0.86 | — | **0.44/0.43** | 0.11/0.25 | **1.06/0.91** | 2/8 | **TRANSFER-FAILED** |
| ema_crossover×META (fast=25, slow=50) | 0.85/0.98 | 0.69/0.91 | 1.05/1.07 | 0.41/0.76 | 0.65/0.86 | — | 0.42/0.43 | −0.05/0.25 | **1.16/0.91** | 1/8 | **TRANSFER-FAILED** |
| donchian×META (entry=55, exit=55) | 0.77/0.98 | 0.74/0.91 | **1.14/1.07** | 0.48/0.76 | 0.41/0.86 | — | 0.22/0.43 | −0.11/0.25 | **1.17/0.91** | 2/8 | **TRANSFER-FAILED** |
| supertrend_flip×BTC-USD (st=14/2.0, ema=200, macd 12/26/9) | **1.06/0.98** | 0.58/0.91 | 0.95/1.07 | 0.48/0.76 | 0.44/0.86 | 0.43/0.76 | 0.17/0.43 | −0.04/0.25 | — | 1/8 | **TRANSFER-FAILED** |
| macd_supertrend×BTC-USD (st=14/2.0, ema=100, macd 12/26/9) | 0.74/0.98 | 0.08/0.91 | 0.87/1.07 | 0.32/0.76 | 0.56/0.86 | 0.16/0.76 | 0.04/0.43 | 0.10/0.25 | — | 0/8 | **TRANSFER-FAILED** |
| rsi_mean_reversion×META (period=2, oversold=10, overbought=50) | 0.82/0.98 | 0.72/0.91 | 0.63/1.07 | 0.59/0.76 | 0.72/0.86 | — | −0.16/0.43 | −0.15/0.25 | 0.28/0.91 | 0/8 | **TRANSFER-FAILED** |
| pullback×META (entry_lookback=7, exit_len=7, trend_len=100) | 0.48/0.98 | 0.61/0.91 | 0.37/1.07 | 0.59/0.76 | 0.53/0.86 | — | 0.16/0.43 | −0.50/0.25 | 0.40/0.91 | 0/8 | **TRANSFER-FAILED** |

## Results — hourly (7 transfer instruments per subject)

| Subject (frozen params) | AAPL | MSFT | NVDA | GOOGL | AMZN | META | GLD | SLV | Beats | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| sma_crossover×GOOGL (fast=10, slow=75) | 0.82/0.96 | **0.99/0.96** | 1.85/1.95 | — | 0.85/1.24 | 1.25/1.46 | 1.17/1.70 | 0.67/0.79 | 1/7 | **TRANSFER-FAILED** |
| ema_crossover×GOOGL (fast=20, slow=50) | 0.81/0.96 | **1.11/0.96** | 1.80/1.95 | — | 0.66/1.24 | 1.41/1.46 | 1.35/1.70 | 0.61/0.79 | 1/7 | **TRANSFER-FAILED** |
| donchian×GOOGL (entry=40, exit=40) | 0.59/0.96 | 0.60/0.96 | **2.12/1.95** | — | **1.48/1.24** | 1.38/1.46 | 1.03/1.70 | 0.72/0.79 | 2/7 | **TRANSFER-FAILED** |
| donchian×AMZN (entry=40, exit=40) | 0.59/0.96 | 0.60/0.96 | **2.12/1.95** | **1.13/1.05** | — | 1.38/1.46 | 1.03/1.70 | 0.72/0.79 | 2/7 | **TRANSFER-FAILED** |
| macd×META (fast=5, slow=26, signal=5) | −0.46/0.96 | −1.24/0.96 | 1.53/1.95 | 0.26/1.05 | −0.30/1.24 | — | −0.32/1.70 | 0.27/0.79 | 0/7 | **TRANSFER-FAILED** |

Note: donchian×GOOGL and donchian×AMZN share the frozen vector
(entry=40, exit=40), so their runs on common instruments are identical —
the two subjects are not independent evidence.

## Honest summary

**0 of 13 subjects transferred: 13/13 TRANSFER-FAILED.** Across all 99
subject×instrument backtests, the frozen params beat buy-and-hold on
Sharpe in only **13 of 99** (13%). No subject reached even the
TRANSFER-WEAK threshold (≥ 1/3): the best did 2/8 or 2/7. The scattered
wins cluster where a long-only trend filter mechanically helps — BTC-USD
daily (4 of the 6 daily-subject attempts on it beat a B&H that ate an
−83% class drawdown) and the NVDA/AMZN hourly momentum regime — i.e.
instrument-regime effects, not evidence that any subject's edge is
portable.

This is the expected shape if the P1/P2 candidates are largely selection
artifacts riding instrument-specific regimes. In particular, the one P2
survivor, **AAPL-donchian (entry=15, exit=5), failed transfer 1/8** — its
P2 promotion (Sharpe 0.62 vs 0.54 on 29 years of pre-consumption AAPL
data) now looks instrument-specific, which sharpens the prior against it
generalizing. Its P2 B&H beat stands as a data point (P2 tested the home
instrument; transfer failure does not retroactively falsify that result),
but the promotion label did not survive: on 2026-07-10 it was re-graded to
RULE-PASS / candidate under the ORDER 007 significance bar
([p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md)), and the P5
holdout read on it should weight both facts heavily. The negative result
is the deliverable.

**No verdict here is a finding.** The holdout (bars ≥ 2025-01-09) remains
sealed until P5; every one of the 99 ledger rows has
`data_end ≤ 2025-01-08` and no `holdout_unlocked` marker.

## Multiple-testing accounting

P4 added exactly **99 backtest runs, 1 variant each, zero re-tuning**
(see `variants_tried` in the ledger rows). Reproduce with
`python3 scripts/run_p4_transfer.py`.

## Evidence

- Ledger rows: 99 new files in `experiments/runs/` (notes prefixed
  `p4-transfer:`); `experiments/index.jsonl` regenerated.
- Per-subject machine-readable summaries:
  `experiments/sweeps/p4-transfer/<family>__<ticker>__<timeframe>.json`.
- Frozen-parameter sources: the P1 sweep JSONs named per subject in the
  summaries (`p1_sweep` field).
