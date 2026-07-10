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
