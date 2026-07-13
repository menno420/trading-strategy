# 2026-07-13 — R3 stochastic + Williams %R mean-reversion sweep (dev-only)

> **Status:** `in-progress`

📊 Model: fable-5 · r3-stoch-willr lane (worker session) · start 2026-07-13T00:53Z

💡 **Session idea:** expand the backtest surface with two classic oscillator
reversion families the lab has never tested — a slow-stochastic %K reversion
and a Williams %R reversion — swept over the full 8-ticker daily universe on
the standard dev rail (data ends 2025-01-08, holdout SPENT and untouched,
costs on, walk-forward OOS only, honest KEEP/KILL verdicts + ORDER 007
promotion-bar arithmetic recorded per lane). Mandated by ORDER 012 (owner
night-run direct order, 2026-07-13): "TRADING RESEARCH: expand the backtest
surface — new strategies, new stocks/tickers, new indicators — every result
recorded honestly." Promotion is CLOSED post-holdout: expected outcome is
mostly KILL/NULL, and that is a first-class result.

## Why this session exists

ORDER 012 (control/inbox.md, owner direct order for the 2026-07-13 night run)
instructs this seat to expand the backtest surface with new strategies and
indicators, recording every result honestly. The stochastic oscillator and
Williams %R are the two most-cited classic oversold oscillators the strategy
library does not yet cover; both slot into the existing long/flat
mean-reversion conventions (signal at bar t, engine fills at bar t+1 open)
with modest, pre-declared grids (12 variants per family). RESEARCH-ONLY rail
holds throughout: dev data only (`load_ohlcv` default rail, data_end
2025-01-08), no holdout reads, no paper-lane files, no promotion claims.

## Work log

- 2026-07-13T00:53Z — clone hard-synced to origin/main HEAD `23b0005`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane.
  Collision check: `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` (inbox-append slice, already merged) — no
  overlap with this scope. Branch `claude/r3-stoch-willr`; this card is the
  born-red FIRST commit together with the claim
  `control/claims/2026-07-13-r3-stoch-willr.md`.

## Close-out

(to be written at session end; badge flips `complete` as the deliberate last
content change, claim file deleted in the same commit)
