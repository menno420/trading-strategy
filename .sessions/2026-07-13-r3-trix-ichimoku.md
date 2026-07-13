# 2026-07-13 — R3 slice 8: TRIX momentum + Ichimoku trend sweep (dev-only)

> **Status:** `complete` — two new classic-indicator families built, tested
> (including explicit ichimoku no-lookahead tests), and swept over the
> 12-ticker mixed set (frozen 8-ticker universe + SPY/QQQ/TSLA/TLT
> lane-local) on the standard dev rail; honest outcome **0 PROMOTED /
> 6 KEEP (dev-candidate only, five of the six at t ≤ 0.14) / 18 KILL** of
> 24 lanes. This card was born red (`in-progress`) and flipped `complete`
> as the deliberate last content change before push; the claim file is
> deleted in this same commit.

📊 Model: fable-5 · r3-trix-ichimoku lane (worker session) · start 2026-07-13T02:39Z

💡 **Session idea:** `walk_forward` treats its two phases asymmetrically —
the TEST window generates signals with full trailing history
(`signal_frame = ohlcv.iloc[:sp.test_end]`, so indicators arrive warm),
but every TRAIN-side selection backtest cold-starts
(`strategy_fn(train, **params)` on the bare 1008-bar slice), forcing the
family's warm-up flat at the top of every train window. For short
lookbacks that's noise, but this lane fielded the lab's longest warm-up
(ichimoku: senkou_b − 1 + displacement = 77 bars ≈ 7.7% of every train
window structurally flat, and the penalty SCALES with the senkou_b/kijun
axes), so parameter selection systematically dings long-lookback variants
under conditions the test phase never reproduces — params are chosen in a
cold-start world and deployed in a warm-history world. Fix in
`trading_lab.walkforward`: score train candidates the same way the test
window is signalled — positions from `ohlcv.iloc[:sp.train_end]` sliced
to `[train_start, train_end)` (the first split has no earlier history and
stays a documented cold start). Test target: a synthetic long-warm-up
strategy whose train-window score changes when history is prepended,
asserted equal post-fix; plus a no-behavior-change check for
warm-up-free families (buy_and_hold). Not covered by recent cards' ideas
(sweep-runner extraction, sweep-verdicts index, OOS activity line,
benchmark-drift arm, cache-provenance sidecar, control-arm convention):
those instrument outputs or grids; this fixes a selection-vs-deployment
mismatch inside the walk-forward itself.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-7 (PRs #81-#87) are merged. This slice adds two
classic indicators the library still lacked — TRIX (`trix_momentum`,
triple-smoothed EMA rate-of-change with a signal-line cross; the
`signal_period == 0` zero-line arm is the committed within-family
control) and Ichimoku Kinko Hyo (`ichimoku_trend`, cloud + tenkan/kijun
confirmation — the lab's first multi-component indicator system, and the
classic lookahead trap: the senkou spans are displaced 26 bars FORWARD,
so the implementation and its tests must prove the cloud at bar t derives
from bars ≤ t−26 only) — both long/flat on the existing conventions
(signal at bar t, engine fills at bar t+1 open), swept over the slice-4/6
12-ticker mixed set on the daily dev rail. Promotion is CLOSED
post-holdout: mostly-KILL was the expected outcome and is recorded as a
first-class result.

## Work log

- 2026-07-13T02:39Z — clone hard-synced to origin/main HEAD `edd02bf`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 8). Collision check: `control/claims/` at HEAD contains only
  `README.md` + `2026-07-13-order-night-run.md` — no overlap with this
  scope. Branch `claude/r3-trix-ichimoku`; this card + the claim
  `control/claims/2026-07-13-r3-trix-ichimoku.md` are the born-red FIRST
  commit (`ec9c97e`), pushed before any build work.
- 2026-07-13T02:44Z — commit `f62514c`: strategies `trix_momentum`
  (TRIX = 1-bar fractional ROC of the triple EMA, recursive `ewm`
  strictly trailing; committed semantic: long while TRIX strictly above
  its EMA(signal_period) signal line — the level rule; a cross/
  reverse-cross formulation yields the identical position series and is
  documented as such; `signal_period == 0` replaces the signal line with
  the constant 0 = the classic TRIX zero-line rule, committed in the grid
  as the control arm per the slice-2/4 convention; warm-up
  `3·period + signal_period + 1` bars flat; boundary ties resolve flat)
  and `ichimoku_trend` (standard Hosoda midpoints; span A/B displaced
  forward the frozen standard 26 bars via `.shift(26)` on trailing series
  — past data only, chikou omitted; entry: close strictly above the cloud
  TOP and tenkan strictly above kijun; committed exit, documented: close
  strictly below the cloud BOTTOM — a full cloud break — OR tenkan
  strictly below kijun; inside the cloud with tenkan ≥ kijun holds the
  previous state; entry/exit provably disjoint; warm-up flat); registered
  in `STRATEGIES`/`DEFAULT_PARAMS` + `R3_TRIX_ICHIMOKU_FAMILY`; grids
  declared in `trading_lab.sweeps` BEFORE the sweep ran (12
  variants/family: trix period {9,12,15,21} × signal_period {0,5,9};
  ichimoku tenkan {7,9,12} × kijun {22,26} × senkou_b {44,52} with
  tenkan < kijun < senkou_b, classic 9/26/52 committed verbatim,
  displacement frozen and asserted un-swept); 29 new tests, incl. THREE
  explicit ichimoku no-lookahead tests (future-truncation over three
  non-default grids × three cut points; future-REWRITE — a fabricated
  crash after bar 250 leaves positions ≤ 250 byte-identical; span-at-t
  pinned to the undisplaced midpoints at t−26), all offline synthetic
  data.
