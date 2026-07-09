#!/usr/bin/env python3
"""Regenerate the committed synthetic fixture data (deterministic, seeded).

Usage: python3 tests/fixtures/make_fixtures.py

The TEST daily series intentionally spans the HOLDOUT_START boundary
(2025-01-09) so the holdout-lock tests exercise real filtering.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from trading_lab.data import save_cache  # noqa: E402

FIXTURES = Path(__file__).resolve().parent


def synth_ohlcv(index: pd.DatetimeIndex, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = len(index)
    ret = rng.normal(0.0003, 0.015, n)
    close = 100.0 * np.exp(np.cumsum(ret))
    open_ = np.empty(n)
    open_[0] = 100.0
    open_[1:] = close[:-1] * np.exp(rng.normal(0, 0.003, n - 1))
    high = np.maximum(open_, close) * np.exp(np.abs(rng.normal(0, 0.004, n)))
    low = np.minimum(open_, close) * np.exp(-np.abs(rng.normal(0, 0.004, n)))
    volume = rng.integers(1_000_000, 5_000_000, n).astype(float)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )


def main() -> None:
    # Daily fixture spanning the holdout boundary (2024-06-03 .. 2025-06-30).
    idx = pd.bdate_range("2024-06-03", "2025-06-30")
    df = synth_ohlcv(idx, seed=42)
    df.index.name = "timestamp"
    print(save_cache(df, "TEST", "daily", data_dir=FIXTURES), len(df))

    # Hourly fixture, pre-holdout only (tz-naive UTC timestamps).
    hidx = pd.date_range("2024-09-02 13:30", periods=400, freq="h")
    hdf = synth_ohlcv(hidx, seed=7)
    hdf.index.name = "timestamp"
    print(save_cache(hdf, "TEST", "hourly", data_dir=FIXTURES), len(hdf))


if __name__ == "__main__":
    main()
