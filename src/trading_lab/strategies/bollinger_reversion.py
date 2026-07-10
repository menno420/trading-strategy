"""Bollinger/z-score reversion: go long when the close's z-score versus its
trailing ``lookback``-bar mean drops below ``-z_entry`` (price stretched below
the lower band), exit when the z-score recovers above ``z_exit``; otherwise
hold the previous state.

The rolling mean/std are trailing (pandas rolling windows include only data
through bar t), so positions[t] uses only data through bar t. Flat while the
rolling window is warming up or the rolling std is zero (flat prices give an
undefined z-score, treated as no signal).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(ohlcv: pd.DataFrame, lookback: int = 20, z_entry: float = 2.0,
             z_exit: float = 0.0) -> pd.Series:
    if lookback < 2:
        raise ValueError(f"lookback ({lookback}) must be >= 2")
    if z_entry <= 0:
        raise ValueError(f"z_entry ({z_entry}) must be > 0")
    if z_exit <= -z_entry:
        raise ValueError(f"z_exit ({z_exit}) must be > -z_entry ({-z_entry})")
    close = ohlcv["close"]
    mean = close.rolling(lookback).mean()
    std = close.rolling(lookback).std(ddof=0)
    z = (close - mean) / std.replace(0.0, np.nan)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[z > z_exit] = 0.0
    raw[z < -z_entry] = 1.0  # entry wins if both fire (cannot, but explicit)
    pos = raw.ffill().fillna(0.0)
    pos[mean.isna()] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
