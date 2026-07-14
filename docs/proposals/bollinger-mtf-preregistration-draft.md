# MTF Bollinger mean-reversion — preregistration draft (OWNER-GATED)

> **Status:** `declined` — **CLOSED, bookkeeping-only (fleet pre-archive sweep,
> 2026-07-14).** Was a FROZEN PREREGISTRATION PROPOSAL (OWNER-GATED /
> FLAG-ONLY — never self-executing) for a *future* out-of-sample evaluation of
> the owner's MTF Bollinger idea. The dev-window study
> ([../research/bollinger-mtf-dev-2026-07-12.md](../research/bollinger-mtf-dev-2026-07-12.md))
> killed all 12 pre-declared configs (every OOS Sharpe delta vs buy-and-hold
> negative, net of costs) and found no conditioning separation (Test A opposite
> the hypothesis; Test B wrong-signed) — a clean null. No owner ORDER ever
> authorized the out-of-sample run this doc proposes. Declined per this doc's
> own §9 recommendation to weigh the null against acquisition cost; the frozen
> protocol below is preserved as reference in case the owner revisits it with
> genuinely new information, but it is not an active proposal. The badge token
> is `declined` because the doc taxonomy has no dedicated closed-proposal
> value; read it as closed/declined.

## 0. Why this is a draft, not a run

The dev-window study
([../research/bollinger-mtf-dev-2026-07-12.md](../research/bollinger-mtf-dev-2026-07-12.md))
found no conditioning separation (Test A opposite the hypothesis; Test B median
success Δ = −0.056, wrong sign) and killed all 12 pre-declared configs (every OOS
Sharpe delta vs buy-and-hold negative, net of costs). This document exists so
that IF the owner still wants a genuine out-of-sample test on data that did not
exist when these parameters were frozen, the protocol is fixed *in advance* and
the result cannot be p-hacked after the fact.

## 1. Hypothesis (stated precisely)

The owner's MTF Bollinger mean-reversion claim, in two testable parts:

- **H-A (break likelihood):** a lower-timeframe Bollinger band break
  (`z_L ≤ −k`) is MORE likely to occur when the higher timeframe is stretched
  beyond its own outer band (`|z_H| ≥ k`) than when it is in-range (`|z_H| < k`).
- **H-B (reversion reliability, the tradeable claim):** GIVEN a lower-band touch,
  reversion to the mid-band (`z_L ≥ 0`) is RELIABLE when the higher TF is in-range
  and FAILS when the higher TF is stretched.

The dev-window result was the opposite of H-A and a null for H-B; this protocol
re-tests both on fresh data.

## 2. Frozen grid

Exactly as pre-declared in the dev study (do NOT widen after seeing results):

- **k ∈ {2, 2.5}**
- **lookback ∈ {20, 50}** (same lookback for both timeframes)
- **TF pairs ∈ {1h/4h, 2h/daily, daily/weekly}** — 3 pairs
- ⇒ **12 configs.**

**Optional extension (SEPARATELY OWNER-GATED on data purchase):** the 15-minute /
45-minute pairs the owner originally imagined require minute-resolution data that
does **not** exist in the cache. Acquiring paid minute data is its own owner
decision; if and only if that data is purchased, the extension grid
`{15m/45m, 15m/1h, 45m/daily}` may be added — but that widens the denominator and
must be counted (see §8). It is NOT part of the core 12 and must not be run on
resampled proxies.

## 3. Frozen regime rule

Higher-TF Bollinger band position, causally aligned to the lower timeline:

- **in-range** = `|z_H| < k`; **stretched** = `|z_H| ≥ k`.
- Alignment uses `trading_lab.mtf.align_higher_to_lower`: the coarse series is
  lagged by **one coarse bar** before a strictly-`<=` forward fill, and the
  function asserts no fine bar uses a coarse value stamped at or after its own
  timestamp. Coarse bars are stamped at their **close** (`resample_ohlcv`,
  `closed='right', label='right'`).
