# trading-lab final report — ranked, honestly-validated (pre-holdout skeleton)

> **Status:** `reference` — the P5 ranked final report, written 2026-07-10
> (lane `p5-prep`, QUEUE item 8 prep). Every pre-holdout section below is
> complete and final; §Holdout is deliberately EMPTY pending the
> owner-gated one-shot evaluation defined in
> [p5-holdout-protocol.md](p5-holdout-protocol.md). Nothing runs against
> the holdout until that gate; this document does not unlock anything.

## What this lab tested, in one paragraph

Across four P1 sweep lanes (trend-following daily, video-strategy daily,
mean-reversion daily, trend-following hourly) the lab evaluated **590
strategy configurations** (177 + 92 + 144 + 177) over 8–9 instruments,
walk-forward with realistic costs, against buy-and-hold of the same
instrument over the same window. P2 re-validated the 14 surviving
candidates on out-of-selection data with frozen parameters; P4 ran the
13 non-killed subjects on every other instrument in their timeframe (99
transfer backtests). **The headline of this program is negative:** after
honest testing, exactly one candidate earned a "finding" label
pre-holdout — it then failed cross-instrument transfer 1/8, and on
2026-07-10 it was **re-graded to candidate** under the ORDER 007
promotion-significance bar (its +0.079 Sharpe edge is 0.42 standard
errors — inside noise; [re-grade
entry](p2-regrade-aapl-donchian.md)). **No candidate currently holds a
finding label.** The holdout read (§Holdout) is the last word and has
not happened yet.

## Methodology summary

Binding methodology: [founding-plan.md](founding-plan.md). As practiced
in every ledgered run:

- **Walk-forward evaluation** — parameters fit on a training window
  (1008 bars), scored on the following unseen window (252 bars), rolled
  through history; only stitched out-of-sample series are reported. No
  single-split in-sample number is ever a result.
- **Realistic costs, no lookahead** — 5 bps slippage + 1 bps commission
  per side on every fill; signals computed on bar *t* execute at bar
  *t+1*'s open. All strategies long/flat, no leverage.
- **Buy-and-hold benchmark** — every result is compared to B&H of the
  same instrument over the *exact same* window, same costs. Not beating
  holding is a negative result, and negative results are deliverables.
