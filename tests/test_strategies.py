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


def _oversold_recovery_prices() -> np.ndarray:
    """Shared Round-3 test path: base, selloff (oscillator pinned oversold),
    flat bottom, slow recovery (cross-up entry, then exit above the exit
    band), flat top."""
    return np.concatenate([
        np.full(30, 100.0),
        np.linspace(100, 60, 20),   # selloff -> oscillator pinned near 0/-100
        np.full(5, 60.0),
        np.linspace(60, 100, 40),   # slow recovery -> cross up, then exit
        np.full(10, 100.0),
    ])


class TestStochasticReversion:
    def test_no_entry_while_pinned_oversold(self):
        # Cross-UP semantics: being oversold is not the signal — the
        # recovery through the band is. Flat all through the selloff.
        ohlcv = make_ohlcv(_oversold_recovery_prices())
        pos = STRATEGIES["stochastic_reversion"](ohlcv, k_period=20,
                                                 d_period=1, buy_below=20,
                                                 sell_above=80)
        assert (pos.iloc[30:55] == 0.0).all()  # selloff + flat bottom

    def test_enters_on_cross_up_exits_above_exit_band(self):
        ohlcv = make_ohlcv(_oversold_recovery_prices())
        pos = STRATEGIES["stochastic_reversion"](ohlcv, k_period=20,
                                                 d_period=1, buy_below=20,
                                                 sell_above=80)
        assert (pos.iloc[:59] == 0.0).all()      # nothing before the cross
        assert (pos.iloc[59:64] == 1.0).all()    # long after %K crosses up
        assert (pos.iloc[64:] == 0.0).all()      # exited once %K > 80

    def test_smoothing_delays_the_cross(self):
        # d_period=3 smooths %K, so the cross up through the band (and the
        # exit) land one bar later than the fast (d_period=1) oscillator.
        ohlcv = make_ohlcv(_oversold_recovery_prices())
        pos3 = STRATEGIES["stochastic_reversion"](ohlcv, k_period=20,
                                                  d_period=3, buy_below=20,
                                                  sell_above=80)
        assert (pos3.iloc[:60] == 0.0).all()
        assert (pos3.iloc[60:65] == 1.0).all()
        assert (pos3.iloc[65:] == 0.0).all()

    def test_warmup_flat(self, random_walk):
        # raw %K defined from iloc k_period-1; the d-bar SMA needs d_period-1
        # more bars -> first definable bar is iloc 15 for (14, 3).
        pos = STRATEGIES["stochastic_reversion"](random_walk, k_period=14,
                                                 d_period=3)
        assert (pos.iloc[:15] == 0.0).all()

    def test_flat_prices_stay_flat(self):
        ohlcv = make_ohlcv(np.full(80, 100.0))
        pos = STRATEGIES["stochastic_reversion"](ohlcv, k_period=14)
        assert (pos == 0.0).all()  # zero range -> undefined %K -> no signal

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="k_period"):
            STRATEGIES["stochastic_reversion"](random_walk, k_period=1)
        with pytest.raises(ValueError, match="d_period"):
            STRATEGIES["stochastic_reversion"](random_walk, d_period=0)
        with pytest.raises(ValueError, match="buy_below"):
            STRATEGIES["stochastic_reversion"](random_walk, buy_below=90,
                                               sell_above=80)


