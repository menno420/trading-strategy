# Paper-lane protocol — pre-registered forward paper-trading, zero money

> **Status:** `binding` — the pre-registered protocol for the paper lane
> (forward paper-trading of the sole surviving RULE-PASS candidate on
> genuinely new bars). Written and committed 2026-07-10, BEFORE any
> paper-lane trade outcome is observable: the lane's first eligible
> signal bar is dated strictly after this document's commit date (§3),
> so no rule below can have been shaped by a known result. Companion to
> [p5-holdout-protocol.md](p5-holdout-protocol.md) (whose §2/§3
> conventions are inherited verbatim) and
> [final-report.md](final-report.md) §Holdout (which this lane follows
> from). **This lane involves no real money, no brokerage account, no
> order, no API, and no signup — ever.** It produces mock trades in a
> git-committed ledger, nothing else.

## Why pre-registration (again)

The holdout is SPENT ([final-report.md](final-report.md) §Holdout;
protocol §6: no re-runs, no tuning, ever). The only data that can still
say anything about the surviving candidate is data that did not exist
when its parameters were frozen — bars accruing from tomorrow onward.
But forward data is only evidence if every decision-shaped rule (what
trades, at what size, graded how, judged when) is fixed *before* the
first outcome is observable. A grading rule chosen after watching the
first trade win or lose is just one more fitted parameter. Everything
below is therefore frozen now, while the lane's dataset is empty by
construction. Per the program-wide guard: **any ambiguity in these
rules resolves against the strategy** (§9).

## 1. Subject — one candidate, params frozen

- **PRIMARY (and only) subject:** `donchian × AAPL × daily`, the sole
  candidate that survived the program: P2 RULE-PASS (label demoted from
  "finding" by ORDER 007 — see
  [p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md)) and
  holdout **CONFIRMED** by the mechanical rule but **not significant**
  (§8).
- **Frozen parameters, verbatim:** `{"entry": 15, "exit": 5}` — the
  `top_full_period_variant.params` of
  `experiments/sweeps/p1-trend-following-daily/donchian__AAPL.json`,
  identical to [p5-holdout-protocol.md](p5-holdout-protocol.md) §2
  row P. Re-verified against the sweep JSON on 2026-07-10 before this
  document was written. Any mismatch between this line and that JSON at
  any future read is a protocol violation: stop, trade nothing.
- **Zero tuning:** no parameter may change for the life of the lane.
  A parameter change ends this lane; restarting requires a new
  pre-registered protocol on data not yet accrued at that time.
- **No other subject** may be added. The subject list is closed at one.

## 2. Entry/exit rules — exactly the implementation, nothing else

Signals are the repo's donchian implementation, verbatim
(`src/trading_lab/strategies/donchian.py::generate`, entry=15, exit=5):

- **Long** when bar *t*'s close breaks **above** the rolling maximum of
  the previous 15 bars' highs (channel shifted one bar: built from bars
  [t−15, t−1], so bar *t* never triggers on its own high).
- **Flat** when bar *t*'s close breaks **below** the rolling minimum of
  the previous 5 bars' lows (same one-bar shift).
- If both fire on the same bar, **entry wins** (upper ≥ lower always;
  code order in `generate` makes the long assignment last).
- Otherwise **hold the previous state**; bars before the 15-bar entry
  channel is full are flat (warm-up).

Execution and costs mirror
[p5-holdout-protocol.md](p5-holdout-protocol.md) §3 and the engine
contract (`src/trading_lab/engine.py::run_backtest`; defaults in
`src/trading_lab/config.py`):

- **Fills: t+1-open.** A signal computed on bar *t*'s close fills at
  bar *t+1*'s open — the actual printed AAPL open of the next trading
  day, as served by the standard data path. No intrabar fills, no
  same-bar fills, no limit logic.
