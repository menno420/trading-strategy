"""Causal multi-timeframe (MTF) helpers for a DEV-ONLY, research-only
Bollinger mean-reversion exploration.

Nothing in here fetches data, touches a broker, or reads the locked holdout.
It only reshapes and aligns already-loaded, dev-window OHLCV frames.

Three primitives, all strictly causal:

* :func:`resample_ohlcv` — aggregate a finer OHLCV frame up to a coarser bar
  (hourly -> "2h"/"4h"/"6h", daily -> "W"/"ME"). Each coarse bar is stamped at
  its CLOSE timestamp (``closed="right", label="right"``) so a bar's index
  label is the instant its information first becomes known.
* :func:`boll_z` — causal rolling Bollinger z-score, mirroring
  :mod:`trading_lab.strategies.bollinger_reversion` (trailing mean/std, NaN
  during warm-up, 0 where std == 0).
* :func:`align_higher_to_lower` — project a coarse-timeframe series onto a fine
  timeframe timeline with NO LOOKAHEAD. The coarse series is lagged by one
  coarse bar before a strictly-``<=`` forward fill, so a fine bar can only ever
  see a coarse value whose close timestamp is strictly earlier than the fine
  bar's own timestamp. This is deliberately one coarse bar MORE conservative
  than the theoretical minimum — it can never leak.

Stamping-convention note (honest): the cached native hourly/daily bars follow
the harness convention already baked into ``trading_lab.engine`` (a decision
made from data through bar ``t``'s close executes at bar ``t+1``'s open). We
stamp resampled coarse bars at their right (close) edge. Combined with the
one-coarse-bar lag in :func:`align_higher_to_lower`, the alignment is
conservative regardless of the finer frame's stamping quirks: it errs toward
using STALER coarse information, never fresher.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

_OHLCV_AGG = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


def resample_ohlcv(ohlcv: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample a finer OHLCV frame up to the coarser ``rule``.

    open=first, high=max, low=min, close=last, volume=sum. Bins are closed and
    labelled on the RIGHT, so each coarse bar's index is its close timestamp.
    Empty bins (e.g. overnight gaps for intraday rules) are dropped.

    Only coarsening is supported/meaningful — the caller must pass a ``rule``
    at least as coarse as the input's native spacing (the finest cached bar is
    hourly; there is no sub-hourly data).
    """
    if not isinstance(ohlcv.index, pd.DatetimeIndex):
        raise TypeError("resample_ohlcv requires a DatetimeIndex")
    cols = [c for c in _OHLCV_AGG if c in ohlcv.columns]
    out = ohlcv[cols].resample(rule, closed="right", label="right").agg(
        {c: _OHLCV_AGG[c] for c in cols}
    )
    # Drop empty bins: any bin with no underlying bar has NaN OHLC.
    price_cols = [c for c in ("open", "high", "low", "close") if c in out.columns]
    out = out.dropna(subset=price_cols)
    out.index.name = ohlcv.index.name or "timestamp"
    return out


def boll_z(close: pd.Series, lookback: int, ddof: int = 0) -> pd.Series:
    """Causal rolling Bollinger z-score = (close - mean) / std over ``lookback``.

    Trailing window (data through bar ``t`` only). NaN during the warm-up
    window; 0.0 where the rolling std is exactly zero (undefined z, treated as
    "no stretch"). Mirrors ``strategies.bollinger_reversion``.
    """
    if lookback < 2:
        raise ValueError(f"lookback ({lookback}) must be >= 2")
    mean = close.rolling(lookback).mean()
    std = close.rolling(lookback).std(ddof=ddof)
    z = (close - mean) / std.replace(0.0, np.nan)
    # std == 0 (flat prices) after warm-up -> no stretch, z = 0.
    z = z.mask((std == 0.0) & mean.notna(), 0.0)
    # warm-up bars stay NaN (mean is NaN there).
    z = z.where(mean.notna(), np.nan)
    z.name = "z"
    return z


