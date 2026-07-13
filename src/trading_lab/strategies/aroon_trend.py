"""Aroon oscillator trend-following (Round 3 family `aroon_trend`).

Aroon-Up = 100 * (period - bars since the highest high) / period and
Aroon-Down = 100 * (period - bars since the lowest low) / period, each over
a trailing window of ``period + 1`` bars (the standard Chande construction:
"bars since" counts back from the current bar, so an extreme ON the current
bar scores 100 and an extreme ``period`` bars ago scores 0). The oscillator
is Aroon-Up − Aroon-Down in [−100, 100].

Signal: long when the oscillator rises strictly above ``entry``, flat when
it falls strictly below ``exit``; otherwise hold the previous state — the
``exit <= entry`` hysteresis band prevents whipsawing around a single
threshold. ``entry == exit == 0`` collapses to the classic rule "long while
Aroon-Up is above Aroon-Down" (the pure cross), which is the within-family
control arm committed in the declared grid.

Causality: the rolling argmax/argmin windows are trailing (pandas includes
only data through bar t), so positions[t] uses only data through bar t; the
engine fills at bar t+1's open. Flat while the window is warming up (the
oscillator is undefined — an unconfirmable trend state resolves against the
strategy). If the entry and exit conditions could both fire on one bar they
cannot both be true (``exit <= entry`` makes ``osc > entry`` and
``osc < exit`` disjoint), so no tie-break is needed; ``osc == entry`` (or
``== exit``) is "no trigger" and holds the previous state — strict
inequalities resolve boundary ties against a NEW entry.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def aroon(ohlcv: pd.DataFrame, period: int = 25) -> pd.DataFrame:
    """Aroon-Up / Aroon-Down / oscillator, each in the standard range
    ([0, 100] for up/down, [−100, 100] for ``osc``); NaN during warm-up
    (first ``period`` bars)."""
    window = period + 1
    # rolling(...).apply(argmax) returns the offset of the extreme WITHIN
    # the trailing window (0 = oldest bar), so bars-since = period - offset.
    up_off = ohlcv["high"].rolling(window).apply(np.argmax, raw=True)
    down_off = ohlcv["low"].rolling(window).apply(np.argmin, raw=True)
    up = 100.0 * up_off / period
    down = 100.0 * down_off / period
    return pd.DataFrame({"up": up, "down": down, "osc": up - down},
                        index=ohlcv.index)


def generate(ohlcv: pd.DataFrame, period: int = 25, entry: float = 0.0,
             exit: float = 0.0) -> pd.Series:
    if period < 2:
        raise ValueError(f"period ({period}) must be >= 2")
    if not -100 <= exit <= entry <= 100:
        raise ValueError(
            f"need -100 <= exit ({exit}) <= entry ({entry}) <= 100")
    osc = aroon(ohlcv, period)["osc"]
    raw = pd.Series(np.nan, index=ohlcv.index)
    raw[osc > entry] = 1.0   # disjoint from the exit since exit <= entry
    raw[osc < exit] = 0.0
    pos = raw.ffill().fillna(0.0)
    pos[osc.isna()] = 0.0  # warm-up bars: flat
    pos.name = "position"
    return pos
