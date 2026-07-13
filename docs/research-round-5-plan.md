# Research Round 5 — Pre-Registered Plan (Deepen the Top KEEP-dev Candidates)

> **Status:** `binding` — pre-registered Round-5 protocol, committed and
> merged BEFORE any Round-5 run, replay, resample, or outcome exists.
> **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion is CLOSED.**
> Every hypothesis, method, and KEEP/KILL rule below is stated in advance;
> a KEEP anywhere in Round 5 means *dev-candidate only*, never a finding.
> The multiple-testing bar is UNCHANGED from Rounds 2–4
> (`trading_lab.promotion.min_tstat`, ~2.64 at K=12) — no bar-lowering
> anywhere in this round; K only ever rises with variants actually tried.
> Direction for this round: after four rounds of surface expansion and new
> idea classes all closing at 0 promoted, Round 5 DEEPENS the evaluation of
> the strongest surviving dev-candidates instead of widening the search.

## Provenance and scope

Round 4 closed (PRs #100–#105;
[research-round-4-results.md](research-round-4-results.md) closing tally)
with six slices, six honest answers, zero findings. The cumulative program
surface stands at 312 graded lanes — 0 PROMOTED / 64 KEEP-dev / 248 KILL —
with the best t-stat anywhere 1.38 against the 2.64 bar, and the
machine-readable KEEP surface cost-stressed by R4-B down to **42
dev-candidates surviving the 2× tier**
([`experiments/sweeps/r4-cost-sensitivity/summary.json`](../experiments/sweeps/r4-cost-sensitivity/summary.json)).
The round-4 closing tally's own conclusion is this round's mandate:
"Anything further on this surface needs either new data (OWNER-GATED) or a
genuinely different idea class, not more variants." Round 5 accordingly
registers **no new strategy families, no new tickers, no new searches** —
it asks whether the top surviving candidates are ROBUST: stable in their
parameter neighborhood, stable across time splits, stable under resampling,
and honest about selection variance. Round-4 synthesis items 1
(selection-fair / story-pinned configs) and 2 (replay pin) are
pre-registered here as R5-D and as the standing fidelity guard.

## The Round-5 target set (fixed in advance)

The **top 5 KEEP-dev lanes** by baseline informational t-stat among the 42
R4-B 2×-survivors (all values verbatim from committed artifacts —
`experiments/sweeps/r4-cost-sensitivity/summary.json` and the r3 per-lane
JSONs it points at):

| # | Sweep | Strategy | Instrument | TF | baseline t | 2× t | committed top full-period variant |
|---|---|---|---|---|---|---|---|
| 1 | r3-btc-coverage | bollinger_breakout | BTC-USD | daily | 1.378 | 1.315 | period=10, num_std=1.0 |
| 2 | r3-stoch-willr | williams_r_reversion | SLV | daily | 1.043 | 0.936 | period=21, buy_below=−90, sell_above=−30 |
| 3 | r3-trix-ichimoku | ichimoku_trend | META | daily | 0.961 | 0.894 | tenkan=7, kijun=26, senkou_b=44 |
| 4 | r3-meanrev-hourly | stochastic_reversion | META | hourly | 0.908 | 0.748 | k_period=14, buy_below=10, sell_above=80 |
| 5 | r3-trend-new-tickers | ema_crossover | TLT | daily | 0.905 | 0.845 | fast=30, slow=50 |

This set is FROZEN by this document: no swap-ins, no extensions, no
re-ranking after outcomes exist. Each lane's walk-forward geometry
(train 1008 / test 252 bars, committed per-split params) is inherited
unchanged from its r3 source file.

## Standing rails (unchanged, restated for this round)

- **Data**: dev rail only, via `trading_lab.data.load_ohlcv` — holdout
  excluded by default, `data/p5holdout/` never read, `unlock_holdout`
  never passed. Committed caches only; nothing fetched. (The paper lane's
  `load_paper_ohlcv` rail is not used by research rounds and
  `experiments/paper/**` is untouched.)
- **Grading**: the Round-2 KEEP/KILL rule plus the ORDER 007 t-stat
  (informational), `classify_verdict` for KILL-SIG at the mirrored bar.
  Bar `trading_lab.promotion.min_tstat(K)` — never lowered. Promotion is
  CLOSED: no Round-5 verdict can promote anything; KEEP = dev-candidate
  only.
