# Research Round 9 — Pre-Registered Plan (Signal-Confluence Vote, cross-class ≥K-of-N)

> **Status:** `binding` — pre-registered Round-9 protocol, committed and
> merged BEFORE any Round-9 sweep, backtest, replay, or outcome exists.
> **PLAN + CODE INFRASTRUCTURE, ZERO RESULTS: this document's own PR lands the
> plan, the `trading_lab.ensemble.confluence_positions` vote gate, and the
> pinned 60-config grid (`sweeps._R9_*`, `r9_total_configs()` = 60) with tests
> — it runs NOTHING and grades NOTHING. Executing Round 9 (the sweep runner +
> graded `docs/research-round-9-results.md`) is a FUTURE session's separately
> claimed slice** (plan-before-outcome, the ORDER 014 round-6 precedent: plan
> PR then run PR). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion
> is CLOSED.** Every hypothesis, method, and KEEP/KILL rule below is stated in
> advance; a KEEP anywhere in Round 9 means *dev-candidate only*, never a
> finding. The multiple-testing bar is UNCHANGED from Rounds 2–8
> (`trading_lab.promotion.min_tstat`) — no bar-lowering anywhere in this round.

## Provenance and scope

Round 9 pre-registers the **owner's live signal-confluence idea**. Owner turn
2026-07-19 (verbatim): *"any more progress on the trading strategies, what I was
thinking about, isn't it a good idea to find multiple strategies and wait untill
at least 2 or 3 give the same signals, what do you think about that?"* — relayed
via the venture-lab coordinator on a live owner turn (ORDER 019). The idea is
signal CONFLUENCE: enter only when several DISTINCT strategies agree. Round 9
tests exactly that — a cross-thesis-class **≥K-of-N majority vote** — under the
program's standing corrections, plan-before-outcome.

The program stands at **5,793 registered configs / 0 promoted** through Round 8
([cross-round-meta-analysis.md](cross-round-meta-analysis.md)); no strategy has
ever cleared the significance bar, and the program best informational t anywhere
is 1.66 (R5) vs a ~2.638 bar. The honest registered prior for Round 9 is the
same null the whole program has returned — and, as § 2 argues, confluence across
distinct classes has a *structural* reason to null (fewer co-agreement bars,
weaker statistics). A negative result is the expected and publishable outcome.

Standing rail, absolute: RESEARCH-ONLY. Dev caches only via
`trading_lab.data.load_ohlcv`; the holdout is SPENT (`data/p5holdout/` never
read, `unlock_holdout` never passed); `experiments/paper/**` untouched; NO
broker/order/exchange-write code, NO live-API config; promotion CLOSED.

## 1. Thesis

The owner's idea, verbatim: *"isn't it a good idea to find multiple strategies
and wait untill at least 2 or 3 give the same signals?"* Round 9 tests whether a
**cross-class ≥K-of-N majority vote** — long only on bars where at least K of N
DISTINCT thesis-class members are simultaneously long — produces a net-of-cost
edge that the isolated members lack. The vote is binary confluence
(`trading_lab.ensemble.confluence_positions`): flat below the threshold, full
long at/above it. "2 or 3 agree" maps directly to K ∈ {2, 3}.

## 2. Distinction from priors (both cited) and the honest prior

Two burned neighbors bracket Round 9; R9 is the untested corner between them.

- **R4-C survivor committee** (`trading_lab.ensemble.committee_positions`,
  [research-round-4-results.md](research-round-4-results.md) § R4-C):
  **AVERAGED** member positions into a *fractional* size (two of three long →
  `0.5` long) — an ~OR-weighted sizing rule, not a gate. Outcome: **5 KEEP-dev
  / 7 KILL / 0 KILL-SIG** of 12 committees, best informational t **1.085**
  (BTC-USD daily) vs the 2.638 bar, **0 promoted**; the diversification premium
  concentrated in small closely-matched committees and cleared nothing.
- **R7-C washout_recovery** (`washout_recovery`,
  [research-round-7c-results.md](research-round-7c-results.md)): **AND-gated two
  windows WITHIN ONE thesis-class** (a long-horizon drawdown AND a short-horizon
  proximity high — both price-state signals). Outcome over 180 configs: **1
  KEEP-dev / 11 KILL / 3 KILL-SIG** of 15 lanes, best t **0.22** (TLT), **0
  promoted**, and **KILL-SIG on AMZN / MSFT / QQQ** — the intersection was
  actively *value-destroying* on three names, not merely uninformative.

