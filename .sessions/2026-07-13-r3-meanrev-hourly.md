# 2026-07-13 — R3 slice 5: mean-reversion families × hourly bars (dev-only)

> **Status:** `complete` — the TIMEFRAME axis expanded with zero new
> strategy code: the four existing mean-reversion families re-swept on
> HOURLY bars over the frozen 8-ticker universe on the p1-trend-hourly dev
> rail; honest outcome **0 PROMOTED / 13 KEEP (dev-candidate only) /
> 19 KILL / 0 INSUFFICIENT-DATA** of 32 lanes. This card was born red
> (`in-progress`) and flipped `complete` as the deliberate last content
> change before push; the claim file is deleted in this same commit.

📊 Model: fable-5 · r3-meanrev-hourly lane (worker session) · start 2026-07-13T01:50Z

💡 **Session idea:** every hourly reversion verdict here is
cost-truncated evidence — at 1638 bars/year the 6 bps/side engine default
is the binding constraint (the p1-trend-hourly doc already flagged "this
cost model bites harder", and this lane's high-turnover families feel it
hardest), yet each sweep record stores only the NET result at that single
cost point, so nobody can distinguish "edge killed by 6 bps" from "no
edge at all" — a distinction the Friday grading and any future
execution-quality work would actually act on. Adopt a per-lane cost-drag
line: after the stitched-OOS evaluation, re-run the SAME stitched OOS
positions once at zero cost and record `oos_gross_sharpe` plus the
implied breakeven cost in bps/side alongside the net number (anchor: the
`walk_forward` result already carries `oos_returns` — the sweep scripts'
step-2 block can recompute the stitched slice with
`slippage_bps=commission_bps=0`; ~3 lines per script, or free if slice
1's sweep-runner extraction lands; test target: gross ≥ net on every
lane, equality iff zero trades). Not covered by recent cards' ideas
(sweep-runner extraction, control arms, cache-provenance sidecar,
sweep-verdicts index): those index or restructure existing numbers; this
records a number the lab currently throws away.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-4 (PRs #81, #82, #83, #84) expanded strategies,
indicators, and instruments — all on daily bars. This slice expands the
TIMEFRAME axis instead: NO new strategy code — the four existing
mean-reversion families (`rsi_mean_reversion`, `bollinger_reversion`,
`stochastic_reversion`, `williams_r_reversion`) are swept on HOURLY bars
over the frozen 8-ticker universe, mirroring the one prior hourly lane
(`p1-trend-hourly`: committed hourly caches only, dev bars 2023-08-10 →
2025-01-08, bar-denominated grids reused as-is — the same lookback numbers
mean hours-to-days instead of days-to-weeks — and the lab's 1008/252 BAR
walk-forward convention kept for cross-lane comparability). Promotion is
CLOSED post-holdout: mostly-KILL was the expected outcome and is
recorded as a first-class result.

## Work log

- 2026-07-13T01:50Z — clone hard-synced to origin/main HEAD `b739f48`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 5, timeframe expansion). Collision check: `control/claims/` at
  HEAD contains only `README.md` + `2026-07-13-order-night-run.md` — no
  overlap with this scope. Branch `claude/r3-meanrev-hourly`; this card +
  the claim `control/claims/2026-07-13-r3-meanrev-hourly.md` are the
  born-red FIRST commit (`264535b`), pushed before any build work.
- 2026-07-13T01:52Z — commit `5fbdca8`: Round-3 slice-5 grids declared in
  `trading_lab.sweeps` BEFORE the sweep ran — 12 variants per family, each
  grid a strict SUBSET of the family's published daily axes
  (p1-trend-hourly convention: bar-denominated lookbacks reused as-is on
  hourly bars; rsi period {2,5,14} × oversold {20,30} × overbought
  {60,70}; bollinger lookback {10,20,30} × z_entry {1.5,2.0} × z_exit
  {0.0,0.5}; stochastic k_period {14,21,28} × buy_below {10,20} ×
  sell_above {70,80}, d_period frozen 3 NOT swept; williams period
  {14,21,28} × buy_below {−90,−80} × sell_above {−30,−20}); registry
  constant `R3_MEANREV_HOURLY_FAMILY` (no strategy code); 8 grid tests
  incl. a daily-subset check and a no-new-strategies check.
