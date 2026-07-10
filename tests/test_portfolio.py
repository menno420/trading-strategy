"""Portfolio engine tests (Round 2 slice R3): execution timing (t+1 open),
per-side per-trade cost application, drift between rebalances, basket
buy & hold benchmark, validation, and portfolio walk-forward."""

import numpy as np
import pandas as pd
import pytest

from trading_lab.engine import buy_and_hold_result
from trading_lab.portfolio import (align_common_index,
                                   basket_buy_and_hold_result,
                                   portfolio_metrics, portfolio_walk_forward,
                                   run_portfolio_backtest)
from trading_lab.strategies.xsec_momentum import generate_weights

from conftest import make_ohlcv


def make_panel(paths: dict, start="2024-01-01") -> tuple[pd.DataFrame, pd.DataFrame]:
    """(opens, closes) panels from {ticker: price array}; opens == closes."""
    tickers = sorted(paths)
    n = len(next(iter(paths.values())))
    idx = pd.bdate_range(start, periods=n)
    opens = pd.DataFrame({t: np.asarray(paths[t], dtype=float)
                          for t in tickers}, index=idx)
    return opens, opens.copy()


def hold_targets(opens: pd.DataFrame, decisions: dict[int, dict]) -> pd.DataFrame:
    """NaN target frame with explicit decision rows at given iloc positions."""
    targets = pd.DataFrame(np.nan, index=opens.index, columns=opens.columns)
    for t, weights in decisions.items():
        targets.iloc[t] = [weights.get(c, 0.0) for c in opens.columns]
    return targets


class TestExecutionAndCosts:
    def test_decision_fills_at_next_bar_open(self):
        # Constant prices isolate cost effects; a decision at bar 2 must
        # trade at bar 3's open — not bar 2's.
        opens, closes = make_panel({"A": np.full(8, 100.0),
                                    "B": np.full(8, 50.0)})
        targets = hold_targets(opens, {2: {"A": 1.0}})
        res = run_portfolio_backtest(opens, closes, targets,
                                     slippage_bps=100.0, commission_bps=0.0)
        assert len(res.trades) == 1
        fill = res.trades.iloc[0]
        assert fill["timestamp"] == opens.index[3]   # t+1, not t
        assert fill["instrument"] == "A"
        assert fill["fill_price"] == 100.0
        assert fill["weight_change"] == 1.0
        # held in force during bar 3 onward, flat before
        assert (res.held_weights.iloc[:3]["A"] == 0.0).all()
        assert (res.held_weights.iloc[3:]["A"] == 1.0).all()

    def test_cost_charged_per_side_per_trade(self):
        # 100 bps per side for easy arithmetic. Entry trades 1.0 of weight
        # (one side); the A->B rebalance trades 2.0 (sell A + buy B).
        opens, closes = make_panel({"A": np.full(10, 100.0),
                                    "B": np.full(10, 50.0)})
        targets = hold_targets(opens, {2: {"A": 1.0}, 5: {"B": 1.0}})
        res = run_portfolio_backtest(opens, closes, targets,
                                     slippage_bps=100.0, commission_bps=0.0)
        expected = np.zeros(10)
        expected[3] = -0.01          # entry: |1.0| * 1%
        expected[6] = -0.02          # rebalance: (|-1| + |+1|) * 1%
        assert np.allclose(res.returns.to_numpy(), expected)
        assert len(res.trades) == 3  # A in, A out, B in

    def test_slippage_and_commission_both_charged(self):
        opens, closes = make_panel({"A": np.full(6, 100.0)})
        targets = hold_targets(opens, {1: {"A": 1.0}})
        res = run_portfolio_backtest(opens, closes, targets,
                                     slippage_bps=5.0, commission_bps=1.0)
        assert np.isclose(res.returns.iloc[2], -6e-4)

    def test_single_instrument_full_weight_matches_engine_buy_and_hold(self):
        # A 1-column portfolio held at weight 1 must reproduce the
        # single-instrument engine's buy & hold exactly (same execution
        # model, same costs).
        rng = np.random.default_rng(5)
        close = 100.0 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 120)))
        open_ = np.concatenate([[100.0], close[:-1]])
        ohlcv = make_ohlcv(open_, close)
        opens = ohlcv[["open"]].rename(columns={"open": "A"})
        closes = ohlcv[["close"]].rename(columns={"close": "A"})
        port = basket_buy_and_hold_result(opens, closes)
        single = buy_and_hold_result(ohlcv)
        assert np.allclose(port.returns.to_numpy(),
                           single.returns.to_numpy())
        assert np.allclose(port.equity.to_numpy(), single.equity.to_numpy())


