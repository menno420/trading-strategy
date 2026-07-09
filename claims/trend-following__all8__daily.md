# Lane claim: trend-following × all8 × daily

- **session:** claude/p1-trend-following-daily (P1 phase 1 worker,
  session card `.sessions/2026-07-09-p1-trend-following-daily.md`)
- **started-at:** 2026-07-09T17:15:00Z
- **scope:** trend-following family — sma_crossover, ema_crossover, macd,
  donchian (grids in `trading_lab.sweeps`, 177 variants total) × all 8
  universe tickers (AAPL MSFT NVDA GOOGL AMZN META GLD SLV) × daily bars,
  pre-holdout dev data, walk-forward evaluation, realistic costs.
- **deliverables:** strategies + tests, `experiments/sweeps/p1-trend-following-daily/`,
  ledger runs + regenerated index, `docs/p1-trend-following-results.md`.
