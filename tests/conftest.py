"""Shared test helpers. All tests are OFFLINE: no network, fixtures only."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def make_ohlcv(opens, closes=None, start="2024-01-01", freq="B") -> pd.DataFrame:
    """Toy OHLCV frame from explicit open (and optionally close) prices."""
    opens = np.asarray(opens, dtype=float)
    closes = opens.copy() if closes is None else np.asarray(closes, dtype=float)
    idx = pd.bdate_range(start, periods=len(opens)) if freq == "B" else \
        pd.date_range(start, periods=len(opens), freq=freq)
    return pd.DataFrame({
        "open": opens,
        "high": np.maximum(opens, closes),
        "low": np.minimum(opens, closes),
        "close": closes,
        "volume": 1_000_000.0,
    }, index=idx)


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def daily_fixture() -> pd.DataFrame:
    """The committed synthetic daily series, holdout bars included (raw read)."""
    df = pd.read_csv(FIXTURES / "daily" / "TEST.csv.gz",
                     parse_dates=["timestamp"], index_col="timestamp")
    return df


@pytest.fixture
def random_walk() -> pd.DataFrame:
    """Seeded 300-bar random walk for strategy/walk-forward tests."""
    rng = np.random.default_rng(123)
    n = 300
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, n)))
    open_ = np.concatenate([[100.0], close[:-1]])
    return make_ohlcv(open_, close)
