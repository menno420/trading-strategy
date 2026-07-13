"""weekday_long strategy tests — Round 4 slice R4-F (day-of-week
seasonality). Positions must flag exactly the chosen weekday's bars and
respect the house signal-at-t / fill-at-t+1-open convention."""

import numpy as np
import pandas as pd
import pytest

from conftest import make_ohlcv
from trading_lab.engine import run_backtest
from trading_lab.strategies import DEFAULT_PARAMS, STRATEGIES, weekday_long


@pytest.fixture
def week_frame() -> pd.DataFrame:
    """Two full business weeks starting on a Monday (2024-01-01)."""
    return make_ohlcv([100.0] * 10, start="2024-01-01", freq="B")


class TestWeekdayLongPositions:
    def test_positions_flag_exactly_the_chosen_weekday(self, week_frame):
        assert week_frame.index[0].dayofweek == 0  # fixture starts Monday
        for d in range(5):
            pos = weekday_long.generate(week_frame, weekday=d)
            expected = (week_frame.index.dayofweek == d).astype(float)
            assert (pos.values == expected).all()
            assert pos.sum() == 2.0  # two of each weekday in two weeks

    def test_positions_are_clean_zero_one(self, week_frame):
        pos = weekday_long.generate(week_frame, weekday=3)
        assert not pos.isna().any()
        assert set(pos.unique()) <= {0.0, 1.0}
        assert pos.index.equals(week_frame.index)
        assert pos.name == "position"

    def test_weekend_variants_flat_on_business_days(self, week_frame):
        # 5/6 are accepted (BTC weekend bars exist) but a business-day
        # frame never triggers them; they are NOT in the registered grid.
        for d in (5, 6):
            assert weekday_long.generate(week_frame, weekday=d).sum() == 0.0

    def test_seven_day_index_btc_like(self):
        # BTC-USD's committed cache trades 7 days a week: the registered
        # variants stay flat on Sat/Sun bars.
        frame = make_ohlcv([100.0] * 14, start="2024-01-01", freq="D")
        pos = weekday_long.generate(frame, weekday=0)
        dow = frame.index.dayofweek
        assert (pos[dow == 0] == 1.0).all()
        assert (pos[dow != 0] == 0.0).all()
        assert (pos[(dow == 5) | (dow == 6)] == 0.0).all()

    def test_invalid_weekday_rejected(self, week_frame):
        for bad in (-1, 7, 2.5, "monday", None, True):
            with pytest.raises(ValueError, match="weekday"):
                weekday_long.generate(week_frame, weekday=bad)

    def test_variants_tile_the_week(self, week_frame):
        # Every business-day bar is flagged by exactly one of the five
        # registered variants — no calendar effect can hide between them.
        total = sum(weekday_long.generate(week_frame, weekday=d)
                    for d in range(5))
        assert (total == 1.0).all()


class TestWeekdayLongFillConvention:
    def test_signal_at_t_fills_at_t_plus_1_open(self):
        # House rail: pos[t]=1 on day-d bars means held[t+1]=1 — the
        # variant labeled weekday=d earns the open(t+1) -> open(t+2)
        # return after each day-d bar (documented in the module docstring).
        opens = [100.0] * 10
        opens[2] = 110.0  # Wednesday open jump: Tue-open -> Wed-open +10%
        frame = make_ohlcv(opens, start="2024-01-01", freq="B")
        pos = weekday_long.generate(frame, weekday=0)  # signal Mondays
        res = run_backtest(frame, pos, slippage_bps=0.0, commission_bps=0.0)
        # Position is in force during Tuesday bars only.
        expected_held = pos.shift(1).fillna(0.0)
        assert (res.held == expected_held).all()
        assert (res.held[frame.index.dayofweek == 1] == 1.0).all()
        assert (res.held[frame.index.dayofweek != 1] == 0.0).all()
        # The zero-cost return on the first Tuesday is the open-to-open
        # move into Wednesday.
        tuesday = frame.index[1]
        assert res.returns.loc[tuesday] == pytest.approx(0.10)
        assert res.returns.drop(tuesday).abs().max() == pytest.approx(0.0)

    def test_registry_and_default_params(self, week_frame):
        pos = STRATEGIES["weekday_long"](week_frame,
                                         **DEFAULT_PARAMS["weekday_long"])
        assert (pos.values
                == (week_frame.index.dayofweek == 0).astype(float)).all()

    def test_costs_charged_on_turnover(self, week_frame):
        # One long day per week = 2 sides per week; net Sharpe must not
        # exceed the zero-cost run on the same positions.
        pos = weekday_long.generate(week_frame, weekday=2)
        gross = run_backtest(week_frame, pos, slippage_bps=0.0,
                             commission_bps=0.0)
        net = run_backtest(week_frame, pos)  # default 5 bps + 1 bp
        assert net.equity.iloc[-1] < gross.equity.iloc[-1]
        # 2 entries + 2 exits over the fixture = 4 unit-turnover fills.
        assert len(net.trades) == 4

    def test_strictly_causal_prefix_property(self):
        # positions[:k] computed on a prefix equal positions computed on
        # the full frame (no lookahead — pure function of each bar's own
        # timestamp).
        rng = np.random.default_rng(7)
        closes = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.01, 60)))
        frame = make_ohlcv(closes, start="2024-03-04", freq="B")
        full = weekday_long.generate(frame, weekday=1)
        for k in (10, 30, 59):
            prefix = weekday_long.generate(frame.iloc[:k], weekday=1)
            assert (prefix == full.iloc[:k]).all()
