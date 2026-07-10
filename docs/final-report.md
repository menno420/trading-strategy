# trading-lab final report — ranked, honestly-validated (FINAL)

> **Status:** `reference` — the P5 ranked final report. Pre-holdout
> sections written 2026-07-10 (lane `p5-prep`); §Holdout FILLED
> 2026-07-10 by the owner-gated one-shot evaluation (ORDER 008, lane
> `p5-holdout-evaluation`) executed exactly per the pre-registered
> [p5-holdout-protocol.md](p5-holdout-protocol.md). The holdout is now
> SPENT and this report is FINAL (protocol §6: no tuning, no re-runs, no
> new windows — ever).

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
entry](p2-regrade-aapl-donchian.md)). **No candidate holds a finding
label.** The one-shot holdout read (§Holdout, executed 2026-07-10) is
the last word: the primary was CONFIRMED by the pre-registered
mechanical rule (Sharpe 0.759 vs B&H 0.740 — a +0.019 edge, t = 0.02,
deep inside noise, RULE-PASS under the significance bar), and 2 of 12
secondaries beat B&H on their holdout windows — indistinguishable from
the pre-registered chance base rates. Nothing tested here earned a
statistically significant edge over buy-and-hold, on any window,
including the holdout.

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
  [holdout-enforcement.md](holdout-enforcement.md)) remained sealed
  through P0–P4. It was unlocked exactly once, on 2026-07-10, for the
  owner-gated one-shot evaluation of §Holdout; exactly 13 ledger rows
  carry the visible `holdout_unlocked` marker (CI-audited on every run),
  and every other row has `data_end ≤ 2025-01-08` with no marker.

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

| Rank | Candidate (family × ticker × tf) | P1 OOS Sharpe vs B&H | Burden | P2 verdict | P4 | P5 holdout (Sharpe vs B&H) | Caveats |
|---|---|---|---|---|---|---|---|
| **1** | **donchian × AAPL × daily** (entry=15, exit=5) | **1.18 vs 0.96** | 177 | **RULE-PASS / candidate** (0.619 vs 0.540, 1980→2009; was PROMOTED-TO-FINDING, [demoted 2026-07-10](p2-regrade-aapl-donchian.md): t = 0.42 < 1.64) | 1/8 FAILED | **CONFIRMED** (0.759 vs 0.740; t = 0.02) | sole out-of-selection B&H beat, but the edge is 0.42 SE — inside noise; drawdown-shaped (MDD −21% vs −37% OOS; −64% vs −82% at P2; −12% vs −31% at P5, CAGR trails 8.9% vs 20.3%); transfer failure sharpens the prior against it |
| 2 | macd × META × hourly (5/26/5) | 1.40 vs 0.49 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 0/7 FAILED | HOLDOUT-MISS (−0.240 vs 0.338) | P1-flagged least trustworthy: fastest grid corner, ~210 changes/yr, per-split Sharpe swings +3.8 → −1.1, single-regime OOS |
| 3 | macd_supertrend × BTC-USD × daily | 1.20 vs 0.82 | 92 | UNVALIDATABLE-PRE-HOLDOUT | 0/8 FAILED | HOLDOUT-BEAT (−0.119 vs −0.314) | Sortino *below* B&H (0.70 vs 0.85); two OOS test years never traded; bubble-instrument trend filter; holdout "beat" = losing −3.8% while B&H lost −32.8% |
| 4 | donchian × AMZN × hourly (40/40) | 0.91 vs 0.61 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/7 FAILED | HOLDOUT-MISS (0.113 vs 0.362) | single-regime ~8.5-month OOS; shares frozen vector with rank 6 — not independent evidence |
| 5 | supertrend_flip × BTC-USD × daily | 1.11 vs 0.82 | 92 | UNVALIDATABLE-PRE-HOLDOUT | 1/8 FAILED | HOLDOUT-MISS (−0.465 vs −0.314) | drawdown reduction (−53% vs −83%), not out-trading; 0/4 untuned spot checks off-BTC |
| 6 | sma_crossover × META × daily (15/75) | 0.93 vs 0.65 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/8 FAILED | HOLDOUT-MISS (−0.013 vs 0.358) | edge concentrated in sidestepping META's 2022 −76% drawdown |
| 7 | sma_crossover × GOOGL × hourly (10/75) | 1.25 vs 1.01 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 1/7 FAILED | HOLDOUT-MISS (1.113 vs 1.322) | thin margin, single-regime OOS |
| 8 | ema_crossover × META × daily (25/50) | 0.83 vs 0.65 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 1/8 FAILED | HOLDOUT-MISS (−0.206 vs 0.358) | same 2022-drawdown profile as rank 6 |
| 9 | donchian × META × daily (55/55) | 0.80 vs 0.65 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/8 FAILED | HOLDOUT-MISS (−0.540 vs 0.358) | same profile |
| 10 | rsi_mean_reversion × META × daily (2/10/50) | 0.79 vs 0.65 | 144 | UNVALIDATABLE-PRE-HOLDOUT | 0/8 FAILED | HOLDOUT-BEAT (1.026 vs 0.358; t = 0.81 < 1.64) | drawdown-shaped (MDD −35% vs −76%); the largest holdout margin of the 13 and still inside noise |
| 11 | ema_crossover × GOOGL × hourly (20/50) | 1.06 vs 1.01 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 1/7 FAILED | HOLDOUT-MISS (1.186 vs 1.322) | margin inside noise |
| 12 | donchian × GOOGL × hourly (40/40) | 1.05 vs 1.01 | 177 | UNVALIDATABLE-PRE-HOLDOUT | 2/7 FAILED | HOLDOUT-MISS (0.894 vs 1.322) | margin inside noise; vector shared with rank 4 |
| 13 | pullback × META × daily (7/7/100) | 0.67 vs 0.65 | 144 | UNVALIDATABLE-PRE-HOLDOUT | 0/8 FAILED | HOLDOUT-MISS (0.029 vs 0.358) | 0.02 Sharpe margin — flagged at P1 as unlikely to survive validation |
| — | pullback × GOOGL × daily (5/7/0) | 0.85 vs 0.72 | 144 | **KILLED** (0.256 vs 1.054 on 2004→2009) | excluded | excluded (killed candidates stay dead) | dead; did not run at P5 |
| — | dual-EMA video control × BTC-USD (400/45 region) | 0.88 vs 0.82 | 92 (control: 20) | negative-complete at P1 | — | not a P5 subject | the video's one fully-stated artifact; weakest of its three interpretations |

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
| **P5 holdout (2025-01-10 → 2026-07-10, 375 bars) Sharpe** | **0.759** | 0.740 |
| P5 CAGR / MDD | 8.9% / −11.8% | 20.3% / −30.7% |
| P5 total return / n_trades | +13.6% / 17 | +31.8% / 1 |

