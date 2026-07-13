# Research Round 3 — Backtest-Surface Expansion (Results)

> **Status:** `reference` — synthesis of the eight merged Round-3 night-run
> research slices (PRs #81–#88, 2026-07-13, ORDER 012). **POST-HOLDOUT,
> DEV-ONLY: the holdout is SPENT and promotion is CLOSED.** Nothing on this
> page is an out-of-sample claim; a KEEP means *dev-candidate only*. Genuine
> OOS validation of any survivor requires a new, owner-gated, pre-registered
> protocol on post-2026 data (owner action — not schedulable by agents).

**Headline: 1,752 registered configs across 8 slices in one night →
0 PROMOTED / 41 KEEP (dev-candidate only) / 125 KILL of 166 graded lanes.
The best t-stat anywhere is 1.04 against a Bonferroni bar of 2.64 — nothing
tonight is a finding, and that null is the deliverable.**

Unlike Round 2 there is no single pre-registration document for this round;
instead each slice committed its grids to `trading_lab.sweeps` (with tests)
*before* its sweep ran, and every lane's summary JSON records its
variants-tried denominators plus the ORDER 007 t-stat (informational only —
promotion is closed). Source of truth per claim below: the per-lane summary
JSONs under `experiments/sweeps/r3-*/`, the ledger rows in
`experiments/index.jsonl`, and the eight session cards in `.sessions/`
(`2026-07-13-r3-*.md`).

## Scope — what Round 3 added

- **11 new strategy families** (all long/flat, signal at bar t fills at bar
  t+1 open, registered in `trading_lab.strategies` with offline synthetic
  tests): `stochastic_reversion` + `williams_r_reversion` (PR #81),
  `roc_momentum` + `adx_filtered_sma` (PR #82, first Wilder ADX in the lab),
  `aroon_trend` + `cci_reversion` (PR #84), `bollinger_breakout` +
  `atr_trailing` (PR #86, first stateful trailing-stop exit),
  `xsec_reversal` (PR #87, portfolio mirror thesis), `trix_momentum` +
  `ichimoku_trend` (PR #88, first multi-component indicator system, with
  explicit no-lookahead tests for the displaced spans).
- **6 new daily instrument caches** — SPY, QQQ, TSLA, JPM, XOM, TLT
  (PR #83) — fetched only via the sanctioned `trading_lab.data.fetch_ohlcv`
  path (all six succeeded on the primary source, zero data-unavailable
  rows); `config.UNIVERSE` stays frozen at 8 tickers, the new instruments
  are declared lane-local in `trading_lab.sweeps`.
- **First hourly mean-reversion sweep** (PR #85): the four existing
  mean-reversion families re-swept on the committed hourly caches with zero
  new strategy code, on the `p1-trend-hourly` rail conventions.
- **Portfolio lane expanded** (PR #87): `xsec_momentum` re-run unchanged on
  the 14-instrument all-equity/ETF basket `XSEC-14` (frozen universe minus
  BTC-USD, plus the six PR #83 instruments), plus the new `xsec_reversal`
  mirror thesis.

## Budget ledger

| Slice | PR | Sweep | Families / axis | Registered configs | Graded lanes | Program cumulative |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 1 | #81 | `r3-stoch-willr` | stochastic_reversion, williams_r_reversion × 8 tickers × daily | 192 | 16 | 872 |
| 2 | #82 | `r3-roc-adx` | roc_momentum, adx_filtered_sma × 8 tickers × daily | 192 | 16 | 1,064 |
| 3 | #83 | `r3-new-tickers` | donchian, sma_crossover, rsi_mean_reversion × 6 NEW tickers × daily | 108 | 18 | 1,172 |
| 4 | #84 | `r3-aroon-cci` | aroon_trend, cci_reversion × 12-ticker mixed set × daily | 288 | 24 | 1,460 |
| 5 | #85 | `r3-meanrev-hourly` | 4 existing mean-reversion families × 8 tickers × HOURLY | 384 | 32 | 1,844 |
| 6 | #86 | `r3-breakout` | bollinger_breakout, atr_trailing × 12-ticker mixed set × daily | 288 | 24 | 2,132 |
| 7 | #87 | `r3-xsec-expanded` | xsec_momentum, xsec_reversal × XSEC-14 basket (portfolio; configs are grid points) | 12 | 12 | 2,144 |
| 8 | #88 | `r3-trix-ichimoku` | trix_momentum, ichimoku_trend × 12-ticker mixed set × daily | 288 | 24 | 2,432 |

**Round 3 total: 1,752 registered configs, 166 graded lanes** (154
single-instrument lanes + 12 portfolio configs). Program cumulative:
**2,432** variants tried (680 before tonight). Every lane runs the shared
rail: `load_ohlcv` default (dev bars only, `data_end ≤ 2025-01-08`,
asserted in-script), costs 5 bps slippage + 1 bp commission per side,
walk-forward 1008-bar train / 252-bar test, contiguous, stitched OOS vs
same-window same-cost buy & hold, Round-2 KEEP/KILL rule.

## Scoreboard

| Slice | PR | Verdicts (of graded lanes) | KEEP rate |
| --- | --- | --- | ---: |
| `r3-stoch-willr` | #81 | 0 PROMOTED / 2 KEEP-dev / 14 KILL of 16 | 13% |
| `r3-roc-adx` | #82 | 0 PROMOTED / 2 KEEP-dev / 14 KILL of 16 | 13% |
| `r3-new-tickers` | #83 | 0 PROMOTED / 5 KEEP-dev / 13 KILL of 18 | 28% |
| `r3-aroon-cci` | #84 | 0 PROMOTED / 4 KEEP-dev / 20 KILL of 24 | 17% |
| `r3-meanrev-hourly` | #85 | 0 PROMOTED / 13 KEEP-dev / 19 KILL of 32 | 41% |
| `r3-breakout` | #86 | 0 PROMOTED / 3 KEEP-dev / 21 KILL of 24 | 13% |
| `r3-xsec-expanded` | #87 | 0 PROMOTED / 6 KEEP-dev / 6 KILL of 12 | 50% |
| `r3-trix-ichimoku` | #88 | 0 PROMOTED / 6 KEEP-dev / 18 KILL of 24 | 25% |
| **Aggregate** | #81–#88 | **0 PROMOTED / 41 KEEP-dev / 125 KILL of 166** | **25%** |

## Every KEEP, against the bar

All 41 KEEPs, from the lane summary JSONs (`experiments/sweeps/<sweep>/`).
`t` is the ORDER 007 t-stat on the stitched-OOS Sharpe delta (Lo 2002 SE);
`bar` is the Bonferroni-adjusted minimum t for the lane's variant count
(K=12 → 2.64; K=6 → 2.39). **No KEEP comes within 1.6 of its bar** — every
one is inside noise, which is why none is a finding.

| Sweep (PR) | Family | Lane | OOS Sharpe | B&H Sharpe | t | bar |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| r3-stoch-willr (#81) | williams_r_reversion | GLD daily | 0.552 | 0.400 | 0.48 | 2.64 |
| r3-stoch-willr (#81) | williams_r_reversion | SLV daily | 0.500 | 0.170 | **1.04** | 2.64 |
| r3-roc-adx (#82) | roc_momentum | META daily | 0.734 | 0.653 | 0.23 | 2.64 |
| r3-roc-adx (#82) | adx_filtered_sma | META daily | 0.700 | 0.653 | 0.13 | 2.64 |
| r3-new-tickers (#83) | donchian | XOM daily | 0.322 | 0.294 | 0.09 | 2.39 |
| r3-new-tickers (#83) | donchian | TLT daily | 0.285 | 0.196 | 0.28 | 2.39 |
| r3-new-tickers (#83) | sma_crossover | XOM daily | 0.347 | 0.294 | 0.17 | 2.39 |
| r3-new-tickers (#83) | sma_crossover | TLT daily | 0.414 | 0.196 | 0.69 | 2.39 |
| r3-new-tickers (#83) | rsi_mean_reversion | JPM daily | 0.747 | 0.645 | 0.32 | 2.39 |
| r3-aroon-cci (#84) | aroon_trend | AAPL daily | 1.132 | 0.963 | 0.53 | 2.64 |
| r3-aroon-cci (#84) | aroon_trend | META daily | 0.880 | 0.653 | 0.64 | 2.64 |
| r3-aroon-cci (#84) | aroon_trend | TLT daily | 0.335 | 0.196 | 0.44 | 2.64 |
| r3-aroon-cci (#84) | cci_reversion | SLV daily | 0.297 | 0.170 | 0.40 | 2.64 |
| r3-meanrev-hourly (#85) | rsi_mean_reversion | AAPL hourly | 1.788 | 1.570 | 0.19 | 2.64 |
| r3-meanrev-hourly (#85) | rsi_mean_reversion | GOOGL hourly | 1.828 | 1.010 | 0.72 | 2.64 |
| r3-meanrev-hourly (#85) | rsi_mean_reversion | AMZN hourly | 1.188 | 0.615 | 0.50 | 2.64 |
| r3-meanrev-hourly (#85) | bollinger_reversion | MSFT hourly | 0.846 | 0.148 | 0.61 | 2.64 |
| r3-meanrev-hourly (#85) | bollinger_reversion | AMZN hourly | 0.875 | 0.615 | 0.23 | 2.64 |
| r3-meanrev-hourly (#85) | bollinger_reversion | META hourly | 0.625 | 0.494 | 0.11 | 2.64 |
| r3-meanrev-hourly (#85) | stochastic_reversion | AAPL hourly | 2.157 | 1.570 | 0.51 | 2.64 |
| r3-meanrev-hourly (#85) | stochastic_reversion | GOOGL hourly | 1.021 | 1.010 | 0.01 | 2.64 |
| r3-meanrev-hourly (#85) | stochastic_reversion | META hourly | 1.529 | 0.494 | 0.91 | 2.64 |
| r3-meanrev-hourly (#85) | williams_r_reversion | MSFT hourly | 0.249 | 0.148 | 0.09 | 2.64 |
| r3-meanrev-hourly (#85) | williams_r_reversion | AMZN hourly | 0.885 | 0.615 | 0.24 | 2.64 |
| r3-meanrev-hourly (#85) | williams_r_reversion | META hourly | 0.648 | 0.494 | 0.13 | 2.64 |
| r3-meanrev-hourly (#85) | williams_r_reversion | SLV hourly | 1.785 | 1.185 | 0.53 | 2.64 |
| r3-breakout (#86) | bollinger_breakout | AAPL daily | 1.045 | 0.963 | 0.26 | 2.64 |
| r3-breakout (#86) | bollinger_breakout | TSLA daily | 0.892 | 0.760 | 0.42 | 2.64 |
| r3-breakout (#86) | atr_trailing | META daily | 0.825 | 0.653 | 0.48 | 2.64 |
| r3-xsec-expanded (#87) | xsec_momentum | XSEC-14, L63/k2 | 1.265 | 1.193 | 0.20 | 2.39 |
| r3-xsec-expanded (#87) | xsec_momentum | XSEC-14, L63/k3 | 1.297 | 1.193 | 0.29 | 2.39 |
| r3-xsec-expanded (#87) | xsec_momentum | XSEC-14, L126/k2 | 1.425 | 1.193 | 0.65 | 2.39 |
| r3-xsec-expanded (#87) | xsec_momentum | XSEC-14, L126/k3 | 1.219 | 1.193 | 0.07 | 2.39 |
| r3-xsec-expanded (#87) | xsec_momentum | XSEC-14, L252/k2 | 1.409 | 1.193 | 0.61 | 2.39 |
| r3-xsec-expanded (#87) | xsec_momentum | XSEC-14, L252/k3 | 1.227 | 1.193 | 0.10 | 2.39 |
| r3-trix-ichimoku (#88) | trix_momentum | AAPL daily | 0.985 | 0.963 | 0.07 | 2.64 |
| r3-trix-ichimoku (#88) | trix_momentum | META daily | 0.672 | 0.653 | 0.05 | 2.64 |
| r3-trix-ichimoku (#88) | trix_momentum | SLV daily | 0.184 | 0.170 | 0.05 | 2.64 |
| r3-trix-ichimoku (#88) | trix_momentum | TLT daily | 0.239 | 0.196 | 0.14 | 2.64 |
| r3-trix-ichimoku (#88) | ichimoku_trend | META daily | 0.993 | 0.653 | 0.96 | 2.64 |
| r3-trix-ichimoku (#88) | ichimoku_trend | TLT daily | 0.203 | 0.196 | 0.02 | 2.64 |

## Cross-cutting patterns (each verified against the summary JSONs)

1. **KEEPs cluster where the benchmark itself is weak.** Of the 22 daily
   single-instrument KEEPs, 11 sit on the four weakest benchmarks — TLT
   (B&H OOS Sharpe 0.196, 5 KEEPs), SLV (0.170, 3), XOM (0.294, 2), GLD
   (0.400, 1) — and 6 more on META (0.653). A low bar cleared, not an edge:
   the pattern every slice card from #83 onward called out in advance of
   the next slice confirming it.
2. **META flatters most families.** A META lane KEEPs in 5 of the 6 slices
   that swept META as a single-instrument lane (#82, #84, #85, #86, #88 —
   only #81 resisted); across all 14 META lanes tonight the split is
   9 KEEP / 5 KILL, family-agnostically spanning reversion AND trend. This
   says more about META's dev-window path than about any strategy.
3. **The strongest benchmarks kill nearly everything.** NVDA (strongest
   daily benchmark, B&H OOS 1.295): 0 KEEP in 14 lanes (10 daily +
   4 hourly). MSFT daily (1.101): 0 in 10. SPY daily (0.761): 0 in 9. QQQ
   daily (0.871): 0 in 9. GLD hourly (2.056, the strongest benchmark
   anywhere): 0 in 4. The one counterexample is AAPL hourly (bench 1.570),
   which KEEPs twice — at t 0.19 and 0.51, i.e., noise.
4. **Hourly bars showed the round's highest single-instrument KEEP rate —
   on one regime.** 13/32 (41%) hourly reversion lanes KEEP vs 2/16 for
   the same two oscillator families on daily bars (#81 vs #85), but every
   hourly t ≤ 0.91 and the entire hourly OOS stitch is a single
   2024-03-07 → 2024-11-22 window (1,260 bars ≈ 8.5 months, one regime).
   "Reversion looks less bad intraday than daily" is the strongest claim
   the data supports.
5. **The cross-sectional momentum tilt is benchmark-hugging.**
   `xsec_momentum` on XSEC-14 goes 6/6 KEEP — but the margin is +0.03 to
   +0.23 Sharpe over an already-strong equal-weight benchmark (OOS 1.193),
   best t 0.65 vs a 2.39 bar, and weaker in t-stat terms than the same
   rule on XSEC-9 in Round 2. The mirror `xsec_reversal` goes 6/6 KILL
   (every config 0.28–0.68 Sharpe below benchmark): on this surface,
   ranking *direction* swings stitched OOS Sharpe by ~0.9 while parameters
   move it ≤ 0.2.

## What this round does NOT say

- **Nothing is promoted.** 0 PROMOTED across all 166 lanes; the ORDER 007
  significance bar was never approached (max t 1.04 vs 2.64/2.39, recorded
  informationally in every lane). 41 same-direction survivors out of 1,752
  tries is selection pressure, not evidence of an edge.
- **Promotion is owner-gated.** The holdout is SPENT and was untouched
  tonight (every lane `data_end ≤ 2025-01-08`, asserted in-script;
  `unlock_holdout` never passed). Any OOS test of any dev-candidate
  requires a new, owner-gated, pre-registered protocol on post-2026 data.
- **The paper lane is untouched** — `experiments/paper/ledger.md` is
  byte-identical to its pre-Round-3 state; the frozen paper protocol
  remains the only forward-looking track.
- **Dev-rail-only caveats** (the Round-2 caveats apply verbatim): all
  numbers come from one stitched walk-forward on one dev window; the
  single-instrument lanes use select-on-train stitching (per-split
  parameter selection), so each lane's number already embeds a selection
  step; the hourly lanes add the single-regime caveat above; the portfolio
  benchmark is a buy-once equal-weight basket whose composition drifts
  toward its own winners (flagged in the #87 card); and per-lane trade
  counts/exposure are not yet recorded, so a KEEP on few trades is
  indistinguishable from a KEEP on many (flagged in the #86 card).

## Reproducibility

Grids are committed in `src/trading_lab/sweeps.py` (declared before each
run, tested); per-lane summaries in `experiments/sweeps/<sweep>/`; ledger
rows + `experiments/index.jsonl` rebuilt via
`trading_lab.ledger.rebuild_index()`; per-slice narratives in
`.sessions/2026-07-13-r3-*.md`. One script per slice:

- `scripts/run_r3_stoch_willr_sweep.py` — slice 1 (#81): stochastic + Williams %R reversion × 8 tickers × daily.
- `scripts/run_r3_roc_adx_sweep.py` — slice 2 (#82): ROC momentum + ADX-filtered SMA × 8 tickers × daily.
- `scripts/run_r3_new_tickers.py` — slice 3 (#83): donchian / SMA-cross / RSI reversion × SPY QQQ TSLA JPM XOM TLT × daily (+ B&H baselines).
- `scripts/run_r3_aroon_cci_sweep.py` — slice 4 (#84): Aroon trend + CCI reversion × 12-ticker mixed set × daily.
- `scripts/run_r3_meanrev_hourly_sweep.py` — slice 5 (#85): 4 mean-reversion families × 8 tickers × hourly.
- `scripts/run_r3_breakout_sweep.py` — slice 6 (#86): Bollinger breakout + ATR trailing-stop × 12-ticker mixed set × daily.
- `scripts/run_r3_xsec_expanded.py` — slice 7 (#87): xsec momentum + reversal × XSEC-14 portfolio basket.
- `scripts/run_r3_trix_ichimoku_sweep.py` — slice 8 (#88): TRIX momentum + Ichimoku trend × 12-ticker mixed set × daily.