- **Multiple-testing discipline** — every result carries its
  variants-tried denominator (the "Burden" column below); survivors were
  required to validate out-of-selection (P2) and transfer to instruments
  they were not tuned on (P4). Since ORDER 007 (2026-07-10), promotion to
  FINDING additionally requires clearing an explicit significance bar
  (minimum t-stat on the Sharpe delta vs B&H, Lo 2002 SE,
  Bonferroni-adjusted for variants tried — `trading_lab.promotion`,
  the founding plan's deflated-Sharpe preference made explicit).
- **Holdout discipline** — every bar dated ≥ 2025-01-09
  (`HOLDOUT_START`, loader- and ledger-enforced:
  [holdout-enforcement.md](holdout-enforcement.md)) has remained sealed
  through P0–P4 and remains sealed as of this skeleton. Every ledger row
  to date has `data_end ≤ 2025-01-08` and no `holdout_unlocked` marker
  (CI-audited on every run).

Source result docs: [p1-trend-following-results.md](p1-trend-following-results.md) ·
[p1-video-strategy-results.md](p1-video-strategy-results.md) ·
[p1-mean-reversion-results.md](p1-mean-reversion-results.md) ·
[p1-trend-hourly-results.md](p1-trend-hourly-results.md) ·
[p2-validation-results.md](p2-validation-results.md) ·
[p4-transfer-results.md](p4-transfer-results.md).

## Ranked table — all candidates, by pre-holdout OOS evidence

Ranking rule (descriptive, not a promotion): Tier 1 = P2 RULE-PASS
(out-of-selection beat of B&H, below the significance bar — the sole P2
promotion was demoted to this label 2026-07-10, [re-grade
entry](p2-regrade-aapl-donchian.md)); Tier 2 = P2
UNVALIDATABLE-PRE-HOLDOUT candidates,
ordered by P1 walk-forward OOS Sharpe margin over B&H (a noisy,
selection-biased statistic — the caveat column is part of the row);
Tier 3 = killed / negative-complete. "Burden" = configurations tried in
the lane that nominated the row (per-split re-selection on top, as
documented in each P1 doc). "P4" = transfer instruments beaten / tried.

| Rank | Candidate (family × ticker × tf) | P1 OOS Sharpe vs B&H | Burden | P2 verdict | P4 | Caveats |
|---|---|---|---|---|---|---|
| **1** | **donchian × AAPL × daily** (entry=15, exit=5) | **1.18 vs 0.96** | 177 | **RULE-PASS / candidate** (0.619 vs 0.540, 1980→2009; was PROMOTED-TO-FINDING, [demoted 2026-07-10](p2-regrade-aapl-donchian.md): t = 0.42 < 1.64) | 1/8 FAILED | sole out-of-selection B&H beat, but the edge is 0.42 SE — inside noise; drawdown-shaped (MDD −21% vs −37% OOS; −64% vs −82% at P2); transfer failure sharpens the prior against it |
| 2 | macd × META × hourly (5/26/5) | 1.40 vs 0.49 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 0/7 FAILED | P1-flagged least trustworthy: fastest grid corner, ~210 changes/yr, per-split Sharpe swings +3.8 → −1.1, single-regime OOS |
| 3 | macd_supertrend × BTC-USD × daily | 1.20 vs 0.82 | 92 | UNVALIDATABLE-PRE-HOLDOUT | 0/8 FAILED | Sortino *below* B&H (0.70 vs 0.85); two OOS test years never traded; bubble-instrument trend filter |
| 4 | donchian × AMZN × hourly (40/40) | 0.91 vs 0.61 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/7 FAILED | single-regime ~8.5-month OOS; shares frozen vector with rank 6 — not independent evidence |
| 5 | supertrend_flip × BTC-USD × daily | 1.11 vs 0.82 | 92 | UNVALIDATABLE-PRE-HOLDOUT | 1/8 FAILED | drawdown reduction (−53% vs −83%), not out-trading; 0/4 untuned spot checks off-BTC |
| 6 | sma_crossover × META × daily (15/75) | 0.93 vs 0.65 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/8 FAILED | edge concentrated in sidestepping META's 2022 −76% drawdown |
| 7 | sma_crossover × GOOGL × hourly (10/75) | 1.25 vs 1.01 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 1/7 FAILED | thin margin, single-regime OOS |
| 8 | ema_crossover × META × daily (25/50) | 0.83 vs 0.65 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 1/8 FAILED | same 2022-drawdown profile as rank 6 |
| 9 | donchian × META × daily (55/55) | 0.80 vs 0.65 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/8 FAILED | same profile |
| 10 | rsi_mean_reversion × META × daily (2/10/50) | 0.79 vs 0.65 | 144 | UNVALIDATABLE-PRE-HOLDOUT | 0/8 FAILED | drawdown-shaped (MDD −35% vs −76%) |
| 11 | ema_crossover × GOOGL × hourly (20/50) | 1.06 vs 1.01 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 1/7 FAILED | margin inside noise |
| 12 | donchian × GOOGL × hourly (40/40) | 1.05 vs 1.01 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/7 FAILED | margin inside noise; vector shared with rank 4 |
| 13 | pullback × META × daily (7/7/100) | 0.67 vs 0.65 | 144 | UNVALIDATABLE-PRE-HOLDOUT | 0/8 FAILED | 0.02 Sharpe margin — flagged at P1 as unlikely to survive validation |
| — | pullback × GOOGL × daily (5/7/0) | 0.85 vs 0.72 | 144 | **KILLED** (0.256 vs 1.054 on 2004→2009) | excluded | dead; does not run at P5 |
| — | dual-EMA video control × BTC-USD (400/45 region) | 0.88 vs 0.82 | 92 (control: 20) | negative-complete at P1 | — | the video's one fully-stated artifact; weakest of its three interpretations |

Frozen parameters for ranks 1–13 are pre-registered verbatim (with
source JSONs) in [p5-holdout-protocol.md](p5-holdout-protocol.md) §2.

## The lead candidate (no longer a finding) — AAPL donchian 15/5, daily

The only candidate to survive out-of-selection validation
([p2-validation-results.md](p2-validation-results.md)). Its P2
PROMOTED-TO-FINDING verdict was **demoted to RULE-PASS / candidate on
2026-07-10** under the ORDER 007 promotion-significance bar: the +0.079
Sharpe edge over 7,331 bars has a Lo (2002) SE of 0.185, t = 0.42 —
far below the 1.64 minimum even at the most lenient variants-tried
denominator (full computation:
[p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md)):

| | Strategy | Buy-and-hold |
|---|---|---|
| P1 walk-forward OOS (2014→2024) Sharpe | **1.18** | 0.96 |
| P1 OOS CAGR / MDD | +21.5% / −21.3% | +26.9% / −37.4% |
| P2 frozen-param window (1980-12-12 → 2009-12-31, 7,331 bars) Sharpe | **0.619** | 0.540 |
| P2 CAGR / MDD | 14.2% / −63.9% | 15.6% / −81.8% |
| P2 total return / n_trades | 46.7× / 327 | 66.4× / 1 |

Honest characterization, as ledgered: a **modest, drawdown-shaped,
instrument-specific, statistically insignificant** result. In both
windows it earns its Sharpe edge by losing less in crashes, not by
out-returning holding (its CAGR trails B&H in both). At P4 it
transferred to 1 of 8 other instruments; under the significance bar its
P2 edge is 0.42 standard errors. A −64% drawdown and a +0.08 Sharpe
edge over three decades is a candidate, not a finding and not a system.
Its one-shot holdout read (the pre-registered PRIMARY) is the final
word.

## P4 cross-instrument transfer — 13/13 FAILED (first-class result)

Full detail: [p4-transfer-results.md](p4-transfer-results.md). All 13
subjects run with params frozen verbatim on every other same-timeframe
committed instrument (99 backtests, 0 new variants), full pre-holdout
windows, vs B&H, pre-registered ≥2/3 / ≥1/3 verdict rule: **0 subjects
TRANSFER-SUPPORTED, 0 TRANSFER-WEAK, 13 TRANSFER-FAILED.** Only 13 of 99
subject×instrument pairs beat B&H on Sharpe (13%); the best subject
managed 2/8. The scattered wins cluster where a long-only trend filter
mechanically helps (BTC-USD daily's −83% class drawdown; the NVDA/AMZN
hourly momentum regime) — instrument-regime effects, not portable edge.
This is the expected shape if the P1/P2 candidates are largely selection
artifacts riding instrument-specific regimes.

## Negative results — the program's main output

- **Trend-following × daily** (177 configs × 8 tickers,
  [doc](p1-trend-following-results.md)): 7/32 family×ticker lanes beat
  B&H OOS. On daily bars in a decade-long tech bull market, long/flat
  trend-following mostly lags holding after costs — MSFT, NVDA, GOOGL,
  AMZN, GLD: 0 of 20 lanes beat. MACD was the worst family on 5 of 8
  tickers (churn × costs). Where trend earned anything, it was drawdown
  reduction (META 2022, AAPL), not return enhancement.
- **Video-strategy × BTC-USD × daily** (92 configs,
  [doc](p1-video-strategy-results.md)): the DaviddTech video's headline
  (+500% / PF 2.295) is **not reproducible as stated** — it is an
  in-sample optimized backtest with unstated parameters. Its one fully
  stated artifact (dual-EMA 400/45) was the weakest of the three
  faithful interpretations (0.88 vs B&H 0.82 — inside noise at this
  burden): **negative-complete**. The two stronger interpretations beat
  B&H Sharpe only via drawdown reduction in a bubble-bust decade, rank
  *below* B&H on Sortino or trail on CAGR, and 0/4 untuned off-BTC spot
  checks beat holding.
- **Mean-reversion × daily** (144 configs × 8 tickers,
  [doc](p1-mean-reversion-results.md)): 3/24 lanes beat B&H OOS; 21
  lose. The whole Bollinger sub-family went **0 for 8**. Pullback was
  negative outright on both metals (GLD −0.15, SLV −0.13). A long/flat
  reverter misses the decade's up-drift and pays 6 bps/side for the
  privilege.
- **Trend-following × hourly** (177 configs × 8 tickers,
  [doc](p1-trend-hourly-results.md)): 5/32 lanes beat B&H over a single
  ~8.5-month OOS regime — 27 lose, including all four families on AAPL,
  MSFT, NVDA, GLD and SLV. Costs bite hardest here: MACD churns 80–210
  changes/yr and goes negative outright on 6 of 8 tickers. All hourly
  conclusions are single-regime provisional.
- **P2 structural exhaustion** ([doc](p2-validation-results.md)): 12 of
  14 candidates were UNVALIDATABLE-PRE-HOLDOUT — P1's walk-forward
  consumed every available pre-holdout bar in their home
  instrument×timeframe (META from its 2012 IPO, BTC-USD from 2014
  inception, hourly from Yahoo's 2023-08 floor). Unvalidatable ≠
  validated; they remain candidates only, and the sealed holdout is the
  only data left that can test them.
- **P2 kill:** GOOGL-pullback's frozen params captured 19.6% total
  return against a 513% B&H run-up (2004→2009) — decisively dead.

## Holdout results (P5 — pending unlock)

**EMPTY BY DESIGN — nothing has run against the holdout.** Every bar
dated ≥ 2025-01-09 remains sealed; no `holdout_unlocked` marker exists
in any ledger row as of this writing (CI-audited). The one-shot
evaluation — 13 pre-registered subjects, frozen params, pre-registered
verdict rules — is fully specified in
[p5-holdout-protocol.md](p5-holdout-protocol.md) and runs **only after
an explicit owner-gated unlock** (⚑ in control/status.md). When it has
run, this section receives: the PRIMARY verdict (CONFIRMED/REFUTED for
AAPL-donchian), the 12 secondary verdicts with the `k of 12` aggregate
line and full denominators, per-subject B&H comparisons over the same
window, and ledger-row citations. One shot; the report is then final.

## Evidence index

- Ledger: `experiments/index.jsonl` + `experiments/runs/*.json`
  (per-run, CI-audited for holdout boundary compliance).
- Sweep evidence: `experiments/sweeps/p1-*/*.json` (per-variant rows,
  `top_full_period_variant` frozen-param sources),
  `experiments/sweeps/p4-transfer/*.json` (per-subject summaries).
- Reproduction scripts: `scripts/run_p1_trend_sweep.py`,
  `scripts/run_p1_video_sweep.py`, `scripts/run_p1_meanrev_sweep.py`,
  `scripts/run_p1_trend_hourly_sweep.py`,
  `scripts/run_p2_validation.py`, `scripts/run_p4_transfer.py`.
