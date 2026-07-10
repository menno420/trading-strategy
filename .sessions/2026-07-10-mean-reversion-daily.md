# 2026-07-10 — mean-reversion × all8 × daily (QUEUE item 2)

> **Status:** `complete` — walking-skeleton/heartbeat phase landed; lane work
> continues via amendments to this card (wind-down-card precedent) or a
> follow-up card.

📊 Model: withheld per session policy · mean-reversion lane · start 2026-07-10T02:41:36Z

💡 **Session idea:** Run the P1 known-indicator sweep for the mean-reversion
family × the full 8-ticker universe × daily bars (QUEUE.md § Next item 2, the
standing default after ORDER 005). Bounded, unit-tested grids in
`trading_lab.sweeps`; walk-forward only (`trading_lab.walkforward.walk_forward`,
train 1008 / test 252, contiguous test windows); costs on (engine defaults
5 bps slippage + 1 bp commission per side, t+1-open fills); holdout untouched;
variants counted; benchmark = buy-and-hold over the exact same stitched OOS
window. A negative result is a complete deliverable. First step: this
heartbeat PR (claim + card → READY PR → tests + substrate-gate → self-landed).

## Previous-session review

Gen-2's first session completed ORDER 005: walking skeleton (PR #14, which
found the born-red-card wall cheap), cold-boot verification (pytest 107 green,
`bootstrap.py check --strict` exit 0, live loader fetch), and the
video-strategy lane (PR #15 — QUEUE item 1 done/absorbed: dual-EMA control
negative-complete, supertrend_flip / macd_supertrend carried to P2 as
candidates only; claim deleted, status overwritten). P1 trend-following ×
all8 × daily was completed by gen-1 (177 variants, honest negative headline)
— do not re-run. Known walls inherited: born-red (`in-progress`) cards cannot
merge — flip to `complete` scoped to the landed phase in the same PR; new
docs need a Status badge + a link from a reachable doc; use the data loader
for Yahoo (proxy workaround implemented); READY-never-draft, merge on green;
tag pushes / branch deletion are 403 for agents.

## Work log

- 2026-07-10T02:41:36Z — heartbeat/skeleton: claimed the lane
  (`claims/mean-reversion__all8__daily.md`), session card (this file),
  branch `session/2026-07-10-mean-reversion-daily`, READY PR, merge on
  green. No overlap: `claims/` held only its README and there were zero
  open PRs at claim time.

## Close-out (heartbeat phase)

**Done:** heartbeat/skeleton — lane claim + this card, READY PR, tests +
substrate-gate green, self-landed on green.

**Verify:** `python3 bootstrap.py check --strict --require-session-log
--session-log .sessions/2026-07-10-mean-reversion-daily.md` → exit 0;
`python3 -m pytest -q` green.

**Next (guard recipe):** sweep phase lands as an amendment to this card:
mean-reversion family grids added to `trading_lab.sweeps` (bounded,
constraint-filtered, unit-tested counts — mirror
`scripts/run_p1_trend_sweep.py`), swept across all 8 tickers on daily
pre-holdout data via `walk_forward` (train 1008 / test 252), aggregate sweep
files under `experiments/sweeps/`, one ledger run per family × ticker top
variant, results doc badged + linked from a reachable doc. Keep MACD's
cost-churn lesson in mind: mean-reversion trades often — turnover kills at
6 bps/side. Delete `claims/mean-reversion__all8__daily.md` when the lane's
ledgered results merge.

## Amendment — sweep phase (2026-07-10T02:57:28Z)

Lane work landed per the heartbeat close-out's guard recipe (Status stays
`complete`; this phase lands as an amendment, wind-down-card precedent).

**Done (sweep phase):**

- Family built: `MEAN_REVERSION_FAMILY` = rsi_mean_reversion (P0 baseline
  reused), bollinger_reversion (new, z-score band reversion), pullback (new,
  short-horizon dip-buying, `trend_len=0/100/200` probes with/without a
  long-term trend filter). Both new strategies causality-unit-tested
  (prefix invariance) plus behavior tests.
- Grids in `trading_lab.sweeps` (`mean_reversion_variants*`, unit-tested
  counts): 48 + 48 + 48 = **144 variants**.
- Sweep run: `scripts/run_p1_meanrev_sweep.py` (mirrors the trend-lane
  script) — all 8 tickers × 3 families, daily pre-holdout dev data via
  `load_ohlcv` only (data_end 2025-01-08 ≤ HOLDOUT_START, loader-enforced;
  no network), walk-forward train 1008 / test 252 contiguous (10 splits,
  META 8), costs 5+1 bps per side, t+1-open fills, B&H benchmark over the
  exact stitched OOS window.
- Evidence: 24 aggregate sweep files under
  `experiments/sweeps/p1-mean-reversion-daily/` (per-variant full-period
  rows + walk-forward OOS + per-split picks), 24 ledger runs (top
  full-period variant per family × ticker, variants_tried=48),
  `experiments/index.jsonl` regenerated (87 rows).
- Results doc: `docs/p1-mean-reversion-results.md` (badged `reference`,
  linked from docs/current-state.md and README.md). **Verdict: 3 of 24
  family × ticker lanes beat B&H OOS (144 variants tried) — the negative
  result is the headline.** Bollinger 0/8; pullback negative outright on
  both metals. Survivors GOOGL-pullback (0.85 vs 0.72), META-rsi (0.79 vs
  0.65), META-pullback (0.67 vs 0.65) are candidates, NOT findings —
  pending P2 validation outside their selection window.
- Lane wrap-up: claim `claims/mean-reversion__all8__daily.md` deleted
  (lifecycle), QUEUE.md item 2 marked DONE, control/status.md overwritten
  as the deliberate last commit.

**Verify:** `python3 -m pytest -q` → 125 green;
`python3 bootstrap.py check --strict --require-session-log --session-log
.sessions/2026-07-10-mean-reversion-daily.md` → exit 0.

**Next (guard recipe):** QUEUE § Next item 3 (trend × hourly — mind the
cost-churn lesson at 1638 bars/year) and item 4 (P2 validation now covers
the trend candidates + GOOGL-pullback / META-rsi / META-pullback). No new
walls hit this phase — the known auto-merge "unstable status" wall and the
REST-squash fallback path are already in NEXT-BOOT.
