# Research Round 6 — Results

> **Status:** `reference` — honest results of the three pre-registered
> Round-6 slices, one dated section per slice, against the protocol in
> [research-round-6-plan.md](research-round-6-plan.md) (merged BEFORE any
> Round-6 outcome existed, PR #116 `c0e6459`). **POST-HOLDOUT, DEV-ONLY:
> the holdout is SPENT and promotion is CLOSED.** Nothing on this page is
> an out-of-sample claim; a KEEP means *dev-candidate only*, and
> nulls/KILLs are first-class results. The multiple-testing bar is
> unchanged (`trading_lab.promotion.min_tstat`, ~2.638 at K=12; only ever
> rises). Round 6 is the FIRST round graded under the selection-fair
> standing gate ([selection-fair-gate.md](selection-fair-gate.md)): the
> gate ran on EVERY lane, and its result block is each lane's R5-D
> fixed-config row.

**Round headline: the registered expectation (mostly honest nulls) is
confirmed — 3 KEEP-dev / 47 KILL / 8 KILL-SIG across the 58
pre-registered lanes, 0 promoted, best informational t anywhere 0.60
(BTC-USD daily `obv_trend`) against the unchanged 2.638 bar. The
program's first volume-based families produce 3 weak KEEP-devs and no
evidence that the volume channel adds information (confirmed-arm vs
pure-OBV full-period mean Sharpe 0.471 vs 0.479 — indistinguishable).
The overnight-gap family is the sharpest null the program has ever
recorded: 0 KEEP / 12 KILL with 7 KILL-SIG — post-gap drift/reversion is
significantly HARMFUL net of costs on this surface, in both mirror
theses. The standing gate ran on all 58 lanes (17 PASS / 41 FAIL) and
demoted nothing: every Round-2-rule KEEP independently passed its
selection-free replay, and `selection_gap > 0` on only 2 of 58 lanes —
walk-forward re-selection lost to the fixed config almost everywhere,
the R5-D lesson at scale. Round-6 burden: 696 new registered configs;
program cumulative 4359 → 5055. Runtime caps nowhere near hit
(25.6 / 12.0 / 7.9 s vs 1200 / 900 / 1200 s); no CAP-HIT, nothing
truncated, no slice remains unrun.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Runtime vs cap |
|---|---|---|---|---|---|---|
| R6-A `r6-volume` (daily) | 30 | 2 | 27 | 1 | 9 / 21 | 25.6 s / 1200 s |
| R6-B `r6-gap` (daily) | 12 | 0 | 5 | 7 | 0 / 12 | 12.0 s / 900 s |
| R6-C `r6-volume-hourly` | 16 | 1 | 15 | 0 | 8 / 8 | 7.9 s / 1200 s |
| **Round 6** | **58** | **3** | **47** | **8** | **17 / 41** | none hit |

Machine-readable rollups: one `summary.json` per slice directory —
[`experiments/sweeps/r6-volume/`](../experiments/sweeps/r6-volume/),
[`experiments/sweeps/r6-gap/`](../experiments/sweeps/r6-gap/),
[`experiments/sweeps/r6-volume-hourly/`](../experiments/sweeps/r6-volume-hourly/)
(runners `scripts/run_r6_volume_sweep.py`, `scripts/run_r6_gap_sweep.py`,
`scripts/run_r6_volume_hourly_sweep.py`).

## Reading the per-lane tables

Every lane below carries its R5-D fixed-config row (standing rule 2 —
satisfied by the gate block in the lane JSON): `searched` is the stitched
walk-forward OOS Sharpe (1008/252 bars, contiguous test windows, baseline
costs 5 bps + 1 bp), `bench` the same-window B&H Sharpe, `fixed` the
selection-free replay of the lane's committed top full-period variant on
the identical windows, `gap = searched − fixed` (informational, no
registered threshold). `t` is the ORDER 007 informational t at the lane's
K=12 (bar 2.638, never lowered). Verdict = Round-2 rule, then
`classify_verdict` (KILL-SIG at the mirrored bar), then
`apply_gate` — the gate only ever demotes. Gate FAIL reasons this round
are ALL one class — `fixed-config replay does not beat same-window B&H
with a positive Sharpe (fixed <x>, bench <y>) — the searched edge does
not survive selection-free` with the lane's own numbers (visible in the
`fixed`/`bench` columns) — and the verbatim strings are recorded in every
lane JSON's `selection_gate.reason` and each slice `summary.json`. Zero
UNGRADEABLE conditions and zero fidelity-guard failures occurred: every
searched-arm replay reproduced its lane's recorded stitched OOS Sharpe
within 1e-8.

