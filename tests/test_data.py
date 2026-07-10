"""Data-layer tests: holdout lock, integrity checks, cache roundtrip.

Offline: reads only committed fixtures under tests/fixtures/.
"""

import gzip

import pandas as pd
import pytest

from trading_lab import config
from trading_lab.data import (DataIntegrityError, HoldoutViolationWarning,
                              cache_path, check_integrity, load_ohlcv,
                              save_cache)

from conftest import make_ohlcv


class TestHoldoutLock:
    def test_loader_excludes_holdout_by_default(self, fixtures_dir, daily_fixture):
        """The fixture spans HOLDOUT_START; the loader must refuse those bars."""
        holdout = pd.Timestamp(config.HOLDOUT_START)
        assert daily_fixture.index.max() >= holdout, "fixture must span the boundary"
        df = load_ohlcv("TEST", "daily", data_dir=fixtures_dir)
        assert len(df) > 0
        assert df.index.max() < holdout
        # exactly the pre-holdout subset, nothing dropped besides holdout bars
        assert len(df) == int((daily_fixture.index < holdout).sum())

    def test_unlock_holdout_requires_explicit_flag_and_warns(self, fixtures_dir):
        with pytest.warns(HoldoutViolationWarning, match="HOLDOUT UNLOCKED"):
            df = load_ohlcv("TEST", "daily", data_dir=fixtures_dir,
                            unlock_holdout=True)
        assert df.index.max() >= pd.Timestamp(config.HOLDOUT_START)

    def test_holdout_constant_unchanged(self):
        """The locked boundary is a fixed constant (P5 reviews against it)."""
        assert config.HOLDOUT_START == "2025-01-09"

    def test_start_end_filters(self, fixtures_dir):
        df = load_ohlcv("TEST", "daily", data_dir=fixtures_dir,
                        start="2024-08-01", end="2024-09-01")
        assert df.index.min() >= pd.Timestamp("2024-08-01")
        assert df.index.max() < pd.Timestamp("2024-09-01")

    def test_data_dir_override_still_enforced(self, tmp_path):
        """Alternate caches (e.g. data/p2ext/) get the same rail: write a
        temp cache spanning the boundary and load it via data_dir=."""
        holdout = pd.Timestamp(config.HOLDOUT_START)
        df = make_ohlcv([100.0 + i for i in range(60)], start="2024-11-01")
        assert df.index.max() >= holdout, "temp cache must span the boundary"
        df.index.name = "timestamp"
        save_cache(df, "EXT", "daily", data_dir=tmp_path)
        loaded = load_ohlcv("EXT", "daily", data_dir=tmp_path)
        assert len(loaded) > 0
        assert loaded.index.max() < holdout
        assert len(loaded) == int((df.index < holdout).sum())

    def test_end_beyond_boundary_still_clipped(self, fixtures_dir,
                                               daily_fixture):
        """end= past HOLDOUT_START must not reintroduce holdout bars."""
        holdout = pd.Timestamp(config.HOLDOUT_START)
        end = str(daily_fixture.index.max() + pd.Timedelta(days=1))
        df = load_ohlcv("TEST", "daily", data_dir=fixtures_dir, end=end)
        assert len(df) > 0
        assert df.index.max() < holdout

    def test_start_after_boundary_returns_empty(self, fixtures_dir):
        """start= inside the holdout yields an empty frame (the holdout
        filter runs BEFORE start/end slicing), never holdout bars."""
        df = load_ohlcv("TEST", "daily", data_dir=fixtures_dir,
                        start=config.HOLDOUT_START)
        assert df.empty


class TestIntegrity:
    def test_valid_frame_passes(self, daily_fixture):
        check_integrity(daily_fixture, "TEST")

    def test_duplicate_timestamps_rejected(self):
        df = make_ohlcv([100.0] * 4)
        dup = pd.concat([df, df.iloc[[1]]]).sort_index()
        with pytest.raises(DataIntegrityError, match="duplicate"):
            check_integrity(dup, "X")

    def test_non_monotonic_rejected(self):
        df = make_ohlcv([100.0] * 4).iloc[[0, 2, 1, 3]]
        with pytest.raises(DataIntegrityError, match="monotonic"):
            check_integrity(df, "X")

    def test_nan_prices_rejected(self):
        df = make_ohlcv([100.0] * 4)
        df.loc[df.index[2], "close"] = float("nan")
        with pytest.raises(DataIntegrityError, match="NaN"):
            check_integrity(df, "X")

    def test_non_positive_prices_rejected(self):
        df = make_ohlcv([100.0] * 4)
        df.loc[df.index[1], "low"] = -1.0
        with pytest.raises(DataIntegrityError, match="non-positive"):
            check_integrity(df, "X")

    def test_loader_runs_integrity_checks(self, tmp_path):
        """A corrupted cache file (duplicate rows) must fail to load."""
        path = tmp_path / "daily" / "BAD.csv.gz"
        path.parent.mkdir(parents=True)
        rows = ("timestamp,open,high,low,close,volume\n"
                "2024-01-02,1,1,1,1,0\n2024-01-02,1,1,1,1,0\n")
        with gzip.open(path, "wt") as fh:
            fh.write(rows)
        with pytest.raises(DataIntegrityError, match="duplicate"):
            load_ohlcv("BAD", "daily", data_dir=tmp_path)


class TestCache:
    def test_roundtrip(self, tmp_path):
        df = make_ohlcv([100, 101, 102, 103], start="2024-03-04")
        df.index.name = "timestamp"
        save_cache(df, "RT", "daily", data_dir=tmp_path)
        loaded = load_ohlcv("RT", "daily", data_dir=tmp_path)
        pd.testing.assert_frame_equal(loaded, df, check_exact=False,
                                      atol=1e-6, check_freq=False)

    def test_cache_path_layout(self, tmp_path):
        assert cache_path("aapl", "hourly", tmp_path) == tmp_path / "hourly" / "AAPL.csv.gz"
        with pytest.raises(ValueError, match="timeframe"):
            cache_path("AAPL", "weekly", tmp_path)

    def test_missing_cache_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="fetch_data"):
            load_ohlcv("NOPE", "daily", data_dir=tmp_path)
