"""Buy-and-hold: long 1 unit for the whole period (also the benchmark)."""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame) -> pd.Series:
    return pd.Series(1.0, index=ohlcv.index, name="position")
