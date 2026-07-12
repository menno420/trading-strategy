# MTF Bollinger mean-reversion — a dev-only null

> **Status:** `reference` — **DEV-ONLY / ILLUSTRATIVE research note.**
> **Promotion is CLOSED (the holdout is SPENT).** This document reports a
> dev-window exploration of the owner's multi-timeframe (MTF) Bollinger
> mean-reversion idea. It reads market data ONLY through the holdout-safe rail
> (`trading_lab.data.load_ohlcv`, bars < 2025-01-09), fetches **no** new data,
> opens **no** account, places **no** live or paper trade, and writes **no**
> ledger row. It makes **no FINDING and no PROMOTED claim** — a positive t-stat
> would be at most a "RULE-PASS candidate (dev, promotion-closed)". Every
> number below is dev-only and illustrative.

## Verdict (plain language)

**The owner's MTF Bollinger mechanism does NOT hold on the cached data.** We
tested the mechanism *before* any strategy P&L, because if the conditional
probabilities don't separate, the strategy has no foundation. They don't
separate — and worse, **Test A runs opposite to the hypothesis**: a lower-timeframe
band break is *less* likely when the higher timeframe is stretched, not more.
**Test B shows no material or consistent regime split** (median reversion-success
difference, in-range minus stretched, is **−0.056** — the wrong sign — and the
"stretched" cells are tiny, N = 11–42). Then **all 12 pre-declared trading
configs are KILLED**: every out-of-sample Sharpe delta versus buy-and-hold is
negative, net of costs, uniformly across all three timeframe pairs. **Nothing
reached the ORDER 007 significance bar because nothing beat buy-and-hold.** This
is a clean null. The strategy has no conditioning foundation on this data.

## Data & scope honesty

- **Daily cache:** 9 tickers (AAPL, AMZN, BTC-USD, GLD, GOOGL, META, MSFT, NVDA,
  SLV), dev window 2010-01-04 → 2025-01-08.
- **Hourly cache:** 8 tickers (same minus BTC-USD), dev window ~2023-08-10 →
  2025-01-08 — only **~1.4 years (~2,400 bars/ticker)**. This is THIN; intraday
  conclusions are correspondingly weak.
- **No minute data exists in the cache.** So **15-minute / 45-minute MTF pairs
  are impossible on cached data.** Acquiring paid minute data is an **OWNER
  DECISION** — this session flags it and does **not** self-execute any fetch.
  The finest available bar is hourly; hourly can only be resampled *up*
  (2h/4h/6h) or paired with native daily/weekly.
- **Walk-forward thinness:** with standard windows (train 1008 / test 252),
  daily/weekly gives 10 splits and 1h/4h gives 5 splits (real walk-forward), but
  **2h/daily gives 0 standard splits** (the 2h series is only ~1,238 bars). It is
  reported as a **single OOS block** after a reduced train reservation — **not**
  walk-forward. Treat its two least-bad configs as noise, not signal.
- **Costs are ON** in every backtest (engine defaults: 5 bps slippage + 1 bp
  commission per side). No zero-cost runs.
- **Causality:** the higher timeframe is aligned to the lower timeline with a
  one-coarse-bar lag before a strictly-`<=` forward fill
  (`trading_lab.mtf.align_higher_to_lower`), which asserts at runtime that no
  fine bar ever uses a coarse value stamped at or after its own timestamp.

## Phase 1 — the conditioning study

Lower-TF band z-score `z_L` (lookback 20, k = 2); a **lower-band touch** is
`z_L ≤ −2`. Higher-TF band z-score `z_H` (lookback 20, k = 2), causally aligned.
**in-range** = `|z_H| < 2`; **stretched** = `|z_H| ≥ 2`.

### Test A — break likelihood: P(lower-band touch | higher-TF z_H bucket)

Pooled across the applicable universe. If the owner's claim held, P(touch) would
*rise* in the stretched (`|z_H| ≥ 2`) buckets. It does the opposite.

| pair | (−∞,−2] | (−2,−1] | (−1,0] | (0,1] | (1,2] | (2,∞) | in-range | stretched | Δ (st−in) |
|---|---|---|---|---|---|---|---|---|---|
| 1h/4h        | 0.030 | 0.077 | 0.077 | 0.050 | 0.034 | 0.008 | 0.0557 | 0.0169 | **−0.039** |
| 1h/6h        | 0.046 | 0.076 | 0.069 | 0.053 | 0.039 | 0.004 | 0.0558 | 0.0201 | **−0.036** |
| 2h/daily     | 0.076 | 0.060 | 0.074 | 0.063 | 0.030 | 0.000 | 0.0542 | 0.0229 | **−0.031** |
| daily/weekly | 0.025 | 0.057 | 0.057 | 0.046 | 0.049 | 0.012 | 0.0510 | 0.0147 | **−0.036** |

