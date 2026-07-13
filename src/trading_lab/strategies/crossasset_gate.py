"""Cross-asset momentum exposure gate (Round 4 family `crossasset_gate`,
slice R4-E).

Pre-registered in ``docs/research-round-4-plan.md`` § R4-E — Cross-asset
lead-lag filter (with ungated control arm): gate the exposure of existing
SPY/QQQ trend-family variants on the momentum sign of a DIFFERENT
instrument (TLT, plus XOM and GLD as pre-declared alternates), and grade
the gated arm head-to-head against an **ungated control arm** (the same
equity component, no gate). Motivating round-3/4 results: PR #92 (the vol
gate's control arm beat the gated arm 6/6) and PR #104 (the trend-strength
control split 3/3 and conditioning still produced zero candidates) — the
informed prior is failure, which is exactly why the slice is worth
running. Registered hypothesis: **null expected**.

Equity component (FROZEN, not swept — a committed grid point of the
round-3 trend sweep on these instruments; no new parameter territory):
``ema_crossover(fast=trend_fast, slow=trend_slow)`` — the
r3-trend-new-tickers grid point (20, 100) by default (PR #90), the same
freeze PR #104 used.

Gate (the ONLY new logic — this is the program's first strategy that
consumes a SECOND instrument's series):

* gate momentum = ``gate_close / gate_close.shift(gate_lookback) - 1``,
  computed on the GATE ASSET'S OWN calendar (strictly trailing);
* the momentum series is aligned onto the equity's index with
  ``reindex(ohlcv.index, method="ffill")`` — the gate value applied at
  equity bar *t* is the most recent gate-asset value with timestamp
  **<= t** (NO lookahead: a gate bar stamped after *t* can never
  influence the position decided at *t*);
* the gate is OPEN at bar *t* iff that aligned momentum is **> 0**
  (long-only-when-gate-momentum-positive, the registered sign rule);
  position = equity trend component where the gate is open, 0 elsewhere.

Warm-up / ambiguity resolve AGAINST the strategy (the house
`vol_filtered_trend` convention): equity bars where the aligned gate
momentum is undefined (gate warm-up, or no gate bar <= t exists) are
flat. The engine then delays execution to bar t+1's open as everywhere
else in the lab — gate-asset data <= t decides the position filled at
t+1.

Control arm (``gated=False``): the SAME frozen equity component with the
gate removed — plain ``ema_crossover(trend_fast, trend_slow)`` on the
equity, exactly the vol-gate/R4-D "flat" control structure. The control
arm never loads or computes any gate-asset data: its output is invariant
to ``gate_asset``, ``gate_lookback`` and ``gate_close`` (pinned by
tests). Costs, execution and rail are identical across arms — the arms
differ ONLY in the gate.

Data: when ``gate_close`` is not supplied, the gate series is loaded via
the dev rail ``trading_lab.data.load_ohlcv(gate_asset, "daily")`` —
holdout bars are excluded by the loader's default; ``unlock_holdout`` is
never passed. Committed caches only (TLT/XOM/GLD, PRs #90–#92). The
loaded close series is cached per gate asset (module-level, read-only).
Tests inject synthetic ``gate_close`` series directly.

Causality: EMAs are recursive (trailing), the gate momentum is a trailing
ratio on the gate calendar, and the ffill alignment only ever looks
BACKWARD in time — positions[t] depends only on equity and gate data
through bar t (prefix invariance holds exactly, pinned by tests).
"""

from __future__ import annotations

import pandas as pd

from . import ema_crossover

# The registered gate universe (committed round-3 daily caches only).
GATE_ASSETS = ("TLT", "XOM", "GLD")

# Module-level read-only cache of dev-rail gate close series.
_GATE_CLOSE_CACHE: dict[str, pd.Series] = {}


def _load_gate_close(gate_asset: str) -> pd.Series:
    """Dev-rail close series for the gate asset (cached; holdout excluded
    by the loader's default — ``unlock_holdout`` is never passed)."""
    if gate_asset not in _GATE_CLOSE_CACHE:
        from trading_lab.data import load_ohlcv  # local: avoid import cycle
        _GATE_CLOSE_CACHE[gate_asset] = load_ohlcv(gate_asset,
                                                   "daily")["close"]
    return _GATE_CLOSE_CACHE[gate_asset]


def gate_momentum(gate_close: pd.Series, gate_lookback: int) -> pd.Series:
    """Trailing momentum on the gate asset's OWN calendar: NaN during the
    first ``gate_lookback`` bars (undefined resolves against the
    strategy)."""
    if gate_lookback < 1:
        raise ValueError(f"gate_lookback ({gate_lookback}) must be >= 1")
    return gate_close / gate_close.shift(gate_lookback) - 1.0


def gate_signal(equity_index: pd.DatetimeIndex, gate_close: pd.Series,
                gate_lookback: int) -> pd.Series:
    """Boolean gate-open series on the EQUITY index, lookahead-free.

    Momentum is computed on the gate calendar, then aligned with
    ``reindex(equity_index, method="ffill")`` — the value at equity bar t
    is the most recent gate momentum with timestamp <= t. Gate OPEN iff
    that momentum is > 0; undefined (warm-up / no gate bar <= t) is
    CLOSED.
    """
    mom = gate_momentum(gate_close, gate_lookback)
    aligned = mom.reindex(equity_index, method="ffill")
    return aligned > 0.0  # NaN compares False -> closed


def generate(ohlcv: pd.DataFrame, gate_asset: str = "TLT",
             gate_lookback: int = 126, gated: bool = True,
             trend_fast: int = 20, trend_slow: int = 100,
             gate_close: pd.Series | None = None) -> pd.Series:
    """Positions for the equity in ``ohlcv``; 0/1 long-flat.

    ``gated=False`` is the MANDATORY ungated control arm: the plain frozen
    trend component — no gate data is ever loaded or computed.
    ``gate_close`` injects an explicit gate close series (tests); when
    None the committed dev-rail cache for ``gate_asset`` is used.
    """
    trend_pos = ema_crossover.generate(ohlcv, fast=trend_fast,
                                       slow=trend_slow)
    if not gated:
        # Ungated control arm: the same component, NO gate — invariant to
        # gate_asset / gate_lookback / gate_close by construction.
        pos = trend_pos.copy()
        pos.name = "position"
        return pos

    if gate_lookback < 1:
        raise ValueError(f"gate_lookback ({gate_lookback}) must be >= 1")
    if gate_close is None:
        if gate_asset not in GATE_ASSETS:
            raise ValueError(f"gate_asset ({gate_asset!r}) must be one of "
                             f"{GATE_ASSETS}")
        gate_close = _load_gate_close(gate_asset)
    open_ = gate_signal(ohlcv.index, gate_close, gate_lookback)
    pos = trend_pos.where(open_, 0.0)
    pos.name = "position"
    return pos
