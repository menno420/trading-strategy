# P2 validation — verdicts for all 14 open candidates

> **Status:** `reference` — P2 validation of the accumulated P1 candidates
> (lane `p2-validation`, 2026-07-10, QUEUE item 4). Parameters frozen from
> P1; zero re-tuning; holdout untouched, per the binding methodology in
> [founding-plan.md](founding-plan.md). Raw evidence:
> `experiments/runs/` (2 new rows), `experiments/index.jsonl`,
> `scripts/run_p2_validation.py`, `data/p2ext/daily/`.
> **Re-graded 2026-07-10 (ORDER 007):** the sole PROMOTED-TO-FINDING verdict
> below (AAPL-donchian) was issued under the original statistics-free rule
> and has been **DEMOTED to candidate (RULE-PASS)** under the promotion
> significance bar — full computation in
> [p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md). Historical
> numbers below are unchanged; verdict labels carry the re-grade note.

## Purpose

P2 per the founding-plan roadmap: take the candidates that survived the P1
walk-forward sweeps and re-validate them on data OUTSIDE their P1 selection
window, with parameters frozen, before anything may be called a finding.
Rules applied here:

- **Validation window:** must be outside the candidate's P1 selection window
  AND strictly before `HOLDOUT_START` (2025-01-09, loader-enforced; the
  holdout remains untouched — `unlock_holdout` was never passed).
- **P1 consumed its entire dev range.** The P1 lanes were walk-forward
  processes: every bar served as train or OOS data for the selection process
  that nominated the candidate, so the whole dev range counts as consumed.
- **Frozen parameters:** P1 recorded no single deployed vector (candidates
  were per-split re-selection processes). The one recorded "selected" vector
  per candidate is the **top full-dev-period variant** —
  `top_full_period_variant` in
  `experiments/sweeps/<sweep>/<family>__<ticker>.json`. That vector is
  frozen here, verbatim from the sweep JSON. Zero re-tuning, zero new
  variants: `variants_tried = 1` per P2 run.
- **Verdicts (as originally issued):** `PROMOTED-TO-FINDING` (frozen params
  beat buy-and-hold on the P2 window, net of costs, by Sharpe), `KILLED`
  (they don't), or `UNVALIDATABLE-PRE-HOLDOUT` (zero unconsumed pre-holdout
  bars exist — exact data math shown below; no rules were bent to
  manufacture a window). **Amended by ORDER 007:** promotion additionally
  requires clearing a significance bar (minimum t-stat on the Sharpe delta,
  Lo 2002 SE, Bonferroni-adjusted for variants tried —
  `trading_lab.promotion`); a positive-but-insignificant delta is
  `RULE-PASS` (candidate), never a finding.

## Headline: structural data exhaustion

**12 of 14 candidates are UNVALIDATABLE-PRE-HOLDOUT.** P1 consumed all
available pre-holdout data in each candidate's timeframe: META lanes start
at the 2012-05-18 IPO, BTC-USD at Yahoo's 2014-09-17 series inception, and
hourly lanes at 2023-08-10 (the earliest hourly bar obtainable from Yahoo,
verified 2026-07-10). Exact math per candidate:

| Candidate (family × ticker × tf) | Available pre-holdout | Consumed by P1 | Unconsumed |
|---|---|---|---|
| sma_crossover × META × daily | 2012-05-18 → 2025-01-08 (3,180 bars; IPO-bounded) | same | **0 bars** |
| ema_crossover × META × daily | 2012-05-18 → 2025-01-08 (3,180 bars) | same | **0 bars** |
| donchian × META × daily | 2012-05-18 → 2025-01-08 (3,180 bars) | same | **0 bars** |
| rsi_mean_reversion × META × daily | 2012-05-18 → 2025-01-08 (3,180 bars) | same | **0 bars** |
| pullback × META × daily | 2012-05-18 → 2025-01-08 (3,180 bars) | same | **0 bars** |
| supertrend_flip × BTC-USD × daily | 2014-09-17 → 2025-01-08 (3,767 bars; series inception — cache first row verified) | same | **0 bars** |
| macd_supertrend × BTC-USD × daily | 2014-09-17 → 2025-01-08 (3,767 bars) | same | **0 bars** |
| sma_crossover × GOOGL × hourly | 2023-08-10 13:30 → 2025-01-08 20:30 (2,476 bars; earliest obtainable) | same | **0 bars** |
| ema_crossover × GOOGL × hourly | 2023-08-10 13:30 → 2025-01-08 20:30 (2,476 bars) | same | **0 bars** |
| donchian × GOOGL × hourly | 2023-08-10 13:30 → 2025-01-08 20:30 (2,476 bars) | same | **0 bars** |
| donchian × AMZN × hourly | 2023-08-10 13:30 → 2025-01-08 20:30 (2,476 bars) | same | **0 bars** |
| macd × META × hourly | 2023-08-10 13:30 → 2025-01-08 20:30 (2,476 bars) | same | **0 bars** |

