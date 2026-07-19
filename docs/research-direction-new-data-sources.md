# Research Direction — New Data Sources (a plan-only scoping sketch)

> **Status:** `plan` — a forward-looking DIRECTION SKETCH / scoping memo, NOT a
> binding pre-registered round. **This document sketches candidate directions;
> no round is pre-registered or executed here; execution awaits an explicit
> owner turn.** It ingests no data, adds no code, adds no dependency, and runs
> nothing. Some directions below need owner-provisioned data access, so the
> owner — not an agent — decides whether and when they run. POST-HOLDOUT,
> DEV-ONLY, RESEARCH-ONLY: the holdout stays SPENT, promotion stays CLOSED, the
> 5,913/0 tally is unchanged, and the `min_tstat(K)` Bonferroni bar is
> UNCHANGED and never lowered.

## Scope and status (read first)

This is a scoping memo, not a plan-before-outcome pre-registration. It does the
one thing the mined-out dev surface leaves open: it asks *what a genuinely NEW
data type would look like* and splits the candidates by access cost, so the
owner can pick a direction. It deliberately stops short of pre-registering a
round — a pre-registration pins a grid in `sweeps.py` with tests and commits
hypotheses + kill criteria before any run (the shape used by
[research-round-9-plan.md](research-round-9-plan.md) /
[research-round-10-plan.md](research-round-10-plan.md)). None of that is done
here. When the owner selects a direction, that direction gets its own binding
plan PR under the identical protocol (§4).

Standing rails, absolute and unchanged by this doc: RESEARCH-ONLY forever (no
broker/exchange/order/live-API/data-vendor-credential/real-money surface — ever;
`requirements.txt` is pandas / numpy / yfinance / requests / pytest only,
[CONSTITUTION.md](../CONSTITUTION.md)); the holdout is SPENT
(`data/p5holdout/` never read, `HOLDOUT_START` enforced, `unlock_holdout` never
passed); promotion is CLOSED (every KEEP is a dev-candidate only); the
significance bar `trading_lab.promotion.min_tstat(K)` is never lowered.

## 1. Why now

Ten rounds. **5,913 registered configs of price/volume-derived indicators plus
their combinations have promoted 0** ([current-state.md](current-state.md);
[research-program-dashboard.md](research-program-dashboard.md)). No strategy has
ever cleared the bar; the program best informational t anywhere is 1.66 (R5) vs
a ~2.638-class bar.

The two most recent rounds close the last obvious price-only move. Rounds 9 and
10 pre-registered the owner's "wait until 2 or 3 strategies agree" idea and its
inverse — a cross-thesis-class ≥K-of-N vote to ENTER (R9) and its De Morgan dual,
a ≥K vote to EXIT (R10) — and both nulled (R9: 11 KEEP-dev / 44 KILL / 5
KILL-SIG, best t 1.04; R10: 11 KEEP-dev / 40 KILL / 9 KILL-SIG, best t 1.04, the
SAME BTC-USD SET-3/K=2 lane). Crucially, the pre-registered correlation check in
BOTH rounds found the members **near-independent** — 0 of 15 instruments trip the
>0.5 flag, and the exit-signal correlations EQUAL the entry-signal correlations
to machine precision (`corr(1-x,1-y)=corr(x,y)`,
[research-round-10-results.md](research-round-10-results.md)). That is the load-
bearing finding: **combining near-independent price-derived signals cannot
manufacture an edge the members individually lack.** A vote among independent
members is not one signal counted twice — but it is also not a new source of
edge; it only re-weights inputs that each already null.

