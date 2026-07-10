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
| R2 | `keltner_breakout` | 24 | 24 | 72 | 662 |

Hard cap: 100 Round 2 configs (78 registered + 22 contingency, contingency
untouchable without a committed pre-run amendment). Used so far: **72**.

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

## R2 — `keltner_breakout` × {BTC-USD, META, AMZN, SLV} × daily

**Headline: 2 KEEP / 2 KILL. The Keltner-channel breakout beat same-window,
same-cost buy & hold on stitched walk-forward OOS Sharpe for BTC-USD (1.348
vs 0.821) and META (0.747 vs 0.653), and lost on AMZN (0.500 vs 0.763) and
SLV (−0.042 vs 0.170).** Both KEEPs are **dev-candidates only** — the
holdout is spent, promotion is closed, and nothing here is an out-of-sample
claim. The two KILLs carry equal weight: the family is 2-for-4, not a
general win.

- **Family (pre-reg §3b):** long when `close > EMA(n) + m · ATR(n)`; exit
  (flat) when `close < EMA(n)`. Long/flat. Between the two triggers the
  position is held (the registration names only an entry and an exit).
- **Grid (frozen):** `n ∈ {20, 50}` × `m ∈ {1.5, 2.0, 2.5}` =
  6 variants/instrument × 4 instruments = **24 configs**.
- **Protocol:** data via `load_ohlcv` default rail only (holdout ≥
  2025-01-09 excluded; dev bars end 2025-01-08 — start varies by listing:
  AMZN/SLV 2010-01-04, META 2012-05-18, BTC-USD 2014-09-17); walk-forward
  1008-bar train / 252-bar test, contiguous, stitched OOS only (10 splits
  for BTC-USD/AMZN/SLV, 8 for META — shorter history); costs 5 bps
  slippage + 1 bp commission per side; signal at bar t fills at bar t+1
  open; benchmark = buy & hold of the same instrument over the exact
  stitched OOS window, same costs.
- **KEEP/KILL (pre-reg §6):** KEEP as dev-candidate iff stitched OOS Sharpe
  > benchmark OOS Sharpe AND > 0; ties/ambiguity resolve KILL.
- **Raw evidence:** `experiments/sweeps/r2-keltner_breakout/` +
  `experiments/index.jsonl` (one ledger run per instrument's top
  full-period variant, in-sample bookkeeping only).

### Verdicts (denominators: 6 variants this instrument / 24 this family / 72 Round-2 lane / 662 program)

| Instrument | Top full-period variant (in-sample, NOT a finding) | Stitched OOS Sharpe | B&H OOS Sharpe | OOS CAGR vs B&H | Verdict |
| --- | --- | ---: | ---: | --- | --- |
| BTC-USD | n 50 / m 1.5 (Sharpe 1.273) | **1.348** | 0.821 | 53.5% vs 36.7% | **KEEP (dev-candidate only)** |
| META | n 50 / m 1.5 (Sharpe 0.756) | **0.747** | 0.653 | 16.0% vs 19.4% | **KEEP (dev-candidate only)** |
| AMZN | n 50 / m 1.5 (Sharpe 0.599) | **0.500** | 0.763 | 8.2% vs 22.6% | **KILL** |
| SLV | n 20 / m 2.0 (Sharpe 0.314) | **−0.042** | 0.170 | −1.3% vs 1.0% | **KILL** |

Stated plainly: **AMZN KILL. SLV KILL.** AMZN's breakout underperformed
buy & hold OOS by a wide margin (Sharpe 0.500 vs 0.763, CAGR 8.2% vs
22.6%); SLV's stitched OOS Sharpe was outright negative. BTC-USD and META
KEEP as dev-candidates only — no promotion path exists this round.

### Honest read

- **BTC-USD is the strong case:** OOS Sharpe 1.348 vs 0.821 with higher
  CAGR (53.5% vs 36.7%) *and* less than half the drawdown (−39.3% vs
  −83.4%). Walk-forward selection was also stable — it chose `m = 1.5`
  in all 10 splits (n 20 in 6, n 50 in 4).
- **META is a marginal KEEP:** the Sharpe edge is 0.747 vs 0.653, but OOS
  CAGR actually *trails* buy & hold (16.0% vs 19.4%) — the edge is purely
  risk-adjusted (max drawdown −32.2% vs −76.4%). It passes the
  pre-registered rule as written; a raw-return investor would not have
  beaten B&H. Split selection was also less stable (three different
  params across 8 splits).
- The grid's in-sample preference was consistent — `n 50 / m 1.5` (the
  slowest channel, tightest multiplier) was the top full-period variant on
  3 of 4 instruments — but consistency did not decide outcomes: the same
  variant family KEEPs on BTC-USD/META and KILLs on AMZN/SLV.
- SLV never had a viable arm: the best full-period variant managed Sharpe
  0.314 in-sample and all n=50 variants were negative; the OOS stitch went
  to −0.042 (7 of 10 split test-Sharpes negative).
- The drawdown reduction is uniform across all four instruments (breakout
  is flat through crashes), but drawdown is not the pre-registered
  decision metric and buys no KEEP where Sharpe loses (AMZN, SLV).
- Denominator honesty: 2 KEEPs out of 24 configs in this family, 72
  Round-2 configs, 662 program-wide. Two same-direction survivors after
  662 tries is selection pressure, not evidence of an edge; only a new,
  owner-gated protocol on post-2026 data could test these dev-candidates
  out of sample.

### Ambiguity resolutions (all against the strategy, per §6)

1. **EMA convention:** recursive smoothing `ewm(span=n, adjust=False)` —
   the repo-wide EMA convention (same as `ema_crossover`, `macd`).
2. **ATR convention:** Wilder's ATR (`ewm(alpha=1/n, adjust=False)` over
   true range) via the shared `wilder_atr` helper — the repo's existing
   ATR (same as the SuperTrend lanes).
3. **Between the triggers** (`EMA ≤ close ≤ EMA + m·ATR`): position held
   unchanged — the registration names only an entry and an exit; no
   graded/partial positions are invented.
4. **Warm-up:** the first `n` bars are forced flat and cannot trigger an
   entry — a breakout cannot be confirmed before the indicators have seen
   a full window (flat = against the strategy).
5. **Ties:** entry requires strict `>` — `close == EMA + m·ATR` is not a
   breakout (flat, against the strategy). The exit's strict `<` is the
   registered rule verbatim (equality holds the position; that is the
   letter of §3b, not a discretionary resolution).

No deviation from the pre-registered grid, instruments, splits, costs, or
rule occurred; no contingency configs were used.

---

*R3 (`xsec_momentum`) section lands here when that slice runs. R4 appends
the round summary to [final-report.md](final-report.md).*