**R9 is neither.** It is a BINARY ≥K vote (not a fractional average, unlike
R4-C) ACROSS DISTINCT thesis-classes (not two windows within one class, unlike
R7-C). No prior round has graded that object.

**Honest registered prior (stated in advance).** Distinct-class signals are
often *anti-correlated*: a momentum member (`ema_crossover`) tends to be long in
uptrends exactly when a mean-reversion member (`rsi_mean_reversion`) is flat or
waiting for oversold. Anti-correlated members rarely co-agree, so an AND-style
≥K vote **collapses the trade count and with it the statistical power** — see
§ 7. The expected Round-9 outcome is more honest nulls (most lanes KILL), and
that is a complete deliverable. If confluence *did* help it would show as a
higher searched t on SET-3/K=2 than the isolated members achieve; the registered
expectation is that no such gradient clears the unchanged 2.638-class bar.

## 3. Member panel (fixed default params)

Members run at their **fixed `DEFAULT_PARAMS`** — NO per-member re-search. This
is a deliberate pre-registered choice: fixing the members keeps the searched
multiplicity K small (the only searched axis is (member-set, K), not each
member's grid) and gives the confluence idea its **best shot** rather than
burning power on member tuning. Every member is a 0/1 long/flat daily lane
already in the `STRATEGIES` registry; each is named with its thesis-class.

**SET-3** (`sweeps._R9_MEMBER_SET_3` — 3 distinct classes):

| Member | Default params | Thesis-class |
| --- | --- | --- |
| `ema_crossover` | `fast 20 / slow 50` | trend / momentum |
| `rsi_mean_reversion` | `period 14 / oversold 30 / overbought 70` | mean-reversion |
| `donchian` | `entry 20 / exit 10` | breakout |

**SET-5** (`sweeps._R9_MEMBER_SET_5` — 5 distinct classes; SET-3 + two more):

| Member | Default params | Thesis-class |
| --- | --- | --- |
| `ema_crossover` | `fast 20 / slow 50` | trend / momentum |
| `rsi_mean_reversion` | `period 14 / oversold 30 / overbought 70` | mean-reversion |
| `donchian` | `entry 20 / exit 10` | breakout |
| `drawdown_reversion` | `lookback 126 / entry_dd 0.10 / exit_frac 1.0` | drawdown STATE |
| `obv_trend` | `window 50 / price_confirm False` | volume |

No family repeats within a panel (a vote among duplicates is one signal counted
twice). `obv_trend` reads the volume column, which every one of the 15 daily
cache tickers carries (verified in the pre-registration PR). **No member
substitutions were required** — all five names resolve to registry families with
sane defaults that emit clean 0/1 positions on the daily surface.

## 4. Vote gates and the grid

The vote is `confluence_positions(members, K)`: long (1.0) iff the per-bar count
of long members is ≥ K, else flat (0.0), memoryless, on the members' shared
index. K ∈ {2, 3} for BOTH sets ("2 or 3 agree"), a registered constraint
`2 ≤ K ≤ len(members)`. That is **4 vote configs** (`sweeps._R9_VOTE_CONFIGS`):
SET-3/K2, SET-3/K3, SET-5/K2, SET-5/K3. Over the 15-ticker daily surface that is
**15 × 4 = 60 registered configs** (`r9_total_configs()` = 60); program
cumulative **5,793 → 5,853**.

## 5. Instruments, timeframe, costs, rail

- **Instruments**: `_R9_INSTRUMENTS = R7_INSTRUMENTS` (verbatim, the SAME tuple
  object) — the committed 15-ticker daily surface: AAPL, AMZN, BTC-USD, GLD,
  GOOGL, JPM, META, MSFT, NVDA, QQQ, SLV, SPY, TLT, TSLA, XOM. No new caches,
  nothing fetched, no post-hoc instrument selection.
- **Timeframe**: daily.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults).
- **Walk-forward geometry**: train 1008 / test 252 daily bars, contiguous test
  windows, exactly as Rounds 2–8.
- **Rail**: dev only via `trading_lab.data.load_ohlcv` — holdout SPENT,
  `HOLDOUT_START` enforced, `data/p5holdout/` never read.

## 6. PRE-REGISTERED correlation check (mandatory, first-class)

