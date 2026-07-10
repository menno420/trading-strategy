# 2026-07-10 — P2 walk-forward validation of open candidates (QUEUE item 4)

> **Status:** `complete` — heartbeat phase landed (claim + card, READY PR,
> merge on green); P2 validation work continues via amendments to this card
> or a follow-up card (wind-down-card precedent).

📊 Model: withheld per session policy · p2-validation lane · start 2026-07-10T03:27:58Z

💡 **Session idea:** QUEUE.md § Next item 4 (the standing default after
ORDER 005): P2 walk-forward validation of the accumulated P1 candidates —
daily trend (AAPL-donchian, META-sma/ema/donchian), video BTC-USD daily
(supertrend_flip, macd_supertrend), mean-reversion daily (GOOGL-pullback,
META-rsi_mean_reversion, META-pullback), trend hourly (GOOGL-sma/ema/donchian,
AMZN-donchian, META-macd). Per founding-plan discipline: walk-forward only,
costs on (engine defaults 5+1 bps/side, t+1-open fills), holdout untouched
(HOLDOUT_START=2025-01-09, loader-enforced), variants-tried counted, deflated
Sharpe / untuned-instrument transfer as the P2 bar; candidates that fail stay
ledgered as negatives — a complete deliverable. First step: this heartbeat PR
(claim + card → READY PR → tests + substrate-gate → landed on green).

## Previous-session review

Gen-2 sessions completed QUEUE items 1–3: video-strategy lane (PR #15,
dual-EMA control negative-complete; supertrend_flip / macd_supertrend to P2),
mean-reversion × daily (PR #17, 3/24 lanes beat B&H with 144 variants;
GOOGL-pullback / META-rsi / META-pullback to P2 as candidates only), and
trend × hourly (PR #19, 5/32 lanes beat B&H over a single ~8.5-month OOS
regime; GOOGL-sma/ema/donchian, AMZN-donchian, META-macd to P2 as candidates
only). Gen-1 completed daily trend (PRs #6/#7; AAPL-donchian,
META-sma/ema/donchian to P2). Known walls inherited: born-red (`in-progress`)
cards cannot merge — badge is `complete` scoped to the landed heartbeat
phase; new docs need a Status badge + a link from a reachable doc;
READY-never-draft, merge on green; auto-merge arm can fail "unstable status"
(pending) and "already in clean status" (green) — REST squash on green is
the fallback; tag pushes / branch deletion are 403 for agents; use the data
loader for Yahoo (proxy workaround implemented in src/trading_lab/data.py).

## Work log

- 2026-07-10T03:27:58Z — heartbeat/skeleton: claimed the lane
  (`claims/p2-validation.md`), session card (this file), branch
  `p2-validation-20260710T032758Z`, READY PR, merge on green. Overlap check
  at claim time: `claims/` held only its README; zero open PRs on the repo.

## Close-out (heartbeat phase)

**Done:** heartbeat/skeleton — lane claim + this card, READY PR, tests +
substrate-gate on green. No analysis code run; no backtests in this phase.

**Next (guard recipe):** P2 validation phase lands as an amendment to this
card or a follow-up card on a NEW branch off updated main: for each candidate
above, regime-diverse re-validation outside the P1 selection window
(consumed windows are recorded in the P1 results docs and
`experiments/sweeps/*/<family>__<ticker>.json`), deflated-Sharpe accounting
against the recorded variants_tried, untuned-instrument transfer checks;
results doc `docs/p2-validation-results.md` (badged + linked from a
reachable doc), ledger runs per validated candidate, claim deleted + QUEUE
item 4 marked DONE in the lane PR. Holdout stays untouched.
