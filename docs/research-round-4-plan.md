# Research Round 4 — Pre-Registered Plan (Six New Idea Classes)

> **Status:** `binding` — pre-registered Round-4 protocol, committed and
> merged BEFORE any Round-4 sweep, backtest, re-grade, or outcome exists.
> **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion is CLOSED.**
> Every hypothesis, method, and KEEP/KILL rule below is stated in advance;
> a KEEP anywhere in Round 4 means *dev-candidate only*, never a finding.
> The multiple-testing bar is UNCHANGED from Rounds 2–3 (Bonferroni-style
> min t-stat via `trading_lab.promotion.grade_promotion`, ~2.64 at K=12) —
> no bar-lowering anywhere in this round; the one slice with a larger K
> (R4-F) states K explicitly and its bar RISES accordingly. Owner mandate:
> ORDER 012 (2026-07-13 night-run direct order, "continue with some new
> ideas") — this is the generative rung after Round 3 (PRs #81–#95).

## Provenance and scope

Round 3 expanded the backtest *surface* (new families, tickers, timeframes;
PRs #81–#88 synthesized in
[research-round-3-results.md](research-round-3-results.md), extended by
PRs #90–#95) and closed with an honest **0 PROMOTED / mostly-KILL**
aggregate — after the hourly-matrix completion (PR #95) the extended round
stands at 312 graded lanes, 0 PROMOTED / 64 KEEP-dev / 248 KILL, and the
best t-stat anywhere in the round is ~1.04 against the 2.64 bar. Round 4
changes the *kind* of question: instead of more families × tickers, it
tests six new **idea classes** — new verdict semantics, robustness
re-grades, and composition/conditioning of existing survivors. Round 2's
lesson is restored at round level: this document is the single
pre-registration, merged before any outcome exists (cf.
[research-round-2.md](research-round-2.md)).

## Standing rails (unchanged, restated for this round)

- **Data**: dev rail only, via `trading_lab.data.load_ohlcv` — every lane's
  `data_end < HOLDOUT_START`. The holdout is SPENT; `data/p5holdout/` is
  never read; `unlock_holdout` is never passed. Committed caches only —
  no new data fetching beyond the committed caches unless a slice
  pre-registers the fetch in its own grid commit before running.
- **Grading**: the Round-2 KEEP/KILL rule (stitched walk-forward OOS vs
  buy-and-hold benchmark, net of costs) plus the ORDER 007 t-stat,
  informational only. Bar: `trading_lab.promotion.min_tstat(K)` — 2.64 at
  the standard K=12; **never lowered**. Promotion is CLOSED: no Round-4
  verdict can promote anything; KEEP = dev-candidate only.
- **Costs baseline**: 5 bps slippage + 1 bp commission per side
  (`config.DEFAULT_SLIPPAGE_BPS` / `DEFAULT_COMMISSION_BPS`), except where
  R4-B pre-registers stressed tiers.
- **Pre-declaration**: each slice commits its grids/configs to
  `trading_lab.sweeps` (with tests) before its sweep runs, exactly as in
  Round 3; this document pre-registers the hypotheses and kill criteria.
- **Honesty**: nulls and KILLs are first-class deliverables and are
  recorded with the same care as KEEPs.

---

## R4-A — KILL-SIG verdict class (retroactive, non-destructive)

- **Motivation** (round-3 result): TSLA `rsi_mean_reversion`'s stitched OOS
  t = **−3.01** (PR #91 card) crosses the 2.64 bar *in the negative
  direction* — the grading vocabulary has no word for "significantly
  harmful", so today that lane is just one KILL among 248. SPY `donchian`
  (t = −2.42, PR #90/#91 cards) just misses the same negative bar. Both
  fields (`tstat`, `min_tstat`) are already computed in every sweep summary
  JSON — this class costs **zero new arithmetic**.
- **Hypothesis**: a small set (1–3) of significantly-harmful lanes exists
  among the round-3 sweeps; almost all KILLs are noise-level, not
  significant harm.
- **Method sketch**: define a third verdict **KILL-SIG** and re-grade all
  merged r3 sweep summaries (`experiments/sweeps/r3-*/`) retroactively as a
  **flagged, non-destructive report** — original JSONs byte-untouched, the
  re-grade emits a separate report artifact + doc table.
- **Pre-registered rule**: KILL-SIG iff `tstat ≤ −min_tstat(K)` at the
  lane's own recorded K (−2.64 at K=12) — the same bar, mirrored. A
  KILL-SIG is explicitly recorded as **evidence AGAINST the lane** and
  against the "invert the loser" temptation: a significantly negative
  dev-rail t-stat is a reason to stop, not a long/short signal (the
  inversion would be a new untested strategy selected on the very data
  that graded it).
- **Expected cost**: 0 new configs, 0 backtests — one re-grade pass over
  ~312 existing summary JSONs + report.

## R4-B — Execution-cost sensitivity re-grade of round-3 KEEPs

- **Motivation** (round-3 result): the synthesis doc shows KEEPs cluster on
  weak benchmarks with small margins (of the 41 slice-1–8
  single-instrument KEEPs, 11 sit on the four weakest benchmarks), and the
  PR #95 card measured the same pattern across the completed hourly matrix
  (12/32 KEEPs in the weakest benchmark-Sharpe tercile vs 3/30 in the
  strongest). Small margins over weak benchmarks are exactly what realistic
  execution costs erase.
- **Hypothesis**: most or all round-3 KEEP-dev lanes flip to KILL at
  realistic-pessimistic costs — a valuable negative that prunes the
  dev-candidate list honestly.
- **Method sketch**: re-run the KEEP/KILL grading of **all round-3 KEEP-dev
  lanes** (64 after PR #95) at two stressed cost tiers — **2×** baseline
  (10 bps slippage + 2 bp commission per side) and **4×** baseline (20 bps
  + 4 bp) — same rail, same walk-forward windows, same chosen top variant
  per lane (no re-search: stressing costs must not become a second
  selection pass).
- **Pre-registered kill criterion (per lane, per tier)**: KILL at that tier
  iff stitched OOS Sharpe ≤ benchmark B&H Sharpe **or** ≤ 0. A lane keeps
  its dev-candidate status only if it survives the 2× tier; the 4× tier is
  reported as a robustness gradient.
- **Expected cost**: 0 new configs; 64 lanes × 2 tiers = 128 re-runs of
  already-selected variants.

## R4-C — Ensemble / committee of survivors

- **Motivation** (round-3 result): several instruments carry ≥2 KEEP-dev
  families from different logic classes (the synthesis KEEP table spans
  trend, reversion, and breakout families on the same tickers, e.g. the
  repeated META and GOOGL KEEPs across PRs #84–#95). Round 3 never asked
  whether survivors *combine*.
- **Hypothesis**: an equal-weight committee raises Sharpe modestly through
  diversification, but **no committee clears t ≥ 2.64** — the expected
  outcome is a small, honest, non-significant improvement.
- **Method sketch**: per instrument with ≥2 KEEP-dev families, form an
  equal-weight signal committee — position = mean of member positions —
  and grade it vs (a) the best single member and (b) B&H, on the same
  rail, costs, and walk-forward windows as the members. Members are frozen
  as the lanes' already-committed top variants (no re-search inside the
  committee).
- **Pre-registered rule**: KEEP (dev-candidate only) iff the committee
  beats **BOTH** the best single member and the benchmark on stitched OOS
  Sharpe; otherwise KILL. t-stat reported informationally at the slice's
  declared K.
- **Expected cost**: one committee lane per qualifying instrument
  (single-digit lanes expected); 0 new strategy families.

## R4-D — Regime-conditional allocation (with mandatory control arm)

- **Motivation** (round-3 result): PR #92 (gated new-ticker slice) found
  the vol gate's `vol_filter=False` **control arm beat the gated arm on
  all six instruments** — conditioning subtracted value everywhere it was
  tried. Round 4 tests a different conditioning axis (trend strength, not
  volatility) with the control-arm discipline now mandatory.
- **Hypothesis**: **null expected** — regime-conditional family switching
  does not beat its unconditional control after costs.
- **Method sketch**: condition family choice on trend-strength buckets
  (e.g. ADX terciles or |200d SMA slope| terciles, thresholds fixed in the
  grid commit): trend family active in the strong-trend bucket, flat or
  reversion family in the weak bucket. **Mandatory unconditional control
  arm** (the same components, no gate) committed in the same grid, and a
  `control_arm_delta` reported per lane.
- **Pre-registered kill criterion**: KILL iff conditional stitched OOS
  Sharpe ≤ the unconditional control's; a KEEP additionally requires
  beating B&H. Null outcome is a first-class result.
- **Expected cost**: small pre-declared grid (≈12 variants per lane,
  standard K=12) over a handful of instruments where both component
  families exist as committed variants.

## R4-E — Cross-asset lead-lag filter (with ungated control arm)

- **Motivation** (round-3 result): the round-3 universe expansion committed
  TLT, XOM, and GLD caches (PRs #90–#92) but used them only as standalone
  lanes; cross-asset information (bond momentum as an equity risk gate) is
  an untested idea class, and the round-3 gating lesson (PR #92's control
  arms winning 6/6) predicts failure — worth testing precisely because the
  prior is now informed.
- **Hypothesis**: **null expected** — a TLT-momentum exposure gate on
  SPY/QQQ trend lanes does not beat its ungated control after costs.
- **Method sketch**: gate the exposure of existing SPY/QQQ trend-family
  variants on TLT momentum sign/strength (plus XOM and GLD gate variants
  as pre-declared alternates), with the **ungated control arm** committed
  in the same grid; committed daily caches only.
- **Pre-registered kill criterion**: same control-arm rule as R4-D — KILL
  iff gated ≤ ungated control on stitched OOS Sharpe; KEEP additionally
  requires beating B&H. `control_arm_delta` reported per lane.
- **Expected cost**: ≈12-variant pre-declared grid (K=12) × 2 instruments
  (SPY, QQQ); no new data fetching (all three gate tickers already
  committed).

## R4-F — Seasonality / day-of-week (explicit larger K, bar rises)

- **Motivation** (round-3 result): Round 3 varied families, parameters,
  tickers, and timeframes but never *calendar* structure; day-of-week is
  the cheapest calendar hypothesis and a classic multiple-testing trap —
  which makes it the right stress test of the round's correction
  discipline.
- **Hypothesis**: **null after correction** — no day×ticker long rule
  clears the Bonferroni bar at the honestly-counted K.
- **Method sketch**: long-on-selected-weekdays rules swept across the
  **15 committed daily tickers**; the base sweep tests each single weekday
  per ticker. **K counts ALL day×ticker combos tested**: 5 weekdays × 15
  tickers = **K = 75**, so the bar RISES to `min_tstat(75)` ≈ **3.21**
  (vs 2.64 at K=12). Any multi-day subsets, if swept, are added to K in
  the grid commit before running — K is never counted down.
- **Pre-registered rule**: KEEP (dev-candidate only) iff a combo clears
  BOTH the Round-2 benchmark rule and t ≥ 3.21 at K=75; everything else
  KILL (or KILL-SIG at t ≤ −3.21 if R4-A has landed).
- **Expected cost**: 75 cheap configs (single-signal rules, no parameter
  search inside a combo), one slice.

---

## Deferred infra (opportunistic, not gating)

Two standing infra candidates may be picked up opportunistically by any
Round-4 slice without further pre-registration, since neither touches
grading semantics: (1) the **round-scope manifest** (`ROUNDS.json`) pinning
each round's slices/PRs/config counts machine-readably, and (2)
**sweep-runner extraction** — the r3 sweep scripts are ~13 near-identical
hand copies; extracting the shared runner is pure refactor. Neither blocks
any R4 slice.

## What round 4 will NOT do

- **No holdout access** — the holdout is SPENT; `data/p5holdout/` is never
  read and `unlock_holdout` is never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched; no paper
  grading run by research sessions.
- **No OOS validation claims** — genuine OOS validation of any KEEP-dev
  survivor is OWNER-GATED behind a new pre-registered protocol on
  post-2026 data; nothing in Round 4 schedules or performs it.
- **No bar-lowering** — `min_tstat` at the honestly-counted K, per slice,
  always; K only ever rises with the variants actually tried.
- **No new data fetching** beyond the committed caches, unless a slice
  pre-registers the fetch before running.
- **No broker/order/exchange-write code, no live API configuration** —
  research-only, per CONSTITUTION.md.
