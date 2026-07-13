# Research Round 4 — Results (running narrative)

> **Status:** `reference` — honest results of the Round-4 slices as they
> land, one dated section per slice, against the pre-registered protocol in
> [research-round-4-plan.md](research-round-4-plan.md) (merged BEFORE any
> Round-4 outcome existed). **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT
> and promotion is CLOSED.** Nothing on this page is an out-of-sample claim;
> a KEEP means *dev-candidate only*, and nulls/KILLs are first-class
> results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`, ~2.64 at K=12; only ever rises).
> Owner mandate: ORDER 012 generative rung. Later Round-4 slices append
> their sections to this file.

## R4-A — KILL-SIG verdict class + retroactive round-3 re-grade (2026-07-13)

**Headline: of the 302 committed round-3 per-lane summaries, exactly 4
lanes are significantly HARMFUL (KILL-SIG, t ≤ −2.638 at K=12); the other
238 KILLs are noise-level, 58 KEEP-dev lanes are unchanged, and the 2 XSEC
bookkeeping-only summaries are UNGRADEABLE. The pre-registered hypothesis
("a small set, 1–3, of significantly-harmful lanes exists; almost all KILLs
are noise") is qualitatively confirmed and quantitatively missed by one:
the set has 4 members, not 1–3.**

- **Rule applied** (pre-registered, zero new arithmetic): KILL-SIG iff the
  lane's already-recorded `tstat ≤ −min_tstat` at its own recorded K — the
  same Bonferroni bar, mirrored. Implemented as
  `trading_lab.promotion.classify_verdict`; report produced by
  `scripts/run_r4_killsig_regrade.py`.
- **Non-destructive**, as registered: every `experiments/sweeps/r3-*/` JSON
  is byte-untouched; the single new artifact is
  [`experiments/sweeps/r4-killsig-regrade/summary.json`](../experiments/sweeps/r4-killsig-regrade/summary.json)
  (per-lane rows: sweep, instrument, strategy, timeframe, original verdict,
  tstat, min_tstat, new verdict). No backtest ran, no data was loaded, and
  `experiments/index.jsonl` is untouched (a re-grade is a report, not runs).
- **Scope note**: the plan's "~312" referred to the extended-round
  graded-lane tally; the per-lane summary files actually committed under
  `experiments/sweeps/r3-*/` number 302, of which 300 carry verdicts.

### Re-grade counts

| New verdict | Lanes |
|---|---|
| KEEP (unchanged) | 58 |
| KILL (noise-level) | 238 |
| **KILL-SIG (significant harm)** | **4** |
| UNGRADEABLE (no recorded t-stat; counted, never recomputed) | 2 |
| **Total** | **302** |

### The four KILL-SIG lanes

| Sweep | Strategy | Instrument | Timeframe | t-stat | bar (K=12) |
|---|---|---|---|---|---|
| r3-roc-adx | adx_filtered_sma | GOOGL | daily | −3.100 | 2.638 |
| r3-meanrev-new-tickers | rsi_mean_reversion | TSLA | daily | −3.011 | 2.638 |
| r3-aroon-cci | cci_reversion | NVDA | daily | −2.930 | 2.638 |
| r3-aroon-cci | cci_reversion | AAPL | daily | −2.838 | 2.638 |

The lane that motivated the slice (TSLA `rsi_mean_reversion`, PR #91 card)
is confirmed KILL-SIG; the plan's near-miss prediction is also confirmed:
SPY `donchian` (r3-trend-new-tickers, t = −2.417) stays **plain KILL** —
it does not cross the −2.638 bar. The two UNGRADEABLE lanes are the
`r3-xsec-expanded` XSEC-14 composites, whose committed summaries carry no
verdict or `promotion_grade` by design ("bookkeeping only") — they are
counted honestly, not recomputed.

### What KILL-SIG means (and does not mean)

A KILL-SIG is **evidence AGAINST the lane** — significantly harmful on the
dev rail, a reason to stop working on it. It is explicitly **NOT a signal
to invert**: a long/short flip of a significantly-negative lane would be a
new, untested strategy selected on the very data that graded it — the
textbook selection-on-outcome error this repo's discipline exists to
prevent. No inversion lane is created, scheduled, or suggested.

## R4-B — Execution-cost sensitivity re-grade of round-3 KEEPs (2026-07-13)

**Headline: of the 58 round-3 KEEP-dev lanes, 42 survive the 2× cost tier
(10 bps slippage + 2 bp commission per side) and keep dev-candidate
status; 16 flip to KILL. Only 25 of 58 also survive the 4× tier (20 bps +
4 bp — reported as a robustness gradient, not a status change). Zero
lanes go KILL-SIG at either tier, and the best t-stat anywhere at 2× is
1.315 (BTC-USD `bollinger_breakout`) against the unchanged 2.638 bar at
K=12 — nothing here reopens promotion; every survivor is a dev-candidate
only, promotion is CLOSED.**

The pre-registered hypothesis ("most or all round-3 KEEP-dev lanes flip
to KILL at realistic-pessimistic costs") is **NOT confirmed** — 72%
survive 2× — and that null-on-the-hypothesis is recorded as the
first-class result it is. The attrition that does happen is strongly
structured: **hourly lanes die at twice the daily rate** (8 of 19 hourly
KEEPs die at 2× vs 8 of 39 daily; at 4× only 4 of 19 hourly survive vs
21 of 39 daily), exactly what higher per-side costs on higher-turnover
bars predict.

- **Pre-registration**: `docs/research-round-4-plan.md` § R4-B (merged
  before any Round-4 outcome). Kill criterion per lane per tier, verbatim:
  KILL iff stitched OOS Sharpe ≤ same-window same-cost B&H Sharpe **or**
  ≤ 0; a lane keeps dev-candidate status only if it survives 2×.
- **KEEP universe**: the 58 `new_verdict == KEEP` lanes of
  [`experiments/sweeps/r4-killsig-regrade/summary.json`](../experiments/sweeps/r4-killsig-regrade/summary.json)
  (R4-A, PR #100). Scope reconciliation, same spirit as R4-A's
  302-vs-~312 note: the plan's "64 after PR #95" was the extended-round
  prose tally; the committed machine-readable KEEP surface is these 58.
- **No re-search, implemented literally** (pre-registered: "stressing
  costs must not become a second selection pass"): the train-window grid
  selection was NOT re-run. Each lane's committed walk-forward per-split
  params were replayed frozen over the exact same positional test windows
  (`scripts/run_r4_cost_sensitivity.py`); positions depend only on price
  data, so the trades are IDENTICAL across tiers — only execution costs
  differ. Fidelity guard: every lane's baseline (5 bps + 1 bp) replay
  reproduced its committed stitched OOS Sharpe within 1e-8 before any
  stress was applied; **0 lanes SKIPPED** (the guard fired nowhere).
- **All 58 graded, both tiers** — 116 per-lane-per-tier detail JSONs plus
  the rollup in
  [`experiments/sweeps/r4-cost-sensitivity/`](../experiments/sweeps/r4-cost-sensitivity/);
  every `experiments/sweeps/r3-*/` file byte-untouched. Full sweep
  runtime ~8 s (replay, not re-search).
- **Ledger decision (deliberate): report-only, NOT ledgered.** No new
  config was searched — the replayed variants are the lanes'
  already-committed choices — so "top variant per lane per tier" rows
  would duplicate the 58 r3-ledgered rows at different costs and pollute
  `experiments/index.jsonl` with confusing near-identical entries.
  `experiments/index.jsonl` is untouched; the rollup records the same
  rationale machine-readably.

### Counts

| Tier (per-side costs) | Survive | Die | Rule |
|---|---|---|---|
| baseline 1× (5 bps + 1 bp) | 58 | — | round-3 verdicts, unchanged |
| **2× (10 bps + 2 bp)** | **42** | **16** | survivors keep dev-candidate status |
| 4× (20 bps + 4 bp) | 25 | 33 | robustness gradient only |

Every 4× survivor also survives 2× (the gradient is monotone lane-by-lane
— no anomalies). KILL-SIG at stress: 0 at 2×, 0 at 4× (the mirrored
−2.638 bar; `classify_verdict` applied to every graded tier).

### Notable survivors (informational t-stats only — none near the bar)

| Sweep | Strategy | Instrument | TF | 2× Sharpe (vs B&H) | 2× t | 4× Sharpe | 4× t |
|---|---|---|---|---|---|---|---|
| r3-btc-coverage | bollinger_breakout | BTC-USD | daily | 1.238 (0.821) | 1.315 | 1.198 | 1.190 |
| r3-stoch-willr | williams_r_reversion | SLV | daily | 0.465 (0.169) | 0.936 | 0.397 | 0.722 |
| r3-trix-ichimoku | ichimoku_trend | META | daily | 0.970 (0.653) | 0.894 | 0.922 | 0.761 |
| r3-trend-new-tickers | ema_crossover | TLT | daily | 0.463 (0.196) | 0.845 | 0.424 | 0.724 |
| r3-meanrev-hourly | rsi_mean_reversion | GOOGL | hourly | 1.771 (1.007) | 0.669 | 1.653 | 0.570 |

All five BTC-USD daily KEEPs survive both tiers (crypto lanes were graded
against a strong B&H benchmark to begin with, and the committed variants
trade slowly); META (8) and TLT (8) carry the most 2× survivors among
equities/bonds. The best absolute stressed Sharpe with a KEEP,
AAPL hourly `stochastic_reversion` (1.926 vs benchmark 1.567 at 2×), dies
at 4× — a clean example of the gradient doing its job.

### Notable deaths (nulls are first-class)

- AAPL hourly `rsi_mean_reversion` — the round-3 baseline stitched OOS of
  1.788 collapses to 1.269 at 2× against a 1.567 benchmark: KILL at the
  first stress rung despite being one of round 3's flashiest KEEPs.
- GLD hourly `aroon_trend` — baseline 2.068 (the highest baseline Sharpe
  in the KEEP set) drops to 1.892 at 2× against a 2.051 benchmark: KILL.
  High-Sharpe hourly lanes sat on high-Sharpe benchmarks; costs decide.
- XOM `macd_supertrend` and `vol_filtered_trend` (daily) die at 2× —
  the thin-margin-over-weak-benchmark cluster the plan's motivation
  section predicted would be erased first.

No surviving lane is a finding. The holdout is SPENT, promotion is
CLOSED, and any OOS test of any survivor remains OWNER-GATED on
post-2026 data.

## R4-F — day-of-week seasonality (2026-07-13)

**Headline: the pre-registered null HOLDS. Across all 75 registered
day×ticker combos (5 weekdays × 15 daily tickers), NOTHING clears the
K=75 bar — `significant_at_k75` is false everywhere, exactly as
hypothesized. Best t anywhere is 0.317 (TSLA Friday) against the 3.209
bar; 0 combos KEEP under the registered rule, 45 KILL, and 30 are
KILL-SIG (significantly HARMFUL, t ≤ −3.209). All 15 lane-level
walk-forwards KILL under the standard Round-2 rule (0 KEEP), with one
lane-level KILL-SIG at K=75 (TLT, t = −3.43).**

- **K accounting, explicit** (the point of this slice): the lane grid
  handed to each ticker's walk-forward is 5 weekday variants, but the
  REGISTERED significance K counts ALL day×ticker combos tested:
  5 × 15 = **K = 75**, so the bar RISES to `min_tstat(75)` = **3.209**
  (vs 2.638 at the standard K=12). K was declared in the grid commit
  before the sweep ran (`trading_lab.sweeps.R4_SEASONALITY_K`, pinned by
  test) and was never counted down; no multi-day subsets were swept, so
  nothing was added to K. Every per-lane JSON records both the
  lane-local informational t (K=5) and the registered K=75 verdict.
- **Rule applied** (pre-registered): a combo is an R4-F KEEP iff it
  clears BOTH the Round-2 benchmark rule AND t ≥ 3.209 at K=75;
  everything else KILL, or KILL-SIG at t ≤ −3.209 (R4-A's mirrored bar,
  `trading_lab.promotion.classify_verdict`). Runner:
  `scripts/run_r4_seasonality_sweep.py`; new family
  `weekday_long` (the program's first calendar rule — t/t+1 fill
  semantics documented in the strategy module: the variant labeled
  weekday=d is exposed to the session after each day-d bar; the five
  variants tile the trading week, so no calendar effect can hide
  between labels).
- **Result — null, first-class**: 0 of 75 combos significant at K=75;
  0 of 75 KEEP under the registered rule; 0 of 15 lanes KEEP under even
  the standard Round-2 rule. The only combos with positive t are three
  Fridays — TSLA (0.317), AAPL (0.135), XOM (0.120) — which pass the
  standard benchmark rule and would have been "dev-candidates" in a
  round graded at the lane-local bar, but the pre-registered K=75 bar
  is the ONLY bar this slice registered for significance and they miss
  it by an order of magnitude. Nothing here is a candidate for anything.
- **The KILL-SIG mass is a benchmark-exposure artifact, read honestly**:
  30/75 combos (and TLT at lane level, t = −3.43) are significantly
  WORSE than same-window same-cost B&H. A rule that is long one session
  per week holds ~20% market exposure plus a weekly round-trip cost
  drag, benchmarked against a fully-invested B&H over a mostly-rising
  dev window — the significant harm says "one-day-a-week exposure loses
  to being invested", not "these weekdays are cursed". Thursday is the
  worst-graded day (11 of its 15 combos KILL-SIG, mean t −3.94, worst
  GOOGL Thu at −5.84) and Friday the least bad (2 KILL-SIG, mean t
  −1.48, and all three positive-t combos) — a *pattern*, but exactly the
  kind the 3.209 bar exists to keep out of the findings column, and on
  the positive side nothing comes remotely close.
- **Artifacts**: 15 per-lane JSONs (r3 schema + `combos` block +
  `verdict_k75` block) and the rollup in
  [`experiments/sweeps/r4-seasonality/`](../experiments/sweeps/r4-seasonality/);
  these ARE new runs (new family, new configs — unlike the R4-B replay),
  so each lane's top full-dev-period variant is ledgered (15 rows,
  `variants_tried=5`, post-hoc-selection caveat in the notes) and
  `experiments/index.jsonl` rebuilt. Full sweep runtime ~23 s.
- **Burden ledger**: 75 new registered configs; program cumulative
  4148 → **4223**.

### Counts

| Level | N | KEEP | KILL | KILL-SIG | significant_at_k75 |
|---|---|---|---|---|---|
| registered combos (K=75 rule) | 75 | 0 | 45 | 30 | 0 |
| lanes (standard Round-2 rule; KILL-SIG at the K=75 bar) | 15 | 0 | 14 | 1 (TLT) | 0 |

Best combo t: **0.317** (TSLA Friday) vs bar **3.209**. Worst combo t:
**−5.840** (GOOGL Thursday). Lane-level t range: −0.91 (TSLA) to −3.43
(TLT).

Day-of-week seasonality on this surface is dead at the honestly-counted
bar — the classic data-mined calendar "edge" does not survive its own K.
No lane, combo, or day is a finding or a dev-candidate. The holdout is
SPENT, promotion is CLOSED, and any OOS claim about anything in this
slice remains OWNER-GATED on post-2026 data.
