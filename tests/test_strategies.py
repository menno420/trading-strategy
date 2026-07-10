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


class TestEmaCrossover:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["ema_crossover"](random_walk, fast=10, slow=30)
        assert (pos.iloc[:30] == 0.0).all()

    def test_long_in_uptrend_flat_in_downtrend(self):
        up = make_ohlcv(np.linspace(100, 200, 120))
        down = make_ohlcv(np.linspace(200, 100, 120))
        pos_up = STRATEGIES["ema_crossover"](up, fast=10, slow=30)
        pos_down = STRATEGIES["ema_crossover"](down, fast=10, slow=30)
        assert (pos_up.iloc[40:] == 1.0).all()
        assert (pos_down.iloc[40:] == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="fast"):
            STRATEGIES["ema_crossover"](random_walk, fast=50, slow=20)


class TestMacd:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["macd"](random_walk, fast=12, slow=26, signal=9)
        assert (pos.iloc[:35] == 0.0).all()  # slow + signal bars

    def test_long_after_turn_up_flat_after_turn_down(self):
        # V shape: MACD line crosses above its signal after the trend turns
        # up, and below after it turns down (inverted V).
        v = make_ohlcv(np.concatenate([np.linspace(200, 100, 80),
                                       np.linspace(100, 220, 80)]))
        iv = make_ohlcv(np.concatenate([np.linspace(100, 220, 80),
                                        np.linspace(220, 100, 80)]))
        pos_v = STRATEGIES["macd"](v, fast=12, slow=26, signal=9)
        pos_iv = STRATEGIES["macd"](iv, fast=12, slow=26, signal=9)
        assert (pos_v.iloc[100:] == 1.0).all()   # long once uptrend confirmed
        assert (pos_iv.iloc[100:] == 0.0).all()  # flat once downtrend confirmed

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="fast"):
            STRATEGIES["macd"](random_walk, fast=26, slow=12)
        with pytest.raises(ValueError, match="signal"):
            STRATEGIES["macd"](random_walk, fast=12, slow=26, signal=0)


class TestDonchian:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["donchian"](random_walk, entry=20, exit=10)
        assert (pos.iloc[:20] == 0.0).all()

    def test_enters_on_breakout_exits_on_breakdown(self):
        prices = np.concatenate([
            np.full(30, 100.0),          # flat base
            np.linspace(100, 130, 20),   # breakout above 30-bar channel high
            np.full(10, 130.0),
            np.linspace(130, 90, 20),    # breakdown below exit-channel low
            np.full(10, 90.0),
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["donchian"](ohlcv, entry=20, exit=10)
        assert pos.loc[ohlcv.index[45]] == 1.0  # long during the breakout leg
        assert pos.loc[ohlcv.index[75]] == 0.0  # exited during the breakdown

    def test_own_bar_never_triggers_breakout(self):
        # A single spike bar: its own high must not create the channel it
        # breaks (channel is shifted one bar).
        prices = np.full(60, 100.0)
        prices[40] = 150.0
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["donchian"](ohlcv, entry=20, exit=10)
        assert pos.loc[ohlcv.index[40]] == 1.0   # close 150 > prior 20-bar high
        prior = STRATEGIES["donchian"](ohlcv.iloc[:40], entry=20, exit=10)
        assert (prior == 0.0).all()              # nothing before the spike

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="exit"):
            STRATEGIES["donchian"](random_walk, entry=20, exit=30)
        with pytest.raises(ValueError, match="entry"):
            STRATEGIES["donchian"](random_walk, entry=1, exit=1)


class TestSupertrendIndicator:
    def test_direction_tracks_trend(self):
        from trading_lab.strategies._supertrend import supertrend_direction
        up = make_ohlcv(np.linspace(100, 300, 200))
        down = make_ohlcv(np.linspace(300, 100, 200))
        assert (supertrend_direction(up, 5, 2.0).iloc[10:] == 1.0).all()
        assert (supertrend_direction(down, 5, 2.0).iloc[10:] == -1.0).all()

    def test_flips_bearish_after_reversal(self):
        from trading_lab.strategies._supertrend import supertrend_direction
        rise_fall = make_ohlcv(np.concatenate([np.linspace(100, 200, 80),
                                               np.linspace(200, 100, 80)]))
        d = supertrend_direction(rise_fall, 5, 2.0)
        assert (d.iloc[40:78] == 1.0).all()   # bullish during the rise
        assert (d.iloc[100:] == -1.0).all()   # bearish once the fall is in force

    def test_rejects_bad_params(self, random_walk):
        from trading_lab.strategies._supertrend import supertrend_direction
        with pytest.raises(ValueError, match="st_period"):
            supertrend_direction(random_walk, 0, 3.0)
        with pytest.raises(ValueError, match="st_mult"):
            supertrend_direction(random_walk, 10, 0.0)


_ST_FLIP_PARAMS = dict(st_period=5, st_mult=2.0, ema_len=30,
                       macd_fast=5, macd_slow=15, macd_signal=3)


class TestSupertrendFlip:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["supertrend_flip"](random_walk,
                                            **DEFAULT_PARAMS["supertrend_flip"])
        assert (pos.iloc[:200] == 0.0).all()  # ema_len dominates the warm-up

    def test_long_in_uptrend_flat_in_downtrend(self):
        up = make_ohlcv(np.linspace(100, 300, 200))
        down = make_ohlcv(np.linspace(300, 100, 200))
        pos_up = STRATEGIES["supertrend_flip"](up, **_ST_FLIP_PARAMS)
        pos_down = STRATEGIES["supertrend_flip"](down, **_ST_FLIP_PARAMS)
        assert (pos_up.iloc[40:] == 1.0).all()
        assert (pos_down == 0.0).all()

    def test_exits_on_supertrend_flip(self):
        rise_fall = make_ohlcv(np.concatenate([np.linspace(100, 200, 80),
                                               np.linspace(200, 100, 80)]))
        pos = STRATEGIES["supertrend_flip"](rise_fall, **_ST_FLIP_PARAMS)
        assert (pos.iloc[45:78] == 1.0).all()  # long during the rise
        assert (pos.iloc[100:] == 0.0).all()   # flat after the flip, no re-entry

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="macd_fast"):
            STRATEGIES["supertrend_flip"](random_walk, macd_fast=26, macd_slow=12)
        with pytest.raises(ValueError, match="macd_signal"):
            STRATEGIES["supertrend_flip"](random_walk, macd_signal=0)
        with pytest.raises(ValueError, match="ema_len"):
            STRATEGIES["supertrend_flip"](random_walk, ema_len=0)


