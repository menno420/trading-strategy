# Lane claim — trend-following__all8__hourly

- **lane:** trend-following × all8 × hourly (QUEUE.md § Next item 3 — the
  standing default order after ORDER 005: QUEUE.md § Next, top to bottom;
  items 1 and 2 are done)
- **session:** 2026-07-10-trend-hourly
  (card: `.sessions/2026-07-10-trend-hourly.md`)
- **started-at:** 2026-07-10T03:06:29Z
- **scope:** P1 known-indicator sweep of the trend-following family
  (SMA/EMA crossover, MACD, Donchian — grids in `trading_lab.sweeps`,
  unit-tested counts; hourly-appropriate window sizes are this lane's
  decide-and-flag) × the full universe in `trading_lab.config.UNIVERSE` ×
  hourly bars, pre-holdout dev data only (committed hourly cache:
  2023-08-10 → 2025-01-08, ~2476 bars/ticker) — walk-forward, costs on
  (5+1 bps per side, t+1-open fills), variants counted, holdout untouched,
  benchmark buy-and-hold over the same stitched OOS window — per
  docs/founding-plan.md. Mind the cost-churn lesson at 1638 bars/year.
- **branch:** session/2026-07-10-trend-hourly (heartbeat), lane work
  follows on session branches until the claim is deleted.

Delete this file in the PR that merges the lane's ledgered results
(claims/README.md lifecycle).
