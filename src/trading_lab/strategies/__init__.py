"""Strategy library (P0 baselines + P1 trend-following family + video lane).

Common interface: ``generate(ohlcv, **params) -> pd.Series`` of target
positions indexed like ``ohlcv``. ``positions[t]`` uses data only through
bar ``t`` (the engine delays execution to bar ``t+1``'s open). Values are
0/1 (long/flat) for all strategies here.

Families:

* baselines (P0): buy_and_hold, sma_crossover, rsi_mean_reversion
* trend-following (P1): sma_crossover, ema_crossover, macd, donchian
* video-strategy (P1, lane video-strategy__btcusd__multi): supertrend_flip,
  macd_supertrend (+ ema_crossover reused as the dual-EMA control) —
  competing interpretations of the DaviddTech video's under-specified rules
  (docs/research/video-source-2026-07-09.md).
"""

from __future__ import annotations

from . import (buy_and_hold, donchian, ema_crossover, macd, macd_supertrend,
               rsi_mean_reversion, sma_crossover, supertrend_flip)

STRATEGIES = {
    "buy_and_hold": buy_and_hold.generate,
    "sma_crossover": sma_crossover.generate,
    "rsi_mean_reversion": rsi_mean_reversion.generate,
    "ema_crossover": ema_crossover.generate,
    "macd": macd.generate,
    "donchian": donchian.generate,
    "supertrend_flip": supertrend_flip.generate,
    "macd_supertrend": macd_supertrend.generate,
}

DEFAULT_PARAMS = {
    "buy_and_hold": {},
    "sma_crossover": {"fast": 20, "slow": 50},
    "rsi_mean_reversion": {"period": 14, "oversold": 30, "overbought": 70},
    "ema_crossover": {"fast": 20, "slow": 50},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "donchian": {"entry": 20, "exit": 10},
    "supertrend_flip": {"st_period": 10, "st_mult": 3.0, "ema_len": 200,
                        "macd_fast": 12, "macd_slow": 26, "macd_signal": 9},
    "macd_supertrend": {"macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
                        "st_period": 10, "st_mult": 3.0, "ema_len": 200},
}

# P1 trend-following family: the four strategies swept in the
# trend-following × all-8-tickers × daily lane.
TREND_FOLLOWING_FAMILY = ["sma_crossover", "ema_crossover", "macd", "donchian"]

# Video-strategy lane: competing interpretations of the video's rules.
# ema_crossover doubles as the dual-EMA control (video Strategy A region).
VIDEO_STRATEGY_FAMILY = ["supertrend_flip", "macd_supertrend", "ema_crossover"]

__all__ = ["STRATEGIES", "DEFAULT_PARAMS", "TREND_FOLLOWING_FAMILY",
           "VIDEO_STRATEGY_FAMILY",
           "buy_and_hold", "sma_crossover", "rsi_mean_reversion",
           "ema_crossover", "macd", "donchian", "supertrend_flip",
           "macd_supertrend"]
