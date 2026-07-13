"""Stochastic %K reversion: go long when the (slow) stochastic %K crosses UP
through ``buy_below`` from oversold (the recovery confirmation, not the dip
itself), exit when %K rises above ``sell_above``; otherwise hold the previous
state.

Raw %K = 100 * (close - lowest low) / (highest high - lowest low) over a
trailing ``k_period`` window; the slow %K signals on is its ``d_period``-bar
SMA (``d_period=1`` recovers the fast oscillator). Rolling windows are
trailing (pandas includes only data through bar t), so positions[t] uses only
data through bar t. Flat while the windows are warming up or the range is
zero (flat prices give an undefined %K, treated as no signal). If the entry
cross and the exit level fire on the same bar, the exit wins (ambiguity
resolves against the strategy).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def stochastic_k(ohlcv: pd.DataFrame, k_period: int = 14,
                 d_period: int = 3) -> pd.Series:
    """Slow stochastic %K in [0, 100]; NaN during warm-up or zero range."""
    lowest = ohlcv["low"].rolling(k_period).min()
    highest = ohlcv["high"].rolling(k_period).max()
    rng = (highest - lowest).replace(0.0, np.nan)
    raw = 100.0 * (ohlcv["close"] - lowest) / rng
    return raw.rolling(d_period).mean()


def generate(ohlcv: pd.DataFrame, k_period: int = 14, d_period: int = 3,
             buy_below: float = 20, sell_above: float = 80) -> pd.Series:
    if k_period < 2:
        raise ValueError(f"k_period ({k_period}) must be >= 2")
    if d_period < 1:
        raise ValueError(f"d_period ({d_period}) must be >= 1")
    if not 0 < buy_below < sell_above < 100:
        raise ValueError("need 0 < buy_below < sell_above < 100")
    k = stochastic_k(ohlcv, k_period, d_period)
    cross_up = (k >= buy_below) & (k.shift(1) < buy_below)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[cross_up] = 1.0
    raw[k > sell_above] = 0.0  # exit wins if both fire on the same bar
    pos = raw.ffill().fillna(0.0)
    pos[k.isna()] = 0.0  # warm-up / zero-range bars: flat
    pos.name = "position"
    return pos
