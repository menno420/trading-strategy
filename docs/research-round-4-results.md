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
