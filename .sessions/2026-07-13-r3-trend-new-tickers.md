# 2026-07-13 — R3 slice 10: full trend families × new tickers (dev-only)

> **Status:** `in-progress` — Round-3 slice 10 of the ORDER 012 night-run
> research lane: the four existing trend families (donchian, ema_crossover,
> macd, supertrend_flip) swept with pre-declared 12-variant sub-grids of
> their published axes over the six PR #83 instruments (SPY, QQQ, TSLA,
> JPM, XOM, TLT) on the standard dev rail. NO new strategy code. This slice
> lands AFTER the Round-3 synthesis (PR #89, slices 1-8) and extends the
> round; the synthesis doc is NOT rewritten.

📊 Model: fable-5 · r3-trend-new-tickers lane (worker session) · start 2026-07-13T03:11Z

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 3 (PR #83) added the six new instrument caches but probed
them with only small 6-variant grids of three families (donchian,
sma_crossover, rsi_mean_reversion). This slice completes the TREND-family
coverage of those instruments: donchian, ema_crossover, macd and
supertrend_flip with ~12 pre-declared variants each — every grid point a
subset of the family's existing published axes (P1 trend axes; the video
lane's supertrend grid), no new parameter territory, no new strategy code.
Honest note up front: `supertrend_flip` has only ever been run on BTC-USD
(the P1 video lane) — this is its first run on equities/ETFs, and that is
an instrument-transfer question, not a tuned-strategy claim. Backtests run
on the default `load_ohlcv` dev rail (holdout ≥ 2025-01-09 excluded; the
holdout is SPENT). Promotion is CLOSED post-holdout: mostly-KILL is the
expected outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T03:11Z — clone hard-synced to origin/main HEAD `374651a`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 10, trend families × new tickers). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-trend-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-trend-new-tickers.md` are the born-red
  FIRST commit, pushed before any build work.

## Previous-session review

[to be written at close-out]

## Close-out

[to be written at close-out]
