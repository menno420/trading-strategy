# Research Round 7C — Pre-Registered Plan (Drawdown × High-Proximity Conjunction, PLAN ONLY)

> **Status:** `binding` — pre-registered Round-7C protocol, committed and
> merged BEFORE any Round-7C sweep, backtest, replay, grid code, or outcome
> exists. **PLAN ONLY: this document's own session runs NOTHING — executing
> Round 7C (including committing the grid + tests below to
> `trading_lab.sweeps`) is a FUTURE session's separately claimed slice**
> (plan-before-outcome, the ORDER 014 round-6 precedent: plan PR then run
> PR, two claims). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT
> and promotion is CLOSED.** Every hypothesis, method, and KEEP/KILL rule
> below is stated in advance; a KEEP anywhere in Round 7C means
> *dev-candidate only*, never a finding. The multiple-testing bar is
> UNCHANGED from Rounds 2–7 (`trading_lab.promotion.min_tstat`, ~2.638 at
> K=12) — no bar-lowering anywhere in this round; K only ever rises with
> variants actually tried.

## Provenance, scope, and the direction pick (justified here)

Round 7 closed (PR #141; [research-round-7-results.md](research-round-7-results.md))
at 5 KEEP-dev / 25 KILL / 0 KILL-SIG of 30 lanes, 0 promoted, best
informational t 1.195 (BTC-USD `high_proximity`) vs the 2.638 bar, program
cumulative **5,415 registered configs — 0 promoted anywhere**. R7 graded two
genuinely new families — `drawdown_reversion` (R7-A) and `high_proximity`
(R7-B) — but ONLY IN ISOLATION: each is a single-signal STATE lane, and the
plan never evaluated any interaction between them.

This plan picks **the first Round-7 INTERACTION family** (overnight menu
proposal #01): the drawdown × high-proximity CONJUNCTION. It is the same
lowest-cost option-2 entry Round 7 used — genuinely new idea family on the
COMMITTED daily caches only, reading only price columns already served by the
dev rail, no owner action, no fetch, compute in the Round-7 range (R7 ran 360
configs in ~19 s total). Menu #01 asks a question R7-A and R7-B each leave
open: does the conjunction of a long-horizon washout AND a short-horizon
recovery — a decision surface neither component evaluates — carry information
the components lack?

Honest registered prior, carried from Round 7 verbatim in effect: three round
closings before R7, and R7 itself, all predict the null — the expected
Round-7C outcome is more honest nulls (most lanes KILL), and that is a complete
deliverable. R7-A nulled (3 KEEP-dev / 12 KILL, 0 KILL-SIG) and R7-B nulled
(2 KEEP-dev / 13 KILL, 0 KILL-SIG, best t 1.195), 0 promoted between them —
the registered prior for their conjunction is the same.

Round 7C registers **one genuinely new family on the COMMITTED daily caches
only** (`washout_recovery`), reading only price columns already served by the
dev rail, structurally distinct from all ~28 burned families and from its own
two nearest neighbors (R7-A and R7-B). Adjacency is declared in advance in the
slice below (nearest burned neighbors: `drawdown_reversion`, `high_proximity`)
with the exact structural difference stated, so "new family vs variant" cannot
be re-litigated after outcomes.

Directions considered and NOT registered, recorded for honesty: any hourly
slice (Round 6 re-confirmed hourly as a KILL amplifier at baseline costs;
the marginal evidence per config is the program's worst); any calendar family
(R4-F burned the class at 0/75 with 30 KILL-SIG); anything needing a fetch
(owner-gated); the `data/p2ext/` extended caches (2 tickers — too thin); and a
single-window collapse of this family (see the constraint below — a single
window makes "washed out yet recovering" a contradiction, so it is a registered
constraint, not a variant).

## The three standing requirements (rails for this round, restated as binding)

1. **Selection-fair gate on every lane** ([selection-fair-gate.md](selection-fair-gate.md),
   which stamps the standing decision; PR #111): every Round-7C runner runs
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
   § reason_class): the Round-7C results rollup MUST tabulate
   `reason_class` counts across all lanes and treat ANY nonzero
   `selection_gate.UNGRADEABLE_CLASSES` share as an **infrastructure
   alarm** reported in the results doc and on the heartbeat — never as
   strategy evidence.

## Standing rails (unchanged, restated)

- **Data**: dev rail only via `trading_lab.data.load_ohlcv` — holdout
  excluded, `data/p5holdout/` never read, `unlock_holdout` never passed;
  committed caches only, nothing fetched; `experiments/paper/**`
  untouched.
- **Grading**: Round-2 KEEP/KILL rule (KEEP as dev-candidate iff stitched
  walk-forward OOS Sharpe > same-window B&H benchmark Sharpe AND > 0;
  ties/ambiguity KILL) + ORDER 007 informational t + `classify_verdict`
  KILL-SIG at the mirrored bar + the selection-fair gate. Bar
  `min_tstat(K)` at each lane's honestly-counted K — never lowered.
  Promotion CLOSED: no Round-7C verdict can promote anything.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults).
- **Walk-forward geometry**: train 1008 / test 252 daily bars, contiguous
  test windows, exactly as Rounds 2–7.
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

## R7-C — Washout-recovery conjunction family (`washout_recovery` × 15 daily tickers)

- **Motivation**: R7-A (`drawdown_reversion`) and R7-B (`high_proximity`)
  each nulled in isolation. Menu #01 asks whether their CONJUNCTION carries
  information the components lack: a lane long ONLY when the close is both
  deeply washed out from a LONG-horizon peak AND simultaneously reclaiming a
  SHORT-horizon high — "washed out from the long-horizon peak yet reclaiming a
  short-horizon high". Neither component evaluates that decision surface, and
  the conjunction is not reducible to either.
- **Family** (implementation + causality tests in the run session's first
  commit): `washout_recovery`. Signal — all causal, per-bar memoryless
  state, engine fills at t+1 open:
  - `peak_long[t] = max(close[t−W_dd+1 … t])` (trailing LONG window,
    includes bar t); `dd_long[t] = close[t] / peak_long[t] − 1` (≤ 0).
    "Washed out" iff `dd_long[t] <= −entry_dd`.
  - `max_short[t] = max(close[t−W_prox+1 … t])` (trailing SHORT window,
    includes bar t). "Recovering" iff `close[t] >= p × max_short[t]`.
  - Position: long (1.0) iff washed-out AND recovering SIMULTANEOUSLY;
    flat (0.0) otherwise. Warm-up flat until both windows have data
    (`max(W_dd, W_prox)` bars).
  - The two windows are DISTINCT (long `W_dd` for the big-picture drawdown,
    short `W_prox` for the local recovery) — that distinctness is what makes
    "washed out from the long-horizon peak yet reclaiming a short-horizon
    high" expressible. A single-window version collapses to a contradiction
    (being at/near the trailing high AND ≥ `entry_dd` below that same
    trailing high cannot both hold), so **`W_prox < W_dd` is a registered
    constraint**, not a tunable variant.
  - All indexing causal (both windows through bar t use closes ≤ t; fills at
    t+1 open as always).
- **Declared adjacency (nearest burned neighbors)**: R7-A
  `drawdown_reversion` (pure long-window drawdown STATE, no proximity, with a
  hysteresis exit) and R7-B `high_proximity` (pure single-window proximity
  STATE, no drawdown). Structural difference: R7-C is the CONJUNCTION of a
  long-horizon washout AND a short-horizon recovery on TWO DISTINCT windows —
  a decision surface neither R7-A nor R7-B evaluates, and not reducible to
  either (a lane long ONLY in the intersection of "deep from the 252-bar peak"
  and "at/near the ≤63-bar high"). R7-A has no proximity term and carries a
  hysteresis exit; R7-B has no drawdown term and one window; R7-C conditions
  on both states at once on two windows with no hysteresis.
- **Hypothesis (registered)**: the conjunction does NOT beat buy-and-hold net
  of costs on this surface — most lanes KILL. R7-A and R7-B each nulled (R7-A
  3 KEEP-dev / 12 KILL, R7-B 2 KEEP-dev / 13 KILL, best t 1.195, 0 promoted —
  cite [research-round-7-results.md](research-round-7-results.md)), and
  "washed-out but recovering" is a story the single-name daily surface has
  repeatedly failed to reward. **Mirror expectation declared**: if the
  conjunction carried information the components lack, tighter recovery bands
  (`p = 0.95`, short `W_prox = 21`) on deeper washouts (`entry_dd = 0.20`)
  should out-grade looser ones — the registered expectation is that no such
  gradient clears the unchanged 2.638 bar.
- **Grid** (to be committed as `sweeps._R7C_CONJUNCTION_AXES`, pinned by
  tests): `W_dd` {252} × `entry_dd` {0.10, 0.20} × `W_prox` {21, 42, 63} ×
  `p` {0.90, 0.95} = **2 × 3 × 2 = 12 variants** (the lab-standard per-lane
  K=12). Registered constraints: `W_prox < W_dd`, `W_dd >= 2`, `W_prox >= 2`,
  `0 < entry_dd < 1`, `0 < p <= 1`.
- **Instruments**: `R7C_INSTRUMENTS = R7_INSTRUMENTS` (verbatim, the same
  tuple object — the committed 15-ticker daily surface of R7-A/R7-B). 15
  lanes; **180 registered configs**; program cumulative **5,415 → 5,595**.
- **Decision rule (per lane, pre-registered)**: Round-2 KEEP/KILL on the
  searched walk-forward, THEN the selection-fair gate on every lane
  (standing rule 1: `run_selection_gate` → `apply_gate`, the R5-D
  fixed-config row); `classify_verdict` KILL-SIG at K=12; gate block = the
  R5-D fixed-config row (standing rule 2); reason_class rollup with the
  mandatory UNGRADEABLE infra-alarm line (standing rule 3); promotion CLOSED
  (no verdict promotes); `min_tstat` bar never lowered.
- **Burden**: 180 new registered configs; per-lane K=12, bar ~2.638.
- **Runtime cap**: ≤ 15 minutes wall-clock for the whole slice.

---

## Exact code + tests the run session must add BEFORE any run

To `src/trading_lab/strategies/washout_recovery.py`: the `washout_recovery`
family with causality tests — signal at bar t must be INVARIANT to bars > t
(no-lookahead); `peak_long[t]` / `max_short[t]` computed on closes ≤ t only;
position long iff washed-out AND recovering simultaneously, flat otherwise,
warm-up flat until `max(W_dd, W_prox)` bars; fills at t+1 open.

To `src/trading_lab/sweeps.py` (mirroring the Round-7 layout at
`_R7_DRAWDOWN_AXES` / `_R7_HIGHPROX_AXES` ff.): `_R7C_CONJUNCTION_AXES`,
`R7C_INSTRUMENTS = R7_INSTRUMENTS` (same object), `r7c_conjunction_variants()`
(constraint-valid expansion enforcing `W_prox < W_dd`, returning 12), and
`r7c_total_configs()` returning **180** (15 instruments × 12 variants) with the
program cumulative advancing **5,415 → 5,595**.

To `tests/test_sweeps.py`: pins for the `_R7C_CONJUNCTION_AXES` dict (exact
values above), the **12-variant count** (2 × 3 × 2), the `W_prox < W_dd`
registered constraint (every expanded variant satisfies it), instrument-tuple
identity with `R7_INSTRUMENTS` (same tuple object), and the **5,415 → 5,595**
totals (`r7c_total_configs()` = 180; program cumulative 5,595). Only after
those tests are green may the R7-C runner (`scripts/run_r7c_*`) execute.

## Round-level aggregation (pre-registered)

Each of the 15 lanes exits Round 7C with exactly one verdict: KEEP-dev iff it
passes the Round-2 rule AND the selection-fair gate; else KILL (or KILL-SIG per
`classify_verdict`). Results land in a new
`docs/research-round-7c-results.md`, reporting: verdict counts, every gate FAIL
reason verbatim, full fixed-config rows (`selection_gap` per lane), the
**reason_class table with the UNGRADEABLE-share infrastructure-alarm line
(standing rule 3 — mandatory)**, best informational t vs the unchanged bar,
runtime vs cap, and the burden ledger line (5,415 → 5,595 exactly; any
deviation is a registration violation, not a rounding note). Ledger convention:
each lane's searched top variant LEDGERED with `variants_tried=12`; gate
replays are report-only rows in the lane JSON.

## What round 7C will NOT do

- **No execution in the planning session** — this plan's PR contains no
  sweep, no backtest, no grid code, no strategy code; running (and the
  pre-run code commit above) is a future session's separately claimed
  slice.
- **No holdout access** — SPENT; `data/p5holdout/` never read,
  `unlock_holdout` never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched.
- **No data fetching, no new tickers** — committed caches only.
- **No bar-lowering** — `min_tstat(K)` at each lane's honestly-counted K=12,
  never lowered.
- **No OOS validation claims, no broker/order/exchange-write code, no live
  API configuration** — research-only, per CONSTITUTION.md.
