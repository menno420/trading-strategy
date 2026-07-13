"""Day-of-week seasonality rule: signal long on every bar whose timestamp
falls on one chosen weekday, flat everywhere else.

Round 4 slice R4-F (docs/research-round-4-plan.md § R4-F, pre-registered):
the cheapest calendar hypothesis and a classic multiple-testing trap —
swept across all 15 committed daily tickers with K counted honestly at
5 weekdays × 15 tickers = 75 (bar ``min_tstat(75)`` ≈ 3.21, RISEN from
2.64 at K=12, never lowered).

Execution semantics under the house rail (documented choice, binding)
----------------------------------------------------------------------
This is a pure calendar rule, so the t/t+1 convention deserves an explicit
statement. ``positions[t] = 1`` iff ``t.dayofweek == weekday``; the engine
then fills at bar t+1's open like every other family (``held[t+1] = pos[t]``,
open-to-open accounting). The variant labeled ``weekday=d`` is therefore
exposed to the open(t+1) → open(t+2) return following each day-d bar — the
honest *tradable* implementation of "be long the session after day d". A
rule that instead targeted holding DURING day d would need the calendar of
the next bar at signal time; rather than special-case the engine's
convention for one family, we keep the same signal→fill rail as every
other strategy. The five variants together still tile the trading week
(each session's return is captured by exactly one variant, label-shifted
by one trading day), so the sweep tests every day-of-week exposure and no
calendar effect can hide between variants.

``weekday`` uses pandas dayofweek numbering: 0=Mon .. 4=Fri (5/6 =
Sat/Sun accepted but not part of the registered R4-F grid; BTC-USD's
weekend bars simply stay flat under the five registered variants — K
stays 75 as registered).
"""

from __future__ import annotations

import pandas as pd


def generate(ohlcv: pd.DataFrame, weekday: int = 0) -> pd.Series:
    """Long (1.0) on every bar whose ``index.dayofweek == weekday``, else
    flat (0.0). Strictly causal: positions[t] uses only bar t's own
    timestamp (fills happen at t+1's open per the engine rail)."""
    if not isinstance(weekday, int) or isinstance(weekday, bool):
        raise ValueError(f"weekday must be an int, got {weekday!r}")
    if not 0 <= weekday <= 6:
        raise ValueError(f"weekday must be in 0..6 (0=Mon), got {weekday}")
    dow = pd.Index(ohlcv.index).dayofweek
    pos = pd.Series((dow == weekday).astype(float), index=ohlcv.index)
    pos.name = "position"
    return pos