class TestWilliamsRReversion:
    def test_matches_fast_stochastic_complement(self, random_walk):
        # %R = %K - 100 at d_period=1, so with the thresholds mapped the two
        # strategies must emit identical positions (the smoothed stochastic
        # arm is what makes the Round-3 families distinct).
        willr = STRATEGIES["williams_r_reversion"](random_walk, period=14,
                                                   buy_below=-80,
                                                   sell_above=-20)
        stoch = STRATEGIES["stochastic_reversion"](random_walk, k_period=14,
                                                   d_period=1, buy_below=20,
                                                   sell_above=80)
        pd.testing.assert_series_equal(willr, stoch)

    def test_enters_on_rise_from_oversold_exits_above_exit(self):
        ohlcv = make_ohlcv(_oversold_recovery_prices())
        pos = STRATEGIES["williams_r_reversion"](ohlcv, period=20,
                                                 buy_below=-80,
                                                 sell_above=-20)
        assert (pos.iloc[30:55] == 0.0).all()    # pinned oversold: no entry
        assert (pos.iloc[59:64] == 1.0).all()    # long after %R rises through
        assert (pos.iloc[64:] == 0.0).all()      # exited once %R > -20

    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["williams_r_reversion"](random_walk, period=14)
        assert (pos.iloc[:13] == 0.0).all()

    def test_flat_prices_stay_flat(self):
        ohlcv = make_ohlcv(np.full(80, 100.0))
        pos = STRATEGIES["williams_r_reversion"](ohlcv, period=14)
        assert (pos == 0.0).all()  # zero range -> undefined %R -> no signal

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="period"):
            STRATEGIES["williams_r_reversion"](random_walk, period=1)
        with pytest.raises(ValueError, match="buy_below"):
            STRATEGIES["williams_r_reversion"](random_walk, buy_below=-20,
                                               sell_above=-80)


class TestRocMomentum:
    def test_classic_zero_threshold_long_up_flat_down(self):
        # entry == exit == 0 recovers the classic time-series momentum rule.
        up = make_ohlcv(np.linspace(100, 200, 120))
        down = make_ohlcv(np.linspace(200, 100, 120))
        pos_up = STRATEGIES["roc_momentum"](up, lookback=20, entry=0.0,
                                            exit=0.0)
        pos_down = STRATEGIES["roc_momentum"](down, lookback=20, entry=0.0,
                                              exit=0.0)
        assert (pos_up.iloc[20:] == 1.0).all()
        assert (pos_down == 0.0).all()

    def test_hysteresis_holds_between_bands(self):
        # Enter on roc > entry, hold while exit <= roc <= entry, exit only
        # on roc < exit. lookback=10: 100s, jump to 110 (roc=+10% -> enter),
        # plateau (roc=0, inside the band -> hold long), ease to 104
        # (roc=-5.45% < -5% -> exit), plateau (roc=0 -> hold flat).
        prices = np.concatenate([np.full(30, 100.0), np.full(20, 110.0),
                                 np.full(20, 104.0)])
        pos = STRATEGIES["roc_momentum"](make_ohlcv(prices), lookback=10,
                                         entry=0.05, exit=-0.05)
        assert (pos.iloc[:30] == 0.0).all()   # warm-up + roc never > entry
        assert (pos.iloc[30:50] == 1.0).all()  # entry, then held in the band
        assert (pos.iloc[50:] == 0.0).all()    # exit, then held flat

    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["roc_momentum"](random_walk, lookback=126)
        assert (pos.iloc[:126] == 0.0).all()

    def test_flat_prices_stay_flat(self):
        # roc == 0 is never strictly above the entry threshold.
        ohlcv = make_ohlcv(np.full(80, 100.0))
        pos = STRATEGIES["roc_momentum"](ohlcv, lookback=10)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="lookback"):
            STRATEGIES["roc_momentum"](random_walk, lookback=0)
        with pytest.raises(ValueError, match="exit"):
            STRATEGIES["roc_momentum"](random_walk, entry=0.0, exit=0.05)


