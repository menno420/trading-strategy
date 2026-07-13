"""Commodity Channel Index mean-reversion (Round 3 family `cci_reversion`).

Lambert's CCI over the typical price TP = (high + low + close) / 3:
``CCI = (TP - SMA(TP, period)) / (0.015 * MAD(TP, period))`` where MAD is
the mean absolute deviation of TP from that same SMA over the trailing
``period`` window, and 0.015 is Lambert's scaling constant (chosen so
roughly 70-80% of values fall in [−100, 100]).

Signal: go long when CCI crosses UP through ``buy_below`` from oversold
(the recovery confirmation, not the dip itself — the same convention as
the stochastic / Williams %R reversion families), exit when CCI rises
above ``sell_above``; otherwise hold the previous state.

Causality: the rolling SMA/MAD windows are trailing (pandas includes only
data through bar t), so positions[t] uses only data through bar t; the
engine fills at bar t+1's open. Flat while the window is warming up or the
MAD is zero (flat prices give an undefined CCI, treated as no signal). If
the entry cross and the exit level fire on the same bar, the exit wins
(ambiguity resolves against the strategy).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def cci(ohlcv: pd.DataFrame, period: int = 20) -> pd.Series:
    """Lambert CCI; NaN during warm-up or zero mean absolute deviation."""
    tp = (ohlcv["high"] + ohlcv["low"] + ohlcv["close"]) / 3.0
    sma = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(
        lambda w: np.abs(w - w.mean()).mean(), raw=True)
    mad = mad.replace(0.0, np.nan)
    return (tp - sma) / (0.015 * mad)


def generate(ohlcv: pd.DataFrame, period: int = 20, buy_below: float = -100,
             sell_above: float = 100) -> pd.Series:
    if period < 2:
        raise ValueError(f"period ({period}) must be >= 2")
    if not buy_below < 0 <= sell_above:
        raise ValueError(
            f"need buy_below ({buy_below}) < 0 <= sell_above ({sell_above})")
    c = cci(ohlcv, period)
    cross_up = (c >= buy_below) & (c.shift(1) < buy_below)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[cross_up] = 1.0
    raw[c > sell_above] = 0.0  # exit wins if both fire on the same bar
    pos = raw.ffill().fillna(0.0)
    pos[c.isna()] = 0.0  # warm-up / zero-MAD bars: flat
    pos.name = "position"
    return pos
