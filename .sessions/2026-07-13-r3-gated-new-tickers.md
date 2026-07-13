# 2026-07-13 — R3 slice 12: R2/gated families × new tickers (dev-only)

> **Status:** `complete` — the three existing R2/gated families
> (keltner_breakout, vol_filtered_trend, macd_supertrend) swept with
> pre-declared sub-grids of their published axes over the six PR #83
> instruments (SPY, QQQ, TSLA, JPM, XOM, TLT) on the standard dev rail;
> NO new strategy code. All three families were previously narrow-universe
> (4/4/1 instruments); macd_supertrend's first ever equities/ETF run.
> Honest outcome **0 PROMOTED / 4 KEEP (dev-candidate only) / 14 KILL** of
> 18 lanes — all 4 KEEPs cluster on the two weakest benchmarks (XOM, TLT),
> all 12 strong-benchmark lanes KILL, and the vol_filtered_trend control
> arm shows the vol gate SUBTRACTS value on every one of these
> instruments. This slice lands AFTER the Round-3 synthesis (PR #89,
> slices 1-8) and extends the round; the synthesis doc is NOT rewritten —
> its delta is recorded here. This card was born red (`in-progress`) and
> flipped `complete` as the deliberate last content change before push;
> the claim file is deleted in this same commit.

📊 Model: fable-5 · r3-gated-new-tickers lane (worker session) · start 2026-07-13T03:36Z