class TestAdxFilteredSma:
    def test_adx_high_in_trend_low_in_chop(self):
        # The indicator itself: a clean trend pins ADX high (one-sided
        # directional movement), a drifting saw keeps it near zero (the
        # +DM/-DM legs cancel).
        from trading_lab.strategies.adx_filtered_sma import adx
        trend = make_ohlcv(np.linspace(100, 200, 120))
        n = 200
        saw = make_ohlcv(100.0 + 0.05 * np.arange(n)
                         + 2.0 * (-1.0) ** np.arange(n))
        assert (adx(trend, 14).iloc[40:] > 25.0).all()
        assert (adx(saw, 14).iloc[40:] < 20.0).all()

    def test_long_in_trending_uptrend(self):
        up = make_ohlcv(np.linspace(100, 200, 120))
        pos = STRATEGIES["adx_filtered_sma"](up, fast=10, slow=30,
                                             adx_period=14, adx_min=20.0)
        assert (pos.iloc[40:] == 1.0).all()

    def test_chop_blocks_the_crossover(self):
        # Drifting saw: the drift keeps fast SMA > slow SMA (the near-zero
        # adx_min arm is long), but the alternating bars keep ADX near zero
        # so the gated arm must stay flat everywhere.
        n = 200
        saw = make_ohlcv(100.0 + 0.05 * np.arange(n)
                         + 2.0 * (-1.0) ** np.arange(n))
        on = STRATEGIES["adx_filtered_sma"](saw, fast=5, slow=30,
                                            adx_period=14, adx_min=20.0)
        off = STRATEGIES["adx_filtered_sma"](saw, fast=5, slow=30,
                                             adx_period=14, adx_min=0.0)
        assert (off.iloc[35:] == 1.0).all()  # crossover arm is long
        assert (on == 0.0).all()             # ADX gate vetoes all of it
        assert (STRATEGIES["sma_crossover"](saw, fast=5, slow=30).iloc[35:]
                == off.iloc[35:]).all()      # near-zero gate = plain SMA

    def test_warmup_flat_until_both_defined(self):
        # Flat until BOTH the slow SMA (slow-1 bars) and ADX (2*adx_period
        # bars, the stacked Wilder seeds) are defined — here ADX dominates:
        # first definable bar is iloc[28] for adx_period=14, slow=10.
        up = make_ohlcv(np.linspace(100, 200, 120))
        pos = STRATEGIES["adx_filtered_sma"](up, fast=5, slow=10,
                                             adx_period=14, adx_min=20.0)
        assert (pos.iloc[:28] == 0.0).all()

    def test_flat_prices_stay_flat(self):
        # Zero range -> undefined DX -> the trending regime can never be
        # confirmed (and the SMAs never cross).
        ohlcv = make_ohlcv(np.full(120, 100.0))
        pos = STRATEGIES["adx_filtered_sma"](ohlcv, fast=5, slow=10,
                                             adx_period=5, adx_min=0.0)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="fast"):
            STRATEGIES["adx_filtered_sma"](random_walk, fast=50, slow=20)
        with pytest.raises(ValueError, match="adx_period"):
            STRATEGIES["adx_filtered_sma"](random_walk, adx_period=1)
        with pytest.raises(ValueError, match="adx_min"):
            STRATEGIES["adx_filtered_sma"](random_walk, adx_min=100.0)


