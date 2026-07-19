# Research Round 10 — Pre-Registered Plan (Inverse-Confluence EXIT Vote, go-flat when cross-class ≥K-of-N agree)

> **Status:** `binding` — pre-registered Round-10 protocol, committed and
> merged BEFORE any Round-10 sweep, backtest, replay, or outcome exists.
> **PLAN ONLY: this document's own session runs NOTHING.** This PR lands the
> plan, the `trading_lab.ensemble.exit_confluence_positions` exit-vote gate, and
> the pinned 60-config grid (`sweeps._R10_*`, `r10_total_configs()` = 60) with
> tests — it runs NOTHING and grades NOTHING. Executing Round 10 (the sweep
> runner + graded `docs/research-round-10-results.md`) is a FUTURE session's
> separately claimed slice (plan-before-outcome, the ORDER 014 round-6
> precedent: plan PR then run PR, exactly as R9 split #153 plan / #154 run).
> **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion is CLOSED.** Every
> hypothesis, method, and KEEP/KILL rule below is stated in advance; a KEEP
> anywhere in Round 10 means *dev-candidate only*, never a finding. The
> multiple-testing bar is UNCHANGED from Rounds 2–9
> (`trading_lab.promotion.min_tstat`) — no bar-lowering anywhere in this round.

## Provenance and scope

Round 10 pre-registers the **INVERSE of the owner's live signal-confluence
idea**. Owner turn 2026-07-19 (verbatim): *"any more progress on the trading
strategies, what I was thinking about, isn't it a good idea to find multiple
strategies and wait untill at least 2 or 3 give the same signals, what do you
think about that?"* — relayed via the venture-lab coordinator (ORDER 019 / 020).
Round 9 answered the ENTRY framing of that idea (require ≥K agreement to enter);
the coordinator, on the same live owner turn, authorized testing the **exit /
de-risking complement** next. Round 10 is that complement: a cross-thesis-class
**≥K-of-N vote to EXIT to cash** — hold long by default, step aside when ≥K
distinct strategies signal out — under the program's standing corrections,
plan-before-outcome.

The program stands at **5,853 registered configs / 0 promoted** through Round 9
([research-round-9-results.md](research-round-9-results.md)); no strategy has ever
cleared the significance bar, and the program best informational t anywhere is
1.66 (R5) vs a ~2.638 bar. R9 itself returned **0 promoted, best t 1.04**, and
its pre-registered correlation check found the members near-INDEPENDENT (0 of 15
instruments tripped the >0.5 flag). The honest registered prior for Round 10 is
the same null the whole program has returned — and, as § 1 and § 7 argue, an exit
vote over near-independent members has a *structural* reason to null: strict
agreement to exit is rare (so it barely deviates from buy-and-hold), loose
agreement to exit fires often (so it sheds the drift a hold rides). A negative
result is the expected and publishable outcome.

Standing rail, absolute: RESEARCH-ONLY. Dev caches only via
`trading_lab.data.load_ohlcv`; the holdout is SPENT (`data/p5holdout/` never
read, `unlock_holdout` never passed); `experiments/paper/**` untouched; NO
broker/order/exchange-write code, NO live-API config; promotion CLOSED.

## 1. Thesis

The **inverse** of the owner's idea. Where the owner asked to *wait until ≥2 or 3
strategies agree before ENTERING* (Round 9), Round 10 asks the mirror question:
hold long by DEFAULT and use a **cross-class ≥K-of-N confluence to decide when to
STEP ASIDE** (go flat). This is a **risk-OFF de-risking overlay on buy-and-hold**:
in-market unless at least K of N distinct thesis-class members are simultaneously
FLAT (signalling out), in which case the lane goes to cash. The gate is binary
(`trading_lab.ensemble.exit_confluence_positions`): long (1.0) by default, flat
(0.0) on bars where ≥K members are flat. "2 or 3 agree" maps directly to
K ∈ {2, 3} — the same threshold grammar as R9, applied to EXIT instead of ENTRY.

Round 10 is directly motivated by the Round-9 finding: the entry-confluence vote
**sat in cash through the market's drift** (KILL-SIG on trending names — waiting
for agreement to enter cost the rise). The natural complement is to invert the
default: ride the drift by default, and let the *same* ≥K agreement gate you out.

