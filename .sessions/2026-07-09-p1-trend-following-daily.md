# 2026-07-09 — P1: trend-following sweep, lane trend-following__all8__daily

> **Status:** `complete`

📊 Model: claude-agent · high · P1 known-indicator sweep (phase 1)

💡 **Session idea:** Open the P1 known-indicator sweep with the trend-following
lane: scaffold the founding-plan lane-claim mechanism (`claims/`), implement
SMA/EMA crossover, MACD and Donchian breakout with bounded unit-tested grids
(177 variants total), sweep all 8 tickers on daily pre-holdout data via
walk-forward with realistic costs, benchmark against buy-and-hold, ledger
everything, and write an honest results doc where the negative result is
first-class.

## Previous-session review

Previous session (2026-07-09-retro-wakeup, ORDER 003) landed the gen-1 retro
(PR #4) and the status heartbeat, and left the P1 guard recipe this session
executes: scaffold `claims/` before any sweep; findings only via
`trading_lab.walkforward.walk_forward`; READY PRs, never drafts; one ledger
JSON per recorded run. All P0 guard rails (holdout enforcement, costs on by
default, causality tests) were inherited unchanged and extended to the three
new strategies.

## Work log

- `claims/README.md` (lane-claim protocol, badged `protocol`, linked from
  README) + `claims/trend-following__all8__daily.md` — the founding-plan
  claims mechanism, created for the first time.
- `src/trading_lab/strategies/`: ema_crossover, macd, donchian added (long/
  flat, strictly trailing indicators); registered in `STRATEGIES`;
  `trading_lab/sweeps.py` holds the constraint-filtered grids (44/44/48/41 =
  177 variants, unit-tested counts). `walkforward.walk_forward` extended to
  accept explicit variant lists (constrained grids). 23 new tests; suite 86.
- `scripts/run_p1_trend_sweep.py`: full sweep — per-variant full-dev-period
  rows + walk-forward OOS (train 1008 / test 252) + B&H benchmark over the
  same stitched OOS period. Decide-and-flag: one aggregate sweep file per
  family × ticker (32 files, ~860 KB) instead of ~1,400 per-variant run
  files; one standard ledger run only for each family's top variant per
  ticker (32 runs); index regenerated via `trading_lab.ledger`.
- `docs/p1-trend-following-results.md` (badged, linked from
  current-state + README): 7 of 32 family × ticker lanes beat buy-and-hold
  on OOS Sharpe — weak evidence under a 177-variant burden; headline is the
  negative result. Candidates for P2: AAPL donchian, META sma/ema/donchian.
- `docs/current-state.md` + `docs/repo-navigation-map.md` refreshed (map
  table was an empty placeholder; filled with real rows incl. `claims/`,
  `experiments/sweeps/`).

## Close-out

**Done:** trend-following lane swept end-to-end and shipped as a READY PR on
branch `claude/p1-trend-following-daily`; claim file deleted + status
heartbeat overwritten in the follow-up PR after merge (lane complete).

**Verify:** `python3 -m pytest -q` → 86 passed; `python3 bootstrap.py check
--strict --require-session-log --session-log
.sessions/2026-07-09-p1-trend-following-daily.md` → exit 0.

**Next (guard recipe):** P2 should deflate-Sharpe the P1 candidates using the
per-variant rows in `experiments/sweeps/p1-trend-following-daily/`; remaining
P1 lanes (mean-reversion × all8 × daily, trend-following × all8 × hourly)
are unclaimed — check `claims/` before starting; keep MACD's cost-churn
lesson in mind when choosing hourly grids (turnover kills at 6 bps/side).
