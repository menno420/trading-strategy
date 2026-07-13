# 2026-07-13 — R3 slice 3: new tickers (dev-only)

> **Status:** `in-progress`

📊 Model: fable-5 · r3-new-tickers lane (worker session) · start 2026-07-13T01:22Z

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-2 (PRs #81, #82) covered new strategies/indicators over
the existing 8-ticker universe; this slice covers NEW TICKERS: candidates
SPY, QQQ, TSLA, JPM, XOM, TLT (broad market, mega-cap growth outside the
universe, financials, energy, rates) to diversify the tech-heavy universe.
Fetch ONLY via the sanctioned `trading_lab.data.fetch_ohlcv` + `save_cache`
path (the same mechanism `scripts/fetch_data.py` uses); any fetch failure is
recorded verbatim as an honest "data unavailable" row — never fabricated,
never sourced elsewhere. Backtests run on the default `load_ohlcv` dev rail
(holdout ≥ 2025-01-09 excluded; the holdout is SPENT). `config.UNIVERSE`
stays frozen at 8 tickers — new instruments are declared lane-local in
`trading_lab.sweeps`. Promotion is CLOSED post-holdout: mostly-KILL is the
expected outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T01:22Z — clone hard-synced to origin/main HEAD `06e79ae`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (new tickers). Collision check: `control/claims/` at HEAD contains only
  `README.md` + `2026-07-13-order-night-run.md` — no overlap with this
  scope. Branch `claude/r3-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-new-tickers.md` are the born-red FIRST
  commit, pushed before any build work.
