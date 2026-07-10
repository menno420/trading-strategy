# Research Round 2 — Results

> **Status:** `reference` — outcomes of the pre-registered Round 2 protocol
> ([research-round-2.md](research-round-2.md), merged before any Round 2
> number existed). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and
> promotion is CLOSED.** Nothing on this page is an out-of-sample claim;
> a KEEP means *dev-candidate only*. Genuine OOS validation of any survivor
> requires a new, owner-gated, pre-registered protocol on post-2026 data
> (owner action — not schedulable by agents).

This page accumulates one section per slice (R1–R3) as each pre-registered
sweep lands. Grids, instruments, walk-forward scheme, costs, and the
KEEP/KILL rule are all frozen in the pre-registration; every number below
carries its variants-tried denominators. No statistical-significance claims
are made anywhere in this round.

## Round 2 budget ledger

| Slice | Family | Registered configs | Run | Lane cumulative (Round 2) | Program cumulative (incl. 590 prior) |
| --- | --- | ---: | ---: | ---: | ---: |
| R1 | `vol_filtered_trend` | 48 | 48 | 48 | 638 |

Hard cap: 100 Round 2 configs (78 registered + 22 contingency, contingency
untouchable without a committed pre-run amendment). Used so far: **48**.

---

## R1 — `vol_filtered_trend` × {AAPL, MSFT, NVDA, GLD} × daily

**Headline: 0 KEEP / 4 KILL. The volatility-filtered trend family failed on
every instrument — stitched walk-forward OOS Sharpe lost to same-window,
same-cost buy & hold on all four.** This negative result is the finding of
the slice.

- **Family (pre-reg §3a):** SMA(fast, slow) crossover, long/flat, long valid
  only when 20-bar realized vol is strictly below its trailing 252-bar
  median; `filter=off` arm = plain-crossover within-family baseline (not a
  new claim surface — mechanically the burned `sma_crossover`).
- **Grid (frozen):** `fast ∈ {10, 20}` × `slow ∈ {50, 100, 200}` ×
  `filter ∈ {on, off}` = 12 variants/instrument × 4 instruments =
  **48 configs**.
- **Protocol:** data via `load_ohlcv` default rail only (dev bars
  2010-01-04 → 2025-01-08; holdout ≥ 2025-01-09 excluded); walk-forward
  1008-bar train / 252-bar test, contiguous, stitched OOS only (10 splits,
  OOS window 2014-01-06 → 2024-01-09); costs 5 bps slippage + 1 bp
  commission per side; signal at bar t fills at bar t+1 open; benchmark =
  buy & hold of the same instrument over the exact stitched OOS window,
  same costs.
- **KEEP/KILL (pre-reg §6):** KEEP as dev-candidate iff stitched OOS Sharpe
  > benchmark OOS Sharpe AND > 0; ties/ambiguity resolve KILL.
- **Raw evidence:** `experiments/sweeps/r2-vol_filtered_trend/` +
  `experiments/index.jsonl` (one ledger run per instrument's top
  full-period variant, in-sample bookkeeping only).

### Verdicts (denominators: 12 variants this instrument / 48 this family / 48 Round-2 lane / 638 program)

| Instrument | Top full-period variant (in-sample, NOT a finding) | Stitched OOS Sharpe | B&H OOS Sharpe | OOS CAGR vs B&H | Verdict |
| --- | --- | ---: | ---: | --- | --- |
| AAPL | fast 10 / slow 200 / filter off (Sharpe 0.955) | **0.635** | 0.963 | 11.6% vs 26.9% | **KILL** |
| MSFT | fast 20 / slow 200 / filter off (Sharpe 0.867) | **1.015** | 1.101 | 20.9% vs 28.5% | **KILL** |
| NVDA | fast 10 / slow 200 / filter off (Sharpe 1.242) | **1.252** | 1.295 | 45.8% vs 64.0% | **KILL** |
| GLD | fast 20 / slow 50 / filter on (Sharpe 0.502) | **0.214** | 0.400 | 1.4% vs 4.7% | **KILL** |

Stated plainly: **AAPL KILL. MSFT KILL. NVDA KILL. GLD KILL.** No
dev-candidate emerges from this family.

### Honest read

- The calm-regime hypothesis did not add value where it was supposed to: on
  3 of 4 instruments the best full-period variant is the **filter-off** arm
  (the plain crossover), i.e. the registered mechanism *subtracted* in-sample
  Sharpe (NVDA best filter-on 0.880 vs filter-off 1.242; AAPL 0.926 vs
  0.955; MSFT 0.824 vs 0.867). Only GLD preferred the filter in-sample
  (0.502 vs 0.341) and it still lost OOS by the widest relative margin.
- Walk-forward selection chose the filter-on arm in only 15 of 40 splits
  (6 of GLD's 10, 3 of 10 elsewhere);
  even where chosen it did not rescue the OOS stitch.
- Max drawdown was the one partial bright spot (e.g. NVDA −36.5% vs B&H
  −67.2%), but drawdown is not the pre-registered decision metric and buys
  no KEEP.

### Ambiguity resolutions (all against the strategy, per §6)

1. **"Realized volatility" definition:** std of daily close-to-close simple
   returns over 20 bars (unannualized — annualization is monotonic and
   cannot change a comparison against the series' own median).
2. **Filter warm-up:** bars where the 20-bar vol or its 252-bar trailing
   median is not yet defined are treated as *not calm* → flat (calm cannot
   be confirmed).
3. **Ties (vol == median):** "below" is strict, so equality is not calm →
   flat.
4. Parameter is exposed as `vol_filter ∈ {True, False}` in code; identical
   to the registered `filter ∈ {on, off}` axis (naming only).

No deviation from the pre-registered grid, instruments, splits, costs, or
rule occurred; no contingency configs were used.

---

*R2 (`keltner_breakout`) and R3 (`xsec_momentum`) sections land here when
those slices run. R4 appends the round summary to
[final-report.md](final-report.md).*
