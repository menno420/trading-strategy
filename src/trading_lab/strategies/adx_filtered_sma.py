"""ADX-filtered SMA crossover (Round 3 family `adx_filtered_sma`).

SMA(fast, slow) crossover, long/flat, gated by a Wilder ADX trending-regime
filter: the long signal is valid only when ``ADX(adx_period)`` is strictly
**above** ``adx_min`` — trend-following only when a trend measurably exists
(the mirror image of `vol_filtered_trend`'s calm-regime gate). This is the
lab's first ADX indicator.

ADX is the standard Wilder construction: directional movement
(+DM = up-move where it exceeds the down-move and is positive, −DM
symmetric), Wilder-smoothed (``ewm(alpha=1/adx_period, adjust=False)``, the
repo's Wilder convention shared with :func:`~._supertrend.wilder_atr`) and
normalised by Wilder ATR into ±DI; DX = 100·|+DI − −DI| / (+DI + −DI); ADX
is the Wilder-smoothed DX. Zero ATR or ±DI summing to zero (flat prices)
gives an undefined DX — treated as no signal.

Causality: SMAs, the DM/DX recursions and the ATR recursion are all
trailing (data through bar t only), so positions[t] is known at bar t's
close; the engine fills at bar t+1's open. Warm-up: bars where the slow SMA
is undefined are flat, and ADX is forced undefined for the first
``2 * adx_period`` bars (the two stacked Wilder recursions' seeds dominate
there) — an unconfirmable trending regime resolves against the strategy,
same convention as `vol_filtered_trend`. Ties (ADX == adx_min) are "not
above" and stay flat.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._supertrend import wilder_atr


def adx(ohlcv: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder ADX in [0, 100]; NaN during warm-up (first ``2 * period``
    bars) or when directional movement is undefined (zero range)."""
    high, low = ohlcv["high"], ohlcv["low"]
    up = high.diff()
    down = -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0),
                        index=ohlcv.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0),
                         index=ohlcv.index)
    atr = wilder_atr(ohlcv, period).replace(0.0, np.nan)
    plus_di = 100.0 * plus_dm.ewm(alpha=1.0 / period,
                                  adjust=False).mean() / atr
    minus_di = 100.0 * minus_dm.ewm(alpha=1.0 / period,
                                    adjust=False).mean() / atr
    di_sum = (plus_di + minus_di).replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    out = dx.ewm(alpha=1.0 / period, adjust=False).mean()
    out.iloc[:min(2 * period, len(out))] = np.nan  # stacked-seed warm-up
    return out


def generate(ohlcv: pd.DataFrame, fast: int = 20, slow: int = 50,
             adx_period: int = 14, adx_min: float = 20.0) -> pd.Series:
    if fast >= slow:
        raise ValueError(f"fast ({fast}) must be < slow ({slow})")
    if adx_period < 2:
        raise ValueError(f"adx_period ({adx_period}) must be >= 2")
    if not 0 <= adx_min < 100:
        raise ValueError(f"adx_min ({adx_min}) must be in [0, 100)")
    close = ohlcv["close"]
    fast_sma = close.rolling(fast).mean()
    slow_sma = close.rolling(slow).mean()
    trend = fast_sma > slow_sma

    # NaN ADX compares False -> flat until the regime is confirmable.
    trending = adx(ohlcv, adx_period) > adx_min
    pos = (trend & trending).astype(float)
    pos[slow_sma.isna()] = 0.0
    pos.name = "position"
    return pos