- **Costs baseline**: 5 bps slippage + 1 bp commission per side
  (`config.DEFAULT_SLIPPAGE_BPS` / `DEFAULT_COMMISSION_BPS`).
- **Replay fidelity guard** (R4-B/R4-C precedent, mandatory in every
  slice that replays a committed lane): before any perturbation, each
  lane's baseline replay must reproduce its committed stitched OOS Sharpe
  within 1e-8; an irreproducible lane is recorded SKIPPED with the
  verbatim reason, never silently regraded.
- **Pre-declaration**: any new configs (R5-A neighbors only) are committed
  to `trading_lab.sweeps` with tests BEFORE the slice runs; this document
  pre-registers every hypothesis and decision rule.
- **Honesty**: nulls and KILLs are first-class deliverables. A Round-5
  KILL of a round-3 KEEP is a *demotion of a dev-candidate*, recorded in
  the results doc and the machine-readable rollup.
- **Escalate-to-owner** (used by R5-C only): "escalate" means writing an
  owner-gated proposal document under `docs/proposals/` recommending a
  NEW pre-registered protocol on post-2026 data — it never touches the
  holdout, never schedules an OOS run, never changes a verdict.

---

## R5-A — Parameter-neighborhood stability (falsifies knife-edge configs)

- **Motivation**: every top-5 lane's KEEP rests on a walk-forward that
  searched a 12-variant grid; a real (if weak) effect should degrade
  smoothly in the neighborhood of the chosen configuration, while a grid
  artifact is a knife-edge — neighbors fail.
- **Hypothesis**: for most of the 5 lanes, a majority of the immediate
  parameter neighbors of the committed top full-period variant still beat
  same-window B&H when replayed selection-free.
- **Procedure**: for each target lane, pre-declare in the grid commit the
  ±1-grid-step neighborhood of the committed top full-period variant
  (one parameter perturbed at a time, both directions, clipped to valid
  ranges; ≤ 8 neighbors per lane). Replay each neighbor SELECTION-FREE
  (one fixed config, no training pick) over the lane's exact committed
  walk-forward test windows at baseline costs; compare each neighbor's
  stitched OOS Sharpe to same-window B&H.
- **Data**: dev rail `load_ohlcv` only, the lane's committed
  instrument/timeframe cache.
- **Decision rule** (per lane, pre-registered): the lane KEEPS dev-candidate
  status iff **≥ 50% of its replayed neighbors beat same-window B&H
  stitched OOS Sharpe**; otherwise the lane is DEMOTED to KILL
  (knife-edge). KILL-SIG per `classify_verdict` if any lane-level t crosses
  the mirrored bar. No neighbor can become a candidate itself (that would
  be selection on outcome); neighbors are probes, not entrants.
- **Burden**: ≤ 40 new registered configs (5 lanes × ≤ 8 neighbors),
  counted into the program cumulative in the grid commit.
- **Runtime cap**: ≤ 10 minutes wall-clock for the whole slice.

## R5-B — Time-split stability / leave-one-split-out (falsifies single-window luck)

- **Hypothesis**: the top lanes' edges are not concentrated in a single
  lucky test window — dropping the best single walk-forward split leaves
  the stitched OOS edge positive.
