"""Causal cross-asset regime conditioning — Round 11 (`xasset_regime`).

Pre-registered in ``docs/research-round-11-plan.md``, the self-serve first step
from ``docs/research-direction-new-data-sources.md`` §2.1. Round 11 conditions a
base long position on a RISK-LEG target (SPY / QQQ / NVDA) by a CAUSAL
cross-asset regime score built entirely from the EXISTING committed daily cache
(TLT / GLD / SPY / QQQ legs) — NO new ingestion, NO new ticker, NO new
dependency, pure pandas/numpy over cached OHLCV.

HOW R11 DIFFERS FROM THE BURNED R4 CLASSES (load-bearing). The Round-4
conditioning families are recorded as BURNED classes in
``docs/strategy-catalog.md``: ``crossasset_gate`` (0 KEEP / 2 KILL, §R4-E — a
frozen EMA-cross equity component gated on the SIGN of another instrument's
momentum, an on/off switch; the ungated control beat the gate) and
``regime_switch`` (0 KEEP / 6 KILL, §R4-D — a trend/reversion switch on a
trend-strength tercile; the unconditioned control beat the gate). R11 is NOT a
re-skin of either:

* **Continuous conditioning, not a binary gate.** The R4 gate was a 0/1 switch
  on a momentum SIGN. R11's exposure is the CAUSAL rolling-percentile-rank of a
  real-valued regime score over a trailing window — exposure scales smoothly in
  [0, 1] with how risk-on the regime is *relative to its own recent history*.
* **Causal ROLLING normalization, not a full-sample state.** The percentile
  rank is computed ONLY over the trailing window ending at bar t — never a
  full-sample rank or full-sample z-score. Full-sample normalization is the
  classic regime-lookahead leak; this module forecloses it by construction (the
  guarantee is pinned by the truncation test in
  ``tests/test_xasset_regime.py``).
* **A mandatory unconditioned control arm.** The RUN grades every conditioned
  lane against plain buy-and-hold of the SAME target (position ≡ 1.0) — the
  meta-analysis records that conditioning "loses to its own controls, on every
  axis tested," so the honest registered prior is the program null even here.

CAUSALITY GUARANTEE (the #1 failure mode for this class). Every regime score at
bar ``t`` uses ONLY data with timestamp ``<= t``: all inputs are trailing
windows (trailing-W total returns, trailing-W SMAs) and the conditioning is a
rolling (never full-sample) percentile rank over the trailing
``PERCENTILE_WINDOW`` bars ending at ``t``. Prefix invariance therefore holds
exactly — the score and the conditioned position at bar ``t`` are IDENTICAL
whether computed on the full series or on the series truncated at bar ``t``
(``series.iloc[:t+1]``). That is the load-bearing correctness property, asserted
directly by the headline no-lookahead test. The engine then delays execution to
bar ``t+1``'s open as everywhere else in the lab.

Calendar note: the three targets (SPY, QQQ, NVDA) and the four regime inputs
(SPY, QQQ, GLD, TLT) are ALL on the NYSE calendar — one shared index, so NO
cross-calendar as-of reindex is needed. BTC-USD is deliberately EXCLUDED as a
target precisely because its 24/7 weekend calendar would force an as-of reindex
and add lookahead risk (see the plan's LOOKAHEAD-CONTROL section).

Research only: this module composes simulated position series from cached
closes; it never touches brokers or orders, and it never reads the holdout (the
RUN loads closes via the ``trading_lab.data.load_ohlcv`` dev rail).
"""

from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

# The three causal regime signals (pinned in sweeps._R11_SIGNALS).
REGIME_SIGNALS = ("xasset_eq_bond_mom", "xasset_metals_riskoff",
                  "xasset_breadth")

# The four legs whose close-vs-trailing-SMA state defines the breadth score.
# All on the NYSE calendar (one shared index with the SPY/QQQ/NVDA targets).
BREADTH_ASSETS = ("SPY", "QQQ", "GLD", "TLT")

# The trailing window (in bars) over which the raw regime score is normalized
# into a causal percentile rank. FIXED, not swept (pinned in
# sweeps._R11_PERCENTILE_WINDOW).
PERCENTILE_WINDOW = 252


def trailing_total_return(close: pd.Series, window: int) -> pd.Series:
    """Trailing-``window`` total return: ``close_t / close_{t-window} - 1``.

    Strictly causal — the value at bar ``t`` reads only ``close_t`` and
    ``close_{t-window}`` (both timestamps ``<= t``). NaN during the first
    ``window`` bars (undefined resolves against the strategy downstream).
    """
    if window < 1:
        raise ValueError(f"window ({window}) must be >= 1")
    return close / close.shift(window) - 1.0


# ---------------------------------------------------------------------------
# The three raw regime scores (higher == more risk-on)
# ---------------------------------------------------------------------------

def eq_bond_momentum_score(closes: Mapping[str, pd.Series],
                           window: int) -> pd.Series:
    """``xasset_eq_bond_mom``: trailing-W total return of SPY MINUS trailing-W
    total return of TLT (equities outrunning long-duration bonds == risk-on
    high). Causal: a difference of two trailing-W returns."""
    return (trailing_total_return(closes["SPY"], window)
            - trailing_total_return(closes["TLT"], window))


