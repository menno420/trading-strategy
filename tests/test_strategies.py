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


class TestBollingerReversion:
    def test_enters_below_band_exits_on_reversion(self):
        prices = np.concatenate([
            100.0 + np.tile([0.5, -0.5], 20),   # 40 bars of tight chop
            np.linspace(100, 80, 10),           # sharp drop -> z << -z_entry
            np.full(5, 80.0),
            np.linspace(80, 105, 25),           # recovery -> z back above 0
            np.full(10, 105.0),
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["bollinger_reversion"](ohlcv, lookback=20,
                                                z_entry=2.0, z_exit=0.0)
        assert pos.loc[ohlcv.index[49]] == 1.0   # long by the end of the drop
        assert pos.iloc[-1] == 0.0               # exited after the recovery
        assert (pos.iloc[:19] == 0.0).all()      # warm-up flat

    def test_flat_prices_stay_flat(self):
        ohlcv = make_ohlcv(np.full(80, 100.0))
        pos = STRATEGIES["bollinger_reversion"](ohlcv, lookback=20,
                                                z_entry=2.0, z_exit=0.0)
        assert (pos == 0.0).all()  # zero std -> undefined z -> no signal

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="lookback"):
            STRATEGIES["bollinger_reversion"](random_walk, lookback=1)
        with pytest.raises(ValueError, match="z_entry"):
            STRATEGIES["bollinger_reversion"](random_walk, z_entry=0.0)
        with pytest.raises(ValueError, match="z_exit"):
            STRATEGIES["bollinger_reversion"](random_walk, z_entry=1.0,
                                              z_exit=-1.5)


class TestPullback:
    def test_buys_dip_in_uptrend_sells_recovery(self):
        prices = np.concatenate([
            np.linspace(100, 160, 60),   # steady uptrend (covers warm-up)
            np.linspace(160, 148, 6),    # pullback -> fresh 5-bar low
            np.linspace(148, 180, 20),   # recovery -> close > exit SMA
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["pullback"](ohlcv, entry_lookback=5, exit_len=5,
                                     trend_len=50)
        assert pos.loc[ohlcv.index[65]] == 1.0   # long during the dip
        assert (pos.iloc[75:] == 0.0).all()      # exited on the recovery
        assert (pos.iloc[:50] == 0.0).all()      # trend-SMA warm-up flat

    def test_trend_filter_blocks_downtrend_entries(self):
        down = make_ohlcv(np.linspace(200, 100, 120))
        pos = STRATEGIES["pullback"](down, entry_lookback=5, exit_len=5,
                                     trend_len=50)
        assert (pos == 0.0).all()  # every dip is below the trend SMA

    def test_no_filter_allows_downtrend_entries(self):
        down = make_ohlcv(np.linspace(200, 100, 120))
        pos = STRATEGIES["pullback"](down, entry_lookback=5, exit_len=5,
                                     trend_len=0)
        assert (pos.iloc[10:] == 1.0).any()  # unfiltered dips do enter

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="entry_lookback"):
            STRATEGIES["pullback"](random_walk, entry_lookback=1)
        with pytest.raises(ValueError, match="exit_len"):
            STRATEGIES["pullback"](random_walk, exit_len=1)
        with pytest.raises(ValueError, match="trend_len"):
            STRATEGIES["pullback"](random_walk, trend_len=-1)


class TestVolFilteredTrend:
    def test_filter_off_equals_plain_sma_crossover(self, random_walk):
        plain = STRATEGIES["sma_crossover"](random_walk, fast=10, slow=30)
        off = STRATEGIES["vol_filtered_trend"](random_walk, fast=10, slow=30,
                                               vol_filter=False)
        pd.testing.assert_series_equal(plain, off)

    def test_warmup_flat_until_filter_defined(self):
        # With the filter ON, positions must stay flat until BOTH the slow
        # SMA and the vol median are defined (ambiguity resolves against the
        # strategy). Warm-up here: 5 (vol incl. pct_change NaN) + 19 more
        # bars for the 20-bar median -> first definable bar is iloc[24].
        up = make_ohlcv(np.linspace(100, 200, 120))
        pos = STRATEGIES["vol_filtered_trend"](up, fast=5, slow=10,
                                               vol_window=5, med_window=20)
        assert (pos.iloc[:24] == 0.0).all()

    def test_long_in_calm_uptrend(self):
        # Smooth uptrend: realized vol is (near-)constant, but with strictly
        # convergent linspace returns the trailing median sits above the
        # newest vol about half the time; use decaying noise so late vol is
        # clearly below its trailing median while the trend is up.
        rng = np.random.default_rng(7)
        n = 160
        drift = np.linspace(100, 200, n)
        noise = rng.normal(0.0, 1.0, n) * np.linspace(3.0, 0.1, n)
        ohlcv = make_ohlcv(drift + noise)
        pos = STRATEGIES["vol_filtered_trend"](ohlcv, fast=5, slow=10,
                                               vol_window=5, med_window=20)
        assert (pos.iloc[-25:] == 1.0).all()

    def test_high_vol_regime_blocks_uptrend_entry(self):
        # Uptrend whose volatility EXPANDS: recent vol ends up above its
        # trailing median, so the filter must veto the (still bullish)
        # crossover; the filter-off arm stays long.
        rng = np.random.default_rng(11)
        n = 160
        drift = np.linspace(100, 200, n)
        noise = rng.normal(0.0, 1.0, n) * np.linspace(0.1, 6.0, n)
        ohlcv = make_ohlcv(drift + noise)
        on = STRATEGIES["vol_filtered_trend"](ohlcv, fast=5, slow=40,
                                              vol_window=5, med_window=20)
        off = STRATEGIES["vol_filtered_trend"](ohlcv, fast=5, slow=40,
                                               vol_filter=False)
        assert (off.iloc[60:] == 1.0).mean() > 0.9   # trend arm is long
        assert (on.iloc[60:] == 0.0).mean() > 0.5    # filter vetoes often

    def test_flat_in_downtrend(self):
        down = make_ohlcv(np.linspace(200, 100, 160))
        pos = STRATEGIES["vol_filtered_trend"](down, fast=5, slow=10,
                                               vol_window=5, med_window=20)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="fast"):
            STRATEGIES["vol_filtered_trend"](random_walk, fast=50, slow=20)
        with pytest.raises(ValueError, match="vol_window"):
            STRATEGIES["vol_filtered_trend"](random_walk, vol_window=1)
        with pytest.raises(ValueError, match="med_window"):
            STRATEGIES["vol_filtered_trend"](random_walk, med_window=1)


class TestKeltnerBreakout:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["keltner_breakout"](random_walk, n=20, m=1.5)
        assert (pos.iloc[:20] == 0.0).all()

    def test_enters_on_breakout_exits_below_ema(self):
        # Flat base (ATR ~ 0), a hard jump far above EMA + m*ATR (entry),
        # a plateau, then a crash far below the EMA (exit).
        prices = np.concatenate([
            np.full(40, 100.0),   # base: channel is tight around 100
            np.full(30, 140.0),   # breakout bar at iloc[40], then plateau
            np.full(20, 80.0),    # crash below EMA at iloc[70]
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["keltner_breakout"](ohlcv, n=5, m=1.5)
        assert pos.iloc[40] == 1.0           # breakout bar goes long
        assert (pos.iloc[40:70] == 1.0).all()  # held through the plateau
        assert (pos.iloc[70:] == 0.0).all()    # exit once close < EMA

    def test_holds_between_ema_and_upper_band(self):
        # After entry the plateau sits between the two triggers (close is
        # neither > EMA + m*ATR once the channel catches up, nor < EMA):
        # the state machine must HOLD the long, not flip-flop.
        prices = np.concatenate([np.full(40, 100.0), np.full(60, 140.0)])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["keltner_breakout"](ohlcv, n=5, m=1.5)
        close = ohlcv["close"]
        ema = close.ewm(span=5, adjust=False).mean()
        # late plateau: EMA has converged to the close, so no fresh breakout
        # fires there (close is not strictly above EMA + m*ATR) ...
        assert np.allclose(close.iloc[80:], ema.iloc[80:], rtol=1e-3)
        # ... yet the position is held long the whole way
        assert (pos.iloc[80:] == 1.0).all()

    def test_flat_series_never_enters(self):
        # Constant price: ATR = 0, close == EMA == upper band. Entry needs a
        # strict '>', so equality is NOT a breakout (tie resolves against
        # the strategy) — flat forever.
        flat = make_ohlcv(np.full(120, 100.0))
        pos = STRATEGIES["keltner_breakout"](flat, n=5, m=2.0)
        assert (pos == 0.0).all()

    def test_flat_in_downtrend(self):
        down = make_ohlcv(np.linspace(200, 100, 160))
        pos = STRATEGIES["keltner_breakout"](down, n=5, m=1.5)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="n"):
            STRATEGIES["keltner_breakout"](random_walk, n=1)
        with pytest.raises(ValueError, match="m"):
            STRATEGIES["keltner_breakout"](random_walk, m=0.0)
