"""Short-term cross-sectional reversal portfolio (Round 3 slice 7 family
`xsec_reversal`).

The mirror thesis of :mod:`trading_lab.strategies.xsec_momentum`: instead
of chasing the winners, buy the recent LOSERS. Every ``rebalance_every``
bars (weekly, 5, on the aligned common date index — frozen by the lane
declaration in ``trading_lab.sweeps``, NOT swept) rank the instruments by
trailing total return over the short lookback ``N`` and hold the
bottom-``k`` equal-weight (1/k each, long-only, no leverage, no
shorting); between rebalances the book drifts with prices. Long/flat
only: the classic long/short reversal factor's short leg is out of scope
(research rail: this library is long/flat everywhere).

Interface: identical to ``xsec_momentum.generate_weights`` — takes a
**panel** of aligned closes (one column per instrument) and returns a
target-weight DataFrame for
:func:`trading_lab.portfolio.run_portfolio_backtest`. It therefore lives
in ``PORTFOLIO_STRATEGIES``, not ``STRATEGIES``.

Output encoding (same as xsec_momentum): rows are NaN except at
**decision bars** (iloc ``N``, ``N + rebalance_every``, ...). A non-NaN
row at bar ``t`` is the full target-weight vector decided at bar ``t``
(from closes through bar ``t``); the portfolio engine executes it at bar
``t+1``'s open and lets weights drift until the next decision row.

Conventions (ambiguities resolved AGAINST the strategy, mirroring the
Round-2 xsec_momentum card):

* Trailing total return over ``N``: ``close[t] / close[t-N] - 1``, where
  ``N`` counts bars of the aligned common index (not calendar days).
* Warm-up: the first possible decision bar is iloc ``N`` — the earliest
  bar with a full ``N``-bar lookback for every instrument. Before the
  first decision's fill the portfolio is flat (cash, 0%).
* Rebalance schedule: anchored at that first valid decision bar and
  strictly every ``rebalance_every`` bars after it (no schedule drift).
* Ranking ties (equal trailing return): broken deterministically by
  column order (alphabetical ticker for the registered universe) — the
  SAME direction as xsec_momentum's tie-break, so a tied pair resolves to
  the same instrument under both theses (arbitration, not favorability).

Causality: the decision at bar ``t`` uses ``close[t]`` and ``close[t-N]``
only, and the schedule is anchored at a fixed iloc — positions are
prefix-invariant; the engine delays execution to bar ``t+1``'s open.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_weights(closes: pd.DataFrame, N: int = 5, k: int = 2,
                     rebalance_every: int = 5) -> pd.DataFrame:
    """Target-weight rows at decision bars, NaN rows (= hold) elsewhere.

    Long equal-weight the ``k`` WORST trailing-``N``-bar performers.
    """
    if N < 1:
        raise ValueError(f"N ({N}) must be >= 1")
    n_inst = closes.shape[1]
    if not 1 <= k <= n_inst:
        raise ValueError(f"k ({k}) must be in [1, {n_inst}] "
                         f"(number of instruments)")
    if rebalance_every < 1:
        raise ValueError(f"rebalance_every ({rebalance_every}) must be >= 1")
    if closes.isna().any().any():
        raise ValueError("closes contain NaN; align instruments on their "
                         "common date index first")

    trailing = closes / closes.shift(N) - 1.0
    weights = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    tie_break = np.arange(n_inst)
    for t in range(N, len(closes), rebalance_every):
        ret = trailing.iloc[t].to_numpy(dtype=float)
        # primary key: LOWEST trailing return (worst performers first);
        # ties -> lowest column index (alphabetical for the registered
        # universe). np.lexsort sorts by the LAST key first.
        order = np.lexsort((tie_break, ret))
        row = np.zeros(n_inst)
        row[order[:k]] = 1.0 / k
        weights.iloc[t] = row
    return weights
