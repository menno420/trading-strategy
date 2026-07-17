"""High-proximity state family (Round 7, R7-B).

`generate(ohlcv, N, p) -> pd.Series` of target positions (0/1) indexed
like `ohlcv`. Long while the close sits within fraction `p` of its
trailing N-bar close-maximum; flat otherwise. A memoryless per-bar STATE
band (no hysteresis): the position at bar t is a pure function of the last
N closes. The engine delays execution to bar t+1 open.

- trailing_max[t] = max of closes over the trailing N-bar window (incl. t)
- long when close[t] >= p * trailing_max[t], else flat

Because the trailing max includes bar t, the band never exceeds 1.0 and a
fresh high always satisfies it. Nearest burned neighbor:
`donchian`/`channel_breakout` (event-triggered channel CROSS with a
separate exit channel); this is a per-bar state band on CLOSES.
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, N: int = 126, p: float = 0.95) -> pd.Series:
    if N < 2:
        raise ValueError(f"N ({N}) must be >= 2")
    if not 0.0 < p <= 1.0:
        raise ValueError(f"p ({p}) must satisfy 0 < p <= 1")
    close = ohlcv["close"]
    trailing_max = close.rolling(N).max()
    pos = (close >= p * trailing_max).astype(float)
    pos[trailing_max.isna()] = 0.0  # warm-up: flat
    pos = pos.fillna(0.0)
    pos.name = "position"
    return pos
