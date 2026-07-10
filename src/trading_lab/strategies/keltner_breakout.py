"""Keltner-channel breakout (Round 2 family `keltner_breakout`).

Long when ``close > EMA(n) + m * ATR(n)``; exit (flat) when
``close < EMA(n)``. Long/flat (docs/research-round-2.md §3b). Between the
two triggers (EMA <= close <= EMA + m*ATR) the position is held — the
registered rules name only an entry and an exit, so the state machine
forward-fills the last confirmed state.

Conventions (ambiguities resolved AGAINST the strategy per pre-reg §6, and
recorded in docs/research-round-2-results.md):

* EMA is recursive smoothing ``ewm(span=n, adjust=False)`` — the repo-wide
  EMA convention (ema_crossover, macd).
* ATR is Wilder's ATR (``ewm(alpha=1/n, adjust=False)`` over true range) —
  the repo's shared :func:`~trading_lab.strategies._supertrend.wilder_atr`.
* Warm-up: the first ``n`` bars are forced flat and cannot trigger an entry
  (EMA/ATR seeds dominate there); a breakout cannot be confirmed before the
  indicators have seen a full window.
* Ties: entry requires a strict ``>`` — ``close == EMA + m*ATR`` is not a
  breakout (flat). The exit's strict ``<`` is the registered rule verbatim.

Causality: EMA and Wilder ATR recursions are strictly trailing and the
state machine only forward-fills past events, so positions[t] depends on
data through bar t alone (prefix-invariant); the engine fills at bar t+1's
open.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._supertrend import wilder_atr


def generate(ohlcv: pd.DataFrame, n: int = 20, m: float = 2.0) -> pd.Series:
    if n < 2:
        raise ValueError(f"n ({n}) must be >= 2")
    if m <= 0:
        raise ValueError(f"m ({m}) must be > 0")
    close = ohlcv["close"]
    ema = close.ewm(span=n, adjust=False).mean()
    atr = wilder_atr(ohlcv, n)
    upper = ema + m * atr

    # ATR >= 0 so upper >= ema: entry (close > upper) and exit (close < ema)
    # can never both fire on one bar.
    entry = close > upper
    exit_ = close < ema

    warmup = min(n, len(ohlcv))
    entry.iloc[:warmup] = False

    state = pd.Series(np.nan, index=ohlcv.index)
    state[entry] = 1.0
    state[exit_] = 0.0
    pos = state.ffill().fillna(0.0)
    pos.iloc[:warmup] = 0.0
    pos.name = "position"
    return pos
