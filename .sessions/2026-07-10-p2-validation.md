# 2026-07-10 — P2 walk-forward validation of open candidates (QUEUE item 4)

> **Status:** `complete` — full session closed: heartbeat (claim + card,
> PR #20), P2 validation of all 14 candidates (PR #21, merged 19f9a5c), and
> this wrap-up (status overwrite + claim released). Lane closed.

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
- 2026-07-10T03:40Z — P2 validation phase (branch `p2-validation-results`):
  verdicts for all 14 open candidates, params frozen from the P1 sweep
  JSONs' `top_full_period_variant` (variants_tried=1 per run, zero
  re-tuning). 12/14 UNVALIDATABLE-PRE-HOLDOUT (P1 consumed every
  pre-holdout bar in their timeframes — structural data exhaustion; math in
  the doc). Fetched pre-2010 daily history for AAPL/GOOGL into
  `data/p2ext/daily/` (max close discrepancy vs committed cache ~1e-6);
  real P2 runs: AAPL-donchian PROMOTED-TO-FINDING (Sharpe 0.62 vs B&H 0.54,
  1980→2009), GOOGL-pullback KILLED (0.26 vs 1.05, 2004→2009). 2 ledger
  rows, index regenerated, `docs/p2-validation-results.md` + QUEUE item 4
  DONE. Holdout untouched.

## Close-out (full session)

**Done:** all three phases of the session —

1. Heartbeat/skeleton (PR #20): lane claim `claims/p2-validation.md` + this
   card, READY PR, tests + substrate-gate green, landed on green.
2. P2 validation (PR #21, merged as main `19f9a5c`): verdicts for all 14
   open candidates with params frozen from the P1 sweep JSONs — 1
   PROMOTED-TO-FINDING (AAPL-donchian daily, entry=15/exit=5, pre-2010
   window Sharpe 0.619 vs B&H 0.540), 1 KILLED (GOOGL-pullback daily,
   Sharpe 0.256 vs B&H 1.054), 12 UNVALIDATABLE-PRE-HOLDOUT (structural
   data exhaustion — P1 consumed every pre-holdout bar in their
   timeframes). Full read: `docs/p2-validation-results.md`. 2 ledger rows,
   index regenerated, QUEUE item 4 marked DONE. Holdout untouched.
3. Wrap-up (this PR, branch `p2-validation-wrapup`): inbox re-read at HEAD
   (no orders newer than ORDER 005), this card flipped to full-session
   close-out, claim `claims/p2-validation.md` deleted (lane closed),
   `control/status.md` overwritten.

**Verify:** `python3 bootstrap.py check --strict --require-session-log
--session-log .sessions/2026-07-10-p2-validation.md` → exit 0;
`python3 -m pytest -q` green at PR #21.

**Next (guard recipe):** standing default resumes at QUEUE.md § Next item 5
(holdout enforcement hardening: segregate `data/holdout/`, gate check on
holdout reads, enforce `data_end ≤ HOLDOUT_START` in every ledger row),
then item 6 (port PR-lifecycle conventions into
`docs/collaboration-model.md`). New session = new claim + new card.

Session end: 2026-07-10T03:42:56Z. Badge stays `complete`.
