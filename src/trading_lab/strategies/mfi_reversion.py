"""Money Flow Index reversion: go long when MFI rises UP through
``buy_below`` from oversold (the recovery confirmation, not the dip
itself), exit when MFI rises above ``sell_above``; otherwise hold the
previous state. Round 6, R6-A — the volume-weighted sibling of the
existing oscillator-reversion families (RSI / stochastic / Williams %R /
CCI), and the lab's first oscillator to read the volume column.

MFI = 100 * positive_flow / (positive_flow + negative_flow) over a
trailing ``period`` window, in [0, 100] (oversold near 0), where money
flow is typical price ``(high + low + close) / 3`` times volume, split by
the sign of the typical-price change. All rolling sums are trailing
(pandas includes only data through bar t), so ``positions[t]`` uses only
data through bar ``t``. Flat while the window is warming up or total flow
is zero (an undefined MFI is treated as no signal). If the entry cross and
the exit level fire on the same bar, the exit wins (ambiguity resolves
against the strategy).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def mfi(ohlcv: pd.DataFrame, period: int = 14) -> pd.Series:
    """Money Flow Index in [0, 100]; NaN during warm-up or zero flow."""
    tp = (ohlcv["high"] + ohlcv["low"] + ohlcv["close"]) / 3.0
    flow = tp * ohlcv["volume"]
    d = tp.diff()  # first bar NaN -> contributes to neither side
    pos_sum = flow.where(d > 0, 0.0).rolling(period).sum()
    neg_sum = flow.where(d < 0, 0.0).rolling(period).sum()
    total = (pos_sum + neg_sum).replace(0.0, np.nan)
    return 100.0 * pos_sum / total


def generate(ohlcv: pd.DataFrame, period: int = 14, buy_below: float = 20,
             sell_above: float = 80) -> pd.Series:
    if period < 2:
        raise ValueError(f"period ({period}) must be >= 2")
    if not 0 < buy_below < sell_above < 100:
        raise ValueError("need 0 < buy_below < sell_above < 100")
    m = mfi(ohlcv, period)
    cross_up = (m >= buy_below) & (m.shift(1) < buy_below)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[cross_up] = 1.0
    raw[m > sell_above] = 0.0  # exit wins if both fire on the same bar
    pos = raw.ffill().fillna(0.0)
    pos[m.isna()] = 0.0  # warm-up / zero-flow bars: flat
    pos.name = "position"
    return pos
