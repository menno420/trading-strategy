"""Drawdown-anatomy reversion family (Round 7, R7-A).

`generate(ohlcv, lookback, entry_dd, exit_frac) -> pd.Series` of target
positions (0/1) indexed like `ohlcv`. Long-only reversion on drawdown
STATE (depth from a trailing-window close peak), with a hysteresis exit.

Signal (all causal — the position at bar t reads only closes <= t; the
engine delays execution to bar t+1 open):

- peak[t]  = max of closes over the trailing `lookback` window (incl. t)
- dd[t]    = close[t] / peak[t] - 1        (<= 0)
- enter long when dd[t] <= -entry_dd       (deep enough in drawdown)
- exit (flat) when dd[t] >= -entry_dd * (1 - exit_frac)
                                           (recovered to the exit band;
                                            exit_frac=1.0 => full recovery
                                            to the peak band, threshold 0)
- between the two thresholds the prior state is held (hysteresis).

Nearest burned neighbor: `pullback` (a FIXED-horizon decline event).
Structural difference: this is a normalized depth-from-peak STATE with a
hysteresis exit -- depth-triggered, not duration-triggered.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(ohlcv: pd.DataFrame, lookback: int = 126, entry_dd: float = 0.10,
             exit_frac: float = 1.0) -> pd.Series:
    if lookback < 2:
        raise ValueError(f"lookback ({lookback}) must be >= 2")
    if not 0.0 < entry_dd < 1.0:
        raise ValueError(f"entry_dd ({entry_dd}) must satisfy 0 < entry_dd < 1")
    if not 0.0 < exit_frac <= 1.0:
        raise ValueError(f"exit_frac ({exit_frac}) must satisfy 0 < exit_frac <= 1")
    close = ohlcv["close"]
    peak = close.rolling(lookback).max()
    dd = close / peak - 1.0
    exit_level = -entry_dd * (1.0 - exit_frac)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[dd >= exit_level] = 0.0
    raw[dd <= -entry_dd] = 1.0
    pos = raw.ffill().fillna(0.0)
    pos[peak.isna()] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
