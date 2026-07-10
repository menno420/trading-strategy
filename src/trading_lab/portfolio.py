"""Portfolio backtest engine (Round 2 slice R3 — first portfolio-level lane).

Multi-instrument counterpart of :mod:`trading_lab.engine`, with the SAME
execution model, deliberately mirrored (documented, unit-tested):

* A target-weight row decided at bar *t* (from data through bar *t*'s
  close) is EXECUTED AT BAR *t+1*'s OPEN.
* P&L is accounted open-to-open per instrument: the return attributed to
  bar *t* is ``open[t+1] / open[t] - 1`` (the final bar closes out at its
  close). The portfolio's bar return is the held-weight-weighted sum;
  residual weight (1 - sum of weights) is cash earning 0%.
* Costs: every unit of traded weight (|target - drifted weight| at a
  fill) pays ``slippage_bps + commission_bps`` of traded notional, per
  side, charged on the fill bar — the pre-registered "per rebalance
  trade" costs (docs/research-round-2.md §3c, §5).

Between decision rows the book DRIFTS with prices: holdings are fixed in
units, so a weight evolves as ``w * (1 + r) / (1 + r_portfolio)``. Buy &
hold of a basket is therefore a single decision row (equal weights at bar
0, filled at bar 1's open, never rebalanced) — exactly analogous to the
single-instrument ``buy_and_hold_result``.

Approximation shared with the single-instrument engine: costs are
subtracted from the bar return but do not shrink the drifted weights
(second-order at 6 bps per side, ~monthly rebalance).

Target-weight encoding (see ``strategies/xsec_momentum.py``): a row of
NaN means "no decision at this bar — hold the drifted book"; a non-NaN
row is a full weight vector (long-only, sum <= 1). Partially-NaN rows are
rejected.

Research only: this engine simulates; it never touches brokers or orders.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from . import config, metrics
from .walkforward import generate_splits


@dataclass
class PortfolioBacktestResult:
    equity: pd.Series           # compounded portfolio equity, starts at 1.0
    returns: pd.Series          # net per-bar portfolio returns
    held_weights: pd.DataFrame  # weights in force during each bar (post-fill)
    trades: pd.DataFrame        # one row per instrument fill (at bar open)
    cost_bps_per_side: float
    timeframe: str = "daily"
    meta: dict = field(default_factory=dict)


def align_common_index(frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Intersect the instruments' date indexes (pre-reg §3c: walk-forward on
    the aligned COMMON date index; bars any instrument lacks — e.g. BTC-USD
    weekends — are dropped for all). Returns (opens, closes) panels with
    instruments as alphabetically sorted columns."""
    if not frames:
        raise ValueError("no instruments to align")
    tickers = sorted(frames)
    idx = None
    for t in tickers:
        idx = frames[t].index if idx is None else idx.intersection(frames[t].index)
    if len(idx) == 0:
        raise ValueError("aligned common index is empty")
    opens = pd.DataFrame({t: frames[t].loc[idx, "open"] for t in tickers},
                         index=idx)
    closes = pd.DataFrame({t: frames[t].loc[idx, "close"] for t in tickers},
                          index=idx)
    return opens, closes


def _validate_targets(targets: pd.DataFrame, opens: pd.DataFrame) -> np.ndarray:
    if not targets.index.equals(opens.index):
        raise ValueError("targets index must match ohlcv index")
    if list(targets.columns) != list(opens.columns):
        raise ValueError("targets columns must match instrument columns")
    vals = targets.to_numpy(dtype=float)
    nan = np.isnan(vals)
    partial = nan.any(axis=1) & ~nan.all(axis=1)
    if partial.any():
        raise ValueError("target rows must be all-NaN (hold) or fully "
                         "specified weight vectors")
    decisions = vals[~nan.all(axis=1)]
    if decisions.size:
        if (decisions < 0).any():
            raise ValueError("weights must be >= 0 (long-only, no shorting)")
        if (decisions.sum(axis=1) > 1.0 + 1e-9).any():
            raise ValueError("weights must sum to <= 1 (no leverage)")
    return vals


