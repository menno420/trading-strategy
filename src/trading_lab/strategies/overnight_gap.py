"""Overnight-gap family: the lab's first family to use the OPEN column as
a signal input (Round 6, R6-B; execution already fills at next-bar open,
but no prior family's *signal* reads it).

``gap[t] = open[t] - close[t-1]``, measured in trailing-ATR units (Wilder
ATR over ``atr_period`` bars, computed through bar ``t-1``).

* ``mode="fade"``: a DOWN-gap of at least ``gap_atr`` ATRs signals a long
  entry — the overnight-overreaction-reverts thesis.
* ``mode="follow"``: an UP-gap of at least ``gap_atr`` ATRs signals a long
  entry — the overnight-news-drifts thesis.

The position is held for ``hold`` bars starting at the signal bar
(overlapping signals extend the hold). ``positions[t]`` uses ``open[t]``
(known at bar ``t``) and history through ``t-1`` only, so the causality
contract holds; the engine fills at bar ``t+1``'s open, so what is
honestly tested is post-gap drift/reversion over the FOLLOWING bars, never
same-day open-to-close gap capture. Flat while the ATR is warming up or
zero (a gap in units of zero range is undefined, treated as no signal).
"""

from __future__ import annotations

import pandas as pd


def trailing_atr(ohlcv: pd.DataFrame, period: int = 14) -> pd.Series:
    """Wilder ATR through bar t-1 (shifted so bar t never sees its own
    range); NaN on the first bars."""
    prev_close = ohlcv["close"].shift(1)
    tr = pd.concat([
        ohlcv["high"] - ohlcv["low"],
        (ohlcv["high"] - prev_close).abs(),
        (ohlcv["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, adjust=False,
                 min_periods=period).mean()
    return atr.shift(1)


def generate(ohlcv: pd.DataFrame, gap_atr: float = 1.0, hold: int = 3,
             mode: str = "fade", atr_period: int = 14) -> pd.Series:
    if mode not in ("fade", "follow"):
        raise ValueError(f"mode ({mode!r}) must be 'fade' or 'follow'")
    if gap_atr <= 0:
        raise ValueError(f"gap_atr ({gap_atr}) must be > 0")
    if hold < 1:
        raise ValueError(f"hold ({hold}) must be >= 1")
    if atr_period < 2:
        raise ValueError(f"atr_period ({atr_period}) must be >= 2")
    atr = trailing_atr(ohlcv, atr_period)
    gap = ohlcv["open"] - ohlcv["close"].shift(1)
    if mode == "fade":
        sig = gap <= -gap_atr * atr
    else:
        sig = gap >= gap_atr * atr
    sig &= atr.notna() & (atr > 0)  # warm-up / zero-range: no signal
    pos = sig.astype(float).rolling(hold, min_periods=1).max()
    pos.name = "position"
    return pos