**Honest registered prior (stated in advance).** Because R9 showed the members
are near-INDEPENDENT (0/15 tripped the >0.5 correlation flag), ≥K *agreement to
exit* is also rare — so the two K corners bracket a null from opposite sides:

- the **strict K=3 exit** requires all members flat at once; on near-independent
  members that almost never happens, so the lane barely deviates from
  buy-and-hold — its OOS return ≈ the hold, its deviation ≈ 0, and its
  informational t ≈ 0 (an edge *indistinguishable* from B&H is ungradeable AS an
  edge, § 7);
- the **loose K=2 exit** steps aside often; on a market that drifts up, stepping
  aside frequently **sheds the drift a hold rides**, so it most likely
  UNDERperforms buy-and-hold.

Either corner is expected to NULL (0 promoted). The exit vote could only WIN if
the members COLLECTIVELY flag genuine bad regimes — i.e. their joint flat-signal
lands disproportionately in the drawdowns a hold suffers, sidestepping losses
without shedding the gains. Round 10 MEASURES that rather than assuming it; the
registered expectation is that no such regime-timing gradient clears the
unchanged 2.638-class bar.

## 2. Distinction from priors (all cited) and the honest prior

Round 10 sits against three burned neighbors; it is the risk-OFF dual of the
newest of them.

- **R9 signal-confluence ENTRY vote** (`trading_lab.ensemble.confluence_positions`,
  [research-round-9-results.md](research-round-9-results.md)): a cross-class
  ≥K-of-N vote to ENTER — long only on bars where ≥K distinct members are LONG,
  flat otherwise. Outcome over 60 configs: **11 KEEP-dev / 44 KILL / 5 KILL-SIG,
  0 promoted, best informational t 1.04** (BTC-USD SET-3/K=2); the pre-registered
  correlation check found **0 of 15 instruments trip >0.5** (members
  near-independent); the vote sat flat through the drift and was KILL-SIG on
  trending names. R10 is the **De Morgan DUAL**: the SAME members, SAME grid, but
  the vote gates you OUT of a hold rather than INTO cash.
- **R4-C survivor committee** (`trading_lab.ensemble.committee_positions`,
  [research-round-4-results.md](research-round-4-results.md) § R4-C): **AVERAGED**
  member positions into a *fractional* size (two of three long → `0.5` long) — an
  ~OR-weighted sizing rule, not a binary gate. **5 KEEP-dev / 7 KILL / 0
  KILL-SIG** of 12, best informational t **1.085**, **0 promoted**.
- **R7-C washout_recovery** (`washout_recovery`,
  [research-round-7c-results.md](research-round-7c-results.md)): **AND-gated two
  windows WITHIN ONE thesis-class**. **1 KEEP-dev / 11 KILL / 3 KILL-SIG** of 15,
  best t **0.22**, **0 promoted**, KILL-SIG on AMZN / MSFT / QQQ.

**R10 is none of these.** It is a BINARY ≥K vote (not a fractional average, unlike
R4-C) ACROSS DISTINCT thesis-classes (not two windows within one class, unlike
R7-C) that gates you OUT of a default-long hold (not INTO a long from cash, unlike
R9). No prior round has graded that object.

**The De Morgan relationship, stated exactly.** For a panel of 0/1 member
positions, R9's position is `1` iff ≥K members are LONG; R10's position is `0`
iff ≥K members are FLAT. Equivalently, going flat when ≥K members are flat is a
≥K confluence on the INVERTED member series, and the held position is its
complement:

    exit_confluence_positions(members, K)
        == 1 - confluence_positions([1 - m for m in members], K)

The R10 gate is literally implemented that way (reusing the R9 primitive), so the
two rounds are a proven De Morgan pair over one identical panel.

## 3. Member panel (fixed default params)