Honest characterization, as ledgered: a **modest, drawdown-shaped,
instrument-specific, statistically insignificant** result. In all three
windows it earns its Sharpe edge by losing less in drawdowns, not by
out-returning holding (its CAGR trails B&H in all three). At P4 it
transferred to 1 of 8 other instruments; under the significance bar its
P2 edge is 0.42 standard errors and its P5 holdout edge is 0.02 standard
errors. Its one-shot holdout read (the pre-registered PRIMARY verdict,
§Holdout) is **CONFIRMED** by the mechanical §5 rule — and that confirms
a candidate's rule-compliance, not a finding: the label remains
**RULE-PASS / candidate**.

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

## Holdout results (P5 — executed 2026-07-10, one shot, SPENT)

Executed 2026-07-10 (lane `p5-holdout-evaluation`, ORDER 008 — the
explicit owner gate of protocol §7.1) exactly per the pre-registered
[p5-holdout-protocol.md](p5-holdout-protocol.md): the §2 frozen-param
table was re-verified 13/13 against the sweep JSONs at run time, fresh
bars were fetched through the standard path into `data/p5holdout/`,
loaded once with `unlock_holdout=True`, and the 13 subject runs + 13
buy-and-hold benchmarks of §1–§3 ran once each
(`scripts/run_p5_holdout.py`; machine-readable results:
`experiments/sweeps/p5-holdout/results.json`). All 13 ledger rows carry
the visible `holdout_unlocked` marker, propagated into
`experiments/index.jsonl` (CI audit green). **The holdout is now spent:
per §6 there will be no re-runs, no tuning, no new windows, no new
variants — ever. This report is final.**

### Headline: the PRIMARY verdict