Consumed windows are as recorded in each sweep JSON's
`data_start`/`data_end`; availability boundaries were re-verified against
the committed cache files' first rows and the known-walls note in
`docs/succession/NEXT-BOOT.md` (Yahoo 1h history reaches back only to
2023-08-10).

The two exceptions: **AAPL-donchian** and **GOOGL-pullback** were consumed
from 2010-01-04 only because the committed daily cache starts there
(`config.DAILY_START = 2010-01-01`); earlier daily history exists (AAPL
since 1980, GOOGL since its 2004-08-19 IPO). Those two got real P2 runs on
pre-2010 data.

## P2 data: pre-2010 extension (`data/p2ext/daily/`)

- Fetched 2026-07-10 via the repo's own fetch path
  (`trading_lab.data.fetch_ohlcv`, yfinance source succeeded first try),
  auto-adjusted, saved with the standard cache schema under
  `data/p2ext/daily/{AAPL,GOOGL}.csv.gz` (fetch range start 1980-01-01 /
  2004-01-01, end 2012-01-01 exclusive). The committed `data/daily/` cache
  is untouched; loading goes through `load_ohlcv(..., data_dir=".../data/p2ext")`,
  so the holdout rail still applies (trivially — the files end in 2011).
- **Adjusted-price consistency check** on the 504 overlapping 2010–2011
  bars vs the committed cache: max relative close discrepancy
  **1.03e-06 (AAPL)** and **2.80e-07 (GOOGL)** — pure float noise, no
  dividend-adjustment drift between the fetches.

**Honesty note:** these P2 windows PRECEDE the P1 selection window. This
tests regime generalization (do the frozen params work in decades they were
never selected on?), NOT forward deployability. Forward validation for any
candidate can only happen at P5 on the locked holdout.

## P2 runs (frozen params, engine defaults: 5+1 bps/side, t+1-open fills)

| | donchian × AAPL (entry=15, exit=5) | pullback × GOOGL (entry_lookback=5, exit_len=7, trend_len=0) |
|---|---|---|
| P2 window | 1980-12-12 → 2009-12-31 (7,331 bars) | 2004-08-19 → 2009-12-31 (1,353 bars) |
| Strategy Sharpe | **0.619** | 0.256 |
| B&H Sharpe | 0.540 | **1.054** |
| Strategy CAGR | 14.2% | 3.4% |
| B&H CAGR | 15.6% | 40.2% |
| Strategy max DD | −63.9% | −43.9% |
| B&H max DD | −81.8% | −64.6% |
| Strategy total return | 46.7× | 19.6% |
| B&H total return | 66.4× | 513% |
| Strategy n_trades | 327 | 180 |
| B&H n_trades | 1 | 1 |
| **Verdict** | **PROMOTED-TO-FINDING** — *re-graded 2026-07-10 to* **RULE-PASS / candidate** *(t = 0.42 < 1.64; [re-grade entry](p2-regrade-aapl-donchian.md))* | **KILLED** |

- **AAPL-donchian:** lower CAGR than B&H but a much shallower drawdown
  (−64% vs −82%) → higher risk-adjusted return across 29 years of data it
  was never tuned on. Even so, a −64% drawdown and a Sharpe edge of +0.08
  over three decades is a modest result, not a system — and under the
  ORDER 007 significance bar that edge is only 0.42 standard errors
  ([re-grade](p2-regrade-aapl-donchian.md)): a candidate, not a finding.
