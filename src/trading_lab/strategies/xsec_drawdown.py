"""Cross-sectional drawdown-ranking portfolio family (Round 7D, R7-D).

`generate_weights(closes, L, k, rebalance_every) -> pd.DataFrame` -- at each
rebalance bar, rank the aligned basket by depth-from-trailing-peak
(close / trailing-L-bar-max - 1, <= 0) and go long the deepest k names
equal-weight (1/k); all other bars are all-NaN (hold the drifted book).
Long-only, weights sum to 1 at each decision bar; cash before the first
decision at iloc L.

Ranks on a DRAWDOWN STATE (depth from a trailing L-bar close peak),
distinct from xsec_momentum / xsec_reversal which rank on trailing
point-to-point return. Causal + prefix-invariant (rolling max through bar
t; schedule anchored at the panel's first bar), preserving the
portfolio_walk_forward prefix-slice contract.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_weights(closes: pd.DataFrame, L: int = 126, k: int = 2,
                     rebalance_every: int = 21) -> pd.DataFrame:
    if L < 2:
        raise ValueError(f"L ({L}) must be >= 2")
    n_inst = closes.shape[1]
    if not 1 <= k <= n_inst:
        raise ValueError(f"k ({k}) must be in [1, {n_inst}] (number of instruments)")
    if rebalance_every < 1:
        raise ValueError(f"rebalance_every ({rebalance_every}) must be >= 1")
    if closes.isna().any().any():
        raise ValueError("closes contain NaN; align instruments on their "
                         "common date index first")

    depth = closes / closes.rolling(L).max() - 1.0  # <= 0; deepest = most negative
    weights = pd.DataFrame(np.nan, index=closes.index, columns=closes.columns)
    tie_break = np.arange(n_inst)
    for t in range(L, len(closes), rebalance_every):
        d = depth.iloc[t].to_numpy(dtype=float)
        # ascending: most-negative depth (deepest drawdown) first;
        # ties -> lowest column index (alphabetical). lexsort: last key primary.
        order = np.lexsort((tie_break, d))
        row = np.zeros(n_inst)
        row[order[:k]] = 1.0 / k
        weights.iloc[t] = row
    return weights
