"""Video interpretation (ii): MACD-cross entry, SuperTrend + EMA as filters.

The alternate faithful reading of the DaviddTech video's "SuperTrend Flip
EMA MACD" (docs/research/video-source-2026-07-09.md — trigger/filter roles
UNSTATED in the source; this competes against ``supertrend_flip`` and the
dual-EMA control):

* ENTER long when the MACD line crosses above its signal line (an event,
  not a level) AND, on that bar, SuperTrend is bullish and the close is
  above EMA(ema_len). A cross that the filters block is skipped entirely —
  no entry until the next confirmed cross.
* EXIT when the MACD line crosses below its signal line (signal-close,
  swing style — the video states no take-profit / no stop-loss).
* Long/flat only — the conservative faithful reading; the transcript never
  states shorts.

Causality: all indicator recursions are strictly trailing and the state
machine only forward-fills past events, so positions[t] depends on data
through bar t alone (prefix-invariant). Warm-up (max of ema_len,
macd_slow + macd_signal, 4 * st_period bars) is forced flat.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._supertrend import supertrend_direction


def generate(ohlcv: pd.DataFrame, macd_fast: int = 12, macd_slow: int = 26,
             macd_signal: int = 9, st_period: int = 10, st_mult: float = 3.0,
             ema_len: int = 200) -> pd.Series:
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

    above = macd_line > signal_line
    cross_up = above & ~above.shift(1, fill_value=False)
    cross_down = ~above & above.shift(1, fill_value=True)

    entry = cross_up & st_up & (close > ema)
    exit_ = cross_down

    warmup = min(max(ema_len, macd_slow + macd_signal, 4 * st_period), len(ohlcv))
    entry.iloc[:warmup] = False
    exit_.iloc[:warmup] = False

    state = pd.Series(np.nan, index=ohlcv.index)
    state[entry] = 1.0
    state[exit_] = 0.0
    pos = state.ffill().fillna(0.0)
    pos.name = "position"
    return pos