Confluence is only meaningful between INDEPENDENT signals. For each instrument
the run session MUST compute and report, over the members' shared dev-rail bars:

  (a) pairwise **correlation of member POSITION series** (the 0/1 lanes);
  (b) pairwise **signal-overlap** = fraction of bars both members are long among
      bars *either* is long (Jaccard-style: `|A∩B| / |A∪B|` over long-bars); and
  (c) pairwise **correlation of member daily RETURN streams**.

The full pairwise overlap matrix is reported per instrument (SET-5 is the
superset; SET-3 is its 3×3 sub-block). **Pre-registered interpretation rule,
verbatim:** *"Confluence between correlated members is one signal counted twice;
if mean pairwise member position-correlation on an instrument exceeds ~0.5, any
apparent vote edge is not diversified and must be reported as such."* A vote edge
on a high-correlation instrument is therefore disqualified as diversification
evidence at report time, not re-litigated after outcomes.

## 7. PRE-REGISTERED trade-count / power impact (mandatory, first-class)

Fewer trades = weaker statistics — this is stated up front, not buried, because
it is the mechanism by which the honest prior (§ 2) expects the null. For each
instrument the run session MUST report:

- **trades(single-member mean)** — the mean trade count across the panel members
  run in isolation;
- **trades(K=2)** and **trades(K=3)** — the vote lanes' trade counts;
- the **median trade-count shrinkage factor** vs the single members
  (`trades(vote) / trades(single-member mean)`, per set); and
- the implied **Sharpe standard-error inflation**: with
  `SE(SR) ∝ sqrt((1 + SR²/2) / N)`, fewer effective trades (smaller N) ⇒ a
  LARGER SE ⇒ a HIGHER t required to clear the same fixed effect.

State explicitly in the results: an AND-style ≥K vote across anti-correlated
distinct-class members can only SHRINK N, RAISE the SE, and make the unchanged
bar HARDER to clear — so the confluence idea, tested honestly, **reduces** the
chance of clearing the bar relative to the isolated members. Trades are never
invented to rescue power; the shrinkage IS part of the finding.

## 8. Promotion bar (SAME as all prior rounds)

`trading_lab.promotion.min_tstat(K)` Bonferroni, K counted from the searched
grid, **never lowered**. Every lane reports its informational t against BOTH
thresholds:

- **per-lane K = 4** (the 4 vote configs searched on a single instrument):
  `min_tstat(4) ≈ 2.24`;
- **program-wide K = 60** (the full round grid): `min_tstat(60) ≈ 3.14`
  (`R9_K = 60`).

The holdout is SPENT (dev rail only); promotion is CLOSED — every KEEP is a
dev-candidate only, never a finding. **0-promoted is a valid, publishable
outcome**; the bar is never softened and trades are never invented.

## 9. Standing rails applied on every lane

The three standing requirements (rails, restated as binding for this round):

