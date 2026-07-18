# Research Round 7D — Pre-Registered Plan (Cross-Sectional Drawdown Ranking on XSEC-14, PLAN ONLY)

> **Status:** `binding` — pre-registered Round-7D protocol, committed and
> merged BEFORE any Round-7D sweep, backtest, replay, grid code, or outcome
> exists. **PLAN ONLY: this document's own session runs NOTHING — executing
> Round 7D (including committing the grid + tests below to
> `trading_lab.sweeps`) is a FUTURE session's separately claimed slice**
> (plan-before-outcome, the ORDER 014 round-6 precedent: plan PR then run
> PR, two claims). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT
> and promotion is CLOSED.** Every hypothesis, method, and KEEP/KILL rule
> below is stated in advance; a KEEP anywhere in Round 7D means
> *dev-candidate only*, never a finding. The multiple-testing bar is
> UNCHANGED from Rounds 2–7 (`trading_lab.promotion.min_tstat`, ≈2.39 at
> the xsec K=6 convention) — no bar-lowering anywhere in this round; K only
> ever rises with variants actually tried.

## Provenance, scope, and the direction pick (justified here)

Round 7C closed (PR #144; [research-round-7c-results.md](research-round-7c-results.md))
at 1 KEEP-dev / 11 KILL / 3 KILL-SIG of 15 lanes, 0 promoted, best
informational t 0.22 (TLT `washout_recovery`) vs the 2.638 bar, program
cumulative **5,595 registered configs — 0 promoted anywhere**. R7C graded the
program's first INTERACTION family (`washout_recovery`, drawdown ×
high-proximity conjunction) and nulled it: the conjunction added no
benchmark-beating edge and was value-destroying on high-drift names.

