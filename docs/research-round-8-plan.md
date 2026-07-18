# Research Round 8 — Pre-Registered Plan (Hourly Companion for the R7 Families, PLAN ONLY)

> **Status:** `binding` — pre-registered Round-8 protocol, committed and
> merged BEFORE any Round-8 sweep, backtest, replay, grid code, or outcome
> exists. **PLAN ONLY: this document's own session runs NOTHING — executing
> Round 8 (including committing the grids + tests below to
> `trading_lab.sweeps` and cloning the runner) is a FUTURE session's
> separately claimed slice** (plan-before-outcome, the ORDER 014 round-6
> precedent: plan PR then run PR, two claims). **POST-HOLDOUT, DEV-ONLY: the
> holdout is SPENT and promotion is CLOSED.** Every hypothesis, method, and
> KEEP/KILL rule below is stated in advance; a KEEP anywhere in Round 8 means
> *dev-candidate only*, never a finding. The multiple-testing bar is UNCHANGED
> from Rounds 2–7 (`trading_lab.promotion.min_tstat`, ~2.638 at K=12) — no
> bar-lowering anywhere in this round; K only ever rises with variants actually
> tried.

## Provenance, scope, and the direction pick (justified here)

Round 7D closed (PR #148; [research-round-7d-results.md](research-round-7d-results.md))
at 0 KEEP-dev / 6 KILL / 0 KILL-SIG of 6 lanes, 0 promoted, program cumulative
**5,601 registered configs — 0 promoted anywhere**. Rounds 7, 7C, and 7D all
graded on the COMMITTED DAILY caches; not one Round-7 slice touched an hourly
bar. That was deliberate: every Round-7 plan recorded "any hourly slice" in its
"directions considered and NOT registered" list, on the standing round-6
finding that hourly is **a KILL amplifier at baseline costs (15/16 KILL in
R6-C)** and the R5-B precedent that the program's only prior hourly KEEP was
demoted for single-window luck.

This plan picks **the declared-but-deferred hourly question** (overnight menu
proposal #03): re-sweep the two newest single-instrument families —
`drawdown_reversion` (R7-A) and `high_proximity` (R7-B) — VERBATIM on the
committed 8-ticker hourly cache. It is the lowest-cost timeframe-companion
entry: NO new strategy code, NO new parameter territory, NO fetch, NO owner
action — the same two families and the same two 12-variant grids re-registered
on hourly bars, exactly the Round-3 slice-5/14/15 and Round-6 slice R6-C
timeframe-expansion precedent. Menu #03 asks a question R7-A and R7-B each leave
open: the daily verdicts nulled (R7-A 3 KEEP-dev / 12 KILL, R7-B 2 KEEP-dev /
13 KILL) — does moving the SAME families to a shorter-horizon, higher-churn
hourly bar do anything but null harder?

Honest registered prior, carried from Rounds 6–7 verbatim in effect: hourly is
the program's thinnest evidence-per-config and its most reliable KILL amplifier.
The expected Round-8 outcome is more honest nulls (most/all 16 lanes KILL,
plausibly KILL-SIG lanes as hourly churn is cost-eaten), and that is a complete
deliverable. This round adds NO family, NO cache, NO holdout access; it isolates
one variable — bar frequency — on two already-graded families.

Directions considered and NOT registered, recorded for honesty: any new family
(this round is a pure timeframe companion, by design); any holdout access
(SPENT); any fetch or new ticker (the hourly cache covers only 8 of the 14
XSEC names — a 14-name hourly portfolio would be owner-gated, explicitly out of
scope below); an hourly XSEC portfolio (same fetch wall); any bar-lowering
(`min_tstat(K)` stays at each lane's honestly-counted K=12); and re-running the
DAILY R7 grids (already graded — this is the hourly companion, not a re-run).

## The three standing requirements (rails for this round, restated as binding)

1. **Selection-fair gate on every lane** ([selection-fair-gate.md](selection-fair-gate.md),
   which stamps the standing decision; PR #111): every Round-8 runner runs
   `trading_lab.selection_gate.run_selection_gate` (fidelity guard armed with
   the lane's recorded searched Sharpe) and folds the result through
   `apply_gate` BEFORE writing any verdict; the full gate result block is
   recorded in the lane JSON. A would-be KEEP that fails the gate is KILL the
   day it is minted. The R6-C hourly runner (`run_r6_volume_hourly_sweep.py`)
   ALREADY does exactly this on hourly bars — the R8 runner clones IT.
2. **R5-D fixed-config row in every searched-arm comparison**
   ([research-round-5-results.md](research-round-5-results.md) closing tally
   item 4; standing since Round 6): every lane summary reports `fixed_sharpe`,
   `bench_sharpe`, `searched_sharpe`, and `selection_gap = searched − fixed`
   (informational, no registered threshold). As in Rounds 6–7, the gate's own
   result block satisfies this row for every graded lane — the gate runs on
   EVERY lane, not only would-be KEEPs.
3. **reason_class rollup (standing round-level requirement since Round 7)**
   (PR #121; [selection-fair-gate.md](selection-fair-gate.md) § reason_class):
   the Round-8 results rollup MUST tabulate `reason_class` counts across all
   lanes and treat ANY nonzero `selection_gate.UNGRADEABLE_CLASSES` share as an
   **infrastructure alarm** reported in the results doc and on the heartbeat —
   never as strategy evidence.

## Standing rails (unchanged, restated)

- **Data**: dev rail only via `trading_lab.data.load_ohlcv(ticker, "hourly")` —
  holdout excluded (bars with timestamp ≥ HOLDOUT_START 2025-01-09 never
  loaded), `data/p5holdout/` never read, `unlock_holdout` never passed;
  committed hourly caches only, nothing fetched; `experiments/paper/**`
  untouched.
- **Grading**: Round-2 KEEP/KILL rule (KEEP as dev-candidate iff stitched
  walk-forward OOS Sharpe > same-window B&H benchmark Sharpe AND > 0;
  ties/ambiguity KILL) + ORDER 007 informational t + `classify_verdict`
  KILL-SIG at the mirrored bar + the selection-fair gate. Bar `min_tstat(K)` at
  each lane's honestly-counted K=12 (≈2.638) — never lowered. Promotion
  CLOSED: no Round-8 verdict can promote anything.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults).
- **Walk-forward geometry**: train 1008 / test 252 HOURLY bars, contiguous test
  windows, exactly the R6-C hourly (lab-convention BAR-denominated) geometry.
- **Pre-declaration (sequencing for the run session)**: the run session's FIRST
  code commit adds the grids below to `trading_lab.sweeps` WITH pinning tests in
  `tests/test_sweeps.py`, and only then runs — grids in code before any sweep,
  exactly the Rounds 6–7 mechanics. This plan doc is the binding source the
  tests pin against.
- **Honesty**: nulls and KILLs are first-class deliverables.
- **Runtime caps, no silent truncation**: cap below; a slice that would exceed
  its cap STOPS, records the partial state and the verbatim overrun, and reports
  CAP-HIT (re-registration required) — silent truncation or grid-narrowing
  mid-run is forbidden.

---

## R8 — Hourly companion for the R7 families (`drawdown_reversion` + `high_proximity` × 8 hourly tickers)

- **Motivation**: Round 7 explicitly DECLINED hourly slices — round-6
  re-confirmed hourly as **a KILL amplifier at baseline costs (15/16 KILL in
  R6-C)**, and R5-B showed hourly 5-split single-window luck (the program's only
  prior hourly KEEP was demoted for exactly that). This round answers the
  declared-but-deferred hourly question for the two NEWEST single-instrument
  families UNDER the same plan-before-outcome discipline, with a null prior
  fixed in advance. NO new strategy code — it reuses the committed
  `drawdown_reversion` (R7-A) and `high_proximity` (R7-B) families verbatim; the
  round adds only hourly sweep grids + a runner + pinning tests.
- **Families & grids** (grids committed in the run session's first commit,
  pinned by tests): `drawdown_reversion` and `high_proximity`, reusing the
  IDENTICAL R7 12-variant grids —
  - `_R8_HOURLY_DRAWDOWN_AXES` = the `_R7_DRAWDOWN_AXES` values:
    `lookback` {63, 126, 252} × `entry_dd` {0.10, 0.20} × `exit_frac` {0.5, 1.0}
    = **3 × 2 × 2 = 12 variants**.
  - `_R8_HOURLY_HIGHPROX_AXES` = the `_R7_HIGHPROX_AXES` values:
    `N` {63, 126, 252} × `p` {0.85, 0.90, 0.95, 0.98} = **3 × 4 = 12 variants**.
  - **Declare explicitly**: these window params (`lookback` / `N`
    {63, 126, 252}) are now HOURLY bars — at 6.5 bars/day they span roughly
    **10 / 19 / 39 trading days**, a deliberately SHORTER calendar horizon than
    R7's daily windows (63 / 126 / 252 daily bars ≈ a quarter / half / full
    trading year). This is a TIMEFRAME COMPANION that isolates the
    bar-frequency effect on the same families — the same window NUMBER, a
    different calendar horizon — NOT a re-run of the daily grids and NOT new
    parameter territory. The grid identity with R7 is pinned by tests.
- **Declared adjacency (nearest burned neighbors)**: the daily R7-A
  `drawdown_reversion` and R7-B `high_proximity` lanes (same families, same
  grids, DAILY bars — R7-A 3 KEEP-dev / 12 KILL, R7-B 2 KEEP-dev / 13 KILL) and
  the R6-C `r6-volume-hourly` lane (the timeframe-companion PRECEDENT — different
  families, same 8-ticker hourly cache, 1/16 KEEP-dev / 15 KILL). Structural
  difference from the daily R7 lanes: identical strategy code and grid values,
  but every window number now denominates an HOURLY bar (a shorter calendar
  horizon and higher churn), and the dev rail affords only 5 walk-forward
  splits instead of R7's daily 8–10 — so R8 is the SAME families on a
  DIFFERENT bar frequency, not a new family and not a re-run.
- **Instruments**: the 8-ticker hourly set `R8_HOURLY_INSTRUMENTS` =
  `R6_VOLUME_HOURLY_INSTRUMENTS` (verbatim, the same committed tuple object —
  which is itself `R3_TREND_HOURLY_INSTRUMENTS`): AAPL, AMZN, GLD, GOOGL, META,
  MSFT, NVDA, SLV (config.UNIVERSE order: AAPL, MSFT, NVDA, GOOGL, AMZN, META,
  GLD, SLV). Committed hourly caches for all 8, nothing fetched.
- **Single-instrument config-counting**: each family is a single-instrument
  lane, so `configs = variants × instruments`. Two families × 12 variants each
  × 8 instruments → **(12 + 12) × 8 = 192 registered configs**; **16 lanes**
  (2 families × 8 tickers). Program cumulative **5,601 → 5,793**.
- **Data adequacy (mandatory honesty line)**: the hourly dev rail (bars <
  HOLDOUT_START 2025-01-09) is **~2,476 bars per ticker → 5 walk-forward splits
  at train 1008 / test 252** (`ppy` hourly = 252 × 6.5 = 1638). This SUFFICES to
  run R8 honestly on these 8 tickers with **NO owner-gated fetch**. **Declared
  caveat (registered in advance, not a post-hoc excuse)**: the entire stitched
  OOS is a SINGLE ~8.5-month 2024 regime (5 splits) — the program's thinnest
  evidence-per-config. Any KEEP-dev here carries the R5-B single-window-luck
  caveat and is the WEAKEST possible dev-candidate; this is the exact exposure
  R5-B demoted a prior hourly KEEP for, and it is registered here BEFORE any
  outcome exists.
- **Hypothesis (registered null)**: hourly AMPLIFIES KILLs — both families null
  HARDER on hourly than their daily R7 verdicts (R7-A 3 KEEP-dev / 12 KILL,
  R7-B 2 KEEP-dev / 13 KILL daily). Expect most/all 16 lanes KILL, plausibly
  KILL-SIG lanes (hourly churn is cost-eaten at 5 bps slip + 1 bp comm).
  **Mirror expectation declared**: if a family carried a real short-horizon
  hourly edge, the tighter-band / shorter-window variants (`p = 0.98`,
  `N = 63`; `entry_dd = 0.20`, `lookback = 63`) would out-grade the looser /
  longer ones — the registered expectation is that NO such gradient clears the
  unchanged K=12 bar (≈2.638).
- **Decision rule (per lane, pre-registered)**: Round-2 KEEP/KILL on the
  stitched hourly walk-forward vs same-window B&H, THEN the selection-fair gate
  on EVERY lane (standing rule 1: `run_selection_gate` → `apply_gate`, the R5-D
  fixed-config row — the R6-C hourly runner already does this, clone IT, not the
  R3 xsec runner); `classify_verdict` KILL-SIG at K=12; gate block = the R5-D
  fixed-config row (standing rule 2); reason_class rollup with the mandatory
  UNGRADEABLE infra-alarm line (standing rule 3); promotion CLOSED (no verdict
  promotes); `min_tstat(12)` ≈ 2.638 never lowered; dev caches only via
  `load_ohlcv(ticker, "hourly")` (holdout excluded); costs 5 bps slip + 1 bp
  comm; walk-forward train 1008 / test 252 HOURLY bars.
- **Burden**: 192 new registered configs; 16 lanes; per-lane K=12, bar ≈2.638.
- **Runtime cap**: ≤ 15 minutes wall-clock for the whole slice.

---

## Exact code + tests the run session must add BEFORE any run

To `src/trading_lab/sweeps.py` (mirroring the Round-6 R6-C hourly layout at
`R6_VOLUME_HOURLY_*` and the Round-7 layout at `_R7_DRAWDOWN_AXES` /
`_R7_HIGHPROX_AXES` ff.), NO new strategy modules (reuse R7-A/R7-B verbatim):

- `_R8_HOURLY_DRAWDOWN_AXES` = the `_R7_DRAWDOWN_AXES` values
  (`lookback` {63, 126, 252} × `entry_dd` {0.10, 0.20} × `exit_frac`
  {0.5, 1.0} = 12).
- `_R8_HOURLY_HIGHPROX_AXES` = the `_R7_HIGHPROX_AXES` values
  (`N` {63, 126, 252} × `p` {0.85, 0.90, 0.95, 0.98} = 12).
- `R8_HOURLY_FAMILIES` = the two R7 families (`drawdown_reversion`,
  `high_proximity`).
- `R8_HOURLY_INSTRUMENTS` = `R6_VOLUME_HOURLY_INSTRUMENTS` (the same committed
  8-ticker hourly tuple object).
- `r8_hourly_variants(family)` delegating to the identical R7 expansion (12 per
  family; grid identity with R7 pinned).
- `r8_total_configs()` returning **192** ((12 + 12) × 8), with the program
  cumulative advancing **5,601 → 5,793**.

To `tests/test_sweeps.py`: pins for the `_R8_HOURLY_DRAWDOWN_AXES` and
`_R8_HOURLY_HIGHPROX_AXES` dicts (exact values above, and value-identity with
the R7 axes), the **12 + 12 variant counts**, the instrument set = the
committed hourly-8 (`R8_HOURLY_INSTRUMENTS is R6_VOLUME_HOURLY_INSTRUMENTS`,
same tuple object; the 8 tickers AAPL, AMZN, GLD, GOOGL, META, MSFT, NVDA,
SLV), the **configs = 192** count ((12 + 12) × 8), and the **5,601 → 5,793**
totals (`r8_total_configs()` = 192; program cumulative 5,793). Only after those
tests are green may the R8 runner execute.

Runner `scripts/run_r8_hourly_sweep.py` — cloned from
`scripts/run_r6_volume_hourly_sweep.py` (the R6-C hourly runner, NOT the R3
xsec runner): `timeframe="hourly"`, the two R7 families, train 1008 / test 252
HOURLY bars, the honest first-class insufficient-data verdict for any lane
short of a full split (r3-trend-hourly precedent), and the selection-fair gate
on EVERY lane (`selection_gate.run_selection_gate` → `selection_gate.apply_gate`
before any verdict is written), writing `docs/research-round-8-results.md`.

## Round-level aggregation (pre-registered)

Each of the 16 lanes exits Round 8 with exactly one verdict: KEEP-dev iff it
passes the Round-2 rule AND the selection-fair gate; else KILL (or KILL-SIG per
`classify_verdict`). Results land in a new `docs/research-round-8-results.md`,
reporting: verdict counts, every gate FAIL reason verbatim, full fixed-config
rows (`selection_gap` per lane), the **reason_class table with the
UNGRADEABLE-share infrastructure-alarm line (standing rule 3 — mandatory)**,
best informational t vs the unchanged bar, the per-lane split count with the
single-2024-regime caveat restated for any KEEP-dev, runtime vs cap, and the
burden ledger line (5,601 → 5,793 exactly; any deviation is a registration
violation, not a rounding note). Ledger convention: each lane's searched top
variant LEDGERED with `variants_tried=12`; gate replays are report-only rows in
the lane JSON.

## What round 8 will NOT do

- **No execution in the planning session** — this plan's PR contains no sweep,
  no backtest, no grid code, no runner; running (and the pre-run code commit
  above) is a future session's separately claimed slice.
- **No new families** — pure timeframe companion; reuses R7-A
  `drawdown_reversion` and R7-B `high_proximity` verbatim, no new strategy
  modules.
- **No holdout access** — SPENT; `data/p5holdout/` never read, `unlock_holdout`
  never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched.
- **No data fetching, no new tickers** — the 8 committed hourly caches only.
- **No hourly XSEC portfolio** — the hourly cache covers only 8 of the XSEC-14
  names; a 14-name hourly portfolio would need an owner-gated fetch, explicitly
  out of scope.
- **No bar-lowering** — `min_tstat(K)` at each lane's honestly-counted K=12,
  never lowered.
- **No OOS validation claims, no broker/order/exchange-write code, no live API
  configuration** — research-only, per CONSTITUTION.md.