**AAPL-donchian (entry=15, exit=5, daily): CONFIRMED** by the
pre-registered §5 rule — strategy Sharpe **0.759** > B&H Sharpe
**0.740**, net of costs, on 2025-01-10 → 2026-07-10 (375 bars, ledger
`runs/20260710T164705692772Z-45c47f3e9649.json`).

What CONFIRMED does and does not mean, per the pre-registered
interpretation context and the [2026-07-10 label
supersession](p2-regrade-aapl-donchian.md): the subject entered the
holdout already **demoted to RULE-PASS / candidate** (ORDER 007 — its P2
"finding" label was rescinded pre-holdout; the protocol's §1 subject
table stands, its "sole P2 PROMOTED-TO-FINDING" prose label is
superseded). The holdout CONFIRMED therefore confirms a *candidate's*
rule-compliance, not a finding. Under the ORDER 007 significance rule
(`trading_lab.promotion.grade_promotion`), the holdout edge of +0.019
Sharpe has a Lo (2002) SE of 0.819 on 376 bars: **t = 0.02**, versus a
minimum of 1.64 at the most lenient denominator K=1 (3.45 at the P1 lane
burden K=177) — **RULE-PASS, deep inside noise**, weaker in SE terms
than the P2 edge that was itself demoted (t = 0.42). The shape repeats
for the third window out of three: the Sharpe edge comes from a smaller
drawdown (−11.8% vs −30.7%), while CAGR (8.9% vs 20.3%) and total return
(+13.6% vs +31.8%) trail holding. Sortino is *below* B&H (0.51 vs 0.76).
A mechanical CONFIRMED with t = 0.02 is reported as exactly that —
nothing more.

### All 13 verdicts (§5, mechanical; ledger rows cited)

Engine per §3 (t+1-open fills, 5+1 bps per side, long/flat); benchmark =
B&H of the same instrument on the identical slice, same costs. Window
per §4: first available bar ≥ 2025-01-09 → last bar available at
evaluation time (fetched 2026-07-10 ~17:39 UTC). n bars = scored
holdout-window bars. Every run: `variants_tried = 1`, `holdout_unlocked
= true`. Ledger files below live in `experiments/runs/` (prefix
`20260710T1647`, suffixed by config hash).

| # | Subject | Window used | n bars | Strategy Sharpe / CAGR / MDD / trades | B&H Sharpe | Verdict | Ledger row (runs/…) |
|---|---|---|---|---|---|---|---|
| P | donchian × AAPL × daily | 2025-01-10 → 2026-07-10 | 375 | **0.759** / 8.9% / −11.8% / 17 | 0.740 | **CONFIRMED** | `…05692772Z-45c47f3e9649.json` |
| S1 | sma_crossover × META × daily | 2025-01-10 → 2026-07-10 | 375 | −0.013 / −2.5% / −21.8% / 8 | 0.358 | HOLDOUT-MISS | `…05717762Z-5458e540ac86.json` |
| S2 | ema_crossover × META × daily | 2025-01-10 → 2026-07-10 | 375 | −0.206 / −6.3% / −27.2% / 8 | 0.358 | HOLDOUT-MISS | `…05740033Z-e877eb3af4ba.json` |
| S3 | donchian × META × daily | 2025-01-10 → 2026-07-10 | 375 | −0.540 / −13.8% / −33.8% / 6 | 0.358 | HOLDOUT-MISS | `…05763292Z-577ed236b6d1.json` |
| S4 | supertrend_flip × BTC-USD × daily | 2025-01-09 → 2026-07-10 | 548 | −0.465 / −8.4% / −24.3% / 20 | −0.314 | HOLDOUT-MISS | `…05793743Z-25c02263cbaf.json` |
| S5 | macd_supertrend × BTC-USD × daily | 2025-01-09 → 2026-07-10 | 548 | −0.119 / −1.8% / −12.0% / 18 | −0.314 | HOLDOUT-BEAT | `…05824767Z-545467f92829.json` |
| S6 | rsi_mean_reversion × META × daily | 2025-01-10 → 2026-07-10 | 375 | 1.026 / 22.2% / −13.9% / 42 | 0.358 | HOLDOUT-BEAT | `…05853847Z-210b940e99ec.json` |
| S7 | pullback × META × daily | 2025-01-10 → 2026-07-10 | 375 | 0.029 / −0.6% / −16.4% / 20 | 0.358 | HOLDOUT-MISS | `…05883591Z-e75c6a265469.json` |
| S8 | sma_crossover × GOOGL × hourly | 2025-01-10 14:30 → 2026-07-10 16:30 UTC | 2601 | 1.113 / 29.2% / −18.8% / 48 | 1.322 | HOLDOUT-MISS | `…05911958Z-32cf50796056.json` |
| S9 | ema_crossover × GOOGL × hourly | 2025-01-10 14:30 → 2026-07-10 16:30 UTC | 2601 | 1.186 / 32.0% / −18.6% / 44 | 1.322 | HOLDOUT-MISS | `…05941222Z-fbaceee1ea05.json` |
| S10 | donchian × GOOGL × hourly | 2025-01-10 14:30 → 2026-07-10 16:30 UTC | 2601 | 0.894 / 22.0% / −27.5% / 31 | 1.322 | HOLDOUT-MISS | `…05970665Z-b0f615a41c56.json` |
| S11 | donchian × AMZN × hourly | 2025-01-10 14:30 → 2026-07-10 16:30 UTC | 2601 | 0.113 / −0.1% / −26.8% / 32 | 0.362 | HOLDOUT-MISS | `…05999316Z-78b3162b659f.json` |
| S12 | macd × META × hourly | 2025-01-10 14:30 → 2026-07-10 16:30 UTC | 2601 | −0.240 / −9.2% / −30.6% / 331 | 0.338 | HOLDOUT-MISS | `…06051351Z-483fcc452687.json` |

