"""Promotion significance bar — ORDER 007 (control/inbox.md, 2026-07-10).

The founding plan's multiple-testing discipline (docs/founding-plan.md)
states: "Prefer deflated Sharpe ratios, and require survivors to also work
on instruments they were not tuned on." Before ORDER 007 the promotion rule
contained no statistics at all — any positive Sharpe delta over buy-and-hold
promoted a candidate to PROMOTED-TO-FINDING. This module adds the missing
significance bar.

Why an explicit minimum t-stat instead of the full deflated Sharpe ratio
--------------------------------------------------------------------------
The Bailey & Lopez de Prado (2014) deflated Sharpe ratio needs inputs the
ledger does not record: the variance of Sharpe estimates ACROSS the trials
that produced the candidate, plus the skewness and kurtosis of the selected
strategy's returns. Rather than reconstruct those (impossible for ledgered
runs whose return series were never persisted), we implement the founding
plan's preference as an EQUIVALENT explicit significance test, sanctioned by
ORDER 007 verbatim ("or an equivalent explicit significance test, e.g. a
minimum t-stat on the Sharpe delta"):

* a t-statistic on the annualized Sharpe delta vs buy-and-hold, using the
  Lo (2002) standard error of the Sharpe estimator, and
* a Bonferroni-adjusted threshold that RISES with the number of variants
  tried — the same penalty direction, applied for the same reason, as the
  deflated Sharpe's expected-maximum term: the more configurations were
  tried, the higher the bar any single winner must clear.

Formulas (annualization matches trading_lab.metrics.sharpe: per-period mean
over per-period std, scaled by sqrt(periods_per_year); zero risk-free rate):

    SR_per   = SR_annual / sqrt(periods_per_year)
    SE(SR_annual) = sqrt((1 + SR_per^2 / 2) / N) * sqrt(periods_per_year)
        # Lo (2002), iid-returns form, expressed at annual scale
    t        = (SR_strategy - SR_benchmark) / SE(SR_strategy)
    t_min(K) = Phi^-1(1 - ALPHA / max(1, K))
        # one-sided normal quantile, Bonferroni over K variants tried

Using the single-strategy SE for the DELTA is the honest simple choice: the
exact SE of a Sharpe difference (Jobson-Korkie/Memmel) needs the return
correlation, which is unavailable from ledgered scalars. For this repo's
long/flat strategies benchmarked against buy-and-hold of the SAME instrument
the returns are strongly positively correlated, which shrinks the true SE of
the difference below the single-estimate SE — so this choice is conservative
(it makes promotion HARDER, never easier). ALPHA = 0.05 one-sided at K = 1
(t_min = 1.645).

Verdicts:

* ``PROMOTED-TO-FINDING`` — beats B&H net of costs AND t >= t_min(K).
* ``RULE-PASS`` — beats B&H net of costs but t < t_min(K): an honest
  candidate, never a finding.
* ``KILLED`` — does not beat B&H net of costs.
"""

from __future__ import annotations

import math
from statistics import NormalDist

from . import metrics

# One-sided significance level at a single trial. Bonferroni divides this by
# the number of variants tried.
ALPHA = 0.05

VERDICT_PROMOTED = "PROMOTED-TO-FINDING"
VERDICT_RULE_PASS = "RULE-PASS"
VERDICT_KILLED = "KILLED"

# Sweep-lane verdict vocabulary (Round-2 KEEP/KILL rule, extended by the
# pre-registered Round-4 slice R4-A with a "significantly harmful" class).
SWEEP_KEEP = "KEEP"
SWEEP_KILL = "KILL"
SWEEP_KILL_SIG = "KILL-SIG"

# Post-holdout dev-lane KEEP verdict string. Historically a per-script
# literal in every round-2..5 runner; defined ONCE here for round-6+ code
# (docs/selection-fair-gate.md). Existing scripts keep their own literals —
# historical artifacts stay byte-identical.
VERDICT_KEEP_DEV = "KEEP (dev-candidate only)"