def align_higher_to_lower(higher_series: pd.Series,
                          lower_index: pd.Index) -> pd.Series:
    """Map a coarse-timeframe series onto a fine-timeframe index, no lookahead.

    At fine bar ``t`` the returned value is the coarse observation from the bar
    BEFORE the most recent coarse bar whose close timestamp is ``<= t``. The
    extra one-coarse-bar lag is a deliberate guard against same-timestamp
    lookahead (a coarse bar stamped exactly at ``t`` closed simultaneously with
    the fine bar and must not be treated as known when acting at ``t``).

    Guarantees, asserted at runtime:

    * both indexes are monotonically increasing;
    * every fine bar's assigned value originates from a coarse bar whose
      timestamp is strictly ``< t`` (never ``>= t``).
    """
    if not isinstance(higher_series, pd.Series):
        raise TypeError("higher_series must be a Series")
    lower_index = pd.DatetimeIndex(lower_index)
    if not higher_series.index.is_monotonic_increasing:
        raise AssertionError("higher_series index must be monotonic increasing")
    if not lower_index.is_monotonic_increasing:
        raise AssertionError("lower_index must be monotonic increasing")
    higher = higher_series

    # Lag by one coarse bar: value stamped at coarse ts c_i becomes the value
    # from c_{i-1}. The FIRST coarse bar has no predecessor -> NaN (unknown).
    lagged = higher.shift(1)

    # Forward-fill the lagged coarse series onto the fine timeline using only
    # coarse timestamps <= t (reindex+ffill over the index union).
    union = lagged.index.union(lower_index)
    aligned = lagged.reindex(union).ffill().reindex(lower_index)
    aligned.name = higher_series.name

    # --- No-lookahead assertion -------------------------------------------
    # For each fine bar t, identify the coarse SOURCE timestamp actually used
    # and assert it is strictly earlier than t. The source is the coarse bar
    # before the most recent coarse close <= t.
    src_pos = higher.index.searchsorted(lower_index, side="right") - 1  # most recent <= t
    src_pos = src_pos - 1  # the one-bar lag
    for t, p, val in zip(lower_index, src_pos, aligned.to_numpy()):
        if pd.isna(val):
            continue
        if p < 0:
            raise AssertionError(
                f"aligned value at {t} has no valid predecessor coarse bar")
        src_ts = higher.index[p]
        if not (src_ts < t):
            raise AssertionError(
                f"LOOKAHEAD: fine bar {t} uses coarse bar {src_ts} (>= t)")
    return aligned


# ---------------------------------------------------------------------------
# Annualization for resampled / native timeframes (dev-only convenience).
# Native hourly = 6.5 regular-session hours/day -> 252*6.5 = 1638 bars/yr.
# Intraday rules scale that by hours-per-bar; coarser rules by trading count.
# ---------------------------------------------------------------------------
_HOURLY_PPY = 252.0 * 6.5

PERIODS_PER_YEAR = {
    "hourly": _HOURLY_PPY,
    "1h": _HOURLY_PPY,
    "2h": _HOURLY_PPY / 2.0,
    "3h": _HOURLY_PPY / 3.0,
    "4h": _HOURLY_PPY / 4.0,
    "6h": _HOURLY_PPY / 6.0,
    "daily": 252.0,
    "1d": 252.0,
    "W": 52.0,
    "weekly": 52.0,
    "ME": 12.0,
    "monthly": 12.0,
}


def periods_per_year(tf: str) -> float:
    """Bars/year for a native or resampled timeframe label (dev-only)."""
    if tf not in PERIODS_PER_YEAR:
        raise ValueError(f"unknown timeframe/rule {tf!r}")
    return PERIODS_PER_YEAR[tf]


if __name__ == "__main__":
    # Runnable causal self-check (no data files needed).
    # 1) resample aggregation on a tiny synthetic hourly frame.
    idx = pd.date_range("2024-01-01 10:00", periods=6, freq="1h")
    df = pd.DataFrame({
        "open": [1, 2, 3, 4, 5, 6],
        "high": [2, 3, 4, 5, 6, 7],
        "low": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
        "close": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        "volume": [10, 10, 10, 10, 10, 10],
    }, index=idx)
    r = resample_ohlcv(df, "3h")
    print("resample 3h:\n", r)

    # 2) explicit no-lookahead demonstration: a naive ffill WOULD leak.
    coarse = pd.Series([10.0, 20.0, 30.0],
                       index=pd.to_datetime(
                           ["2024-01-01 12:00", "2024-01-01 15:00",
                            "2024-01-01 18:00"]), name="z_h")
    fine_idx = pd.date_range("2024-01-01 12:00", "2024-01-01 18:00", freq="1h")
    aligned = align_higher_to_lower(coarse, fine_idx)
    naive = coarse.reindex(coarse.index.union(fine_idx)).ffill().reindex(fine_idx)
    print("\nfine_idx     naive_ffill   causal_aligned")
    for t in fine_idx:
        print(t, float(naive.loc[t]) if pd.notna(naive.loc[t]) else None,
              float(aligned.loc[t]) if pd.notna(aligned.loc[t]) else None)
    # At 12:00 the naive ffill already exposes the coarse bar stamped 12:00
    # (its close == the fine bar's timestamp) -> leak. The causal version is
    # NaN there (no strictly-earlier coarse bar yet).
    assert pd.isna(aligned.loc[fine_idx[0]]), "expected NaN at first fine bar"
    assert naive.loc[fine_idx[0]] == 10.0, "naive ffill should leak here"
    print("\nOK: causal alignment does not leak future coarse info.")