### Secondaries: k = 2 of 12 HOLDOUT-BEAT — unremarkable under the pre-registered null

**2 of 12 secondaries (16.7%) beat B&H Sharpe on the holdout**, judged
against the full §6 selection burden behind them (177 trend-daily, 92
video, 144 mean-reversion-daily, 177 trend-hourly configurations, plus
per-split re-selection; program-wide, 13 subjects read on the holdout
once each). The pre-registered null said several beats out of 12 would
be unremarkable: pre-holdout lane base rates were 7/32, 3/24 and 5/32
(≈ 12–22%) and P4 transfer hit 13/99 (13%). **2/12 sits squarely on
those chance base rates.** Secondary verdicts are descriptive, never
promotions (§5); the two beats:

- **S5 macd_supertrend × BTC-USD**: a "beat" earned entirely by losing
  less in a falling market — the strategy *lost* −3.8% (Sharpe −0.119)
  while B&H lost −32.8% (Sharpe −0.314). Nothing here made money.
  ORDER 007 grade at K=1: RULE-PASS (t = 0.29 < 1.64).
- **S6 rsi_mean_reversion × META**: the only subject of 13 that beat
  B&H while actually earning a positive return (Sharpe 1.026 vs 0.358,
  CAGR 22.2% vs 6.5%). Still inside noise — ORDER 007 grade at K=1:
  RULE-PASS (t = 0.81 < 1.64; the honest K of its 144-config lane would
  demand 3.4) — and it arrived with the worst possible prior: 0/8 at P4
  and a P1 margin that was itself drawdown-shaped. One holdout beat at
  t = 0.81 from a 144-config lane is what chance looks like.

Applying the ORDER 007 significance rule (reported alongside, per the
order): **0 of 13 subjects clears the promotion bar on the holdout even
at the most lenient K=1** — P, S5 and S6 grade RULE-PASS (beat, below
the bar); the other 10 grade KILLED-equivalent (no beat). No subject
ever cleared a significance test on any window in this program.

### Contingencies, ambiguities, and mechanical notes (§4/§5 guard)

- **§4 hourly contingency: NOT triggered.** Fresh hourly history was
  obtainable back to 2023-08-11, well before 2025-01-09; all five hourly
  subjects ran their full holdout window (2,601 bars ≥ 250). **No
  subject was NOT-EVALUABLE.**
- **Warm-up / first fill (fixed ex-ante, before any number was read;
  documented in `scripts/run_p5_holdout.py`):** positions were computed
  over the full fetched series (§4 permits pre-holdout warm-up), and
  each evaluated slice includes exactly one pre-window warm-in bar —
  contributing zero return and zero cost by engine construction — so
  the position decided on the last dev bar fills at the first holdout
  bar's open ("scored returns begin at the first holdout-window fill",
  §4). The B&H benchmark runs on the identical slice, entering at the
  same first holdout open with the same costs. Ledger `data_start` is
  therefore the 2025-01-08 warm-in bar; scored windows are as tabled.