class TestMacdSupertrend:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["macd_supertrend"](random_walk,
                                            **DEFAULT_PARAMS["macd_supertrend"])
        assert (pos.iloc[:200] == 0.0).all()  # ema_len dominates the warm-up

    def test_enters_on_confirmed_cross_exits_on_cross_down(self):
        # Uptrend with a shallow pullback: the pullback produces a MACD
        # cross-down then cross-up WHILE supertrend stays bullish and price
        # stays above the EMA — that recovery cross is the confirmed entry.
        prices = np.concatenate([
            np.linspace(100, 200, 60),   # rise (covers the warm-up)
            np.linspace(200, 188, 12),   # shallow pullback -> macd cross down
            np.linspace(188, 300, 60),   # resume -> confirmed macd cross up
            np.linspace(300, 150, 60),   # decline -> macd cross down = exit
        ])
        pos = STRATEGIES["macd_supertrend"](
            make_ohlcv(prices), st_period=5, st_mult=2.0, ema_len=20,
            macd_fast=5, macd_slow=15, macd_signal=3)
        assert (pos.iloc[:70] == 0.0).all()      # no entry before the cross
        assert (pos.iloc[80:130] == 1.0).all()   # long after confirmation
        assert (pos.iloc[140:] == 0.0).all()     # exited on the cross down

    def test_blocked_cross_is_skipped(self):
        # V shape: the MACD crosses up right at the bottom, but supertrend is
        # still bearish and price is below the EMA — no entry, ever (the
        # filters block the event; there is no later cross to re-arm it).
        v = make_ohlcv(np.concatenate([np.linspace(200, 100, 80),
                                       np.linspace(100, 250, 80)]))
        pos = STRATEGIES["macd_supertrend"](v, st_period=5, st_mult=2.0,
                                            ema_len=10, macd_fast=5,
                                            macd_slow=15, macd_signal=3)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="macd_fast"):
            STRATEGIES["macd_supertrend"](random_walk, macd_fast=26, macd_slow=12)
        with pytest.raises(ValueError, match="macd_signal"):
            STRATEGIES["macd_supertrend"](random_walk, macd_signal=0)
        with pytest.raises(ValueError, match="ema_len"):
            STRATEGIES["macd_supertrend"](random_walk, ema_len=0)


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
