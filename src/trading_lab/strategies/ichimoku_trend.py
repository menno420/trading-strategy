"""Ichimoku cloud trend-following (Round 3 slice 8 family `ichimoku_trend`).

Standard Ichimoku Kinko Hyo components (Hosoda), each a rolling
high/low midpoint:

* tenkan-sen (conversion) = (HH + LL) / 2 over ``tenkan`` bars,
* kijun-sen (base)        = (HH + LL) / 2 over ``kijun`` bars,
* senkou span A = (tenkan-sen + kijun-sen) / 2, displaced FORWARD
  ``displacement`` bars,
* senkou span B = (HH + LL) / 2 over ``senkou_b`` bars, displaced FORWARD
  ``displacement`` bars.

The cloud (kumo) at bar t is the band between span A and span B **as
displaced**: both spans are shifted forward the standard 26 bars
(``.shift(displacement)`` on a trailing series), so the cloud value AT bar
t derives from bars ≤ t − displacement — strictly past data, no lookahead.
(The chikou span, which needs FUTURE bars to evaluate at t, is deliberately
omitted.) ``displacement`` is frozen at the standard 26 and NOT swept
(mirroring the frozen stochastic ``d_period`` / ADX period conventions).

Committed signal semantic: LONG when the close is strictly above the cloud
top (above BOTH spans) AND tenkan-sen is strictly above kijun-sen (the
classic bullish confirmation). Committed exit (documented, resolves
ambiguity against the strategy): FLAT when the close falls strictly below
the cloud BOTTOM (below both spans — a full cloud break, not merely
entering the cloud) OR tenkan-sen falls strictly below kijun-sen; anything
in between — close inside the cloud, or resting exactly on a span, or
tenkan == kijun — holds the previous state (hysteresis). Entry and exit
cannot both fire on one bar (entry requires close > top and tenkan >
kijun; exit requires close < bottom ≤ top or tenkan < kijun — disjoint),
so no tie-break is needed; boundary ties trigger neither and resolve
against a NEW entry.

Causality: rolling max/min windows are trailing (pandas includes only data
through bar t) and the displacement shift only moves PAST values forward,
so positions[t] uses only data through bar t (prefix-invariant); the
engine fills at bar t+1's open. Flat while any component is warming up
(tenkan/kijun/senkou windows or the displaced spans undefined — an
unconfirmable trend state resolves against the strategy).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _midpoint(ohlcv: pd.DataFrame, window: int) -> pd.Series:
    return (ohlcv["high"].rolling(window).max()
            + ohlcv["low"].rolling(window).min()) / 2.0


def ichimoku(ohlcv: pd.DataFrame, tenkan: int = 9, kijun: int = 26,
             senkou_b: int = 52, displacement: int = 26) -> pd.DataFrame:
    """Tenkan/kijun lines plus the DISPLACED senkou spans (the cloud as it
    stands at each bar, derived from bars ≤ t − displacement); NaN during
    warm-up."""
    conv = _midpoint(ohlcv, tenkan)
    base = _midpoint(ohlcv, kijun)
    span_a = ((conv + base) / 2.0).shift(displacement)
    span_b = _midpoint(ohlcv, senkou_b).shift(displacement)
    return pd.DataFrame({"tenkan": conv, "kijun": base,
                         "span_a": span_a, "span_b": span_b},
                        index=ohlcv.index)


def generate(ohlcv: pd.DataFrame, tenkan: int = 9, kijun: int = 26,
             senkou_b: int = 52, displacement: int = 26) -> pd.Series:
    if tenkan < 2:
        raise ValueError(f"tenkan ({tenkan}) must be >= 2")
    if not tenkan < kijun < senkou_b:
        raise ValueError(f"need tenkan ({tenkan}) < kijun ({kijun}) "
                         f"< senkou_b ({senkou_b})")
    if displacement < 1:
        raise ValueError(f"displacement ({displacement}) must be >= 1")
    ich = ichimoku(ohlcv, tenkan, kijun, senkou_b, displacement)
    close = ohlcv["close"]
    cloud_top = ich[["span_a", "span_b"]].max(axis=1)
    cloud_bottom = ich[["span_a", "span_b"]].min(axis=1)
    entry = (close > cloud_top) & (ich["tenkan"] > ich["kijun"])
    exit_ = (close < cloud_bottom) | (ich["tenkan"] < ich["kijun"])
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[entry] = 1.0   # disjoint from the exit (see module docstring)
    raw[exit_] = 0.0
    pos = raw.ffill().fillna(0.0)
    pos[ich.isna().any(axis=1)] = 0.0  # warm-up bars: flat
    pos.name = "position"
    return pos