The [cross-round meta-analysis](cross-round-meta-analysis.md) states the same
conclusion from five convergent angles: the dev surface is mined out
(three round closings say "anything further on this surface needs either new
data (OWNER-GATED) or a genuinely different idea class, not more variants"),
selection ≈ noise, conditioning loses to its own controls, drawdown reduces
drawdown not return, and nothing transfers across instruments (P4: 13/13
TRANSFER-FAILED).

**The honest conclusion.** The binding constraint is not the *combination* of
price/volume signals — it is the **absence of a single source of post-cost edge
in price/volume history itself**. Rounds 6–10 spent the last untouched channels
of that one input class (volume, gaps, bar frequency, drawdown-anatomy,
interaction conjunctions, cross-class votes) and each confirmed the null. So the
frontier is a genuinely NEW *data type* — an input that could carry information
price does not already reflect — not another transformation or combination of
the inputs we have. This doc scopes those data types.

## 2. Candidate data types

For each candidate: the economic thesis (why it might carry edge that price
does not), example concrete signals, and an HONEST access-cost assessment split
into **(a) self-serve** — testable with data we ALREADY hold or free public
sources importable within the current `requirements.txt` rails — vs **(b)
owner-gated** — needs owner-provisioned, paid, or credentialed access.

### 2.1 Cross-asset / macro-regime — LOWEST cost (self-serve)

**Economic thesis.** A single instrument's own price history says nothing about
the *regime* it sits in. But relationships BETWEEN assets — how bonds and
equities co-move, whether metals are bid as risk-off, the slope implied by
long-duration rates — carry macro-regime information that a per-instrument trend
or reversion rule structurally cannot see. If any regime signal separates the
drawdowns a buy-and-hold suffers from the drift it rides, it would be a genuinely
different information channel than the 30 single-name families already tested.

**Why this is self-serve.** We ALREADY hold the raw material in the committed
15-ticker daily cache (`trading_lab.data.load_ohlcv`): **TLT (long-duration
bonds/rates), GLD + SLV (metals), SPY + QQQ (equity index), BTC-USD (crypto)** —
alongside single names AAPL, AMZN, GOOGL, JPM, META, MSFT, NVDA, TSLA, XOM.
Cross-asset relationship and regime signals are computable from these existing
series with NO new ingestion, NO new ticker, NO new dependency — pure pandas/numpy
over cached OHLCV. This is the only candidate that needs zero new data access.

**Example concrete signals** (all derivable from the existing cache):
- **Bond–equity correlation regime** — rolling `corr(TLT returns, SPY returns)`;
  condition an equity lane on whether bonds and stocks are co-moving (a
  risk-parity-stress tell) vs anti-correlated (normal).
- **Metals-as-risk-off** — rolling `GLD/SPY` (or `GLD`-momentum) as a risk-off
  proxy; condition exposure on whether metals are being bid relative to equities.
- **Term-structure / duration proxy via TLT** — TLT trend/level as a coarse
  rates-regime proxy (falling TLT ≈ rising long rates), conditioning risk assets
  on the rates backdrop.
- **Cross-asset breadth / risk-on composite** — a simple composite of the
  index (SPY/QQQ), credit-sensitive (via TLT), and crypto (BTC) legs as a
  continuous risk-on/off score.

**HONEST caveat — the burned neighbors.** Cross-asset conditioning is NOT
virgin territory. The Round-4 conditioning families already failed a first
attempt and are recorded as **burned classes** in
[strategy-catalog.md](strategy-catalog.md): `crossasset_gate` (a frozen EMA-cross
equity component gated on another instrument's momentum SIGN — 0 KEEP / 2 KILL,
the ungated control beat the gate, [research-round-4-results.md](research-round-4-results.md)
§R4-E) and `regime_switch` (0 KEEP / 6 KILL, §R4-D). A new cross-asset round
must therefore differ **materially** from those, not merely re-skin them, or it
inherits their null by construction. Two ways it can genuinely differ:
- **Continuous conditioning instead of a binary gate.** R4-E gated on the SIGN
  of another instrument's momentum (an on/off switch). A new round would condition
  on a CONTINUOUS regime score (e.g. rolling bond-equity correlation as a
  real-valued state, sizing/tilting smoothly), which is a different object than a
  binary gate and was not what R4 tested.
- **A genuinely new pair / relationship.** R4-E gated an equity component on a
  single other instrument's momentum. A new round would use a cross-asset
  RELATIONSHIP (e.g. the bond-equity correlation regime, or a metals/equity
  ratio) that R4 never formed — the signal is the *co-movement*, not one leg's
  direction.

Either way, the burned-class precedent must be cited in the plan and the control
arm (an unconditioned baseline) is mandatory — the meta-analysis records that
conditioning "loses to its own controls, on every axis tested," so the null is
the honest registered prior even here.

### 2.2 Fundamentals (value / quality) — owner-gated

**Economic thesis.** Earnings, valuation ratios, margins, and balance-sheet
quality are the classic non-price value/quality channel. The thesis is that
cheap/high-quality names outperform expensive/low-quality ones over horizons a
price rule cannot capture, because the signal lives in the financial statements,
not the tape. This is a genuinely different information class than anything the
program has tested (every family to date reads price or volume only).

**Example concrete signals.** Trailing/forward earnings yield, price/book,
gross or operating margin trend, accruals, debt/equity, return-on-equity — as a
cross-sectional rank across the universe (a value/quality tilt), or as a
single-name state condition.

**HONEST access-cost caveat — why this is owner-gated.** yfinance exposes SOME
fundamentals for free, but they are **point-in-time-biased**: the values it
returns are the LATEST reported/restated figures, stamped as if known earlier
than they were. Naive yfinance fundamentals therefore **leak look-ahead**
(survivorship + restatement + reporting-lag bias) — a strategy backtested on
them would "know" earnings before they were released and would silently drop
delisted names. A rigorous fundamentals round needs **point-in-time** data
(as-reported figures with true as-of dates, and a survivorship-complete
universe), which is a provisioned/paid data source, not a free public feed.
**Mark: owner-gated** — the higher-potential signal, blocked on point-in-time
data access the owner must provision.

### 2.3 Flows / positioning — owner-gated

**Economic thesis.** Positioning and flow data measure what other participants
are actually doing — crowding, hedging pressure, sentiment extremes — which can
lead price at turning points in a way price-derived indicators cannot. The thesis
is that extremes in positioning (everyone already long) or in options-implied
fear (rich put skew) precede reversals or regime shifts.

**Example concrete signals.** Short interest / days-to-cover; CFTC Commitment of
Traders (COT) futures positioning; fund-flow series; options-implied put/call
ratio and implied-volatility skew (fear/greed and hedging-demand tells).

**HONEST access-cost caveat — why this is owner-gated.** Most of these are
**owner-provisioned or paid, or awkward to source cleanly** without look-ahead.
COT is public but coarse, lagged, and futures-only (mapping it to the cash
tickers is a modeling choice, not a clean feed); short interest is bi-monthly and
patchy; fund flows and especially **options-implied signals need a data feed**
(a clean options chain / IV-surface history is a vendor product). None is
importable cleanly within the current `requirements.txt` rails without a
credentialed or paid source. **Mark: owner-gated.**

### 2.4 Deliberately out of scope (and why)

Named here so the boundary is explicit, not an oversight:
- **No alt-data scraping** (web-scraped prices, satellite, card-spend, etc.) —
  outside the `requirements.txt` rails, brittle, and licensing-fraught.
- **No sentiment / text feeds requiring vendor keys** (news NLP, social
  sentiment APIs) — needs vendor credentials the constitution forbids adding.
- **Nothing touching a real-money or broker surface** — RESEARCH-ONLY forever;
  no broker, exchange, order, live-API, or data-vendor-credential surface is
  ever added ([CONSTITUTION.md](../CONSTITUTION.md)).

## 3. The recommended first step

**Cross-asset / macro-regime (§2.1) is the recommended first step** — because it
needs NO new data access. The raw material (TLT, GLD, SLV, SPY, QQQ, BTC-USD)
already sits in the committed daily cache, so a cross-asset/macro-regime round
can be pre-registered and RUN under the existing rails on an owner turn, with
zero provisioning, zero new dependency, and zero fetch. It is the lowest-cost way
to test whether a genuinely NEW information channel (cross-asset RELATIONSHIPS,
which no single-name family can see) separates regimes — provided it differs
materially from the burned R4 `crossasset_gate` / `regime_switch` classes
(continuous conditioning and/or a genuinely new pair — see §2.1).

The **fundamentals (§2.2) and flows/positioning (§2.3)** directions are
**higher-potential** — they are genuinely orthogonal information classes, not
transformations of price — **but they are blocked on owner-provisioned
point-in-time / feed data** and cannot self-serve. They are the better bets if
the owner is willing to provision data; the cross-asset step is the better bet if
the constraint is "no new access."

Honest prior, stated up front: even the cross-asset step carries the burned-class
precedent (§2.1), so the registered expectation remains the program null. The
recommendation is about which direction is *runnable now at lowest cost*, not a
claim that it will clear the bar.

## 4. Pre-registration shape (unchanged)

Whichever direction the owner selects would follow the **identical protocol**
already used by every round — a new data type does NOT get an easier bar:
- **Plan before outcome.** The grid is pinned in `sweeps.py` by tests; a binding
  plan PR lands (hypotheses + kill criteria committed) BEFORE any run, and the
  run is a separately claimed slice (the R9 #153-plan / #154-run split, the R10
  #155-plan / #156-run split).
- **The SAME promotion bar.** `trading_lab.promotion.min_tstat(K)` Bonferroni, K
  counted from the searched grid, **never lowered** — reported per-lane and
  program-wide, exactly as Rounds 2–10.
- **Holdout SPENT.** Dev rail only via `trading_lab.data.load_ohlcv`;
  `data/p5holdout/` never read; `unlock_holdout` never passed.
- **Standing rails on every lane.** Selection-fair gate
  ([selection-fair-gate.md](selection-fair-gate.md)) folded through `apply_gate`
  before any verdict; R5-D fixed-config row (`fixed_sharpe` / `searched_sharpe` /
  `selection_gap`); `reason_class` rollup with the UNGRADEABLE-share
  infrastructure alarm.
- **Same costs.** 5 bps slippage + 1 bp commission per side (engine defaults).
- **Control arm mandatory** for any conditioning direction (the unconditioned
  baseline) — the meta-analysis records that conditioning loses to its own
  controls on every axis tested.

## 5. RESEARCH-ONLY guardrails for new data

Any new source admitted to a future round must satisfy the standing rails:
- **Free / public and importable within the current `requirements.txt`** (pandas
  / numpy / yfinance / requests / pytest) — **no new paid dependency, no vendor
  credential, no broker/exchange/live-API/real-money surface**, ever
  ([CONSTITUTION.md](../CONSTITUTION.md)).
- Anything requiring provisioned, paid, or credentialed access is an
  **owner-queue item**, not a self-serve round — an agent cannot take the fetch
  or the spend decision. This is exactly why §2.2 (fundamentals) and §2.3
  (flows) are owner-gated: they cannot be run without an owner provisioning the
  data first.
- New tickers or extended history — even free ones — are an owner go (no new
  fetch without an explicit owner decision, per the constitution's holdout/data
  rail).

## 6. Owner decision needed

Framed as owner-queue items (the owner decides; nothing here is scheduled or
run):

- **(a) Go/no-go on the cross-asset/macro-regime first step (§2.1, §3) —
  self-serve, no new access needed.** If GO, it can be pre-registered as a
  binding plan PR and run under the existing rails on an owner turn, using only
  the committed cache. The one thing to confirm: the plan must differ materially
  from the burned R4 `crossasset_gate` / `regime_switch` classes (continuous
  conditioning and/or a genuinely new cross-asset pair — §2.1), with the
  mandatory unconditioned control arm.
- **(b) Whether to provision point-in-time fundamentals (§2.2) or flows /
  options-implied data (§2.3) for the higher-potential owner-gated directions.**
  These are genuinely orthogonal information classes with more upside than
  cross-asset, but they are BLOCKED on data access: a rigorous fundamentals round
  needs point-in-time (as-reported, survivorship-complete) data, and flows /
  options-implied signals need a data feed. Cost / access is an owner call an
  agent cannot make.

Doing nothing is a perfectly acceptable owner choice — the negative result across
5,913 configs is itself the program's main product, and the paper lane continues
to accrue forward evidence at no compute or owner cost. This doc opens no
data/holdout/promotion path on its own; it only scopes the options.
