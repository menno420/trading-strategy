"""Strategy library (P0 baselines + P1 trend-following family).

Common interface: ``generate(ohlcv, **params) -> pd.Series`` of target
positions indexed like ``ohlcv``. ``positions[t]`` uses data only through
bar ``t`` (the engine delays execution to bar ``t+1``'s open). Values are
0/1 (long/flat) for all strategies here.

Families:

* baselines (P0): buy_and_hold, sma_crossover, rsi_mean_reversion
* trend-following (P1): sma_crossover, ema_crossover, macd, donchian
"""

from __future__ import annotations

from . import (buy_and_hold, donchian, ema_crossover, macd,
               rsi_mean_reversion, sma_crossover)

STRATEGIES = {
    "buy_and_hold": buy_and_hold.generate,
    "sma_crossover": sma_crossover.generate,
    "rsi_mean_reversion": rsi_mean_reversion.generate,
    "ema_crossover": ema_crossover.generate,
    "macd": macd.generate,
    "donchian": donchian.generate,
}

DEFAULT_PARAMS = {
    "buy_and_hold": {},
    "sma_crossover": {"fast": 20, "slow": 50},
    "rsi_mean_reversion": {"period": 14, "oversold": 30, "overbought": 70},
    "ema_crossover": {"fast": 20, "slow": 50},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "donchian": {"entry": 20, "exit": 10},
}

# P1 trend-following family: the four strategies swept in the
# trend-following × all-8-tickers × daily lane.
TREND_FOLLOWING_FAMILY = ["sma_crossover", "ema_crossover", "macd", "donchian"]

__all__ = ["STRATEGIES", "DEFAULT_PARAMS", "TREND_FOLLOWING_FAMILY",
           "buy_and_hold", "sma_crossover", "rsi_mean_reversion",
           "ema_crossover", "macd", "donchian"]