def run_portfolio_backtest(opens: pd.DataFrame, closes: pd.DataFrame,
                           targets: pd.DataFrame, *,
                           slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                           commission_bps: float = config.DEFAULT_COMMISSION_BPS,
                           timeframe: str = "daily") -> PortfolioBacktestResult:
    """Backtest target-weight decisions over aligned (opens, closes) panels.

    ``targets`` rows are decisions at bar ``t`` (NaN row = hold); each
    decision is entered at bar ``t+1``'s open. See module docstring.
    """
    if not opens.index.equals(closes.index) or \
            list(opens.columns) != list(closes.columns):
        raise ValueError("opens and closes must share index and columns")
    if opens.isna().any().any() or closes.isna().any().any():
        raise ValueError("opens/closes contain NaN; align instruments first")
    tvals = _validate_targets(targets, opens)

    o = opens.to_numpy(dtype=float)
    c = closes.to_numpy(dtype=float)
    n_bars, n_inst = o.shape
    # Open-to-open bar returns; the final bar closes out at its close.
    next_open = np.vstack([o[1:], c[-1:]]) if n_bars > 1 else c[-1:]
    bar_ret = next_open / o - 1.0

    # Decision at bar t fills at bar t+1's open.
    exec_targets = np.vstack([np.full((1, n_inst), np.nan), tvals[:-1]])

    cost_per_side = (slippage_bps + commission_bps) / 1e4
    w = np.zeros(n_inst)
    rets = np.zeros(n_bars)
    held = np.zeros((n_bars, n_inst))
    fills: list[tuple] = []
    index = opens.index
    cols = list(opens.columns)
    for t in range(n_bars):
        tgt = exec_targets[t]
        cost = 0.0
        if not np.isnan(tgt).all():
            delta = tgt - w
            for i in np.nonzero(delta != 0.0)[0]:
                fills.append((index[t], cols[i], o[t, i],
                              delta[i], tgt[i]))
            cost = np.abs(delta).sum() * cost_per_side
            w = tgt.copy()
        held[t] = w
        gross = float(w @ bar_ret[t])
        rets[t] = gross - cost
        # Drift: holdings are fixed in units until the next fill.
        w = w * (1.0 + bar_ret[t]) / (1.0 + gross)

    returns = pd.Series(rets, index=index, name="returns")
    equity = (1.0 + returns).cumprod()
    trades = pd.DataFrame(fills, columns=["timestamp", "instrument",
                                          "fill_price", "weight_change",
                                          "weight_after"])
    return PortfolioBacktestResult(
        equity=equity, returns=returns,
        held_weights=pd.DataFrame(held, index=index, columns=cols),
        trades=trades,
        cost_bps_per_side=slippage_bps + commission_bps,
        timeframe=timeframe,
        meta={
            "slippage_bps": slippage_bps,
            "commission_bps": commission_bps,
            "execution": "signal at bar t fills at bar t+1 open",
            "n_bars": int(n_bars),
            "n_instruments": int(n_inst),
        },
    )


def basket_buy_and_hold_result(opens: pd.DataFrame, closes: pd.DataFrame, *,
                               slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                               commission_bps: float = config.DEFAULT_COMMISSION_BPS,
                               timeframe: str = "daily") -> PortfolioBacktestResult:
    """Benchmark: equal-weight basket bought once at the first possible fill
    (bar 1's open), never rebalanced (weights drift), same costs."""
    targets = pd.DataFrame(np.nan, index=opens.index, columns=opens.columns)
    targets.iloc[0] = 1.0 / opens.shape[1]
    return run_portfolio_backtest(opens, closes, targets,
                                  slippage_bps=slippage_bps,
                                  commission_bps=commission_bps,
                                  timeframe=timeframe)