💡 **Session idea:** gated grids commit their neutral control arm (the
slice-2/4 convention this lane follows for vol_filtered_trend), but
NOTHING in the pipeline ever consumes it — the gate-vs-no-gate comparison
the arm exists to enable stays buried in `full_period_variants.rows`, and
any reader must recompute it by hand. This session's data shows what that
costs: on all six new instruments the `vol_filter=False` arm's best
full-dev-period Sharpe beats the gated arm's best (TLT 0.486 vs 0.101 is
a 4.8× gap), and the walk-forward selector picked the ungated arm in
46/60 splits — the honest sentence "the vol gate subtracts value on these
instruments; the family's KEEPs are the plain SMA crossover showing
through" exists only because this card's author manually diffed 72 JSON
rows. Add a `control_arm_delta` block to the sweep record, computed at
sweep time for any family whose grid carries a declared neutral arm:
{best gated vs best neutral full-period Sharpe, wf split-selection share
per arm, and the stitched-OOS Sharpe of the neutral-arm-only sub-grid as
its own walk-forward}. Zero new search burden for the first two fields
(pure aggregation of rows already in every record); the third is one
extra walk-forward over an already-registered sub-grid, declared as part
of the lane. Payoff: (a) "does the gate earn its complexity?" becomes a
machine-readable field instead of card archaeology; (b) gate-family
verdicts stop conflating the gate's contribution with its base signal's;
(c) future gate proposals (ADX, vol, regime) get a standing evidence
format to be judged against. Machine-checkable: recompute the aggregation
fields from `full_period_variants.rows` + `walk_forward.per_split` in any
sweep JSON whose grid declares a neutral arm.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 3 (PR #83) added the six new instrument caches; slice 10
(PR #90) completed the TREND-family coverage of that surface and slice 11
(PR #91) the MEAN-REVERSION coverage. This slice completes the remaining
single-instrument coverage with the three R2/gated families — all of them
previously NARROW-UNIVERSE, stated honestly up front:
`vol_filtered_trend` has only ever run on the Round-2 §3a four (AAPL,
MSFT, NVDA, GLD); `keltner_breakout` only on the Round-2 §3b four
(BTC-USD, META, AMZN, SLV); `macd_supertrend` only on BTC-USD (the P1
video lane) — this is its first run on equities/ETFs. Grids are
pre-declared subsets of each family's published axes (no new parameter
territory, no new strategy code): vol_filtered_trend reuses its full
12-variant R2 grid VERBATIM including the `vol_filter=False` control arm
(slice-2 card convention: gated grids commit their neutral arm);
keltner_breakout reuses its full R2 grid VERBATIM — that grid is only 6
variants, and expanding it to ~12 would open new parameter territory, so
the honest choice is 6, not 12; macd_supertrend takes a 12-variant
sub-grid of the 36-variant P1 video grid with the MACD triple frozen at
the classic 12/26/9 (slice 10's supertrend_flip precedent). Backtests run
on the default `load_ohlcv` dev rail (holdout ≥ 2025-01-09 excluded; the
holdout is SPENT). Promotion is CLOSED post-holdout: mostly-KILL is the
expected outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T03:36Z — clone hard-synced to origin/main HEAD `39ab8aa`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 12, R2/gated families × new tickers). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-gated-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-gated-new-tickers.md` are the born-red
  FIRST commit (`0286a41`), pushed before any build work.
- 2026-07-13T03:38Z — grids declared in `trading_lab.sweeps` BEFORE the
  sweep ran (`R3_GATED_NEW_TICKERS_*`: keltner_breakout n {20,50} × m
  {1.5,2.0,2.5} — the full R2 §3b grid VERBATIM, honestly 6 variants;
  vol_filtered_trend fast {10,20} × slow {50,100,200} × vol_filter
  {on,off} — the full R2 §3a grid VERBATIM incl. the filter-off control
  arm; macd_supertrend st_period {10,14} × st_mult {2.0,3.0,4.0} ×
  ema_len {100,200} with the MACD triple frozen at 12/26/9 — a 12-variant
  sub-grid of the 36-variant P1 video grid, slice 10's supertrend_flip
  axes verbatim). Every point a member of the family's published grid;
  subset/equality + control-arm + frozen-triple relations pinned in
  `tests/test_sweeps.py::TestR3GatedNewTickersGrid` (9 tests).
  Instruments = the slice-3 set reused verbatim (same tuple object);
  `config.UNIVERSE` untouched. Commit `4e2ee9e`.
- 2026-07-13T03:40Z — sweep run (`scripts/run_r3_gated_new_tickers.py`,
  mirrors `scripts/run_r3_meanrev_new_tickers.py`: `load_ohlcv` default
  rail with `data_end ≤ 2025-01-08` ASSERTED per ticker — all six lanes
  end 2025-01-08 exactly; costs 5 bps + 1 bp per side; walk-forward
  1008/252 contiguous stitched OOS vs same-window same-cost B&H; 180
  registered configs, program cumulative 3260 = 3080 prior + 180; NO new
  B&H ledger rows — the six baselines are on the ledger from slice 3).
  Honest verdicts (Round-2 KEEP/KILL rule; ORDER 007 t-stat at Bonferroni
  K = variants this lane → min t 2.39 for keltner (K=6), 2.64 for the
  others (K=12), informational only, promotion CLOSED):
  - keltner_breakout: **5/6 KILL**; XOM KEEP (0.337 vs 0.294, t=0.14).
  - vol_filtered_trend: **4/6 KILL**; XOM KEEP (0.298 vs 0.294, t=0.01 —
    a hairline strict-inequality edge), TLT KEEP (0.414 vs 0.196, t=0.69 —
    the slice's best, still far under 2.64).
  - macd_supertrend: **5/6 KILL**; XOM KEEP (0.319 vs 0.294, t=0.08).
    First equities/ETF run for this family: it is a null away from
    BTC-USD.
  - Honest pattern: the weak-benchmark clustering slice 11 partially
    broke is fully restored — all 4 KEEPs sit on the two weakest
    benchmarks (XOM B&H 0.294, TLT 0.196); all 12 strong-benchmark lanes
    (SPY/QQQ/TSLA/JPM) KILL. Max KEEP t = 0.69; NOT findings, nothing
    promoted. No lane crosses the NEGATIVE bar either (worst SPY
    macd_supertrend t=−1.70 — nothing like slice 11's TSLA rsi −3.01).
  - Gate-value note (in-sample bookkeeping, NOT a finding): the
    vol_filter=False control arm's best full-dev-period Sharpe beats the
    gated arm's best on ALL SIX instruments (e.g. SPY 0.859 vs 0.519,
    TLT 0.486 vs 0.101) and the walk-forward selector picked the ungated
    arm in 46/60 splits — the vol gate subtracts value here; XOM (the
    lone family KEEP, t=0.01) is the only instrument where the selector
    mostly picked the gated arm (7/10 splits). See this card's 💡.
  - 18 sweep summaries in `experiments/sweeps/r3-gated-new-tickers/`, 18
    top-variant ledger rows (`variants_tried` = 6 or 12), index rebuilt
    via `trading_lab.ledger.rebuild_index()`. Commit `b32ae3a`.
- 2026-07-13T03:42Z — verify: `python3 -m pytest -q` → **411 passed**
  (402 on main + 9 new grid tests); pre-flip `bootstrap.py check --strict
  --require-session-log` red ONLY on the designed born-red gate. PR **#92**
  opened READY (non-draft) with the full honest results table, the
  keltner 6-not-12 count note, the gate-value note and the explicit
  synthesis-scope note; no merge action by this session
  (auto-merge-enabler is the landing path).
- Round-3 delta recorded here, NOT in the synthesis doc (it is scoped to
  slices 1-8 / PRs #81-#88 with pinned totals; the docs convention has no
  addendum mechanism for `reference` docs, so rewriting it would breach
  its own scope statement): after this slice the extended round stands at
  **2,580 registered configs, 238 graded lanes, 0 PROMOTED / 53 KEEP-dev /
  185 KILL**, program cumulative **3,260**.
- 2026-07-13T03:44Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-meanrev-new-tickers.md`,
Status `complete`) landed PR #91 clean and is the direct template of this
session: born-red first commit, grids pre-declared with subset relations
pinned by tests, dev rail asserted per ticker, no duplicate B&H rows,
synthesis doc left untouched with the extended-round delta in the card,
flip+claim-delete in one final commit. Its verify block reproduces at
this session's start: 402 passed on main matches its claimed count, and
its "program cumulative 3,080" is what this session's
`PROGRAM_PRIOR_CONFIGS = 3080` is anchored to. Three observations from
building on it: (1) its 💡 (a KILL-SIG verdict class for significant
underperformance) remains unimplemented and this slice is a clean
negative test for the gap's other side — NO lane here crosses t ≤ −2.64/
−2.39, so under KILL-SIG this whole slice would still grade plain KILL,
which is exactly the discrimination the class is for (slice 11's TSLA
rsi would grade KILL-SIG; this slice's worst, SPY macd_supertrend
t=−1.70, would not). (2) Its honest-pattern language transferred
cleanly: the strong/weak-benchmark framing it sharpened (after slice 10)
predicted this slice's outcome — all 4 KEEPs on weak benchmarks, all 12
strong-benchmark lanes KILL. (3) Its `family_status` honesty-note
convention scaled to a per-family dict here (three different
narrow-universe histories), which is tidier than slice 10/11's inline
conditional — a small structural improvement worth keeping. No defect
found in its work; its "12 variants per family" framing did surface one
friction this session had to resolve honestly rather than mechanically:
keltner_breakout's full published grid is 6, and copying the "12"
headline number would have required inventing parameter territory — the
card convention should say "sub-grids of published axes, sized honestly"
rather than pinning a count.

## Close-out

**Done:** on branch `claude/r3-gated-new-tickers` (PR #92) —

1. Pre-declared Round-3 slice-12 grids (`src/trading_lab/sweeps.py`,
   `R3_GATED_NEW_TICKERS_*`: keltner_breakout 6 + vol_filtered_trend 12 +
   macd_supertrend 12 variants, subsets of the published R2/P1-video
   axes — keltner and vol_filtered full R2 grids verbatim, the
   vol_filter=False control arm committed, the MACD triple frozen) +
   tests (`tests/test_sweeps.py::TestR3GatedNewTickersGrid`, 9 tests).
2. Sweep script `scripts/run_r3_gated_new_tickers.py` (dev rail asserted
   per ticker) + 18 lane summaries under
   `experiments/sweeps/r3-gated-new-tickers/` + 18 top-variant ledger
   rows (`variants_tried` = 6 or 12; no duplicate B&H baselines) +
   rebuilt `experiments/index.jsonl`.
3. NO new strategy code, NO new data fetches, NO synthesis-doc rewrite
   (delta recorded in this card's work log).
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 411 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-gated-new-tickers.md`
→ exit 0 after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: dev rail only (every lane
`data_end = 2025-01-08`, asserted in-script), holdout (SPENT) untouched,
`unlock_holdout` never passed, `data/p5holdout/` untouched, paper-lane
files byte-untouched, `control/inbox.md` + `control/status.md` +
`control/outbox.md` byte-untouched, no triggers created or modified, no
market data fetched, no broker/order/exchange code, no promotion/finding
language beyond the recorded KILL/KEEP-dev verdicts, NO merge action
taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the `control_arm_delta` block (this card's 💡 — two of three fields are
pure aggregation of data already in every gated sweep JSON), the KILL-SIG
verdict class (slice 11's 💡), the round-scope manifest (slice 10's 💡,
now three post-synthesis extensions deep), then the standing stack
(sweep-runner extraction — this session hand-copied the ~250-line sweep
script a TENTH time — graded-unit schema normalization, walk-forward
warm-history fix, provenance sidecar). The 4 KEEPs are dev-candidates
only; any OOS test of them is OWNER-GATED behind a new pre-registered
protocol on post-2026 data, per docs/research-round-2-results.md and
docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
