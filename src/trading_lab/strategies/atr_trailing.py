"""ATR trailing-stop trend follower (Round 3 slice 6 family `atr_trailing`,
chandelier-style).

Entry: go long when the close breaks above the highest HIGH of the previous
``entry_lookback`` bars (Donchian-style channel, SHIFTED BY ONE BAR so bar
t's own high never triggers its own breakout — the merged `donchian`
convention verbatim). Exit: flat when the close falls below the chandelier
stop ``highest close since entry - k * ATR(atr_period)`` (Wilder ATR, the
repo's shared :func:`~trading_lab.strategies._supertrend.wilder_atr`). The
stop only ever ratchets UP while the trade's highest close rises; the ATR
term still breathes with volatility, which is the chandelier design.

This is the lab's first stateful trailing-stop exit: unlike the fixed
channels/bands of `donchian` / `keltner_breakout` / `bollinger_breakout`,
the exit level depends on the entry time (highest close SINCE ENTRY), so
positions are computed with an explicit state loop rather than a
vectorized ffill.

Conventions (ambiguities resolved AGAINST the strategy, keltner_breakout
precedent):

* Ties: entry requires a strict ``>`` (close equal to the channel is not a
  breakout); exit requires a strict ``<`` (close sitting exactly on the
  stop holds the position).
* On the entry bar the trade's highest close is that bar's close, so the
  stop (``close - k*ATR``) cannot fire on the same bar (ATR >= 0, k > 0).
* Warm-up: no entry before ``max(entry_lookback, atr_period)`` bars — the
  entry channel needs a full window (and one shift bar) and the Wilder ATR
  recursion is seed-dominated before ``atr_period`` bars (the
  keltner_breakout warm-up rule).
* Re-entry after a stop-out requires a fresh channel breakout; the rolling
  channel keeps including the bars of the previous trade, so a stopped-out
  trend must reclaim its recent ``entry_lookback``-bar high first.

Causality: the channel is shifted, the ATR recursion is strictly trailing,
and the loop's state at bar t is built from closes at bars <= t only, so
positions[t] depends on data through bar t alone (prefix-invariant); the
engine fills at bar t+1's open.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._supertrend import wilder_atr


def generate(ohlcv: pd.DataFrame, entry_lookback: int = 20,
             atr_period: int = 14, k: float = 3.0) -> pd.Series:
    if entry_lookback < 2:
        raise ValueError(f"entry_lookback ({entry_lookback}) must be >= 2")
    if atr_period < 2:
        raise ValueError(f"atr_period ({atr_period}) must be >= 2")
    if k <= 0:
        raise ValueError(f"k ({k}) must be > 0")
    close = ohlcv["close"].to_numpy(dtype=float)
    upper = (ohlcv["high"].rolling(entry_lookback).max().shift(1)
             .to_numpy(dtype=float))
    atr = wilder_atr(ohlcv, atr_period).to_numpy(dtype=float)

    n = len(ohlcv)
    warmup = min(max(entry_lookback, atr_period), n)
    pos = np.zeros(n)
    in_pos = False
    highest = np.nan
    for t in range(warmup, n):
        if not in_pos:
            if close[t] > upper[t]:  # NaN channel compares False: no entry
                in_pos = True
                highest = close[t]
        else:
            highest = max(highest, close[t])
            if close[t] < highest - k * atr[t]:
                in_pos = False
        pos[t] = 1.0 if in_pos else 0.0
    return pd.Series(pos, index=ohlcv.index, name="position")