def portfolio_metrics(result: PortfolioBacktestResult) -> dict:
    """Standard metrics for a portfolio result, JSON-serializable.

    Same keys as :func:`trading_lab.metrics.compute_all` where meaningful.
    ``win_rate`` is None: the single-book episode definition does not apply
    to a cross-sectional portfolio. ``turnover_per_year`` is total traded
    |weight| per year across instruments (same units as the engine metric:
    2.0 = one full round trip of the whole book).
    """
    tf = result.timeframe
    years = len(result.returns) / metrics.periods_per_year(tf)
    turnover = float(result.trades["weight_change"].abs().sum()) \
        if len(result.trades) else 0.0
    out = {
        "total_return": metrics.total_return(result.equity),
        "cagr": metrics.cagr(result.equity, tf),
        "sharpe": metrics.sharpe(result.returns, tf),
        "sortino": metrics.sortino(result.returns, tf),
        "max_drawdown": metrics.max_drawdown(result.equity),
        "win_rate": None,
        "turnover_per_year": (turnover / years) if years > 0 else float("nan"),
        "n_bars": int(len(result.equity)),
        "n_trades": int(len(result.trades)),
    }
    return {k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in out.items()}


def portfolio_walk_forward(opens: pd.DataFrame, closes: pd.DataFrame,
                           weight_fn: Callable, grid: list[dict],
                           train_size: int, test_size: int,
                           step: int | None = None, *,
                           timeframe: str = "daily",
                           slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                           commission_bps: float = config.DEFAULT_COMMISSION_BPS) -> dict:
    """Walk-forward for portfolio rules — mirrors
    :func:`trading_lab.walkforward.walk_forward` (identical split scheme,
    pre-reg §5) on the aligned common index.

    With ``grid=[one config]`` the train-window selection is trivial and
    this evaluates the FIXED rule on the stitched OOS test windows — the
    per-config number the pre-registered §6 rule judges. With the full grid
    it reproduces the prior lanes' select-on-train machinery.
    """
    if not grid:
        raise ValueError("empty parameter grid")
    splits = generate_splits(len(opens), train_size, test_size, step)
    if not splits:
        raise ValueError("not enough bars for a single walk-forward split")

    oos_returns = []
    per_split = []
    for sp in splits:
        train_o = opens.iloc[sp.train_start:sp.train_end]
        train_c = closes.iloc[sp.train_start:sp.train_end]
        best_params, best_score = None, float("-inf")
        for params in grid:
            res = run_portfolio_backtest(
                train_o, train_c, weight_fn(train_c, **params),
                slippage_bps=slippage_bps, commission_bps=commission_bps,
                timeframe=timeframe)
            s = metrics.sharpe(res.returns, timeframe)
            if pd.notna(s) and s > best_score:
                best_params, best_score = params, s
        if best_params is None:
            best_params = grid[0]
        # Signals for the test window may use trailing history from before
        # test_start (the ranking is causal), but never anything >= test_end.
        targets = weight_fn(closes.iloc[:sp.test_end], **best_params) \
            .iloc[sp.test_start:sp.test_end]
        test_res = run_portfolio_backtest(
            opens.iloc[sp.test_start:sp.test_end],
            closes.iloc[sp.test_start:sp.test_end], targets,
            slippage_bps=slippage_bps, commission_bps=commission_bps,
            timeframe=timeframe)
        oos_returns.append(test_res.returns)
        per_split.append({"split": sp, "params": best_params,
                          "train_score": best_score,
                          "test_sharpe": metrics.sharpe(test_res.returns,
                                                        timeframe)})

    stitched = pd.concat(oos_returns)
    equity = (1.0 + stitched).cumprod()
    return {
        "splits": per_split,
        "oos_returns": stitched,
        "oos_equity": equity,
        "oos_sharpe": metrics.sharpe(stitched, timeframe),
        "variants_tried": len(grid) * len(splits),
    }
