# 2026-07-13 — R3 slice 11: mean-reversion families × new tickers (dev-only)

> **Status:** `in-progress` — Round-3 slice 11 of the ORDER 012 night-run
> research lane: the five existing mean-reversion families
> (rsi_mean_reversion, bollinger_reversion, pullback, stochastic_reversion,
> williams_r_reversion) swept with pre-declared 12-variant sub-grids of
> their published axes over the six PR #83 instruments (SPY, QQQ, TSLA,
> JPM, XOM, TLT) on the standard dev rail. NO new strategy code. This slice
> lands AFTER the Round-3 synthesis (PR #89, slices 1-8) and extends the
> round; the synthesis doc is NOT rewritten.

📊 Model: fable-5 · r3-meanrev-new-tickers lane (worker session) · start 2026-07-13T03:23Z

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 3 (PR #83) added the six new instrument caches but probed
them with only small 6-variant grids of three families; slice 10 (PR #90)
completed the TREND-family coverage of that surface. This slice does the
same for the MEAN-REVERSION side: rsi_mean_reversion, bollinger_reversion,
pullback, stochastic_reversion and williams_r_reversion with 12
pre-declared variants each — every grid point a subset of the family's
existing published axes (P1 mean-reversion axes; the r3-stoch-willr axes),
no new parameter territory, no new strategy code. Overlap honesty note up
front: slice 3 already probed `rsi_mean_reversion` on these six
instruments with a 6-variant grid (period {2,5,14} × oversold {30} ×
overbought {60,70}); this slice's rsi sub-grid is deliberately DISJOINT
from that probe (oversold ∈ {10, 20}, never 30) so no config is registered
twice — the relation is pinned by a unit test, following slice 10's
donchian precedent. Backtests run on the default `load_ohlcv` dev rail
(holdout ≥ 2025-01-09 excluded; the holdout is SPENT). Promotion is CLOSED
post-holdout: mostly-KILL is the expected outcome and is recorded as a
first-class result.

## Work log

- 2026-07-13T03:23Z — clone hard-synced to origin/main HEAD `6cc5938`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 11, mean-reversion families × new tickers). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-meanrev-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-meanrev-new-tickers.md` are the born-red
  FIRST commit, pushed before any build work.

## Previous-session review

[to be written at close-out]

## Close-out

[to be written at close-out]