Members run at their **fixed `DEFAULT_PARAMS`** — NO per-member re-search — the
SAME two panels as R9, reused verbatim (`sweeps._R10_MEMBER_SET_3` /
`_R10_MEMBER_SET_5` alias the R9 constants). Fixing the members keeps the searched
multiplicity K small (the only searched axis is (member-set, K), not each
member's grid) and gives the exit-confluence idea its **best shot** rather than
burning power on member tuning. Every member is a 0/1 long/flat daily lane in the
`STRATEGIES` registry, named with its thesis-class.

**SET-3** (`sweeps._R10_MEMBER_SET_3` — 3 distinct classes):

| Member | Default params | Thesis-class |
| --- | --- | --- |
| `ema_crossover` | `fast 20 / slow 50` | trend / momentum |
| `rsi_mean_reversion` | `period 14 / oversold 30 / overbought 70` | mean-reversion |
| `donchian` | `entry 20 / exit 10` | breakout |

**SET-5** (`sweeps._R10_MEMBER_SET_5` — 5 distinct classes; SET-3 + two more):

| Member | Default params | Thesis-class |
| --- | --- | --- |
| `ema_crossover` | `fast 20 / slow 50` | trend / momentum |
| `rsi_mean_reversion` | `period 14 / oversold 30 / overbought 70` | mean-reversion |
| `donchian` | `entry 20 / exit 10` | breakout |
| `drawdown_reversion` | `lookback 126 / entry_dd 0.10 / exit_frac 1.0` | drawdown STATE |
| `obv_trend` | `window 50 / price_confirm False` | volume |

No family repeats within a panel (a vote among duplicates is one signal counted
twice). `obv_trend` reads the volume column, which every one of the 15 daily cache
tickers carries. **No member substitutions were required** — the panels are the R9
panels verbatim, and all five names resolve to registry families with sane
defaults that emit clean 0/1 positions on the daily surface. Note the members'
`0` state is read here as a **flat / step-aside signal** (an "out" vote); the exit
vote counts flats, exactly as R9 counted longs.

## 4. Exit-vote gates and the grid

The vote is `exit_confluence_positions(members, K)`: long (1.0) by DEFAULT, flat
(0.0) iff the per-bar count of FLAT members is ≥ K, memoryless, on the members'
shared index. K ∈ {2, 3} for BOTH sets ("2 or 3 agree"), a registered constraint
`2 ≤ K ≤ len(members)`. That is **4 exit-vote configs** (`sweeps._R10_VOTE_CONFIGS`):
SET-3/K2, SET-3/K3, SET-5/K2, SET-5/K3 — identical (set, members, K) axes to R9,
only the compositor differs. Over the 15-ticker daily surface that is **15 × 4 =
60 registered configs** (`r10_total_configs()` = 60); program cumulative **5,853 →
5,913** (on the future RUN).

## 5. Instruments, timeframe, costs, rail

- **Instruments**: `_R10_INSTRUMENTS = R7_INSTRUMENTS` (verbatim, the SAME tuple
  object, identical to `_R9_INSTRUMENTS`) — the committed 15-ticker daily surface:
  AAPL, AMZN, BTC-USD, GLD, GOOGL, JPM, META, MSFT, NVDA, QQQ, SLV, SPY, TLT,
  TSLA, XOM. No new caches, nothing fetched, no post-hoc instrument selection.
- **Timeframe**: daily.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults).
- **Walk-forward geometry**: train 1008 / test 252 daily bars, contiguous test
  windows, exactly as Rounds 2–9.
- **Rail**: dev only via `trading_lab.data.load_ohlcv` — holdout SPENT,
  `HOLDOUT_START` enforced, `data/p5holdout/` never read.

## 6. PRE-REGISTERED correlation check (mandatory, first-class)

Confluence — entry OR exit — is only meaningful between INDEPENDENT signals. For
each instrument the run session MUST compute and report, over the members' shared
dev-rail bars, on the **exit-signal series** (the members' FLAT-bars, the "out"
votes):

  (a) pairwise **correlation of member EXIT-SIGNAL series** (the 0/1 flat lanes);
  (b) pairwise **signal-overlap** = fraction of bars both members are flat among
      bars *either* is flat (Jaccard-style: `|A∩B| / |A∪B|` over flat-bars); and
  (c) pairwise **correlation of member daily RETURN streams**.

**Note the Pearson identity.** For 0/1 series, `corr(1-x, 1-y) = corr(x, y)` — so
the member EXIT-signal (flat-bar) correlation EQUALS the R9 member POSITION
(long-bar) correlation already reported. The registered expectation is therefore
the SAME finding R9 reported: **0 of 15 instruments trip the >0.5 flag**, members
near-independent. R10 recomputes and reports it on the exit-signal series to
CONFIRM the identity, not to re-derive a different number.