- **Undefined-Sharpe rule (pre-specified, resolved against the
  strategy):** a NaN/undefined Sharpe would count as not-a-beat. It did
  not trigger — all 26 Sharpes were finite.
- **Last bar (per §4 "last bar available at evaluation time"):** the
  2026-07-10 daily bars and the 16:30 UTC hourly bars were in-progress
  bars at fetch time (~17:39 UTC). Taken as-is per protocol; not
  padded, not trimmed.
- **First equity holdout bar:** US equities have no 2025-01-09 bar
  (market closure); their windows begin at the first available bar,
  2025-01-10, per §4's "first bar available" semantics. BTC-USD (24/7)
  begins exactly 2025-01-09.

### One shot, spent

The 13 subject runs + 13 benchmarks above are the first, only, and last
reads of the holdout. Per protocol §6: **no further tuning, no re-runs,
no parameter changes, no new variants, no additional windows — ever.**
Follow-on research requires genuinely new post-2026 data and a new
pre-registered protocol (an owner decision). This report is final.

## Evidence index

- Ledger: `experiments/index.jsonl` + `experiments/runs/*.json`
  (per-run, CI-audited for holdout boundary compliance).
- Sweep evidence: `experiments/sweeps/p1-*/*.json` (per-variant rows,
  `top_full_period_variant` frozen-param sources),
  `experiments/sweeps/p4-transfer/*.json` (per-subject summaries),
  `experiments/sweeps/p5-holdout/results.json` (the one-shot holdout
  summary; input bars in `data/p5holdout/`).
- Reproduction scripts: `scripts/run_p1_trend_sweep.py`,
  `scripts/run_p1_video_sweep.py`, `scripts/run_p1_meanrev_sweep.py`,
  `scripts/run_p1_trend_hourly_sweep.py`,
  `scripts/run_p2_validation.py`, `scripts/run_p4_transfer.py`,
  `scripts/run_p5_holdout.py` (evidence only — the holdout is one-shot
  and spent; its `--evaluate` phase refuses to re-run).

---

## Research Round 2 summary — POST-HOLDOUT DEV-ONLY ROUND (2026-07-10)

> **BANNER — READ FIRST.** The holdout (bars ≥ 2025-01-09) is **SPENT**
> (the 13 one-shot reads above are the first, only, and last). This
> round makes **NO out-of-sample claims**: every number below is
> computed on **dev data only** (bars strictly before 2025-01-09, via
> the `load_ohlcv` default rail — never `unlock_holdout`, never the
> paper rail). **Promotion is CLOSED.** A "KEEP" below means
> *dev-candidate only* — never a finding, never a validated edge. This
> section does not amend, weaken, or reopen anything above it; the P5
> report remains final.

