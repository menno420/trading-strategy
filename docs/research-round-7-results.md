# Research Round 7 — Results

> **Status:** `reference` — honest results of the two pre-registered
> Round-7 slices, one dated section per slice, against the protocol in
> [research-round-7-plan.md](research-round-7-plan.md) (merged BEFORE any
> Round-7 outcome existed). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT
> and promotion is CLOSED.** Nothing on this page is an out-of-sample
> claim; a KEEP means *dev-candidate only*, and nulls/KILLs are first-class
> results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`, ~2.638 at K=12; only ever rises).
> Round 7 is graded under the selection-fair standing gate
> ([selection-fair-gate.md](selection-fair-gate.md)): the gate ran on
> EVERY lane, and its result block is each lane's R5-D fixed-config row.

**Round headline: the registered expectation (honest nulls) is confirmed —
5 KEEP-dev / 25 KILL / 0 KILL-SIG across the 30 pre-registered lanes, 0
promoted, best informational t anywhere 1.20 (BTC-USD daily
`high_proximity`) against the unchanged 2.638 bar. The program's first
drawdown-anatomy family (`drawdown_reversion`) yields 3 weak KEEP-devs
(SLV t 0.07, TLT t 0.11, XOM t 0.30) and never beats same-window B&H by
anything close to significance; the high-proximity family
(`high_proximity`) yields 2 (BTC-USD t 1.20, TSLA t 0.21) — its BTC-USD
lane is the round's strongest arm but still less than half the bar. No
lane produced a significant KILL in either direction (0 KILL-SIG of 30):
both families are unexploitable rather than harmful net of costs. The
standing gate ran on all 30 lanes (14 PASS / 16 FAIL) and demoted
nothing: every Round-2-rule KEEP independently passed its selection-free
replay, and `selection_gap > 0` on only 1 of 30 lanes (SPY
`drawdown_reversion` +0.052, itself a KILL) — walk-forward re-selection
lost to the fixed config almost everywhere, the R5-D lesson again. Zero
UNGRADEABLE lanes, no infrastructure alarm. Round-7 burden: 360 new
registered configs; program cumulative 5,055 → 5,415. Runtime caps
nowhere near hit (9.0 / 9.4 s vs 900 / 900 s); no CAP-HIT, nothing
truncated, no slice remains unrun.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Runtime vs cap |
|---|---|---|---|---|---|---|
| R7-A `r7-drawdown-reversion` (daily) | 15 | 3 | 12 | 0 | 7 / 8 | 9.0 s / 900 s |
| R7-B `r7-high-proximity` (daily) | 15 | 2 | 13 | 0 | 7 / 8 | 9.4 s / 900 s |
| **Round 7** | **30** | **5** | **25** | **0** | **14 / 16** | none hit |

Machine-readable rollups: one `summary.json` per slice directory —
[`experiments/sweeps/r7-drawdown-reversion/`](../experiments/sweeps/r7-drawdown-reversion/),
[`experiments/sweeps/r7-high-proximity/`](../experiments/sweeps/r7-high-proximity/)
(runners `scripts/run_r7_drawdown_reversion_sweep.py`,
`scripts/run_r7_high_proximity_sweep.py`).

## Reading the per-lane tables

Every lane below carries its R5-D fixed-config row (standing rule 2 —
satisfied by the gate block in the lane JSON): `searched` is the stitched
walk-forward OOS Sharpe (1008/252 bars, contiguous test windows, baseline
costs 5 bps + 1 bp), `bench` the same-window B&H Sharpe, `fixed` the
selection-free replay of the lane's committed top full-period variant on
the identical windows, `gap = searched − fixed` (informational, no
registered threshold). `t` is the ORDER 007 informational t at the lane's
K=12 (bar 2.638, never lowered). Verdict = Round-2 rule, then
`classify_verdict` (KILL-SIG at the mirrored bar), then `apply_gate` — the
gate only ever demotes. Gate FAIL reasons this round are ALL one class —
`fixed-config replay does not beat same-window B&H with a positive Sharpe
(fixed <x>, bench <y>) — the searched edge does not survive selection-free`
(machine-readable `reason_class = FAIL_UNDERPERFORM`, fixed Sharpe positive
everywhere but below its benchmark) — and the verbatim strings are
recorded in every lane JSON's `selection_gate.reason` and each slice
`summary.json`. Zero UNGRADEABLE conditions and zero fidelity-guard
failures occurred: every searched-arm replay reproduced its lane's
recorded stitched OOS Sharpe within 1e-8.

## R7-A — drawdown-anatomy family `drawdown_reversion` (2026-07-17)

**Headline: the registered hypothesis (drawdown reduction is the program's
only consistently observed effect, but does not translate into
benchmark-beating OOS edge) is confirmed. 3 KEEP / 12 KILL / 0 KILL-SIG of
15 lanes; the three KEEPs (SLV searched 0.191 vs bench 0.170, t = 0.07;
TLT 0.230 vs 0.196, t = 0.11; XOM 0.389 vs 0.294, t = 0.30) are the three
lowest-volatility instruments on the surface, all gate PASS, all nowhere
near the 2.638 bar. The searched arm beats same-window B&H on only 3 of 15
lanes and no lane clears the significance bar in either direction. The
selection-free fixed config is positive on all 15 lanes yet beats its
benchmark on only 7 (the gate PASSes), and `selection_gap < 0` on 14 of
15 (only SPY +0.052, itself a KILL) — walk-forward re-selection subtracted
value almost everywhere, the R5-D pattern once more.**

- **Pre-declaration honored**: grid verbatim from
  `sweeps._R7_DRAWDOWN_AXES` (12 variants, pinned by
  `tests/test_sweeps.py`), the committed 15-ticker daily surface
  (`sweeps.R7_INSTRUMENTS`, same tuple object as R6-A/R4-F), runner
  asserts the counts before running. 180 registered configs.
- **Method** (registered): full-period bookkeeping rows per variant;
  1008/252 walk-forward (contiguous test windows, data through 2025-01-08
  dev rail); Round-2 KEEP/KILL rule; `classify_verdict` at K=12; the
  standing gate on EVERY lane with the fidelity guard armed (15/15
  reproduced within 1e-8).
- **Gate, read honestly**: 7 PASS / 8 FAIL, 0 KEEPs demoted — the gate
  was never load-bearing this slice. Its 4 PASS-but-KILL lanes (GLD,
  GOOGL, JPM, TSLA: the fixed config beats bench while the searched arm
  loses) are the measured cost of in-window re-selection.
- **The KEEPs, read honestly**: all three are low-vol instruments (SLV,
  TLT, XOM) where any long-biased state spends most of its time flat and
  the depth-from-peak entry rarely fires — the cheapest reading is
  survivorship of a near-B&H exposure profile, not a drawdown-timing
  edge. Dev-candidates only.
- **Artifacts**: 15 lane JSONs + `summary.json` in
  [`experiments/sweeps/r7-drawdown-reversion/`](../experiments/sweeps/r7-drawdown-reversion/);
  top full-period variant per lane LEDGERED with `variants_tried=12`
  (Round-3 convention, 15 rows); gate replays report-only inside the lane
  JSONs (R4-B precedent); `experiments/index.jsonl` rebuilt. Runtime
  **9.0 s** (cap 900 s — not hit, nothing skipped).
- **Burden ledger**: 180 new registered configs; program cumulative
  5,055 → **5,235**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| drawdown_reversion · AAPL | 0.507 | 0.963 | 0.722 | -0.215 | -1.442 | FAIL | **KILL** |
| drawdown_reversion · AMZN | 0.253 | 0.763 | 0.448 | -0.195 | -1.611 | FAIL | **KILL** |
| drawdown_reversion · BTC-USD | 0.196 | 0.821 | 0.437 | -0.241 | -1.978 | FAIL | **KILL** |
| drawdown_reversion · GLD | 0.396 | 0.400 | 0.756 | -0.360 | -0.012 | PASS | **KILL** |
| drawdown_reversion · GOOGL | 0.582 | 0.720 | 0.816 | -0.234 | -0.437 | PASS | **KILL** |
| drawdown_reversion · JPM | 0.362 | 0.645 | 0.740 | -0.378 | -0.893 | PASS | **KILL** |
| drawdown_reversion · META | 0.307 | 0.653 | 0.459 | -0.152 | -0.979 | FAIL | **KILL** |
| drawdown_reversion · MSFT | 0.491 | 1.101 | 0.633 | -0.143 | -1.931 | FAIL | **KILL** |
| drawdown_reversion · NVDA | 0.643 | 1.295 | 0.935 | -0.292 | -2.062 | FAIL | **KILL** |
| drawdown_reversion · QQQ | 0.574 | 0.871 | 0.709 | -0.135 | -0.939 | FAIL | **KILL** |
| drawdown_reversion · SLV | 0.191 | 0.170 | 0.469 | -0.278 | 0.069 | PASS | **KEEP** |
| drawdown_reversion · SPY | 0.472 | 0.761 | 0.420 | 0.052 | -0.913 | FAIL | **KILL** |
| drawdown_reversion · TLT | 0.230 | 0.196 | 0.768 | -0.538 | 0.107 | PASS | **KEEP** |
| drawdown_reversion · TSLA | 0.632 | 0.760 | 0.796 | -0.164 | -0.406 | PASS | **KILL** |
| drawdown_reversion · XOM | 0.389 | 0.294 | 0.411 | -0.021 | 0.302 | PASS | **KEEP** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 15 | 3 | 12 | 0 | 7 | 8 | 0 |

## R7-B — high-proximity state family `high_proximity` (2026-07-17)

**Headline: the registered expectation (a proximity-to-high state is a
noisy proxy for the trends the program has already graded, no new
information channel) holds — 2 KEEP / 13 KILL / 0 KILL-SIG of 15 lanes.
The two KEEPs are BTC-USD (searched 1.200 vs bench 0.821, t = 1.20 — the
round's strongest arm, still less than half the 2.638 bar, gate PASS) and
TSLA (0.825 vs 0.760, t = 0.21, gate PASS) — both instruments whose daily
lanes already hold trend-family KEEP-devs, so the cheapest reading is that
"close within p of the trailing N-bar high" re-expresses a trend filter
rather than adding signal. The searched arm beats B&H on only 2 of 15
lanes; `selection_gap < 0` on ALL 15 (−0.03 to −0.48), and the gate FAILs
8 of 15 (fixed positive but under benchmark on every FAIL) — the family
has no selection-free edge anywhere.**

- **Pre-declaration honored**: grid verbatim from
  `sweeps._R7_HIGHPROX_AXES` (12 variants, pinned by
  `tests/test_sweeps.py`), the committed 15-ticker daily surface
  (`sweeps.R7_INSTRUMENTS`, same tuple as R7-A), runner asserts the counts
  before running. 180 registered configs.
- **Method / gate**: identical to R7-A (Round-2 rule, `classify_verdict`
  at K=12, gate on every lane; fidelity guard 15/15 within 1e-8). Gate 7
  PASS / 8 FAIL, 0 KEEPs demoted. The 5 PASS-but-KILL lanes (JPM, META,
  NVDA, SLV, TLT) are the slice's honest story: fixed beats bench,
  searched does not.
- **The KEEPs, read honestly**: BTC-USD and TSLA are the two highest-
  momentum instruments on the surface and already hold price-only
  trend-family KEEP-devs; a proximity-to-high long is long the same
  regime. Both are dev-candidates only, both far below the bar.
- **Artifacts**: 15 lane JSONs + `summary.json` in
  [`experiments/sweeps/r7-high-proximity/`](../experiments/sweeps/r7-high-proximity/);
  top full-period variant per lane LEDGERED with `variants_tried=12` (15
  rows); `experiments/index.jsonl` rebuilt. Runtime **9.4 s** (cap 900 s —
  not hit, nothing skipped).
- **Burden ledger**: 180 new registered configs; program cumulative
  5,235 → **5,415**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| high_proximity · AAPL | 0.546 | 0.963 | 0.771 | -0.225 | -1.319 | FAIL | **KILL** |
| high_proximity · AMZN | 0.523 | 0.763 | 0.727 | -0.204 | -0.758 | FAIL | **KILL** |
| high_proximity · BTC-USD | 1.200 | 0.821 | 1.397 | -0.197 | 1.195 | PASS | **KEEP** |
| high_proximity · GLD | 0.276 | 0.400 | 0.301 | -0.025 | -0.393 | FAIL | **KILL** |
| high_proximity · GOOGL | 0.268 | 0.720 | 0.586 | -0.318 | -1.429 | FAIL | **KILL** |
| high_proximity · JPM | 0.452 | 0.645 | 0.711 | -0.259 | -0.609 | PASS | **KILL** |
| high_proximity · META | 0.226 | 0.653 | 0.704 | -0.477 | -1.208 | PASS | **KILL** |
| high_proximity · MSFT | 0.923 | 1.101 | 0.978 | -0.056 | -0.565 | FAIL | **KILL** |
| high_proximity · NVDA | 1.239 | 1.295 | 1.309 | -0.070 | -0.179 | PASS | **KILL** |
| high_proximity · QQQ | 0.676 | 0.871 | 0.789 | -0.113 | -0.618 | FAIL | **KILL** |
| high_proximity · SLV | 0.133 | 0.170 | 0.585 | -0.452 | -0.117 | PASS | **KILL** |
| high_proximity · SPY | 0.469 | 0.761 | 0.699 | -0.230 | -0.924 | FAIL | **KILL** |
| high_proximity · TLT | 0.123 | 0.196 | 0.313 | -0.190 | -0.233 | PASS | **KILL** |
| high_proximity · TSLA | 0.825 | 0.760 | 0.928 | -0.103 | 0.206 | PASS | **KEEP** |
| high_proximity · XOM | -0.149 | 0.294 | 0.235 | -0.384 | -1.401 | FAIL | **KILL** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 15 | 2 | 13 | 0 | 7 | 8 | 0 |

## reason_class rollup (all 30 lanes)

Machine-readable `selection_gate.reason_class` across both slices
(standing rule 3 — the UNGRADEABLE-share is an INFRASTRUCTURE alarm, never
strategy evidence):

| reason_class | count | kind |
|---|---|---|
| `PASS` | 14 | gate pass |
| `FAIL_UNDERPERFORM` | 16 | genuine rule failure (fixed positive, below same-window B&H) |
| `FAIL_NONPOSITIVE` | 0 | genuine rule failure (fixed Sharpe ≤ 0) |
| `UNGRADEABLE_MISSING_WINDOWS` | 0 | infrastructure |
| `UNGRADEABLE_DRIFT` | 0 | infrastructure |
| `UNGRADEABLE_NONCONTIGUOUS` | 0 | infrastructure |
| `UNGRADEABLE_FIDELITY` | 0 | infrastructure |
| `UNGRADEABLE_NAN` | 0 | infrastructure |
| **total** | **30** | |

**UNGRADEABLE share: 0 of 30 lanes (0.0%) — no infrastructure alarm.**
Every `selection_gate.UNGRADEABLE_CLASSES` count is zero: no missing/
non-contiguous windows, no cache drift, no fidelity-guard miss, no NaN
degeneracy. The 16 gate FAILs are all genuine `FAIL_UNDERPERFORM` rule
failures (the fixed-config replay is positive on every lane but beats its
same-window benchmark on only 14), not irreproducible lanes — so the
Round-7 nulls are strategy evidence, read as designed.

## Round 7 — closing tally (2026-07-17)

Both pre-registered Round-7 slices ran top-down against the plan merged
before any outcome existed. One-line verdicts:

| Slice | One-line verdict |
|---|---|
| R7-A drawdown_reversion | **3/15 KEEP-dev** (SLV t 0.07, TLT t 0.11, XOM t 0.30 — the three lowest-vol instruments), 0 KILL-SIG; drawdown timing adds no benchmark-beating OOS edge |
| R7-B high_proximity | **2/15 KEEP-dev** (BTC-USD t 1.20, TSLA t 0.21 — instruments that already hold trend KEEP-devs), 0 KILL-SIG; proximity-to-high re-expresses a trend filter, no new channel |

- **Cumulative burden**: exactly **5,055 → 5,415 registered configs (360
  new: 180 + 180)** (`sweeps.r7_total_configs()`, pinned by tests). No K
  was counted down and no bar was lowered (informational t graded at each
  lane's K=12 throughout, bar 2.638).
- **Runtime caps**: none hit (slice runtimes 9.0 / 9.4 s against caps of
  900 / 900 s); nothing was truncated, no lanes skipped, **no CAP-HIT
  anywhere, no slice remains unrun**.
- **The standing gate, read honestly**: it ran on all 30 lanes (fidelity
  guard 30/30 within 1e-8, zero UNGRADEABLE) and demoted zero KEEPs —
  every Round-2-rule KEEP also passed selection-free. `selection_gap > 0`
  on only 1 of 30 lanes (SPY `drawdown_reversion` +0.052, a KILL), and 9
  lanes across the round show gate PASS with a KILLed searched arm.
  Walk-forward re-selection subtracted value almost everywhere it was
  measured — R5-D's "selection variance, not signal" holds on 30 fresh
  lanes.
- **0 promoted — promotion remains CLOSED, holdout SPENT.** The five
  KEEP-devs are dev-candidates only (best t 1.20 vs bar 2.638 — nothing
  within a factor of 2 of significance); genuine OOS validation of any
  KEEP-dev stays OWNER-GATED behind a new pre-registered protocol on
  post-2026 data.
- **What the round actually established**: (1) the drawdown-anatomy
  channel — the program's only consistently observed effect (drawdown
  reduction) — does not translate into benchmark-beating OOS edge (3 weak
  KEEP-devs, all low-vol, none near the bar); (2) a proximity-to-high
  state is a noisy proxy for trends already graded (2 KEEP-devs on
  instruments that already hold trend KEEP-devs); (3) neither family is
  significantly harmful (0 KILL-SIG of 30) — both are honest unexploitable
  nulls; (4) the selection-fair gate remains cheap (30 gate replays inside
  ~19 s of total slice runtime), zero-UNGRADEABLE, and demotes nothing.

Round 7 is graded. Two slices, two honest answers, zero findings, zero
cap-hits, five weak dev-candidates, and both genuinely new idea classes
graded as unexploitable nulls. Anything further still needs new data
(OWNER-GATED) or a genuinely different idea class.