## R6-A — volume-confirmation families (2026-07-13)

**Headline: the registered hypothesis ("volume confirmation does not
create edge on this surface") is confirmed. 2 KEEP / 27 KILL /
1 KILL-SIG of 30 lanes; both KEEPs are `obv_trend` (BTC-USD searched
1.011 vs bench 0.821, t = 0.60; META 0.717 vs 0.653, t = 0.18 — both
pass the gate, both nowhere near the 2.638 bar). `mfi_reversion` KEEPs
NOWHERE on the daily surface (0/15) and produces the slice's one
KILL-SIG (MSFT, t = −2.89 ≤ −2.638) — the volume-weighted oscillator
grades no better than its price-only siblings. The within-family control
arm answers the registered question against the volume channel:
confirmed (`price_confirm=True`) arms' full-period mean Sharpe is 0.471
vs 0.479 for pure OBV — the price filter adds nothing, and top
full-period variants split 7 confirmed / 8 pure across the 15 tickers.**

- **Pre-declaration honored**: grids verbatim from
  `sweeps._R6_VOLUME_AXES` (12 + 12 variants, pinned by tests), the
  committed 15-ticker daily surface (same tuple object as R4-F), runner
  asserts the counts before running. 360 registered configs.
- **Method** (registered): full-period bookkeeping rows per variant;
  1008/252 walk-forward (8–10 splits per lane, data through 2025-01-08
  dev rail); Round-2 KEEP/KILL rule; `classify_verdict` at K=12; the
  standing gate on EVERY lane with the fidelity guard armed (30/30
  reproduced within 1e-8).
- **Gate, read honestly**: 9 PASS / 21 FAIL, 0 KEEPs demoted — the gate
  was never load-bearing this slice. Its 7 PASS-but-KILL lanes (e.g.
  NVDA `obv_trend`: fixed 1.427 beats bench 1.295 while the searched arm
  1.293 loses by 0.002 — the narrowest miss of the round) are the
  measured cost of in-window re-selection: `selection_gap < 0` on 29 of
  30 lanes (only TLT `mfi_reversion` +0.164, itself a KILL).
- **The KEEPs, read honestly**: both are trend-following OBV on
  instruments whose daily lanes already hold KEEP-devs of price-only
  families (BTC-USD `bollinger_breakout`, META `ichimoku_trend`) — the
  cheapest reading is that OBV-above-SMA is a noisy proxy for the same
  trends, not a new information channel. Dev-candidates only.
- **Artifacts**: 30 lane JSONs + `summary.json` in
  [`experiments/sweeps/r6-volume/`](../experiments/sweeps/r6-volume/);
  top full-period variant per lane LEDGERED with `variants_tried=12`
  (Round-3 convention, 30 rows); gate replays report-only inside the
  lane JSONs (R4-B precedent); `experiments/index.jsonl` rebuilt.
  Runtime **25.6 s** (cap 1200 s — not hit, nothing skipped).
- **Burden ledger**: 360 new registered configs; program cumulative
  4359 → **4719**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| obv_trend · AAPL | 0.835 | 0.963 | 1.137 | -0.302 | -0.405 | PASS | **KILL** |
| mfi_reversion · AAPL | 0.631 | 0.963 | 0.800 | -0.170 | -1.050 | FAIL | **KILL** |
| obv_trend · AMZN | 0.287 | 0.763 | 0.584 | -0.297 | -1.505 | FAIL | **KILL** |
| mfi_reversion · AMZN | 0.174 | 0.763 | 0.677 | -0.503 | -1.861 | FAIL | **KILL** |
| obv_trend · BTC-USD | 1.011 | 0.821 | 1.060 | -0.049 | 0.601 | PASS | **KEEP** |
| mfi_reversion · BTC-USD | 0.096 | 0.821 | 0.372 | -0.276 | -2.293 | FAIL | **KILL** |
| obv_trend · GLD | 0.122 | 0.400 | 0.136 | -0.014 | -0.882 | FAIL | **KILL** |
| mfi_reversion · GLD | 0.374 | 0.400 | 0.599 | -0.225 | -0.084 | PASS | **KILL** |
| obv_trend · GOOGL | 0.289 | 0.720 | 0.609 | -0.320 | -1.364 | FAIL | **KILL** |
| mfi_reversion · GOOGL | 0.387 | 0.720 | 0.740 | -0.353 | -1.053 | PASS | **KILL** |
| obv_trend · JPM | 0.405 | 0.645 | 0.617 | -0.212 | -0.758 | FAIL | **KILL** |
| mfi_reversion · JPM | 0.530 | 0.645 | 0.681 | -0.151 | -0.363 | PASS | **KILL** |
| obv_trend · META | 0.717 | 0.653 | 0.895 | -0.178 | 0.180 | PASS | **KEEP** |
| mfi_reversion · META | -0.217 | 0.653 | 0.103 | -0.320 | -2.461 | FAIL | **KILL** |
| obv_trend · MSFT | 0.495 | 1.101 | 0.734 | -0.239 | -1.918 | FAIL | **KILL** |
| mfi_reversion · MSFT | 0.187 | 1.101 | 0.653 | -0.466 | -2.892 | FAIL | **KILL-SIG** |
| obv_trend · NVDA | 1.293 | 1.295 | 1.427 | -0.134 | -0.007 | PASS | **KILL** |
| mfi_reversion · NVDA | 0.477 | 1.295 | 0.539 | -0.063 | -2.589 | FAIL | **KILL** |
| obv_trend · QQQ | 0.560 | 0.871 | 0.804 | -0.243 | -0.982 | FAIL | **KILL** |
| mfi_reversion · QQQ | 0.501 | 0.871 | 0.703 | -0.203 | -1.171 | FAIL | **KILL** |
| obv_trend · SLV | -0.286 | 0.170 | 0.159 | -0.445 | -1.442 | FAIL | **KILL** |
| mfi_reversion · SLV | 0.157 | 0.170 | 0.478 | -0.321 | -0.041 | PASS | **KILL** |
| obv_trend · SPY | 0.397 | 0.761 | 0.710 | -0.312 | -1.149 | FAIL | **KILL** |
| mfi_reversion · SPY | 0.544 | 0.761 | 0.746 | -0.202 | -0.686 | FAIL | **KILL** |
| obv_trend · TLT | 0.065 | 0.196 | 0.194 | -0.129 | -0.415 | FAIL | **KILL** |
| mfi_reversion · TLT | -0.003 | 0.196 | -0.167 | 0.164 | -0.631 | FAIL | **KILL** |
| obv_trend · TSLA | 0.519 | 0.760 | 0.771 | -0.252 | -0.763 | PASS | **KILL** |
| mfi_reversion · TSLA | 0.548 | 0.760 | 0.619 | -0.071 | -0.670 | FAIL | **KILL** |
| obv_trend · XOM | -0.137 | 0.294 | 0.162 | -0.299 | -1.363 | FAIL | **KILL** |
| mfi_reversion · XOM | -0.297 | 0.294 | 0.208 | -0.505 | -1.868 | FAIL | **KILL** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 30 | 2 | 27 | 1 | 9 | 21 | 0 |

## R6-B — overnight-gap family (2026-07-13)

**Headline: the sharpest null in six rounds, stronger than the
registered hypothesis. 0 KEEP / 5 KILL / 7 KILL-SIG of 12 lanes —
post-gap next-day drift/reversion is not merely unexploitable net of
costs, it is SIGNIFICANTLY harmful on 7 of 12 tickers (informational t
down to −4.01 on AAPL, through the mirrored −2.638 bar at K=12). The
searched walk-forward's stitched Sharpe is negative on 9 of 12 lanes,
`selection_gap < 0` on ALL 12 (−0.07 to −1.00), and the gate FAILs all
12 — no configuration of either mirror thesis survives anywhere. Fade
and follow cannot both be right per instrument; on this surface neither
is: fade arms' full-period mean Sharpe −0.117, follow −0.004, with fade
picked as the top full-period variant on 8 of 12 tickers and still never
beating B&H out of sample.**

- **Pre-declaration honored**: grid verbatim from `sweeps._R6_GAP_AXES`
  (mode × gap_atr × hold = 12, `atr_period` frozen at 14, both mirror
  theses in one grid), the 12-ticker slice-8 mixed set, BTC-USD excluded
  (asserted by the runner — a 24/7 market has no overnight session). 144
  registered configs.
- **Honesty note carried from the plan**: the engine fills at bar t+1's
  open, so this slice tested post-gap drift/reversion over the following
  bars — the classic same-day overnight-capture claim was NOT testable
  and is NOT graded by these KILLs.
- **Method / gate**: identical to R6-A (Round-2 rule, `classify_verdict`
  at K=12, gate on every lane; fidelity guard 12/12 within 1e-8). Gate 0
  PASS / 12 FAIL, 0 KEEPs to demote — every fixed-config replay ALSO
  lost to B&H (10 of 12 fixed replays still positive in absolute terms,
  but none above its benchmark), so the searched failure is not a
  selection artifact: the family itself has no edge here.
- **Artifacts**: 12 lane JSONs + `summary.json` in
  [`experiments/sweeps/r6-gap/`](../experiments/sweeps/r6-gap/); top
  full-period variant per lane LEDGERED with `variants_tried=12` (12
  rows); `experiments/index.jsonl` rebuilt. Runtime **12.0 s** (cap
  900 s — not hit, nothing skipped).
- **Burden ledger**: 144 new registered configs; program cumulative
  4719 → **4863**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| overnight_gap · AAPL | -0.307 | 0.963 | 0.694 | -1.000 | -4.014 | FAIL | **KILL-SIG** |
| overnight_gap · MSFT | 0.147 | 1.101 | 0.492 | -0.345 | -3.018 | FAIL | **KILL-SIG** |
| overnight_gap · NVDA | 0.102 | 1.295 | 0.423 | -0.321 | -3.773 | FAIL | **KILL-SIG** |
| overnight_gap · GOOGL | -0.536 | 0.720 | 0.136 | -0.672 | -3.971 | FAIL | **KILL-SIG** |
| overnight_gap · AMZN | -0.116 | 0.763 | 0.420 | -0.536 | -2.778 | FAIL | **KILL-SIG** |
| overnight_gap · META | -0.116 | 0.653 | -0.047 | -0.069 | -2.175 | FAIL | **KILL** |
| overnight_gap · GLD | -0.438 | 0.400 | 0.083 | -0.521 | -2.650 | FAIL | **KILL-SIG** |
| overnight_gap · SLV | -0.015 | 0.170 | 0.153 | -0.169 | -0.585 | FAIL | **KILL** |
| overnight_gap · SPY | -0.067 | 0.761 | 0.206 | -0.273 | -2.618 | FAIL | **KILL** |
| overnight_gap · QQQ | -0.299 | 0.871 | 0.111 | -0.410 | -3.699 | FAIL | **KILL-SIG** |
| overnight_gap · TSLA | 0.087 | 0.760 | 0.355 | -0.268 | -2.127 | FAIL | **KILL** |
| overnight_gap · TLT | -0.332 | 0.196 | -0.175 | -0.157 | -1.670 | FAIL | **KILL** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 12 | 0 | 5 | 7 | 0 | 12 | 0 |

## R6-C — volume families on hourly bars (2026-07-13)

**Headline: the registered hourly expectation (KILLs MORE likely than
daily) holds — 1 KEEP / 15 KILL / 0 KILL-SIG of 16 lanes, and the sole
KEEP (AMZN `mfi_reversion`, searched 0.942 vs bench 0.615, t = 0.29,
gate PASS) rests on the SAME 5-split short-history geometry that R5-B
used to demote the program's only previous hourly KEEP — the
single-window-luck caveat registered in the plan attaches to it
explicitly, and it should be treated as the round's least trustworthy
KEEP. `obv_trend` KILLs on all 8 hourly tickers. The hourly
`selection_gap` spread is the widest of the round (+0.38 to −1.89,
negative on 15 of 16): with only 5 splits, in-window re-selection is
almost pure noise — three KILLed lanes' FIXED configs beat their
benchmarks handily (NVDA `mfi_reversion` fixed 2.238 vs bench 1.387;
GOOGL both families) while their searched arms lost, exactly the failure
mode the gate exists to price.**

- **Pre-declaration honored**: grids IDENTICAL to R6-A (pinned by tests
  and re-asserted by the runner at startup), the committed 8-ticker
  hourly surface (same tuple object as r3-trend-hourly). 192 registered
  configs. 1008/252 BARS on hourly data (lab convention), 5 splits per
  lane (~2,476 dev-rail bars per cache, 2023-08 → 2025-01).
- **Known-weakness note honored**: the plan's recorded hourly
  zero-volume-bars fact (≤ 10 per ticker) produced zero UNGRADEABLE
  lanes — `mfi_reversion` treats zero flow as flat by construction and
  every lane graded normally (no INSUFFICIENT-DATA verdicts either).
- **Method / gate**: identical to R6-A (Round-2 rule, `classify_verdict`
  at K=12, gate on every lane; fidelity guard 16/16 within 1e-8). Gate 8
  PASS / 8 FAIL, 0 KEEPs demoted. The 7 PASS-but-KILL lanes are the
  slice's honest story (fixed beats bench, searched does not).
- **Artifacts**: 16 lane JSONs + `summary.json` in
  [`experiments/sweeps/r6-volume-hourly/`](../experiments/sweeps/r6-volume-hourly/);
  top full-period variant per lane LEDGERED with `variants_tried=12` (16
  rows); `experiments/index.jsonl` rebuilt. Runtime **7.9 s** (cap
  1200 s — not hit, nothing skipped).
- **Burden ledger**: 192 new registered configs; program cumulative
  4863 → **5055**.

| Lane (family · instrument) | searched | bench | fixed | gap | t (K=12) | gate | verdict |
|---|---|---|---|---|---|---|---|
| obv_trend · AAPL | -0.302 | 1.570 | 0.674 | -0.977 | -1.642 | FAIL | **KILL** |
| mfi_reversion · AAPL | 1.323 | 1.570 | 0.938 | 0.384 | -0.217 | FAIL | **KILL** |
| obv_trend · MSFT | -0.799 | 0.148 | -0.174 | -0.624 | -0.830 | FAIL | **KILL** |
| mfi_reversion · MSFT | -0.519 | 0.148 | 0.252 | -0.770 | -0.585 | PASS | **KILL** |
| obv_trend · NVDA | 0.095 | 1.387 | 0.201 | -0.106 | -1.134 | FAIL | **KILL** |
| mfi_reversion · NVDA | 0.448 | 1.387 | 2.238 | -1.790 | -0.824 | PASS | **KILL** |
| obv_trend · GOOGL | 0.493 | 1.010 | 1.470 | -0.976 | -0.453 | PASS | **KILL** |
| mfi_reversion · GOOGL | 0.459 | 1.010 | 2.147 | -1.688 | -0.483 | PASS | **KILL** |
| obv_trend · AMZN | -0.252 | 0.615 | 0.096 | -0.348 | -0.760 | FAIL | **KILL** |
| mfi_reversion · AMZN | 0.942 | 0.615 | 1.144 | -0.202 | 0.287 | PASS | **KEEP** |
| obv_trend · META | -0.419 | 0.494 | -0.190 | -0.229 | -0.801 | FAIL | **KILL** |
| mfi_reversion · META | -0.832 | 0.494 | 1.062 | -1.894 | -1.163 | PASS | **KILL** |
| obv_trend · GLD | 1.222 | 2.056 | 1.249 | -0.028 | -0.731 | FAIL | **KILL** |
| mfi_reversion · GLD | 1.826 | 2.056 | 2.468 | -0.642 | -0.202 | PASS | **KILL** |
| obv_trend · SLV | -0.345 | 1.185 | 0.390 | -0.736 | -1.342 | FAIL | **KILL** |
| mfi_reversion · SLV | 1.148 | 1.185 | 1.984 | -0.836 | -0.032 | PASS | **KILL** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate |
|---|---|---|---|---|---|---|
| 16 | 1 | 15 | 0 | 8 | 8 | 0 |

## Round 6 — closing tally (2026-07-13)

All three pre-registered Round-6 slices ran top-down against the plan
merged before any outcome existed. One-line verdicts:

| Slice | One-line verdict |
|---|---|
| R6-A volume daily | **2/30 KEEP-dev** (both `obv_trend`: BTC-USD t 0.60, META t 0.18), 1 KILL-SIG (MSFT `mfi_reversion` −2.89); the volume channel adds nothing the control arm can detect |
| R6-B overnight gap | **0/12 KEEP, 7 KILL-SIG** — the program's sharpest null; both mirror theses harmful net of costs, gate 0/12 |
| R6-C volume hourly | **1/16 KEEP-dev** (AMZN `mfi_reversion`, t 0.29, 5 splits — carries the registered R5-B single-window-luck caveat) |

- **Cumulative burden**: Round 6 registered **696 new configs**
  (360 + 144 + 192, exactly as pre-declared in `trading_lab.sweeps` and
  pinned by tests), taking the program cumulative from 4359 to **5055**
  (`sweeps.r6_total_configs()`). No K was counted down and no bar was
  lowered (informational t graded at each lane's K=12 throughout).
- **Runtime caps**: none hit (slice runtimes 7.9–25.6 s against caps of
  900–1200 s); nothing was truncated, no lanes skipped, **no CAP-HIT
  anywhere, no slice remains unrun**.
- **The standing gate's first round, read honestly**: it ran on all 58
  lanes (fidelity guard 58/58 within 1e-8, zero UNGRADEABLE) and
  demoted zero KEEPs — every Round-2-rule KEEP also passed
  selection-free. Its measured contribution is the fixed-config row on
  every lane: `selection_gap > 0` on only 2 of 58 (TLT `mfi_reversion`
  daily +0.164, AAPL `mfi_reversion` hourly +0.384 — both KILLs), and 14
  lanes across the round show gate PASS with a KILLed searched arm.
  Walk-forward re-selection subtracted value almost everywhere it was
  measured this round — R5-D's "selection variance, not signal" now
  holds on 58 fresh lanes, most extremely on the 5-split hourly surface.
- **Deviations from the pre-registration**: none of method. One
  mechanization the plan left implicit is recorded here: the runtime cap
  is enforced as a check before each lane starts (a slice that reaches
  its cap stops before the next lane and records the skipped lanes in
  `summary.json`) — it was never triggered. The
  degenerate-Sharpe guard (KILL with `promotion_grade` marked "not
  computable" if a stitched Sharpe were NaN) was likewise never
  triggered.
- **0 promoted — promotion remains CLOSED, holdout SPENT.** The three
  KEEP-devs are dev-candidates only (best t 0.60 vs bar 2.638 — nothing
  within a factor of 4 of significance); genuine OOS validation of any
  KEEP-dev stays OWNER-GATED behind a new pre-registered protocol on
  post-2026 data.
- **What the round actually established**: (1) the volume column — the
  last untouched data channel in the committed caches — does not carry
  exploitable information on this surface, by the pre-registered
  control-arm test (confirmed 0.471 vs pure 0.479) and by 46 volume
  lanes yielding 3 weak KEEPs; (2) the overnight gap on daily bars is
  the program's first *significantly harmful* family (7 KILL-SIG of 12,
  t to −4.01) — an honest, publishable negative; (3) hourly bars remain
  a KILL amplifier at baseline costs (15/16), as registered; (4) the
  selection-fair gate is cheap (58 gate replays inside 46 s of total
  slice runtime) and its fixed-config rows are the round's most
  informative artifact even when the gate itself demotes nothing.

Round 6 is closed. Three slices, three honest answers, zero findings,
zero cap-hits, three weak dev-candidates, and both genuinely new idea
classes graded: one null, one significantly harmful. Anything further
still needs new data (OWNER-GATED) or a genuinely different idea class.