- **GOOGL-pullback:** decisively killed — the frozen params captured 19.6%
  total return against a 513% B&H run-up in GOOGL's early high-growth
  regime. The P1 edge does not generalize backward.

## Verdicts — all 14 candidates

| # | Candidate | P1 sweep | Frozen params | Verdict |
|---|---|---|---|---|
| 1 | donchian × AAPL × daily | p1-trend-following-daily | entry=15, exit=5 | **RULE-PASS / candidate** (was PROMOTED-TO-FINDING; [demoted 2026-07-10](p2-regrade-aapl-donchian.md)) |
| 2 | sma_crossover × META × daily | p1-trend-following-daily | fast=15, slow=75 | UNVALIDATABLE-PRE-HOLDOUT |
| 3 | ema_crossover × META × daily | p1-trend-following-daily | fast=25, slow=50 | UNVALIDATABLE-PRE-HOLDOUT |
| 4 | donchian × META × daily | p1-trend-following-daily | entry=55, exit=55 | UNVALIDATABLE-PRE-HOLDOUT |
| 5 | supertrend_flip × BTC-USD × daily | p1-video-strategy-daily | st=14/2.0, ema=200, macd 12/26/9 | UNVALIDATABLE-PRE-HOLDOUT |
| 6 | macd_supertrend × BTC-USD × daily | p1-video-strategy-daily | st=14/2.0, ema=100, macd 12/26/9 | UNVALIDATABLE-PRE-HOLDOUT |
| 7 | pullback × GOOGL × daily | p1-mean-reversion-daily | entry_lookback=5, exit_len=7, trend_len=0 | **KILLED** |
| 8 | rsi_mean_reversion × META × daily | p1-mean-reversion-daily | period=2, oversold=10, overbought=50 | UNVALIDATABLE-PRE-HOLDOUT |
| 9 | pullback × META × daily | p1-mean-reversion-daily | entry_lookback=7, exit_len=7, trend_len=100 | UNVALIDATABLE-PRE-HOLDOUT |
| 10 | sma_crossover × GOOGL × hourly | p1-trend-hourly | fast=10, slow=75 | UNVALIDATABLE-PRE-HOLDOUT |
| 11 | ema_crossover × GOOGL × hourly | p1-trend-hourly | fast=20, slow=50 | UNVALIDATABLE-PRE-HOLDOUT |
| 12 | donchian × GOOGL × hourly | p1-trend-hourly | entry=40, exit=40 | UNVALIDATABLE-PRE-HOLDOUT |
| 13 | donchian × AMZN × hourly | p1-trend-hourly | entry=40, exit=40 | UNVALIDATABLE-PRE-HOLDOUT |
| 14 | macd × META × hourly | p1-trend-hourly | fast=5, slow=26, signal=5 (P1-flagged least trustworthy) | UNVALIDATABLE-PRE-HOLDOUT |

**Score: 1 promoted, 1 killed, 12 unvalidatable pre-holdout** — *since the
2026-07-10 re-grade: 0 promoted, 1 rule-pass candidate, 1 killed, 12
unvalidatable pre-holdout.*

Unvalidatable ≠ validated. Those 12 candidates remain candidates-only; the
only remaining data that could test them is the locked holdout, which stays
untouched until P5. Any P5 read on them must account for the full P1
`variants_tried` behind each.

## Multiple-testing accounting

P2 added exactly **2 backtest runs, 1 variant each, zero re-tuning** (see
`variants_tried` in the two ledger rows). Reproduce with
`python3 scripts/run_p2_validation.py`.

## Evidence

- Ledger rows: `experiments/runs/20260710T033624806389Z-1943c6697c7c.json`
  (AAPL), `experiments/runs/20260710T033624870221Z-33316ae1158e.json`
  (GOOGL); `experiments/index.jsonl` regenerated.
- Frozen-parameter sources:
  `experiments/sweeps/p1-trend-following-daily/donchian__AAPL.json`,
  `experiments/sweeps/p1-mean-reversion-daily/pullback__GOOGL.json`.
- The holdout (bars ≥ 2025-01-09) remains untouched; both P2 windows end
  in 2009.

Next: P4 cross-instrument transfer validation of these subjects —
[p4-transfer-results.md](p4-transfer-results.md).
