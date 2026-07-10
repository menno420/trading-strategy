"""Short-horizon pullback reversion: buy the dip, sell the recovery.

Entry: today's close breaks below the lowest close of the *previous*
``entry_lookback`` bars (a fresh short-horizon low). With ``trend_len > 0``
the entry is additionally gated by a long-term trend filter — close must be
above its ``trend_len``-bar SMA ("buy the dip in an uptrend"); ``trend_len=0``
disables the filter.

Exit: close recovers above its trailing ``exit_len``-bar SMA (the
mean-reversion target). Exits are never gated by the trend filter.

All indicators are trailing (rolling windows plus a one-bar shift for the
entry channel), so positions[t] uses only data through bar t. Flat during
warm-up.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(ohlcv: pd.DataFrame, entry_lookback: int = 5, exit_len: int = 5,
             trend_len: int = 200) -> pd.Series:
    if entry_lookback < 2:
        raise ValueError(f"entry_lookback ({entry_lookback}) must be >= 2")
    if exit_len < 2:
        raise ValueError(f"exit_len ({exit_len}) must be >= 2")
    if trend_len < 0:
        raise ValueError(f"trend_len ({trend_len}) must be >= 0")
    close = ohlcv["close"]
    prior_low = close.rolling(entry_lookback).min().shift(1)
    entry = close < prior_low
    if trend_len > 0:
        trend_sma = close.rolling(trend_len).mean()
        entry &= close > trend_sma
    else:
        trend_sma = pd.Series(0.0, index=ohlcv.index)  # never NaN, no gate
    exit_sma = close.rolling(exit_len).mean()
    exit_ = close > exit_sma

    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[exit_] = 0.0
    raw[entry] = 1.0  # entry wins on the (impossible for exit_len>=2) overlap
    pos = raw.ffill().fillna(0.0)
    pos[prior_low.isna() | exit_sma.isna() | trend_sma.isna()] = 0.0  # warm-up
    pos.name = "position"
    return pos
