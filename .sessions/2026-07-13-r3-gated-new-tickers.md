# 2026-07-13 — R3 slice 12: R2/gated families × new tickers (dev-only)

> **Status:** `in-progress` — Round-3 slice 12 of the ORDER 012 night-run
> research lane: the three existing R2/gated families (keltner_breakout,
> vol_filtered_trend, macd_supertrend) swept with pre-declared sub-grids of
> their published axes over the six PR #83 instruments (SPY, QQQ, TSLA,
> JPM, XOM, TLT) on the standard dev rail. NO new strategy code. This slice
> lands AFTER the Round-3 synthesis (PR #89, slices 1-8) and extends the
> round; the synthesis doc is NOT rewritten.

📊 Model: fable-5 · r3-gated-new-tickers lane (worker session) · start 2026-07-13T03:36Z

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 3 (PR #83) added the six new instrument caches; slice 10
(PR #90) completed the TREND-family coverage of that surface and slice 11
(PR #91) the MEAN-REVERSION coverage. This slice completes the remaining
single-instrument coverage with the three R2/gated families — all of them
previously NARROW-UNIVERSE, stated honestly up front:
`vol_filtered_trend` has only ever run on the Round-2 §3a four (AAPL,
MSFT, NVDA, GLD); `keltner_breakout` only on the Round-2 §3b four
(BTC-USD, META, AMZN, SLV); `macd_supertrend` only on BTC-USD (the P1
video lane) — this is its first run on equities/ETFs. Grids are
pre-declared subsets of each family's published axes (no new parameter
territory, no new strategy code): vol_filtered_trend reuses its full
12-variant R2 grid VERBATIM including the `vol_filter=False` control arm
(slice-2 card convention: gated grids commit their neutral arm);
keltner_breakout reuses its full R2 grid VERBATIM — that grid is only 6
variants, and expanding it to ~12 would open new parameter territory, so
the honest choice is 6, not 12; macd_supertrend takes a 12-variant
sub-grid of the 36-variant P1 video grid with the MACD triple frozen at
the classic 12/26/9 (slice 10's supertrend_flip precedent). Backtests run
on the default `load_ohlcv` dev rail (holdout ≥ 2025-01-09 excluded; the
holdout is SPENT). Promotion is CLOSED post-holdout: mostly-KILL is the
expected outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T03:36Z — clone hard-synced to origin/main HEAD `39ab8aa`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 12, R2/gated families × new tickers). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-gated-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-gated-new-tickers.md` are the born-red
  FIRST commit, pushed before any build work.

## Previous-session review

[to be written at close-out]

## Close-out

[to be written at close-out]