Touches concentrate in the *middle* buckets and are *rarest* in the stretched
outer buckets, consistently across all four pairs. **Test A refutes the
hypothesis.**

### Test B — reversion reliability: P(reversion success | regime)

Given a fresh lower-band touch, **success** = `z_L` returns to the mid-band
(`z_L ≥ 0`) within a 20-bar horizon *before* it falls to `z_L ≤ −3.5`. Reported
with N per cell, the per-bar forward return, and the per-ticker spread
(min / median / max).

| pair | success in-range (N) | success stretched (N) | Δ (in−st) | fwd/bar (in vs st) | per-ticker in-range (min/med/max) | per-ticker stretched (min/med/max) |
|---|---|---|---|---|---|---|
| 1h/4h        | 0.722 (454) | 0.762 (21) | **−0.039** | +0.00149 / +0.00090 | 0.627 / 0.722 / 0.814 | 0 / 1.0 / 1.0 |
| 1h/6h        | 0.721 (445) | 0.767 (30) | **−0.045** | +0.00147 / +0.00144 | 0.633 / 0.736 / 0.796 | 0 / 0.9 / 1.0 |
| 2h/daily     | 0.807 (280) | 0.909 (11) | **−0.102** | +0.00261 / +0.00299 | 0.588 / 0.847 / 0.944 | 0 / 1.0 / 1.0 |
| daily/weekly | 0.814 (738) | 0.881 (42) | **−0.067** | +0.00379 / +0.00554 | 0.643 / 0.840 / 0.949 | 0.4 / 1.0 / 1.0 |

Two things to read here. First, **base reversion is 72–81% in *every* regime** —
the wide `−3.5` stop plus a mid-band (`z_L ≥ 0`) target means most touches
eventually revert regardless of the higher timeframe, so there is little room for
a regime split to matter. Second, the split that does exist is both
**underpowered** (the stretched cells are N = 11–42, and the per-ticker stretched
spread swings from 0 to 1.0 — i.e. a handful of events per ticker) **and
wrong-signed** (stretched reverts *marginally better*, not worse). The owner's
tradeable claim is therefore both **unsupported** and **hard to even test** on
this data. Median success Δ (in−stretched) across pairs = **−0.056**.

**Conditioning verdict: NULL.** The conditional probabilities do not separate
materially or consistently; where they move at all, they move against the
hypothesis.

## Phase 2 — the pre-declared trading grid

Frozen rule: go long (+1) on a lower-TF lower-band touch (`z_L ≤ −k`) **only**
when the higher TF is in-range (`|z_H| < k`, causally aligned); exit to flat when
`z_L ≥ 0`; otherwise flat. No shorting. Costs ON, t+1-open execution. Pre-declared
grid (frozen): k ∈ {2, 2.5}; lookback ∈ {20, 50}; pairs ∈ {1h/4h, 2h/daily,
daily/weekly} = **12 configs**. OOS pooled across tickers per config.

| pair | k | lookback | trades | net exp/trade | win% | OOS Sharpe | B&H Sharpe | Δ Sharpe | worst trade | median win | splits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1h/4h        | 2.0 | 20 | 185 | 0.00455 | 66.5% | 0.675 | 1.057 | **−0.382** | −0.1489 | 0.0133 | 5 |
| 1h/4h        | 2.0 | 50 | 94  | 0.00814 | 72.3% | 0.653 | 1.057 | **−0.404** | −0.1188 | 0.0174 | 5 |
| 1h/4h        | 2.5 | 20 | 131 | 0.00581 | 67.9% | 0.730 | 1.057 | **−0.327** | −0.1489 | 0.0135 | 5 |
| 1h/4h        | 2.5 | 50 | 63  | 0.00946 | 71.4% | 0.593 | 1.057 | **−0.464** | −0.1188 | 0.0217 | 5 |
| 2h/daily     | 2.0 | 20 | 52  | 0.00594 | 71.2% | 0.618 | 1.257 | **−0.639** | −0.1118 | 0.0163 | 1* |
| 2h/daily     | 2.0 | 50 | 29  | 0.01772 | 72.4% | 1.168 | 1.257 | **−0.090** | −0.0213 | 0.0313 | 1* |
| 2h/daily     | 2.5 | 20 | 32  | 0.00554 | 68.8% | 0.446 | 1.257 | **−0.812** | −0.1118 | 0.0181 | 1* |
| 2h/daily     | 2.5 | 50 | 19  | 0.02022 | 78.9% | 1.043 | 1.257 | **−0.215** | −0.0086 | 0.0271 | 1* |
| daily/weekly | 2.0 | 20 | 374 | 0.01557 | 72.5% | 0.339 | 0.814 | **−0.475** | −0.3940 | 0.0337 | 10 |
| daily/weekly | 2.0 | 50 | 164 | 0.03377 | 76.8% | 0.345 | 0.814 | **−0.469** | −0.3655 | 0.0628 | 10 |
| daily/weekly | 2.5 | 20 | 204 | 0.02357 | 74.0% | 0.343 | 0.814 | **−0.471** | −0.3940 | 0.0382 | 10 |
| daily/weekly | 2.5 | 50 | 98  | 0.04282 | 79.6% | 0.307 | 0.814 | **−0.507** | −0.3655 | 0.0704 | 10 |

