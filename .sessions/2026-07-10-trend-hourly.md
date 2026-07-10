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

**Next (guard recipe, executed — see amendment below):** sweep phase lands
as an amendment to this card:
reuse the trend-family grids in `trading_lab.sweeps` (or hourly-scaled
variants — decide-and-flag, unit-tested counts), sweep all 8 tickers on the
hourly pre-holdout cache via `walk_forward` with windows sized to ~2476
bars (e.g. train 1008 / test 252 hourly bars → 5 splits, stitched OOS
~1260 bars ≈ 9 months — state the single-regime caveat in the results
doc), aggregate sweep files under `experiments/sweeps/`, one ledger run
per family × ticker top variant, results doc badged + linked from a
reachable doc, claim deleted + QUEUE item 3 marked DONE in the lane PR.

## Amendment — lane execution (2026-07-10T03:14:56Z)

Sweep phase executed on branch `lane/trend-hourly` per the guard recipe:

- Reused the daily trend grids unchanged (`trading_lab.sweeps`, 44/44/48/41
  = 177 variants — decide-and-flag: same numbers, different physical
  horizons on hourly bars; stated in the results doc) via a new script
  `scripts/run_p1_trend_hourly_sweep.py` (cache-only `load_ohlcv`, zero
  network; asserts `data_end < HOLDOUT_START` per ticker).
- Walk-forward with the lab's 1008/252/252 BAR convention (kept for
  cross-lane comparability): 5 splits per ticker on 2,476 bars (GLD 2,475),
  stitched OOS 1,260 bars = 2024-03-07 → 2024-11-22 (~8.5 months, one
  regime — caveat stated as first-class in the results doc). Costs on
  (5+1 bps/side, t+1-open fills); benchmark B&H over the same OOS bars.
- Evidence: 32 aggregate sweep files in `experiments/sweeps/p1-trend-hourly/`
  (per-variant rows + walk-forward + per-split picks), 32 hourly ledger runs
  in `experiments/runs/` (all `data_end` = 2025-01-08 20:30 < HOLDOUT_START),
  `experiments/index.jsonl` regenerated via `python3 -m trading_lab.ledger`.
- Result: **5/32 family × ticker lanes beat B&H OOS** (GOOGL sma/ema/donchian
  thin margins, AMZN donchian, META macd unstable) — negative headline;
  MACD worst family on 5/8 tickers, cost-eaten at hourly churn. Full honest
  read: `docs/p1-trend-hourly-results.md` (badged, linked from
  docs/current-state.md + README.md).
- Wrap-up in this PR: claim `claims/trend-following__all8__hourly.md`
  deleted, QUEUE § Next item 3 marked DONE, NEXT-BOOT hourly-depth note
  added, control/status.md overwritten (inbox re-read first).

Lane end: 2026-07-10T03:14:56Z. Badge stays `complete`.
