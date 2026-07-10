# P1 results — video-strategy interpretations × BTC-USD × daily

> **Status:** `reference` — video-strategy sweep
> (lane `video-strategy__btcusd__multi`, 2026-07-10). Findings are
> walk-forward out-of-sample only, per the binding methodology in
> [founding-plan.md](founding-plan.md). Source material:
> [research/video-source-2026-07-09.md](research/video-source-2026-07-09.md).
> Raw evidence: `experiments/sweeps/p1-video-strategy-daily/` +
> `experiments/index.jsonl`.

## What was tested and why interpretations, plural

The source video (DaviddTech, "I Built a FREE AI Trading Bot With Claude +
TradingView") shows two strategies on BTCUSDT but **never states the
parameters or the trigger/filter roles** of its headline "SuperTrend Flip
EMA MACD" system (see the ambiguities section of the source doc). Per the
lane brief, each plausible resolution runs as its own faithful
interpretation, competing against the others and against buy-and-hold:

| # | family | reading (all long/flat, signal-open/signal-close, no TP/SL) |
|---|---|---|
| i | `supertrend_flip` | SuperTrend-flip entry gated by EMA trend filter + MACD confirmation; exit when SuperTrend flips bearish |
| ii | `macd_supertrend` | MACD cross-up entry gated by SuperTrend + EMA filters (blocked crosses are skipped); exit on MACD cross-down |
| iii | `ema_crossover` | dual-EMA crossover control on the video's stated Strategy-A sweep region, incl. its stated winner slow=400 / fast=45 |

Flagged interpretation choices: **long/flat only** (the transcript never
states shorts; swing, no TP/SL is stated) — and the entry/exit split above
is one reading each of an unstated rule.

## Data decisions (decide-and-flag)

- **Instrument mapping:** the video trades BTCUSDT on Bybit; this lane uses
  Yahoo's **BTC-USD** index via the standard cached loader
  (`data/daily/BTC-USD.csv.gz`). Same underlying, different venue/quote.
- **Timeframe:** the video uses 1h/4h. Yahoo hourly caps at ~730 days: the
  fetch returned 17,464 hourly bars starting 2024-07-11, of which only
  **4,367 bars (~6 months) predate the holdout** (2024-07-11 → 2025-01-08)
  — far too thin for the lab's train-1008/test-252 walk-forward, and the
  lab's hourly annualization (252 × 6.5 sessions) is calibrated to
  equities, not 24/7 crypto. **Daily is the primary timeframe; flagged as a
  deviation from the source.**
- **Annualization:** metrics use 252 periods/year while BTC trades ~365
  days/year, so annualized Sharpe/CAGR are understated by a constant factor
  for strategy and benchmark alike; comparisons vs B&H are unaffected.
- **Dev data:** daily bars 2014-09-17 → 2025-01-08 (3,767 bars; Yahoo
  BTC-USD history starts 2014-09-17). Holdout untouched.
- **Costs on:** 5 bps slippage + 1 bp commission per side, t+1-open fills
  (engine defaults). The video's 7x leverage and $100-margin execution
  config is broker plumbing, not strategy logic — not simulated.

## Method

Identical to [p1-trend-following-results.md](p1-trend-following-results.md):
`trading_lab.walkforward.walk_forward`, train 1008 bars / test 252 bars,
contiguous test windows (10 splits); per split the best in-train-Sharpe grid
point is applied to the following unseen window. The stitched OOS series
(**2017-06-21 → 2024-05-14**, 2,520 bars) is the finding. Benchmark =
buy-and-hold of BTC-USD over the *exact same* stitched OOS window, same
costs.

## Grids and multiple-testing burden

Grids live in `trading_lab.sweeps` (video section, unit-tested counts). The
video never states SuperTrend/EMA/MACD parameters, so axes bracket common
published defaults; the control's axes are the video's own stated sweep
bounds coarsened.

| family | axes | variants |
|---|---|---|
| supertrend_flip | ST period ∈ {7,10,14} × ST mult ∈ {2,3,4} × EMA ∈ {100,200} × MACD ∈ {12-26-9, 8-21-5} | 36 |
| macd_supertrend | same axes | 36 |
| ema_crossover (control) | slow ∈ {110,200,300,400} × fast ∈ {10,25,45,70,100} | 20 |

**Lane total: 92 configurations** (each also backtested full-dev-period as
bookkeeping rows), plus walk-forward re-selection (grid × 10 splits = 360 /
360 / 200 train evaluations). Every "winner" below must be discounted
against this burden — and against the fact that the instrument itself
(BTC 2017–2024) was a serial bubble.

## Headline table — walk-forward OOS (net of costs) vs buy-and-hold

Stitched OOS window 2017-06-21 → 2024-05-14, 10 splits. `*` = beat
buy-and-hold Sharpe over the same window.

| system | OOS Sharpe | OOS CAGR | OOS MDD | OOS Sortino | wf evals |
|---|---|---|---|---|---|
| buy-and-hold BTC-USD | 0.82 | +36.7% | −83.4% | 0.85 | — |
| (i) supertrend_flip | **1.11*** | +40.9% | −52.9% | 0.83 | 360 |
| (ii) macd_supertrend | **1.20*** | +33.6% | −29.1% | 0.70 | 360 |
| (iii) dual-EMA control | 0.88* | +36.2% | −71.9% | 0.70 | 200 |

Untuned default-parameter spot checks on universe tickers (context only,
variants_tried=1 each, full dev period): supertrend_flip NVDA 0.85 vs B&H
1.07, GLD 0.35 vs 0.43; macd_supertrend NVDA 0.48 vs 1.07, GLD −0.02 vs
0.43 — **0 of 4 beat buy-and-hold off-BTC**.

## Honest read

- **All three interpretations beat B&H Sharpe on BTC-USD OOS, but none is a
  finding.** 92 configurations + per-split re-selection on a single
  instrument, in a market where "long during bubbles, flat during busts"
  is the one trade trend filters are built for. The margins come almost
  entirely from **drawdown reduction** (−29% to −53% vs −83.4%), the same
  profile P1 found on equities — not from out-trading the asset (only
  interpretation (i) beat B&H on CAGR, and only by 4 points).
- **Sortino disagrees:** on downside deviation, (ii) and (iii) rank *below*
  buy-and-hold (0.70 vs 0.85). The Sharpe edge partly reflects clipped
  upside volatility, not only avoided losses.
- **Per-split instability:** test-window Sharpes flip sign split to split
  (control: +1.9, −2.8, +1.5, −1.2, …), and two macd_supertrend test years
  never traded at all. Ten splits on one instrument is thin evidence.
- **The video's headline is not reproducible as stated** — its +500% / PF
  2.295 figure is an in-sample optimized 4h backtest with unstated
  parameters. Its one fully stated artifact, the dual-EMA slow=400/fast=45
  region, is the *weakest* of the three systems here (0.88 vs 0.82, a
  margin well inside noise at this multiple-testing burden).
- **Nothing generalizes off-BTC untuned:** 0 of 4 spot checks beat B&H.
- **Verdict per interpretation:** (iii) dual-EMA control —
  **negative-complete** (no meaningful edge over B&H; the video's stated
  winner region does not survive honest OOS testing). (i) supertrend_flip
  and (ii) macd_supertrend — **candidates, not findings**: carried forward
  for P2 deflated-Sharpe/robustness scrutiny alongside the P1 survivors.
  This completes the video-strategy family as specified: the video's
  claims, tested honestly, reduce to "BTC trend filters cut drawdown in a
  bubble-and-bust decade" — already known, and not evidence of the video's
  workflow producing alpha.

## Reproduce

```
python3 scripts/run_p1_video_sweep.py
```
