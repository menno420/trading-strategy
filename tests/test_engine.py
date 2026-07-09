"""Engine tests: t+1-open execution (no lookahead), cost application."""

import numpy as np
import pandas as pd
import pytest

from trading_lab.engine import buy_and_hold_result, run_backtest

from conftest import make_ohlcv


class TestNoLookahead:
    """Prove a signal cannot capture the price move of its own bar: fills
    happen at bar t+1's open."""

    def _jump_frame(self):
        # Price doubles during bar 4: close[4] and every price from bar 5 on
        # is 200; opens before bar 5 are 100.
        opens = [100, 100, 100, 100, 100, 200, 200, 200]
        closes = [100, 100, 100, 100, 200, 200, 200, 200]
        return make_ohlcv(opens, closes)

    def test_signal_on_jump_bar_gains_nothing(self):
        """The jump is first visible at bar 4's close. A signal at bar 4
        fills at open[5]=200 — after the move — so it earns ~0."""
        ohlcv = self._jump_frame()
        pos = pd.Series(0.0, index=ohlcv.index)
        pos.iloc[4] = 1.0
        res = run_backtest(ohlcv, pos, slippage_bps=0, commission_bps=0)
        assert res.equity.iloc[-1] == pytest.approx(1.0)

    def test_prescient_signal_would_have_gained(self):
        """Sanity check of the same frame: only a signal at bar 3 (i.e.
        knowing the future) captures the open[4]->open[5] move. Together with
        the test above this pins execution to t+1 open."""
        ohlcv = self._jump_frame()
        pos = pd.Series(0.0, index=ohlcv.index)
        pos.iloc[3] = 1.0
        res = run_backtest(ohlcv, pos, slippage_bps=0, commission_bps=0)
        assert res.equity.iloc[-1] == pytest.approx(2.0)

    def test_shifted_signal_cannot_see_future(self):
        """Shifting a profitable signal one bar later must not reproduce the
        original profit — returns are strictly attributed after the fill."""
        rng = np.random.default_rng(0)
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, 100)))
        ohlcv = make_ohlcv(np.concatenate([[100], close[:-1]]), close)
        # 'oracle' signal: long exactly on bars before an up-move
        future_up = (ohlcv["open"].shift(-1) > ohlcv["open"]).astype(float)
        oracle = future_up.shift(-1).fillna(0.0)
        res_oracle = run_backtest(ohlcv, oracle, slippage_bps=0, commission_bps=0)
        res_late = run_backtest(ohlcv, oracle.shift(1).fillna(0.0),
                                slippage_bps=0, commission_bps=0)
        assert res_oracle.equity.iloc[-1] > 1.5  # oracle prints money...
        assert res_late.equity.iloc[-1] < res_oracle.equity.iloc[-1] * 0.7

    def test_first_bar_position_not_filled_same_bar(self):
        """pos[0]=1 must fill at bar 1's open, missing bar 0's move."""
        ohlcv = make_ohlcv([100, 150, 150, 150])
        pos = pd.Series([1.0, 1, 1, 1], index=ohlcv.index)
        res = run_backtest(ohlcv, pos, slippage_bps=0, commission_bps=0)
        # held[0] = 0, so the 100->150 open move (bar 0) is not captured
        assert res.returns.iloc[0] == pytest.approx(0.0)
        assert res.equity.iloc[-1] == pytest.approx(1.0)


class TestCosts:
    def test_round_trip_costs_applied(self):
        """Flat prices, one round trip: equity = (1 - c)^2 with c = 6 bps."""
        ohlcv = make_ohlcv([100.0] * 6)
        pos = pd.Series([0, 1.0, 1, 0, 0, 0], index=ohlcv.index)
        res = run_backtest(ohlcv, pos, slippage_bps=5, commission_bps=1)
        c = 6e-4
        assert res.equity.iloc[-1] == pytest.approx((1 - c) ** 2)
        assert len(res.trades) == 2

    def test_costs_default_on(self):
        """Default runs pay costs; zero-cost must be requested explicitly."""
        ohlcv = make_ohlcv([100.0] * 6)
        pos = pd.Series([0, 1.0, 1, 0, 0, 0], index=ohlcv.index)
        res_default = run_backtest(ohlcv, pos)
        res_free = run_backtest(ohlcv, pos, slippage_bps=0, commission_bps=0)
        assert res_default.equity.iloc[-1] < 1.0
        assert res_free.equity.iloc[-1] == pytest.approx(1.0)

    def test_costs_scale_with_turnover(self):
        ohlcv = make_ohlcv([100.0] * 10)
        churn = pd.Series([0, 1.0, 0, 1, 0, 1, 0, 1, 0, 0], index=ohlcv.index)
        lazy = pd.Series([0, 1.0, 1, 1, 1, 1, 1, 1, 1, 1], index=ohlcv.index)
        res_churn = run_backtest(ohlcv, churn)
        res_lazy = run_backtest(ohlcv, lazy)
        assert res_churn.equity.iloc[-1] < res_lazy.equity.iloc[-1]


class TestEngineContracts:
    def test_rejects_nan_positions(self):
        ohlcv = make_ohlcv([100.0] * 5)
        pos = pd.Series([0, np.nan, 1, 1, 0], index=ohlcv.index)
        with pytest.raises(ValueError, match="NaN"):
            run_backtest(ohlcv, pos)

    def test_rejects_mismatched_index(self):
        ohlcv = make_ohlcv([100.0] * 5)
        pos = pd.Series(1.0, index=ohlcv.index[:-1])
        with pytest.raises(ValueError, match="index"):
            run_backtest(ohlcv, pos)

    def test_short_positions_supported(self):
        """-1 position profits when prices fall."""
        ohlcv = make_ohlcv([100, 100, 90, 80, 80])
        pos = pd.Series([-1.0, -1, -1, -1, -1], index=ohlcv.index)
        res = run_backtest(ohlcv, pos, slippage_bps=0, commission_bps=0)
        assert res.equity.iloc[-1] > 1.0

    def test_benchmark_is_long_from_first_fill(self):
        ohlcv = make_ohlcv([100, 100, 110, 121, 121])
        res = buy_and_hold_result(ohlcv, slippage_bps=0, commission_bps=0)
        assert (res.held.iloc[1:] == 1.0).all()
        assert res.equity.iloc[-1] == pytest.approx(1.21)
