"""MACD trend-following: long while the MACD line is above its signal line.

MACD line = EMA(fast) - EMA(slow); signal = EMA(MACD line, span=signal).
All EMAs use recursive smoothing (``ewm(span=..., adjust=False)``) — strictly
trailing, so positions[t] uses only closes through bar t (prefix-invariant).
The first ``slow + signal`` bars are forced flat: until both the slow EMA and
the signal EMA have seen a full window, values are seed-dominated warm-up.
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, fast: int = 12, slow: int = 26,
             signal: int = 9) -> pd.Series:
    if fast >= slow:
        raise ValueError(f"fast ({fast}) must be < slow ({slow})")
    if signal < 1:
        raise ValueError(f"signal ({signal}) must be >= 1")
    close = ohlcv["close"]
    macd_line = (close.ewm(span=fast, adjust=False).mean()
                 - close.ewm(span=slow, adjust=False).mean())
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    pos = (macd_line > signal_line).astype(float)
    pos.iloc[: min(slow + signal, len(pos))] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