1. **Selection-fair gate on every lane**
   ([selection-fair-gate.md](selection-fair-gate.md); PR #111): every Round-9
   runner runs `trading_lab.selection_gate.run_selection_gate` (fidelity guard
   armed with the lane's recorded searched Sharpe) and folds the result through
   `apply_gate` BEFORE writing any verdict; the full gate block is recorded in
   the lane JSON. A would-be KEEP that fails the gate is KILL the day it is
   minted.
2. **R5-D fixed-config row in every searched-arm comparison**
   ([research-round-5-results.md](research-round-5-results.md); standing since
   Round 6): every lane summary reports `fixed_sharpe`, `bench_sharpe`,
   `searched_sharpe`, and `selection_gap = searched − fixed` (informational, no
   registered threshold).
3. **reason_class rollup** (standing round-level requirement since Round 7; PR
   #121): the Round-9 rollup MUST tabulate `reason_class` counts across all
   lanes and treat ANY nonzero `selection_gate.UNGRADEABLE_CLASSES` share as an
   **infrastructure alarm** reported in the results doc and on the heartbeat —
   never as strategy evidence.

**How the selection-fair gate / R5-D row map onto a VOTE round.** Because members
use FIXED default params (no per-member grid selection), each confluence lane is
itself a fixed-config evaluation — the "search" dimension for the gate is
**(member-set, K)**, exactly the 4 vote configs searched on that instrument. So,
per instrument:

- `fixed_sharpe` = the specific reported config's OOS Sharpe (the pre-declared
  config the lane ledgers);
- `searched_sharpe` = the BEST vote config on that instrument (best over the 4);
- `selection_gap = searched − fixed`.

This is consistent with how R7-C mapped the gate onto a searched family: the gate
runs on EVERY lane, not only would-be KEEPs, and a positive `selection_gap` that
inflates a would-be KEEP is exactly what the fidelity guard is armed to catch.
Each instrument's searched top config is LEDGERED with the round's searched K;
gate replays are report-only rows in the lane JSON. Keep it honest and
consistent with R7-C.

---

## Code + tests already landed in THIS pre-registration PR

Unlike the pure plan-only rounds (R7-C/R8 committed their grids in the RUN
session), Round 9's header protocol lands PLAN + CODE INFRASTRUCTURE here, so the
grid is pinned by tests BEFORE any run:

- To `src/trading_lab/ensemble.py`: `confluence_positions(members, k)` — the
  binary ≥k-of-N vote gate (AND/vote, distinct from `committee_positions`'
  AVERAGE), with the same validation posture as `committee_positions` (≥2
  members, aligned NaN-free indices) plus 0/1-only values and `1 ≤ k ≤ N`.
- To `src/trading_lab/sweeps.py` (mirroring the Round-7/8 layout):
  `_R9_MEMBER_SET_3`, `_R9_MEMBER_SET_5`, `_R9_VOTE_CONFIGS`,
  `_R9_INSTRUMENTS = R7_INSTRUMENTS` (same object), `r9_vote_configs()`, and
  `r9_total_configs()` returning **60** (15 instruments × 4 vote configs) with
  the program cumulative advancing **5,793 → 5,853**.
- To `tests/test_ensemble.py` and `tests/test_sweeps.py`: unit tests for the
  vote threshold logic and edge cases, and pins for the member sets, the 4 vote
  configs, `2 ≤ K ≤ N`, instrument-tuple identity with `R7_INSTRUMENTS`, and the
  **5,793 → 5,853** totals (`r9_total_configs()` = 60).

## What the FUTURE run session must add BEFORE flipping to results

Only the runner + results remain for the RUN PR (plan-before-outcome):

- `scripts/run_r9_confluence_sweep.py` — for each (instrument × vote config):
  load the members at their default params via `load_ohlcv`, compose the lane
  with `confluence_positions`, backtest at engine-default costs on the 1008/252
  walk-forward, and grade under the Round-2 KEEP/KILL rule + ORDER 007
  informational t + `classify_verdict` KILL-SIG + the selection-fair gate on
  every lane (standing rule 1). CLONE a gate-carrying runner (the R7/R8 daily
  runner), never a gate-less template.
- The pre-registered correlation check (§ 6) and trade-count / power impact
  (§ 7) as first-class report sections, computed over the same dev-rail bars.
- `docs/research-round-9-results.md`: verdict counts, every gate FAIL reason
  verbatim, full fixed-config rows (`selection_gap` per lane), the reason_class
  table with the UNGRADEABLE-share infrastructure-alarm line (standing rule 3),
  the correlation + overlap matrices, the trade-count shrinkage / SE-inflation
  table, best informational t vs BOTH the K=4 and K=60 bars, runtime vs cap, and
  the burden ledger line (**5,793 → 5,853** exactly).

## Round-level aggregation (pre-registered)

Each of the 60 lanes exits Round 9 with exactly one verdict: KEEP-dev iff it
passes the Round-2 rule AND the selection-fair gate; else KILL (or KILL-SIG per
`classify_verdict`). Ledger convention: each instrument's searched top vote
config LEDGERED with the round's searched K; gate replays are report-only rows in
the lane JSON. 0-promoted is the expected, complete deliverable.

## What Round 9 will NOT do

- **No execution in THIS pre-registration PR** — this PR contains no sweep, no
  backtest, no runner, and no results; running is a future separately claimed
  slice.
- **No holdout access** — SPENT; `data/p5holdout/` never read, `unlock_holdout`
  never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched.
- **No data fetching, no new tickers** — committed caches only.
- **No per-member re-search** — members are FIXED at default params by design;
  the only searched axis is (member-set, K).
- **No bar-lowering** — `min_tstat(K)` at each lane's honestly-counted K, never
  lowered; reported vs both K=4 and K=60.
- **No OOS validation claims, no broker/order/exchange-write code, no live-API
  configuration** — research-only, per CONSTITUTION.md.
