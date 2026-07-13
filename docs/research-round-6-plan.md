# Research Round 6 — Pre-Registered Plan (New Idea Classes Under the Selection-Fair Gate)

> **Status:** `binding` — pre-registered Round-6 protocol, committed and
> merged BEFORE any Round-6 sweep, backtest, replay, or outcome exists.
> **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion is CLOSED.**
> Every hypothesis, method, and KEEP/KILL rule below is stated in advance;
> a KEEP anywhere in Round 6 means *dev-candidate only*, never a finding.
> The multiple-testing bar is UNCHANGED from Rounds 2–5
> (`trading_lab.promotion.min_tstat`, ~2.64 at K=12) — no bar-lowering
> anywhere in this round; K only ever rises with variants actually tried.
> **Round 6 is the FIRST round under the selection-fair standing gate**
> (PR #111, `d498018`, decision [D-0002]): no Round-6 KEEP-dev verdict
> exists until `run_selection_gate`/`apply_gate` has passed it.

## Provenance and scope

Round 5 closed (PR #110;
[research-round-5-results.md](research-round-5-results.md) closing tally)
with 4 KEEP-dev / 1 KILL of the program's top 5 lanes, 0 promoted, and the
program cumulative surface at **4,359 registered configs** — 0 PROMOTED
anywhere, best t-stat 1.38 against the 2.64 bar. Its conclusion: "anything
further still needs new data (OWNER-GATED) or a genuinely different idea
class." ORDER 012 item 4 is the standing owner direction to keep expanding
the backtest surface — "new strategies, new stocks/tickers, new
indicators — every result recorded honestly" — and ORDER 014 items 1+3
(`control/inbox.md` @ `c9297a7`) direct this pre-registered Round-6 plan,
with the R5-D fixed-config-row convention folded in as a standing rule.

Round 6 accordingly registers **two genuinely new indicator classes on the
COMMITTED data caches only** — the first VOLUME-based families the program
has ever run (every prior family reads only price columns; the volume
column has sat unused in every committed cache since P0) and the first
family whose *signal* reads the OPEN column (the overnight gap) — plus one
timeframe-expansion slice. No new data is fetched; every instrument below
is an existing `data/daily/` or `data/hourly/` cache, and the dev rail
truncation at `HOLDOUT_START` applies as always. New-ticker expansion is
explicitly NOT available to this round: all 15 committed daily caches and
all 8 committed hourly caches are already probed surface, and fetching is
out of scope — the honest "new tickers" answer for Round 6 is *none
available without a fetch*.

Two candidate directions were considered and NOT registered, recorded here
for honesty: an OBV/MFI sweep on the `data/p2ext/` extended-history caches
(only 2 tickers — too thin for a verdict-bearing slice) and any slice
requiring a data fetch (blocked by the committed-caches rail).

## The two new standing rules (effective this round, folded into the rails)

1. **Selection-fair gate on every KEEP** ([D-0002], PR #111 `d498018`,
   binding doc [selection-fair-gate.md](selection-fair-gate.md)): every
   Round-6+ runner that mints a would-be KEEP-dev verdict MUST run
   `trading_lab.selection_gate.run_selection_gate` on the lane (fidelity
   guard armed with the lane's own recorded searched Sharpe) and fold the
   result through `apply_gate` BEFORE writing the verdict; the full gate
   result block is recorded in the lane JSON. A lane whose searched edge
   does not survive the selection-free fixed-config replay is KILLed the
   day it is minted. A runner that mints KEEP-dev without a
   `selection_gate` block in its lane JSON violates [D-0002].
2. **R5-D fixed-config row in every searched-arm comparison** (ORDER 014
   item 3; [research-round-5-results.md](research-round-5-results.md)
   closing tally item 4: "future rounds comparing searched arms should
   carry the R5-D fixed-config row by default"): every Round-6+ lane
   summary that reports a searched walk-forward number ALSO reports, in
   the same machine-readable artifact, the selection-free fixed-config
   replay of the lane's committed top full-period variant on the identical
   test windows — `fixed_sharpe`, `bench_sharpe`, `searched_sharpe`, and
   `selection_gap = searched − fixed` (informational, no registered
   threshold). In Round 6 the gate's own result block satisfies this row
   for every graded lane — the gate runs on EVERY lane, not only would-be
   KEEPs, so KILLed lanes carry the row too.

## Standing rails (unchanged, restated for this round)

- **Data**: dev rail only, via `trading_lab.data.load_ohlcv` — holdout
  excluded by default, `data/p5holdout/` never read, `unlock_holdout`
  never passed. Committed caches only; nothing fetched. (The paper lane's
  `load_paper_ohlcv` rail is not used by research rounds and
  `experiments/paper/**` is untouched.)
- **Grading**: the Round-2 KEEP/KILL rule (KEEP as dev-candidate iff
  stitched walk-forward OOS Sharpe > same-window B&H benchmark Sharpe AND
  > 0; ties/ambiguity KILL) plus the ORDER 007 t-stat (informational),
  `classify_verdict` for KILL-SIG at the mirrored bar, AND — new this
  round — the selection-fair gate (standing rule 1 above). Bar
  `trading_lab.promotion.min_tstat(K)` at each lane's honestly-counted
  K — never lowered. Promotion is CLOSED: no Round-6 verdict can promote
  anything; KEEP = dev-candidate only.
- **Costs baseline**: 5 bps slippage + 1 bp commission per side
  (`config.DEFAULT_SLIPPAGE_BPS` / `DEFAULT_COMMISSION_BPS`).
- **Walk-forward geometry**: train 1008 / test 252 bars, contiguous test
  windows, exactly as Rounds 2–5, on both timeframes.
- **Pre-declaration**: all Round-6 grids are committed to
  `trading_lab.sweeps` WITH tests in this plan's own PR, BEFORE any slice
  runs — `r6_volume_*`, `r6_gap_*`, `r6_volume_hourly_*`, totals pinned by
  `tests/test_sweeps.py` (12 constraint-valid variants per family per
  lane; 696 new registered configs; program cumulative 4359 → **5055**).
- **Honesty**: nulls and KILLs are first-class deliverables. The expected
  outcome, after five rounds closing at 0 promoted, is more honest nulls.
- **Runtime caps, no silent truncation**: each slice pre-declares a
  wall-clock cap below. A slice that would exceed its cap STOPS, records
  the partial state and the verbatim overrun in its summary artifact, and
  the results doc reports the slice as CAP-HIT (re-registration required
  to continue) — silent truncation, silent sub-sampling, or quietly
  narrowing a registered grid mid-run are all forbidden.

---

## R6-A — Volume-confirmation families (r6-volume × 15 daily tickers)

- **Motivation**: the volume column is committed, verified non-degenerate
  in every daily cache (zero zero-volume bars on the 15-ticker surface),
  and has never been read by any of the program's 25 prior families —
  volume confirmation is the textbook "different information channel"
  claim, and after 4,359 price-only configs it is the cheapest genuinely
  new idea class available without a fetch.
- **Families** (implementations + causality tests in this plan's PR):
  `obv_trend` — long while on-balance volume sits above its own trailing
  SMA; `price_confirm=False` is the pure-OBV **within-family control arm**
  (does the volume line add anything beyond a plain price-SMA regime?),
  committed in the same grid so neither arm can be cherry-picked after
  outcomes. `mfi_reversion` — Money Flow Index oversold cross-up
  reversion, the volume-weighted sibling of the existing RSI / stochastic
  / Williams %R / CCI oscillator families (its price-only siblings are the
  natural comparison set already on the ledger).
- **Hypothesis**: volume confirmation does not create edge on this
  surface — most lanes KILL, and no lane's informational t approaches the
  bar. If the volume channel carries real information, `obv_trend`
  confirmed arms should beat their own pure-price behaviour and
  `mfi_reversion` should out-grade its price-only oscillator siblings;
  the registered expectation is that neither happens.
- **Grid** (committed in `sweeps._R6_VOLUME_AXES`, pinned by tests):
  `obv_trend` window {10, 20, 50, 100, 150, 200} × price_confirm
  {False, True} = 12; `mfi_reversion` period {7, 14, 21} × buy_below
  {10, 20} × sell_above {70, 80} = 12.
- **Instruments**: `R6_VOLUME_INSTRUMENTS` — verbatim (same tuple object)
  the committed 15-ticker daily surface of R4-F. 30 lanes; 360 registered
  configs.
- **Decision rule** (per lane, pre-registered): Round-2 KEEP/KILL rule on
  the searched walk-forward, THEN the selection-fair gate
  (`run_selection_gate` with fidelity guard, `apply_gate`) on every lane —
  a would-be KEEP that fails the gate is KILL (gate reason recorded);
  KILL-SIG per `classify_verdict` at K=12. Gate block = the lane's R5-D
  fixed-config row (standing rule 2).
- **Burden**: 360 new registered configs. Informational per-lane K=12,
  bar ~2.64.
- **Runtime cap**: ≤ 20 minutes wall-clock for the whole slice.

## R6-B — Overnight-gap family (r6-gap × 12-ticker mixed equity/ETF set)

- **Motivation**: execution has always filled at next-bar open, but no
  family's *signal* has ever read the open column — the overnight session
  (close→open) is unexamined territory in every committed equity/ETF
  cache. Gap-fade and gap-follow are the two classic, mutually exclusive
  theses about it.
- **Family** (implementation + causality tests in this plan's PR):
  `overnight_gap` — trailing-ATR-normalized gap
  (`open[t] − close[t−1]`, Wilder ATR through `t−1`, `atr_period` frozen
  at the lab-standard 14 and NOT swept), `mode="fade"` (down-gap ≥
  threshold → long) / `mode="follow"` (up-gap ≥ threshold → long), held
  `hold` bars. Both mirror theses are committed in the SAME grid (6
  variants each, pinned by tests) so neither can be cherry-picked after
  outcomes. Honesty note, stated in advance: the engine fills at bar
  t+1's open, so what this slice tests is **post-gap drift/reversion over
  the following bars**, never same-day open-to-close gap capture — the
  classic overnight-capture claim is NOT testable in this engine and is
  NOT claimed.
- **Hypothesis**: post-gap next-day drift/reversion is not exploitable
  net of costs on daily bars — most lanes KILL under the benchmark rule;
  fade and follow cannot both be right per instrument, and the registered
  expectation is that neither clears it.
- **Grid** (committed in `sweeps._R6_GAP_AXES`, pinned by tests): mode
  {fade, follow} × gap_atr {0.5, 1.0, 1.5} × hold {1, 3} = 12.
- **Instruments**: `R6_GAP_INSTRUMENTS` — verbatim (same tuple object)
  the slice-8 12-ticker mixed set. **BTC-USD is deliberately excluded**:
  a 24/7 market has no overnight session, so the family is untestable
  there (pinned by a test). 12 lanes; 144 registered configs.
- **Decision rule** (per lane, pre-registered): identical to R6-A —
  Round-2 rule, then the selection-fair gate on every lane, KILL-SIG per
  `classify_verdict` at K=12; gate block = the R5-D fixed-config row.
- **Burden**: 144 new registered configs. Informational per-lane K=12.
- **Runtime cap**: ≤ 15 minutes wall-clock for the whole slice.

## R6-C — Volume families on hourly bars (r6-volume-hourly × 8 hourly tickers)

- **Motivation**: the Round-3 slice-5/14/15 precedent — every daily
  family gets its hourly counterpart run before the timeframe question is
  considered answered. The hourly caches carry real volume (spot-checked
  ≤ 10 zero-volume bars per ticker out of ~5,065 — recorded here so the
  run session inherits the fact), and volume signals are conventionally
  claimed to work *better* intraday.
- **Families and grids**: the SAME two R6-A families with the IDENTICAL
  12-variant grids — grid identity with R6-A is pinned by tests
  (`r6_volume_hourly_variants(fam) == r6_volume_variants(fam)`); no new
  strategy code, no new parameter territory.
- **Hypothesis**: same as R6-A, on hourly bars — with the added
  registered expectation from the Round-3 hourly matrix that hourly bars'
  higher churn at baseline costs makes KILLs MORE likely, not less.
- **Instruments**: `R6_VOLUME_HOURLY_INSTRUMENTS` — verbatim (same tuple
  object) the committed 8-ticker hourly surface. 16 lanes; 192 registered
  configs. The short dev-rail hourly history (~2023-08 → 2025-01, ≈ 5
  walk-forward splits) is a KNOWN weakness recorded in advance — R5-B
  demoted the program's only prior hourly KEEP for exactly this
  single-window-luck exposure, so any hourly KEEP here inherits that
  caveat explicitly in the results doc.
- **Decision rule / burden / cap**: identical rule structure to R6-A;
  192 new registered configs, per-lane K=12; **runtime cap ≤ 20 minutes**
  wall-clock for the whole slice.

---

## Round-level aggregation (pre-registered)

Each of the 58 lanes (30 + 12 + 16) exits Round 6 with exactly one
verdict: KEEP-dev iff it passes the Round-2 rule AND the selection-fair
gate; else KILL (or KILL-SIG per `classify_verdict`). Results land
slice-by-slice in `docs/research-round-6-results.md` (created by the
first results slice, R4/R5 convention), each slice section reporting:
counts (KEEP / KILL / KILL-SIG), gate outcomes including every gate FAIL
reason verbatim, the full fixed-config rows (`selection_gap` per lane),
best informational t vs the unchanged bar, runtime vs cap, and the
burden ledger line. Ledger convention: each slice's searched top variant
per lane is LEDGERED with `variants_tried=12` (Round-3 convention);
gate replays are report-only rows inside the lane JSON (R4-B precedent).
Expected honest outcome given five rounds of nulls: mostly KILLs — that
is a complete, publishable deliverable.

## What round 6 will NOT do

- **No holdout access** — the holdout is SPENT; `data/p5holdout/` is never
  read and `unlock_holdout` is never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched; no paper
  grading run by research sessions.
- **No new data fetching** — committed caches only; no new tickers exist
  without a fetch, so none are registered.
- **No R5-C BTC-USD OOS execution** — the escalate proposal
  ([proposals/r5c-btc-bollinger-breakout-oos-proposal.md](proposals/r5c-btc-bollinger-breakout-oos-proposal.md))
  stays OWNER-GATED; this round schedules and runs nothing against it.
- **No MTF-Bollinger pre-registration activity** — that draft is FROZEN
  (dev result NULL); it is not a Round-6 slice.
- **No OOS validation claims** — genuine OOS validation of any KEEP-dev
  stays OWNER-GATED behind a new pre-registered protocol on post-2026
  data.
- **No bar-lowering** — `min_tstat` at the honestly-counted K, always.
- **No broker/order/exchange-write code, no live API configuration** —
  research-only, per CONSTITUTION.md.
