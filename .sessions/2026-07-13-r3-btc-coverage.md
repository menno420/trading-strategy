# 2026-07-13 — R3 slice 13: Round-3 families × BTC-USD coverage (dev-only)

> **Status:** `in-progress` — born red by design; flips `complete` as the
> deliberate last content change of the session.

📊 Model: fable-5 · r3-btc-coverage lane (worker session) · start 2026-07-13T03:51Z

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." The BTC-USD daily cache (committed since the P1 video lane;
dev rail ends 2025-01-08) has only ever been swept by the video-strategy
lane families (supertrend_flip, macd_supertrend, the dual-EMA control)
plus the R2 §3b keltner_breakout arm and the P4 transfer spot checks —
the TEN single-instrument families Round 3 added (stochastic_reversion,
williams_r_reversion, roc_momentum, adx_filtered_sma, aroon_trend,
cci_reversion, bollinger_breakout, atr_trailing, trix_momentum,
ichimoku_trend) have NEVER run on BTC-USD. This slice completes that
coverage: each family's declared Round-3 12-variant grid reused VERBATIM
(no new strategy code, no new parameter territory), dev rail asserted,
promotion CLOSED post-holdout — mostly-KILL is the expected outcome and
is recorded as a first-class result.

## Work log

- 2026-07-13T03:51Z — clone hard-synced to origin/main HEAD `2a1fa22`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order).
  Collision check: `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-btc-coverage`; this card + the claim
  `control/claims/2026-07-13-r3-btc-coverage.md` are the born-red FIRST
  commit, pushed before any build work.

## Close-out

(pending — filled at session close)
