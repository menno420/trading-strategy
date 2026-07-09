"""Strategy tests: valid positions, causality (prefix invariance), params."""

import numpy as np
import pandas as pd
import pytest

from trading_lab.strategies import DEFAULT_PARAMS, STRATEGIES

from conftest import make_ohlcv


@pytest.mark.parametrize("name", list(STRATEGIES))
class TestAllStrategies:
    def test_positions_valid(self, name, random_walk):
        pos = STRATEGIES[name](random_walk, **DEFAULT_PARAMS[name])
        assert isinstance(pos, pd.Series)
        assert pos.index.equals(random_walk.index)
        assert not pos.isna().any()
        assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_causality_prefix_invariance(self, name, random_walk):
        """Truncating the future must not change past positions: positions[t]
        depends only on data through bar t."""
        full = STRATEGIES[name](random_walk, **DEFAULT_PARAMS[name])
        cut = len(random_walk) - 60
        truncated = STRATEGIES[name](random_walk.iloc[:cut], **DEFAULT_PARAMS[name])
        pd.testing.assert_series_equal(full.iloc[:cut], truncated)


class TestBuyAndHold:
    def test_always_long(self, random_walk):
        pos = STRATEGIES["buy_and_hold"](random_walk)
        assert (pos == 1.0).all()


class TestSmaCrossover:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["sma_crossover"](random_walk, fast=10, slow=30)
        assert (pos.iloc[:29] == 0.0).all()

    def test_long_in_uptrend_flat_in_downtrend(self):
        up = make_ohlcv(np.linspace(100, 200, 120))
        down = make_ohlcv(np.linspace(200, 100, 120))
        pos_up = STRATEGIES["sma_crossover"](up, fast=10, slow=30)
        pos_down = STRATEGIES["sma_crossover"](down, fast=10, slow=30)
        assert (pos_up.iloc[35:] == 1.0).all()
        assert (pos_down.iloc[35:] == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="fast"):
            STRATEGIES["sma_crossover"](random_walk, fast=50, slow=20)


class TestRsiMeanReversion:
    def test_enters_after_selloff_exits_after_rally(self):
        prices = np.concatenate([
            np.full(30, 100.0),
            np.linspace(100, 60, 20),   # heavy selloff -> RSI oversold
            np.full(10, 60.0),
            np.linspace(60, 120, 30),   # strong rally -> RSI overbought
            np.full(10, 120.0),
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["rsi_mean_reversion"](ohlcv, period=14,
                                               oversold=30, overbought=70)
        assert pos.loc[ohlcv.index[49]] == 1.0   # long by the end of selloff
        assert pos.loc[ohlcv.index[75]] == 0.0   # exited during the rally
        assert (pos.iloc[:14] == 0.0).all()      # warm-up flat

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="oversold"):
            STRATEGIES["rsi_mean_reversion"](random_walk, oversold=80,
                                             overbought=70)
