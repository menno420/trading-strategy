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
| R3 | `xsec_momentum` | 6 | 6 | 78 | 668 |

Hard cap: 100 Round 2 configs (78 registered + 22 contingency, contingency
untouchable without a committed pre-run amendment). Used so far: **78**
(all registered configs run; contingency untouched).

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

## R3 — `xsec_momentum` × 9-instrument basket × daily (portfolio lane)

**Headline: 3 KEEP / 3 KILL. The cross-sectional momentum portfolio beat
the equal-weight-basket buy & hold on stitched walk-forward OOS Sharpe for
L=63/k=2 (1.627 vs 1.147), L=63/k=3 (1.631 vs 1.147) and L=252/k=3 (1.277
vs 1.147), and lost for L=126/k=2 (0.953), L=126/k=3 (1.136) and L=252/k=2
(1.050).** All three KEEPs are **dev-candidates only** — the holdout is
spent, promotion is closed, and nothing here is an out-of-sample claim.
The three KILLs carry equal weight: the family is 3-for-6, and the middle
lookback (126) failed on both arms.

- **Family (pre-reg §3c):** first PORTFOLIO-level lane. One strategy over
  all 9 cached daily instruments (AAPL, AMZN, BTC-USD, GLD, GOOGL, META,
  MSFT, NVDA, SLV) as a single portfolio: rank by trailing total return
  over lookback `L`, hold the top-`k` equal-weight (long-only, no
  leverage), rebalance every 21 bars; weights drift with prices between
  rebalances. Per-side costs are charged on every rebalance trade.
- **Grid (frozen):** `L ∈ {63, 126, 252}` × `k ∈ {2, 3}` = **6 configs**
  (portfolio lane: configs are grid points, NOT × instruments; the 21-bar
  rebalance interval is frozen and not swept).
