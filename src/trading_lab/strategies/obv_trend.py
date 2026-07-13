"""OBV trend confirmation: long while on-balance volume sits above its own
trailing SMA — the lab's first VOLUME-based indicator family (Round 6,
R6-A; every prior family reads only price columns).

OBV[t] is the cumulative sum of ``sign(close[t] - close[t-1]) * volume[t]``
(the first bar contributes 0). The long condition is ``OBV > SMA(OBV,
window)``; with ``price_confirm=True`` the long additionally requires
``close > SMA(close, window)`` — volume flow agreeing WITH the price trend.
``price_confirm=False`` is the pure-OBV arm and doubles as the
within-family control (does the volume line add anything beyond a plain
price SMA regime?). All statistics are trailing (cumsum + rolling), so
``positions[t]`` uses only data through bar ``t``. Flat while the SMA
window is warming up.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def obv(ohlcv: pd.DataFrame) -> pd.Series:
    """On-balance volume: cumulative signed volume (first bar contributes
    0 — its close-to-close change is undefined)."""
    sign = np.sign(ohlcv["close"].diff()).fillna(0.0)
    return (sign * ohlcv["volume"]).cumsum()


def generate(ohlcv: pd.DataFrame, window: int = 50,
             price_confirm: bool = False) -> pd.Series:
    if window < 2:
        raise ValueError(f"window ({window}) must be >= 2")
    line = obv(ohlcv)
    line_sma = line.rolling(window).mean()
    long = line > line_sma  # NaN warm-up compares False
    if price_confirm:
        long &= ohlcv["close"] > ohlcv["close"].rolling(window).mean()
    pos = long.astype(float)
    pos[line_sma.isna()] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
