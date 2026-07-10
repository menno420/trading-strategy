"""Strategy library (P0 baselines + P1 trend-following family + video lane
+ P1 mean-reversion family).

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
* mean-reversion (P1, lane mean-reversion__all8__daily): rsi_mean_reversion
  (the P0 baseline, reused with a sweep grid), bollinger_reversion
  (z-score/band reversion), pullback (short-horizon dip-buying with an
  optional long-term trend filter).
* Round 2 (post-holdout dev-only, docs/research-round-2.md):
  vol_filtered_trend (slice R1 — SMA crossover gated by a realized-vol
  calm-regime filter; the filter-off arm is the within-family baseline);
  keltner_breakout (slice R2 — long on close > EMA(n) + m*ATR(n), exit on
  close < EMA(n)); xsec_momentum (slice R3 — cross-sectional momentum
  PORTFOLIO over the 9-instrument basket; different interface, see below).

Portfolio strategies (``PORTFOLIO_STRATEGIES``) take a panel of aligned
closes (one column per instrument) and return a target-weight DataFrame
for ``trading_lab.portfolio.run_portfolio_backtest`` — they do NOT fit the
single-instrument ``generate(ohlcv, **params) -> pd.Series`` interface and
are deliberately kept out of ``STRATEGIES``.
"""

from __future__ import annotations

from . import (bollinger_reversion, buy_and_hold, donchian, ema_crossover,
               keltner_breakout, macd, macd_supertrend, pullback,
               rsi_mean_reversion, sma_crossover, supertrend_flip,
               vol_filtered_trend, xsec_momentum)

STRATEGIES = {
    "buy_and_hold": buy_and_hold.generate,
    "sma_crossover": sma_crossover.generate,
    "rsi_mean_reversion": rsi_mean_reversion.generate,
    "ema_crossover": ema_crossover.generate,
    "macd": macd.generate,
    "donchian": donchian.generate,
    "supertrend_flip": supertrend_flip.generate,
    "macd_supertrend": macd_supertrend.generate,
    "bollinger_reversion": bollinger_reversion.generate,
    "pullback": pullback.generate,
    "vol_filtered_trend": vol_filtered_trend.generate,
    "keltner_breakout": keltner_breakout.generate,
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
    "bollinger_reversion": {"lookback": 20, "z_entry": 2.0, "z_exit": 0.0},
    "pullback": {"entry_lookback": 5, "exit_len": 5, "trend_len": 200},
    "vol_filtered_trend": {"fast": 20, "slow": 50, "vol_filter": True},
    "keltner_breakout": {"n": 20, "m": 2.0},
}

# P1 trend-following family: the four strategies swept in the
# trend-following × all-8-tickers × daily lane.
TREND_FOLLOWING_FAMILY = ["sma_crossover", "ema_crossover", "macd", "donchian"]

# Video-strategy lane: competing interpretations of the video's rules.
# ema_crossover doubles as the dual-EMA control (video Strategy A region).
VIDEO_STRATEGY_FAMILY = ["supertrend_flip", "macd_supertrend", "ema_crossover"]

# P1 mean-reversion family: the three strategies swept in the
# mean-reversion × all-8-tickers × daily lane (QUEUE item 2).
MEAN_REVERSION_FAMILY = ["rsi_mean_reversion", "bollinger_reversion",
                         "pullback"]

# Round 2 slice R1 (docs/research-round-2.md §3a): the single family swept
# in the r2-vol_filtered_trend × {AAPL, MSFT, NVDA, GLD} × daily lane.
R2_VOL_TREND_FAMILY = ["vol_filtered_trend"]

# Round 2 slice R2 (docs/research-round-2.md §3b): the single family swept
# in the r2-keltner_breakout × {BTC-USD, META, AMZN, SLV} × daily lane.
R2_KELTNER_FAMILY = ["keltner_breakout"]

# Round 2 slice R3 (docs/research-round-2.md §3c): the single PORTFOLIO
# family swept in the r2-xsec_momentum × 9-instrument-basket × daily lane.
# Portfolio interface (weights over a panel), so it lives in
# PORTFOLIO_STRATEGIES, not STRATEGIES.
R2_XSEC_FAMILY = ["xsec_momentum"]

PORTFOLIO_STRATEGIES = {
    "xsec_momentum": xsec_momentum.generate_weights,
}

__all__ = ["STRATEGIES", "DEFAULT_PARAMS", "PORTFOLIO_STRATEGIES",
           "TREND_FOLLOWING_FAMILY",
           "VIDEO_STRATEGY_FAMILY", "MEAN_REVERSION_FAMILY",
           "R2_VOL_TREND_FAMILY", "R2_KELTNER_FAMILY", "R2_XSEC_FAMILY",
           "buy_and_hold", "sma_crossover", "rsi_mean_reversion",
           "ema_crossover", "macd", "donchian", "supertrend_flip",
           "macd_supertrend", "bollinger_reversion", "pullback",
           "vol_filtered_trend", "keltner_breakout", "xsec_momentum"]
