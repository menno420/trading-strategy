# 2026-07-13 — R3 slice 10: full trend families × new tickers (dev-only)

> **Status:** `complete` — the four existing trend families (donchian,
> ema_crossover, macd, supertrend_flip) swept with pre-declared 12-variant
> sub-grids of their published axes over the six PR #83 instruments (SPY,
> QQQ, TSLA, JPM, XOM, TLT) on the standard dev rail; NO new strategy code.
> Honest outcome **0 PROMOTED / 5 KEEP (dev-candidate only) / 19 KILL** of
> 24 lanes — all 16 lanes on the strong-benchmark instruments KILL. This
> slice lands AFTER the Round-3 synthesis (PR #89, slices 1-8) and extends
> the round; the synthesis doc is NOT rewritten — its delta is recorded
> here. This card was born red (`in-progress`) and flipped `complete` as
> the deliberate last content change before push; the claim file is
> deleted in this same commit.

📊 Model: fable-5 · r3-trend-new-tickers lane (worker session) · start 2026-07-13T03:11Z

💡 **Session idea:** a research round's synthesis doc has no machine-checked
SCOPE, and this session is the first live collision with that gap:
`docs/research-round-3-results.md` pins "1,752 configs / 166 lanes /
41 KEEP / 125 KILL" for PRs #81–#88, but nothing marks which sweep dirs
that covers — the moment this slice merged, any consumer that aggregates
`experiments/sweeps/r3-*/` (the morning tally, the Friday grading, and
notably the aggregation test proposed in the synthesis card's own 💡,
which would assert 41/125/166 over the r3-* glob) silently disagrees with
the doc it was built to verify. Adopt a round-scope manifest: the
synthesis commits a small sidecar (e.g. `experiments/sweeps/ROUNDS.json`:
round → list of sweep dirs + PR numbers + pinned verdict totals), the
synthesis doc's totals cite the manifest entry, and the future aggregation
test asserts each round's totals over ITS MANIFEST ENTRY, not over a name
glob — a late-landing slice like this one then appends itself as an
`addendum` entry (this slice: `r3-trend-new-tickers`, +288 configs, +24
lanes, +5/+19) instead of silently drifting every consumer (anchor: the
scope sentence at the top of `docs/research-round-3-results.md` and its
budget-ledger table; test target: manifest totals == re-aggregated JSON
totals per entry). Recent cards' ideas (sweep-runner extraction, verdicts
index, graded-unit schema normalization, control arms, provenance sidecar,
walk-forward warm-history fix, cost-drag / OOS-activity lines) don't cover
this: schema normalization makes records parseable one way; this makes the
SET of records a round claims explicit and testable.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 3 (PR #83) added the six new instrument caches but probed
them with only small 6-variant grids of three families (donchian,
sma_crossover, rsi_mean_reversion). This slice completes the TREND-family
coverage of those instruments: donchian, ema_crossover, macd and
supertrend_flip with 12 pre-declared variants each — every grid point a
subset of the family's existing published axes (P1 trend axes; the video
lane's supertrend grid), no new parameter territory, no new strategy code.
Honest note up front: `supertrend_flip` had only ever been run on BTC-USD
(the P1 video lane) — this is its first run on equities/ETFs, and that is
an instrument-transfer question, not a tuned-strategy claim. Backtests run
on the default `load_ohlcv` dev rail (holdout ≥ 2025-01-09 excluded; the
holdout is SPENT). Promotion is CLOSED post-holdout: mostly-KILL is the
expected outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T03:11Z — clone hard-synced to origin/main HEAD `374651a`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 10, trend families × new tickers). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-trend-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-trend-new-tickers.md` are the born-red
  FIRST commit (`043a94c`), pushed before any build work.
- 2026-07-13T03:13Z — grids declared in `trading_lab.sweeps` BEFORE the
  sweep ran (`R3_TREND_NEW_TICKERS_*`: donchian entry {10,15,30,80,100} ×
  exit {5,15,30}, constraint-filtered to 12 and DISJOINT from the slice-3
  probe grid; ema_crossover fast {10,20,30} × slow {50,100,150,200};
  macd fast {8,12} × slow {21,26,35} × signal {5,9}; supertrend_flip
  st_period {10,14} × st_mult {2,3,4} × ema_len {100,200} with the MACD
  triple frozen at the classic 12/26/9 — 12 variants/family, every point a
  member of the family's published grid, subset + disjointness relations
  pinned in `tests/test_sweeps.py::TestR3TrendNewTickersGrid`, 9 tests).
  Instruments = the slice-3 set reused verbatim (same tuple object);
  `config.UNIVERSE` untouched. Commit `327d63d`.
- 2026-07-13T03:15Z — sweep run (`scripts/run_r3_trend_new_tickers.py`,
  mirrors the merged r3 scripts: `load_ohlcv` default rail with
  `data_end ≤ 2025-01-08` ASSERTED per ticker — all six lanes end
  2025-01-08 exactly; costs 5 bps + 1 bp per side; walk-forward 1008/252
  contiguous stitched OOS vs same-window same-cost B&H; 288 registered
  configs, program cumulative 2720 = 2432 prior + 288; NO new B&H ledger
  rows — the six baselines are on the ledger from slice 3). Honest
  verdicts (Round-2 KEEP/KILL rule; ORDER 007 t-stat at Bonferroni K=12 →
  min t 2.64 recorded per lane, informational only, promotion CLOSED):
  - donchian: **4/6 KILL**; XOM KEEP (0.382 vs 0.294, t=0.28), TLT KEEP
    (0.303 vs 0.196, t=0.34). Worst lane SPY (−0.003 vs 0.761, t=−2.42).
  - ema_crossover: **4/6 KILL**; XOM KEEP (0.329 vs 0.294, t=0.11), TLT
    KEEP (0.482 vs 0.196, t=0.90 — the slice's best, still far under the
    2.64 bar).
  - macd: **6/6 KILL** — the slice's cleanest null.
  - supertrend_flip (first equities/ETF run; previously BTC-USD-only):
    **5/6 KILL**; TLT KEEP (0.361 vs 0.196, t=0.52).
  - Honest pattern, same as slice 3 and now confirmed on the full trend
    battery: on the strong-benchmark instruments (SPY/QQQ/TSLA/JPM, B&H
    OOS Sharpe ≥ 0.645) **all 16 lanes KILL**; the 5 KEEPs cluster where
    the benchmark is weak (XOM 0.294, TLT 0.196) — a low bar cleared, not
    an edge. All KEEPs at t = 0.11–0.90 vs 2.64; NOT findings, nothing
    promoted. 24 sweep summaries in `experiments/sweeps/
    r3-trend-new-tickers/`, 24 top-variant ledger rows
    (`variants_tried=12`), index rebuilt via
    `trading_lab.ledger.rebuild_index()`. Commit `ea5f07d`.
- 2026-07-13T03:17Z — verify: `python3 -m pytest -q` → **392 passed**
  (383 on main + 9 new grid tests); pre-flip `bootstrap.py check --strict
  --require-session-log` red ONLY on the designed born-red gate. PR **#90**
  opened READY (non-draft) with the full honest results table and the
  explicit synthesis-scope note; no merge action by this session
  (auto-merge-enabler is the landing path).
- Round-3 delta recorded here, NOT in the synthesis doc (it is scoped to
  slices 1-8 / PRs #81-#88 with pinned totals; the docs convention has no
  addendum mechanism for `reference` docs, so rewriting it would breach
  its own scope statement): after this slice the extended round stands at
  **2,040 registered configs, 190 graded lanes, 0 PROMOTED / 46 KEEP-dev /
  144 KILL**, program cumulative **2,720**.
- 2026-07-13T03:19Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-synthesis.md`,
Status `complete`) landed PR #89 clean — a docs-only slice done right:
born-red first commit, a ground-truth re-aggregation of all 166 graded
units from the merged JSONs BEFORE writing (not from card prose), zero
discrepancies found, one reachability bullet in current-state and no
live-state edits, flip+claim-delete folded into one final commit. Its
verify block reproduces at this session's start: 383 passed on main
matches its claimed count, and its doc's budget ledger is what this
session's PROGRAM_PRIOR_CONFIGS = 2432 is anchored to — the synthesis
paid its way within hours. Its 💡 (graded-unit schema normalization + a
one-code-path aggregation test) is sound and still unimplemented, and
this session sharpens it with a live failure mode: the proposed test
asserts 41/125/166 over the `r3-*` glob, and THIS slice — a legitimate
post-synthesis extension of the round — would have turned it red on
merge. The normalization idea survives; its test needs the round-scope
manifest (this card's 💡) as its denominator instead of a name glob. One
transfer-note: its "what this round does NOT say" section's warning that
KEEPs cluster on weak benchmarks is now independently confirmed by a
fourth family battery on fresh instruments (16/16 KILL where B&H is
strong).

## Close-out

**Done:** on branch `claude/r3-trend-new-tickers` (PR #90) —

1. Pre-declared Round-3 slice-10 grids (`src/trading_lab/sweeps.py`,
   `R3_TREND_NEW_TICKERS_*`: 12 variants × 4 trend families, subsets of
   the published P1/video axes, donchian disjoint from the slice-3 probe)
   + tests (`tests/test_sweeps.py::TestR3TrendNewTickersGrid`, 9 tests).
2. Sweep script `scripts/run_r3_trend_new_tickers.py` (dev rail asserted
   per ticker) + 24 lane summaries under
   `experiments/sweeps/r3-trend-new-tickers/` + 24 top-variant ledger rows
   (`variants_tried=12`; no duplicate B&H baselines) + rebuilt
   `experiments/index.jsonl`.
3. NO new strategy code, NO new data fetches, NO synthesis-doc rewrite
   (delta recorded in this card's work log).
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 392 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-trend-new-tickers.md`
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
the round-scope manifest (this card's 💡 — it unblocks the synthesis
card's aggregation test safely), then the standing stack (graded-unit
schema normalization, sweep-runner extraction — this session hand-copied
the ~250-line sweep script an EIGHTH time — walk-forward warm-history
fix, control arms, provenance sidecar). The 5 KEEPs are dev-candidates
only; any OOS test of them is OWNER-GATED behind a new pre-registered
protocol on post-2026 data, per docs/research-round-2-results.md and
docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
