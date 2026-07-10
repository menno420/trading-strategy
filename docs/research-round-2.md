# Research Round 2 — Pre-Registration

> **Status:** `binding` — pre-registered Round 2 protocol. Committed and merged
> before any Round 2 sweep, backtest, or outcome exists. Post-holdout,
> dev-only: promotion is closed (see banner below).

- **Status detail:** pre-registered (no sweeps run, no outcomes computed as of this commit)
- **Date:** 2026-07-10
- **Git context:** branched from `main` @ `c47f74d` ("control: status close-out — paper-lane foundation complete (#40-#43), lane opens 2026-07-11 (#45)")
- **Author:** agent lane, coordinator-directed

---

## POST-HOLDOUT, DEV-ONLY ROUND

> **The holdout (2025-01-09 → 2026-07-10) is SPENT** (13 holdout reads consumed by
> the P5 protocol). **Promotion is CLOSED for this round.** Nothing evaluated under
> this pre-registration can make out-of-sample claims, and no candidate from this
> round can advance past *dev-candidate* status. Genuine OOS validation of any
> Round 2 survivor requires a **NEW, owner-gated, pre-registered protocol on
> post-2026 data**. That is an **OWNER-ACTION**: agents may flag it as a proposal
> but must not schedule, initiate, or run it.

This document is committed and merged **before any Round 2 backtest, sweep, or
metric is computed**. Grids, instruments, budgets, metrics, and KEEP/KILL rules
below are binding. Any change requires a committed amendment to this file
**before** the affected runs execute.

## 1. Data contract

- All price data is loaded **only** via `trading_lab.data.load_ohlcv` on its
  **default rail**, which serves bars strictly **before 2025-01-09** (dev data).
- **Never** `unlock_holdout=True`. **Never** `load_paper_ohlcv`. **Never** ad-hoc
  reads of `data/**` (CSV/parquet/etc.).
- Source is the cached snapshot already in the repo. Cached instruments:
  - Daily: AAPL, AMZN, BTC-USD, GLD, GOOGL, META, MSFT, NVDA, SLV
  - Hourly: same minus BTC-USD (unused this round — all Round 2 lanes are daily)
- The paper lane (`experiments/paper/**`, `docs/paper-lane-protocol.md`) is a
  separate program and is **out of scope** for this round.

## 2. Prior program burden (denominators)

Cumulative configurations tested before this round: **590**

| Lane | Configs |
| --- | ---: |
| P1 trend-following daily | 177 |
| P1 video-derived strategy | 92 |
| P1 mean-reversion daily | 144 |
| P1 trend hourly | 177 |
| **Total prior** | **590** |

Plus **13 holdout reads** (holdout now spent). Every Round 2 result must carry
variants-tried denominators: this-config, this-lane cumulative, and
program-wide cumulative (including the prior 590).

Families already swept and therefore **burned** (verified against
`experiments/sweeps/*/*.json` `family` fields and `src/trading_lab/strategies/`):
`bollinger_reversion`, `donchian`, `ema_crossover`, `macd`, `macd_supertrend`,
`pullback`, `rsi_mean_reversion`, `sma_crossover`, `supertrend_flip`.
None of the three families below collides with that list; no substitution was
needed.

## 3. Candidate families (exactly 3, grids frozen here)

### 3a. `vol_filtered_trend` (daily)

SMA(fast, slow) crossover, long/flat, **gated by a realized-volatility regime
filter**: the long signal is valid only when 20-bar realized volatility is
**below** its trailing 252-bar median (calm-regime trend). The filter-off arm is
a plain-crossover control (mechanically equivalent to the burned
`sma_crossover` family) included **only** as a within-family baseline for the
filter's incremental effect — it is not a new claim surface.

- Grid: `fast ∈ {10, 20}`, `slow ∈ {50, 100, 200}` with `fast < slow`;
  `filter ∈ {on, off}` → **12 variants/instrument**
- Instruments: AAPL, MSFT, NVDA, GLD (4)
- **Configs: 48**

