# trading-lab — founding plan

> **Status:** `plan` — founding brief, manager-seeded 2026-07-09

## Mission

An autonomous research lab that systematically discovers and validates trading strategies
across timeframes — daily and hourly first — on tech stocks and gold/silver. The lab runs
extensive parallel backtesting of known indicators, indicator combinations, and novel
data-derived indicators, producing an evidence ledger of every experiment and a ranked,
honestly-validated strategy report.

## Methodology — anti-overfitting is the core discipline

**This section is binding.** A backtest that flatters itself is worse than no backtest;
every rule here exists to keep results honest.

- **Walk-forward testing** — every strategy is evaluated walk-forward: parameters are fit
  on a training window, then scored on the *following* unseen window, rolling through
  history. No single-split in-sample result is ever reported as a finding.
- **Locked out-of-sample HOLDOUT** — the most recent **18 months** of data is a locked
  holdout period, untouched until final review (roadmap P5). Sessions must never peek:
  no fitting, no scoring, no "just checking" against it. First evaluation against the
  holdout happens once, at final review.
- **Realistic costs** — every backtest includes realistic transaction costs and slippage.
  A strategy that only survives at zero cost is not a strategy.
- **Multiple-testing discipline** — report the number of variants tried alongside any
  result; the more you try, the less any single winner means. Prefer deflated Sharpe
  ratios, and require survivors to also work on instruments they were not tuned on.
- **No lookahead bias** — indicators are computed strictly on past data. Nothing at bar
  *t* may use information from bar *t* onward (signals act at *t+1* or later).
- **Benchmark** — the benchmark for every result is buy-and-hold of the same instrument
  over the same period. A strategy that does not beat holding is a negative result —
  which still goes in the ledger.

## Data policy

Free daily + hourly data (yfinance or equivalent), cached and committed under `data/`
for reproducibility — mind repo size, use compact formats (parquet or csv.gz). Paid data
or minute-level data is an owner decision; flag it only if results justify the ask.

## Experiment ledger

The ledger is the product. One small result file per backtest run under `experiments/`,
containing: config hash, strategy family, instrument, timeframe, data range, and metrics
— Sharpe, Sortino, max drawdown, CAGR, win rate, turnover, and the variants-tried count
(multiple-testing discipline above) — plus an index file. One-file-per-run means parallel
sessions never conflict on the ledger.

## Parallel-session lanes

Sessions claim a lane before starting work. A lane = strategy-family × instrument-set ×
timeframe. One claim file per lane (like superbot's claims dir): create it when you start,
delete it when you finish, and check for existing claims before picking a lane.

## Roadmap

- **P0 — scaffold**: data layer (cached daily + hourly), backtest engine, 3 baseline
  strategies (buy-and-hold, SMA crossover, RSI mean-reversion), experiment ledger, CI
  quality gate — all unit-tested.
- **P1 — known-indicator sweep**: broad parallel backtesting of standard indicators and
  parameterizations across instruments and timeframes.
- **P2 — walk-forward validation** of P1 survivors.
- **P3 — novel / combined indicator generation**: combinations and data-derived
  indicators, under the same multiple-testing discipline.
- **P4 — cross-instrument robustness**: survivors must work on instruments they were
  not tuned on.
- **P5 — ranked final report**: first and only evaluation against the locked holdout;
  ranked, honestly-validated strategy report.

## Hard rails

- **RESEARCH ONLY.** This project never connects to brokers, never executes trades, never
  touches real money or credentials. Anything money-adjacent goes to ⚑ needs-owner.
- **Forward-only git** — no force pushes, no history rewrites; fixes go in new commits.
- **Decide-and-flag** — reversible research/design decisions are made by the session
  (recommendation + one-line rationale + a flag in status), not parked for the owner.
- **Live-data quirks** — splits, dividends, missing bars, and similar data surprises are
  documented when found, so later sessions inherit the fix rather than rediscovering it.

## Stack (manager defaults, veto-able)

Python 3.11+, pandas, and a standard backtesting library — **vectorbt** and
**backtesting.py** are the candidates; the final choice is the P0 session's
decide-and-flag. pytest for tests; pinned requirements.
