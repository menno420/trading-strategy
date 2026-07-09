"""Parameter grids for the P1 known-indicator sweeps.

Grids are defined ONCE here so the sweep scripts, the ledger records and the
tests all count the same variants — the multiple-testing discipline in
docs/founding-plan.md requires the number of variants tried to be reported
alongside any result, so the count must be reproducible.

Each family's grid is bounded (roughly 40-80 variants per family) and
constraint-filtered: combinations the strategy itself would reject
(``fast >= slow``, ``exit > entry``) are excluded up front, so
:func:`variants` yields exactly the configurations that actually run.
"""

from __future__ import annotations

from itertools import product
from typing import Callable

# ---------------------------------------------------------------------------
# P1 trend-following family (lane: trend-following × all-8 × daily)
# ---------------------------------------------------------------------------
# Axes deliberately span fast/slow lookbacks used in the classic literature
# (golden cross 50/200, MACD 12/26/9, turtle Donchian 20/10 and 55/20) plus a
# sensible spread around them. Kept bounded on purpose: every extra variant
# raises the multiple-testing burden on any winner.

_TREND_AXES: dict[str, dict[str, list]] = {
    "sma_crossover": {"fast": [5, 10, 15, 20, 25, 30, 40, 50],
                      "slow": [30, 50, 75, 100, 150, 200]},
    "ema_crossover": {"fast": [5, 10, 15, 20, 25, 30, 40, 50],
                      "slow": [30, 50, 75, 100, 150, 200]},
    "macd": {"fast": [5, 8, 12, 16], "slow": [21, 26, 35, 50],
             "signal": [5, 9, 13]},
    "donchian": {"entry": [10, 15, 20, 30, 40, 55, 80, 100],
                 "exit": [5, 10, 15, 20, 30, 40, 55]},
}

_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "sma_crossover": lambda p: p["fast"] < p["slow"],
    "ema_crossover": lambda p: p["fast"] < p["slow"],
    "macd": lambda p: p["fast"] < p["slow"],
    "donchian": lambda p: p["exit"] <= p["entry"],
}

TREND_FOLLOWING_FAMILIES = tuple(_TREND_AXES)


def variants(family: str) -> list[dict]:
    """All valid parameter dicts for ``family``, constraint-filtered, in a
    deterministic order."""
    try:
        axes = _TREND_AXES[family]
    except KeyError:
        raise ValueError(f"unknown sweep family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def variants_per_family() -> dict[str, int]:
    """Variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(variants(fam)) for fam in TREND_FOLLOWING_FAMILIES}


def total_variants() -> int:
    """Total distinct configurations in the trend-following sweep."""
    return sum(variants_per_family().values())
