"""Time-series rate-of-change momentum: go long when the ``lookback``-day
rate of change rises above ``entry`` (strict), exit (flat) when it falls
below ``exit`` (strict); otherwise hold the previous state — the
``exit <= entry`` hysteresis band prevents whipsawing around a single
threshold (``exit == entry`` collapses to the classic single-threshold
time-series momentum rule).

ROC = close / close.shift(lookback) - 1, a trailing transform (data through
bar t only), so positions[t] uses only data through bar t. Flat while the
lookback is warming up (ROC undefined — the momentum state cannot be
confirmed, so ambiguity resolves against the strategy). If the entry and
exit conditions could both fire on one bar they cannot both be true
(``exit <= entry`` makes ``roc > entry`` and ``roc < exit`` disjoint), so
no tie-break is needed; ``roc == entry`` (or ``== exit``) is "no trigger"
and holds the previous state — strict inequalities resolve boundary ties
against a NEW entry.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def rate_of_change(ohlcv: pd.DataFrame, lookback: int = 126) -> pd.Series:
    """Fractional ``lookback``-bar rate of change; NaN during warm-up."""
    close = ohlcv["close"]
    return close / close.shift(lookback) - 1.0


def generate(ohlcv: pd.DataFrame, lookback: int = 126, entry: float = 0.0,
             exit: float = 0.0) -> pd.Series:
    if lookback < 1:
        raise ValueError(f"lookback ({lookback}) must be >= 1")
    if exit > entry:
        raise ValueError(f"exit ({exit}) must be <= entry ({entry})")
    roc = rate_of_change(ohlcv, lookback)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[roc > entry] = 1.0   # disjoint from the exit since exit <= entry
    raw[roc < exit] = 0.0
    pos = raw.ffill().fillna(0.0)
    pos[roc.isna()] = 0.0  # warm-up bars: flat
    pos.name = "position"
    return pos
