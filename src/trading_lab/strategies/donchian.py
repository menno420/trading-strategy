"""Donchian channel breakout (turtle-style): go long when the close breaks
above the highest high of the previous ``entry`` bars; exit when the close
breaks below the lowest low of the previous ``exit`` bars; otherwise hold the
previous state.

Channels are rolling extremes SHIFTED BY ONE BAR — the channel bar t is
compared against is built from bars [t-entry, t-1], so bar t's own high/low
never triggers its own breakout and positions[t] uses only data through bar t
(prefix-invariant). Bars before the entry channel is full are flat.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(ohlcv: pd.DataFrame, entry: int = 20, exit: int = 10) -> pd.Series:
    if entry < 2:
        raise ValueError(f"entry ({entry}) must be >= 2")
    if not 1 <= exit <= entry:
        raise ValueError(f"exit ({exit}) must satisfy 1 <= exit <= entry ({entry})")
    close = ohlcv["close"]
    upper = ohlcv["high"].rolling(entry).max().shift(1)
    lower = ohlcv["low"].rolling(exit).min().shift(1)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[close < lower] = 0.0
    raw[close > upper] = 1.0  # entry wins if both fire (upper >= lower always)
    pos = raw.ffill().fillna(0.0)
    pos[upper.isna()] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
