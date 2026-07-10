"""Video interpretation (i): SuperTrend-flip entry, EMA + MACD as filters.

Faithful reading of the DaviddTech video's "SuperTrend Flip EMA MACD"
(docs/research/video-source-2026-07-09.md — exact parameters and trigger/
filter roles are UNSTATED in the source; this module is one flagged
interpretation, competing against ``macd_supertrend`` and the dual-EMA
control):

* ENTER long on the first bar where SuperTrend is bullish AND both filters
  confirm (close above EMA(ema_len), MACD line above its signal line). The
  SuperTrend flip is the trigger; if the filters confirm only after the
  flip while SuperTrend is still bullish, entry happens on that later bar.
* EXIT when SuperTrend flips bearish (signal-close, swing style — the video
  states no take-profit / no stop-loss). Filters are not required to hold.
* Long/flat only — the conservative faithful reading; the transcript never
  states shorts.

Causality: SuperTrend, EMA and MACD recursions are strictly trailing, and
the entry/exit state machine only forward-fills past events, so
positions[t] depends on data through bar t alone (prefix-invariant).
Warm-up (max of ema_len, macd_slow + macd_signal, 4 * st_period bars) is
forced flat: seed-dominated indicator values must not trade.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._supertrend import supertrend_direction


def generate(ohlcv: pd.DataFrame, st_period: int = 10, st_mult: float = 3.0,
             ema_len: int = 200, macd_fast: int = 12, macd_slow: int = 26,
             macd_signal: int = 9) -> pd.Series:
    if macd_fast >= macd_slow:
        raise ValueError(f"macd_fast ({macd_fast}) must be < macd_slow ({macd_slow})")
    if macd_signal < 1:
        raise ValueError(f"macd_signal ({macd_signal}) must be >= 1")
    if ema_len < 1:
        raise ValueError(f"ema_len ({ema_len}) must be >= 1")

    close = ohlcv["close"]
    st_up = supertrend_direction(ohlcv, st_period, st_mult) > 0
    ema = close.ewm(span=ema_len, adjust=False).mean()
    macd_line = (close.ewm(span=macd_fast, adjust=False).mean()
                 - close.ewm(span=macd_slow, adjust=False).mean())
    signal_line = macd_line.ewm(span=macd_signal, adjust=False).mean()

    entry = st_up & (close > ema) & (macd_line > signal_line)
    exit_ = ~st_up

    warmup = min(max(ema_len, macd_slow + macd_signal, 4 * st_period), len(ohlcv))
    entry.iloc[:warmup] = False
    exit_.iloc[:warmup] = False

    state = pd.Series(np.nan, index=ohlcv.index)
    state[entry] = 1.0
    state[exit_] = 0.0
    pos = state.ffill().fillna(0.0)
    pos.name = "position"
    return pos
