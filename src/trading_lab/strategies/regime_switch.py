"""Trend-strength regime switch (Round 4 family `regime_switch`, slice R4-D).

Pre-registered in ``docs/research-round-4-plan.md`` § R4-D — Regime-
conditional allocation (with mandatory control arm): condition family
choice on TREND-STRENGTH buckets — the trend component is active in the
strong-trend bucket, a flat or mean-reversion component in the weak
bucket — and grade the conditional allocation head-to-head against an
**unconditional control arm** (the same components, no regime condition).
The motivating round-3 result is PR #92: the vol gate's
``vol_filter=False`` control arm beat the gated arm on all six
instruments, so the control-arm discipline is now mandatory.

Components (FROZEN, not swept — both are committed grid points of the
round-3 sweeps on the R4-D instruments; no new parameter territory):

* trend component: ``ema_crossover(fast=trend_fast, slow=trend_slow)`` —
  the r3-trend-new-tickers grid point (20, 100) by default (PR #90).
* weak component: ``weak_family="reversion"`` uses
  ``rsi_mean_reversion(period=rsi_period, oversold=rsi_oversold,
  overbought=rsi_overbought)`` — the r3-meanrev-new-tickers grid point
  (2, 20, 60) by default (PR #91); ``weak_family="flat"`` holds no
  position in the weak bucket.

Trend-strength metric (the ONLY new logic; both registered by the plan):

* ``metric="adx"`` — Wilder ``ADX(adx_period)`` (reused verbatim from
  :mod:`~.adx_filtered_sma`, the lab's existing ADX).
* ``metric="sma_slope"`` — |relative slope of the 200d SMA|:
  ``abs(SMA(slope_sma) / SMA(slope_sma).shift(slope_horizon) - 1)``,
  with ``slope_sma=200`` and ``slope_horizon=21`` frozen (the "|200d SMA
  slope|" the plan names, measured over ~1 trading month).

Bucketing (tercile thresholds FIXED here, in the grid commit, per the
plan): the metric's trailing percentile rank over the last
``rank_window`` bars (the fraction of that window <= today's value,
current bar included) is cut at the tercile boundaries ``weak_q = 1/3``
and ``strong_q = 2/3``:

* rank >= ``strong_q``  -> STRONG-trend bucket -> trend component;
* rank <= ``weak_q``    -> WEAK-trend bucket   -> weak component;
* middle tercile        -> HOLD the previous bucket (hysteresis — no
  family flip without crossing a tercile boundary).

Warm-up / ambiguity resolve AGAINST the strategy (the
`vol_filtered_trend` convention): bars where the trailing rank is not yet
defined over a FULL window of defined metric values — or where no
strong/weak bucket has ever been assigned (middle tercile from the start)
— are flat.

Control arm (``regime_condition=False``): the SAME components with the
regime condition removed —

* ``weak_family="flat"``      -> the trend component always (the only
  active component, ungated — exactly the vol-gate control structure);
* ``weak_family="reversion"`` -> the equal-weight mean of both
  components, ``0.5 * (trend + reversion)``, always (the R4-C committee
  convention: position = mean of member positions; fractional positions
  are supported natively by the engine).

The control arm never computes the metric: its output is invariant to
``metric`` and ``rank_window`` (pinned by tests). Costs, execution and
rail are identical across arms — the arms differ ONLY in the condition.

Causality: EMAs, Wilder RSI/ADX recursions, rolling SMAs and the trailing
rolling rank all use data through bar t only, so positions[t] is known at
bar t's close; the engine fills at bar t+1's open (prefix invariance
holds exactly).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import ema_crossover, rsi_mean_reversion
from .adx_filtered_sma import adx

METRICS = ("adx", "sma_slope")
WEAK_FAMILIES = ("flat", "reversion")

# Tercile boundaries — FIXED in the grid commit per the R4-D plan.
WEAK_Q = 1.0 / 3.0
STRONG_Q = 2.0 / 3.0


def trend_strength(ohlcv: pd.DataFrame, metric: str = "adx",
                   adx_period: int = 14, slope_sma: int = 200,
                   slope_horizon: int = 21) -> pd.Series:
    """The trend-strength metric series (NaN during warm-up)."""
    if metric == "adx":
        return adx(ohlcv, adx_period)
    if metric == "sma_slope":
        sma = ohlcv["close"].rolling(slope_sma).mean()
        return (sma / sma.shift(slope_horizon) - 1.0).abs()
    raise ValueError(f"metric ({metric!r}) must be one of {METRICS}")


def trailing_rank(series: pd.Series, rank_window: int) -> pd.Series:
    """Trailing percentile rank: fraction of the last ``rank_window``
    values (current bar included) <= the current value. NaN until a FULL
    window of defined metric values exists — an unconfirmable regime
    resolves against the strategy."""
    if rank_window < 2:
        raise ValueError(f"rank_window ({rank_window}) must be >= 2")
    rank = series.rolling(rank_window, min_periods=rank_window).apply(
        lambda w: float(np.mean(w <= w[-1])), raw=True)
    full = (series.notna().astype(float)
            .rolling(rank_window, min_periods=rank_window).sum()
            == rank_window)
    return rank.where(full)


def bucket_assignments(ohlcv: pd.DataFrame, metric: str, rank_window: int,
                       adx_period: int = 14, slope_sma: int = 200,
                       slope_horizon: int = 21) -> pd.Series:
    """Tercile bucket per bar: 1.0 = strong trend, 0.0 = weak trend, NaN =
    undefined (warm-up, or middle tercile before any boundary was
    crossed). Middle-tercile bars HOLD the previous bucket (hysteresis)."""
    rank = trailing_rank(
        trend_strength(ohlcv, metric, adx_period=adx_period,
                       slope_sma=slope_sma, slope_horizon=slope_horizon),
        rank_window)
    bucket = pd.Series(np.nan, index=ohlcv.index)
    bucket[rank >= STRONG_Q] = 1.0
    bucket[rank <= WEAK_Q] = 0.0
    return bucket.ffill()


def generate(ohlcv: pd.DataFrame, metric: str = "adx",
             rank_window: int = 252, weak_family: str = "reversion",
             regime_condition: bool = True,
             trend_fast: int = 20, trend_slow: int = 100,
             rsi_period: int = 2, rsi_oversold: float = 20,
             rsi_overbought: float = 60,
             adx_period: int = 14, slope_sma: int = 200,
             slope_horizon: int = 21) -> pd.Series:
    if metric not in METRICS:
        raise ValueError(f"metric ({metric!r}) must be one of {METRICS}")
    if weak_family not in WEAK_FAMILIES:
        raise ValueError(f"weak_family ({weak_family!r}) must be one of "
                         f"{WEAK_FAMILIES}")
    if rank_window < 2:
        raise ValueError(f"rank_window ({rank_window}) must be >= 2")

    trend_pos = ema_crossover.generate(ohlcv, fast=trend_fast,
                                       slow=trend_slow)
    if weak_family == "reversion":
        weak_pos = rsi_mean_reversion.generate(
            ohlcv, period=rsi_period, oversold=rsi_oversold,
            overbought=rsi_overbought)
    else:
        weak_pos = pd.Series(0.0, index=ohlcv.index)

    if not regime_condition:
        # Unconditional control arm: the same components, NO regime
        # condition — the metric is never computed (invariant to
        # `metric`/`rank_window` by construction).
        if weak_family == "flat":
            pos = trend_pos.copy()
        else:
            pos = 0.5 * (trend_pos + weak_pos)
        pos.name = "position"
        return pos

    bucket = bucket_assignments(ohlcv, metric, rank_window,
                                adx_period=adx_period, slope_sma=slope_sma,
                                slope_horizon=slope_horizon)
    pos = pd.Series(0.0, index=ohlcv.index)
    strong = bucket == 1.0
    weak = bucket == 0.0
    pos[strong] = trend_pos[strong]
    pos[weak] = weak_pos[weak]
    # Undefined regime (bucket NaN) stays flat — ambiguity resolves
    # against the strategy.
    pos.name = "position"
    return pos
