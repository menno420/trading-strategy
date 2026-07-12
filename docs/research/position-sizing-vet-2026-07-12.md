# Position-sizing vet — 80% vs 40% vs fixed stake on a small account

> **Status:** `reference` — **DEV-ONLY / ILLUSTRATIVE research note.** This
> document vets the owner's position-sizing idea with textbook
> fractional-Kelly math and a **self-contained synthetic Monte Carlo**
> (`scripts/position_sizing_mc.py`, pure numpy + stdlib). It reads **no market
> data**, imports **no `trading_lab` data module**, touches **no holdout** (the
> holdout is SPENT — [final-report.md](../final-report.md) §Holdout), opens **no
> account**, and places **no live or paper trade**. It makes **no
> out-of-sample, FINDING, or PROMOTED claim** and does not reopen the CLOSED
> research round. Every number below is synthetic and illustrative — it shows
> how sizing rules *behave*, and cannot show that any real strategy has an edge,
> because **sizing scales edge and drag; it never creates edge.**

---

## 0. Plain-language verdict for the owner (read this first)

You asked: run a small live account (€100–200), a bot that holds at most one
open trade and stakes ~80% of the current account value each trade (compounding
up and down); later, parallel bots at 40% and at a fixed constant stake — **what
honestly happens?**

**The honest answer: the experiment as designed measures LUCK and COST DRAG, not
skill — unless a genuinely profitable strategy exists *first*, and our own
evidence says we do not have one.** Position sizing is a *multiplier* on a
strategy's per-trade edge. If the edge is real and positive, 80% sizing
compounds it hardest (and swings hardest). If the edge is zero or negative — the
base case for everything this lab has tested — then:

- **80% sizing:** on a **no-edge** bot (µ = 0), €100 drifts to a **median of
  ≈ €94 after 200 trades** purely from volatility drag (25th–75th percentile
  ≈ €75–€118), with occasional lucky paths up top and losing paths below. Ruin
  (falling under €20) is rare at low per-trade volatility but climbs steeply as
  volatility rises or the horizon lengthens (≈15% ruin by 500 trades at 5%
  per-trade vol). On a **slightly negative-edge** bot (µ = −0.2%/trade) the same
  €100 → **median ≈ €68 after 200 trades**, ≈ €39 by 500 — a slow-then-faster
  compounding bleed.
- **40% sizing:** the same shape, gentler — less drag, less ruin, less upside.
  Half the fraction is roughly a quarter of the drag.
- **Fixed €80 stake:** loses **roughly linearly** rather than compounding away —
  but because it does **not** shrink the bet as the account shrinks, over long
  losing runs it is actually the **most** likely to hit outright zero (at
  µ = −0.2% it wipes the median path by ~trade 302 over a 500-trade run).