- **Costs: 5 bps slippage + 1 bps commission per side**
  (`DEFAULT_SLIPPAGE_BPS = 5.0`, `DEFAULT_COMMISSION_BPS = 1.0`),
  charged on every fill, entry and exit alike. Net-of-cost numbers
  only.
- **Position model: long/flat only.** No shorts, no leverage, no
  scaling, no partial fills.

## 3. Signal data & load path — post-holdout live bars only

- **Only permitted market-data path:** `trading_lab.data.fetch_ohlcv`
  (network fetch into the standard cache) followed by
  `trading_lab.data.load_ohlcv(...)`. No ad-hoc reads of `data/**`, no
  other data source, per the residual-bypass rule in
  [holdout-enforcement.md](holdout-enforcement.md).
- **`unlock_holdout=True` is FORBIDDEN in this lane — permanently.**
  That kwarg existed for exactly one purpose (the P5 one-shot, ORDER
  008) and that purpose is consumed. Any `HoldoutViolationWarning`
  emitted by paper-lane code is a protocol violation, full stop.
- **`HOLDOUT_START = "2025-01-09"` stays pinned**
  (`src/trading_lab/config.py`, enforced by
  `tests/test_data.py::test_holdout_constant_unchanged`) and **the
  holdout is SPENT**: the window 2025-01-09 → 2026-07-10 was read once
  under ORDER 008 and may never be re-read, re-run, or tuned against —
  not for signals, not for warm-up, not for benchmarks.
- **PAPER_LANE_START = 2026-07-11.** Signals may be computed only from
  bars with timestamp ≥ 2026-07-11 — strictly after the last bar
  consumed by the holdout evaluation (fetched 2026-07-10). Bars in
  [2025-01-09, 2026-07-11) are spent and untouchable; bars before
  2025-01-09 are consumed dev data and are not used here either (§9,
  ambiguity A1: warm-up uses live bars only).
- **Warm-up consequence (accepted, against the strategy):** the entry
  channel needs 15 prior bars, so the first bar that can even emit an
  entry signal is the 16th trading day on/after 2026-07-11; the first
  possible fill is the open after that. The lane starts flat and earns
  nothing until then.
- **Known rail gap, pre-registered resolution:** as implemented,
  `load_ohlcv` with `unlock_holdout=False` drops **every** bar
  ≥ `HOLDOUT_START` (`src/trading_lab/data.py`, the
  `df = df[df.index < holdout]` branch) — including post-2026-07-10
  live bars. The standard path therefore cannot currently serve this
  lane's signal data at all. Resolution: **until a dedicated
  paper-lane loader rail exists** — one that returns ONLY bars with
  timestamp ≥ PAPER_LANE_START, can never return a bar in
  [HOLDOUT_START, PAPER_LANE_START), leaves `unlock_holdout` and its
  warning untouched, and lands with its own pinning tests — **no
  signal is computed and the ledger stays empty.** The lane idles
  rather than bending the holdout rail (§9, ambiguity A2). That rail
  is an ordinary code PR (no money, no accounts, no owner gate), but
  it must merge before the first signal.

## 4. Sizing — fixed, small, paper-only

- **Fixed notional: $10,000 per position.** Every entry is a mock
  purchase of $10,000 ÷ fill price shares (fractional shares allowed —
  it is paper). Exits close the whole position.
- **No compounding.** Wins do not raise the next position; losses do
  not lower it. Every position is $10,000 at entry, for the life of
  the lane.
- **Max one open position** at any time (which the long/flat signal
  guarantees anyway; stated so it survives any future refactor).
- **Paper only.** No order is ever placed anywhere. **DEGIRO is a
  read-only manual benchmark only** (owner decision Q-0250): the owner
  may, at their own discretion, manually mirror or eyeball positions
  in their own DEGIRO view — the agent never logs in, never connects,
  never automates, never asks for credentials, and no DEGIRO number
  ever feeds a signal, a fill, or a grade. Nothing in this lane
  requires any account action by the agent; there is deliberately no
  owner-action item here.

