# Lane claim — mean-reversion__all8__daily

- **lane:** mean-reversion × all8 × daily (QUEUE.md § Next item 2 — the
  standing default order after ORDER 005: QUEUE.md § Next, top to bottom;
  item 1 is done/absorbed)
- **session:** 2026-07-10-mean-reversion-daily
  (card: `.sessions/2026-07-10-mean-reversion-daily.md`)
- **started-at:** 2026-07-10T02:41:36Z
- **scope:** P1 known-indicator sweep of the mean-reversion family (RSI
  mean-reversion plus bounded sibling variants, e.g. Bollinger/z-score
  reversion — grids defined in `trading_lab.sweeps`, unit-tested counts) ×
  the full universe in `trading_lab.config.UNIVERSE` × daily bars,
  pre-holdout dev data only — walk-forward (train 1008 / test 252), costs on,
  variants counted, holdout untouched, benchmark buy-and-hold over the same
  stitched OOS window — per docs/founding-plan.md.
- **branch:** session/2026-07-10-mean-reversion-daily (heartbeat), lane work
  follows on session branches until the claim is deleted.

Delete this file in the PR that merges the lane's ledgered results
(claims/README.md lifecycle).
