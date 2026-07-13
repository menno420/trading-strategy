"""TRIX momentum (Round 3 slice 8 family `trix_momentum`).

TRIX (Hutson) is the 1-bar fractional rate of change of a triple-smoothed
EMA of the close: ``ema3 = EMA(EMA(EMA(close, period), period), period)``,
``trix = ema3 / ema3.shift(1) - 1``. The triple smoothing filters
insignificant price moves; the rate of change turns it into a momentum
oscillator around zero.

Committed signal semantic (the signal-line rule, chosen over the raw
zero-line rule because the extra smoothing on the trigger is the point of
the indicator): long while TRIX is strictly above its signal line
(``EMA(trix, span=signal_period)``), flat while at or below it — the level
rule; a "crosses above / crosses below" formulation produces the identical
position series, since the state between crosses is exactly "which side of
the signal line TRIX is on". ``signal_period == 0`` replaces the signal
line with the constant 0, recovering the classic TRIX ZERO-LINE rule (long
while TRIX > 0) — the within-family control arm committed in the declared
grid per the slice-2 card convention (banded/gated/derived-trigger grids
must include their neutral arm).

Causality: all EMAs are recursive (``ewm(span=..., adjust=False)``),
strictly trailing, and the 1-bar ROC uses ``shift(1)`` — positions[t] uses
only closes through bar t (prefix-invariant); the engine fills at bar
t+1's open. The first ``3 * period + signal_period + 1`` bars are forced
flat: until the three stacked EMAs, the 1-bar shift, and the signal EMA
have each seen a full window, values are seed-dominated warm-up. A
boundary tie (``trix == signal line``, e.g. flat prices where both are 0)
is "not above" and resolves flat — against a NEW entry.
"""

from __future__ import annotations

import pandas as pd


def trix(ohlcv: pd.DataFrame, period: int = 15) -> pd.Series:
    """Fractional TRIX oscillator (triple-EMA 1-bar rate of change); the
    first bar is NaN (undefined ROC), later bars are seed-dominated until
    the stacked EMAs warm up (the caller masks them)."""
    close = ohlcv["close"]
    ema1 = close.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    return ema3 / ema3.shift(1) - 1.0


def generate(ohlcv: pd.DataFrame, period: int = 15,
             signal_period: int = 9) -> pd.Series:
    if period < 2:
        raise ValueError(f"period ({period}) must be >= 2")
    if signal_period < 0:
        raise ValueError(
            f"signal_period ({signal_period}) must be >= 0 (0 = zero-line rule)")
    t = trix(ohlcv, period)
    if signal_period == 0:
        signal_line = pd.Series(0.0, index=ohlcv.index)  # classic zero-line
    else:
        signal_line = t.ewm(span=signal_period, adjust=False).mean()
    pos = (t > signal_line).astype(float)
    warmup = min(3 * period + signal_period + 1, len(pos))
    pos.iloc[:warmup] = 0.0  # warm-up: flat
    pos[t.isna()] = 0.0
    pos.name = "position"
    return pos
