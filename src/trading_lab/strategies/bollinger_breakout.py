"""Bollinger-band BREAKOUT (Round 3 slice 6 family `bollinger_breakout`).

The inverse thesis of the merged `bollinger_reversion`: where the reversion
family buys a close stretched BELOW the lower band and sells the snap-back,
this trend/breakout family goes long when the close crosses ABOVE the upper
band (``close > SMA(period) + num_std * std(period)``) and treats the
strength as the start of a trend, not an anomaly.

Exit semantic (one of the two allowed, committed here and mirrored in the
sweep doc): flat when the close falls below the MIDDLE band
(``close < SMA(period)``) — the direct Bollinger analogue of the merged
``keltner_breakout``'s ``close < EMA(n)`` exit, chosen so the two channel
breakouts differ only in band construction (SMA + k·std vs EMA + m·ATR)
and the comparison across families is clean. Between the two triggers
(SMA <= close <= upper band) the position is held — the rules name only an
entry and an exit, so the state machine forward-fills the last confirmed
state.

Conventions (ambiguities resolved AGAINST the strategy, keltner_breakout
precedent):

* Bands use the trailing rolling mean and population std (``ddof=0``) over
  ``period`` bars — identical math to `bollinger_reversion`'s z-score
  denominator, so the two families disagree only in thesis, never in
  indicator arithmetic.
* Warm-up: flat while the rolling window is incomplete (band is NaN — a
  NaN comparison is False, so no entry can fire there).
* Ties: entry requires a strict ``>`` (``close == upper`` is not a
  breakout) and exit requires a strict ``<``. std >= 0 so upper >= middle:
  entry and exit can never both fire on one bar.

Causality: rolling mean/std are trailing (pandas rolling windows include
only data through bar t) and the state machine only forward-fills past
events, so positions[t] depends on data through bar t alone
(prefix-invariant); the engine fills at bar t+1's open.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate(ohlcv: pd.DataFrame, period: int = 20,
             num_std: float = 2.0) -> pd.Series:
    if period < 2:
        raise ValueError(f"period ({period}) must be >= 2")
    if num_std <= 0:
        raise ValueError(f"num_std ({num_std}) must be > 0")
    close = ohlcv["close"]
    middle = close.rolling(period).mean()
    std = close.rolling(period).std(ddof=0)
    upper = middle + num_std * std

    # std >= 0 so upper >= middle: entry (close > upper) and exit
    # (close < middle) can never both fire on one bar.
    state = pd.Series(np.nan, index=ohlcv.index)
    state[close < middle] = 0.0
    state[close > upper] = 1.0
    pos = state.ffill().fillna(0.0)
    pos[middle.isna()] = 0.0  # warm-up: flat
    pos.name = "position"
    return pos
