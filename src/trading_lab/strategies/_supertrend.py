"""SuperTrend indicator (shared helper, not a strategy itself).

Standard construction: ATR uses Wilder's smoothing
(``ewm(alpha=1/period, adjust=False)``); basic bands are
``hl2 ± mult * ATR``; final bands ratchet (the upper band only moves down
while price stays below it, the lower band only moves up while price stays
above it); the direction flips bullish when the close crosses above the
final upper band and bearish when it crosses below the final lower band.

Causality: every recursion uses only values through the current bar —
``direction[t]`` depends on OHLC data through bar ``t`` alone, so the
prefix-invariance test holds exactly. The seed direction is bearish (-1);
callers force a warm-up window flat so the seed never trades.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def wilder_atr(ohlcv: pd.DataFrame, period: int) -> pd.Series:
    """Average True Range with Wilder's recursive smoothing."""
    if period < 1:
        raise ValueError(f"st_period ({period}) must be >= 1")
    high, low, close = ohlcv["high"], ohlcv["low"], ohlcv["close"]
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(),
                    (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / period, adjust=False).mean()


def supertrend_direction(ohlcv: pd.DataFrame, period: int = 10,
                         mult: float = 3.0) -> pd.Series:
    """SuperTrend direction: +1 while bullish, -1 while bearish."""
    if mult <= 0:
        raise ValueError(f"st_mult ({mult}) must be > 0")
    atr = wilder_atr(ohlcv, period).to_numpy()
    hl2 = ((ohlcv["high"] + ohlcv["low"]) / 2.0).to_numpy()
    close = ohlcv["close"].to_numpy(dtype=float)
    upper_basic = hl2 + mult * atr
    lower_basic = hl2 - mult * atr

    n = len(close)
    upper = np.empty(n)
    lower = np.empty(n)
    direction = np.empty(n)
    if n == 0:
        return pd.Series(direction, index=ohlcv.index, name="st_direction")
    upper[0], lower[0], direction[0] = upper_basic[0], lower_basic[0], -1.0
    for i in range(1, n):
        upper[i] = (upper_basic[i]
                    if upper_basic[i] < upper[i - 1] or close[i - 1] > upper[i - 1]
                    else upper[i - 1])
        lower[i] = (lower_basic[i]
                    if lower_basic[i] > lower[i - 1] or close[i - 1] < lower[i - 1]
                    else lower[i - 1])
        if direction[i - 1] < 0:
            direction[i] = 1.0 if close[i] > upper[i] else -1.0
        else:
            direction[i] = -1.0 if close[i] < lower[i] else 1.0
    return pd.Series(direction, index=ohlcv.index, name="st_direction")
