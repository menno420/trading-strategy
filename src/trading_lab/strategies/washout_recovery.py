"""Washout-recovery conjunction family (Round 7C, R7-C).

`generate(ohlcv, W_dd, entry_dd, W_prox, p) -> pd.Series` of target
positions (0/1) indexed like `ohlcv`. Long only when a name is
SIMULTANEOUSLY (a) deep in a long-horizon drawdown from its trailing
W_dd-bar close peak AND (b) reclaiming a short-horizon high -- within
fraction p of its trailing W_prox-bar close-max. A memoryless per-bar
STATE band (no hysteresis): the position at bar t is a pure function of
the last W_dd closes. The engine delays execution to bar t+1 open.

- peak_long[t]  = max(close[t-W_dd+1 .. t])    (long window, incl. t)
- dd_long[t]    = close[t] / peak_long[t] - 1  (<= 0) -> washed out iff dd_long <= -entry_dd
- max_short[t]  = max(close[t-W_prox+1 .. t])  (short window, incl. t) -> recovering iff close >= p * max_short
- long iff washed-out AND recovering; else flat.

Two DISTINCT windows (long W_dd for the big-picture washout, short W_prox
for the local recovery); W_prox < W_dd is required (a single-window
version collapses to a contradiction). Conjunction of R7-A
`drawdown_reversion` and R7-B `high_proximity` on two distinct windows --
a decision surface neither tests alone.
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, W_dd: int = 252, entry_dd: float = 0.10,
             W_prox: int = 63, p: float = 0.95) -> pd.Series:
    if W_dd < 2:
        raise ValueError(f"W_dd ({W_dd}) must be >= 2")
    if W_prox < 2:
        raise ValueError(f"W_prox ({W_prox}) must be >= 2")
    if W_prox >= W_dd:
        raise ValueError(f"W_prox ({W_prox}) must satisfy W_prox < W_dd ({W_dd})")
    if not 0.0 < entry_dd < 1.0:
        raise ValueError(f"entry_dd ({entry_dd}) must satisfy 0 < entry_dd < 1")
    if not 0.0 < p <= 1.0:
        raise ValueError(f"p ({p}) must satisfy 0 < p <= 1")
    close = ohlcv["close"]
    peak_long = close.rolling(W_dd).max()
    dd_long = close / peak_long - 1.0
    max_short = close.rolling(W_prox).max()
    washed_out = dd_long <= -entry_dd
    recovering = close >= p * max_short
    pos = (washed_out & recovering).astype(float)
    pos[peak_long.isna()] = 0.0  # warm-up: long window not full -> flat
    pos = pos.fillna(0.0)
    pos.name = "position"
    return pos