class TestDriftAndBenchmark:
    def test_weights_drift_between_rebalances(self):
        # One decision (50/50), zero costs, A grows 10%/bar and B is flat:
        # holdings are fixed in units, so final equity is the average of the
        # two price relatives from the fill bar — NOT the compounded
        # fixed-weight (daily-rebalanced) return.
        n = 8
        a = 100.0 * 1.1 ** np.arange(n)
        opens, closes = make_panel({"A": a, "B": np.full(n, 100.0)})
        targets = hold_targets(opens, {0: {"A": 0.5, "B": 0.5}})
        res = run_portfolio_backtest(opens, closes, targets,
                                     slippage_bps=0.0, commission_bps=0.0)
        drift_value = 0.5 * (a[-1] / a[1]) + 0.5   # buy at bar 1's open
        daily_rebal = (1.0 + 0.05) ** (n - 2)
        assert np.isclose(res.equity.iloc[-1], drift_value)
        assert not np.isclose(res.equity.iloc[-1], daily_rebal)
        assert len(res.trades) == 2                # entry fills only

    def test_basket_buy_and_hold_single_entry(self):
        rng = np.random.default_rng(9)
        paths = {t: 100.0 * np.exp(np.cumsum(rng.normal(0, 0.02, 60)))
                 for t in ("A", "B", "C")}
        opens, closes = make_panel(paths)
        res = basket_buy_and_hold_result(opens, closes,
                                         slippage_bps=0.0, commission_bps=0.0)
        assert len(res.trades) == 3                # one fill per instrument
        expected = np.mean([paths[t][-1] / paths[t][1] for t in paths])
        assert np.isclose(res.equity.iloc[-1], expected)

    def test_portfolio_metrics_shape(self):
        opens, closes = make_panel({"A": np.linspace(100, 150, 60),
                                    "B": np.linspace(100, 90, 60)})
        m = portfolio_metrics(basket_buy_and_hold_result(opens, closes))
        assert set(m) == {"total_return", "cagr", "sharpe", "sortino",
                          "max_drawdown", "win_rate", "turnover_per_year",
                          "n_bars", "n_trades"}
        assert m["win_rate"] is None               # undefined for a book
        assert m["n_trades"] == 2
        assert m["turnover_per_year"] > 0


class TestValidation:
    def test_rejects_partial_nan_decision_row(self):
        opens, closes = make_panel({"A": np.full(6, 100.0),
                                    "B": np.full(6, 100.0)})
        targets = pd.DataFrame(np.nan, index=opens.index,
                               columns=opens.columns)
        targets.iloc[2, 0] = 0.5                   # B left NaN
        with pytest.raises(ValueError, match="all-NaN"):
            run_portfolio_backtest(opens, closes, targets)

    def test_rejects_shorts_and_leverage(self):
        opens, closes = make_panel({"A": np.full(6, 100.0),
                                    "B": np.full(6, 100.0)})
        with pytest.raises(ValueError, match="long-only"):
            run_portfolio_backtest(opens, closes,
                                   hold_targets(opens, {2: {"A": -0.5,
                                                            "B": 0.5}}))
        with pytest.raises(ValueError, match="leverage"):
            run_portfolio_backtest(opens, closes,
                                   hold_targets(opens, {2: {"A": 0.8,
                                                            "B": 0.8}}))

    def test_rejects_index_mismatch(self):
        opens, closes = make_panel({"A": np.full(6, 100.0)})
        targets = hold_targets(opens, {1: {"A": 1.0}}).iloc[:-1]
        with pytest.raises(ValueError, match="index"):
            run_portfolio_backtest(opens, closes, targets)

    def test_align_common_index_intersects(self):
        a = make_ohlcv(np.full(10, 100.0))
        b = make_ohlcv(np.full(8, 50.0)).iloc[2:]  # starts 2 bars later
        opens, closes = align_common_index({"A": a, "B": b})
        assert list(opens.columns) == ["A", "B"]
        assert opens.index.equals(a.index.intersection(b.index))
        assert not closes.isna().any().any()


class TestPortfolioWalkForward:
    def make_universe(self, n=260, n_inst=4, seed=3):
        rng = np.random.default_rng(seed)
        paths = {f"T{i}": 100.0 * np.exp(np.cumsum(rng.normal(0.0004, 0.02, n)))
                 for i in range(n_inst)}
        return make_panel(paths)

    def test_fixed_rule_oos_stitch(self):
        opens, closes = self.make_universe()
        wf = portfolio_walk_forward(opens, closes, generate_weights,
                                    [{"L": 21, "k": 2,
                                      "rebalance_every": 21}],
                                    train_size=100, test_size=50)
        n_splits = len(wf["splits"])
        assert n_splits == (len(opens) - 100 - 50) // 50 + 1
        assert len(wf["oos_returns"]) == n_splits * 50
        assert wf["variants_tried"] == n_splits    # 1-config grid
        for s in wf["splits"]:                      # nothing to select
            assert s["params"] == {"L": 21, "k": 2, "rebalance_every": 21}

    def test_selection_grid_bookkeeping(self):
        opens, closes = self.make_universe(seed=8)
        grid = [{"L": 21, "k": 2, "rebalance_every": 21},
                {"L": 42, "k": 2, "rebalance_every": 21}]
        wf = portfolio_walk_forward(opens, closes, generate_weights, grid,
                                    train_size=100, test_size=50)
        assert wf["variants_tried"] == 2 * len(wf["splits"])
        assert all(s["params"] in grid for s in wf["splits"])

    def test_oos_test_window_uses_trailing_history(self):
        # The test-window targets are computed on the full prefix, so a
        # decision can land on the window's FIRST bar (lookback from
        # history before test_start) — the stitch must not silently lose
        # the schedule.
        opens, closes = self.make_universe(n=210)
        wf = portfolio_walk_forward(opens, closes, generate_weights,
                                    [{"L": 50, "k": 1,
                                      "rebalance_every": 50}],
                                    train_size=100, test_size=50)
        # windows start at iloc 100, 150, 200... schedule fires at 50, 100,
        # 150 — so each test window holds a position, not permanent cash.
        assert (wf["oos_returns"] != 0.0).any()
