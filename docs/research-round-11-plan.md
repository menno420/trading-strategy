# Research Round 11 — Pre-Registered Plan (Cross-Asset Regime Conditioning, continuous + causal)

> **Status:** `binding` — pre-registered Round-11 protocol, committed and
> merged BEFORE any Round-11 sweep, backtest, replay, or outcome exists.
> **PLAN ONLY: this document's own session runs NOTHING.** This PR lands the
> plan, the `trading_lab.xasset_regime` module (3 causal cross-asset regime
> signals + the continuous rolling-percentile conditioning), and the pinned
> 27-config grid (`sweeps._R11_*`, `r11_total_configs()` = 27) with tests — it
> runs NOTHING and grades NOTHING. Executing Round 11 (the sweep runner +
> graded `docs/research-round-11-results.md`) is a FUTURE session's separately
> claimed slice (plan-before-outcome, the ORDER 014 round-6 precedent: plan PR
> then run PR, exactly as R9 split #153 plan / #154 run and R10 split #155 plan
> / #156 run). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion is
> CLOSED.** Every hypothesis, method, and KEEP/KILL rule below is stated in
> advance; a KEEP anywhere in Round 11 means *dev-candidate only*, never a
> finding. The multiple-testing bar is UNCHANGED from Rounds 2–10
> (`trading_lab.promotion.min_tstat`) — no bar-lowering anywhere in this round.

## Provenance and scope

Round 11 pre-registers the **self-serve first step from the new-data-source
direction**. After 10 rounds / 5,913 registered configs / 0 promoted on
price/volume-derived signals and their combinations, the scoping memo
[research-direction-new-data-sources.md](research-direction-new-data-sources.md)
(PR #157) named **cross-asset / macro-regime (§2.1)** as the LOWEST-cost,
SELF-SERVE first step — the only candidate testable with data the lab ALREADY
holds (the committed 15-ticker daily cache's TLT / GLD / SPY / QQQ legs), with
NO new ingestion, NO new ticker, NO new dependency. Coordinator-authorized on the
owner's standing 2026-07-19 turn, Round 11 executes that first step under the
identical plan-before-outcome protocol every round has used.

The program stands at **5,913 registered configs / 0 promoted** through Round 10
([current-state.md](current-state.md)); no strategy has ever cleared the
significance bar, and the program best informational t anywhere is 1.66 (R5) vs
a ~2.638-class bar. The honest registered prior for Round 11 is the same null —
and, as §1–2 argue, cross-asset conditioning carries a specific burned-class
precedent (R4 `crossasset_gate` 0/2, `regime_switch` 0/6, the unconditioned
control beat the gate both times). A negative result is the expected and
publishable outcome; R11's value is a rigorous, lookahead-controlled test of the
CONTINUOUS-conditioning form the burned binary gate never tried.

Standing rail, absolute: RESEARCH-ONLY. Dev caches only via
`trading_lab.data.load_ohlcv`; the holdout is SPENT (`data/p5holdout/` never
read, `unlock_holdout` never passed); `experiments/paper/**` untouched; NO
broker/order/exchange-write code, NO live-API config; promotion CLOSED. Uses
ONLY the existing cache — no new data provisioning, no new dependency
(`requirements.txt` unchanged), inside the RESEARCH-ONLY rails.

## 1. Thesis

A single instrument's own price history says nothing about the *regime* it sits
in. Relationships BETWEEN assets — equities outrunning long-duration bonds,
metals being bid as risk-off, cross-asset breadth — carry macro-regime
information a per-instrument trend or reversion rule structurally cannot see.
Round 11 tests whether a CROSS-ASSET regime score, built CAUSALLY from assets
already in the cache, can condition a risk-leg's exposure to **beat plain
buy-and-hold of that same leg**.

The conditioning is CONTINUOUS: the target's position at bar *t* is the CAUSAL
rolling-percentile-rank (trailing 252 bars) of the chosen regime score, clipped
to [0, 1] — exposure scales smoothly with how risk-on the regime is *relative to
its own recent history*, rather than switching fully on/off.

**Honest registered prior (stated in advance).** The
[cross-round meta-analysis](cross-round-meta-analysis.md) records that
conditioning "loses to its own controls, on every axis tested," and the
cross-asset neighbours are BURNED (§2). The registered expectation is the program
null: most or all lanes KILL, 0 promoted. R11 would only WIN if a causal
cross-asset regime separates the drawdowns a buy-and-hold suffers from the drift
it rides — i.e. if scaling exposure down in risk-off regimes sidesteps losses
without shedding the gains. Round 11 MEASURES that rather than assuming it.

## 2. How R11 differs MATERIALLY from the burned R4 classes

Cross-asset conditioning is NOT virgin territory. Two Round-4 families are
recorded as **burned classes** in [strategy-catalog.md](strategy-catalog.md);
R11 must differ materially or it inherits their null by construction.

- **`crossasset_gate`** ([research-round-4-results.md](research-round-4-results.md)
  §R4-E): a frozen EMA-cross equity component gated on the **SIGN** of another
  instrument's momentum — a BINARY on/off switch. **0 KEEP / 2 KILL**; the
  ungated control beat the gate.
- **`regime_switch`** (§R4-D): a trend/reversion switch on a trend-strength
  tercile, again a discrete regime bucket. **0 KEEP / 6 KILL**; the
  unconditioned control beat the gate.

**R11 is neither a re-skin.** It differs on three axes at once:

1. **Continuous conditioning, not a binary gate.** R4-E gated on a momentum
   SIGN (0/1). R11 sizes exposure CONTINUOUSLY in [0, 1] as the causal
   rolling-percentile-rank of a real-valued regime score — a different object
   than a binary gate, and exactly the form the memo (§2.1) flagged as untested.
2. **Causal ROLLING normalization, not a full-sample / discrete state.** The
   percentile rank uses ONLY the trailing 252-bar window ending at *t* — never a
   full-sample rank or full-sample z-score. Full-sample normalization is the
   classic regime-lookahead leak; R11 forecloses it by construction (§4).
3. **A mandatory unconditioned control arm.** Every conditioned lane is graded
   against plain buy-and-hold of the SAME target (position ≡ 1.0), reported
   next to each lane (§5), per the memo's control-arm discipline — the null is
   the honest registered prior even here.

No prior round has graded a continuous, causally-normalized cross-asset regime
conditioner with its unconditioned control reported alongside.

## 3. The regime signals, windows, targets, and the grid

**Regime signals (3)** — all built from the existing daily cache, all 100%
causal (the score at bar *t* uses ONLY data with timestamp ≤ *t*; trailing
windows only). Defined precisely (`trading_lab.xasset_regime`):

- **`xasset_eq_bond_mom`** — the trailing-W total return of SPY minus the
  trailing-W total return of TLT (`SPY_t/SPY_{t-W} − TLT_t/TLT_{t-W}`; equities
  outrunning long-duration bonds ⇒ risk-on high).
- **`xasset_metals_riskoff`** — the NEGATIVE of GLD's trailing-W total return
  (gold being bid ⇒ risk-off ⇒ a LOWER risk-on score).
- **`xasset_breadth`** — the fraction of {SPY, QQQ, GLD, TLT} whose `close_t`
  exceeds their own trailing-W SMA at bar *t* (a continuous risk-on composite in
  [0, 1]).

**Windows W (3):** 63, 126, 252 (quarter / half / full year), the canonical
time-series-momentum lookbacks the program has used since Round 2.

**Targets / risk legs (3):** SPY, QQQ, NVDA. All three are on the **NYSE
calendar** — the SAME index as the SPY/QQQ/GLD/TLT regime inputs — so NO
cross-calendar alignment is needed. **BTC-USD is deliberately EXCLUDED** as a
target precisely because its 24/7 weekend calendar would force an as-of reindex
and add lookahead risk (the same reason the Round-2/3 cross-sectional lanes
dropped BTC's weekend bars); this exclusion is a lookahead-safety choice, not a
performance filter.

**Conditioning (CONTINUOUS).** The target's position at bar *t* = the CAUSAL
rolling-percentile-rank of the raw regime score over the trailing 252-bar window
ending at *t* (`_R11_PERCENTILE_WINDOW = 252`, FIXED, not swept), clipped to
[0, 1]. Warm-up bars (score or its trailing-252 rank undefined) resolve to `0.0`
(flat) — the house "undefined resolves against the strategy" convention (as in
`crossasset_gate`) — so the position series is NaN-free and in [0, 1] on every
bar. Values scale continuously; this is NOT a binary gate.

**Grid.** 3 signals × 3 windows × 3 targets = **27 configs**
(`r11_total_configs()` = 27, `R11_K = 27`). Each config names its own target, so
targets do NOT multiply the count a second time. Program cumulative **5,913 →
5,940** (on the future RUN). The grid, the signal names, the windows, the
targets, and the fixed percentile window are pinned by `tests/test_sweeps.py`.

## 4. LOOKAHEAD CONTROL (headline)

Regime-detection lookahead is the **#1 failure mode for this class** — a regime
label that peeks at future data manufactures an edge that evaporates live. R11's
design forecloses it explicitly, and the guarantee is a committed unit test, not
a comment:

- **Every regime label at bar *t* uses only data with timestamp ≤ *t*.** All
  inputs are trailing windows: trailing-W total returns (`close_t / close_{t-W}`)
  and trailing-W SMAs (`close.rolling(W).mean()`), all reading only closes at or
  before *t*.
- **Rolling, never full-sample, normalization.** The conditioning percentile
  rank is computed ONLY over the trailing 252-bar window ending at *t* — never a
  full-sample rank or full-sample z-score. This is the single most important
  design choice; full-sample normalization is the classic regime-lookahead leak,
  and R11 does not use it anywhere.
- **Execution at t+1 open.** As everywhere else in the lab, the engine delays
  execution to bar *t+1*'s open — the position decided from data ≤ *t* is filled
  at *t+1*.
- **ENFORCED by a truncation unit test.** `tests/test_xasset_regime.py`
  (`TestNoLookahead`) asserts, for several bars *t* across all 3 signals and all
  3 windows, that the regime score AND the conditioned position at bar *t* are
  IDENTICAL whether computed on the full series or on the series TRUNCATED at bar
  *t* (`series.iloc[:t+1]`). This prefix-invariance property is the load-bearing
  correctness guarantee — if it ever fails, the design leaks and must be fixed,
  never papered over. The RUN session MUST re-assert the same property on the
  REAL cached panels before grading.

## 5. Instruments, timeframe, costs, rail, control arm

- **Regime inputs**: SPY, QQQ, GLD, TLT (committed daily caches); **targets**:
  SPY, QQQ, NVDA. All NYSE-calendar. No new caches, nothing fetched, no post-hoc
  instrument selection.
- **Timeframe**: daily.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults);
  fractional positions charged on `|Δ held position|`, which the continuous
  conditioning exercises directly.
- **Walk-forward geometry**: train 1008 / test 252 daily bars, contiguous test
  windows, exactly as Rounds 2–10.
- **Rail**: dev only via `trading_lab.data.load_ohlcv` — holdout SPENT,
  `HOLDOUT_START` enforced, `data/p5holdout/` never read.
- **Mandatory unconditioned CONTROL ARM.** The benchmark for every conditioned
  lane is plain **buy-and-hold** of the same target (position ≡ 1.0). The
  promotion test already measures each lane's edge as its Sharpe-delta vs
  buy-and-hold, so the control IS the benchmark — but the RUN's
  `docs/research-round-11-results.md` MUST additionally **report the base
  buy-and-hold Sharpe next to each conditioned lane**, so the reader sees
  directly whether conditioning beat just holding. Conditioning that fails to
  beat its own control is reported as such, not as a candidate.

## 6. Promotion bar (SAME as all prior rounds)

`trading_lab.promotion.min_tstat(K)` Bonferroni, K counted from the searched
grid, **never lowered**. Every lane reports its informational t against BOTH
thresholds:

- **per-lane K = 9** (the 9 (signal, window) configs searched for a single
  target): `min_tstat(9) ≈ 2.54`;
- **program-wide K = 27** (the full round grid): `min_tstat(27) ≈ 2.90`
  (`R11_K = 27`).

The holdout is SPENT (dev rail only); promotion is CLOSED — every KEEP is a
dev-candidate only, never a finding. **0-promoted is a valid, publishable
outcome**; the bar is never softened and exposure is never re-scaled after the
fact to rescue a lane.

## 7. Standing rails applied on every lane

The three standing requirements (rails, restated as binding for this round):

1. **Selection-fair gate on every lane**
   ([selection-fair-gate.md](selection-fair-gate.md); PR #111): every Round-11
   runner runs `trading_lab.selection_gate.run_selection_gate` (fidelity guard
   armed with the lane's recorded searched Sharpe) and folds the result through
   `apply_gate` BEFORE writing any verdict; the full gate block is recorded in
   the lane JSON. A would-be KEEP that fails the gate is KILL the day it is
   minted.
2. **R5-D fixed-config row in every searched-arm comparison**
   ([research-round-5-results.md](research-round-5-results.md); standing since
   Round 6): every lane summary reports `fixed_sharpe`, `bench_sharpe` (the
   buy-and-hold control), `searched_sharpe`, and `selection_gap = searched −
   fixed` (informational, no registered threshold).
3. **reason_class rollup** (standing round-level requirement since Round 7; PR
   #121): the Round-11 rollup MUST tabulate `reason_class` counts across all
   lanes and treat ANY nonzero `selection_gate.UNGRADEABLE_CLASSES` share as an
   **infrastructure alarm** reported in the results doc and on the heartbeat —
   never as strategy evidence.

**How the selection-fair gate / R5-D row map onto a CONDITIONING round.** The
regime signals and the fixed 252-bar percentile window are FIXED (no per-signal
re-search); the "search" dimension for the gate is **(signal, window)** per
target — the 9 configs searched for that target. So, per target:

- `fixed_sharpe` = the specific reported config's OOS Sharpe (the pre-declared
  config the lane ledgers);
- `bench_sharpe` = the unconditioned buy-and-hold control on that target;
- `searched_sharpe` = the BEST (signal, window) config on that target (best over
  the 9);
- `selection_gap = searched − fixed`.

This is consistent with how R9 / R10 mapped the gate onto a searched family: the
gate runs on EVERY lane, not only would-be KEEPs, and a positive `selection_gap`
that inflates a would-be KEEP is exactly what the fidelity guard is armed to
catch. Each target's searched top config is LEDGERED with the round's searched K;
gate replays are report-only rows in the lane JSON. Keep it honest and consistent
with R9 / R10.

---

## Code + tests already landed in THIS pre-registration PR

Following the R9/R10 header protocol, Round 11's pre-registration lands PLAN +
CODE INFRASTRUCTURE here, so the grid is pinned by tests BEFORE any run:

- `src/trading_lab/xasset_regime.py` — the 3 causal regime scores
  (`eq_bond_momentum_score`, `metals_riskoff_score`, `breadth_score`) built from
  a dict of aligned daily closes given W, dispatched by `regime_score`; the
  causal `rolling_percentile_rank`; and `regime_conditioned_positions(...)`
  returning the target's continuous position ∈ [0, 1]. Docstrings state the
  causality guarantee and contrast the burned binary `crossasset_gate`.
- `tests/test_xasset_regime.py` — the headline no-lookahead TRUNCATION test
  (`TestNoLookahead`: score and conditioned position at bar *t* identical on the
  full series vs `series.iloc[:t+1]`, plus a monotone-score rank check that a
  full-sample rank would fail), shape/range/alignment/NaN-freeness tests, and a
  hand-constructed exact-arithmetic example for each of the 3 signals.
- `src/trading_lab/sweeps.py` — `_R11_SIGNALS`, `_R11_WINDOWS`, `_R11_TARGETS`,
  `_R11_PERCENTILE_WINDOW`, `R11_K = 27`, `r11_configs()`, and
  `r11_total_configs()` returning **27** (3 × 3 × 3) with the program cumulative
  advancing **5,913 → 5,940** on the RUN.
- `tests/test_sweeps.py` — pins for the signal names (identical to
  `xasset_regime.REGIME_SIGNALS`), the windows, the NYSE-calendar targets (BTC
  excluded), the fixed 252 percentile window, the exact 27-config product, and
  the **5,913 → 5,940** ledger (`r11_total_configs()` = 27).

## What the FUTURE run session must add BEFORE flipping to results

Only the runner + results remain for the RUN PR (plan-before-outcome):

- `scripts/run_r11_xasset_regime_sweep.py` — for each (signal × window ×
  target): load the aligned daily closes for the target + the regime legs via
  `load_ohlcv`, compose the lane with
  `xasset_regime.regime_conditioned_positions`, backtest at engine-default costs
  on the 1008/252 walk-forward, and grade under the Round-2 KEEP/KILL rule +
  ORDER 007 informational t + `classify_verdict` KILL-SIG + the selection-fair
  gate on every lane (standing rule 1). CLONE a gate-carrying runner (the R9/R10
  daily runner), never a gate-less template. The benchmark is **buy-and-hold**
  of the target (the unconditioned control), so each lane's edge is measured as
  its deviation from the hold, and the base buy-and-hold Sharpe is reported next
  to every lane (§5).
- A RUN-side re-assertion of the truncation / prefix-invariance property (§4) on
  the REAL cached panels before grading (not only on the synthetic test series).
- `docs/research-round-11-results.md`: verdict counts, every gate FAIL reason
  verbatim, full fixed-config rows (`selection_gap` + the buy-and-hold
  `bench_sharpe` per lane), the reason_class table with the UNGRADEABLE-share
  infrastructure-alarm line (standing rule 3), best informational t vs BOTH the
  K=9 and K=27 bars, runtime vs cap, and the burden ledger line (**5,913 →
  5,940** exactly).

## Round-level aggregation (pre-registered)

Each of the 27 lanes exits Round 11 with exactly one verdict: KEEP-dev iff it
passes the Round-2 rule AND the selection-fair gate; else KILL (or KILL-SIG per
`classify_verdict`). A conditioned lane that fails to beat its unconditioned
buy-and-hold control is reported as such (not a candidate). Ledger convention:
each target's searched top config LEDGERED with the round's searched K; gate
replays are report-only rows in the lane JSON. 0-promoted is the expected,
complete deliverable.

## What Round 11 will NOT do

- **No execution in THIS pre-registration PR** — this PR contains no sweep, no
  backtest, no runner, and no results; running is a future separately claimed
  slice.
- **No holdout access** — SPENT; `data/p5holdout/` never read, `unlock_holdout`
  never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched.
- **No data fetching, no new tickers, no new dependency** — committed caches
  only, `requirements.txt` unchanged.
- **No full-sample normalization** — the regime percentile rank is ROLLING
  (trailing 252) only; a full-sample rank/z-score is the lookahead leak this
  round is designed to foreclose.
- **No BTC-USD target** — excluded by design to avoid a cross-calendar as-of
  reindex and its lookahead risk.
- **No bar-lowering** — `min_tstat(K)` at each lane's honestly-counted K, never
  lowered; reported vs both K=9 and K=27.
- **No OOS validation claims, no broker/order/exchange-write code, no live-API
  configuration** — research-only, per CONSTITUTION.md.