`*` 2h/daily has **0 standard walk-forward splits** (thin ~1,238-bar series);
these rows are a single OOS block, not walk-forward.

- **Tail-loss shape:** classic **many-small-wins / rare-big-loss**. Win rates are
  66–80% with positive per-trade expectancy, but the **worst trade dwarfs the
  median win** (e.g. daily/weekly worst −0.39 vs median win +0.03–0.07; 1h/4h
  worst −0.15 vs +0.013). Long-only, concentrated exposure with large
  regime-break losses ⇒ **every config loses to buy-and-hold on Sharpe**.
- **Cross-TF consistency:** Δ Sharpe is **negative for all 12 configs across all
  three pairs**. The effect degrades gracefully to *nothing* everywhere — there
  is **no lone-exotic-pair artifact**. The two 2h/daily lookback-50 configs come
  closest to B&H (Δ −0.09, −0.215) but are still negative on the thinnest sample
  (19–29 trades, 1 split) — noise, not edge.

## ORDER 007 (significance bar)

**No config was graded** — all 12 have Δ Sharpe ≤ 0 versus buy-and-hold net of
costs, so every one is **KILLED before the significance bar**. For transparency,
the ORDER 007 minimum t-stats that *would* apply (Lo-2002 SE, one-sided
Bonferroni `t_min = Φ⁻¹(1 − 0.05/K)`) are:

| K (variants) | context | `t_min` |
|---|---|---|
| 1   | single trial | 1.645 |
| 12  | this lane | 2.87 |
| 602 | program-wide burden (590 prior + 12) | 3.55 |

Nothing clears the *prerequisite* (beat B&H net of costs), so none is even
tested. Honest label for the whole lane: **KILLED (dev, promotion-closed)** —
zero RULE-PASS candidates.

## Denominator (multiple-testing burden)

| scope | count |
|---|---|
| this config | 1 |
| this lane (grid configs) | 12 |
| conditioning study | 4 descriptive TF-pair passes (descriptive, **not** selections) |
| program prior configs | 590 |
| **program cumulative configs** | **602** (590 + 12) |
| prior holdout reads (separate burden) | 13 |

## Conclusion

An honest null: on the cached dev window the MTF Bollinger conditioning does not
separate, Test A runs against the hypothesis, and every pre-declared config loses
to buy-and-hold net of costs. This is **dev-only** and **promotion-closed** — no
finding, no promoted claim, nothing armed. The reusable artifact is the causal
MTF helper (`src/trading_lab/mtf.py`, tested in `tests/test_mtf.py`).

If the owner still wants a *real* out-of-sample test, the honest path is the
**owner-gated preregistration draft**:
[../proposals/bollinger-mtf-preregistration-draft.md](../proposals/bollinger-mtf-preregistration-draft.md)
— a frozen protocol for a post-2026 minute-data run, **never self-executing**.
Given this dev-window null, the owner should weigh whether paid minute-data
acquisition is worth it before ordering that run.

### Reproduce

- Phase 1: `python3 scripts/mtf_conditioning_study.py`
  → `scratchpad/mtf_conditioning_results.json`
- Phase 2: `python3 scripts/mtf_bollinger_grid.py`
  → `scratchpad/mtf_grid_results.json`
- Helper + tests: `src/trading_lab/mtf.py`, `python3 -m pytest tests/test_mtf.py -q`
