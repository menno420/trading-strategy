# Research Round 7 — Pre-Registered Plan (Structure-of-Price Families, PLAN ONLY)

> **Status:** `binding` — pre-registered Round-7 protocol, committed and
> merged BEFORE any Round-7 sweep, backtest, replay, grid code, or outcome
> exists. **PLAN ONLY: this document's own session runs NOTHING — executing
> Round 7 (including committing the grids + tests below to
> `trading_lab.sweeps`) is a FUTURE session's separately claimed slice**
> (plan-before-outcome, the ORDER 014 round-6 precedent: plan PR #116,
> run PR #118, two claims). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT
> and promotion is CLOSED.** Every hypothesis, method, and KEEP/KILL rule
> below is stated in advance; a KEEP anywhere in Round 7 means
> *dev-candidate only*, never a finding. The multiple-testing bar is
> UNCHANGED from Rounds 2–6 (`trading_lab.promotion.min_tstat`, ~2.64 at
> K=12) — no bar-lowering anywhere in this round; K only ever rises with
> variants actually tried.

## Provenance, scope, and the direction pick (justified here, per ORDER 015)

Round 6 closed (PR #118, `0d12515`;
[research-round-6-results.md](research-round-6-results.md)) at 3 KEEP-dev /
47 KILL / 8 KILL-SIG of 58 lanes, 0 promoted, best t 0.60 vs the 2.638 bar,
program cumulative **5,055 registered configs — 0 promoted anywhere**. The
program retrospective
([research-program-retrospective.md](research-program-retrospective.md) §(g))
lists four neutral round-7+ options. This plan picks **option 2 — genuinely
new idea families on existing data** — because it is the CHEAPEST option
that still bears evidence:

- Options 1 (new data classes) and 3 (R5-C OOS execution) are
  **owner-gated** — each needs an explicit owner ORDER plus a fetch;
  agents cannot take that decision, so neither is plannable agent-side
  (§(g) items 1 and 3, verbatim: "require a fetch decision the agents
  cannot take" / "one owner ORDER fixing a post-2026 window").
- Option 4 (stopping / steady-state) costs zero but **registers no new
  evidence** and needs no plan — the paper lane already runs on cron.
- Option 2 is §(g)'s own lowest-cost entry: "Cost: lowest — no owner
  action, committed caches only, compute in the round-6 range (r6 ran 696
  configs in under 26 s/slice)". Standing owner direction ORDER 012 item 4
  ("new strategies, new stocks/tickers, new indicators — every result
  recorded honestly") makes it self-startable, per the ORDER 014 round-6
  precedent and ORDER 015(a)(3).

Honest registered prior, carried from §(g) verbatim: "three round closings
already predict the null" — the expected Round-7 outcome is more honest
nulls, and that is a complete deliverable.

Round 7 registers **two genuinely new families on the COMMITTED daily
caches only**, both reading only price columns already served by the dev
rail, both structurally distinct from all ~27 burned families: the first
**drawdown-anatomy** family (signal = depth of the current drawdown from a
trailing peak — no prior family conditions on drawdown, which the
retrospective §(f) flags as "the only consistently observed effect, never
a decision metric") and the first **high-proximity state** family (signal
= closeness of the close to its trailing N-bar maximum — the classic
52-week-high effect as a state band, NOT an event-triggered breakout).
Adjacency is declared in advance in each slice below (nearest burned
neighbors: pullback / Donchian) with the exact structural difference
stated, so "new family vs variant" cannot be re-litigated after outcomes.

Directions considered and NOT registered, recorded for honesty: any hourly
slice (round 6 re-confirmed hourly as "a KILL amplifier at baseline costs
(15/16)" and R5-B showed 5-split single-window luck — the marginal
evidence per config is the program's worst); any calendar family (R4-F
burned the class at 0/75 with 30 KILL-SIG); anything needing a fetch
(owner-gated); the `data/p2ext/` extended caches (2 tickers — too thin,
same reason round 6 declined them).

## The three standing requirements (rails for this round, restated as binding)

1. **Selection-fair gate on every lane** ([selection-fair-gate.md](selection-fair-gate.md),
   which stamps the standing decision; PR #111 `d498018`): every Round-7 runner runs
   `trading_lab.selection_gate.run_selection_gate` (fidelity guard armed
   with the lane's recorded searched Sharpe) and folds the result through
   `apply_gate` BEFORE writing any verdict; the full gate result block is
   recorded in the lane JSON. A would-be KEEP that fails the gate is KILL
   the day it is minted.
2. **R5-D fixed-config row in every searched-arm comparison**
   ([research-round-5-results.md](research-round-5-results.md) closing
   tally item 4; standing since round 6): every lane summary reports
   `fixed_sharpe`, `bench_sharpe`, `searched_sharpe`, and
   `selection_gap = searched − fixed` (informational, no registered
   threshold). As in round 6, the gate's own result block satisfies this
   row for every graded lane — the gate runs on EVERY lane, not only
   would-be KEEPs.
3. **reason_class rollup (NEW as a round-level requirement this round)**
   (PR #121 `c60183f`; [selection-fair-gate.md](selection-fair-gate.md)
   § reason_class): the Round-7 results rollup MUST tabulate
   `reason_class` counts across all lanes and treat ANY nonzero
   `selection_gate.UNGRADEABLE_CLASSES` share as an **infrastructure
   alarm** reported in the results doc and on the heartbeat — never as
   strategy evidence. (Round 6 predates the taxonomy; Round 7 is its
   first consumer, closing the night-research-infra card's guard recipe.)

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
  Promotion CLOSED: no Round-7 verdict can promote anything.
- **Costs**: 5 bps slippage + 1 bp commission per side (engine defaults).
- **Walk-forward geometry**: train 1008 / test 252 daily bars, contiguous
  test windows, exactly as Rounds 2–6.
- **Pre-declaration (sequencing for the run session)**: the run session's
  FIRST code commit adds the grids below to `trading_lab.sweeps` WITH
  pinning tests in `tests/test_sweeps.py`, and only then runs — grids in
  code before any sweep, exactly the round-6 mechanics. This plan doc is
  the binding source the tests pin against.
- **Honesty**: nulls and KILLs are first-class deliverables.
- **Runtime caps, no silent truncation**: per-slice caps below; a slice
  that would exceed its cap STOPS, records the partial state and the
  verbatim overrun, and reports CAP-HIT (re-registration required) —
  silent truncation or grid-narrowing mid-run is forbidden.

---

## R7-A — Drawdown-anatomy family (`drawdown_reversion` × 15 daily tickers)

- **Motivation**: no prior family's signal reads drawdown state. The
  retrospective records drawdown reduction as the program's only
  consistently observed effect while never being a decision input
  (§(f) "Drawdown reduction — the only consistently observed effect,
  never a decision metric"). This family inverts the lens: does entering
  INTO large drawdowns (long-only reversion on the existing surface)
  carry exploitable information net of costs?
- **Family** (implementation + causality tests in the run session's first
  commit): `drawdown_reversion` — compute the running peak of closes over
  a trailing `lookback` window (window-local peak, not all-time, so the
  signal cannot embed unbounded history); enter long at bar t when
  `close[t] / peak[t] − 1 ≤ −entry_dd`; exit when the drawdown has
  retraced to `close[t] / peak[t] − 1 ≥ −entry_dd × (1 − exit_frac)`
  (exit_frac = 1.0 means full recovery to the peak band). All indexing
  causal (peak through bar t uses closes ≤ t; fills at t+1 open as
  always).
- **Declared adjacency (nearest burned neighbor)**: `pullback` (P1
  mean-reversion: short-horizon N-day decline triggers). Structural
  difference: pullback is an event on a FIXED short horizon (bars-counted
  decline); drawdown_reversion is a STATE on a normalized depth-from-peak
  measure with a hysteresis exit — depth-triggered, not duration-triggered.
- **Hypothesis (registered)**: drawdown depth is not exploitable
  long-only net of costs on this surface — most lanes KILL; buying large
  drawdowns on single names mostly buys drift-down regimes (the R4-F
  exposure lesson: being out of the market loses to being invested), so
  KILL-SIG lanes are plausible.
- **Grid** (to be committed as `sweeps._R7_DRAWDOWN_AXES`, pinned by
  tests): `lookback` {63, 126, 252} × `entry_dd` {0.10, 0.20} ×
  `exit_frac` {0.5, 1.0} = **12 variants** (the lab-standard per-lane
  K=12).
- **Instruments**: `R7_INSTRUMENTS = R6_VOLUME_INSTRUMENTS` (verbatim,
  the same tuple object — the committed 15-ticker daily surface of
  R4-F/R6-A). 15 lanes; **180 registered configs**.
- **Decision rule (per lane, pre-registered)**: Round-2 KEEP/KILL on the
  searched walk-forward, THEN the selection-fair gate on every lane
  (standing rule 1); KILL-SIG per `classify_verdict` at K=12; gate block
  = the R5-D fixed-config row (standing rule 2).
- **Burden**: 180 new registered configs; per-lane K=12, bar ~2.638.
- **Runtime cap**: ≤ 15 minutes wall-clock for the whole slice.

## R7-B — High-proximity state family (`high_proximity` × 15 daily tickers)

- **Motivation**: the 52-week-high effect is a classic documented anomaly
  whose mechanism (anchoring near the trailing high) is a STATE claim —
  distinct from breakout (an event claim). No burned family holds a
  position by proximity band: Donchian and `channel_breakout` enter on a
  CROSS of the prior extreme and exit on an opposite-channel cross.
- **Family** (implementation + causality tests in the run session's first
  commit): `high_proximity` — long at bar t while
  `close[t] ≥ p × max(close[t−N+1 … t])`, flat otherwise (state
  evaluated every bar; the trailing max includes bar t so the band can
  never exceed 1.0 and a new high always satisfies it; fills t+1 open).
- **Declared adjacency (nearest burned neighbor)**: `donchian` /
  `channel_breakout`. Structural difference: those are event-triggered
  (entry fires only on the crossing bar, with a separate exit channel);
  this is a memoryless per-bar state band on CLOSES (not highs/lows) with
  a single parameter pair — under it, position is a pure function of the
  last N closes, which no burned family satisfies.
- **Hypothesis (registered)**: the high-proximity state does not beat
  buy-and-hold net of costs here — at high p it approximates B&H minus
  whipsaw costs around the band, at low p it approximates always-long;
  most lanes KILL. The mirror expectation is declared: if proximity DID
  carry the documented anomaly's information, tight bands (p ≥ 0.95, long
  N) should out-grade loose ones — the registered expectation is that no
  such gradient clears anything.
- **Grid** (to be committed as `sweeps._R7_HIGHPROX_AXES`, pinned by
  tests): `N` {63, 126, 252} × `p` {0.85, 0.90, 0.95, 0.98} = **12
  variants**.
- **Instruments**: `R7_INSTRUMENTS` (same tuple as R7-A). 15 lanes;
  **180 registered configs**.
- **Decision rule / burden / cap**: identical rule structure to R7-A;
  180 new registered configs, per-lane K=12; **runtime cap ≤ 15 minutes**
  wall-clock for the whole slice.

---

## Exact code + tests the run session must add BEFORE any run

To `src/trading_lab/sweeps.py` (mirroring the r6 layout at
`_R6_VOLUME_AXES` ff.): `_R7_DRAWDOWN_AXES`, `_R7_HIGHPROX_AXES`,
`R7_FAMILIES`, `R7_INSTRUMENTS = R6_VOLUME_INSTRUMENTS` (same object),
`r7_drawdown_variants()`, `r7_highprox_variants()` (constraint-valid
expansion, 12 each), and `r7_total_configs()` returning **360**
(program cumulative 5,055 → **5,415**). To `tests/test_sweeps.py`: pins
for both axes dicts (exact values above), variant counts (12 + 12),
instrument-tuple identity with `R6_VOLUME_INSTRUMENTS`, and the 360 /
5,415 totals. To `src/trading_lab/strategies/`: the two families with
causality tests (no-lookahead: signal at t must be invariant to bars
> t), in the SAME pre-run commit. Only after those tests are green may
`scripts/run_r7_*.py` execute.

## Round-level aggregation (pre-registered)

Each of the 30 lanes exits Round 7 with exactly one verdict: KEEP-dev iff
it passes the Round-2 rule AND the selection-fair gate; else KILL (or
KILL-SIG per `classify_verdict`). Results land in a new
`docs/research-round-7-results.md`, reporting per slice: verdict counts,
every gate FAIL reason verbatim, full fixed-config rows (`selection_gap`
per lane), the **reason_class table with the UNGRADEABLE-share
infrastructure-alarm line (standing rule 3 — mandatory)**, best
informational t vs the unchanged bar, runtime vs cap, and the burden
ledger line (5,055 → 5,415 exactly; any deviation is a registration
violation, not a rounding note). Ledger convention: each lane's searched
top variant LEDGERED with `variants_tried=12`; gate replays are
report-only rows in the lane JSON.

## What round 7 will NOT do

- **No execution in the planning session** — this plan's PR contains no
  sweep, no backtest, no grid code, no strategy code; running (and the
  pre-run code commit above) is a future session's separately claimed
  slice.
- **No holdout access** — SPENT; `data/p5holdout/` never read,
  `unlock_holdout` never passed.
- **No paper-lane writes** — `experiments/paper/**` untouched.
- **No data fetching, no new tickers** — committed caches only.
- **No R5-C BTC-USD OOS execution** — stays OWNER-GATED
  ([proposals/r5c-btc-bollinger-breakout-oos-proposal.md](proposals/r5c-btc-bollinger-breakout-oos-proposal.md));
  nothing here schedules it.
- **No MTF-Bollinger pre-registration activity** — the draft stays FROZEN.
- **No hourly slices this round** (declared above, with reasons — a
  future round may register them separately).
- **No OOS validation claims, no bar-lowering, no
  broker/order/exchange-write code, no live API configuration** —
  research-only, per CONSTITUTION.md.