### 3b. `keltner_breakout` (daily)

Long when `close > EMA(n) + m · ATR(n)`; exit (flat) when `close < EMA(n)`.
Long/flat.

- Grid: `n ∈ {20, 50}`, `m ∈ {1.5, 2.0, 2.5}` → **6 variants/instrument**
- Instruments: BTC-USD, META, AMZN, SLV (4)
- **Configs: 24**

### 3c. `xsec_momentum` (daily, cross-sectional portfolio)

First portfolio-level lane. One strategy over **all 9 cached daily instruments**
as a single portfolio: rank instruments by trailing total return over lookback
`L`, hold the top-`k` equal-weight, rebalance every 21 bars. Per-side costs
(Section 5) are applied to **each rebalance trade**.

- Grid: `L ∈ {63, 126, 252}`, `k ∈ {2, 3}` → **6 configs**
- Benchmark: **equal-weight buy & hold of the 9-instrument basket**, same
  window, same costs.
- Walk-forward splits are applied on the **aligned common date index** across
  the 9 instruments.

## 4. Round variant budget

- Registered: 48 + 24 + 6 = **78 configs**
- **Hard cap: 100 configs.** The remaining 22 are contingency and are
  **unusable without a committed amendment to this document BEFORE running**
  any contingency config.
- New program-wide burden after this round: **≤ 690** (590 prior + ≤ 100).

## 5. Evaluation protocol

- **Walk-forward:** 1008-bar train / 252-bar test, as in prior lanes; roll
  forward and **report stitched OOS only**. For `xsec_momentum`, the identical
  split scheme is applied to the aligned common date index.
- **Costs:** 5 bps slippage + 1 bps commission **per side** (per rebalance
  trade for the portfolio lane).
- **Execution:** signal at bar `t` fills at bar `t+1` open. Long/flat (no
  shorting, no leverage).
- **Benchmark:** buy & hold of the same instrument, same window, same costs;
  for `xsec_momentum`, the equal-weight 9-instrument basket B&H, same costs.
- **Metrics:** net-of-costs stitched-OOS **Sharpe (primary)**, plus sortino,
  CAGR, max drawdown, total return, n_trades; benchmark same-window B&H
  reported alongside.

## 6. Pre-registered KEEP/KILL rule

Per family × instrument (and per `xsec_momentum` config):

> **KEEP as dev-candidate iff** stitched OOS Sharpe > benchmark OOS Sharpe
> **AND** stitched OOS Sharpe > 0. **Otherwise KILL.**

- Ties or any ambiguity (missing data, unstable splits, borderline equality)
  resolve **AGAINST the strategy** (KILL).
- No statistical-significance claims at this stage.
- KEEPs are **dev-candidates only**; promotion is closed (see banner). Any path
  beyond dev-candidate is an owner-gated proposal on post-2026 data.

## 7. Reporting

- Every reported number carries its variants-tried denominators: this config,
  lane cumulative, and program cumulative (including the prior 590).
- Negative results are reported with **equal prominence** to positive ones.
- Raw sweep outputs land in `experiments/sweeps/r2-<family>/` JSONs following
  the existing schema conventions (`family`, `variants_tried`,
  `lane_variants_tried`, `walk_forward{...}`, `costs`, per-variant rows), one
  file per `<family>__<TICKER>.json` (single portfolio file for
  `xsec_momentum`).
- Narrative results land in `docs/research-round-2-results.md`.
- A round summary is appended to `docs/final-report.md`, clearly marked
  **post-holdout dev-only**.

## 8. Execution plan (slices)

| Slice | Scope |
| --- | --- |
| R0 | This pre-registration, merged before any Round 2 number exists (this doc) |
| R1 | `vol_filtered_trend` sweep (48 configs) |
| R2 | `keltner_breakout` sweep (24 configs) |
| R3 | `xsec_momentum` sweep (6 configs) |
| R4 | Close-out: results doc, final-report append, KEEP/KILL ledger, budget reconciliation |

Slices R1–R3 must run within the frozen grids above. R4 makes no new runs.
