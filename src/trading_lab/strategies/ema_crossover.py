"""EMA crossover: long while the fast EMA is above the slow EMA, else flat.

EMAs use recursive smoothing (``ewm(span=..., adjust=False)``), which is
strictly trailing: positions[t] depends only on closes through bar t, so the
prefix-invariance causality test holds exactly. Bars before the slow span has
seen a full window of data are forced flat (EMA warm-up values are dominated
by the seed price and are not meaningful crossover signals).
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.Series:
    if fast >= slow:
        raise ValueError(f"fast ({fast}) must be < slow ({slow})")
    close = ohlcv["close"]
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    pos = (fast_ema > slow_ema).astype(float)
    pos.iloc[: min(slow, len(pos))] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
