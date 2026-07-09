"""Performance metrics, annualization-aware per timeframe.

Annualization factors come from :data:`trading_lab.config.PERIODS_PER_YEAR`
(daily = 252, hourly = 252 * 6.5). All ratios use a zero risk-free rate.
"""

from __future__ import annotations

import math

import pandas as pd

from . import config
from .engine import BacktestResult


def periods_per_year(timeframe: str) -> float:
    try:
        return config.PERIODS_PER_YEAR[timeframe]
    except KeyError:
        raise ValueError(f"unknown timeframe {timeframe!r}") from None


def total_return(equity: pd.Series) -> float:
    return float(equity.iloc[-1] - 1.0)


def cagr(equity: pd.Series, timeframe: str) -> float:
    n = len(equity)
    if n == 0 or equity.iloc[-1] <= 0:
        return float("nan")
    years = n / periods_per_year(timeframe)
    if years <= 0:
        return float("nan")
    return float(equity.iloc[-1] ** (1.0 / years) - 1.0)


def sharpe(returns: pd.Series, timeframe: str) -> float:
    sd = returns.std(ddof=1)
    if sd == 0 or math.isnan(sd):
        return float("nan")
    return float(returns.mean() / sd * math.sqrt(periods_per_year(timeframe)))


def sortino(returns: pd.Series, timeframe: str) -> float:
    downside = returns[returns < 0]
    if len(downside) == 0:
        return float("nan")
    dd = math.sqrt(float((downside ** 2).mean()))
    if dd == 0:
        return float("nan")
    return float(returns.mean() / dd * math.sqrt(periods_per_year(timeframe)))


def max_drawdown(equity: pd.Series) -> float:
    """Most negative peak-to-trough drawdown (a negative number)."""
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def win_rate(result: BacktestResult) -> float:
    """Fraction of round-trip position episodes with positive net P&L.

    An episode is a maximal run of bars with the same nonzero held position.
    NaN when the strategy never held a position.
    """
    held = result.held
    episode_id = (held != held.shift()).cumsum()
    wins = 0
    total = 0
    for _, seg in result.returns.groupby(episode_id):
        if held.loc[seg.index[0]] == 0:
            continue
        total += 1
        if (1.0 + seg).prod() - 1.0 > 0:
            wins += 1
    if total == 0:
        return float("nan")
    return wins / total


def turnover_per_year(result: BacktestResult) -> float:
    """Total |position change| per year (2.0 = one full round trip)."""
    delta = result.held.diff()
    delta.iloc[0] = result.held.iloc[0]
    years = len(result.held) / periods_per_year(result.timeframe)
    if years <= 0:
        return float("nan")
    return float(delta.abs().sum() / years)


def compute_all(result: BacktestResult) -> dict:
    """All standard metrics for a backtest result, JSON-serializable."""
    tf = result.timeframe
    out = {
        "total_return": total_return(result.equity),
        "cagr": cagr(result.equity, tf),
        "sharpe": sharpe(result.returns, tf),
        "sortino": sortino(result.returns, tf),
        "max_drawdown": max_drawdown(result.equity),
        "win_rate": win_rate(result),
        "turnover_per_year": turnover_per_year(result),
        "n_bars": int(len(result.equity)),
        "n_trades": int(len(result.trades)),
    }
    return {k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in out.items()}