- 2026-07-13T01:54Z — sweep run (`scripts/run_r3_meanrev_hourly_sweep.py`,
  mirrors `run_p1_trend_hourly_sweep.py` + the slice-1/2/4 scripts:
  committed hourly caches only, zero network fetches, `load_ohlcv` default
  rail with `data_end < HOLDOUT_START` additionally asserted per ticker —
  every lane 2023-08-10 → **2025-01-08 20:30**, 2475-2476 bars; costs
  5 bps + 1 bp per side; hourly annualization 1638; walk-forward 1008/252
  BAR convention kept decide-and-flag as in p1-trend-hourly → 5 splits,
  stitched OOS 2024-03-07 → 2024-11-22 = 1260 bars ≈ 8.5 months, one
  regime; 384 registered configs, program cumulative 1844 = 1460 prior +
  384; an `INSUFFICIENT-DATA` first-class verdict path exists for any
  cache under 1260 bars — 0 occurrences). Honest verdicts (Round-2
  KEEP/KILL rule; ORDER 007 t-stat at Bonferroni K=12 → min t 2.64
  recorded per lane, informational only, promotion CLOSED):
  - rsi_mean_reversion: **5/8 KILL**; KEEPs (dev-candidate only) AAPL
    (OOS 1.788 vs 1.570, t=0.19), GOOGL (1.828 vs 1.010, t=0.72), AMZN
    (1.188 vs 0.615, t=0.50).
  - bollinger_reversion: **5/8 KILL**; KEEPs MSFT (0.846 vs 0.148,
    t=0.61), AMZN (0.875 vs 0.615, t=0.23), META (0.625 vs 0.494, t=0.11).
  - stochastic_reversion: **5/8 KILL**; KEEPs AAPL (2.157 vs 1.570,
    t=0.51), GOOGL (1.021 vs 1.010, t=0.01 — razor-thin), META (1.529 vs
    0.494, t=0.91, the lane's best and still deep inside noise).
  - williams_r_reversion: **4/8 KILL**; KEEPs MSFT (0.249 vs 0.148,
    t=0.09), AMZN (0.885 vs 0.615, t=0.24), META (0.648 vs 0.494,
    t=0.13), SLV (1.785 vs 1.185, t=0.53).
  - Honest pattern: 13/32 (~41%) is the highest KEEP rate of any Round-3
    lane — the same oscillator families scored 2/16 on daily bars (PR
    #81) and trend scored 5/32 on this exact hourly rail — but every
    t-stat ≤ 0.91 vs the 2.64 bar, the OOS is one 8.5-month regime, and
    KILLs concentrate where B&H is strongest (NVDA and GLD 0/4 each);
    META KEEPs family-agnostically for the 4th slice of 5. "Reversion
    looks less bad intraday than daily" is the claim the data supports;
    NOT an edge, nothing promoted. 32 sweep summaries in
    `experiments/sweeps/r3-meanrev-hourly/` (all `timeframe: "hourly"`,
    `variants_tried=12`), 32 ledger rows, index rebuilt via
    `trading_lab.ledger.rebuild_index()`. Commit `28b7e75`.
- 2026-07-13T01:57Z — PR **#85** opened READY (non-draft) with the full
  honest results table; no merge action by this session (auto-merge-enabler
  is the landing path).

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-aroon-cci.md`,
Status `complete`) landed PR #84 clean — born-red first commit, grids
declared before the run, flip+claim-delete folded into one final commit —
correct discipline throughout, and its verify block reproduces from this
session's start: 303 passed there + this session's 8 new grid tests =
the 311 observed here, and its 24 `r3-aroon-cci` sweep JSONs are on main
with `data_end = 2025-01-08` as claimed. Its honest-pattern note (KEEPs
cluster where the benchmark itself is weak; META the family-agnostic
repeat offender) predicted this lane's outcome shape exactly — META
KEEPs again in 3 of 4 families here, and NVDA/GLD (strongest hourly
benchmarks) go 0/8. Its 💡 (a queryable sweep-verdicts index at
`experiments/sweeps/index.jsonl`) is sound and still unimplemented —
this session AGAIN built its PR results table by re-parsing script
stdout, the exact pain that card documented; endorsed, now with a third
concrete instance. One nit: its committed-control-arm convention was not
applicable to this lane (reversion bands have no neutral arm), so the
convention remains exercised only by gated/banded trend grids.

## Close-out

**Done:** on branch `claude/r3-meanrev-hourly` (PR #85) —

1. Pre-declared Round-3 slice-5 hourly grids, strict subsets of the
   published daily axes (`src/trading_lab/sweeps.py`) + registry constant
   only, no strategy code (`src/trading_lab/strategies/__init__.py`) +
   8 grid tests (`tests/test_sweeps.py`).
2. Sweep script `scripts/run_r3_meanrev_hourly_sweep.py` (p1-trend-hourly
   conventions; first-class `INSUFFICIENT-DATA` verdict path) + 32 lane
   summaries under `experiments/sweeps/r3-meanrev-hourly/` + 32 ledger
   rows + rebuilt `experiments/index.jsonl`.
3. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 311 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-meanrev-hourly.md`
→ exit 0 after this flip. Integrity at close: dev rail only (every lane
`data_end = 2025-01-08`, asserted per ticker in-script), holdout (SPENT)
untouched, `unlock_holdout` never passed, paper-lane files byte-untouched,
`control/inbox.md` + `control/status.md` byte-untouched, `config.UNIVERSE`
untouched, committed caches only (zero network fetches), no
broker/order/exchange code, no promotion/finding language beyond the
recorded KILL/KEEP-dev verdicts, NO merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the per-lane cost-drag/breakeven-bps line (this card's 💡 — anchors and
test target named there; especially informative for exactly these hourly
reversion lanes), the sweep-verdicts index (slice 4's 💡, endorsed again),
and the sweep-runner extraction (slice 1's 💡). The 13 KEEPs are
dev-candidates only; any OOS test of them is OWNER-GATED behind a new
pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
