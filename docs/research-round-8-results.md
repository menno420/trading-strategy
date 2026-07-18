# Research Round 8 — Results

> **Status:** `reference` — honest results of the pre-registered Round-8
> hourly companion sweep, graded against the protocol in
> [research-round-8-plan.md](research-round-8-plan.md) (merged BEFORE any
> Round-8 outcome existed, PR #149). **POST-HOLDOUT, DEV-ONLY: the holdout
> is SPENT and promotion is CLOSED.** Nothing on this page is an
> out-of-sample claim; a KEEP means *dev-candidate only*, and nulls/KILLs
> are first-class results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`, ~2.638 at K=12; only ever rises).
> Round 8 adds NO new strategy code — it re-registers the two newest R7
> single-instrument families (`drawdown_reversion`, `high_proximity`)
> VERBATIM on the committed 8-ticker hourly cache, isolating the single
> variable of bar frequency. The selection-fair standing gate
> ([selection-fair-gate.md](selection-fair-gate.md)) ran on EVERY lane, and
> its result block is each lane's R5-D fixed-config row.

**Round headline: the registered null held on the substance and split on
the coarse count — 3 KEEP-dev / 13 KILL / 0 KILL-SIG of 16 hourly lanes,
0 promoted, gate 8 PASS / 8 FAIL (0 KEEPs demoted), best informational t
anywhere 1.079 (MSFT `drawdown_reversion`) against the unchanged 2.638
bar — NOTHING clears it. `high_proximity` nulled HARDER on hourly exactly
as predicted (0 KEEP-dev / 8 KILL, versus its daily R7-B 2 KEEP-dev / 13
KILL — the two daily dev-KEEPs vanished, all 8 hourly lanes KILL).
`drawdown_reversion` did NOT amplify KILLs by raw count (3 KEEP-dev / 5
KILL, 37.5% dev-KEEP rate versus daily R7-A's 20%) — but every one of its
3 hourly dev-KEEPs is the WEAKEST possible dev-candidate: best t 1.079 far
under the bar, resting on a SINGLE ~8.5-month 2024 regime (5 splits), the
exact R5-B single-window-luck exposure the plan registered as a caveat in
advance. INFRASTRUCTURE ALARM (standing rule 3): 1 of 16 lanes
(`drawdown_reversion` · GLD) is `UNGRADEABLE_NAN` — the strategy produced
degenerate/flat stitched OOS returns on GLD hourly (no gradeable signal);
that lane is counted KILL but its number is an infra fact, NEVER strategy
evidence. Runtime 4.8 s vs the 900 s cap — no CAP-HIT, nothing truncated,
no lane unrun. Burden: 192 new registered configs; program cumulative
5,601 → 5,793.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Runtime vs cap |
|---|---|---|---|---|---|---|
| R8 `r8-hourly` (drawdown_reversion + high_proximity × 8 hourly) | 16 | 3 | 13 | 0 | 8 / 8 | 4.8 s / 900 s |

Machine-readable rollup: `summary.json` in
[`experiments/sweeps/r8-hourly/`](../experiments/sweeps/r8-hourly/)
(runner `scripts/run_r8_hourly_sweep.py`, cloned from the R6-C hourly
runner so the selection-fair gate runs on every lane).

## Reading the per-lane table

Every lane below carries its R5-D fixed-config row (standing rule 2 —
satisfied by the gate block in the lane JSON): `searched` is the stitched
walk-forward OOS Sharpe (1008/252 HOURLY bars, contiguous test windows,
baseline costs 5 bps + 1 bp), `bench` the same-window B&H Sharpe, `fixed`
the selection-free replay of the lane's committed top full-period variant
on the identical windows, `gap = searched − fixed` (informational, no
registered threshold). `t` is the ORDER 007 informational t at the lane's
K=12 (bar 2.638, never lowered). Verdict = Round-2 rule, then
`classify_verdict` (KILL-SIG at the mirrored bar), then `apply_gate` — the
gate only ever demotes. The verbatim gate `reason` and `reason_class` are
recorded in every lane JSON's `selection_gate` block and each slice
`summary.json`.

## R8 — R7 families on hourly bars (2026-07-18)

- **Pre-declaration honored**: grids IDENTICAL to the daily R7-A / R7-B
  axes (`_R8_HOURLY_DRAWDOWN_AXES == _R7_DRAWDOWN_AXES`,
  `_R8_HOURLY_HIGHPROX_AXES == _R7_HIGHPROX_AXES`), pinned by tests and
  re-asserted by the runner at startup (grid identity with `r7_variants`
  checked per family before any lane runs). The committed 8-ticker hourly
  surface (same tuple object as R6-C / r3-trend-hourly). 12 variants ×
  2 families × 8 tickers = **192 registered configs**. 1008/252 BARS on
  hourly data (lab convention), **5 splits per lane** (~2,476 dev-rail
  bars per cache).
- **Data adequacy caveat honored (registered in advance)**: the entire
  stitched OOS is a SINGLE ~8.5-month 2024 regime (5 splits) — the
  program's thinnest evidence-per-config. Any KEEP-dev here carries the
  R5-B single-window-luck caveat and is the WEAKEST possible dev-candidate;
  this is the exact exposure R5-B demoted a prior hourly KEEP for.
- **Method / gate**: identical to R6-C (Round-2 rule, `classify_verdict`
  at K=12, gate on every lane). Gate 8 PASS / 8 FAIL, **0 KEEPs demoted**.
  The 5 PASS-but-KILL lanes are the slice's honest story (the searched arm
  simply did not beat B&H with a positive Sharpe).
- **Infrastructure alarm (standing rule 3 — mandatory)**: 1 of 16 lanes
  (`drawdown_reversion` · GLD) resolved `reason_class = UNGRADEABLE_NAN` —
  the stitched OOS Sharpe is NaN (degenerate/flat returns: the family took
  no gradeable position on GLD hourly over the 2024 window). Nonzero
  UNGRADEABLE share (**1/16 = 6.25%**) is an INFRASTRUCTURE fact reported
  here and NEVER treated as strategy evidence; the lane is counted KILL.
- **Artifacts**: 16 lane JSONs + `summary.json` in
  [`experiments/sweeps/r8-hourly/`](../experiments/sweeps/r8-hourly/); top
  full-period variant per lane LEDGERED with `variants_tried=12` (16 rows);
  `experiments/index.jsonl` rebuilt. Runtime **4.8 s** (cap 900 s — not
  hit, nothing skipped).
- **Burden ledger**: 192 new registered configs; program cumulative
  5,601 → **5,793**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| drawdown_reversion · AAPL | 1.012 | 1.570 | 1.581 | -0.569 | -0.490 | PASS | **KILL** |
| drawdown_reversion · MSFT | 1.379 | 0.148 | 1.532 | -0.153 | 1.079 | PASS | **KEEP** |
| drawdown_reversion · NVDA | 1.166 | 1.387 | 3.165 | -1.999 | -0.194 | PASS | **KILL** |
| drawdown_reversion · GOOGL | 0.706 | 1.010 | 0.706 | 0.000 | -0.267 | FAIL | **KILL** |
| drawdown_reversion · AMZN | 0.697 | 0.615 | 2.530 | -1.833 | 0.072 | PASS | **KEEP** |
| drawdown_reversion · META | 0.572 | 0.494 | 1.338 | -0.766 | 0.068 | PASS | **KEEP** |
| drawdown_reversion · GLD | — | 2.056 | — | — | — | FAIL | **KILL** |
| drawdown_reversion · SLV | 0.768 | 1.185 | 1.422 | -0.654 | -0.366 | PASS | **KILL** |
| high_proximity · AAPL | 1.453 | 1.570 | 0.923 | 0.530 | -0.103 | FAIL | **KILL** |
| high_proximity · MSFT | -0.428 | 0.148 | -0.075 | -0.353 | -0.505 | FAIL | **KILL** |
| high_proximity · NVDA | -0.339 | 1.387 | 1.304 | -1.643 | -1.515 | FAIL | **KILL** |
| high_proximity · GOOGL | 0.712 | 1.010 | 1.109 | -0.396 | -0.261 | PASS | **KILL** |
| high_proximity · AMZN | -0.241 | 0.615 | 0.501 | -0.743 | -0.751 | FAIL | **KILL** |
| high_proximity · META | -0.019 | 0.494 | 0.261 | -0.279 | -0.450 | FAIL | **KILL** |
| high_proximity · GLD | 1.526 | 2.056 | 2.050 | -0.524 | -0.465 | FAIL | **KILL** |
| high_proximity · SLV | 0.306 | 1.185 | 1.369 | -1.063 | -0.771 | PASS | **KILL** |

### Counts — overall

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 16 | 3 | 13 | 0 | 8 | 8 | 0 |

### Counts — `drawdown_reversion` (8 hourly lanes)

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL |
|---|---|---|---|---|---|
| 8 | 3 | 5 | 0 | 6 | 2 |

KEEP-dev: MSFT (t 1.079), AMZN (t 0.072), META (t 0.068) — all gate PASS,
all far under the 2.638 bar, all on the single 5-split 2024 regime
(dev-candidates only, R5-B caveat).

### Counts — `high_proximity` (8 hourly lanes)

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL |
|---|---|---|---|---|---|
| 8 | 0 | 8 | 0 | 2 | 6 |

Clean sweep of KILLs — the sharpest hourly null in this companion.

### reason_class rollup (standing rule 3)

| reason_class | count | share | note |
|---|---|---|---|
| PASS | 8 | 50.0% | searched arm reproduced + gradeable |
| FAIL_UNDERPERFORM | 6 | 37.5% | fixed replay does not beat B&H with positive Sharpe |
| FAIL_NONPOSITIVE | 1 | 6.25% | searched/fixed Sharpe non-positive |
| **UNGRADEABLE_NAN** | **1** | **6.25%** | **INFRASTRUCTURE ALARM — degenerate/NaN stitched OOS (GLD drawdown_reversion); NOT strategy evidence** |

**UNGRADEABLE share 1/16 = 6.25% (nonzero) → infrastructure alarm raised
per standing rule 3.** The single ungradeable lane (`drawdown_reversion` ·
GLD) produced flat/NaN stitched returns because the family opened no
gradeable position on GLD hourly over the 2024 window; it is reported as an
infra fact and excluded from any strategy conclusion (it is counted KILL by
the Round-2 tie-to-KILL rule, not by a measured underperformance).

## Comparison to the daily R7 verdicts — did hourly amplify KILLs?

The plan registered the null *"hourly AMPLIFIES KILLs — both families null
HARDER on hourly than their daily R7 verdicts."* Result: **split by
family, but confirmed on the substance.**

| Family | Daily R7 (15 lanes) | Hourly R8 (8 lanes) | KILLs amplified? |
|---|---|---|---|
| `drawdown_reversion` | 3 KEEP-dev / 12 KILL (20% dev-KEEP) | 3 KEEP-dev / 5 KILL (37.5% dev-KEEP) | **No** by raw count — but 0 clear the bar (best t 1.079), all on 1 regime |
| `high_proximity` | 2 KEEP-dev / 13 KILL (13% dev-KEEP) | 0 KEEP-dev / 8 KILL (0% dev-KEEP) | **Yes** — both daily dev-KEEPs vanished, all 8 hourly lanes KILL |

- **`high_proximity` confirms the registered null cleanly**: moving to the
  shorter-horizon, higher-churn hourly bar removed every dev-KEEP the daily
  grid found — the family nulls harder on hourly, exactly as predicted.
- **`drawdown_reversion` splits the null on the coarse count but confirms
  it on the substance**: the raw dev-KEEP *rate* rose on hourly, which is
  the opposite of "more KILLs by count." But the plan's substantive claim —
  *no gradient clears the unchanged K=12 bar (~2.638)* — held completely:
  the best hourly t anywhere is 1.079, 0 lanes clear the bar, 0 promoted,
  and all 3 hourly dev-KEEPs rest on a single ~8.5-month 2024 regime (5
  splits), the weakest evidence-per-config in the program and the exact
  R5-B single-window-luck exposure registered in advance. Read honestly:
  hourly did not manufacture a real edge here; it manufactured a handful of
  regime-fragile dev-candidates on the thinnest possible evidence.
- **No KILL-SIG lanes materialized** (the plan noted these as *plausible*,
  not predicted): the worst informational t is −1.515 (NVDA
  `high_proximity`), nowhere near the −2.638 significance mirror. Hourly
  churn eroded the searched edge without making it *significantly* worse
  than B&H on this surface.

**Best informational t anywhere: 1.079 (MSFT `drawdown_reversion`) vs the
unchanged 2.638 bar — nothing in Round 8 clears it, and nothing is a
finding. 0 promoted; promotion CLOSED.**