The full pairwise overlap matrix is reported per instrument (SET-5 is the
superset; SET-3 is its 3×3 sub-block). **Pre-registered interpretation rule,
verbatim (identical to R9):** *"Confluence between correlated members is one
signal counted twice; if mean pairwise member position-correlation on an
instrument exceeds ~0.5, any apparent vote edge is not diversified and must be
reported as such."* A vote edge on a high-correlation instrument is therefore
disqualified as diversification evidence at report time, not re-litigated after
outcomes.

## 7. PRE-REGISTERED trade-count / power impact (mandatory, first-class)

Fewer / opposite trades = weaker or degenerate statistics — this is stated up
front, not buried, because it is the mechanism by which the honest prior (§ 1)
expects the null. For each instrument the run session MUST report:

- **exits(K=2)** and **exits(K=3)** — the count of step-aside events per lane
  (the number of times each exit-vote lane goes flat);
- the **trade count vs buy-and-hold** per lane (buy-and-hold trades once at entry
  and holds; each exit adds a round-trip), and the implied deviation from the
  hold; and
- the implied **Sharpe standard-error inflation**: with
  `SE(SR) ∝ sqrt((1 + SR²/2) / N)`, fewer *effective* independent return
  observations that differ from the hold ⇒ a LARGER SE ⇒ a HIGHER t required to
  clear the same fixed effect.

State explicitly in the results: because the members are near-independent (§ 6),
the two exit corners fail from opposite directions —

- a **rarely-firing strict K=3 exit ≈ buy-and-hold**: near-zero deviation ⇒
  near-zero informational t ⇒ **ungradeable as an edge** (indistinguishable from
  the hold, not a finding); and
- a **frequently-firing loose K=2 exit sheds drift**: it steps aside through
  up-days a hold rides, most likely UNDERperforming B&H —

either way fewer/opposite trades weaken the statistics; the shrinkage/degeneracy
IS part of the finding, never buried. **Flag any (instrument, K) exit lane that
produces ~0 exits** — a degenerate lane indistinguishable from buy-and-hold — in
the `reason_class` rollup (§ 9). Trades are never invented to rescue power.

## 8. Promotion bar (SAME as all prior rounds)

`trading_lab.promotion.min_tstat(K)` Bonferroni, K counted from the searched
grid, **never lowered**. Every lane reports its informational t against BOTH
thresholds:

- **per-lane K = 4** (the 4 exit-vote configs searched on a single instrument):
  `min_tstat(4) ≈ 2.24`;
- **program-wide K = 60** (the full round grid): `min_tstat(60) ≈ 3.14`
  (`R10_K = 60`).

The holdout is SPENT (dev rail only); promotion is CLOSED — every KEEP is a
dev-candidate only, never a finding. **0-promoted is a valid, publishable
outcome**; the bar is never softened and trades are never invented.

## 9. Standing rails applied on every lane

The three standing requirements (rails, restated as binding for this round):

1. **Selection-fair gate on every lane**
   ([selection-fair-gate.md](selection-fair-gate.md); PR #111): every Round-10
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
   #121): the Round-10 rollup MUST tabulate `reason_class` counts across all
   lanes and treat ANY nonzero `selection_gate.UNGRADEABLE_CLASSES` share as an
   **infrastructure alarm** reported in the results doc and on the heartbeat —
   never as strategy evidence. The degenerate ~0-exit lanes flagged in § 7 are
   rolled up here (indistinguishable-from-B&H, reported as infra/degeneracy, not
   as strategy evidence).

**How the selection-fair gate / R5-D row map onto an EXIT-VOTE round.** Because
members use FIXED default params (no per-member grid selection), each exit-vote
lane is itself a fixed-config evaluation — the "search" dimension for the gate is
**(member-set, K)**, exactly the 4 exit-vote configs searched on that instrument.
So, per instrument:

- `fixed_sharpe` = the specific reported config's OOS Sharpe (the pre-declared
  config the lane ledgers);
- `searched_sharpe` = the BEST exit-vote config on that instrument (best over the
  4);
- `selection_gap = searched − fixed`.