class TestAroonTrend:
    def test_aroon_extremes_in_clean_trends(self):
        # The indicator itself: a monotone uptrend keeps the new high on
        # the current bar (Aroon-Up = 100) and the low at the window's far
        # edge (Aroon-Down = 0), so the oscillator pins at +100; a monotone
        # downtrend mirrors to -100.
        from trading_lab.strategies.aroon_trend import aroon
        up = make_ohlcv(np.linspace(100, 200, 120))
        down = make_ohlcv(np.linspace(200, 100, 120))
        assert (aroon(up, 25)["osc"].iloc[25:] == 100.0).all()
        assert (aroon(down, 25)["osc"].iloc[25:] == -100.0).all()

    def test_classic_zero_band_long_up_flat_down(self):
        # entry == exit == 0 recovers the classic Aroon-Up/Aroon-Down cross
        # (the committed within-family control arm).
        up = make_ohlcv(np.linspace(100, 200, 120))
        down = make_ohlcv(np.linspace(200, 100, 120))
        pos_up = STRATEGIES["aroon_trend"](up, period=25, entry=0.0, exit=0.0)
        pos_down = STRATEGIES["aroon_trend"](down, period=25, entry=0.0,
                                             exit=0.0)
        assert (pos_up.iloc[25:] == 1.0).all()
        assert (pos_down == 0.0).all()

    def test_hysteresis_holds_between_bands(self):
        # period=10: a fresh uptrend pins the oscillator at +100 (> entry
        # -> enter); the subsequent plateau ages the trend's last high out
        # of the window while every plateau bar ties both extremes — the
        # first-occurrence argmax/argmin then put the tied high at the
        # window's oldest bar (Aroon-Up -> 0) and the tied low equally old
        # (Aroon-Down -> 0), so the oscillator decays through the band
        # (hold long) and settles at 0 without ever crossing exit=-50:
        # the entry state must persist to the very end.
        prices = np.concatenate([np.linspace(100, 130, 30),
                                 np.full(30, 130.0)])
        pos = STRATEGIES["aroon_trend"](make_ohlcv(prices), period=10,
                                        entry=50.0, exit=-50.0)
        assert (pos.iloc[10:] == 1.0).all()   # entered at +100, never exits
        # Same path with exit=0 exits nothing either (osc reaches 0, never
        # strictly below), but a strict-positive exit line does fire:
        tight = STRATEGIES["aroon_trend"](make_ohlcv(prices), period=10,
                                          entry=50.0, exit=50.0)
        assert tight.iloc[-1] == 0.0          # decayed osc < 50: exited

    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["aroon_trend"](random_walk, period=25)
        assert (pos.iloc[:25] == 0.0).all()

    def test_flat_prices_stay_flat(self):
        # All-equal highs/lows: argmax/argmin land on the window's oldest
        # bar, so both Aroon legs read 0 and the oscillator is 0 — never
        # strictly above the entry threshold.
        ohlcv = make_ohlcv(np.full(80, 100.0))
        pos = STRATEGIES["aroon_trend"](ohlcv, period=10)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="period"):
            STRATEGIES["aroon_trend"](random_walk, period=1)
        with pytest.raises(ValueError, match="exit"):
            STRATEGIES["aroon_trend"](random_walk, entry=0.0, exit=50.0)


class TestCciReversion:
    def test_cci_sign_matches_price_vs_mean(self):
        # The indicator itself: a V-shaped path drives CCI deeply negative
        # at the trough and positive on the recovery.
        from trading_lab.strategies.cci_reversion import cci
        prices = np.concatenate([np.full(40, 100.0)
                                 + 0.5 * np.sin(np.arange(40)),
                                 np.linspace(100, 80, 15),
                                 np.linspace(80, 105, 30)])
        c = cci(make_ohlcv(prices), 20)
        assert c.min() < -100.0
        assert c.max() > 100.0

    def test_enters_on_recovery_not_on_dip(self):
        # The dip itself (CCI falling below buy_below) must NOT enter; the
        # cross back UP through buy_below is the entry; the rally above
        # sell_above exits.
        prices = np.concatenate([np.full(40, 100.0)
                                 + 0.5 * np.sin(np.arange(40)),
                                 np.linspace(100, 80, 15),
                                 np.linspace(80, 105, 30)])
        ohlcv = make_ohlcv(prices)
        from trading_lab.strategies.cci_reversion import cci
        c = cci(ohlcv, 20)
        pos = STRATEGIES["cci_reversion"](ohlcv, period=20, buy_below=-100,
                                          sell_above=100)
        first_below = (c < -100).idxmax()
        assert pos.loc[first_below] == 0.0   # dip bar: still flat
        assert (pos == 1.0).any()            # recovery cross: entered
        assert pos.iloc[-1] == 0.0           # exit above sell_above

    def test_uptrend_never_enters(self):
        # A monotone uptrend never dips oversold, so the mean-reversion
        # entry never triggers.
        up = make_ohlcv(np.linspace(100, 200, 120))
        pos = STRATEGIES["cci_reversion"](up, period=20, buy_below=-100,
                                          sell_above=100)
        assert (pos == 0.0).all()

    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["cci_reversion"](random_walk, period=20)
        assert (pos.iloc[:19] == 0.0).all()

    def test_flat_prices_stay_flat(self):
        # Zero mean absolute deviation -> undefined CCI -> no signal.
        ohlcv = make_ohlcv(np.full(80, 100.0))
        pos = STRATEGIES["cci_reversion"](ohlcv, period=10)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="period"):
            STRATEGIES["cci_reversion"](random_walk, period=1)
        with pytest.raises(ValueError, match="buy_below"):
            STRATEGIES["cci_reversion"](random_walk, buy_below=50,
                                        sell_above=100)


