# 2026-07-10 — trend-following × all8 × hourly (QUEUE item 3)

> **Status:** `complete` — walking-skeleton/heartbeat phase landed; lane work
> continues via amendments to this card (wind-down-card precedent) or a
> follow-up card.

📊 Model: withheld per session policy · trend-hourly lane · start 2026-07-10T03:06:29Z

💡 **Session idea:** Run the P1 known-indicator sweep for the trend-following
family × the full 8-ticker universe × hourly bars (QUEUE.md § Next item 3, the
standing default after ORDER 005). Bounded, unit-tested grids in
`trading_lab.sweeps` (hourly-appropriate window scaling is this lane's
decide-and-flag); walk-forward only (`trading_lab.walkforward.walk_forward`,
window sizes chosen for the ~2476-bar pre-holdout hourly history); costs on
(engine defaults 5 bps slippage + 1 bp commission per side, t+1-open fills —
the cost-churn lesson bites harder at 1638 bars/year); holdout untouched
(hourly cache is loader-enforced like daily); variants counted; benchmark =
buy-and-hold over the exact same stitched OOS window. A negative result is a
complete deliverable. First step: this heartbeat PR (claim + card → READY PR
→ tests + substrate-gate → self-landed).

## Previous-session review

Gen-2 sessions completed QUEUE items 1 (video-strategy lane, PR #15 —
dual-EMA control negative-complete, supertrend_flip / macd_supertrend to P2
as candidates) and 2 (mean-reversion × daily, PR #17 — 3/24 lanes beat B&H
with 144 variants tried; GOOGL-pullback / META-rsi / META-pullback to P2 as
candidates only). Trend × daily was swept by gen-1 (177 variants, honest
negative headline) — do not re-run. Known walls inherited: born-red
(`in-progress`) cards cannot merge — flip to `complete` scoped to the landed
phase in the same PR; new docs need a Status badge + a link from a reachable
doc; use the data loader for Yahoo (proxy workaround implemented);
READY-never-draft, merge on green; auto-merge arm can fail "unstable status"
(pending) and "already in clean status" (green) — REST squash on green is the
fallback; tag pushes / branch deletion are 403 for agents.

## Work log

- 2026-07-10T03:06:29Z — heartbeat/skeleton: claimed the lane
  (`claims/trend-following__all8__hourly.md`), session card (this file),
  branch `session/2026-07-10-trend-hourly`, READY PR, merge on green. No
  overlap: `claims/` held only its README and there were zero open PRs at
  claim time.
- Data feasibility (read-only recon, this phase): committed hourly cache
  spans 2023-08-10 → 2026-07-09; loader-enforced pre-holdout slice is
  2023-08-10 → 2025-01-08, ~2476 bars for every UNIVERSE ticker. A live
  loader fetch (AAPL 1h) confirmed Yahoo currently serves history back to
  the same 2023-08-10 boundary — the committed cache is the lane's data,
  no refresh needed or wanted.

## Close-out (heartbeat phase)

**Done:** heartbeat/skeleton — lane claim + this card, READY PR, tests +
substrate-gate green, self-landed on green.

**Verify:** `python3 bootstrap.py check --strict --require-session-log
--session-log .sessions/2026-07-10-trend-hourly.md` → exit 0;
`python3 -m pytest -q` green.

**Next (guard recipe):** sweep phase lands as an amendment to this card:
reuse the trend-family grids in `trading_lab.sweeps` (or hourly-scaled
variants — decide-and-flag, unit-tested counts), sweep all 8 tickers on the
hourly pre-holdout cache via `walk_forward` with windows sized to ~2476
bars (e.g. train 1008 / test 252 hourly bars → 5 splits, stitched OOS
~1260 bars ≈ 9 months — state the single-regime caveat in the results
doc), aggregate sweep files under `experiments/sweeps/`, one ledger run
per family × ticker top variant, results doc badged + linked from a
reachable doc, claim deleted + QUEUE item 3 marked DONE in the lane PR.