This is consistent with how R9 and R7-C mapped the gate onto a searched family:
the gate runs on EVERY lane, not only would-be KEEPs, and a positive
`selection_gap` that inflates a would-be KEEP is exactly what the fidelity guard
is armed to catch. Each instrument's searched top config is LEDGERED with the
round's searched K; gate replays are report-only rows in the lane JSON. Keep it
honest and consistent with R9.

---

## Code + tests already landed in THIS pre-registration PR

Following the R9 header protocol, Round 10's pre-registration lands PLAN + CODE
INFRASTRUCTURE here, so the grid is pinned by tests BEFORE any run:

- To `src/trading_lab/ensemble.py`: `exit_confluence_positions(members, k)` — the
  risk-OFF ≥k-of-N exit-vote gate (long by default, go flat when ≥k members are
  flat), the De Morgan dual of `confluence_positions` applied to a buy-and-hold
  baseline, implemented as `1 - confluence_positions([1 - m for m in members], k)`
  and inheriting the R9 primitive's validation (≥2 members, aligned NaN-free
  indices, 0/1-only values, `1 ≤ k ≤ N`).
- To `src/trading_lab/sweeps.py` (mirroring the Round-9 layout):
  `_R10_MEMBER_SET_3` / `_R10_MEMBER_SET_5` (aliasing the R9 sets),
  `_R10_VOTE_CONFIGS`, `_R10_INSTRUMENTS = R7_INSTRUMENTS` (same object),
  `r10_vote_configs()`, and `r10_total_configs()` returning **60** (15 instruments
  × 4 exit-vote configs) with the program cumulative advancing **5,853 → 5,913**.
- To `tests/test_ensemble.py` and `tests/test_sweeps.py`: unit tests for the
  exit-vote threshold logic, the De Morgan identity, and edge cases, and pins for
  the member sets (identity with the R9 panels), the 4 exit-vote configs,
  `2 ≤ K ≤ N`, instrument-tuple identity with `R7_INSTRUMENTS`, and the
  **5,853 → 5,913** totals (`r10_total_configs()` = 60).

## What the FUTURE run session must add BEFORE flipping to results

Only the runner + results remain for the RUN PR (plan-before-outcome):

- `scripts/run_r10_exit_confluence_sweep.py` — for each (instrument × exit-vote
  config): load the members at their default params via `load_ohlcv`, compose the
  lane with `exit_confluence_positions`, backtest at engine-default costs on the
  1008/252 walk-forward, and grade under the Round-2 KEEP/KILL rule + ORDER 007
  informational t + `classify_verdict` KILL-SIG + the selection-fair gate on every
  lane (standing rule 1). CLONE a gate-carrying runner (the R9 daily runner),
  never a gate-less template. The benchmark is **buy-and-hold** (the exit vote is
  an overlay ON the hold), so each lane's edge is measured as its deviation from
  the hold.
- The pre-registered correlation check (§ 6) and trade-count / power impact (§ 7)
  as first-class report sections, computed over the same dev-rail bars.
- `docs/research-round-10-results.md`: verdict counts, every gate FAIL reason
  verbatim, full fixed-config rows (`selection_gap` per lane), the reason_class
  table with the UNGRADEABLE-share infrastructure-alarm line AND the degenerate
  ~0-exit / indistinguishable-from-B&H flags (standing rule 3, § 7), the exit-
  signal correlation + overlap matrices (confirming the `corr(1-x,1-y)=corr(x,y)`
  identity vs R9), the exit-count / trade-count-vs-B&H / SE-inflation table, best
  informational t vs BOTH the K=4 and K=60 bars, runtime vs cap, and the burden
  ledger line (**5,853 → 5,913** exactly).

## Round-level aggregation (pre-registered)

Each of the 60 lanes exits Round 10 with exactly one verdict: KEEP-dev iff it
passes the Round-2 rule AND the selection-fair gate; else KILL (or KILL-SIG per
`classify_verdict`). A lane that produces ~0 exits (indistinguishable from
buy-and-hold) is flagged degenerate in the reason_class rollup and reported as
infra/degeneracy, never as strategy evidence. Ledger convention: each instrument's
searched top exit-vote config LEDGERED with the round's searched K; gate replays
are report-only rows in the lane JSON. 0-promoted is the expected, complete
deliverable.

## What Round 10 will NOT do

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