- **Procedure**: for each target lane, replay the committed per-split
  params over the committed test windows (frozen replay, fidelity guard
  first), then recompute the stitched OOS Sharpe delta vs same-window B&H
  **leaving each test split out in turn** (N splits → N leave-one-out
  deltas, N = 5–10 per lane). Report per-split strategy-vs-benchmark
  deltas and the worst-case leave-one-out stitched delta (i.e. with the
  lane's single BEST split removed).
- **Data**: dev rail `load_ohlcv` only; splits of the dev walk-forward
  windows only — the spent holdout is never touched.
- **Decision rule** (per lane, pre-registered): the lane KEEPS dev-candidate
  status iff the stitched OOS Sharpe delta vs B&H **remains > 0 after
  removing the lane's single best test split**; otherwise DEMOTED to KILL
  (single-window luck). Informational t reported at the lane's committed K.
- **Burden**: 0 new registered configs (pure replay/re-aggregation of
  committed choices).
- **Runtime cap**: ≤ 5 minutes wall-clock for the whole slice.

## R5-C — Moving-block bootstrap of the Sharpe-delta t (stability of the headline statistic)

- **Hypothesis**: the top lanes' informational t-stats (0.9–1.38) are
  stable in location under resampling — the point estimates are honest
  summaries, not artifacts of a few return observations — but no lane's
  bootstrap distribution comes close to the promotion bar.
- **Procedure**: for each target lane, take the stitched OOS per-bar
  strategy and benchmark return series from the fidelity-guarded frozen
  replay; moving-block bootstrap (block length 21 bars daily / 63 bars
  hourly, 1,000 resamples, RNG seed fixed to 20260713 in the runner)
  the PAIRED strategy-minus-benchmark series; report the bootstrap
  distribution of the annualized Sharpe delta and of the ORDER 007 t,
  plus `P(delta <= 0)`.
- **Data**: dev rail `load_ohlcv` only (via the replay); no new bars.
- **Decision rule** (per lane, pre-registered):
  - DEMOTED to KILL iff `P(delta <= 0) >= 0.60` (the resampled edge is no
    better than a coin flip, tilted against);
  - ESCALATE-TO-OWNER iff `P(delta <= 0) <= 0.10` — an owner-gated
    proposal doc recommending a new pre-registered protocol on post-2026
    data (per the Standing-rails definition), verdict unchanged
    (KEEP-dev), nothing scheduled or run;
  - otherwise KEEP-dev, unchanged.
- **Burden**: 0 new registered configs (resampling of committed replays).
- **Runtime cap**: ≤ 10 minutes wall-clock for the whole slice.

## R5-D — Selection-fair fixed-config replay (round-4 synthesis item 1)

- **Motivation** (r4-regime + r4-crossasset cards): every searched
  walk-forward mixes signal with grid-selection variance. The
  selection-free counterpart — ONE fixed config replayed over the same
  test windows — measures what survives with zero re-picking.
- **Hypothesis**: for most of the 5 lanes the fixed-config replay of the
  committed top full-period variant still beats same-window B&H, but by
  less than the searched walk-forward did (`selection_gap > 0`).
- **Procedure**: for each target lane, replay the committed top
  full-period variant (table above) selection-free over the lane's exact
  committed walk-forward test windows at baseline costs; report its
  stitched OOS Sharpe vs same-window B&H, and
  `selection_gap = searched_stitched_sharpe − fixed_stitched_sharpe`
  machine-readably per lane.
- **Data**: dev rail `load_ohlcv` only.
- **Decision rule** (per lane, pre-registered): the lane KEEPS dev-candidate
  status iff the fixed-config replay's stitched OOS Sharpe **beats
  same-window B&H**; otherwise DEMOTED to KILL (the edge exists only
  through in-window re-selection). `selection_gap` itself is
  informational — no threshold on it is registered.
- **Burden**: 0 new registered configs (the fixed config is the lane's
  already-committed variant; R5-A's neighbor grid commit covers any
  overlap).
- **Runtime cap**: ≤ 5 minutes wall-clock for the whole slice.

---

## Round-level aggregation (pre-registered)

A target lane exits Round 5 as **KEEP-dev** only if it keeps dev-candidate
status under **ALL FOUR** verdict-bearing slices (R5-A, R5-B, R5-C, R5-D);
any single demotion is a KILL for the lane (recorded with the slice that
killed it). The R5-C escalate branch changes no verdict. Expected honest
outcome given four rounds of nulls: some or all of the top 5 demote —
that pruning IS the deliverable. Results land slice-by-slice in
`docs/research-round-5-results.md` (created by the first results slice,
R4 convention).

## What round 5 will NOT do

- **No holdout access** — the holdout is SPENT; `data/p5holdout/` is never
  read and `unlock_holdout` is never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched; no paper
  grading run by research sessions.
- **No new searches** — no new strategy families, tickers, timeframes, or
  grid searches; R5-A's neighbors are selection-free probes, never
  entrants, and no Round-5 result selects a new configuration.
- **No OOS validation claims** — genuine OOS validation of any KEEP-dev
  survivor stays OWNER-GATED behind a new pre-registered protocol on
  post-2026 data; the R5-C escalate branch only *proposes*, never runs.
- **No bar-lowering** — `min_tstat` at the honestly-counted K, always.
- **No new data fetching** beyond the committed caches.
- **No broker/order/exchange-write code, no live API configuration** —
  research-only, per CONSTITUTION.md.