- 2026-07-13T02:46Z — sweep run (`scripts/run_r3_trix_ichimoku_sweep.py`,
  mirrors the slice-4/6 scripts: `load_ohlcv` default rail with
  `data_end ≤ 2025-01-08` additionally asserted per ticker, costs 5 bps +
  1 bp per side, walk-forward 1008/252 contiguous stitched OOS vs
  same-window same-cost B&H; 288 registered configs, program cumulative
  2432 = 2144 prior + 288). Honest verdicts (Round-2 KEEP/KILL rule;
  ORDER 007 t-stat at Bonferroni K=12 → min t 2.64 recorded per lane,
  informational only, promotion CLOSED):
  - trix_momentum: **8/12 KILL**; KEEPs (dev-candidate only) AAPL (OOS
    0.985 vs 0.963, t=0.07), META (0.672 vs 0.653, t=0.05), SLV (0.184
    vs 0.170, t=0.05), TLT (0.239 vs 0.196, t=0.14).
  - ichimoku_trend: **10/12 KILL**; KEEPs META (0.993 vs 0.653, t=0.96 —
    the lane's best, still nowhere near 2.64) and TLT (0.203 vs 0.196,
    t=0.02).
  - Honest pattern: five of six KEEPs sit at t ≤ 0.14 (+0.007..+0.043
    Sharpe margins — coin-flip territory) and cluster where the benchmark
    itself is weak (SLV/TLT B&H OOS ≤ 0.2; META the repeat offender, now
    6 slices running) — a low bar cleared, not an edge. The extra
    Ichimoku machinery buys nothing systematic over the single TRIX line
    (6-6 across tickers). NOT findings, nothing promoted. 24 sweep
    summaries in `experiments/sweeps/r3-trix-ichimoku/`, 24 ledger rows
    (one top-variant run per lane, `variants_tried=12`), index rebuilt
    via `trading_lab.ledger.rebuild_index()`. Commit `4a01140`.
- 2026-07-13T02:50Z — PR **#88** opened READY (non-draft) with the full
  honest results table; no merge action by this session (auto-merge-enabler
  is the landing path). Flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-xsec-expanded.md`,
Status `complete`) landed PR #87 clean — born-red first commit, grids
declared before the run, honest 6 KEEP-dev / 6 KILL verdicts with the
reversal KILL framed as the deliverable, flip+claim-delete folded into
one final commit — correct discipline throughout, and its verify block
reproduces from this session's start: its 354 passed + this session's 29
new tests = the 383 observed here, and its 2 `r3-xsec-expanded` sweep
JSONs are on main (`variants_tried=6`, `data_end=2025-01-08`) exactly as
claimed. Its sharpest honest move — flagging that META's IPO, not TSLA's,
truncates the common window, against the task brief's expectation —
recurs in this lane in miniature (META is again the odd window out:
8 splits / 2016 OOS bars vs 10/2520 everywhere else), and its
"KEEPs ride weak benchmarks" reading is re-confirmed a sixth time here.
Its 💡 (benchmark-drift instrumentation + a rebalanced equal-weight
benchmark arm) is sound, portfolio-lane-specific, and still
unimplemented; endorsed — though it deliberately does NOT apply to this
single-instrument lane, whose B&H benchmark has no composition to drift.
One structural observation rather than a nit: its close-out already
flagged that `portfolio_walk_forward` shares slice 6's stitched-positions
blind spot, and this session found a third walk-forward gap (the
train-side cold-start asymmetry, this card's 💡) — `walkforward.py` is
now the fleet's most-cited unpaid-instrumentation site and probably the
right next infrastructure slice.

## Close-out

**Done:** on branch `claude/r3-trix-ichimoku` (PR #88) —

1. Two new strategies + registration
   (`src/trading_lab/strategies/trix_momentum.py`, `ichimoku_trend.py`,
   `__init__.py`).
2. Pre-declared Round-3 slice-8 grids over the 12-ticker mixed set
   (`src/trading_lab/sweeps.py`) + 29 tests (`tests/test_strategies.py`,
   `tests/test_sweeps.py`, incl. the explicit ichimoku no-lookahead
   trio and the committed trix zero-line control-arm check).
3. Sweep script `scripts/run_r3_trix_ichimoku_sweep.py` + 24 lane
   summaries under `experiments/sweeps/r3-trix-ichimoku/` + 24 ledger
   rows + rebuilt `experiments/index.jsonl`.
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 383 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-trix-ichimoku.md`
→ exit 0 after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: dev rail only (every lane
`data_end = 2025-01-08`, asserted per ticker in-script), holdout (SPENT)
untouched, `unlock_holdout` never passed, paper-lane files
byte-untouched, `control/inbox.md` + `control/status.md` byte-untouched,
`config.UNIVERSE` untouched (extra instruments lane-local, slice-3
caches reused, zero network fetches), no broker/order/exchange code, no
promotion/finding language beyond the recorded KILL/KEEP-dev verdicts,
NO merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the walk-forward train-side warm-history fix (this card's 💡 — anchors
and test targets named there), the stitched-positions/OOS-activity
plumbing (slice 6's 💡, endorsed by slice 7 for both walk-forwards), the
sweep-verdicts index (slice 4's 💡). The six KEEPs are dev-candidates
only; any OOS test of them is OWNER-GATED behind a new pre-registered
protocol on post-2026 data, per docs/research-round-2-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
