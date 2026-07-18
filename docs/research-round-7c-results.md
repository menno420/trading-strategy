# Research Round 7C — Results

> **Status:** `reference` — honest results of the single pre-registered
> Round-7C slice, against the protocol in
> [research-round-7c-plan.md](research-round-7c-plan.md) (merged as PR #144
> BEFORE any Round-7C outcome existed). **POST-HOLDOUT, DEV-ONLY: the
> holdout is SPENT and promotion is CLOSED.** Nothing on this page is an
> out-of-sample claim; a KEEP means *dev-candidate only*, and nulls/KILLs
> are first-class results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`, ~2.638 at K=12; only ever rises).
> Round 7C is graded under the selection-fair standing gate
> ([selection-fair-gate.md](selection-fair-gate.md)): the gate ran on EVERY
> lane, and its result block is each lane's R5-D fixed-config row.

**Round headline: the registered expectation (honest nulls) is confirmed,
and more sharply than for either component — the drawdown × high-proximity
CONJUNCTION `washout_recovery` yields 1 KEEP-dev / 11 KILL / 3 KILL-SIG
across the 15 pre-registered lanes, 0 promoted, best informational t
anywhere 0.22 (TLT daily) against the unchanged 2.638 bar. The sole KEEP is
TLT (searched 0.265 vs bench 0.196, t 0.22, gate PASS) — the same low-vol
instrument the two components each KEEP-dev'd in isolation, again far below
half the bar. What is new versus R7-A/R7-B is the KILL side: the conjunction
is significantly WORSE than same-window B&H on 3 of 15 lanes (AMZN t −3.00,
MSFT t −3.72, QQQ t −3.11 — the first KILL-SIG lanes any R7 family has
produced), i.e. requiring "washed-out AND recovering" at once selects a
worse-than-hold slice of the tape on those high-momentum names, net of
costs. The standing gate ran on all 15 lanes (2 PASS / 13 FAIL) and this
time WAS load-bearing: it demoted 1 Round-2-rule KEEP (GLD, the only lane
with `selection_gap > 0` at +0.031, fixed 0.398 just under bench 0.400) to
KILL — the first R7-family gate demotion. `selection_gap < 0` on 14 of 15
lanes, the R5-D pattern once more. Zero UNGRADEABLE lanes, no infrastructure
alarm. Round-7C burden: 180 new registered configs; program cumulative
5,415 → 5,595. Runtime nowhere near the cap (9.3 s vs 900 s); no CAP-HIT,
nothing truncated, no lane remains unrun.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Runtime vs cap |
|---|---|---|---|---|---|---|
| R7-C `r7c-conjunction` (daily) | 15 | 1 | 11 | 3 | 2 / 13 | 9.3 s / 900 s |
| **Round 7C** | **15** | **1** | **11** | **3** | **2 / 13** | none hit |

Machine-readable rollup: `summary.json` in the slice directory —
[`experiments/sweeps/r7c-conjunction/`](../experiments/sweeps/r7c-conjunction/)
(runner `scripts/run_r7c_conjunction_sweep.py`).

## Reading the per-lane tables

Every lane below carries its R5-D fixed-config row (standing rule 2 —
satisfied by the gate block in the lane JSON): `searched` is the stitched
walk-forward OOS Sharpe (1008/252 bars, contiguous test windows, baseline
costs 5 bps + 1 bp), `bench` the same-window B&H Sharpe, `fixed` the
selection-free replay of the lane's committed top full-period variant on the
identical windows, `gap = searched − fixed` (informational, no registered
threshold). `t` is the ORDER 007 informational t at the lane's K=12 (bar
2.638, never lowered). Verdict = Round-2 rule, then `classify_verdict`
(KILL-SIG at the mirrored bar), then `apply_gate` — the gate only ever
demotes. The 13 gate FAILs this round are all one class — `fixed-config
replay does not beat same-window B&H with a positive Sharpe (fixed <x>,
bench <y>) — the searched edge does not survive selection-free`
(machine-readable `reason_class = FAIL_UNDERPERFORM`, fixed Sharpe positive
everywhere but below its benchmark) — and the verbatim strings are recorded
in every lane JSON's `selection_gate.reason` and the slice `summary.json`.
Zero UNGRADEABLE conditions and zero fidelity-guard failures occurred: every
searched-arm replay reproduced its lane's recorded stitched OOS Sharpe within
1e-8.

## R7-C — washout-recovery conjunction family `washout_recovery` (2026-07-18)

**Headline: the registered hypothesis (the conjunction of a long-horizon
washout and a short-horizon recovery does NOT beat buy-and-hold net of costs
— most lanes KILL) is confirmed, and the conjunction is if anything worse
than either component alone. 1 KEEP / 11 KILL / 3 KILL-SIG of 15 lanes. The
sole KEEP is TLT (searched 0.265 vs bench 0.196, t 0.22, gate PASS) — the
lowest-vol instrument on the surface, the same name R7-A `drawdown_reversion`
and R7-B `high_proximity` each KEEP-dev'd in isolation, nowhere near the
2.638 bar. The searched arm beats same-window B&H on only 2 of 15 lanes
(TLT, GLD), and on 3 high-momentum names (AMZN, MSFT, QQQ) the conjunction
is SIGNIFICANTLY below B&H (t < −2.638) — the first significant negatives any
R7 family has produced: demanding "deeply washed out from the 252-bar peak
AND at/near the ≤63-bar high" at the same instant selects a slice of tape
that underperforms holding, net of costs, on exactly the names a buy-and-hold
did best. The selection-free fixed config is positive on all 15 lanes yet
beats its benchmark on only 2 (the gate PASSes), and `selection_gap < 0` on
14 of 15 (only GLD +0.031, itself demoted to KILL) — walk-forward
re-selection subtracted value almost everywhere, the R5-D pattern once
more.**

- **Pre-declaration honored**: grid verbatim from
  `sweeps._R7C_CONJUNCTION_AXES` (12 variants — W_dd {252} × entry_dd {0.10,
  0.20} × W_prox {21, 42, 63} × p {0.90, 0.95}, pinned by
  `tests/test_sweeps.py` with the `W_prox < W_dd` registered constraint),
  the committed 15-ticker daily surface (`sweeps.R7C_INSTRUMENTS`, the same
  tuple object as R7), runner asserts the counts before running. 180
  registered configs.
- **Method** (registered): full-period bookkeeping rows per variant;
  1008/252 walk-forward (contiguous test windows, data through 2025-01-08
  dev rail); Round-2 KEEP/KILL rule; `classify_verdict` at K=12; the standing
  gate on EVERY lane with the fidelity guard armed (15/15 reproduced within
  1e-8).
- **Gate, read honestly**: 2 PASS / 13 FAIL, and — unlike R7-A/R7-B — the
  gate WAS load-bearing: it demoted 1 KEEP (GLD, searched 0.429 > bench 0.400
  by Round-2 rule, but the selection-free fixed config 0.398 loses to the
  0.400 benchmark → FAIL → KILL). The one PASS-but-KILL lane is XOM (fixed
  0.491 beats bench 0.294 while the searched arm is negative). Both PASS
  lanes (TLT, XOM) are low-vol/low-benchmark instruments.
- **The KEEP, read honestly**: TLT is the lowest-vol instrument on the
  surface, where any long-biased state spends most of its time flat and the
  conjunction rarely fires — the cheapest reading is survivorship of a
  near-B&H exposure profile, not a washout-recovery edge, the same reading
  R7-A gave TLT/SLV/XOM. Dev-candidate only.
- **The KILL-SIG lanes, read honestly**: AMZN (t −3.00), MSFT (t −3.72),
  QQQ (t −3.11) are the round's genuine information — the conjunction is not
  merely unexploitable there, it is significantly worse than holding: on
  high-drift names the "washed-out AND recovering" gate is systematically
  out of the market during the recoveries that a buy-and-hold captures. That
  is evidence the conjunction destroys value on trending names, not that it
  times them.
- **Artifacts**: 15 lane JSONs + `summary.json` in
  [`experiments/sweeps/r7c-conjunction/`](../experiments/sweeps/r7c-conjunction/);
  top full-period variant per lane LEDGERED with `variants_tried=12`
  (Round-3 convention, 15 rows); gate replays report-only inside the lane
  JSONs (R4-B precedent); `experiments/index.jsonl` rebuilt. Runtime **9.3 s**
  (cap 900 s — not hit, nothing skipped).
- **Burden ledger**: 180 new registered configs; program cumulative
  5,415 → **5,595**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| washout_recovery · AAPL | 0.660 | 0.963 | 0.953 | -0.292 | -0.956 | FAIL | **KILL** |
| washout_recovery · AMZN | -0.186 | 0.763 | 0.522 | -0.708 | -3.001 | FAIL | **KILL-SIG** |
| washout_recovery · BTC-USD | 0.049 | 0.821 | 0.636 | -0.586 | -2.441 | FAIL | **KILL** |
| washout_recovery · GLD | 0.429 | 0.400 | 0.398 | 0.031 | 0.092 | FAIL | **KILL** |
| washout_recovery · GOOGL | 0.110 | 0.720 | 0.597 | -0.487 | -1.928 | FAIL | **KILL** |
| washout_recovery · JPM | 0.210 | 0.645 | 0.224 | -0.014 | -1.375 | FAIL | **KILL** |
| washout_recovery · META | -0.142 | 0.653 | 0.525 | -0.667 | -2.250 | FAIL | **KILL** |
| washout_recovery · MSFT | -0.073 | 1.101 | 0.289 | -0.362 | -3.715 | FAIL | **KILL-SIG** |
| washout_recovery · NVDA | 0.638 | 1.295 | 0.754 | -0.117 | -2.078 | FAIL | **KILL** |
| washout_recovery · QQQ | -0.113 | 0.871 | 0.146 | -0.259 | -3.112 | FAIL | **KILL-SIG** |
| washout_recovery · SLV | -0.255 | 0.170 | 0.022 | -0.277 | -1.344 | FAIL | **KILL** |
| washout_recovery · SPY | 0.070 | 0.761 | 0.683 | -0.613 | -2.186 | FAIL | **KILL** |
| washout_recovery · TLT | 0.265 | 0.196 | 0.460 | -0.195 | 0.217 | PASS | **KEEP** |
| washout_recovery · TSLA | 0.368 | 0.760 | 0.676 | -0.308 | -1.239 | FAIL | **KILL** |
| washout_recovery · XOM | -0.126 | 0.294 | 0.491 | -0.617 | -1.329 | PASS | **KILL** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 15 | 1 | 11 | 3 | 2 | 13 | 1 |

## reason_class rollup (all 15 lanes)

Machine-readable `selection_gate.reason_class` across the slice (standing
rule 3 — the UNGRADEABLE-share is an INFRASTRUCTURE alarm, never strategy
evidence):

| reason_class | count | kind |
|---|---|---|
| `PASS` | 2 | gate pass |
| `FAIL_UNDERPERFORM` | 13 | genuine rule failure (fixed positive, below same-window B&H) |
| `FAIL_NONPOSITIVE` | 0 | genuine rule failure (fixed Sharpe ≤ 0) |
| `UNGRADEABLE_MISSING_WINDOWS` | 0 | infrastructure |
| `UNGRADEABLE_DRIFT` | 0 | infrastructure |
| `UNGRADEABLE_NONCONTIGUOUS` | 0 | infrastructure |
| `UNGRADEABLE_FIDELITY` | 0 | infrastructure |
| `UNGRADEABLE_NAN` | 0 | infrastructure |
| **total** | **15** | |

**UNGRADEABLE share: 0 of 15 lanes (0.0%) — no infrastructure alarm.** Every
`selection_gate.UNGRADEABLE_CLASSES` count is zero: no missing/non-contiguous
windows, no cache drift, no fidelity-guard miss, no NaN degeneracy. The 13
gate FAILs are all genuine `FAIL_UNDERPERFORM` rule failures (the
fixed-config replay is positive on every lane but beats its same-window
benchmark on only 2), not irreproducible lanes — so the Round-7C nulls and
the 3 KILL-SIG negatives are strategy evidence, read as designed.

## Round 7C — closing tally (2026-07-18)

The single pre-registered Round-7C slice ran top-down against the plan merged
before any outcome existed. One-line verdict:

| Slice | One-line verdict |
|---|---|
| R7-C washout_recovery | **1/15 KEEP-dev** (TLT t 0.22 — the lowest-vol instrument), 3 KILL-SIG (AMZN t −3.00, MSFT t −3.72, QQQ t −3.11); the drawdown × high-proximity conjunction adds no benchmark-beating edge and is significantly value-destroying on high-drift names |

- **Cumulative burden**: exactly **5,415 → 5,595 registered configs (180
  new)** (`sweeps.r7c_total_configs()`, pinned by tests). No K was counted
  down and no bar was lowered (informational t graded at K=12 throughout, bar
  2.638).
- **Runtime cap**: not hit (slice runtime 9.3 s against a 900 s cap); nothing
  was truncated, no lanes skipped, **no CAP-HIT, no lane remains unrun**.
- **The standing gate, read honestly**: it ran on all 15 lanes (fidelity
  guard 15/15 within 1e-8, zero UNGRADEABLE) and — for the first time in the
  R7 family — demoted a KEEP (GLD, the only lane with `selection_gap > 0`).
  `selection_gap < 0` on 14 of 15 lanes; the two gate PASSes are both low-vol
  instruments and only one (TLT) survives the Round-2 rule. Walk-forward
  re-selection subtracted value almost everywhere it was measured — R5-D's
  "selection variance, not signal" holds on 15 fresh lanes.
- **0 promoted — promotion remains CLOSED, holdout SPENT.** The single
  KEEP-dev is a dev-candidate only (best t 0.22 vs bar 2.638 — an order of
  magnitude below significance); genuine OOS validation stays OWNER-GATED
  behind a new pre-registered protocol on post-2026 data.
- **What the round actually established**: (1) the conjunction of a
  long-horizon washout and a short-horizon recovery carries NO information the
  two components lacked — its one KEEP is the same low-vol survivorship name
  the components each returned, far below the bar; (2) the conjunction is
  strictly WORSE than its components on the KILL side — 3 KILL-SIG lanes
  (AMZN, MSFT, QQQ) where insisting on both states at once is significantly
  value-destroying versus holding, against 0 KILL-SIG in all of R7-A/R7-B;
  (3) the selection-fair gate stayed cheap (15 replays inside ~9 s),
  zero-UNGRADEABLE, and this time earned its keep by demoting the round's one
  gap-positive KEEP.

Round 7C is graded. One slice, one honest answer, zero findings, zero
cap-hits, one weak dev-candidate, and the first Round-7 interaction family
graded not merely as an unexploitable null but as an actively value-destroying
conjunction on trending names. Anything further still needs new data
(OWNER-GATED) or a genuinely different idea class.