## 5. Ledger discipline — commit before the outcome can exist

- **The paper ledger** is `experiments/paper/ledger.md`, append-only:
  one row per action (ENTRY or EXIT) recording signal date, action,
  intended fill bar (next trading day's open), shares at $10,000
  notional, and the signal-side numbers (close, channel values) that
  triggered it.
- **Every mock trade is committed to git BEFORE its outcome window
  opens.** Concretely: a signal computed on bar *t*'s close must be
  committed before bar *t+1*'s market open (the fill). The **git
  commit timestamp is the tamper evidence** — it proves the call was
  made before the outcome was observable.
- **Never backdated, never amended.** Rows are append-only; a wrong
  row is corrected by a new row that references it, never by editing
  history. Forward-only git, as everywhere in this repo.
- **Late = MISS.** If an ENTRY row's commit timestamp is not strictly
  before its fill bar's open, the trade window it opens is graded
  **MISS regardless of its P&L** and the lapse is documented in the
  ledger (§9, ambiguity A3). If a signal could not be committed in
  time (fetch failure, no session), it is **skipped — stay flat**,
  never backfilled.
- Fill prices are recorded at the first grading read after the fill
  bar, from the standard path. Grading recomputes strategy and
  benchmark from the *same* price series at the same read, so
  retroactive dividend/split adjustments cancel in the comparison
  (§9, ambiguity A4).

## 6. Horizon & grading schedule

- **Outcome window = entry fill → exit fill.** A window opens when an
  entry fills (t+1-open after the entry signal) and closes when the
  donchian exit signal's fill lands (t+1-open after the exit signal).
  No fixed calendar horizon; the strategy's own exit defines the
  window, exactly as in every backtest phase.
- **A window is graded when its exit fills** — never while open.
  Open positions are marked in review notes as OPEN, ungraded.
- **Weekly review cadence:** one review pass per calendar week grades
  every window that closed since the last pass and appends the grades
  to the ledger. A week with no closed window and no open position is
  recorded **FLAT** (§7). Missing a weekly pass delays grading; it
  never changes a grade.

## 7. Grading metric & verdict grammar

- **Metric: net-of-costs P&L and return vs same-window AAPL
  buy-and-hold.** Two numbers per closed window, both net of 6 bps per
  side on $10,000 notional:
  1. **Trade P&L:** strategy return over the outcome window itself =
     (exit fill − entry fill)/entry fill, costs both sides. Reported
     as color; it cannot decide a verdict on its own.
  2. **The comparison that decides the verdict** runs over the
     **cycle window**: from the previous window's exit fill (for the
     first cycle: the open of the first trading bar
     ≥ PAPER_LANE_START, warm-up included) to this window's exit
     fill. Strategy return over the cycle = flat (0%) outside the
     outcome window plus the trade P&L inside it; benchmark = $10,000
     of AAPL bought at the cycle start, sold at this exit fill, same
     costs both sides. Same bars, same prices, same cost model.
  The cycle window is used because the naive comparator — B&H over
  the outcome window alone — is degenerate: inside its own window the
  strategy and B&H hold the identical asset at identical fills and
  costs, so they tie by construction and no window could ever grade
  BEAT. The cycle comparator is the meaningful reading that is *less*
  favorable to the strategy: it charges every flat day (warm-up
  included) at full B&H opportunity cost — the benchmark is holding,
  per the founding plan (§9, ambiguity A6).
- **Per-window verdict grammar (closed):**
  - **BEAT** iff strategy cycle return > B&H cycle return, strictly.
  - **MISS** otherwise — including exact ties (§9, ambiguity A5) and
    including §5's late-commit rule.
  - **FLAT** is the verdict of a review week with no position held and
    no window closed — it records that the strategy chose nothing, and
    counts in weeks-reviewed, never in the window denominator.
