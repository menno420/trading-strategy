"""Williams %R reversion: go long when %R rises UP through ``buy_below``
from oversold (the recovery confirmation, not the dip itself), exit when %R
rises above ``sell_above``; otherwise hold the previous state.

%R = -100 * (highest high - close) / (highest high - lowest low) over a
trailing ``period`` window, in [-100, 0] (oversold near -100). The rolling
extremes are trailing (pandas includes only data through bar t), so
positions[t] uses only data through bar t. Flat while the window is warming
up or the range is zero (flat prices give an undefined %R, treated as no
signal). If the entry cross and the exit level fire on the same bar, the
exit wins (ambiguity resolves against the strategy).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def williams_r(ohlcv: pd.DataFrame, period: int = 14) -> pd.Series:
    """Williams %R in [-100, 0]; NaN during warm-up or zero range."""
    lowest = ohlcv["low"].rolling(period).min()
    highest = ohlcv["high"].rolling(period).max()
    rng = (highest - lowest).replace(0.0, np.nan)
    return -100.0 * (highest - ohlcv["close"]) / rng


def generate(ohlcv: pd.DataFrame, period: int = 14, buy_below: float = -80,
             sell_above: float = -20) -> pd.Series:
    if period < 2:
        raise ValueError(f"period ({period}) must be >= 2")
    if not -100 < buy_below < sell_above < 0:
        raise ValueError("need -100 < buy_below < sell_above < 0")
    r = williams_r(ohlcv, period)
    cross_up = (r >= buy_below) & (r.shift(1) < buy_below)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[cross_up] = 1.0
    raw[r > sell_above] = 0.0  # exit wins if both fire on the same bar
    pos = raw.ffill().fillna(0.0)
    pos[r.isna()] = 0.0  # warm-up / zero-range bars: flat
    pos.name = "position"
    return pos
