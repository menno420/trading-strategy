"""Focused causality tests for the DEV-ONLY MTF helpers (trading_lab.mtf)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from trading_lab.mtf import align_higher_to_lower, boll_z, resample_ohlcv


def test_resample_ohlcv_aggregation():
    """OHLC(V) aggregation on a tiny synthetic hourly frame is exact."""
    idx = pd.date_range("2024-01-01 10:00", periods=6, freq="1h")
    df = pd.DataFrame({
        "open": [1.0, 2, 3, 4, 5, 6],
        "high": [2.0, 3, 4, 5, 6, 7],
        "low": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
        "close": [1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        "volume": [10, 11, 12, 13, 14, 15],
    }, index=idx)
    r = resample_ohlcv(df, "3h")

    # closed="right", label="right": first bin covers (09:00, 12:00] = the
    # 10:00 & 11:00 & 12:00 bars, stamped at 12:00.
    assert list(r.index) == [pd.Timestamp("2024-01-01 12:00"),
                             pd.Timestamp("2024-01-01 15:00")]
    b0 = r.loc["2024-01-01 12:00"]
    assert b0["open"] == 1.0          # first
    assert b0["high"] == 4.0          # max of 2,3,4
    assert b0["low"] == 0.5           # min of 0.5,1.5,2.5
    assert b0["close"] == 3.5         # last
    assert b0["volume"] == 33         # 10+11+12
    b1 = r.loc["2024-01-01 15:00"]
    assert b1["open"] == 4.0
    assert b1["high"] == 7.0
    assert b1["close"] == 6.5
    assert b1["volume"] == 42         # 13+14+15


def test_resample_drops_empty_bins():
    """Overnight gaps produce no phantom coarse bars."""
    idx = pd.to_datetime([
        "2024-01-01 14:00", "2024-01-01 15:00",   # day 1
        "2024-01-02 14:00", "2024-01-02 15:00",   # day 2 (18h gap)
    ])
    df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0,
                       "close": 1.0, "volume": 1.0}, index=idx)
    r = resample_ohlcv(df, "4h")
    # Only bins that actually contain bars survive (no NaN OHLC rows).
    assert not r[["open", "high", "low", "close"]].isna().any().any()
    assert len(r) >= 2


def test_boll_z_causal_and_warmup():
    """z-score is trailing, NaN during warm-up, 0 where std == 0."""
    close = pd.Series(np.arange(1, 11, dtype=float),
                      index=pd.date_range("2024-01-01", periods=10, freq="D"))
    z = boll_z(close, lookback=5, ddof=0)
    # first lookback-1 bars are warm-up NaN.
    assert z.iloc[:4].isna().all()
    assert z.iloc[4:].notna().all()
    # A flat window -> std 0 -> z defined as 0.
    flat = pd.Series([5.0] * 6,
                     index=pd.date_range("2024-02-01", periods=6, freq="D"))
    zf = boll_z(flat, lookback=3, ddof=0)
    assert (zf.iloc[2:] == 0.0).all()


def test_boll_z_matches_manual():
    rng = np.random.default_rng(0)
    close = pd.Series(100 + rng.standard_normal(60).cumsum(),
                      index=pd.date_range("2024-01-01", periods=60, freq="D"))
    z = boll_z(close, lookback=20, ddof=0)
    m = close.rolling(20).mean()
    s = close.rolling(20).std(ddof=0)
    expected = (close - m) / s
    pd.testing.assert_series_equal(
        z.dropna(), expected.dropna(), check_names=False)


def test_align_no_lookahead_naive_would_leak():
    """A coarse bar stamped exactly at a fine bar's timestamp must NOT be seen
    at that fine bar. Naive ffill leaks it; the lagged alignment does not."""
    coarse = pd.Series(
        [10.0, 20.0, 30.0],
        index=pd.to_datetime(["2024-01-01 12:00", "2024-01-01 15:00",
                              "2024-01-01 18:00"]), name="z_h")
    fine_idx = pd.date_range("2024-01-01 12:00", "2024-01-01 18:00", freq="1h")

    aligned = align_higher_to_lower(coarse, fine_idx)
    naive = (coarse.reindex(coarse.index.union(fine_idx))
             .ffill().reindex(fine_idx))

    # Naive ffill exposes the 12:00 coarse value AT the 12:00 fine bar (leak).
    assert naive.loc["2024-01-01 12:00"] == 10.0
    # Causal: no strictly-earlier coarse bar exists yet -> NaN.
    assert pd.isna(aligned.loc["2024-01-01 12:00"])
    # At 15:00 the naive sees the simultaneously-closing 15:00 coarse bar (20);
    # causal sees only the 12:00 bar (10) — one full coarse bar staler.
    assert naive.loc["2024-01-01 15:00"] == 20.0
    assert aligned.loc["2024-01-01 15:00"] == 10.0
    # At 18:00 causal sees the 15:00 bar (20), never the simultaneous 30.
    assert aligned.loc["2024-01-01 18:00"] == 20.0

    # Every non-null aligned value must come from a coarse ts strictly < t.
    for t in fine_idx:
        v = aligned.loc[t]
        if pd.isna(v):
            continue
        src_ts = coarse.index[coarse.to_numpy() == v][0]
        assert src_ts < t


def test_align_requires_monotonic():
    bad = pd.Series([1.0, 2.0],
                    index=pd.to_datetime(["2024-01-02", "2024-01-01"]))
    with pytest.raises(AssertionError):
        align_higher_to_lower(bad, pd.date_range("2024-01-01", periods=2))