def sharpe_se(sharpe_annual: float, n_periods: int, timeframe: str) -> float:
    """Lo (2002) standard error of an annualized Sharpe estimate.

    ``sharpe_annual`` must be annualized exactly as
    :func:`trading_lab.metrics.sharpe` annualizes (sqrt(periods_per_year)
    scaling); ``n_periods`` is the number of return observations (bars).
    """
    if n_periods <= 0:
        raise ValueError(f"n_periods must be positive, got {n_periods}")
    ppy = metrics.periods_per_year(timeframe)
    sr_per = sharpe_annual / math.sqrt(ppy)
    return math.sqrt((1.0 + sr_per ** 2 / 2.0) / n_periods) * math.sqrt(ppy)


def sharpe_delta_tstat(strategy_sharpe: float, benchmark_sharpe: float,
                       n_periods: int, timeframe: str) -> float:
    """t-statistic of the annualized Sharpe delta vs the benchmark.

    SE is the strategy's own Lo (2002) SE — conservative for same-instrument
    positively-correlated benchmark returns (see module docstring).
    """
    se = sharpe_se(strategy_sharpe, n_periods, timeframe)
    return (strategy_sharpe - benchmark_sharpe) / se


def min_tstat(variants_tried: int, alpha: float = ALPHA) -> float:
    """Bonferroni-adjusted one-sided minimum t: Phi^-1(1 - alpha / K)."""
    k = max(1, int(variants_tried))
    return NormalDist().inv_cdf(1.0 - alpha / k)


def grade_promotion(*, strategy_sharpe: float, benchmark_sharpe: float,
                    n_periods: int, timeframe: str,
                    variants_tried: int = 1) -> dict:
    """Apply the full promotion rule. Returns the verdict plus its arithmetic.

    Promotion to FINDING requires BOTH: (a) strategy Sharpe > benchmark
    (buy-and-hold) Sharpe net of costs, and (b) the Sharpe-delta t-stat
    clears the Bonferroni-adjusted bar for ``variants_tried``. A positive
    delta below the bar is ``RULE-PASS`` (candidate), never a finding.
    """
    for name, value in (("strategy_sharpe", strategy_sharpe),
                        ("benchmark_sharpe", benchmark_sharpe)):
        if value is None or (isinstance(value, float) and math.isnan(value)):
            raise ValueError(f"{name} must be a finite number, got {value!r}")
    delta = strategy_sharpe - benchmark_sharpe
    se = sharpe_se(strategy_sharpe, n_periods, timeframe)
    t = delta / se
    threshold = min_tstat(variants_tried)
    if delta <= 0:
        verdict = VERDICT_KILLED
    elif t >= threshold:
        verdict = VERDICT_PROMOTED
    else:
        verdict = VERDICT_RULE_PASS
    return {
        "verdict": verdict,
        "sharpe_delta": delta,
        "sharpe_se": se,
        "tstat": t,
        "min_tstat": threshold,
        "alpha_one_sided": ALPHA,
        "variants_tried": max(1, int(variants_tried)),
        "n_periods": int(n_periods),
        "timeframe": timeframe,
    }


def classify_verdict(keep: bool, tstat, min_tstat) -> str:
    """Three-way sweep-lane verdict — R4-A (docs/research-round-4-plan.md).

    Pre-registered rule: **KILL-SIG** iff the lane is not a KEEP and its
    already-recorded ``tstat <= -min_tstat`` — the SAME Bonferroni bar,
    mirrored into the negative direction. Zero new arithmetic: both inputs
    come verbatim from the lane's committed sweep summary. A KILL-SIG is
    evidence AGAINST the lane (significant harm), never a long/short
    inversion signal.

    Total by design: a missing/NaN/non-numeric ``tstat`` or ``min_tstat``
    degrades safely to plain :data:`SWEEP_KILL` — this function never
    raises and never invents a significance claim it cannot support.
    """
    if keep:
        return SWEEP_KEEP
    try:
        t = float(tstat)
        bar = float(min_tstat)
    except (TypeError, ValueError):
        return SWEEP_KILL
    if math.isnan(t) or math.isnan(bar):
        return SWEEP_KILL
    if t <= -bar:
        return SWEEP_KILL_SIG
    return SWEEP_KILL