- **Protocol:** data via `load_ohlcv` default rail only (holdout ≥
  2025-01-09 excluded); instruments aligned on their common date index
  (2,595 bars, 2014-09-17 → 2025-01-08 — the start is BTC-USD's listing);
  walk-forward 1008-bar train / 252-bar test, contiguous, stitched OOS
  only (6 splits, OOS window 2018-09-18 → 2024-09-20, 1,512 bars); costs
  5 bps slippage + 1 bp commission per side per rebalance trade; decision
  at bar t fills at bar t+1 open; benchmark = equal-weight buy & hold of
  the 9-instrument basket over the exact stitched OOS window, same costs
  (OOS Sharpe 1.147, CAGR 32.3%).
- **Per-config evaluation:** each config is one fixed portfolio rule —
  there is no per-split parameter fitting — so its stitched OOS number is
  the rule evaluated on the identical split scheme's test windows, and §6
  verdicts are per config as registered. A select-on-train stitch over
  the 6-config grid (the prior lanes' machinery) is reported as
  bookkeeping only below.
- **KEEP/KILL (pre-reg §6):** KEEP as dev-candidate iff stitched OOS
  Sharpe > benchmark OOS Sharpe AND > 0; ties/ambiguity resolve KILL.
- **Raw evidence:** `experiments/sweeps/r2-xsec_momentum/xsec_momentum__XSEC-9.json`
  + `experiments/index.jsonl` (one ledger run for the top full-period
  config, instrument `XSEC-9`, in-sample bookkeeping only).

### Verdicts (denominators: 6 configs this family / 78 Round-2 lane / 668 program)

Benchmark for every row: equal-weight 9-instrument basket B&H over the
same stitched OOS window, same costs — **OOS Sharpe 1.147**, CAGR 32.3%,
max drawdown −50.4%.

| Config | Stitched OOS Sharpe | B&H basket OOS Sharpe | OOS CAGR vs B&H | OOS max DD vs B&H | Verdict |
| --- | ---: | ---: | --- | --- | --- |
| L=63, k=2 | **1.627** | 1.147 | 69.6% vs 32.3% | −52.9% vs −50.4% | **KEEP (dev-candidate only)** |
| L=63, k=3 | **1.631** | 1.147 | 58.3% vs 32.3% | −47.7% vs −50.4% | **KEEP (dev-candidate only)** |
| L=126, k=2 | **0.953** | 1.147 | 35.1% vs 32.3% | −57.3% vs −50.4% | **KILL** |
| L=126, k=3 | **1.136** | 1.147 | 37.2% vs 32.3% | −44.2% vs −50.4% | **KILL** |
| L=252, k=2 | **1.050** | 1.147 | 41.6% vs 32.3% | −55.6% vs −50.4% | **KILL** |
| L=252, k=3 | **1.277** | 1.147 | 45.9% vs 32.3% | −47.0% vs −50.4% | **KEEP (dev-candidate only)** |

Stated plainly: **L=126/k=2 KILL. L=126/k=3 KILL. L=252/k=2 KILL.** The
126-bar lookback lost to the basket on Sharpe with both k values, and
L=252/k=2 lost too; L=126/k=3 (1.136 vs 1.147) is a near-tie that the
pre-registered rule resolves against the strategy. L=63/k=2, L=63/k=3 and
L=252/k=3 KEEP as dev-candidates only — no promotion path exists this
round.

### Honest read

- **The benchmark was hard to beat and beating it is not evidence of an
  edge.** The equal-weight basket (a third of it mega-cap tech plus
  BTC-USD) did 32.3% CAGR at Sharpe 1.147 over this OOS window; three
  same-direction survivors out of 6 configs — after 668 program-wide
  tries — is selection pressure until a new, owner-gated protocol on
  post-2026 data says otherwise.
- **The shortest lookback is the strongest arm:** both L=63 configs
  cleared the bar by ~0.48 Sharpe with the highest OOS CAGRs (69.6% and
  58.3%). The KEEPs' edge is concentration in whatever was already
  running (mostly NVDA/BTC-heavy sleeves), not drawdown protection: max
  drawdowns (−47.7% to −52.9%) are basket-like, and L=63/k=2's is
  *worse* than B&H's.
- **Every config lost money in the 2021-09 → 2022-09 test window** (split
  4 test Sharpe −0.24 to −0.88): a long-only momentum basket held risk
  assets through the 2022 bear market and the 21-bar rebalance did not
  rotate it to safety. The 2020-09 → 2021-09 and 2023-09 → 2024-09
  windows carry most of the KEEPs' edge.
- **The select-on-train stitch (bookkeeping only, no verdict): OOS Sharpe
  1.264** — it picked L=63/k=3 in 3 of 6 splits but wasted two early
  splits on longer lookbacks, landing below both always-L=63 arms. Had
  "walk-forward selection" been the claim surface, the family would still
  have beaten the basket, more weakly.
- Full-period in-sample rows agree in direction (top config L=63/k=2 at
  Sharpe 1.777 vs basket 1.288) — bookkeeping, not findings.
- Costs were not the binding constraint: turnover is 3.2–8.4 book-units
  per year, i.e. ≈ 0.2–0.5%/year of cost drag at 6 bps per side (≈ 0.01
  Sharpe at this book's ~30% vol). That cannot explain the L=63 wins or
  the L=126/k=2 and L=252/k=2 losses; it is the same order as the
  L=126/k=3 near-tie (1.136 vs 1.147), which the pre-registered rule
  resolves against the strategy regardless.

### Ambiguity resolutions (per §6; recorded here, resolved against the strategy where a side existed)

1. **Aligned common date index:** intersection of the 9 instruments'
   dev-rail date indexes — BTC-USD bars on days any equity market is
   closed (weekends/holidays) are dropped, and the index starts at
   BTC-USD's 2014-09-17 listing (the shortest history truncates all).
   Lookback `L` and the 21-bar rebalance count **aligned bars**, not
   calendar days.
2. **Warm-up:** the first decision bar is the first aligned bar with a
   full `L`-bar lookback for every instrument; the portfolio sits in cash
   (0%) until that decision's t+1-open fill — a ranking cannot be
   confirmed before the lookback exists (flat = against the strategy).
3. **Rebalance schedule:** anchored at that first valid decision bar and
   strictly every 21 bars after it; frozen, not swept. (On this index the
   schedule happens to land exactly on every test-window start, so no OOS
   window waits for its first decision.)
4. **Drift between rebalances:** holdings are fixed in units between
   fills (weights drift with prices; equal weight is restored only at
   rebalance fills). The benchmark is the same book: one equal-weight
   purchase at bar 1's open, never rebalanced, same per-side costs. As in
   the single-instrument engine, costs reduce bar returns but not the
   drifted weights (second-order at 6 bps/side).
5. **Ranking ties** (equal trailing return): broken deterministically by
   alphabetical ticker order — arbitration on a measure-zero event, not a
   favorability choice.
6. **Per-config walk-forward:** a fixed rule has nothing to fit per
   split, so the §6 per-config verdict uses the fixed rule's stitched OOS
   under the identical split scheme; the select-on-train variant is
   bookkeeping only (see Honest read) and creates no new configs.
7. **Stitching resets:** the book restarts flat at each test window and
   pays full re-entry costs there (6 windows), exactly like prior lanes'
   stitching — against the strategy. The 75 aligned bars after the last
   complete test window (2024-09-23 → 2025-01-08) are unused by the
   stitch, as in prior lanes.
8. **`win_rate`** is reported as null for the portfolio lane: the
   single-book episode definition does not apply to a cross-sectional
   book. Every other schema field carries over.

No deviation from the pre-registered grid, instruments, splits, costs, or
rule occurred; no contingency configs were used.

---

*R1–R3 complete: all 78 registered Round 2 configs have run. R4 appends
the round summary to [final-report.md](final-report.md).*
