# 2026-07-13 — R3 slice 11: mean-reversion families × new tickers (dev-only)

> **Status:** `complete` — the five existing mean-reversion families
> (rsi_mean_reversion, bollinger_reversion, pullback, stochastic_reversion,
> williams_r_reversion) swept with pre-declared 12-variant sub-grids of
> their published axes over the six PR #83 instruments (SPY, QQQ, TSLA,
> JPM, XOM, TLT) on the standard dev rail; NO new strategy code. Honest
> outcome **0 PROMOTED / 3 KEEP (dev-candidate only) / 27 KILL** of 30
> lanes — three families are sweep-wide nulls, and one lane (TSLA
> rsi_mean_reversion, t=−3.01) is significantly WORSE than B&H at the
> promotion bar. This slice lands AFTER the Round-3 synthesis (PR #89,
> slices 1-8) and extends the round; the synthesis doc is NOT rewritten —
> its delta is recorded here. This card was born red (`in-progress`) and
> flipped `complete` as the deliberate last content change before push;
> the claim file is deleted in this same commit.

📊 Model: fable-5 · r3-meanrev-new-tickers lane (worker session) · start 2026-07-13T03:23Z

💡 **Session idea:** the KEEP/KILL rule has no verdict class for
SIGNIFICANT UNDERPERFORMANCE, and this session produced the program's
clearest instance of the gap: TSLA rsi_mean_reversion stitched OOS Sharpe
−0.192 vs B&H 0.760 grades t = −3.01 — it crosses the very Bonferroni bar
(|t| ≥ 2.64) a winner would have needed, in the NEGATIVE direction — yet
the record collapses it into the same flat "KILL" bucket as TSLA
stochastic_reversion at t = −0.01 (indistinguishable from benchmark).
Those are different scientific results: one is "no evidence either way",
the other is "robust evidence this family reliably destroys value vs B&H
on this instrument after costs". Adopt a three-way verdict:
KEEP / KILL / KILL-SIG, where KILL-SIG iff `tstat ≤ −min_tstat` from the
already-computed `promotion_grade` (zero new arithmetic — the fields are
in every sweep JSON today; slice 10's SPY donchian t=−2.42 just misses,
this lane's TSLA rsi clears it). Payoff: (a) exclusion lists become
evidence-graded rather than anecdotal; (b) honest-nulls summaries stop
flattening "noise" and "reliably harmful" together; (c) any future
"invert the loser" temptation meets a pre-registered record of which
losers were significant. Machine-checkable: verdict recomputation from
`promotion_grade.tstat` + `min_tstat` per sweep JSON; the standing-stack
ideas (sweep-runner extraction, round-scope manifest, schema
normalization, verdicts index, control arms, provenance sidecar,
warm-history fix, cost-drag lines) grade or aggregate records — none adds
a verdict class.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 3 (PR #83) added the six new instrument caches but probed
them with only small 6-variant grids of three families; slice 10 (PR #90)
completed the TREND-family coverage of that surface. This slice does the
same for the MEAN-REVERSION side: rsi_mean_reversion, bollinger_reversion,
pullback, stochastic_reversion and williams_r_reversion with 12
pre-declared variants each — every grid point a subset of the family's
existing published axes (P1 mean-reversion axes; the r3-stoch-willr axes),
no new parameter territory, no new strategy code. Overlap honesty note up
front: slice 3 already probed `rsi_mean_reversion` on these six
instruments with a 6-variant grid (period {2,5,14} × oversold {30} ×
overbought {60,70}); this slice's rsi sub-grid is deliberately DISJOINT
from that probe (oversold ∈ {10, 20}, never 30) so no config is registered
twice — the relation is pinned by a unit test, following slice 10's
donchian precedent. Backtests run on the default `load_ohlcv` dev rail
(holdout ≥ 2025-01-09 excluded; the holdout is SPENT). Promotion is CLOSED
post-holdout: mostly-KILL is the expected outcome and is recorded as a
first-class result.

## Work log

- 2026-07-13T03:23Z — clone hard-synced to origin/main HEAD `6cc5938`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 11, mean-reversion families × new tickers). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-meanrev-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-meanrev-new-tickers.md` are the born-red
  FIRST commit (`e021118`), pushed before any build work.
- 2026-07-13T03:25Z — grids declared in `trading_lab.sweeps` BEFORE the
  sweep ran (`R3_MEANREV_NEW_TICKERS_*`: rsi_mean_reversion period
  {2,5,14} × oversold {10,20} × overbought {60,70}, DISJOINT from the
  slice-3 probe; bollinger_reversion lookback {10,20,30} × z_entry
  {1.5,2.0} × z_exit {0.0,0.5} — the r3-meanrev-hourly daily-twin subset
  reused verbatim; pullback entry_lookback {3,5} × exit_len {5,10} ×
  trend_len {0,100,200} with the trend_len=0 unfiltered control arm
  committed; stochastic_reversion and williams_r_reversion reuse the
  r3-stoch-willr grids VERBATIM (already exactly 12; d_period stays frozen
  at 3) — 12 variants/family, every point a member of the family's
  published grid, subset + disjointness + control-arm relations pinned in
  `tests/test_sweeps.py::TestR3MeanrevNewTickersGrid`, 10 tests).
  Instruments = the slice-3 set reused verbatim (same tuple object);
  `config.UNIVERSE` untouched. Commit `7b5f3bd`.
- 2026-07-13T03:27Z — sweep run (`scripts/run_r3_meanrev_new_tickers.py`,
  mirrors `scripts/run_r3_trend_new_tickers.py`: `load_ohlcv` default rail
  with `data_end ≤ 2025-01-08` ASSERTED per ticker — all six lanes end
  2025-01-08 exactly; costs 5 bps + 1 bp per side; walk-forward 1008/252
  contiguous stitched OOS vs same-window same-cost B&H; 360 registered
  configs, program cumulative 3080 = 2720 prior + 360; NO new B&H ledger
  rows — the six baselines are on the ledger from slice 3). Honest
  verdicts (Round-2 KEEP/KILL rule; ORDER 007 t-stat at Bonferroni K=12 →
  min t 2.64 recorded per lane, informational only, promotion CLOSED):
  - rsi_mean_reversion: **6/6 KILL** — including TSLA at t=−3.01,
    SIGNIFICANTLY worse than B&H at the promotion bar (see this card's 💡),
    and TLT at t=−2.15.
  - bollinger_reversion: **6/6 KILL** — best lane JPM (0.478 vs 0.645,
    t=−0.53).
  - pullback: **4/6 KILL**; QQQ KEEP (0.934 vs 0.871, t=0.20), TLT KEEP
    (0.472 vs 0.196, t=0.87 — the slice's best, still far under 2.64).
  - stochastic_reversion: **6/6 KILL** — two hairline losses (TSLA
    t=−0.01, JPM t=−0.13) resolve KILL per the ties/ambiguity rule.
  - williams_r_reversion: **5/6 KILL**; JPM KEEP (0.670 vs 0.645, t=0.08).
  - Honest pattern: mean reversion is even weaker on these instruments
    than the trend battery was (slice 10: 5/24 KEEP; here 3/30). Three
    families are sweep-wide nulls. Unlike slice 10 the KEEPs do NOT purely
    cluster on weak benchmarks (QQQ pullback and JPM williams clear strong
    benchmarks — but at t=0.20/0.08, carrying no evidential weight); TLT
    pullback is the familiar weak-benchmark clear. All KEEPs at
    t = 0.08–0.87 vs 2.64; NOT findings, nothing promoted. 30 sweep
    summaries in `experiments/sweeps/r3-meanrev-new-tickers/`, 30
    top-variant ledger rows (`variants_tried=12`), index rebuilt via
    `trading_lab.ledger.rebuild_index()`. Commit `cbc0e8c`.
- 2026-07-13T03:28Z — verify: `python3 -m pytest -q` → **402 passed**
  (392 on main + 10 new grid tests); pre-flip `bootstrap.py check --strict
  --require-session-log` red ONLY on the designed born-red gate. PR **#91**
  opened READY (non-draft) with the full honest results table and the
  explicit synthesis-scope note; no merge action by this session
  (auto-merge-enabler is the landing path).
- Round-3 delta recorded here, NOT in the synthesis doc (it is scoped to
  slices 1-8 / PRs #81-#88 with pinned totals; the docs convention has no
  addendum mechanism for `reference` docs, so rewriting it would breach
  its own scope statement): after this slice the extended round stands at
  **2,400 registered configs, 220 graded lanes, 0 PROMOTED / 49 KEEP-dev /
  171 KILL**, program cumulative **3,080**.
- 2026-07-13T03:30Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-trend-new-tickers.md`,
Status `complete`) landed PR #90 clean and is the direct template of this
session: born-red first commit, grids pre-declared with subset +
disjointness tests, dev rail asserted per ticker, no duplicate B&H rows,
synthesis doc left untouched with the extended-round delta in the card,
flip+claim-delete in one final commit. Its verify block reproduces at this
session's start: 392 passed on main matches its claimed count, and its
"program cumulative 2,720" is what this session's
`PROGRAM_PRIOR_CONFIGS = 2720` is anchored to. Two sharpenings from
building on it: (1) its 💡 (round-scope manifest) gains force with THIS
slice — the extended-round totals now live only as arithmetic across TWO
cards' work logs (2,040 → 2,400 configs), so any consumer must do card
archaeology to know what "Round 3 extended" means; the manifest with
`addendum` entries is now the difference between one lookup and N-card
forensics, and it remains unimplemented. (2) Its honest-pattern claim
("KEEPs cluster where the benchmark is weak — all 16 strong-benchmark
lanes KILL") transferred imperfectly to the mean-reversion battery: 2 of
this slice's 3 KEEPs sit on strong-benchmark lanes (QQQ 0.871, JPM
0.645) — though at t ≤ 0.20 the pattern-break is itself noise, which is
exactly why the card-level pattern language needs the significance
qualifier it already carries. No defect found in its work; its
supertrend_flip honesty-note convention (`family_status` in every sweep
JSON) is reused here for the rsi probe-overlap note.

## Close-out

**Done:** on branch `claude/r3-meanrev-new-tickers` (PR #91) —

1. Pre-declared Round-3 slice-11 grids (`src/trading_lab/sweeps.py`,
   `R3_MEANREV_NEW_TICKERS_*`: 12 variants × 5 mean-reversion families,
   subsets of the published P1/r3-stoch-willr axes, rsi disjoint from the
   slice-3 probe, pullback control arm committed) + tests
   (`tests/test_sweeps.py::TestR3MeanrevNewTickersGrid`, 10 tests).
2. Sweep script `scripts/run_r3_meanrev_new_tickers.py` (dev rail asserted
   per ticker) + 30 lane summaries under
   `experiments/sweeps/r3-meanrev-new-tickers/` + 30 top-variant ledger
   rows (`variants_tried=12`; no duplicate B&H baselines) + rebuilt
   `experiments/index.jsonl`.
3. NO new strategy code, NO new data fetches, NO synthesis-doc rewrite
   (delta recorded in this card's work log).
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 402 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-meanrev-new-tickers.md`
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
the KILL-SIG verdict class (this card's 💡 — zero new arithmetic, fields
already in every sweep JSON), the round-scope manifest (slice 10's 💡,
strengthened by this second post-synthesis extension), then the standing
stack (sweep-runner extraction — this session hand-copied the ~250-line
sweep script a NINTH time — graded-unit schema normalization,
walk-forward warm-history fix, control arms, provenance sidecar). The 3
KEEPs are dev-candidates only; any OOS test of them is OWNER-GATED behind
a new pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md and docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