Round 2 was **pre-registered before any outcome existed**: grids,
instruments, walk-forward scheme (1008/252, stitched OOS only), costs
(5 + 1 bps per side, t+1-open fills), benchmarks, and the KEEP/KILL
rule were frozen in [research-round-2.md](research-round-2.md) and
merged as PR #46 before any Round 2 backtest, sweep, or metric was
computed. Three new families were then swept exactly within the frozen
grids — `vol_filtered_trend` (PR #47), `keltner_breakout` (PR #48),
and `xsec_momentum`, the program's first portfolio-level lane (PR #49)
— using **78 of the 100-config hard-cap budget** (all 78 registered
configs run; the 22 contingency configs untouched, as registered). Full
narrative, honest reads, and ambiguity resolutions:
[research-round-2-results.md](research-round-2-results.md) (the source
of truth for every number below).

### Verdict table — all 14 claim surfaces, KILLs with equal prominence

Rule (pre-registered §6): KEEP as dev-candidate iff stitched OOS Sharpe
> benchmark OOS Sharpe AND > 0; ties/ambiguity resolve KILL. Benchmark
= same-window, same-cost B&H of the instrument (for `xsec_momentum`,
the equal-weight 9-instrument basket B&H).

| Family | Instrument / config | Stitched OOS Sharpe | Benchmark OOS Sharpe | Verdict |
|---|---|---:|---:|---|
| vol_filtered_trend | AAPL | 0.635 | 0.963 | **KILL** |
| vol_filtered_trend | MSFT | 1.015 | 1.101 | **KILL** |
| vol_filtered_trend | NVDA | 1.252 | 1.295 | **KILL** |
| vol_filtered_trend | GLD | 0.214 | 0.400 | **KILL** |
| keltner_breakout | BTC-USD | 1.348 | 0.821 | **KEEP (dev-candidate only)** |
| keltner_breakout | META | 0.747 | 0.653 | **KEEP (dev-candidate only)** |
| keltner_breakout | AMZN | 0.500 | 0.763 | **KILL** |
| keltner_breakout | SLV | −0.042 | 0.170 | **KILL** |
| xsec_momentum | L=63, k=2 | 1.627 | 1.147 | **KEEP (dev-candidate only)** |
| xsec_momentum | L=63, k=3 | 1.631 | 1.147 | **KEEP (dev-candidate only)** |
| xsec_momentum | L=126, k=2 | 0.953 | 1.147 | **KILL** |
| xsec_momentum | L=126, k=3 | 1.136 | 1.147 | **KILL** |
| xsec_momentum | L=252, k=2 | 1.050 | 1.147 | **KILL** |
| xsec_momentum | L=252, k=3 | 1.277 | 1.147 | **KEEP (dev-candidate only)** |

**Headline: 5 KEEP / 9 KILL.** Stated plainly, the KILLs:
vol_filtered_trend died on all four instruments (AAPL, MSFT, NVDA,
GLD); keltner_breakout lost on AMZN and went outright negative on SLV;
xsec_momentum's 126-bar lookback failed with both k values and
L=252/k=2 failed too (L=126/k=3 at 1.136 vs 1.147 is a near-tie the
pre-registered rule resolves against the strategy).

### Denominators (multiple-testing burden)

- This round: **78 configs** (48 vol_filtered_trend + 24
  keltner_breakout + 6 xsec_momentum; 78/100 budget, contingency
  unused).
- Program cumulative: **668** (590 prior P1 configs + 78 Round 2).
- Holdout reads: **still 13** — unchanged, spent, untouched by this
  round.

### Dev-candidates (the complete list — and what they are not)

1. keltner_breakout × BTC-USD × daily (OOS Sharpe 1.348 vs 0.821)
2. keltner_breakout × META × daily (0.747 vs 0.653 — CAGR *trails* B&H
   16.0% vs 19.4%; the edge is purely risk-adjusted)
3. xsec_momentum L=63/k=2 (1.627 vs 1.147)
4. xsec_momentum L=63/k=3 (1.631 vs 1.147)
5. xsec_momentum L=252/k=3 (1.277 vs 1.147)

These are **dev-candidates only**: dev-data results after 668
program-wide tries, with no significance claim of any kind. Five
same-direction survivors out of 668 is selection pressure, not
evidence of an edge. Any step beyond dev-candidate requires a **NEW,
owner-gated, pre-registered protocol on genuinely new post-2026 data**
— recorded here as an **owner-gated PROPOSAL** only, which agents must
never schedule, initiate, or run.

### Honest reading

- **The registered mechanism of R1 subtracted value.** The
  calm-regime volatility filter was the family's entire hypothesis,
  and on 3 of 4 instruments the best full-period variant was the
  filter-**off** arm (the plain crossover); the one instrument that
  preferred the filter in-sample (GLD) lost OOS by the widest relative
  margin. 0 KEEP / 4 KILL is the finding of that slice.
- **keltner_breakout is 2-for-4, not a general win.** The drawdown
  reduction was uniform across all four instruments, but drawdown is
  not the decision metric and bought no KEEP where Sharpe lost (AMZN,
  SLV — SLV's OOS stitch was outright negative).
- **xsec_momentum beat a very hard benchmark on 3 of 6 configs** —
  the equal-weight basket did 32.3% CAGR at Sharpe 1.147 over the OOS
  window — but every config lost money in the 2021-09 → 2022-09 test
  window (a long-only momentum basket rode the 2022 bear down), and
  the KEEPs' edge is concentration in already-running assets, not
  protection: L=63/k=2's max drawdown (−52.9%) is *worse* than the
  basket's (−50.4%).
- **Selection burden context:** the round's 5 KEEPs emerged from 78
  configs this round and 668 program-wide, on dev data the program has
  been mining since P1. Under this program's own standards (ORDER
  007), nothing here approaches a significance bar, none was tested
  against one, and no such claim is made. The only honest label
  available is the one used: dev-candidate.
