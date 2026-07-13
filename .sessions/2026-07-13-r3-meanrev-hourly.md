# 2026-07-13 — R3 slice 5: mean-reversion families × hourly bars (dev-only)

> **Status:** `in-progress`

📊 Model: fable-5 · r3-meanrev-hourly lane (worker session) · start 2026-07-13T01:50Z

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-4 (PRs #81, #82, #83, #84) expanded strategies,
indicators, and instruments — all on daily bars. This slice expands the
TIMEFRAME axis instead: NO new strategy code — the four existing
mean-reversion families (`rsi_mean_reversion`, `bollinger_reversion`,
`stochastic_reversion`, `williams_r_reversion`) are swept on HOURLY bars
over the frozen 8-ticker universe, mirroring the one prior hourly lane
(`p1-trend-hourly`: committed hourly caches only, dev bars 2023-08-10 →
2025-01-08, bar-denominated grids reused as-is — the same lookback numbers
mean hours-to-days instead of days-to-weeks — and the lab's 1008/252 BAR
walk-forward convention kept for cross-lane comparability). Promotion is
CLOSED post-holdout: mostly-KILL is the expected outcome and will be
recorded as a first-class result.

## Work log

- 2026-07-13T01:50Z — clone hard-synced to origin/main HEAD `b739f48`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 5, timeframe expansion). Collision check: `control/claims/` at
  HEAD contains only `README.md` + `2026-07-13-order-night-run.md` — no
  overlap with this scope. Branch `claude/r3-meanrev-hourly`; this card +
  the claim `control/claims/2026-07-13-r3-meanrev-hourly.md` are the
  born-red FIRST commit, pushed before any build work.