This plan picks **the first cross-sectional PORTFOLIO family that ranks the
basket on DRAWDOWN DEPTH** (overnight menu proposal #02): `xsec_drawdown` on the
committed XSEC-14 basket. It is the same lowest-cost option-2 entry Round 7 used
— a genuinely new idea family on the COMMITTED daily caches only, reading only
price columns already served by the dev rail, no owner action, no fetch, compute
in the Round-3 xsec range (the R3 portfolio slice ran 12 configs in seconds).
Menu #02 asks a question the two burned cross-sectional lanes each leave open:
the program's only consistently-observed effect is drawdown (retrospective §f),
yet no cross-sectional lane has ever ranked the cross-section on drawdown STATE
— both `xsec_momentum` and `xsec_reversal` rank on trailing point-to-point
RETURN. Does drawdown depth carry cross-sectional information where single-name
drawdown lanes (R7-A) mostly nulled?

Honest registered prior, carried from Round 3 and Round 7 verbatim in effect:
`xsec_reversal` (ranking on trailing LOSERS — the closest thing to "buy the
beaten-down names") went **6/6 KILL** on exactly this basket in Round 3, every
config 0.28–0.68 Sharpe below the equal-weight benchmark (cite
[research-round-3-results.md](research-round-3-results.md)), and single-name
drawdown reversion mostly nulled in R7-A. The expected Round-7D outcome is more
honest nulls — KILL on most/all 6 lanes — and that is a complete deliverable.

Round 7D registers **one genuinely new family on the COMMITTED daily caches
only** (`xsec_drawdown`), reading only the price column already served by the
dev rail, structurally distinct from all burned families and from its own two
nearest neighbors (`xsec_momentum`, `xsec_reversal`). Adjacency is declared in
advance in the slice below (nearest burned neighbors named, with the exact
structural difference stated) so "new family vs variant" cannot be re-litigated
after outcomes.

Directions considered and NOT registered, recorded for honesty: any hourly
slice (Round 6 re-confirmed hourly as a KILL amplifier at baseline costs; the
marginal evidence per config is the program's worst); any single-instrument
drawdown family (R7-A burned that class on the daily surface); a long/short
version of the ranking (this library is long/flat everywhere — the short leg is
out of scope, exactly as `xsec_reversal` declared); anything needing a fetch
(owner-gated); and BTC-USD in the basket (deliberately excluded to keep the
aligned common index on exchange trading days, the standing XSEC-14 rule).

## The three standing requirements (rails for this round, restated as binding)

1. **Selection-fair gate on every lane** ([selection-fair-gate.md](selection-fair-gate.md),
   which stamps the standing decision; PR #111): every Round-7D runner runs
   `trading_lab.selection_gate.run_selection_gate` (fidelity guard armed
   with the lane's recorded searched Sharpe) and folds the result through
   `apply_gate` BEFORE writing any verdict; the full gate result block is
   recorded in the lane JSON. A would-be KEEP that fails the gate is KILL
   the day it is minted.
2. **R5-D fixed-config row in every searched-arm comparison**
   ([research-round-5-results.md](research-round-5-results.md) closing
   tally item 4; standing since Round 6): every lane summary reports
   `fixed_sharpe`, `bench_sharpe`, `searched_sharpe`, and
   `selection_gap = searched − fixed` (informational, no registered
   threshold). As in Rounds 6–7, the gate's own result block satisfies this
   row for every graded lane — the gate runs on EVERY lane, not only
   would-be KEEPs.
3. **reason_class rollup (standing round-level requirement since Round 7)**
   (PR #121; [selection-fair-gate.md](selection-fair-gate.md)
   § reason_class): the Round-7D results rollup MUST tabulate
   `reason_class` counts across all lanes and treat ANY nonzero
   `selection_gate.UNGRADEABLE_CLASSES` share as an **infrastructure
   alarm** reported in the results doc and on the heartbeat — never as
   strategy evidence.

## Standing rails (unchanged, restated)

- **Data**: dev rail only via `trading_lab.data.load_ohlcv` — holdout
  excluded, `data/p5holdout/` never read, `unlock_holdout` never passed;
  committed caches only, nothing fetched; `experiments/paper/**`
  untouched. The panel is aligned on its common date index via
  `trading_lab.data.align_common_index` before any weight is computed.
- **Grading**: Round-2 KEEP/KILL rule (KEEP as dev-candidate iff stitched
  portfolio-walk-forward OOS Sharpe > same-window equal-weight basket B&H
  benchmark Sharpe AND > 0; ties/ambiguity KILL) + ORDER 007 informational t
  + `classify_verdict` KILL-SIG at the mirrored bar + the selection-fair
  gate. Bar `min_tstat(K)` at the honestly-counted K — never lowered.
  Promotion CLOSED: no Round-7D verdict can promote anything.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults).
- **Walk-forward geometry**: train 1008 / test 252 daily bars, contiguous
  test windows, stitched via `trading_lab.portfolio.portfolio_walk_forward`,
  exactly as Rounds 2–7. The ledger run is keyed `instrument="XSEC-14"` (the
  basket is the unit, not any single ticker).
- **Pre-declaration (sequencing for the run session)**: the run session's
  FIRST code commit adds the grid below to `trading_lab.sweeps` WITH
  pinning tests in `tests/test_sweeps.py`, and only then runs — grid in
  code before any sweep, exactly the Rounds 6–7 mechanics. This plan doc is
  the binding source the tests pin against.
- **Honesty**: nulls and KILLs are first-class deliverables.
- **Runtime caps, no silent truncation**: cap below; a slice
  that would exceed its cap STOPS, records the partial state and the
  verbatim overrun, and reports CAP-HIT (re-registration required) —
  silent truncation or grid-narrowing mid-run is forbidden.

---

## R7-D — Cross-sectional drawdown-ranking family (`xsec_drawdown` × XSEC-14 basket)

- **Motivation**: drawdown is the program's only consistently-observed
  effect (retrospective §f), yet the cross-sectional PORTFOLIO lane has only
  ever ranked the basket on trailing point-to-point RETURN
  (`xsec_momentum` long winners, `xsec_reversal` long losers). No lane has
  ranked on drawdown STATE — how deep each name sits below its own trailing
  peak. Menu #02 asks whether ranking the cross-section by drawdown depth and
  holding the deepest names carries information the return-ranked lanes lack,
  where single-name drawdown reversion (R7-A) mostly nulled.
- **Family** (PORTFOLIO family — a
  `generate_weights(closes, **params) -> pd.DataFrame` callable registered in
  `PORTFOLIO_STRATEGIES`, NOT in the single-instrument `STRATEGIES` dict;
  implementation + causality tests in the run session's first commit).
  Signal — mirrors `xsec_reversal.generate_weights` EXACTLY but ranks on
  drawdown depth instead of trailing return:
  - `depth[t, i] = closes[t, i] / max(closes[t−L+1 … t, i]) − 1` per
    instrument `i` (trailing `L`-bar close peak, INCLUDES bar `t`;
    `depth <= 0`, deepest = most negative).
  - At each rebalance bar (iloc `L`, `L+rebalance_every`, …, anchored at the
    panel's first bar), rank the basket ASCENDING by `depth` (most-negative =
    deepest drawdown first; tie-break lowest column index = alphabetical for
    the registered universe, via `np.lexsort((tie_break, depth_row))`), set
    the deepest `k` instruments to equal weight `1/k` and the rest to 0; all
    OTHER bars are all-NaN rows (hold the drifted book). Cash (all-zero /
    flat, 0%) before the first decision at iloc `L`. Long-only, no leverage,
    no shorting; weights sum to 1 at each decision bar.
  - Causal + prefix-invariant: the rolling max at bar `t` uses closes ≤ `t`
    only, and the rebalance schedule is anchored at the frame's iloc 0 —
    positions are prefix-invariant, so
    `portfolio_walk_forward`'s `weight_fn(closes.iloc[:test_end]).iloc[test_start:test_end]`
    slicing preserves the schedule (the xsec_momentum / xsec_reversal
    contract). The engine delays execution to bar `t+1`'s open.
- **Declared adjacency (nearest burned neighbors)**: `xsec_momentum` and
  `xsec_reversal` — both rank the cross-section on trailing point-to-point
  RETURN (`close/close.shift(N) − 1`) and hold the equal-weight top-`k`
  (winners) or bottom-`k` (losers) respectively. Structural difference:
  `xsec_drawdown` ranks on DEPTH-FROM-TRAILING-PEAK
  (`close/rolling(L).max() − 1`) — a drawdown STATE, not a point-to-point
  return. A name can have a strongly negative trailing return yet a shallow
  drawdown (it fell early in the window then recovered toward its peak), and a
  name can have a mild trailing return yet a deep drawdown (it topped mid-window
  and is still below that peak); the two ranking keys are not monotone
  transforms of each other, so `xsec_drawdown` is not reducible to either
  return-ranked neighbor. No cross-sectional lane has ranked on drawdown depth.
  This tests whether the program's only consistently-observed effect (drawdown,
  retrospective §f) carries cross-sectional information where single-name
  drawdown lanes (R7-A) mostly nulled.
- **Hypothesis (registered null)**: cross-sectional drawdown ranking does NOT
  beat the equal-weight basket buy-and-hold net of costs — expect KILL on
  most/all 6 lanes. `xsec_reversal` (ranking on trailing losers, the closest
  return-ranked analogue to "buy the beaten-down names") went **6/6 KILL** on
  this basket, every config 0.28–0.68 Sharpe below the equal-weight benchmark
  (cite [research-round-3-results.md](research-round-3-results.md)), and
  single-name drawdown reversion mostly nulled in R7-A. **Mirror expectation
  declared**: if drawdown carried cross-sectional information, the
  deeper-concentration lanes (`k = 2`, longer `L`) should out-grade the
  shallower ones (`k = 3`, shorter `L`) — the registered expectation is that
  no such gradient clears the unchanged xsec K=6 bar (≈2.39).
- **Grid** (to be committed as `sweeps._R7D_XSEC_DRAWDOWN_AXES`, pinned by
  tests): `L` {63, 126, 252} × `k` {2, 3} = **3 × 2 = 6 variants** (the
  xsec K=6 convention; bar `min_tstat(6)` ≈ 2.39). `rebalance_every` is
  FROZEN = 21 (the `xsec_momentum` monthly cadence) and is NOT a swept axis —
  it is declared in a `R7D_XSEC_DRAWDOWN_REBALANCE_EVERY = {"xsec_drawdown": 21}`
  map, exactly like `R3_XSEC_EXPANDED_REBALANCE_EVERY`. Registered
  constraints: `L >= 2`, `1 <= k <= 14`, `rebalance_every >= 1`.
- **Instruments**: `R7D_INSTRUMENTS = R3_XSEC_EXPANDED_INSTRUMENTS` (the
  XSEC-14 basket, the SAME tuple object — the committed 14-ticker all-equity/ETF
  daily surface: AAPL, AMZN, GLD, GOOGL, JPM, META, MSFT, NVDA, QQQ, SLV, SPY,
  TLT, TSLA, XOM; BTC-USD deliberately excluded to keep the aligned common
  index on exchange trading days).
- **PORTFOLIO config-counting**: `configs = variants` — the instruments do
  NOT multiply the count. Each grid point is ONE portfolio lane over the whole
  14-instrument basket (the Round-2 / Round-3 portfolio-lane accounting,
  identical to `r3_xsec_expanded_total_configs`), so **6 variants → 6
  registered configs**, one portfolio lane per variant over the whole basket.
  Program cumulative **5,595 → 5,601**.
- **Decision rule (per lane, pre-registered)**: §6 KEEP iff stitched
  portfolio-walk-forward OOS Sharpe > the equal-weight basket B&H OOS Sharpe
  (same window, same costs) AND > 0; else KILL. THEN the selection-fair gate
  on every lane (standing rule 1: `run_selection_gate` → `apply_gate`, the
  R5-D fixed-config row); informational t via
  `promotion.grade_promotion(..., variants_tried=6)` at the K=6 Bonferroni bar
  (≈2.39, never lowered, INFORMATIONAL — promotion CLOSED); `classify_verdict`
  KILL-SIG at the mirrored bar; gate block = the R5-D fixed-config row
  (standing rule 2); reason_class rollup with the mandatory UNGRADEABLE
  infra-alarm line (standing rule 3); `min_tstat` bar never lowered.
- **Burden**: 6 new registered configs; K=6, bar ≈2.39.
- **Runtime cap**: ≤ 15 minutes wall-clock for the whole slice.

---

## Exact code + tests the run session must add BEFORE any run

To `src/trading_lab/strategies/xsec_drawdown.py`: the `xsec_drawdown`
`generate_weights(closes, L=..., k=..., rebalance_every=21) -> pd.DataFrame`
callable (mirroring `xsec_reversal.generate_weights` but ranking on
`depth[t,i] = closes[t,i] / closes.rolling(L).max()[t,i] − 1` ascending), with:
- **causality / no-lookahead tests** — the weight row at decision bar `t` is
  INVARIANT to bars > `t` (the rolling max through bar `t` uses closes ≤ `t`
  only); flat/cash before iloc `L`.
- **prefix-invariance test** — `generate_weights(closes.iloc[:end]).iloc[start:end]`
  equals the corresponding slice of `generate_weights(closes)` (the schedule is
  anchored at iloc 0, so the `portfolio_walk_forward` slicing contract holds).
- **a "requires-both / long-only / sums-to-1" behavioral test** — at every
  decision bar exactly `k` instruments carry weight `1/k` and the rest 0, all
  weights are ≥ 0 (long-only), the row sums to 1, the deepest-drawdown `k`
  names are selected, and ties resolve to the lowest column index.

To `trading_lab.strategies`: register `xsec_drawdown` in `PORTFOLIO_STRATEGIES`
(NOT `STRATEGIES`) and export an `R7D_XSEC_DRAWDOWN_FAMILY` symbol naming the
family.

To `src/trading_lab/sweeps.py` (mirroring the Round-3 xsec layout at
`_R3_XSEC_EXPANDED_AXES` ff.): `_R7D_XSEC_DRAWDOWN_AXES` (`{"xsec_drawdown":
{"L": [63, 126, 252], "k": [2, 3]}}`), `R7D_XSEC_DRAWDOWN_FAMILIES = tuple(_R7D_XSEC_DRAWDOWN_AXES)`,
`R7D_INSTRUMENTS = R3_XSEC_EXPANDED_INSTRUMENTS` (SAME tuple object),
`R7D_XSEC_DRAWDOWN_REBALANCE_EVERY = {"xsec_drawdown": 21}` (frozen, NOT swept),
`r7d_xsec_drawdown_variants()` (constraint-valid expansion, returning 6), and
`r7d_total_configs()` returning **6** (PORTFOLIO: `configs = variants`,
instruments do NOT multiply) with the program cumulative advancing
**5,595 → 5,601**.

To `tests/test_sweeps.py`: pins for the `_R7D_XSEC_DRAWDOWN_AXES` dict (exact
values above), the **6-variant count** (`L`{3} × `k`{2}), the **portfolio
config-count = variants** (`r7d_total_configs()` == `r7d_xsec_drawdown_variants`
length == 6, NOT 6 × 14 = 84), the **basket identity** (`R7D_INSTRUMENTS is
R3_XSEC_EXPANDED_INSTRUMENTS`, the XSEC-14 tuple), the **frozen /
not-swept `rebalance_every`** (`R7D_XSEC_DRAWDOWN_REBALANCE_EVERY["xsec_drawdown"]
== 21`, and `rebalance_every` absent from `_R7D_XSEC_DRAWDOWN_AXES`), and the
**5,595 → 5,601** totals. Only after those tests are green may the R7-D runner
(`scripts/run_r7d_*`) execute.

## Round-level aggregation (pre-registered)

Each of the 6 portfolio lanes exits Round 7D with exactly one verdict: KEEP-dev
iff it passes the Round-2 rule AND the selection-fair gate; else KILL (or
KILL-SIG per `classify_verdict`). Results land in a new
`docs/research-round-7d-results.md`, reporting: verdict counts, every gate FAIL
reason verbatim, full fixed-config rows (`selection_gap` per lane), the
**reason_class table with the UNGRADEABLE-share infrastructure-alarm line
(standing rule 3 — mandatory)**, best informational t vs the unchanged bar,
runtime vs cap, and the burden ledger line (5,595 → 5,601 exactly; any
deviation is a registration violation, not a rounding note). Ledger convention:
each lane LEDGERED with `variants_tried=6` and keyed `instrument="XSEC-14"`
(the basket is the unit); gate replays are report-only rows in the lane JSON.
The results doc will mirror the Round-3 xsec portfolio-lane format (per-variant
`L`/`k` row: stitched OOS Sharpe vs equal-weight B&H OOS Sharpe vs t vs the
2.39 bar), the format the future run will mirror.

## What round 7D will NOT do

- **No execution in the planning session** — this plan's PR contains no
  sweep, no backtest, no grid code, no strategy code; running (and the
  pre-run code commit above) is a future session's separately claimed
  slice.
- **No holdout access** — SPENT; `data/p5holdout/` never read,
  `unlock_holdout` never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched.
- **No data fetching, no new tickers** — the committed XSEC-14 basket only.
- **No bar-lowering** — `min_tstat(6)` ≈ 2.39, never lowered.
- **No OOS validation claims, no broker/order/exchange-write code, no live
  API configuration** — research-only, per CONSTITUTION.md.