def metals_riskoff_score(closes: Mapping[str, pd.Series],
                         window: int) -> pd.Series:
    """``xasset_metals_riskoff``: the NEGATIVE of GLD's trailing-W total return
    (gold being bid == risk-OFF, so a rising GLD LOWERS the risk-on score).
    Causal: the negation of a trailing-W return."""
    return -trailing_total_return(closes["GLD"], window)


def breadth_score(closes: Mapping[str, pd.Series], window: int) -> pd.Series:
    """``xasset_breadth``: the fraction of ``BREADTH_ASSETS`` whose ``close_t``
    exceeds their OWN trailing-W SMA at bar ``t`` — a continuous risk-on
    composite in ``[0, 1]``.

    Causal: each asset's SMA is a trailing rolling mean of its last ``window``
    closes (all timestamps ``<= t``); the fraction reads only bar-``t`` states.
    NaN until every leg's SMA is defined (the legs share one calendar and one
    window, so they warm up together).
    """
    if window < 1:
        raise ValueError(f"window ({window}) must be >= 1")
    flags = {}
    for asset in BREADTH_ASSETS:
        close = closes[asset]
        sma = close.rolling(window).mean()  # trailing SMA ending at t (causal)
        # (close > NaN) evaluates False, so mask the warm-up explicitly to NaN
        # rather than silently scoring an undefined leg as "below its SMA".
        above = (close > sma).astype(float).where(sma.notna())
        flags[asset] = above
    frame = pd.DataFrame(flags)
    # Fraction over the four legs; NaN only while every leg is still in warm-up.
    return frame.mean(axis=1)


_SCORE_BUILDERS = {
    "xasset_eq_bond_mom": eq_bond_momentum_score,
    "xasset_metals_riskoff": metals_riskoff_score,
    "xasset_breadth": breadth_score,
}


def regime_score(closes: Mapping[str, pd.Series], signal: str,
                 window: int) -> pd.Series:
    """Dispatch to the named causal regime score (see ``REGIME_SIGNALS``)."""
    try:
        builder = _SCORE_BUILDERS[signal]
    except KeyError:
        raise ValueError(
            f"unknown regime signal {signal!r}; expected one of "
            f"{REGIME_SIGNALS}") from None
    return builder(closes, window)


def rolling_percentile_rank(score: pd.Series,
                            window: int = PERCENTILE_WINDOW) -> pd.Series:
    """CAUSAL rolling-percentile-rank of ``score`` over its trailing ``window``.

    The value at bar ``t`` is the fraction of the ``window`` most-recent VALID
    score observations (ending at, and including, bar ``t``) that are ``<=``
    the score at bar ``t`` — a number in ``(0, 1]``. This is a rolling,
    strictly-trailing normalization: it NEVER uses a full-sample rank or a
    full-sample z-score (the classic regime-lookahead leak).

    Warm-up NaNs in ``score`` (the first ``W`` bars of the trailing-W return /
    SMA) are dropped BEFORE ranking so the window spans ``window`` genuinely
    valid observations; the result is reindexed back onto ``score``'s index,
    leaving NaN on both the score warm-up and the first ``window - 1`` valid
    bars. Prefix invariance holds exactly: dropping NaN and taking the trailing
    ``window`` ending at ``t`` yields the same window whether computed on the
    full series or on ``series.iloc[:t+1]``.
    """
    if window < 1:
        raise ValueError(f"window ({window}) must be >= 1")
    valid = score.dropna()

    def _rank(w: np.ndarray) -> float:
        return float((w <= w[-1]).mean())

    ranks = valid.rolling(window).apply(_rank, raw=True)
    return ranks.reindex(score.index)


def regime_conditioned_positions(closes: Mapping[str, pd.Series], *,
                                 target: str, signal: str, window: int,
                                 percentile_window: int = PERCENTILE_WINDOW
                                 ) -> pd.Series:
    """Continuous conditioned position ∈ ``[0, 1]`` for ``target``, aligned to
    the target's index.

    The position at bar ``t`` is the CAUSAL rolling-percentile-rank (trailing
    ``percentile_window``) of the raw ``signal`` regime score — exposure scales
    smoothly with how risk-on the regime is relative to its own recent history.
    This is CONTINUOUS conditioning (contrast the burned binary
    ``crossasset_gate``, which switched a component fully on/off on a momentum
    SIGN).

    ``closes`` is a mapping of ALIGNED daily close series (one per ticker) that
    must contain every leg the ``signal`` reads plus ``target``; all share the
    NYSE calendar, so no cross-calendar reindex is performed. Warm-up bars
    (where the score or its trailing-``percentile_window`` rank is undefined)
    resolve to ``0.0`` (flat) — the house "undefined resolves against the
    strategy" convention (as in ``crossasset_gate``) — so the returned series is
    NaN-free and in ``[0, 1]`` on every bar.

    Causality: every input is trailing-only and the normalization is rolling
    (never full-sample), so the position at bar ``t`` depends only on data with
    timestamp ``<= t`` (prefix invariance, pinned by the truncation test). The
    engine delays execution to bar ``t+1``'s open as everywhere else.
    """
    if signal not in REGIME_SIGNALS:
        raise ValueError(
            f"unknown regime signal {signal!r}; expected one of "
            f"{REGIME_SIGNALS}")
    target_index = closes[target].index
    score = regime_score(closes, signal, window)
    ranks = rolling_percentile_rank(score, percentile_window)
    pos = ranks.reindex(target_index).clip(0.0, 1.0).fillna(0.0)
    pos.name = "position"
    return pos
