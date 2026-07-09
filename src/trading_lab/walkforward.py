"""Walk-forward split helper (founding-plan: walk-forward only).

Parameters are fit on a training window and scored on the FOLLOWING unseen
test window, rolling forward through history. No single-split in-sample
result is ever a finding.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable

import pandas as pd

from . import config, metrics
from .engine import run_backtest


@dataclass(frozen=True)
class Split:
    """Positional (iloc) boundaries; train is [train_start, train_end),
    test is [test_start, test_end), with test_start == train_end."""
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def generate_splits(n_bars: int, train_size: int, test_size: int,
                    step: int | None = None) -> list[Split]:
    """Rolling walk-forward splits over ``n_bars`` observations.

    Each split trains on ``train_size`` bars and tests on the next
    ``test_size`` bars; windows advance by ``step`` (default: ``test_size``,
    i.e. contiguous non-overlapping test windows).
    """
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive")
    step = step or test_size
    if step <= 0:
        raise ValueError("step must be positive")
    splits = []
    start = 0
    while start + train_size + test_size <= n_bars:
        splits.append(Split(
            train_start=start,
            train_end=start + train_size,
            test_start=start + train_size,
            test_end=start + train_size + test_size,
        ))
        start += step
    return splits


def _param_grid(grid: dict[str, Iterable] | list[dict]) -> list[dict]:
    """Expand a ``{param: values}`` grid to its cartesian product, or pass an
    explicit list of param dicts through unchanged (for grids with constraints
    such as fast < slow, where the full product contains invalid combos)."""
    if not grid:
        raise ValueError("empty parameter grid")
    if isinstance(grid, list):
        return list(grid)
    keys = list(grid)
    return [dict(zip(keys, combo)) for combo in product(*(grid[k] for k in keys))]


def walk_forward(ohlcv: pd.DataFrame, strategy_fn: Callable,
                 grid: dict[str, Iterable] | list[dict],
                 train_size: int, test_size: int, step: int | None = None, *,
                 timeframe: str = "daily",
                 slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                 commission_bps: float = config.DEFAULT_COMMISSION_BPS,
                 score: Callable | None = None) -> dict:
    """Fit params on each train window (best in-sample score), apply to the
    following test window; stitch the out-of-sample test returns together.

    Returns a dict with per-split choices, stitched OOS returns/equity, and
    ``variants_tried`` (grid size × splits — multiple-testing discipline).
    """
    score = score or (lambda res: metrics.sharpe(res.returns, timeframe))
    combos = _param_grid(grid)
    if not combos:
        raise ValueError("empty parameter grid")
    splits = generate_splits(len(ohlcv), train_size, test_size, step)
    if not splits:
        raise ValueError("not enough bars for a single walk-forward split")

    oos_returns = []
    per_split = []
    for sp in splits:
        train = ohlcv.iloc[sp.train_start:sp.train_end]
        test = ohlcv.iloc[sp.test_start:sp.test_end]
        best_params, best_score = None, float("-inf")
        for params in combos:
            res = run_backtest(train, strategy_fn(train, **params),
                               slippage_bps=slippage_bps,
                               commission_bps=commission_bps,
                               timeframe=timeframe)
            s = score(res)
            if pd.notna(s) and s > best_score:
                best_params, best_score = params, s
        if best_params is None:  # e.g. no combo ever traded on this window
            best_params = combos[0]
        # Signals for the test window may use trailing history from before
        # test_start (indicators are causal), but never anything >= test_end.
        signal_frame = ohlcv.iloc[:sp.test_end]
        pos_test = strategy_fn(signal_frame, **best_params).iloc[sp.test_start:sp.test_end]
        test_res = run_backtest(test, pos_test,
                                slippage_bps=slippage_bps,
                                commission_bps=commission_bps,
                                timeframe=timeframe)
        oos_returns.append(test_res.returns)
        per_split.append({"split": sp, "params": best_params,
                          "train_score": best_score,
                          "test_sharpe": metrics.sharpe(test_res.returns, timeframe)})

    stitched = pd.concat(oos_returns)
    equity = (1.0 + stitched).cumprod()
    return {
        "splits": per_split,
        "oos_returns": stitched,
        "oos_equity": equity,
        "oos_sharpe": metrics.sharpe(stitched, timeframe),
        "variants_tried": len(combos) * len(splits),
    }
