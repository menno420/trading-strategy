# Re-grade ledger entry — AAPL-donchian 15/5 under the ORDER 007 significance bar

> **Status:** `reference` — first-class re-grade entry (ORDER 007,
> control/inbox.md, 2026-07-10T12:47:35Z; executed 2026-07-10, lane
> `order-007-significance-bar`). Amends the verdict recorded in
> [p2-validation-results.md](p2-validation-results.md); the underlying P2
> backtest and its ledger row are unchanged and were NOT re-run. The holdout
> stayed sealed throughout — zero bars loaded, zero backtests, no
> `holdout_unlocked` marker anywhere.

## What the rule was (old rule)

`scripts/run_p2_validation.py` promoted on **any positive Sharpe delta**:

```
verdict = "PROMOTED-TO-FINDING" if strategy_sharpe > bh_sharpe else "KILLED"
```

No statistics at all — a +0.001 Sharpe edge on a short window would have
promoted. This is calibrated to mechanical rule-compliance, not statistical
reality, and contradicts the founding plan's own multiple-testing rail
("Prefer deflated Sharpe ratios…", [founding-plan.md](founding-plan.md)).

## What the rule becomes (new rule)

`trading_lab.promotion.grade_promotion` (new module, tested in
`tests/test_promotion.py`). Promotion to FINDING now requires **both**:

1. **Beat buy-and-hold net of costs** — strategy Sharpe > B&H Sharpe on the
   same window, same costs (unchanged), AND
2. **Clear the significance bar** — the t-statistic of the Sharpe delta must
   reach a Bonferroni-adjusted one-sided minimum:

   - `SE(SR_annual) = sqrt((1 + SR_per²/2) / N) · sqrt(periods_per_year)`
     (Lo 2002, iid form, at annual scale; `SR_per = SR_annual / sqrt(ppy)`,
     annualization identical to `trading_lab.metrics.sharpe`),
   - `t = (SR_strategy − SR_B&H) / SE(SR_strategy)`,
   - `t_min(K) = Φ⁻¹(1 − 0.05 / max(1, K))` where `K = variants_tried`
     (`t_min(1) = 1.645`, `t_min(177) = 3.448`).

Verdicts: both conditions → `PROMOTED-TO-FINDING`; beats B&H but below the
bar → `RULE-PASS` (candidate, never a finding); no beat → `KILLED`.

**Equivalence to the deflated-Sharpe preference** (justification, per
ORDER 007's "or an equivalent explicit significance test"): the Bailey &
López de Prado deflated Sharpe needs the cross-trial variance of Sharpe
estimates and the return skew/kurtosis, none of which the ledger records
(return series were not persisted). The Bonferroni-adjusted minimum t-stat
applies the same penalty in the same direction for the same reason — more
variants tried ⇒ a higher bar for any single winner — and is fully explicit
and reproducible from ledgered scalars. Using the strategy's own Lo SE for
the delta is conservative: strategy and B&H returns on the same instrument
are strongly positively correlated, which shrinks the true SE of the
difference below the single-estimate SE, so this choice only makes promotion
harder.

## The re-grade computation — donchian × AAPL × daily (entry=15, exit=5)

Inputs verbatim from the ledgered P2 row
`experiments/runs/20260710T033624806389Z-1943c6697c7c.json`
(window 1980-12-12 → 2009-12-31, `data_end = 2009-12-31` ≤ 2025-01-09;
nothing re-run):

| Quantity | Value |
|---|---|
| Strategy Sharpe (net of costs) | 0.618959 |
| B&H Sharpe (net of costs) | 0.540180 |
| Sharpe delta (edge) | **+0.078779** |
| N (daily bars) | 7,331 |
| SR_per = 0.618959 / √252 | 0.038991 |
| SE = √((1 + 0.038991²/2) / 7331) · √252 | **0.185474** |
| t = 0.078779 / 0.185474 | **0.4247** |
| Threshold t_min(K=1) = Φ⁻¹(0.95) | 1.6449 |
| Threshold t_min(K=41) / t_min(K=177) | 3.0308 / 3.4479 |

**Verdict: t = 0.42 < 1.64 even at the most lenient possible denominator
(K=1, matching the P2 ledger row's `variants_tried = 1`). The edge is ~0.4
standard errors — deep inside noise. → DEMOTED: `PROMOTED-TO-FINDING` is
rescinded; the honest label is RULE-PASS / candidate.**

### Variants-tried denominator

K=1 is the P2 run's own count (one frozen vector, zero re-tuning). The
candidate was nominated by a P1 lane that tried 177 configurations (41 in
the donchian family alone, plus per-split re-selection) — any honest K ≥ 1
only raises the bar (to 3.03–3.45), so the demotion is robust to every
choice of denominator. Pinned in
`tests/test_promotion.py::TestAAPLDonchianRegrade`.

### Why (context)

- The P2 promotion was real rule-compliance (it did beat B&H net of costs on
  29 years it was never tuned on) but was never a statistically significant
  edge; the old rule simply had no way to say so.
- The P4 transfer result already argued against it: 13/13 subjects
  TRANSFER-FAILED, AAPL-donchian itself 1/8
  ([p4-transfer-results.md](p4-transfer-results.md)).
- Fleet night-review Q3: the one-shot holdout is the repo's single most
  valuable pre-registered asset; it must not be spent to headline a
  candidate that never cleared a significance test.

## Implications for the P5 holdout protocol (noted, NOT edited)

[p5-holdout-protocol.md](p5-holdout-protocol.md) is binding and
pre-registered; per ORDER 007 it is not edited. Two of its prose labels are
affected by this re-grade (its §1 calls AAPL-donchian "the sole P2
PROMOTED-TO-FINDING"; §5's primary verdict rule is unaffected):

- AAPL-donchian's status label is now **candidate (RULE-PASS, demoted
  2026-07-10)**, not finding. Its role as PRIMARY subject, its frozen
  params, the closed subject list, the windows, and the pre-registered
  verdict rules are all unchanged — the protocol's inclusion rule ("reached
  the P2 ledger and was not KILLED there") still holds: the re-grade demotes
  to candidate, it does not kill.
- Interpretation note for the evaluating session: a holdout CONFIRMED on the
  primary would confirm a *candidate*, not validate a pre-existing
  "finding"; the pre-registered prior against every subject (P4 13/13
  transfer failure) is now joined by "no subject has ever cleared a
  significance test".

## Evidence

- Rule: `src/trading_lab/promotion.py` (formulas + equivalence note),
  `tests/test_promotion.py` (14 tests incl. this exact computation),
  `scripts/run_p2_validation.py` (verdict path now calls
  `promotion.grade_promotion`).
- Inputs: `experiments/runs/20260710T033624806389Z-1943c6697c7c.json`
  (unchanged; `data_end = 2009-12-31`).
- Labels updated by this re-grade:
  [p2-validation-results.md](p2-validation-results.md),
  [final-report.md](final-report.md),
  [succession/QUEUE.md](succession/QUEUE.md),
  [current-state.md](current-state.md).
