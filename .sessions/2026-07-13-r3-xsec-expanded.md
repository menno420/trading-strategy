# 2026-07-13 — R3 slice 7: cross-sectional lane on the expanded 14-ticker universe (dev-only)

> **Status:** `in-progress` — born-red card, first commit of the session.
> Scope: the R2 cross-sectional momentum portfolio lane re-run on the
> EXPANDED 14-instrument daily equity/ETF universe (label `XSEC-14`), plus
> one NEW short-term cross-sectional reversal family (`xsec_reversal`),
> dev rail only. Promotion CLOSED; honest KILL/NULL verdicts are the
> expected first-class outcome.

📊 Model: fable-5 · r3-xsec-expanded lane (worker session) · start 2026-07-13T02:21Z

💡 **Session idea:** [to be written at close]

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-6 (PRs #81-#86) are merged. This slice expands the
lab's only PORTFOLIO-level lane (Round 2 R3, `xsec_momentum` over the
9-instrument XSEC-9 basket) onto the expanded 14-ticker daily equity/ETF
surface (the frozen 8-ticker universe minus BTC-USD, plus the six slice-3
instruments SPY/QQQ/TSLA/JPM/XOM/TLT), and adds the mirror thesis:
short-term cross-sectional REVERSAL (long the k worst performers over the
past N days, weekly rebalance) — same portfolio plumbing, long/flat only.

## Work log

- 2026-07-13T02:21Z — clone hard-synced to origin/main HEAD `554cc52`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 7, cross-sectional lane on the expanded universe). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-xsec-expanded`; this card + the claim
  `control/claims/2026-07-13-r3-xsec-expanded.md` are the born-red FIRST
  commit, pushed before any build work.

## Previous-session review

[to be written at close — reviewing .sessions/2026-07-13-r3-breakout.md]

## Close-out

[to be written at close]
