"""Metrics tests with hand-computed expected values."""

import math

import pandas as pd
import pytest

from trading_lab import metrics
from trading_lab.engine import BacktestResult, run_backtest

from conftest import make_ohlcv


def _series(values):
    return pd.Series(values, index=pd.bdate_range("2024-01-01", periods=len(values)))


class TestBasics:
    def test_total_return(self):
        equity = (1 + _series([0.10, -0.05])).cumprod()
        # 1.10 * 0.95 = 1.045
        assert metrics.total_return(equity) == pytest.approx(0.045)

    def test_max_drawdown_hand_computed(self):
        equity = _series([1.0, 1.2, 0.9, 1.1])
        # trough 0.9 from peak 1.2 -> -25%
        assert metrics.max_drawdown(equity) == pytest.approx(-0.25)

    def test_max_drawdown_monotonic_up_is_zero(self):
        equity = _series([1.0, 1.1, 1.2, 1.3])
        assert metrics.max_drawdown(equity) == pytest.approx(0.0)

    def test_cagr_doubling_in_one_year(self):
        # 252 daily bars ending at 2.0 -> exactly one year -> CAGR = 100%
        equity = _series([2.0 ** ((i + 1) / 252) for i in range(252)])
        assert metrics.cagr(equity, "daily") == pytest.approx(1.0, rel=1e-9)

    def test_sharpe_hand_computed(self):
        # returns 1%, 2%, 3%: mean = 0.02, std(ddof=1) = 0.01
        # daily sharpe = 0.02 / 0.01 * sqrt(252) = 2 * sqrt(252)
        r = _series([0.01, 0.02, 0.03])
        assert metrics.sharpe(r, "daily") == pytest.approx(2 * math.sqrt(252))

    def test_sharpe_hourly_annualization(self):
        # same returns, hourly: uses 252 * 6.5 periods per year
        r = _series([0.01, 0.02, 0.03])
        assert metrics.sharpe(r, "hourly") == pytest.approx(2 * math.sqrt(252 * 6.5))

    def test_sharpe_zero_variance_is_nan(self):
        assert math.isnan(metrics.sharpe(_series([0.01, 0.01, 0.01]), "daily"))

    def test_sortino_hand_computed(self):
        # returns 1%, -2%, 3%: mean = 2/300, downside dev = sqrt(0.02^2) = 0.02
        # sortino = (0.02/3) / 0.02 * sqrt(252) = sqrt(252)/3
        r = _series([0.01, -0.02, 0.03])
        assert metrics.sortino(r, "daily") == pytest.approx(math.sqrt(252) / 3)

    def test_unknown_timeframe_rejected(self):
        with pytest.raises(ValueError, match="timeframe"):
            metrics.periods_per_year("weekly")


class TestTradeLevel:
    def _result(self, held_vals, ret_vals):
        idx = pd.bdate_range("2024-01-01", periods=len(held_vals))
        held = pd.Series(held_vals, index=idx, dtype=float)
        rets = pd.Series(ret_vals, index=idx, dtype=float)
        return BacktestResult(equity=(1 + rets).cumprod(), returns=rets,
                              held=held, trades=pd.DataFrame(),
                              cost_bps_per_side=0.0, timeframe="daily")

    def test_win_rate_hand_computed(self):
        # episode 1 (bars 0-1, +10%) wins; episode 2 (bars 3-4, -5%) loses
        res = self._result([1, 1, 0, 1, 1], [0.10, 0.0, 0.0, -0.05, 0.0])
        assert metrics.win_rate(res) == pytest.approx(0.5)

    def test_win_rate_nan_when_never_positioned(self):
        res = self._result([0, 0, 0], [0.0, 0.0, 0.0])
        assert math.isnan(metrics.win_rate(res))

    def test_turnover_hand_computed(self):
        # one round trip (enter +1, exit -1 => total 2.0) over 252 bars = 1 yr
        held = [0.0] * 252
        held[10:200] = [1.0] * 190
        res = self._result(held, [0.0] * 252)
        assert metrics.turnover_per_year(res) == pytest.approx(2.0)

    def test_compute_all_schema_and_json_safety(self):
        ohlcv = make_ohlcv([100.0] * 30)
        pos = pd.Series(0.0, index=ohlcv.index)
        res = run_backtest(ohlcv, pos)
        out = metrics.compute_all(res)
        expected_keys = {"total_return", "cagr", "sharpe", "sortino",
                         "max_drawdown", "win_rate", "turnover_per_year",
                         "n_bars", "n_trades"}
        assert set(out) == expected_keys
        # flat/no-trade run: NaNs become None (JSON-safe), never NaN
        assert out["sharpe"] is None
        assert out["win_rate"] is None
        assert out["n_trades"] == 0
