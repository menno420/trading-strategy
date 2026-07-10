"""Volatility-filtered SMA crossover (Round 2 family `vol_filtered_trend`).

SMA(fast, slow) crossover, long/flat, gated by a realized-volatility regime
filter (docs/research-round-2.md §3a): the long signal is valid only when
the ``vol_window``-bar realized volatility (std of close-to-close returns)
is strictly **below** its trailing ``med_window``-bar median — calm-regime
trend. ``vol_filter=False`` disables the gate and reduces to the plain
crossover (the within-family baseline arm).

Causality: rolling means/std/median are all trailing (data through bar t
only), so positions[t] is known at bar t's close; the engine fills at bar
t+1's open. Bars where the slow SMA is not yet defined are flat. With the
filter on, bars where the vol or its median is not yet defined are ALSO
flat — the calm regime cannot be confirmed, so ambiguity resolves against
the strategy (pre-registration §6). Ties (vol == median) are "not below"
and stay flat, same resolution.

The window lengths (20 / 252) are frozen by the pre-registration and are
NOT swept; they are parameters here only so unit tests can exercise the
filter on short synthetic series.
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, fast: int = 20, slow: int = 50,
             vol_filter: bool = True, vol_window: int = 20,
             med_window: int = 252) -> pd.Series:
    if fast >= slow:
        raise ValueError(f"fast ({fast}) must be < slow ({slow})")
    if vol_window < 2:
        raise ValueError(f"vol_window ({vol_window}) must be >= 2")
    if med_window < 2:
        raise ValueError(f"med_window ({med_window}) must be >= 2")
    close = ohlcv["close"]
    fast_sma = close.rolling(fast).mean()
    slow_sma = close.rolling(slow).mean()
    trend = fast_sma > slow_sma

    if vol_filter:
        vol = close.pct_change().rolling(vol_window).std()
        vol_med = vol.rolling(med_window).median()
        # NaN vol/median compares False -> flat until both are defined.
        calm = vol < vol_med
        pos = (trend & calm).astype(float)
    else:
        pos = trend.astype(float)

    pos[slow_sma.isna()] = 0.0
    pos.name = "position"
    return pos
