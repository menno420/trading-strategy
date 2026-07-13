# 2026-07-13 — R3 stochastic + Williams %R mean-reversion sweep (dev-only)

> **Status:** `complete` — two new oscillator reversion families built,
> tested, and swept over the full 8-ticker daily universe on the standard
> dev rail; honest outcome **0 PROMOTED / 2 KEEP (dev-candidate only) /
> 14 KILL** of 16 lanes. This card was born red (`in-progress`) and flipped
> `complete` as the deliberate last content change before push; the claim
> file is deleted in this same commit.

📊 Model: fable-5 · r3-stoch-willr lane (worker session) · start 2026-07-13T00:53Z

💡 **Session idea:** every sweep script since P1 hand-copies the same ~80
lines (per-variant full-period rows, walk-forward stitch, top-variant ledger
run, summary JSON) — five near-identical copies now exist and each new one
risks silent drift in costs/window handling. Extract a
`trading_lab.sweeprunner.run_lane(family, variants, instruments, sweep_name)`
helper (anchors: `scripts/run_p1_meanrev_sweep.py` main loop +
`scripts/run_r3_stoch_willr_sweep.py`; test target: a synthetic-fixture lane
asserting the summary JSON schema and that `variants_tried` matches the
declared grid) so slice N+1 is a 20-line script and the schema can never
fork. Recent cards' ideas (in-flight decay advisory, enabler install, order
acks) don't cover this.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." The stochastic oscillator and Williams %R are the two most-cited
classic oversold oscillators the strategy library did not cover; both slot
into the existing long/flat mean-reversion conventions (signal at bar t,
engine fills at bar t+1 open) with modest pre-declared grids. Promotion is
CLOSED post-holdout: mostly-KILL was the expected outcome and is recorded as
a first-class result.

## Work log

- 2026-07-13T00:53Z — clone hard-synced to origin/main HEAD `23b0005`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane.
  Collision check: `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` (inbox-append slice, already merged) — no
  overlap with this scope. Branch `claude/r3-stoch-willr`; this card + the
  claim `control/claims/2026-07-13-r3-stoch-willr.md` were the born-red
  FIRST commit (`463e295`), pushed before any build work.
- 2026-07-13T00:56Z — commit `1ff9494`: strategies
  `stochastic_reversion` (slow %K, `d_period=3` SMA frozen; long on %K
  cross UP through `buy_below` from oversold, exit on %K > `sell_above`;
  exit wins a same-bar tie; warm-up/zero-range flat) and
  `williams_r_reversion` (same cross-up semantics on %R; the unsmoothed
  complement of %K — pinned by a test that fast-stoch(20/80) ≡
  willr(−80/−20)); registered in `STRATEGIES`/`DEFAULT_PARAMS` +
  `R3_STOCH_WILLR_FAMILY`; grids declared in `trading_lab.sweeps` BEFORE the
  sweep ran (12 variants/family: window {14,21,28} × oversold {10,20 |
  −90,−80} × exit {70,80 | −30,−20}; d_period NOT swept); 11 new unit tests
  + 6 grid tests, all offline synthetic data.
- 2026-07-13T00:59Z — sweep run (`scripts/run_r3_stoch_willr_sweep.py`,
  mirrors the Round-2 scripts: `load_ohlcv` default rail, dev bars
  2010-01-04 → **2025-01-08**, costs 5 bps + 1 bp per side, walk-forward
  1008/252 contiguous stitched OOS vs same-window same-cost B&H; 192
  registered configs, program cumulative 872 = 680 prior + 192). Honest
  verdicts (Round-2 KEEP/KILL rule; ORDER 007 t-stat at Bonferroni K=12 →
  min t 2.64 recorded per lane, informational only, promotion CLOSED):
  - stochastic_reversion: **8/8 KILL** (best lane GOOGL OOS 0.592 vs B&H
    0.720, t=−0.41; worst META −0.016 vs 0.653).
  - williams_r_reversion: **6/8 KILL**; GLD KEEP (dev-candidate only, OOS
    0.552 vs 0.400, t=0.48) and SLV KEEP (dev-candidate only, OOS 0.500 vs
    0.170, t=1.04) — both deep inside noise vs the 2.64 bar; NOT findings,
    nothing promoted.
  - 16 sweep summaries in `experiments/sweeps/r3-stoch-willr/`, 16 ledger
    rows (one top-variant run per lane, `variants_tried=12`), index rebuilt
    via `trading_lab.ledger.rebuild_index()`. Commit `02917df`.
- 2026-07-13T01:02Z — PR **#81** opened READY (non-draft) with the full
  honest results table; no merge action by this session (auto-merge-enabler
  is the landing path).

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-12-docs-restamp.md`,
Status `complete`) landed PR #77 clean: `docs/current-state.md` re-stamped
to live GitHub state (two stale in-flight lanes recorded terminal) and
`docs/CAPABILITIES.md` given its first real append-log entry (the
auto-merge-enabler landing path). Correct born-red → complete discipline and
a genuine idea (a docs-gate advisory flagging in-flight bullets that cite
already-merged PR numbers). Its claim (`claude-docs-restamp.md`) was deleted
via the follow-up PR #78 rather than in the flip commit itself — this
session folds the claim deletion into the flip commit, which is one less PR
of control traffic.

## Close-out

**Done:** on branch `claude/r3-stoch-willr` (PR #81) —

1. Two new strategies + registration
   (`src/trading_lab/strategies/stochastic_reversion.py`,
   `williams_r_reversion.py`, `__init__.py`).
2. Pre-declared Round-3 grids (`src/trading_lab/sweeps.py`) + tests
   (`tests/test_strategies.py`, `tests/test_sweeps.py`).
3. Sweep script `scripts/run_r3_stoch_willr_sweep.py` + 16 lane summaries
   under `experiments/sweeps/r3-stoch-willr/` + 16 ledger rows + rebuilt
   `experiments/index.jsonl`.
4. This card (born-red first commit → flipped `complete` last) — claim file
   deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 250 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-stoch-willr.md`
→ exit 0 after this flip. Integrity at close: dev rail only (every lane
`data_end = 2025-01-08`), holdout (SPENT) untouched, `unlock_holdout` never
passed, paper-lane files byte-untouched, `control/inbox.md` +
`control/status.md` byte-untouched, no promotion/finding language beyond the
recorded KILL/KEEP-dev verdicts, NO merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidate: the
sweep-runner extraction (see 💡 above — anchors and test target named
there). The two Williams-%R metal KEEPs are dev-candidates only; any OOS
test of them is OWNER-GATED behind a new pre-registered protocol on
post-2026 data, per docs/research-round-2-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
