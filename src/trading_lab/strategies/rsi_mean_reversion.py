"""RSI mean-reversion: go long when RSI drops below ``oversold``, exit when
RSI rises above ``overbought``; otherwise hold the previous state.

RSI uses Wilder's smoothing (EWM with alpha = 1/period) over close-to-close
changes — strictly trailing, so positions[t] uses only data through bar t.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    out = 100.0 - 100.0 / (1.0 + rs)
    # avg_loss == 0 -> all gains -> RSI 100 (rs is inf, handled fine), but
    # 0/0 (flat prices) yields NaN; treat as neutral 50.
    out = out.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)
    return out


def generate(ohlcv: pd.DataFrame, period: int = 14, oversold: float = 30,
             overbought: float = 70) -> pd.Series:
    if not 0 < oversold < overbought < 100:
        raise ValueError("need 0 < oversold < overbought < 100")
    r = rsi(ohlcv["close"], period)
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[r < oversold] = 1.0
    raw[r > overbought] = 0.0
    pos = raw.ffill().fillna(0.0)
    pos[r.isna()] = 0.0  # warm-up period: flat
    pos.name = "position"
    return pos