class TestXsecMomentum:
    """Round 2 slice R3 portfolio family: panel interface (weights over
    aligned closes), so it lives in PORTFOLIO_STRATEGIES, not STRATEGIES."""

    @staticmethod
    def make_closes(growth: dict, n: int = 60) -> pd.DataFrame:
        """Aligned closes panel, one column per ticker, constant per-bar
        growth rates so trailing total returns rank deterministically."""
        idx = pd.bdate_range("2024-01-01", periods=n)
        return pd.DataFrame({t: 100.0 * (1.0 + g) ** np.arange(n)
                             for t, g in sorted(growth.items())}, index=idx)

    def test_registered_as_portfolio_strategy_only(self):
        from trading_lab.strategies import PORTFOLIO_STRATEGIES, R2_XSEC_FAMILY
        assert R2_XSEC_FAMILY == ["xsec_momentum"]
        assert "xsec_momentum" in PORTFOLIO_STRATEGIES
        assert "xsec_momentum" not in STRATEGIES  # panel interface

    def test_ranking_selects_top_k_by_trailing_return(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        closes = self.make_closes({"A": 0.01, "B": 0.03, "C": 0.02,
                                   "D": 0.00})
        w = generate_weights(closes, L=5, k=2, rebalance_every=21)
        first = w.iloc[5]  # first decision bar (iloc L)
        assert first["B"] == 0.5 and first["C"] == 0.5  # top-2 momentum
        assert first["A"] == 0.0 and first["D"] == 0.0

    def test_decision_rows_only_on_the_21_bar_schedule(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        closes = self.make_closes({"A": 0.01, "B": 0.02}, n=100)
        w = generate_weights(closes, L=10, k=1, rebalance_every=21)
        decision_ilocs = np.nonzero(~w.isna().all(axis=1).to_numpy())[0]
        assert list(decision_ilocs) == [10, 31, 52, 73, 94]
        # warm-up: nothing before iloc L
        assert w.iloc[:10].isna().all().all()

    def test_weights_are_equal_weight_top_k(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        closes = self.make_closes({"A": 0.01, "B": 0.03, "C": 0.02,
                                   "D": 0.00}, n=90)
        for k in (2, 3):
            w = generate_weights(closes, L=5, k=k, rebalance_every=21)
            rows = w.dropna(how="all")
            assert len(rows) > 0
            assert np.allclose(rows.sum(axis=1), 1.0)
            assert ((rows == 0.0) | np.isclose(rows, 1.0 / k)).all().all()
            assert ((rows > 0).sum(axis=1) == k).all()

    def test_membership_switches_when_leadership_rotates(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        # A leads for the first half, then goes flat while B accelerates.
        n = 80
        a = np.concatenate([100.0 * 1.03 ** np.arange(40),
                            np.full(40, 100.0 * 1.03 ** 39)])
        b = np.concatenate([np.full(40, 100.0),
                            100.0 * 1.03 ** np.arange(40)])
        idx = pd.bdate_range("2024-01-01", periods=n)
        closes = pd.DataFrame({"A": a, "B": b}, index=idx)
        w = generate_weights(closes, L=10, k=1, rebalance_every=21)
        assert w.iloc[10]["A"] == 1.0   # A leads early
        assert w.iloc[73]["B"] == 1.0   # B leads late

    def test_tie_breaks_deterministically_by_column_order(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        closes = self.make_closes({"A": 0.02, "B": 0.02})  # identical returns
        w = generate_weights(closes, L=5, k=1, rebalance_every=21)
        assert w.iloc[5]["A"] == 1.0 and w.iloc[5]["B"] == 0.0

    def test_causality_prefix_invariance(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        rng = np.random.default_rng(42)
        idx = pd.bdate_range("2024-01-01", periods=150)
        closes = pd.DataFrame(
            {t: 100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.02, 150)))
             for t in ("A", "B", "C")}, index=idx)
        full = generate_weights(closes, L=21, k=2, rebalance_every=21)
        cut = 100
        truncated = generate_weights(closes.iloc[:cut], L=21, k=2,
                                     rebalance_every=21)
        pd.testing.assert_frame_equal(full.iloc[:cut], truncated)

    def test_rejects_bad_params(self):
        from trading_lab.strategies.xsec_momentum import generate_weights
        closes = self.make_closes({"A": 0.01, "B": 0.02})
        with pytest.raises(ValueError, match="L"):
            generate_weights(closes, L=0, k=1)
        with pytest.raises(ValueError, match="k"):
            generate_weights(closes, L=5, k=0)
        with pytest.raises(ValueError, match="k"):
            generate_weights(closes, L=5, k=3)  # only 2 instruments
        with pytest.raises(ValueError, match="rebalance_every"):
            generate_weights(closes, L=5, k=1, rebalance_every=0)
        with pytest.raises(ValueError, match="NaN"):
            bad = closes.copy()
            bad.iloc[3, 0] = np.nan
            generate_weights(bad, L=5, k=1)


class TestBollingerBreakout:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["bollinger_breakout"](random_walk, period=20,
                                               num_std=2.0)
        assert (pos.iloc[:19] == 0.0).all()

    def test_enters_on_breakout_exits_below_middle(self):
        # Flat base (std ~ 0), a hard jump far above the upper band (entry),
        # a plateau, then a crash far below the middle band (exit) — the
        # keltner_breakout test path, re-run against SMA + k*std bands.
        prices = np.concatenate([
            np.full(40, 100.0),   # base: bands are tight around 100
            np.full(30, 140.0),   # breakout bar at iloc[40], then plateau
            np.full(20, 80.0),    # crash below the middle band at iloc[70]
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["bollinger_breakout"](ohlcv, period=5, num_std=1.5)
        assert pos.iloc[40] == 1.0             # breakout bar goes long
        assert (pos.iloc[40:70] == 1.0).all()  # held through the plateau
        assert (pos.iloc[70:] == 0.0).all()    # exit once close < middle

    def test_holds_between_middle_and_upper_band(self):
        # Late in the plateau the bands have converged onto the close
        # (std -> 0, middle == close): no fresh breakout fires there, yet
        # the state machine must HOLD the long, not flip-flop.
        prices = np.concatenate([np.full(40, 100.0), np.full(60, 140.0)])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["bollinger_breakout"](ohlcv, period=5, num_std=1.5)
        close = ohlcv["close"]
        middle = close.rolling(5).mean()
        assert np.allclose(close.iloc[80:], middle.iloc[80:])
        assert (pos.iloc[80:] == 1.0).all()

    def test_inverse_thesis_of_reversion_in_steady_uptrend(self):
        # A steady uptrend keeps the close pinned above the middle band:
        # the breakout family rides it long while the reversion family
        # (which buys only stretches BELOW the lower band) never enters.
        up = make_ohlcv(np.linspace(100, 200, 120))
        pos_break = STRATEGIES["bollinger_breakout"](up, period=20,
                                                     num_std=1.0)
        pos_revert = STRATEGIES["bollinger_reversion"](up, lookback=20,
                                                       z_entry=1.0)
        assert (pos_break.iloc[25:] == 1.0).all()
        assert (pos_revert == 0.0).all()

    def test_flat_series_never_enters(self):
        # Constant price: std = 0, close == middle == upper band. Entry
        # needs a strict '>' (tie resolves against the strategy) — flat.
        flat = make_ohlcv(np.full(120, 100.0))
        pos = STRATEGIES["bollinger_breakout"](flat, period=5, num_std=2.0)
        assert (pos == 0.0).all()

    def test_flat_in_downtrend(self):
        down = make_ohlcv(np.linspace(200, 100, 160))
        pos = STRATEGIES["bollinger_breakout"](down, period=20, num_std=1.5)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="period"):
            STRATEGIES["bollinger_breakout"](random_walk, period=1)
        with pytest.raises(ValueError, match="num_std"):
            STRATEGIES["bollinger_breakout"](random_walk, num_std=0.0)


class TestAtrTrailing:
    def test_warmup_flat(self, random_walk):
        pos = STRATEGIES["atr_trailing"](random_walk, entry_lookback=20,
                                         atr_period=14, k=3.0)
        assert (pos.iloc[:20] == 0.0).all()

    def test_enters_on_channel_breakout_exits_on_trailing_stop(self):
        # Flat base, a hard jump above the 20-bar high channel (entry), a
        # plateau (ATR decays toward 0, stop ratchets up under the highs),
        # then a modest dip that pierces highest-close - k*ATR (exit).
        prices = np.concatenate([
            np.full(40, 100.0),   # base: channel pinned at 100
            np.full(30, 140.0),   # breakout bar at iloc[40], then plateau
            np.full(20, 130.0),   # dip below the tight stop at iloc[70]
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["atr_trailing"](ohlcv, entry_lookback=20,
                                         atr_period=14, k=2.0)
        assert pos.iloc[40] == 1.0             # breakout bar goes long
        assert (pos.iloc[40:70] == 1.0).all()  # held through the plateau
        assert (pos.iloc[70:] == 0.0).all()    # stopped out on the dip;
        # no re-entry: 130 never breaks the (140-high) channel again

    def test_stop_ratchets_with_highest_close_not_entry_price(self):
        # After a rally the trade must be stopped out on a pullback that is
        # still far ABOVE the entry price: the chandelier hangs from the
        # highest close since entry, not from the entry level.
        prices = np.concatenate([
            np.full(40, 100.0),           # base
            np.linspace(104, 200, 30),    # breakout + rally to 200
            np.full(20, 150.0),           # pullback: > entry, < ratcheted stop
        ])
        ohlcv = make_ohlcv(prices)
        pos = STRATEGIES["atr_trailing"](ohlcv, entry_lookback=20,
                                         atr_period=14, k=2.0)
        assert (pos.iloc[41:70] == 1.0).all()  # long through the rally
        assert (pos.iloc[70:] == 0.0).all()    # stopped despite close > entry

    def test_flat_series_never_enters(self):
        # Constant price: close equals the prior 20-bar high. Entry needs a
        # strict '>' (tie resolves against the strategy) — flat forever.
        flat = make_ohlcv(np.full(120, 100.0))
        pos = STRATEGIES["atr_trailing"](flat, entry_lookback=20,
                                         atr_period=14, k=3.0)
        assert (pos == 0.0).all()

    def test_flat_in_downtrend(self):
        down = make_ohlcv(np.linspace(200, 100, 160))
        pos = STRATEGIES["atr_trailing"](down, entry_lookback=20,
                                         atr_period=14, k=2.0)
        assert (pos == 0.0).all()

    def test_rejects_bad_params(self, random_walk):
        with pytest.raises(ValueError, match="entry_lookback"):
            STRATEGIES["atr_trailing"](random_walk, entry_lookback=1)
        with pytest.raises(ValueError, match="atr_period"):
            STRATEGIES["atr_trailing"](random_walk, atr_period=1)
        with pytest.raises(ValueError, match="k"):
            STRATEGIES["atr_trailing"](random_walk, k=0.0)