- **No significance claims at small n.** With the trade rate observed
  on comparable windows (17 trades in ~18 months on the holdout read),
  n will be single-digit for months. Verdicts are counted, not
  tested: no t-stats, no p-values, no "significant" in any weekly
  note. The ORDER 007 significance machinery
  (`trading_lab.promotion.grade_promotion`) applies only at the
  promotion gate (§8), which this lane cannot trigger.
- **Aggregate reporting:** every summary line carries its denominator
  explicitly — `k BEAT of n closed windows (m weeks reviewed, of
  which f FLAT)`. No aggregate without its window count; no omitting
  MISS or FLAT rows, ever.

## 8. Multiple-testing burden inherited — what this lane can and cannot show

Carried in verbatim so it cannot be forgotten later:

- The candidate emerged from **177 configurations tried in its P1 lane**
  (`p1-trend-following-daily`, plus per-split re-selection as
  documented there) and from a program that made **13 holdout reads**
  program-wide (ORDER 008, one shot each).
- Its holdout verdict was **CONFIRMED but NOT significant**: Sharpe
  **0.759 vs B&H 0.740**, net of costs — **t = 0.02** under the ORDER
  007 rule, versus a 1.64 minimum at the most lenient K=1 (3.45 at the
  honest K=177). Deep inside noise; the Sharpe edge came from smaller
  drawdown while total return trailed holding
  ([final-report.md](final-report.md) §Holdout).
- Therefore: **paper-lane results are evidence-gathering, NOT
  promotion.** No count of BEATs here — however long the streak —
  promotes the candidate, changes its RULE-PASS label, or licenses any
  real-money implication. **Promotion would require a NEW, owner-gated,
  pre-registered out-of-sample protocol on post-2026 data**, written
  before its own data is read, with its own verdict rules — **and the
  agent never schedules it.** That decision belongs to the owner alone
  (a new ORDER in `control/inbox.md`), exactly like the §7 gate in
  [p5-holdout-protocol.md](p5-holdout-protocol.md).

## 9. Ambiguity rule — and the ambiguities already resolved

**Binding rule (inherited from
[p5-holdout-protocol.md](p5-holdout-protocol.md) §5):** if any rule in
this document turns out to be ambiguous in some edge case, the
resolution must be the one *less favorable* to the strategy, and the
ambiguity plus its resolution must be documented **where the result
lands** — in the ledger row / weekly note it affects, not in a
separate file nobody reads.

Ambiguities identified while writing this protocol, resolved against
the strategy now:

- **A1 — warm-up data.** Spent-holdout bars could arguably serve as
  channel warm-up (they are consumed data, and P5 allowed dev-data
  warm-up). Resolved against: warm-up uses ONLY bars
  ≥ PAPER_LANE_START; the lane forfeits ~3 weeks of potential signals
  (§3).
- **A2 — load-path gap.** The standard loader cannot serve live bars
  without the forbidden kwarg. Resolved against: the lane trades
  nothing until a dedicated ≥ PAPER_LANE_START rail merges; no interim
  ad-hoc reads (§3).
- **A3 — late commits.** A trade committed after its fill's outcome
  window opened is graded MISS regardless of P&L (§5).
- **A4 — retroactive price adjustment.** Auto-adjusted history can
  restate past bars; grading reads strategy and benchmark from the
  same series at the same time so the restatement cancels; recorded
  fills are never edited (§5).
- **A5 — ties.** A window whose strategy cycle return exactly equals
  B&H's is a MISS (§7).
- **A6 — degenerate comparator.** "Same-window B&H" over the outcome
  window alone always ties (identical asset, fills, and costs while
  in-position), which would make BEAT unreachable and the lane
  uninformative. Resolved to the cycle-window comparator — the
  meaningful reading that is harsher on the strategy, since every
  flat day (warm-up included) is charged at full B&H opportunity
  cost (§7).