- **Trading rule (frozen):** long (+1) on `z_L ≤ −k` **only** when in-range; exit
  to flat on `z_L ≥ 0`; otherwise flat. No shorting. t+1-open execution.

## 4. Significance bar (ORDER 007)

A config is eligible for a "RULE-PASS candidate" verdict ONLY if it **first beats
buy-and-hold net of costs** (Δ Sharpe > 0 over the same instrument/period), and
THEN clears the Lo-2002 t-stat bar:

- `SE(SR) = sqrt((1 + SR_per²/2) / N) · sqrt(PPY)`, `SR_per = SR_annual/sqrt(PPY)`
- `t = (SR_strategy − SR_benchmark) / SE`
- `t_min(K) = Φ⁻¹(1 − 0.05/K)`, one-sided, **Bonferroni over the FULL variants
  tried including the carried program burden** (§8). At K = 602, `t_min ≈ 3.55`.

Use `trading_lab.promotion.grade_promotion` for daily/hourly TFs; for resampled
intraday TFs the same formula applies with the resampled periods-per-year
(`trading_lab.mtf.periods_per_year`). **Promotion remains CLOSED** unless the
owner explicitly reopens it; absent that, the ceiling verdict is "RULE-PASS
candidate", never FINDING/PROMOTED.

## 5. Kill rule (pre-declared)

A config is **KILLED** if ANY of:

1. **Δ Sharpe ≤ 0** vs buy-and-hold net of costs (the prerequisite fails), OR
2. the **conditioning separation is absent** on the new data — pre-declared
   thresholds: **Test A** `P(touch|stretched) − P(touch|in-range) < +0.10`
   (i.e. H-A not materially confirmed in the claimed direction), OR **Test B**
   `success(in-range) − success(stretched) < +0.10` **with an adequately powered
   stretched cell (N ≥ 100 events)**. An underpowered stretched cell (N < 100) is
   itself a KILL for "cannot be tested", not a pass.

Both the mechanism (Test A/B thresholds) and the P&L (Δ Sharpe) must pass; a
config that trades profitably without the conditioning separation is an artifact
and is killed under rule 2.

## 6. Data, costs, and windows

- **Data:** fresh bars that did NOT exist when this grid was frozen. For the paper
  cadence, use only the dedicated forward rail
  (`trading_lab.data.load_paper_ohlcv`, bars ≥ `PAPER_LANE_START`); for a future
  historical OOS window, a NEW locked holdout must be defined and read exactly
  once. **The 2010–2025-01-08 dev window and the SPENT 2025 holdout are both
  off-limits** — they are consumed.
- **Costs ON:** 5 bps slippage + 1 bp commission per side (engine defaults). No
  zero-cost runs.
- **Walk-forward:** train 1008 / test 252, contiguous non-overlapping test
  windows. A TF pair that cannot fit ≥ 1 standard split on the available data
  (e.g. thin intraday) must be reported as thin and single-OOS, and its result
  treated as indicative only — not as a walk-forward pass.

## 7. Execution gate (binding)

This protocol is **FLAG-ONLY**. It executes ONLY when ALL hold:

1. an explicit **owner ORDER** in `control/inbox.md` authorizing the run;
2. a **fresh session** opened for it (no reuse of a session that has already seen
   any of the new data);
3. if minute data is involved, a **separate owner action** confirming the data
   purchase (§2 extension).

No agent may self-arm, self-execute, fetch, or trade under this draft. Absent the
gate, this file is documentation only.

## 8. Denominator accounting rule

Any run under this protocol **carries the existing program burden forward**: the
Bonferroni K is `602 (prior program cumulative) + (configs run in this protocol)`,
plus a separate count of holdout reads (currently 13). The 12 core configs, if
re-run on new data, do NOT reset the denominator — they add to it. The optional
minute-data extension adds its own configs to K and must be counted explicitly in
the run's report.

## 9. One-line owner note

On the current dev data this idea already returned a clean null; before ordering
an out-of-sample run (and especially before buying minute data for the 15m/45m
extension), weigh that null against the acquisition cost and the 602-config
multiple-testing burden any new positive result must overcome.