**None of this is a reason to fund a live account.** Our program has **no
demonstrated positive net edge**: after 668 configurations, **0 of 13** holdout
subjects cleared the significance bar, the sole rule-pass read **t = 0.02**, and
measured edges were fractions of a Sharpe point ([§2](#2-cost-reality-at-100200)).
At €100–200, round-trip costs of 0.5–3% per trade make the base case **µ_net ≤ 0
by construction** ([§2](#2-cost-reality-at-100200)). The place to answer "what
would happen" with **€0 at risk** already exists: the frozen paper lane, grading
from **2026-07-17** ([§4](#4-the-constructive-alternative-zero-money)).

---

## 1. The math — fractional sizing scales edge and drag, it never creates edge

Model each trade as an i.i.d. return `r` on the position, with per-trade edge
`µ = E[r]` and per-trade volatility `σ = std(r)`. A **fractional** rule stakes a
fixed fraction `f` of the *current* account, so the account multiplies:

```
account_{t+1} = account_t · (1 + f · r)
```

Compounding means the relevant growth rate is the **log** growth per trade.
Expanding `log(1 + f·r)` to second order and taking expectations:

```
g(f)  ≈  f·µ  −  ½ · f² · σ²
        └edge┘    └ volatility drag ┘
```

Two terms, and both are **pure functions of the strategy's µ and σ**:

- **`f·µ`** — the edge term. Linear in `f`. **If µ ≤ 0 this term is ≤ 0 for
  every f > 0.** Sizing cannot flip its sign.
- **`−½·f²·σ²`** — **volatility drag**, always negative, growing with the
  **square** of the fraction. Doubling `f` **quadruples** the drag.

**The growth-optimal fraction (Kelly):** maximise `g(f)` → `dg/df = µ − f·σ² = 0`:

```
f*  =  µ / σ²          (Kelly fraction)
```

- **µ > 0:** `g(f)` is an upside-down parabola peaking at `f*`. It is positive
  on `0 < f < 2f*` and **turns negative for `f > 2f*`** — **over-betting past
  twice Kelly converts a genuinely positive-edge system into a losing one**,
  entirely through drag. Example (σ = 3%): a *real but tiny* edge µ = 0.02%/trade
  has `f* = 0.0002/0.0009 ≈ 0.22`, so `2f* ≈ 0.44`. At **f = 0.80** the growth
  rate is `0.8·0.0002 − ½·0.64·0.0009 = −1.3×10⁻⁴/trade` — **negative**, i.e. the
  80% bot *loses* on a real, positive-edge strategy because it is over-betting;
  the 40% bot (`g = +8×10⁻⁶`) barely wins, and Kelly-22% wins most. Higher
  fraction is **not** "more aggressive growth"; past `2f*` it is self-liquidation.
- **µ = 0:** `g(f) = −½·f²·σ² < 0` for any `f > 0`. **Every fractional bettor
  loses to drag; the bigger the fraction, the faster.** Only a fixed stake
  (which does not compound) avoids the drag — it instead random-walks with a
  constant-euro step.
- **µ < 0:** every term is negative. Higher `f` loses faster **and**
  compounds the loss (the bet shrinks with the account, so a fractional bettor
  bleeds asymptotically toward — but never exactly reaches — zero); a **fixed**
  stake loses roughly **linearly** and *can* reach exactly zero.

**The load-bearing point:** `f` (80% vs 40% vs fixed) only ever rescales `µ` and
its drag. **It is a lever on an edge that must already exist.** Whether the
experiment makes money is decided by the sign of `µ_net`, not by the sizing rule.

---

## 2. Cost reality at €100–200

`µ` above must be **net of trading costs**. Net edge per trade is
`µ_net = µ_gross − c`, where `c` is the **round-trip** cost as a fraction of the
position. To merely break even (`µ_net = 0`) the strategy's **gross** per-trade
edge must **exceed the round-trip cost**:

```
break-even gross per-trade edge  =  c   (round-trip cost, as % of position)
```

At €100–200 with positions of €80–160, `c` is punishing because fixed fees and
spreads are large *relative to the tiny position*:

| Round-trip cost `c` | Typical small-account source | Break-even gross edge **per trade** | On a €80 position that is |
|---|---|---:|---:|
| 0.5% | tight crypto spot spread + low fee | 0.50% | €0.40 |
| 1.0% | typical retail crypto / CFD | 1.00% | €0.80 |
| 2.0% | wider spread or ~€0.80/side flat fee | 2.00% | €1.60 |
| 3.0% | wide spread + flat fees on a tiny ticket | 3.00% | €2.40 |

A flat commission alone is brutal at this size: **€1 per side on an €80 position
is €2 round-trip = 2.5%** that the strategy must out-earn *every trade* before it
makes a cent.

**Now compare with what this program actually measured** (all citations to
[final-report.md](../final-report.md)):

- **0 of 13** holdout subjects cleared the ORDER 007 significance bar, "even at
  the most lenient K = 1" (final-report §Holdout; ORDER 007 in
  [control/inbox.md](../../control/inbox.md), coded in
  [`src/trading_lab/promotion.py`](../../src/trading_lab/promotion.py):
  `PROMOTED-TO-FINDING` requires `t ≥ t_min(K)`, else `RULE-PASS`).
- The **sole rule-pass** candidate (AAPL-donchian 15/5) read a holdout edge of
  **+0.019 Sharpe, t = 0.02** — "deep inside noise" (final-report §Headline).
- Program-wide, edges were **fractions of a Sharpe point**, earned by *losing
  less in drawdowns*, not by out-returning buy-and-hold (CAGR trailed B&H in all
  three windows).

A fraction-of-a-Sharpe, statistically-insignificant, drawdown-shaped edge does
**not** translate into a **0.5–3% gross edge per trade net of costs**. There is
no measured strategy in this lab whose `µ_gross` clears even the cheapest
break-even row above with any confidence. **Honest conclusion: the base case is
`µ_net ≤ 0`.** The sizing experiment therefore runs on top of a zero-or-negative
edge, and §1 says exactly what that produces.

---

## 3. Monte Carlo — three sizing rules × four net-edge scenarios

Fully synthetic and reproducible: `scripts/position_sizing_mc.py` (pure numpy +
stdlib; **no repo data imports, no market data, no holdout**). Per-trade returns
are drawn `r ~ Normal(µ, σ)` with **µ already net of costs**. Start €100;
"ruin" = equity < €20. Fractional rules multiply the account by `(1 + f·r)`
(wiped if `1 + f·r ≤ 0`); the fixed rule adds `€80 · r` each trade (floored at
€0, absorbing). **10,000 paths** per cell, base **σ = 3%/trade**, seed = 20260712
(deterministic). Raw dump: `docs/research/position-sizing-mc-2026-07-12.json`.

### 3a. Headline: the no-edge base case (µ = 0), σ = 3%

| Horizon | Rule | Median final | 25th–75th pct | Ruin prob | Median time-to-ruin |
|---|---|---:|---:|---:|---:|
| **200** | **frac 80%** | **€94.43** | €75.20 – €118.10 | **0.0%** | — |
| 200 | frac 40% | €98.41 | €88.23 – €110.82 | 0.0% | — |
| 200 | fixed €80 | €100.27 | €77.92 – €123.03 | 1.5% | — |
| 100 | frac 80% | €97.15 | €82.55 – €115.04 | 0.0% | — |
| 100 | frac 40% | €99.33 | €91.65 – €107.86 | 0.0% | — |
| 100 | fixed €80 | €100.62 | €83.94 – €116.67 | 0.1% | — |
| 500 | frac 80% | €85.86 | €59.22 – €123.35 | 0.8% | — |
| 500 | frac 40% | €96.67 | €80.60 – €115.68 | 0.0% | — |
| 500 | fixed €80 | €99.21 | €62.82 – €135.26 | 12.8% | — |

The MC reproduces the analytic drag exactly: µ = 0, f = 0.8, σ = 3% predicts
`exp(−½·0.64·0.0009·200) = €94.4` — the table reads €94.43. **A no-edge 80% bot
does not stay at €100; it erodes to a median ≈ €94 over 200 trades, with wide
scatter, purely from volatility drag.** 40% erodes ~4× less; a fixed stake holds
its median near €100 (no compounding drag) but its **flat euro bet makes it the
most ruin-prone over long horizons** (12.8% ruin by 500 trades — it keeps
staking €80 of a shrinking account).

### 3b. Slightly negative edge (µ = −0.2%/trade), σ = 3%

| Horizon | Rule | Median final | 25th–75th pct | Ruin prob | Median time-to-ruin |
|---|---|---:|---:|---:|---:|
| 200 | frac 80% | €68.28 | €54.12 – €85.70 | 0.0% | — |
| 200 | frac 40% | €83.67 | €74.68 – €93.85 | 0.0% | — |
| 200 | fixed €80 | €67.88 | €45.24 – €91.22 | 11.0% | — |
| 500 | frac 80% | €38.52 | €26.58 – €55.24 | 14.7% | — |
| 500 | frac 40% | €64.73 | €53.84 – €77.55 | 0.0% | — |
| 500 | fixed €80 | **€0.00** | €0.00 – €55.81 | **60.7%** | **~302 trades** |

The compounding bleed: 80% halves the account by ~500 trades and starts ruining
paths; 40% bleeds far slower. The **fixed €80 stake wipes the median path to €0**
over 500 trades (60.7% ruin) — a small constant edge loss × a constant euro bet
depletes a €100 account **linearly to zero**, because the stake never de-risks as
the account falls. (This is the honest counter-intuition: a fixed stake protects
you from *compounding away* in mild/short runs, but exposes you to *outright
ruin* in long negative-edge runs.)

### 3c. If a real positive edge existed (µ = +0.2% and +0.5%), σ = 3%, 200 trades

| µ | Rule | Median final | 25th–75th pct | Ruin prob |
|---|---|---:|---:|---:|
| +0.20% | frac 80% | €130.38 | €103.95 – €163.83 | 0.0% |
| +0.20% | frac 40% | €115.60 | €103.40 – €129.93 | 0.0% |
| +0.20% | fixed €80 | €131.93 | €109.48 – €154.75 | 0.1% |
| +0.50% | frac 80% | €211.14 | €166.59 – €265.29 | 0.0% |
| +0.50% | frac 40% | €146.78 | €130.76 – €164.98 | 0.0% |
| +0.50% | fixed €80 | €179.93 | €157.17 – €203.40 | 0.0% |

**This is the *only* regime where 80% sizing shines** — and it is entirely
conditional on `µ_net` being genuinely, repeatably positive. At +0.5%/trade the
80% bot compounds €100 → median €211 over 200 trades; the 40% bot to €147. But
§2 shows we have **no evidence** this regime is real for any strategy in the lab,
and §1's over-betting result warns that even a *small* real edge can sit past
`2f*`, where 80% flips back to a loss. Sizing up is only rational **after** an
edge is demonstrated, and **calibrated to that edge**, not set at 80% by default.

### 3d. Volatility sensitivity (µ = 0)

Drag scales with σ². At the µ = 0 base case, the 80% bot's median-after-200 and
ruin-by-500 worsen sharply with per-trade vol:

| σ/trade | frac 80% median @200 | frac 80% ruin @500 | fixed €80 ruin @500 |
|---|---:|---:|---:|
| 2% | €97.47 | 0.0% | 2.5% |
| 3% | €94.43 | 0.8% | 12.8% |
| 5% | €85.07 | 14.8% | 35.5% |

Higher per-trade volatility (typical of the small, fast, leveraged instruments a
€100 account reaches for) makes the drag and ruin materially worse for the 80%
rule, and turns the fixed stake into a coin-flip on survival over long horizons.

---

## 4. The constructive alternative — answer "what would happen" with €0 at risk

There is already a lane designed to answer exactly the owner's question without
risking a euro: the **frozen paper lane**
([docs/paper-lane-protocol.md](../paper-lane-protocol.md)). It forward-tracks the
sole surviving candidate (AAPL-donchian 15/5) on **genuinely new bars**, in a
**git-committed mock ledger — no real money, no brokerage account, no order, no
API, ever** (protocol header). Its grading is pre-registered: a **weekly review
cadence** (protocol §6) grades every window that closed since the last pass; the
first re-armed weekly grading pass fires **2026-07-17** (recorded in
[control/status.md](../../control/status.md) via the prior ORDER 011 slice;
expected `FLAT` during the ~3-week warm-up).

**Recommendation:** gate **any** live-€ position-sizing experiment behind
(1) the paper lane accumulating real forward evidence of a positive net edge
first, and (2) the program's existing **go-live OWNER-ACTION gate**. The founding
methodology is **RESEARCH ONLY — "never connects to brokers, never executes
trades, never touches real money"; anything money-adjacent goes to ⚑
needs-owner** ([docs/founding-plan.md](../founding-plan.md)). The only place a
live allocation is even *described* is the sniper-bucket §8 six-field
OWNER-ACTION form, and it is explicit that its **pessimistic payback is zero —
"nothing in this program cleared significance, so the expected edge is
indistinguishable from noise and the realistic outcome is underperforming
buy-and-hold after costs"** ([docs/sniper-bucket.md](../sniper-bucket.md) §8).
Position sizing does not change that calculus; per §1 it only rescales it.

**Bottom line for the owner:** the sizing rule is a knob, not an engine. Point the
free paper lane at the question, watch it grade from 2026-07-17, and only bring
the go-live OWNER-ACTION into play if — and calibrated to how much — a real,
net-of-cost, statistically-supported edge actually shows up first.

---

*DEV-ONLY / ILLUSTRATIVE. No holdout read, no market-data import, no account, no
live/paper trade, no OOS/FINDING/PROMOTED claim. Reproduce:
`python3 scripts/position_sizing_mc.py --sigma-sensitivity`.*
