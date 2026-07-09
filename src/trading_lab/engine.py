"""Vectorized backtest engine.

Execution model (documented, unit-tested, binding for the lab):

* A signal/position decided on bar *t* (using data through bar *t*'s close)
  is EXECUTED AT BAR *t+1*'s OPEN. Internally: ``held = positions.shift(1)``
  — ``held[t]`` is the position in force during bar *t*, entered at
  ``open[t]``.
* P&L is accounted open-to-open: the return attributed to bar *t* is
  ``open[t+1] / open[t] - 1`` (the final bar closes out at its close).
  The equity value at index *t* is therefore marked as of bar *t+1*'s open.
* Costs: every unit of turnover (|change in held position|) pays
  ``slippage_bps + commission_bps`` of traded notional, per side. Defaults
  come from :mod:`trading_lab.config`; a zero-cost run must be requested
  explicitly (``slippage_bps=0, commission_bps=0``).

Positions may be -1/0/1 (short allowed) or 0/1 (long/flat); fractional
weights in [-1, 1] also work.

Research only: this engine simulates; it never touches brokers or orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import config


@dataclass
class BacktestResult:
    equity: pd.Series          # compounded equity curve, starts at 1.0
    returns: pd.Series         # net per-bar strategy returns
    held: pd.Series            # position in force during each bar
    trades: pd.DataFrame       # one row per position change (fills at bar open)
    cost_bps_per_side: float
    timeframe: str = "daily"
    meta: dict = field(default_factory=dict)


def run_backtest(ohlcv: pd.DataFrame, positions: pd.Series, *,
                 slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                 commission_bps: float = config.DEFAULT_COMMISSION_BPS,
                 timeframe: str = "daily") -> BacktestResult:
    """Run a vectorized backtest of ``positions`` over ``ohlcv``.

    ``positions[t]`` is the target position decided at bar ``t`` (from data
    through bar ``t``); it is entered at bar ``t+1``'s open. See module
    docstring for the full execution model.
    """
    if not ohlcv.index.equals(positions.index):
        raise ValueError("positions index must match ohlcv index")
    if positions.isna().any():
        raise ValueError("positions contain NaN; strategies must emit a "
                         "position (possibly 0) for every bar")
    pos = positions.astype(float)
    if (pos.abs() > 1).any():
        raise ValueError("positions must lie in [-1, 1]")

    opens = ohlcv["open"].astype(float)
    closes = ohlcv["close"].astype(float)

    # Position in force during bar t (entered at open[t], decided at bar t-1).
    held = pos.shift(1).fillna(0.0)

    # Open-to-open bar returns; final bar closes out at its close.
    next_open = opens.shift(-1)
    next_open.iloc[-1] = closes.iloc[-1]
    bar_ret = next_open / opens - 1.0

    gross = held * bar_ret

    # Turnover and costs (charged at the open where the fill happens).
    turnover = held.diff()
    turnover.iloc[0] = held.iloc[0]
    cost_per_side = (slippage_bps + commission_bps) / 1e4
    costs = turnover.abs() * cost_per_side

    net = gross - costs
    equity = (1.0 + net).cumprod()

    fills = turnover[turnover != 0]
    trades = pd.DataFrame({
        "timestamp": fills.index,
        "fill_price": opens.loc[fills.index],
        "size_change": fills.values,
        "position_after": held.loc[fills.index],
    }).reset_index(drop=True)

    return BacktestResult(
        equity=equity, returns=net, held=held, trades=trades,
        cost_bps_per_side=slippage_bps + commission_bps,
        timeframe=timeframe,
        meta={
            "slippage_bps": slippage_bps,
            "commission_bps": commission_bps,
            "execution": "signal at bar t fills at bar t+1 open",
            "n_bars": int(len(ohlcv)),
        },
    )


def buy_and_hold_result(ohlcv: pd.DataFrame, *,
                        slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                        commission_bps: float = config.DEFAULT_COMMISSION_BPS,
                        timeframe: str = "daily") -> BacktestResult:
    """Benchmark: long 1 unit from the first possible fill, same costs."""
    positions = pd.Series(1.0, index=ohlcv.index)
    return run_backtest(ohlcv, positions, slippage_bps=slippage_bps,
                        commission_bps=commission_bps, timeframe=timeframe)
