"""Cross-sectional momentum portfolio (Round 2 family `xsec_momentum`).

First portfolio-level family (docs/research-round-2.md §3c): one strategy
over all 9 cached daily instruments as a single portfolio. Every 21 bars
(on the aligned common date index) rank the instruments by trailing total
return over lookback ``L`` and hold the top-``k`` equal-weight (1/k each,
long-only, no leverage); between rebalances the book drifts with prices.

Interface: unlike the single-instrument strategies in this package,
:func:`generate_weights` takes a **panel** of aligned closes (one column
per instrument) and returns a target-weight DataFrame for
:func:`trading_lab.portfolio.run_portfolio_backtest`. It therefore lives
in ``PORTFOLIO_STRATEGIES``, not ``STRATEGIES``.

Output encoding: rows are NaN except at **decision bars** (iloc ``L``,
``L + rebalance_every``, ...). A non-NaN row at bar ``t`` is the full
target-weight vector decided at bar ``t`` (from closes through bar ``t``);
the portfolio engine executes it at bar ``t+1``'s open and lets weights
drift until the next decision row.

Conventions (ambiguities resolved AGAINST the strategy per pre-reg §6, and
recorded in docs/research-round-2-results.md):

* Trailing total return over ``L``: ``close[t] / close[t-L] - 1``, where
  ``L`` counts bars of the aligned common index (not calendar days).
* Warm-up: the first possible decision bar is iloc ``L`` — the earliest
  bar with a full ``L``-bar lookback for every instrument. Before the
  first decision's fill the portfolio is flat (cash, 0%): a ranking
  cannot be confirmed before the lookback exists.
* Rebalance schedule: anchored at that first valid decision bar and
  strictly every ``rebalance_every`` bars after it (no drift of the
  schedule). ``rebalance_every`` is frozen at 21 by the pre-registration
  and is NOT swept.
* Ranking ties (equal trailing return): broken deterministically by
  column order (alphabetical ticker for the registered universe). Ties
  are measure-zero on real prices; the break is arbitration, not a
  favorability choice.

Causality: the decision at bar ``t`` uses ``close[t]`` and ``close[t-L]``
only, and the schedule is anchored at a fixed iloc — positions are
prefix-invariant; the engine delays execution to bar ``t+1``'s open.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_weights(closes: pd.DataFrame, L: int = 126, k: int = 2,
                     rebalance_every: int = 21) -> pd.DataFrame:
    """Target-weight rows at decision bars, NaN rows (= hold) elsewhere."""
    if L < 1:
        raise ValueError(f"L ({L}) must be >= 1")
    n_inst = closes.shape[1]
    if not 1 <= k <= n_inst:
        raise ValueError(f"k ({k}) must be in [1, {n_inst}] "
                         f"(number of instruments)")
    if rebalance_every < 1:
        raise ValueError(f"rebalance_every ({rebalance_every}) must be >= 1")
    if closes.isna().any().any():
        raise ValueError("closes contain NaN; align instruments on their "
                         "common date index first")

    momentum = closes / closes.shift(L) - 1.0
    weights = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    tie_break = np.arange(n_inst)
    for t in range(L, len(closes), rebalance_every):
        mom = momentum.iloc[t].to_numpy(dtype=float)
        # primary key: highest trailing return; ties -> lowest column index
        # (alphabetical for the registered universe). np.lexsort sorts by
        # the LAST key first.
        order = np.lexsort((tie_break, -mom))
        row = np.zeros(n_inst)
        row[order[:k]] = 1.0 / k
        weights.iloc[t] = row
    return weights
