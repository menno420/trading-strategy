"""SMA crossover: long while the fast SMA is above the slow SMA, else flat.

Rolling means use only data through bar t (pandas rolling windows are
trailing), so positions[t] is known at bar t's close; the engine fills at
bar t+1's open. Bars before the slow window is full are flat.
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.Series:
    if fast >= slow:
        raise ValueError(f"fast ({fast}) must be < slow ({slow})")
    close = ohlcv["close"]
    fast_sma = close.rolling(fast).mean()
    slow_sma = close.rolling(slow).mean()
    pos = (fast_sma > slow_sma).astype(float)
    pos[slow_sma.isna()] = 0.0
    pos.name = "position"
    return pos
